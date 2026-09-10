"""Le manuel de premiere a change de programme : le differentiel doit le dire.

Sans lui, deux erreurs symetriques passent inapercues : un attendu retire en
2026 qu'on continue de compter comme couverture, et un attendu ajoute que
personne ne cherche parce qu'il n'existait pas dans la version d'avant.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DIFF = ROOT / "audit" / "1SPE_PROGRAMME_DIFF_2019_2026.json"
VERDICTS = {
    "UNCHANGED", "MOVED", "RECLASSIFIED_2026",
    "REFORMULATED_2026", "ADDED_2026", "REMOVED_2026",
}


@pytest.fixture(scope="module")
def diff():
    return json.loads(DIFF.read_text(encoding="utf-8"))


def test_le_differentiel_compare_bien_les_deux_autorites(diff):
    assert diff["from_authority"] == "MENE1901632A"
    assert diff["to_authority"] == "MENE2602917A"
    assert diff["from_effective"] < diff["to_effective"]


def test_chaque_attendu_des_deux_editions_recoit_un_verdict(diff):
    """Un attendu sans verdict serait un attendu qu'on a cesse de suivre."""
    verdicts = diff["verdicts"]
    assert all(v["verdict"] in VERDICTS for v in verdicts)
    cotes_2026 = sum(
        1 for v in verdicts if v["verdict"] != "REMOVED_2026"
    )
    cotes_2019 = sum(
        1 for v in verdicts if v["verdict"] != "ADDED_2026"
    )
    assert cotes_2026 == diff["summary"]["items_2026"]
    assert cotes_2019 == diff["summary"]["items_2019"]


def test_un_rapprochement_mesure_ne_se_donne_pas_pour_une_certitude(diff):
    for v in diff["verdicts"]:
        if v["verdict"] in ("REFORMULATED_2026",):
            assert v["review_status"] == "PROPOSED_REQUIRES_HUMAN_CONFIRMATION"
            assert v["wording_2019"] and v["similarity"] is not None
        if v["verdict"] in ("UNCHANGED", "MOVED", "ADDED_2026", "REMOVED_2026"):
            assert v["review_status"] == "ESTABLISHED"


def test_un_attendu_inchange_reste_au_meme_endroit(diff):
    """Sinon « inchange » recouvrirait aussi une reorganisation du programme."""
    for v in diff["verdicts"]:
        if v["verdict"] == "UNCHANGED":
            assert v["location_2019"] == v["location_2026"]
        if v["verdict"] == "MOVED":
            assert v["location_2019"] != v["location_2026"]


def test_les_automatismes_de_2026_sont_bien_une_nouveaute_du_programme(diff):
    """Le programme de 2019 n'avait pas de partie « Automatismes ».

    Les dix-sept automatismes de 2026 sont donc, pour le manuel, un chantier
    entier et non un ajustement : le compter comme acquis serait faux.
    """
    resume = diff["summary"]
    assert resume["AUTOMATISMS_2026"] == 17
    sans_antecedent = resume["AUTOMATISMS_2026_WITHOUT_ANY_2019_ANTECEDENT"]
    herites = resume["AUTOMATISMS_2026_INHERITED_FROM_A_2019_CAPACITY"]
    assert sans_antecedent + herites == resume["AUTOMATISMS_2026"]
    assert sans_antecedent >= 15


def test_un_changement_de_nature_est_publie_et_pas_dissous(diff):
    """Une capacite devenue automatisme ne se travaille plus au meme moment.

    C'est le mouvement le plus facile a manquer : le libelle bouge a peine.
    """
    changes = diff["kind_changed_between_editions"]
    assert changes, "aucun changement de nature releve entre 2019 et 2026"
    assert len(changes) == diff["summary"]["KIND_CHANGED_BETWEEN_EDITIONS"]
    for v in changes:
        assert v["kind_2019"] != v["kind"]
    assert any(v["kind"] == "AUTOMATISM" for v in changes)


def test_la_trigonometrie_a_bien_ete_deplacee_et_allegee(diff):
    """Verification sur un cas connu et documente de la reforme.

    Le differentiel doit retrouver ce que le depot decrit deja par ailleurs :
    la trigonometrie change de sous-partie, et l'etude des fonctions cosinus
    et sinus quitte le programme de premiere.
    """
    deplaces = [
        v for v in diff["verdicts"]
        if v["verdict"] == "MOVED" and v["location_2026"][1] == "Trigonométrie"
    ]
    assert deplaces, "le deplacement de la trigonometrie n'est pas detecte"
    assert all(v["location_2019"][1] == "Fonctions trigonométriques" for v in deplaces)

    retires = [
        v for v in diff["verdicts"]
        if v["verdict"] == "REMOVED_2026"
        and v["location_2019"][1] == "Fonctions trigonométriques"
    ]
    assert retires, "aucun retrait detecte sur les fonctions trigonometriques"


def test_le_differentiel_est_bien_regenere_par_son_generateur():
    acheve = subprocess.run(
        [sys.executable, "scripts/build_1spe_programme_diff_2019_2026.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert acheve.returncode == 0, acheve.stdout + acheve.stderr
