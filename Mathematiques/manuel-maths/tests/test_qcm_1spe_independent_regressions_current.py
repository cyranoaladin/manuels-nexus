"""Régressions issues de la recomputation indépendante des 162 QCM 1SPE."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path


CHAPTERS = Path(__file__).resolve().parents[1] / "chapitres"


def question(chapter: str, filename: str, question_id: str) -> dict:
    source = CHAPTERS / chapter / "qcm" / filename
    data = json.loads(source.read_text(encoding="utf-8"))
    return next(item for item in data["questions"] if item["id"] == question_id)


def test_suites_q1_et_q19_correspondent_aux_recalculs_independants() -> None:
    q1 = question("1SPE-SUITES", "1SPE-SUITES-QCM.json", "Q1")
    assert 2 * 3**2 - 3 * 3 + 1 == 10
    assert q1["correcte"] == "A"
    assert q1["options"]["A"] == "$10$"

    q19 = question("1SPE-SUITES", "1SPE-SUITES-QCM.json", "Q19")
    value = 2
    for _ in range(3):
        value = 3 * value + 1
    assert value == 67
    assert q19["correcte"] == "C"
    assert q19["options"]["C"] == "$67$"


def test_suites_q9_utilise_la_definition_sans_exclure_les_termes_nuls() -> None:
    q9 = question("1SPE-SUITES", "1SPE-SUITES-QCM.json", "Q9")
    assert q9["correcte"] == "C"
    assert "u_{n+1}=q" in q9["options"]["C"]
    assert "ne peut" not in q9["options"]["B"].lower()
    assert all(
        "ne peut pas avoir de terme nul" not in diagnostic["erreur"].lower()
        for diagnostic in q9["diagnostics"].values()
    )


def test_produit_scalaire_q8_ne_contient_qu_une_propriete_vraie() -> None:
    q8 = question(
        "1SPE-PRODUIT-SCALAIRE", "1SPE-PRODUIT-SCALAIRE-QCM.json", "Q8"
    )
    assert 2 * 3 + 3 * (-2) == 0
    assert 2**2 + 3**2 == 3**2 + (-2) ** 2
    assert q8["correcte"] == "B"
    assert "différentes" in q8["options"]["C"]
    assert "colineaires" in q8["diagnostics"]["D"]["erreur"]


def test_proba_conditionnelle_q8_a_une_seule_option_egale_a_un_tiers() -> None:
    q8 = question("1SPE-PROBA-COND", "1SPE-PROBCOND-QCM.json", "Q8")
    result = Fraction(1, 3) * Fraction(1, 2) + Fraction(2, 3) * Fraction(1, 4)
    assert result == Fraction(1, 3)
    assert q8["correcte"] == "D"
    assert q8["options"]["D"] == "$1/3$"
    assert list(q8["options"].values()).count("$1/3$") == 1


def test_proba_conditionnelle_q17_donne_la_specificite_et_la_vpp_exacte() -> None:
    q17 = question("1SPE-PROBA-COND", "1SPE-PROBCOND-QCM.json", "Q17")
    vpp = (Fraction(99, 100) * Fraction(1, 1000)) / (
        Fraction(99, 100) * Fraction(1, 1000)
        + Fraction(1, 100) * Fraction(999, 1000)
    )
    assert float(vpp) == 0.09016393442622951
    assert "specificite" in q17["enonce"].lower()
    assert q17["correcte"] == "C"
    assert "9" in q17["options"]["C"]


def test_second_degre_distracteurs_q3_et_q7_sont_reproductibles() -> None:
    q3 = question("1SPE-SECOND-DEGRE", "1SPE-SECDEG-QCM.json", "Q3")
    assert q3["options"]["D"] == "$3x^2 + 2$"
    assert "3x^2 + 2" in q3["diagnostics"]["D"]["erreur"]

    q7 = question("1SPE-SECOND-DEGRE", "1SPE-SECDEG-QCM.json", "Q7")
    assert -(-5) ** 2 + 4 * 1 * 6 == -1
    assert q7["options"]["C"] == "$\\Delta = -1$"
    assert "-1" in q7["diagnostics"]["C"]["erreur"]


def test_diagnostics_derivation_globale_restent_lies_aux_distracteurs() -> None:
    q8 = question(
        "1SPE-DERIVATION-GLOBAL", "1SPE-DERIVATION-GLOBAL-QCM.json", "Q8"
    )
    assert "convexit" in q8["diagnostics"]["D"]["erreur"].lower()
    assert "f'(4)=4" not in q8["diagnostics"]["D"]["erreur"]

    q9 = question(
        "1SPE-DERIVATION-GLOBAL", "1SPE-DERIVATION-GLOBAL-QCM.json", "Q9"
    )
    assert "asymptote" in q9["diagnostics"]["D"]["erreur"].lower()
    assert "f'(3)=0" not in q9["diagnostics"]["D"]["erreur"]


def test_suites_q4_diagnostique_exactement_le_premier_terme() -> None:
    q4 = question("1SPE-SUITES", "1SPE-SUITES-QCM.json", "Q4")
    assert 4 * 0 - 7 == -7
    assert 4 * 1 - 7 == -3
    diagnostic = q4["diagnostics"]["D"]["erreur"]
    assert "u_1" in diagnostic
    assert "u_0 = -3" not in diagnostic


def test_exponentielle_q1_ne_propose_qu_une_caracterisation_valide() -> None:
    q1 = question("1SPE-EXPONENTIELLE", "1SPE-EXPONENTIELLE-QCM.json", "Q1")
    assert q1["correcte"] == "B"
    assert "f(0) = 1" in q1["options"]["B"]
    assert "f(1) = 1" in q1["options"]["A"]
    assert "\\mathrm{e}^{x-1}" in q1["diagnostics"]["A"]["erreur"]


def test_geometrie_reperee_q5_n_admet_qu_un_vecteur_directeur() -> None:
    q5 = question("1SPE-GEOMETRIE-REPEREE", "1SPE-GEOREP-QCM.json", "Q5")
    vectors = {
        "A": (2, 5),
        "B": (-5, 2),
        "C": (5, 2),
        "D": (-5, -2),
    }
    perpendicular = [key for key, (x, y) in vectors.items() if 2 * x + 5 * y == 0]
    assert perpendicular == [q5["correcte"]]
    assert q5["options"]["D"] == "$\\vec{u}(-5 ; -2)$"


def test_trigonometrie_q9_precise_que_k_est_entier() -> None:
    q9 = question("1SPE-TRIGONOMETRIE", "1SPE-TRIGONOMETRIE-QCM.json", "Q9")
    assert "k \\in \\mathbb{Z}" in q9["enonce"]


def test_qcm_1spe_n_expose_plus_les_coquilles_editoriales_identifiees() -> None:
    local_q1 = question(
        "1SPE-DERIVATION-LOCAL", "1SPE-DERIVATION-LOCAL-QCM.json", "Q1"
    )
    second_q18 = question("1SPE-SECOND-DEGRE", "1SPE-SECDEG-QCM.json", "Q18")
    assert "taux de variation" in local_q1["enonce"]
    assert second_q18["enonce"].startswith("Une balle")


def test_qcm_obligatoires_n_exigent_pas_le_logarithme_ni_un_angle_oriente() -> None:
    global_q3 = question(
        "1SPE-DERIVATION-GLOBAL", "1SPE-DERIVATION-GLOBAL-QCM.json", "Q3"
    )
    suites_q14 = question("1SPE-SUITES", "1SPE-SUITES-QCM.json", "Q14")
    scalar_q9 = question(
        "1SPE-PRODUIT-SCALAIRE", "1SPE-PRODUIT-SCALAIRE-QCM.json", "Q9"
    )
    serialized = json.dumps([global_q3, suites_q14], ensure_ascii=False).lower()
    assert "\\ln" not in serialized
    assert "logarith" not in serialized
    assert "angle géométrique" in scalar_q9["enonce"]
