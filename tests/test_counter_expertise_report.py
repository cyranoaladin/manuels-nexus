"""Un compteur qui tombe a zero n'explique pas pourquoi il est tombe.

Treize attendus obligatoires etaient declares manquants, quarante-cinq
partiels, trois indecidables. Tous sont aujourd'hui couverts. Cette phrase,
seule, ne distingue pas un manuel complete d'une mesure assouplie : c'est
pourquoi chacun doit dire ce qu'il est devenu, et pourquoi le rapport se
deduit d'un instantane fige plutot que d'une memoire.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "audit" / "baselines" / "COVERAGE_BEFORE_COUNTER_EXPERTISE.json"
RAPPORT = ROOT / "audit" / "PROGRAMME_COUNTER_EXPERTISE_REPORT.json"

VERDICTS_MANQUANTS = {
    "FALSE_MISSING_TOOLING",
    "MISSING_FROM_ASSEMBLY",
    "TRUE_CONTENT_GAP",
}
VERDICTS_PARTIELS = {"FALSE_PARTIAL_TOOLING", "TRUE_PARTIAL_PEDAGOGICAL"}


@pytest.fixture(scope="module")
def rapport():
    return json.loads(RAPPORT.read_text(encoding="utf-8"))


def test_la_ligne_de_base_reste_ce_qu_elle_etait():
    """Sans instantane fige, il n'y aurait plus rien a refuter."""
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    assert base["MISSING_BEFORE"] == 13
    assert base["PARTIAL_BEFORE"] == 45
    assert base["UNDECIDABLE_BEFORE"] == 3
    assert len(base["rows"]) == 13 + 45 + 3
    assert base["source_commit"]


def test_chaque_attendu_non_couvert_recoit_un_verdict(rapport):
    """Aucun des cinquante-huit ne disparait sans explication."""
    resume = rapport["summary"]
    # Les trois familles restent distinctes : un attendu que la mesure n'avait
    # pas pu chercher n'etait pas un attendu declare manquant, et les
    # confondre gonflerait le nombre de « manquants » refutes.
    assert (
        resume["FALSE_MISSING_TOOLING"]
        + resume["MISSING_FROM_ASSEMBLY"]
        + resume["TRUE_CONTENT_GAP"]
        == resume["MISSING_BEFORE"]
    )
    assert (
        resume["UNDECIDABLE_FALSE_MISSING_TOOLING"]
        + resume["UNDECIDABLE_TRUE_CONTENT_GAP"]
        == resume["UNDECIDABLE_BEFORE"]
    )
    assert (
        resume["FALSE_PARTIAL_TOOLING"] + resume["TRUE_PARTIAL_PEDAGOGICAL"]
        == resume["PARTIAL_BEFORE"]
    )
    for ligne in rapport["former_missing"] + rapport["former_undecidable"]:
        assert ligne["verdict_apres_contre_expertise"] in VERDICTS_MANQUANTS
        assert ligne["cause"]
        assert ligne["modification_effectuee"]
    for ligne in rapport["former_partial"]:
        assert ligne["verdict_apres_contre_expertise"] in VERDICTS_PARTIELS
        assert ligne["cause"]


def test_un_verdict_de_refutation_designe_ce_qui_le_prouve(rapport):
    """Refuter un manquant sans citer un objet du manuel serait une opinion."""
    refutes = [
        ligne
        for ligne in rapport["former_missing"]
        + rapport["former_partial"]
        + rapport["former_undecidable"]
        if ligne["verdict_apres_contre_expertise"]
        in ("FALSE_MISSING_TOOLING", "FALSE_PARTIAL_TOOLING", "MISSING_FROM_ASSEMBLY")
    ]
    assert refutes
    for ligne in refutes:
        if ligne["mandatory_now"]:
            assert ligne["existing_evidence_if_any"], ligne["official_id"]
        assert ligne["coverage_status_now"] in (
            "COMPLETE",
            "OUT_OF_SCOPE_ENRICHMENT",
        )


def test_un_vrai_manque_a_produit_un_contenu_et_lui_seul(rapport):
    """Le contenu ecrit se limite aux manques reels.

    Un verdict TRUE_CONTENT_GAP ou TRUE_PARTIAL_PEDAGOGICAL sans contenu ecrit
    serait un manque declare puis oublie ; un contenu ecrit sous un verdict de
    refutation serait une redaction sans motif.
    """
    toutes = (
        rapport["former_missing"]
        + rapport["former_partial"]
        + rapport["former_undecidable"]
    )
    for ligne in toutes:
        reel = ligne["verdict_apres_contre_expertise"] in (
            "TRUE_CONTENT_GAP",
            "TRUE_PARTIAL_PEDAGOGICAL",
        )
        assert (ligne["content_created"] == "YES") == reel, ligne["official_id"]
    ecrits = rapport["CONTENT_CREATED_BECAUSE_PROGRAMME_REALLY_MISSING"]
    assert ecrits
    assert len(ecrits) == rapport["summary"][
        "CONTENT_CREATED_BECAUSE_PROGRAMME_REALLY_MISSING"
    ]
    for entree in ecrits:
        assert (ROOT / entree["path"]).exists(), entree["path"]


def test_l_enrichissement_ne_se_melange_pas_aux_manques(rapport):
    """Le BO nomme la planche de Galton ; il ne l'impose pas.

    Ranger ces deux pages parmi les manques combles ferait passer un
    enrichissement editorial pour une obligation satisfaite.
    """
    enrichissements = rapport["EDITORIAL_QUALITY_ENRICHMENT"]
    assert enrichissements
    chemins_de_manques = {
        e["path"] for e in rapport["CONTENT_CREATED_BECAUSE_PROGRAMME_REALLY_MISSING"]
    }
    for entree in enrichissements:
        assert entree["path"] not in chemins_de_manques
        assert entree["standard"] == "NEXUS_ALGORITHMIC_QUALITY_STANDARD"
        assert (ROOT / entree["path"]).exists()


def test_le_rapport_est_bien_regenere_par_son_generateur():
    acheve = subprocess.run(
        [sys.executable, "scripts/build_counter_expertise_report.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert acheve.returncode == 0, acheve.stdout + acheve.stderr


def test_les_compteurs_du_rapport_sont_canoniques():
    """Aucun rapport ne recopie a la main un compteur calcule ailleurs."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from programme_metrics import canonical_metrics

    metriques = canonical_metrics()
    charge = json.loads(RAPPORT.read_text(encoding="utf-8"))
    for nom in (
        "FALSE_MISSING_TOOLING",
        "MISSING_FROM_ASSEMBLY",
        "TRUE_CONTENT_GAP",
        "FALSE_PARTIAL_TOOLING",
        "TRUE_PARTIAL_PEDAGOGICAL",
        "CONTENT_CREATED_BECAUSE_PROGRAMME_REALLY_MISSING",
    ):
        assert metriques[nom].artifact == "audit/PROGRAMME_COUNTER_EXPERTISE_REPORT.json"
        assert metriques[nom].value == charge["summary"][nom]
