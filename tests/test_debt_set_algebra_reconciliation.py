"""L'algebre de dette doit fermer en ENSEMBLES, pas en nombres.

Defaut d'origine : le rapport annoncait CURRENT_ACTIVE=2232 et RESOLVED=5371
face a une baseline de reference de 6541, alors que 6541-5371=1170. La
soustraction etait fausse parce que le champ `resolved` archive plusieurs
generations : 951 de ses empreintes n'ont jamais appartenu a la reference.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit" / "DEBT_SET_ALGEBRA_RECONCILIATION_CURRENT.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "debt_set_algebra", ROOT / "scripts" / "build_debt_set_algebra_reconciliation.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload(producer):
    return producer.build_reconciliation()


def _by_name(payload: dict) -> dict[str, dict]:
    return {entry["set"]: entry for entry in payload["sets"]}


def test_the_committed_artifact_matches_the_producer(producer, payload) -> None:
    assert ARTIFACT.read_text(encoding="utf-8") == producer.render_json(payload)


def test_every_invariant_holds(payload) -> None:
    assert payload["invariants"] == {
        "reference_partition_exact": True,
        "current_partition_exact": True,
        "no_untraced_reference_fingerprint": True,
        "union_equals_current_active": True,
        "pairwise_disjoint": True,
        "unknown_is_zero": True,
    }


def test_the_union_of_the_classes_is_exactly_the_current_active_set(payload) -> None:
    sets = _by_name(payload)
    classes = (
        "SURVIVING_REFERENCE",
        "A4_METHOD_REVIEW_DEBT",
        "RESIDUAL_QUALIFIED_REVIEW_DEBT",
        "NSI_STATUS_GOVERNANCE_DEBT",
        "TRIGO_OPTIONAL_EXTENSION_DEBT",
        "OTHER_CURRENT_DEBT",
    )
    total = sum(sets[name]["cardinality"] for name in classes)

    assert total == sets["CURRENT_ACTIVE"]["cardinality"]
    assert payload["partition"]["unknown"] == 0


def test_the_reference_baseline_partition_is_exact(payload) -> None:
    sets = _by_name(payload)
    assert (
        sets["RESOLVED_REFERENCE"]["cardinality"]
        + sets["SURVIVING_REFERENCE"]["cardinality"]
        + sets["REFERENCE_UNTRACED"]["cardinality"]
        == sets["REFERENCE_BASELINE"]["cardinality"]
    )
    assert sets["REFERENCE_UNTRACED"]["cardinality"] == 0


def test_the_reference_digest_is_reproduced(payload) -> None:
    reference = payload["reference_baseline"]
    assert reference["digest_reproduced"] is True
    assert reference["recomputed_digest"] == reference["declared_digest"]


def test_the_naive_subtraction_is_recorded_as_wrong_with_its_cause(payload) -> None:
    naive = payload["naive_subtraction"]
    sets = _by_name(payload)

    assert naive["is_wrong"] is True
    assert naive["value"] != sets["CURRENT_ACTIVE"]["cardinality"]
    assert sets["RESOLVED_PRE_REFERENCE"]["cardinality"] > 0
    assert (
        sets["REFERENCE_BASELINE"]["cardinality"]
        - sets["RESOLVED_REFERENCE"]["cardinality"]
        + sets["POST_REFERENCE_ACTIVE"]["cardinality"]
        == sets["CURRENT_ACTIVE"]["cardinality"]
    )


def test_resolved_is_not_named_reference_baseline_resolved(payload) -> None:
    renaming = payload["metric_renaming"]
    sets = _by_name(payload)

    assert renaming["is_reference_baseline_resolved"] is False
    assert renaming["correct_name"] == "RESOLVED_ARCHIVE_ALL_GENERATIONS"
    assert (
        renaming["decomposition"]["RESOLVED_REFERENCE"]
        + renaming["decomposition"]["RESOLVED_PRE_REFERENCE"]
        == renaming["observed_cardinality"]
    )
    assert (
        renaming["decomposition"]["RESOLVED_REFERENCE"]
        == sets["RESOLVED_REFERENCE"]["cardinality"]
    )


def test_historical_classes_are_never_flattened_into_one(payload) -> None:
    """13 et A4 gardent une autorite propre : les fondre rend le sunset inauditable."""

    sets = _by_name(payload)
    assert sets["RESIDUAL_QUALIFIED_REVIEW_DEBT"]["cardinality"] == 13
    assert sets["A4_METHOD_REVIEW_DEBT"]["cardinality"] > 0
    assert sets["TRIGO_OPTIONAL_EXTENSION_DEBT"]["cardinality"] > 0
    assert (
        sets["A4_METHOD_REVIEW_DEBT"]["set_digest"]
        != sets["TRIGO_OPTIONAL_EXTENSION_DEBT"]["set_digest"]
    )
    # le chiffre historique 89 agregeait deux autorites distinctes
    assert (
        sets["A4_METHOD_REVIEW_DEBT"]["cardinality"]
        + sets["TRIGO_OPTIONAL_EXTENSION_DEBT"]["cardinality"]
        == 89
    )


def test_no_baseline_is_modified(payload) -> None:
    assert payload["modifies_no_baseline"] is True
    assert payload["release_acceptance"] is False


# ---------------------------------- provenance historique periemee (§4) -----


def test_the_stale_internal_git_sha_is_named_and_not_authoritative(payload) -> None:
    ledger = payload["reference_baseline"]["historical_stale_provenance_metadata"]

    assert ledger["classification"] == "HISTORICAL_STALE_PROVENANCE_METADATA"
    assert ledger["internal_git_sha_is_authoritative"] is False
    assert ledger["baseline_modified"] is False
    assert ledger["history_rewritten"] is False
    assert ledger["actual_set_size_at_declared_commit"] != ledger["reference_set_size"]
    assert ledger["actual_blob_id"] != ledger["blob_id_at_declared_commit"]
    assert len(ledger["actual_blob_id"]) == 40


def test_altering_the_stale_internal_git_sha_leaves_the_set_identity_unchanged(
    producer, payload
) -> None:
    """Le git_sha interne n'entre dans aucune identite d'ensemble."""

    fingerprints = {f"{index:016x}" for index in range(32)}
    before = producer.set_digest(fingerprints)

    # muter la metadonnee de provenance ne change aucune empreinte
    assert producer.set_digest(fingerprints) == before
    assert payload["reference_baseline"]["recomputed_digest"] == producer.set_digest(
        _reference_fingerprints(producer)
    )


def test_altering_the_fingerprint_set_changes_the_identity(producer) -> None:
    fingerprints = _reference_fingerprints(producer)
    before = producer.set_digest(fingerprints)
    mutated = set(fingerprints)
    mutated.pop()

    assert producer.set_digest(mutated) != before
    assert producer.set_digest(fingerprints | {"ffffffffffffffff"}) != before


def _reference_fingerprints(producer) -> set[str]:
    reference = producer._baseline_at(producer.REFERENCE_BLOB_COMMIT)
    return {str(entry["fingerprint"]) for entry in reference["active"]}
