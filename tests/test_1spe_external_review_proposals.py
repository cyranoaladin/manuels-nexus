"""Une recommandation de revue externe n'est pas un verdict humain.

Elle entre dans le dossier comme proposition, confrontée au manuel courant, et
elle ne fabrique ni identité, ni reçu, ni barème matérialisé. Ce module vérifie
les trois : ce qui est enregistré correspond au manuel, rien n'est matérialisé,
personne n'est nommé.
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

import build_1spe_external_review_proposals as gate  # noqa: E402


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


def test_every_recommendation_found_its_question(payload: dict[str, Any]) -> None:
    for metric in gate.BLOCKING:
        assert payload["summary"][metric] == 0, metric
    assert payload["summary"]["GEOREP_ALLOCATIONS"] == 34
    assert payload["summary"]["PROBABILITY_EXPECTATIONS"] == 3


def test_the_georep_grid_totals_twenty_on_each_variant(
    payload: dict[str, Any],
) -> None:
    """Cinq exercices à quatre points : c'est ce que le sujet déclare."""

    for object_id in gate.GEOREP_OBJECTS:
        rows = [
            row
            for row in payload["georep_allocations"]
            if row["object_id"] == object_id
        ]
        assert len(rows) == 17, object_id
        total = sum(
            Fraction(row["points"].split()[0].replace(",", ".")) for row in rows
        )
        assert total == 20, (object_id, total)


def test_the_two_variants_carry_the_same_grid(payload: dict[str, Any]) -> None:
    grids = {
        object_id: [
            (row["exercise"], row["points"])
            for row in payload["georep_allocations"]
            if row["object_id"] == object_id
        ]
        for object_id in gate.GEOREP_OBJECTS
    }
    assert grids["1SPE-GEOREP-EV-A"] == grids["1SPE-GEOREP-EV-B"]


def test_the_probability_expectations_carry_their_result(
    payload: dict[str, Any],
) -> None:
    # Deux des trois portent le même label « Q4 » : c'est l'exercice qui les
    # distingue, et les confondre masquerait une recommandation perdue.
    results = {
        (row["object_id"], row["exercise"], row["question"])
        for row in payload["probability_expectations"]
    }
    assert len(results) == 3
    joined = " ".join(row["expected"] for row in payload["probability_expectations"])
    assert "P_G(R) = \\dfrac{3}{4}" in joined
    assert "P_G(B) = \\dfrac{3}{5}" in joined
    assert "41" in joined
    for row in payload["probability_expectations"]:
        assert row["points"] == "1 pt"
        assert row["provenance"] == gate.PROVENANCE


def test_nothing_here_is_a_human_verdict(payload: dict[str, Any]) -> None:
    assert payload["approves_nothing"] is True
    assert payload["provenance"] == "AI_REVIEW_RECOMMENDATION"
    assert payload["summary"]["HUMAN_RECEIPTS_CREATED"] == 0
    assert payload["summary"]["MATERIALISED_BAREMES"] == 0
    blob = json.dumps(payload, ensure_ascii=False)
    for name in ("Claude", "OpenAI", "Anthropic", "ChatGPT", "reviewer_id"):
        assert name not in blob, name
    for row in payload["georep_allocations"] + payload["probability_expectations"]:
        assert row["status"] == "PROPOSED_BY_EXTERNAL_REVIEW"


# ---------------------------------------------------------------------------
#  Ce que la confrontation doit refuser
# ---------------------------------------------------------------------------


def test_an_allocation_that_misses_the_declared_total_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Une grille qui ne tombe pas sur le total du sujet n'est pas enregistrée."""

    wrong = {number: list(values) for number, values in gate.GEOREP_ALLOCATION.items()}
    wrong[1] = ["1", "1", "1", "0,5"]
    monkeypatch.setattr(gate, "GEOREP_ALLOCATION", wrong)

    result = gate.build()

    assert result["summary"]["ALLOCATION_NOT_MATCHING_DECLARED_TOTAL"] >= 1
    assert gate.main(["--check"]) == 1


def test_an_allocation_with_the_wrong_number_of_questions_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wrong = {number: list(values) for number, values in gate.GEOREP_ALLOCATION.items()}
    wrong[2] = ["1", "1", "1", "1"]
    monkeypatch.setattr(gate, "GEOREP_ALLOCATION", wrong)

    result = gate.build()

    faults = result["allocations_not_matching_declared_total"]
    assert any("memes questions" in row["why"] for row in faults)


def test_an_expectation_on_a_question_the_subject_values_differently_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    altered = [dict(row) for row in gate.PROBABILITY_EXPECTATIONS]
    altered[0]["points"] = "3 pts"
    monkeypatch.setattr(gate, "PROBABILITY_EXPECTATIONS", tuple(altered))

    result = gate.build()

    assert result["summary"]["POINTS_DISAGREEING_WITH_SUBJECT"] == 1
    assert result["points_disagreeing_with_subject"][0]["subject_says"] == "1 pt"


def test_an_expectation_on_a_question_that_does_not_exist_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    altered = [dict(row) for row in gate.PROBABILITY_EXPECTATIONS]
    altered[0]["question"] = "Q99"
    monkeypatch.setattr(gate, "PROBABILITY_EXPECTATIONS", tuple(altered))

    result = gate.build()

    assert result["summary"]["RECOMMENDATION_WITHOUT_A_QUESTION"] == 1
