"""Régressions de clôture scientifique des QCM de Terminale spécialité.

Ces contrôles figent les rattachements de capacité et interdisent le retour des
diagnostics génériques ou causalement faux relevés par la revue indépendante.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _question(chapter: str, question_id: str) -> dict:
    source = next((ROOT / "chapitres" / chapter / "qcm").glob("*-QCM.json"))
    data = json.loads(source.read_text(encoding="utf-8"))
    return next(question for question in data["questions"] if question["id"] == question_id)


EXPECTED_CAPACITIES = {
    ("TSPE-CALCUL-INTEGRAL", "Q1"): "C2",
    ("TSPE-CALCUL-INTEGRAL", "Q2"): "C2",
    ("TSPE-CALCUL-INTEGRAL", "Q5"): "C2",
    ("TSPE-COMBINATOIRE", "Q1"): "C2",
    ("TSPE-COMBINATOIRE", "Q2"): "C2",
    ("TSPE-COMBINATOIRE", "Q5"): "C4",
    ("TSPE-DERIVATION-CONVEXITE", "Q7"): "C5",
    ("TSPE-DERIVATION-CONVEXITE", "Q9"): "C5",
    ("TSPE-DERIVATION-CONVEXITE", "Q11"): "C5",
    ("TSPE-LIMITES-FONCTIONS", "Q11"): "C1",
    ("TSPE-LIMITES-FONCTIONS", "Q12"): "C1",
    ("TSPE-LIMITES-FONCTIONS", "Q13"): "C1",
    ("TSPE-LIMITES-FONCTIONS", "Q15"): "C1",
    ("TSPE-PROBABILITES", "Q1"): "C5",
    ("TSPE-PROBABILITES", "Q4"): "C8",
    ("TSPE-PROBABILITES", "Q5"): "C9",
    ("TSPE-TRIGONOMETRIE", "Q2"): "C2",
    ("TSPE-TRIGONOMETRIE", "Q3"): "C2",
}


TARGETED_GENERIC_DIAGNOSTICS = {
    ("TSPE-CALCUL-INTEGRAL", "Q1", "D"),
    ("TSPE-CALCUL-INTEGRAL", "Q5", "B"),
    ("TSPE-COMBINATOIRE", "Q2", "B"),
    ("TSPE-COMBINATOIRE", "Q3", "C"),
    ("TSPE-COMBINATOIRE", "Q4", "D"),
    ("TSPE-COMBINATOIRE", "Q5", "A"),
    ("TSPE-COMBINATOIRE", "Q5", "B"),
    ("TSPE-COMBINATOIRE", "Q5", "C"),
    ("TSPE-LIMITES-FONCTIONS", "Q3", "D"),
    ("TSPE-SUITES-LIMITES", "Q5", "A"),
    ("TSPE-SUITES-LIMITES", "Q5", "C"),
}

for chapter, questions in {
    "TSPE-DERIVATION-CONVEXITE": {
        "Q1": "ACD", "Q2": "ACD", "Q4": "BCD", "Q5": "ABD",
        "Q7": "BCD", "Q8": "ABD", "Q9": "ACD", "Q10": "BCD",
        "Q12": "BCD", "Q13": "ACD", "Q14": "BCD",
    },
    "TSPE-PROBABILITES": {
        "Q1": "ACD", "Q2": "ACD", "Q3": "ACD", "Q5": "ACD",
        "Q6": "BCD",
    },
    "TSPE-TRIGONOMETRIE": {
        "Q1": "ACD", "Q2": "ACD", "Q3": "ACD", "Q4": "ACD",
    },
}.items():
    for question_id, letters in questions.items():
        TARGETED_GENERIC_DIAGNOSTICS.update(
            (chapter, question_id, letter) for letter in letters
        )


TARGETED_INVALID_DIAGNOSTICS = {
    ("TSPE-CALCUL-INTEGRAL", "Q1", "C"): "facteur $1/3$",
    ("TSPE-CALCUL-INTEGRAL", "Q2", "A"): "$f(1)=2$",
    ("TSPE-CALCUL-INTEGRAL", "Q2", "B"): "$f(4)=8$",
    ("TSPE-CALCUL-INTEGRAL", "Q2", "D"): "integrale vaut $16$",
    ("TSPE-CONTINUITE", "Q2", "A"): "signe de $f'$",
    ("TSPE-CONTINUITE", "Q13", "B"): "ne garantit ni que la suite est bornee",
}


HISTORICAL_EXPECTED_ANSWERS_AND_CAPACITIES = {
    ("TSPE-DERIVATION-CONVEXITE", "Q3"): ("B", "C1"),
    ("TSPE-DERIVATION-CONVEXITE", "Q6"): ("B", "C2"),
    ("TSPE-DERIVATION-CONVEXITE", "Q15"): ("A", "C6"),
    ("TSPE-PROBABILITES", "Q4"): ("A", "C8"),
    ("TSPE-TRIGONOMETRIE", "Q5"): ("B", "C2"),
    ("TSPE-LOGARITHME", "Q1"): ("B", "C1"),
    ("TSPE-LOGARITHME", "Q2"): ("B", "C3"),
    ("TSPE-LOGARITHME", "Q3"): ("C", "C2"),
    ("TSPE-LOGARITHME", "Q4"): ("B", "C4"),
    ("TSPE-LOGARITHME", "Q5"): ("B", "C1"),
    ("TSPE-GEOMETRIE-ESPACE", "Q1"): ("C", "C3"),
    ("TSPE-GEOMETRIE-ESPACE", "Q2"): ("B", "C7"),
    ("TSPE-GEOMETRIE-ESPACE", "Q3"): ("A", "C13"),
    ("TSPE-GEOMETRIE-ESPACE", "Q4"): ("A", "C12"),
    ("TSPE-GEOMETRIE-ESPACE", "Q5"): ("B", "C11"),
    ("TSPE-PRIMITIVES-EQDIFF", "Q1"): ("C", "C1"),
    ("TSPE-PRIMITIVES-EQDIFF", "Q2"): ("C", "C4"),
    ("TSPE-PRIMITIVES-EQDIFF", "Q3"): ("B", "C5"),
    ("TSPE-PRIMITIVES-EQDIFF", "Q4"): ("A", "C2"),
    ("TSPE-PRIMITIVES-EQDIFF", "Q5"): ("B", "C3"),
}


BANNED_GENERIC_FRAGMENTS = (
    "Consulter le cours correspondant",
    "Erreur de facteur",
    "Primitive incomplete",
    "Erreur de denominateur",
    "Confusions avec",
    "Relation de recurrence fausse",
    "Erreur sur l'indice",
    "Choix de l'indice",
    "Confusion avec une autre forme",
    "Erreur de calcul dans",
    "resolu $\\ell = 0{,}9\\ell + 20$ incorrectement",
)


def test_les_qcm_sont_rattaches_a_la_capacite_quils_evaluent() -> None:
    assert len(EXPECTED_CAPACITIES) == 18
    for (chapter, question_id), capacity in EXPECTED_CAPACITIES.items():
        assert _question(chapter, question_id)["capacite"] == capacity


def test_les_renvois_directs_suivent_les_capacites_corrigees() -> None:
    for chapter, question_id in EXPECTED_CAPACITIES:
        question = _question(chapter, question_id)
        for diagnostic in question["diagnostics"].values():
            renvoi = diagnostic.get("renvoi", "")
            if re.match(r"C\d+", renvoi):
                assert renvoi.startswith(question["capacite"]), (
                    f"{chapter}/{question_id}: {renvoi} != {question['capacite']}"
                )


def test_les_diagnostics_generiques_tspe_sont_remplaces_par_un_modele_derreur() -> None:
    assert len(TARGETED_GENERIC_DIAGNOSTICS) == 71
    for chapter, question_id, letter in TARGETED_GENERIC_DIAGNOSTICS:
        error = _question(chapter, question_id)["diagnostics"][letter]["erreur"]
        assert len(error) >= 60, f"{chapter}/{question_id}/{letter}: {error}"
        assert not any(fragment in error for fragment in BANNED_GENERIC_FRAGMENTS)


def test_les_six_diagnostics_causalement_faux_restants_sont_corriges() -> None:
    for (chapter, question_id, letter), expected in TARGETED_INVALID_DIAGNOSTICS.items():
        error = _question(chapter, question_id)["diagnostics"][letter]["erreur"]
        assert expected in error, f"{chapter}/{question_id}/{letter}: {error}"


def test_convexite_q12_ne_propose_pas_deux_proprietes_vraies() -> None:
    question = _question("TSPE-DERIVATION-CONVEXITE", "Q12")

    assert question["correcte"] == "A"
    assert question["options"]["D"] == "au-dessus de ses tangentes et de ses cordes"
    assert "au-dessous de ses cordes" in question["diagnostics"]["D"]["erreur"]


def test_integrales_c1_et_c3_sont_evaluees_par_des_questions_dediees() -> None:
    encadrement = _question("TSPE-CALCUL-INTEGRAL", "Q3")
    comparaison = _question("TSPE-CALCUL-INTEGRAL", "Q4")

    assert encadrement["capacite"] == "C1"
    assert encadrement["correcte"] == "B"
    assert encadrement["options"]["B"] == "$6 \\leqslant I \\leqslant 15$"
    assert comparaison["capacite"] == "C3"
    assert comparaison["correcte"] == "A"
    assert "\\int_0^1 f" in comparaison["options"]["A"]


def test_combinatoire_c1_et_c3_sont_evaluees_par_des_questions_dediees() -> None:
    representation = _question("TSPE-COMBINATOIRE", "Q3")
    somme = _question("TSPE-COMBINATOIRE", "Q4")

    assert representation["capacite"] == "C1"
    assert representation["correcte"] == "B"
    assert "arbre" in representation["options"]["B"]
    assert "$2\\times3\\times4=24$" in representation["options"]["B"]
    assert somme["capacite"] == "C3"
    assert somme["correcte"] == "A"
    assert "2^n" in somme["options"]["A"]


def test_les_qcm_tspe_historiques_ont_les_bonnes_cles_et_capacites() -> None:
    assert len(HISTORICAL_EXPECTED_ANSWERS_AND_CAPACITIES) == 20
    for (chapter, question_id), (answer, capacity) in (
        HISTORICAL_EXPECTED_ANSWERS_AND_CAPACITIES.items()
    ):
        question = _question(chapter, question_id)
        assert question["correcte"] == answer, f"{chapter}/{question_id}: mauvaise cle"
        assert question["capacite"] == capacity, (
            f"{chapter}/{question_id}: {question['capacite']} != {capacity}"
        )


def test_les_diagnostics_tspe_historiques_expliquent_une_erreur_causale() -> None:
    for chapter, question_id in HISTORICAL_EXPECTED_ANSWERS_AND_CAPACITIES:
        question = _question(chapter, question_id)
        assert set(question["diagnostics"]) == set(question["options"]) - {
            question["correcte"]
        }
        for letter, diagnostic in question["diagnostics"].items():
            error = diagnostic["erreur"]
            assert len(error) >= 60, f"{chapter}/{question_id}/{letter}: {error}"
            assert "Consulter le cours" not in error


def test_les_questions_tspe_historiques_nont_plus_de_reponse_dupliquee_ou_incomplete() -> None:
    derivation = _question("TSPE-DERIVATION-CONVEXITE", "Q3")
    trigonometrie = _question("TSPE-TRIGONOMETRIE", "Q5")
    geometrie = _question("TSPE-GEOMETRIE-ESPACE", "Q3")

    assert derivation["options"]["B"] != derivation["options"]["D"]
    assert "points critiques interieurs" in trigonometrie["options"]["B"]
    assert "bornes" in trigonometrie["options"]["B"]
    assert geometrie["options"]["D"] == "$(-2,3,1)$."


def test_probabilites_q4_presente_lindependance_comme_une_condition_suffisante() -> None:
    question = _question("TSPE-PROBABILITES", "Q4")

    assert "est garantie lorsque" in question["enonce"]
    assert "necessite" not in question["enonce"]
    assert question["correcte"] == "A"


def test_derivation_q6_distingue_les_extrema_locaux_des_extrema_globaux() -> None:
    question = _question("TSPE-DERIVATION-CONVEXITE", "Q6")

    assert "extrema locaux" in question["enonce"]
    assert "maximum local" in question["options"]["B"]
    assert "minimum local" in question["options"]["B"]
