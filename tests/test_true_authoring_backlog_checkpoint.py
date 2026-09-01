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


def test_only_an_established_checkpoint_is_backed_by_a_green_full_run(
    payload: dict,
) -> None:
    """Toute preuve de full run attachée au checkpoint doit être verte."""

    run = payload["validating_full_run"]
    if run is not None:
        assert run["failed"] == 0
        assert run["errors"] == 0
        assert run["rc"] == 0
        assert run["passed"] == run["collected"]
        assert len(run["source_sha"]) == 40
        assert len(run["log_sha256"]) == 64
    if payload["checkpoint_status"] != "ESTABLISHED":
        assert payload["checkpoint_status"] == "CANDIDATE_UNVALIDATED"
        assert payload["checkpoint"] == "TRUE_AUTHORING_BACKLOG_CANDIDATE"


def test_green_full_run_removes_only_the_technical_backlog_blocker(
    payload: dict,
) -> None:
    run = payload["validating_full_run"]
    assert run is not None
    assert run["source_sha"] == "6724cbf366df923e228b494e05157676780f2578"
    assert run["passed"] == run["collected"] == 9358
    assert "FULL_SUPPORTED_SUITE_NOT_GREEN" not in payload["establishment_blockers"]
    assert payload["establishment_blockers"] == [
        "SEMANTIC_ALIGNMENT_NOT_ESTABLISHED_COLLECTION_WIDE"
    ]


def test_the_totals_close_exactly(payload: dict) -> None:
    totals = payload["totals"]
    assert (
        totals["cells_with_declared_exact_identity"]
        + totals["cells_with_indeterminate_credit"]
        + totals["AUTHORING_UNITS_REQUIRED_CURRENT"]
        == totals["cells"]
    )
    assert len(payload["authoring_units"]) == totals["AUTHORING_UNITS_REQUIRED_CURRENT"]
    assert len(set(payload["authoring_units"])) == len(payload["authoring_units"])
    assert sum(payload["per_manual"].values()) == len(payload["authoring_units"])
    assert sum(payload["per_role"].values()) == len(payload["authoring_units"])
    assert sum(payload["per_chapter"].values()) == len(payload["authoring_units"])


def test_checkpoint_exposes_auditable_sets_for_every_projection(payload: dict) -> None:
    units = set(payload["authoring_units"])
    for dimension in ("per_manual", "per_chapter", "per_capacity", "per_role"):
        buckets = payload["authoring_unit_projections"][dimension]
        projected = [set(bucket["unit_ids"]) for bucket in buckets.values()]
        assert set().union(*projected) == units
        assert all(
            left.isdisjoint(right)
            for index, left in enumerate(projected)
            for right in projected[index + 1 :]
        )
        assert all(
            bucket["count"] == len(bucket["unit_ids"])
            for bucket in buckets.values()
        )
        assert all(
            bucket["set_digest"].startswith("sha256:")
            for bucket in buckets.values()
        )


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
    """La correction de mesure et l'authoring réel restent disjoints."""

    previous = payload["previous_measure"]
    delta = json.loads(
        (ROOT / "audit/FALSE_MISSING_GAP_DELTA.json").read_text(encoding="utf-8")
    )
    assert previous["removed_as_false"] == delta["false_missing_gaps_removed"]
    assert len(delta["removed_units"]) == previous["removed_as_false"]
    assert delta["unexplained_removals"] == len(delta["unexplained_units"])
    assert delta["unexplained_removals"] == 145
    assert delta["status"] == "GAP"
    assert sum(previous["removal_classes"].values()) == previous["removed_as_false"]
    assert payload["real_authoring_closure"]["count"] == delta[
        "real_authoring_closure"
    ]["count"]
    false_units = {
        f"{row['chapter']}/{row['capacity']}/{row['role']}"
        for row in delta["measurement_reclassification"]["units"]
    }
    authored_units = {
        f"{row['chapter']}/{row['capacity']}/{row['role']}"
        for row in delta["real_authoring_closure"]["units"]
    }
    assert false_units.isdisjoint(authored_units)
    for row in delta["removed_units"]:
        assert row["current_object_paths"], row
        assert row["canonical_capacity_uid"]
