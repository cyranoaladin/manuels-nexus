"""Le delta historique sépare erreur de mesure et écriture réelle."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit/FALSE_MISSING_GAP_DELTA.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "false_missing_gap_delta",
        ROOT / "scripts/build_false_missing_gap_delta.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload(producer) -> dict:
    return producer.build_delta()


def _keys(rows: list[dict]) -> set[str]:
    return {
        f"{row['chapter']}/{row['capacity']}/{row['role']}" for row in rows
    }


def test_historical_stages_are_named_and_close_exactly(payload: dict) -> None:
    assert payload["comparison_scope"] == {
        "roles": ["cours", "methodes", "exercices", "corriges", "remediation"],
        "reason": "les snapshots historiques ne mesuraient que ces cinq roles",
    }
    stages = payload["stages"]
    assert [stage["name"] for stage in stages] == [
        "LEGACY_MEASURE",
        "CAPACITY_IDENTITY_CORRECTED",
        "COUPLED_1NSI_AUTHORED",
        "CURRENT",
    ]
    # Les trois premieres etapes sont HISTORIQUES : elles ne bougent plus.
    # La derniere est l'etat courant, et elle bouge des qu'on ecrit ou qu'on
    # tranche une cellule -- la graver reviendrait a interdire de progresser.
    # Ce qui est verrouille est que l'equation FERME sur les valeurs du jour.
    assert [stage["authoring_units"] for stage in stages][:3] == [460, 324, 315]
    assert len({stage["backlog_set_digest"] for stage in stages}) == 4
    reconciliation = payload["delta_reconciliation"]
    assert reconciliation["holds"] is True
    attendue = (
        f"{reconciliation['legacy']}"
        f" - {reconciliation['gross_measurement_removals'] - payload['measurement_reclassification']['phases'][1]['count']}"
        f" - {reconciliation['real_authoring_closures']}"
        f" - {payload['measurement_reclassification']['phases'][1]['count']}"
        f" + {reconciliation['gaps_added_by_stricter_false_positive_rejection']}"
        f" = {reconciliation['current']}"
    )
    assert payload["equation"] == attendue
    assert stages[-1]["authoring_units"] == reconciliation["current"]


def test_measurement_reclassification_is_not_conflated_with_authoring(
    payload: dict,
) -> None:
    measurement = payload["measurement_reclassification"]
    authoring = payload["real_authoring_closure"]
    # La reclassification de MESURE et la fermeture par ECRITURE ne doivent
    # jamais etre confondues : c'est cela qu'on verrouille, pas leurs stocks.
    assert measurement["count"] == sum(measurement["per_class"].values())
    assert measurement["count"] == sum(p["count"] for p in measurement["phases"])
    assert set(measurement["per_class"]) == {
        "RECOVERED_EXACT_DECLARATION_SEMANTIC_REVIEW_PENDING",
        "RECLASSIFIED_AS_REVIEW_DEBT",
    }
    assert measurement["phases"][0]["count"] == 136      # phase historique figee
    assert authoring["count"] == 9
    assert _keys(measurement["units"]).isdisjoint(_keys(authoring["units"]))
    assert payload["total_delta_to_current"] == measurement["count"] - len(
        measurement["gaps_added"]
    ) + authoring["count"]
    assert payload["false_missing_gaps_removed"] == 0
    assert payload["proven_false_missing"]["units"] == []
    assert payload["authoring_decision_deferred_pending_semantic_review"][
        "count"
    ] == measurement["count"]


def test_every_removed_unit_keeps_transition_and_current_evidence_separate(
    payload: dict,
) -> None:
    rows = (
        payload["measurement_reclassification"]["units"]
        + payload["real_authoring_closure"]["units"]
    )
    assert rows
    for row in rows:
        assert row["canonical_capacity_uid"]
        assert row["transition_object_ids_digest"].startswith("sha256:")
        assert row["transition_object_paths_digest"].startswith("sha256:")
        assert row["transition_row_digest"].startswith("sha256:")
        assert row["current_object_ids_digest"].startswith("sha256:")
        assert row["current_object_paths_digest"].startswith("sha256:")


def test_transition_evidence_is_not_replaced_by_later_current_content(producer) -> None:
    base = {
        "manual": "1NSI",
        "canonical_capacity_uid": "1NSI::1NSI-X::C1",
        "state": "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED",
        "valid_object_ids": ["OLD"],
        "valid_object_paths": ["old.tex"],
        "indeterminate_object_ids": [],
        "indeterminate_object_paths": [],
    }
    current = {
        **base,
        "valid_object_ids": ["NEW"],
        "valid_object_paths": ["new.tex"],
    }
    row = producer._row(
        ("1NSI-X", "C1", "cours"),
        before_state="MISSING",
        transition_result_state=base["state"],
        transition_row=base,
        current_row=current,
        classification="TEST",
        why="fixture",
        valid_capacity_credit_claimed=False,
    )
    assert row["transition_object_ids"] == ["OLD"]
    assert row["current_object_ids"] == ["NEW"]
    assert row["transition_evidence_still_identical_current"] is False


def test_missing_to_indeterminate_never_counts_as_proven_false_missing(
    producer,
) -> None:
    row = {
        "classification": "RECLASSIFIED_AS_REVIEW_DEBT",
        "valid_capacity_credit_claimed": False,
    }
    proven, deferred = producer._partition_measurement_rows([row])
    assert proven == []
    assert deferred == [row]


def test_review_debt_is_never_described_as_valid_credit(payload: dict) -> None:
    review_rows = [
        row
        for row in payload["measurement_reclassification"]["units"]
        if row["classification"] == "RECLASSIFIED_AS_REVIEW_DEBT"
    ]
    # Le stock varie ; ce qui ne varie pas, c'est qu'une dette de revue n'est
    # JAMAIS presentee comme un credit de capacite valide.
    assert len(review_rows) == payload["measurement_reclassification"][
        "per_class"
    ]["RECLASSIFIED_AS_REVIEW_DEBT"]
    assert review_rows
    assert {row["before_state"] for row in review_rows} == {"MISSING"}
    assert {row["transition_result_state"] for row in review_rows} == {
        "INDETERMINATE_CLONE_CREDIT"
    }
    assert all(row["valid_capacity_credit_claimed"] is False for row in review_rows)


def test_no_stage_adds_an_unexplained_gap(payload: dict) -> None:
    # Les lacunes ajoutees sont celles qu'un rejet plus strict des faux
    # positifs fait apparaitre : leur nombre suit le corpus, mais il doit
    # rester exactement celui que la reconciliation declare.
    assert len(payload["measurement_reclassification"]["gaps_added"]) == payload[
        "delta_reconciliation"
    ]["gaps_added_by_stricter_false_positive_rejection"]
    assert payload["real_authoring_closure"]["gaps_added"] == []
    assert payload["status"] == "GAP"
    assert payload["unexplained_units"]


def test_committed_artifact_matches_the_producer(producer) -> None:
    expected = producer.render(producer.build_delta())
    assert ARTIFACT.read_text(encoding="utf-8") == expected
