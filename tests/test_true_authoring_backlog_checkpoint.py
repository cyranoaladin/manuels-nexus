"""Le backlog gele : ce qui manque REELLEMENT, avant toute ecriture.

Ecrire contre un backlog gonfle recree exactement le remplissage que cette
campagne repare. Ces tests protegent la reference : elle doit rester
reproductible, exacte, et distinguer ce qui est a ECRIRE de ce qui est a
REVOIR.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "audit/TRUE_AUTHORING_BACKLOG_ESTABLISHED.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "backlog_checkpoint",
        ROOT / "scripts/build_true_authoring_backlog_checkpoint.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(CHECKPOINT.read_text(encoding="utf-8"))


def test_the_committed_checkpoint_matches_the_producer(producer) -> None:
    assert producer.main(["--check"]) == 0


def test_the_checkpoint_is_backed_by_a_green_full_run(payload: dict) -> None:
    """Un backlog gele sur une suite rouge n'a aucune autorite."""

    run = payload["validating_full_run"]
    assert run["failed"] == 0
    assert run["errors"] == 0
    assert run["rc"] == 0
    assert run["passed"] == run["collected"]
    assert len(run["source_sha"]) == 40
    assert len(run["log_sha256"]) == 64


def test_the_totals_close_exactly(payload: dict) -> None:
    totals = payload["totals"]
    assert (
        totals["cells_with_valid_content"]
        + totals["cells_with_indeterminate_credit"]
        + totals["AUTHORING_UNITS_REQUIRED_CURRENT"]
        == totals["cells"]
    )
    assert len(payload["authoring_units"]) == totals["AUTHORING_UNITS_REQUIRED_CURRENT"]
    assert len(set(payload["authoring_units"])) == len(payload["authoring_units"])
    assert sum(payload["per_manual"].values()) == len(payload["authoring_units"])
    assert sum(payload["per_role"].values()) == len(payload["authoring_units"])
    assert sum(payload["per_chapter"].values()) == len(payload["authoring_units"])


def test_review_debt_is_not_counted_as_authoring(payload: dict) -> None:
    """Une cellule a revoir n'est pas une cellule a ecrire.

    C'est la distinction qui evite de faire reecrire un contenu present : un
    clone dont le proprietaire n'est pas demontrable existe bel et bien, seule
    son appartenance est indeterminee.
    """

    assert "INDETERMINATE_CLONE_CREDIT" in payload["what_is_excluded"]
    assert payload["totals"]["cells_with_indeterminate_credit"] > 0
    assert payload["open_clone_debt"]["ambiguous_canonical_groups"] > 0

    coverage = json.loads(
        (ROOT / "audit/TRUE_PEDAGOGICAL_COVERAGE.json").read_text(encoding="utf-8")
    )
    frozen = set(payload["authoring_units"])
    for row in coverage["rows"]:
        key = f"{row['chapter']}/{row['capacity']}/{row['role']}"
        if row["state"] == "MISSING":
            assert key in frozen
        else:
            assert key not in frozen


def test_the_previous_measure_is_explained_unit_by_unit(payload: dict) -> None:
    """Pas de « -136 » sans nommer les 136."""

    previous = payload["previous_measure"]
    delta = json.loads(
        (ROOT / "audit/FALSE_MISSING_GAP_DELTA.json").read_text(encoding="utf-8")
    )
    assert previous["removed_as_false"] == delta["false_missing_gaps_removed"]
    assert len(delta["removed_units"]) == previous["removed_as_false"]
    assert delta["unexplained_removals"] == 0
    assert sum(previous["removal_classes"].values()) == previous["removed_as_false"]
    for row in delta["removed_units"]:
        assert row["satisfied_by"], row
        assert row["resolution_rules_that_recover_it"]
