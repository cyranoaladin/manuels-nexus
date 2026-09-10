"""La couverture du programme se prouve sur les objets, pas sur un referentiel.

Deux questions distinctes, deux matrices. Le rattachement demande si les
capacites internes sont correctement raccrochees au BO. Celle-ci demande si
l'eleve trouve, dans le manuel, de quoi apprendre ce que le programme exige.
Un attendu peut etre parfaitement enseigne sans avoir jamais recu d'atome
interne : exiger un atome par attendu ferait apparaitre comme manquant ce qui
est enseigne, et pousserait a fabriquer des atomes vides pour faire tomber un
compteur.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "audit" / "OFFICIAL_TO_MANUAL_COVERAGE.json"
INDEX = ROOT / "audit" / "OFFICIAL_PROGRAMME_INVENTORY.json"

STATUTS = {
    "COMPLETE",
    "PARTIAL",
    "MISSING",
    "INSTITUTIONAL_IMPLEMENTATION_REQUIREMENT",
    "UNDECIDABLE_BY_CONTENT_MATCH",
    "OUT_OF_SCOPE_ENRICHMENT",
}


@pytest.fixture(scope="module")
def couverture():
    return json.loads(COVERAGE.read_text(encoding="utf-8"))


def test_chaque_attendu_applicable_recoit_un_statut(couverture):
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    attendu = sum(e["items"] for e in index["documents"] if e["applies_to_edition"])
    assert len(couverture["rows"]) == attendu
    assert all(r["coverage_status"] in STATUTS for r in couverture["rows"])
    assert all(r["coverage_reason"] for r in couverture["rows"])


def test_les_statuts_partitionnent_les_attendus_obligatoires(couverture):
    """Un attendu obligatoire sans statut echapperait au compte."""
    resume = couverture["summary"]
    total = (
        resume["OFFICIAL_REQUIRED_COMPLETE"]
        + resume["OFFICIAL_REQUIRED_PARTIAL"]
        + resume["OFFICIAL_REQUIRED_MISSING"]
        + resume["OFFICIAL_REQUIRED_INSTITUTIONAL"]
        + resume["OFFICIAL_REQUIRED_UNDECIDABLE_BY_CONTENT_MATCH"]
    )
    assert total == resume["mandatory_items"]
    assert resume["mandatory_items"] == sum(1 for r in couverture["rows"] if r["mandatory"])


def test_un_attendu_couvert_designe_les_objets_qui_le_couvrent(couverture):
    """Une couverture sans objet nomme n'est pas verifiable."""
    for ligne in couverture["rows"]:
        if ligne["coverage_status"] in ("COMPLETE", "PARTIAL"):
            assert ligne["object_count"] > 0, ligne["official_id"]
            assert ligne["objects_by_role"], ligne["official_id"]
            assert ligne["chapters"], ligne["official_id"]
        if ligne["coverage_status"] == "MISSING":
            assert ligne["object_count"] == 0, ligne["official_id"]


def test_une_connaissance_peut_etre_couverte_sans_atome_interne(couverture):
    """C'est le point de fond : le referentiel n'est pas la condition.

    Les referentiels du projet encodent surtout des capacites. Si la matrice
    exigeait un atome par attendu, toutes les connaissances du programme
    ressortiraient comme manquantes alors qu'elles sont enseignees.
    """
    sans_atome = [
        r for r in couverture["rows"]
        if r["mandatory"]
        and not r["internal_atoms"]
        and r["coverage_status"] == "COMPLETE"
    ]
    assert sans_atome, (
        "aucune preuve par le contenu : l'atome interne serait devenu une "
        "condition de conformite"
    )
    assert all(r["evidence_kind"] for r in sans_atome)
    par_contenu = [
        r for r in sans_atome
        if r["evidence_kind"] in ("CONTENT_MATCH", "CONTENT_MATCH_MANUAL_WIDE")
    ]
    assert par_contenu
    assert all(r["matched_terms"] for r in par_contenu)


def test_une_demonstration_exigible_ne_se_prouve_pas_par_un_exercice(couverture):
    """Le nom d'un theoreme ne demontre rien.

    Une demonstration exigible n'est couverte que si la preuve est ecrite
    quelque part dans le manuel.
    """
    demonstrations = [
        r for r in couverture["rows"]
        if r["official_normativity"] == "REQUIRED_DEMONSTRATION"
    ]
    assert demonstrations
    partielles = [r for r in demonstrations if r["coverage_status"] == "PARTIAL"]
    for ligne in partielles:
        assert "demonstration redigee" in ligne["coverage_reason"]
        assert ligne["object_count"] > 0


def test_un_exemple_d_algorithme_n_impose_pas_cet_exemple_la(couverture):
    """Le BO nomme des exemples ; il ne les impose pas.

    Exiger l'algorithme cite transformerait une illustration en obligation que
    le texte ne porte pas, et declarerait manquant un chapitre qui fait le
    travail autrement.
    """
    lignes = [
        r for r in couverture["rows"]
        if r["official_normativity"] == "PRESCRIBED_ALGORITHMIC_WORK"
        and r["coverage_status"] == "COMPLETE"
    ]
    assert lignes
    motifs = {r["coverage_reason"] for r in lignes}
    assert any("il ne l'impose pas" in m for m in motifs), motifs


def test_le_quart_de_l_horaire_n_est_jamais_declare_satisfait_par_le_livre(couverture):
    """Un manuel ne peut pas prouver l'emploi du temps d'un etablissement.

    Le declarer couvert serait une fausse preuve ; le declarer manquant serait
    reprocher au manuel ce qui ne lui incombe pas.
    """
    transversales = [
        r for r in couverture["rows"]
        if r["official_normativity"] == "TRANSVERSAL_REQUIREMENT"
    ]
    assert transversales
    assert all(
        r["coverage_status"] == "INSTITUTIONAL_IMPLEMENTATION_REQUIREMENT"
        for r in transversales
    )
    quart = [r for r in transversales if "quart au moins" in r["official_wording"]]
    assert quart, "l'exigence du quart de l'horaire doit rester inventoriee"
    assert all(r["coverage_status"] != "COMPLETE" for r in quart)


def test_aucun_pourcentage_global_ne_tient_lieu_de_verdict(couverture):
    """Un « 97,4 % couvert » masquerait la nature des manques.

    Le resume publie des comptes par nature d'attendu, jamais un taux unique.
    """
    resume = couverture["summary"]
    assert not any(
        isinstance(v, float) and 0 < v < 100 for v in resume.values()
    ), resume
    for detail in couverture["per_manual"].values():
        assert detail["by_normativity"], detail


def test_la_matrice_est_bien_regeneree_par_son_generateur():
    acheve = subprocess.run(
        [sys.executable, "scripts/build_official_to_manual_coverage.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert acheve.returncode == 0, acheve.stdout + acheve.stderr
