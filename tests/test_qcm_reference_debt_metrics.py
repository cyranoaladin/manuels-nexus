"""Le nombre 108 ne doit plus jamais designer deux ensembles differents.

Des points de controle anterieurs annoncaient "108 renvois TSPE casses" ; la
mesure courante annonce "108 distracteurs sans diagnostic ou sans renvoi". Ces
tests fixent deux metriques nommees, chacune avec son ensemble exact, et
interdisent qu'un futur rapport les confonde a nouveau.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit" / "QCM_REFERENCE_DEBT_METRICS.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "qcm_reference_debt", ROOT / "scripts" / "build_qcm_reference_debt_metrics.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload(producer):
    return producer.build_metrics()


def _metrics(payload: dict) -> dict[str, dict]:
    return {entry["metric"]: entry for entry in payload["metrics"]}


def test_the_committed_artifact_matches_the_producer(producer, payload) -> None:
    assert ARTIFACT.read_text(encoding="utf-8") == producer.render_json(payload)


def test_the_two_metrics_are_distinct_objects(payload) -> None:
    metrics = _metrics(payload)
    broken = metrics["TSPE_BROKEN_REMEDIATION_REFERENCES"]
    missing = metrics["GLOBAL_DISTRACTORS_MISSING_DIAGNOSTIC_OR_REFERENCE"]

    assert broken["metric"] != missing["metric"]
    assert broken["set_digest"] != missing["set_digest"]
    assert payload["disambiguation"]["same_set"] is False


def test_every_metric_carries_its_exact_ids_and_distribution(payload) -> None:
    for metric in payload["metrics"]:
        assert len(metric["ids"]) == metric["count"]
        assert len(set(metric["ids"])) == metric["count"]
        assert sum(metric["by_chapter"].values()) == metric["count"]


def test_the_or_is_decomposed_exactly(payload) -> None:
    metrics = _metrics(payload)
    total = metrics["GLOBAL_DISTRACTORS_MISSING_DIAGNOSTIC_OR_REFERENCE"]["count"]

    assert (
        metrics["MISSING_DIAGNOSTIC_ONLY"]["count"]
        + metrics["MISSING_REFERENCE_ONLY"]["count"]
        + metrics["MISSING_BOTH"]["count"]
        == total
    )
    assert payload["invariants"]["three_way_split_is_exact"] is True


def test_the_contract_requires_both_and_targets_zero(payload) -> None:
    contract = payload["contract"]
    metrics = _metrics(payload)

    assert contract["diagnostic_required"] is True
    assert contract["reference_required"] is True
    assert contract["objective"] == {
        "REQUIRED_DISTRACTOR_DIAGNOSTIC_MISSING": 0,
        "REQUIRED_REMEDIATION_REFERENCE_MISSING": 0,
    }
    assert (
        metrics["REQUIRED_DISTRACTOR_DIAGNOSTIC_MISSING"]["count"]
        == metrics["MISSING_DIAGNOSTIC_ONLY"]["count"]
        + metrics["MISSING_BOTH"]["count"]
    )
    assert (
        metrics["REQUIRED_REMEDIATION_REFERENCE_MISSING"]["count"]
        == metrics["MISSING_REFERENCE_ONLY"]["count"]
        + metrics["MISSING_BOTH"]["count"]
    )


def test_every_present_reference_resolves(payload) -> None:
    """Un renvoi present doit designer un objet qui existe."""

    metrics = _metrics(payload)
    assert payload["invariants"]["unparsed_is_zero"] is True
    assert payload["unparsed_references"] == []
    assert metrics["GLOBAL_BROKEN_REMEDIATION_REFERENCES"]["count"] == 0
    assert payload["inventory"]["references_analysed"] > 0
