"""Une proposition de barème se dérive ou se refuse — elle ne s'invente pas.

La politique fixe le format et interdit la granularité fictive : pas de
répartition uniforme, pas de demi-point partout, pas de sous-critère absent de
la solution. Ce module vérifie que chaque proposition vient bien du sujet et du
corrigé, que le crédit partiel n'apparaît que sur une décomposition réelle, et
que l'ambiguïté devient un drapeau plutôt qu'une invention.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_bareme_commentary_proposal as gate  # noqa: E402


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
#  Chaque question reçoit une proposition ou un drapeau
# ---------------------------------------------------------------------------


def test_every_question_is_either_proposed_or_flagged(
    payload: dict[str, Any],
) -> None:
    summary = payload["summary"]
    assert summary["QUESTIONS_WITHOUT_PROPOSAL_OR_FLAG"] == 0
    assert summary["QUESTIONS"] == (
        summary["PROPOSED"] + summary["PEDAGOGICAL_JUDGEMENT_REQUIRED"]
    )
    assert summary["ASSESSMENTS"] == 20
    assert summary["PROPOSED"] > 200


def test_a_proposal_carries_points_a_gesture_and_a_result(
    payload: dict[str, Any],
) -> None:
    for assessment in payload["assessments"]:
        for exercise in assessment["exercises"]:
            for question in exercise["questions"]:
                if question["verdict"] != "PROPOSED":
                    assert question["expected"] == "", question
                    assert question["partial_credit"] == "", question
                    assert question["why"].strip(), question
                    continue
                assert question["points"], question
                assert question["gesture"], question
                assert " — " in question["expected"], question


def test_the_mathematics_is_carried_verbatim(payload: dict[str, Any]) -> None:
    """Un barème qui déforme la formule qu'il évalue est pire qu'absent.

    Une première version « nettoyait » le LaTeX : `\\pi` disparaissait, et
    « 5π/6 » devenait « (5 )/(6) ». Les attendus doivent donc porter du LaTeX
    réel, et jamais une formule mutilée.
    """

    with_math = 0
    for assessment in payload["assessments"]:
        for exercise in assessment["exercises"]:
            for question in exercise["questions"]:
                expected = question["expected"]
                if "$" in expected:
                    with_math += 1
                    # Les délimiteurs vont par paires : une formule coupée en
                    # deux ne serait pas compilable.
                    assert expected.count("$") % 2 == 0, question
                # La trace de l'ancien mutilage : une fraction vidée.
                assert "( )/(" not in expected, question
    assert with_math > 100, "presque aucun attendu ne porte de mathématiques"


def test_no_expected_swallows_a_latex_comment(payload: dict[str, Any]) -> None:
    """Les corrigés séparent leurs exercices par des lignes de `%=====`."""

    for assessment in payload["assessments"]:
        for exercise in assessment["exercises"]:
            for question in exercise["questions"]:
                expected = question["expected"]
                assert "%===" not in expected, question
                # Un `\%` échappé n'est pas un commentaire : c'est un signe
                # pour cent, et « 0,06 % » a parfaitement sa place dans un
                # attendu. Seul le `%` NON échappé ouvre un commentaire.
                assert not __import__("re").search(r"(?<!\\)%", expected), question


# ---------------------------------------------------------------------------
#  Le crédit partiel n'apparaît que sur une décomposition réelle
# ---------------------------------------------------------------------------


def test_partial_credit_only_where_the_correction_separates_its_steps(
    payload: dict[str, Any],
) -> None:
    for assessment in payload["assessments"]:
        for exercise in assessment["exercises"]:
            for question in exercise["questions"]:
                if not question["partial_credit"]:
                    continue
                assert question.get("separable_steps", 0) >= 2, question
                assert question["answer_scope"] == "question", question
    # Il en existe, sinon la règle ne serait jamais exercée -- et il n'y en a
    # pas partout, sinon elle serait devenue une répartition uniforme.
    proposed = payload["summary"]["PROPOSED"]
    partial = payload["summary"]["PARTIAL_CREDIT_PROPOSED"]
    assert 0 < partial < proposed // 4, (partial, proposed)


def test_a_single_step_answer_gets_no_partial_credit() -> None:
    """Plein crédit ou rien : la politique l'autorise explicitement."""

    question = {
        "question": "Q1",
        "points": "1 pt",
        "statement": "Calculer $u_1$.",
        "correction_answer": "$u_1 = 7$.",
        "correction_answer_scope": "question",
        "competence": None,
    }

    row = gate.propose(question)

    assert row["verdict"] == "PROPOSED"
    assert row["partial_credit"] == ""


def test_points_that_do_not_divide_on_the_half_point_grid_are_refused() -> None:
    """Pas de granularité fictive : une coupure impossible n'est pas proposée."""

    assert gate.divide(Fraction(1), 3) is None, "un point ne se coupe pas en deux"
    assert gate.divide(Fraction(3), 1) is None, "sans étape séparable, pas de crédit"
    split = gate.divide(Fraction(3), 2)
    assert split is not None
    assert sum(split) == Fraction(3)
    for part in split:
        assert part % Fraction(1, 2) == 0


def test_an_ambiguous_question_is_flagged_not_invented() -> None:
    """Sans geste lisible ni résultat repérable, on demande un humain."""

    row = gate.propose(
        {
            "question": "Q1",
            "points": "2 pts",
            "statement": "Lina observe la courbe.",
            "correction_answer": "",
            "correction_answer_scope": "absent",
            "competence": None,
        }
    )

    assert row["verdict"] == "PEDAGOGICAL_JUDGEMENT_REQUIRED"
    assert row["expected"] == ""
    assert row["partial_credit"] == ""


def test_an_unvalued_question_is_flagged() -> None:
    """Les deux GEOREP ne valuent aucune question : rien à proposer."""

    row = gate.propose(
        {
            "question": "Q1",
            "points": None,
            "statement": "Calculer les coordonnées.",
            "correction_answer": "$(2\\,;\\,-1)$.",
            "correction_answer_scope": "question",
            "competence": None,
        }
    )

    assert row["verdict"] == "PEDAGOGICAL_JUDGEMENT_REQUIRED"
    assert "ne value pas" in row["why"]


# ---------------------------------------------------------------------------
#  Rien n'est écrit dans les corrigés
# ---------------------------------------------------------------------------


def test_the_proposals_stay_proposals(payload: dict[str, Any]) -> None:
    assert payload["approves_nothing"] is True
    assert payload["policy"] == "RESOLVED_BY_HUMAN_DECISION_2026_09_04"
    assert "revue de chapitre" in payload["these_are_proposals_not_content"]
    # Aucun corrigé ne porte encore la couche : elle entre par la revue.
    corrections = sorted(
        (ROOT / "Mathematiques/manuel-maths/chapitres").glob(
            "1SPE-*/evaluations/*-corrige.tex"
        )
    )
    assert corrections
    for path in corrections:
        text = path.read_text(encoding="utf-8")
        assert "Attendu :" not in text, path


def test_the_gesture_list_is_read_from_the_corpus_not_guessed() -> None:
    """Chaque verbe déclaré doit exister dans un énoncé du corpus."""

    subjects = sorted(
        (ROOT / "Mathematiques/manuel-maths/chapitres").glob(
            "1SPE-*/evaluations/*[AB].tex"
        )
    )
    corpus = " ".join(
        path.read_text(encoding="utf-8").lower() for path in subjects
    )
    for pattern, name in gate.GESTURES:
        assert __import__("re").search(pattern, corpus), name
