"""Un artefact de rapport ne doit pas etre perime par le commit qui le publie.

Defaut mesure : audit/QCM_GAP_METRICS.json portait un champ `source_sha` fige
au HEAD de sa generation. Des que le commit de publication du rapport tombait,
ce champ designait un commit anterieur et la provenance devenait "stale" alors
que les valeurs n'avaient pas bouge d'un iota. La semantique retenue est celle
deja adoptee ailleurs dans ce depot : OBSERVED_SOURCE_SHA constate, et une
autorite de fraicheur portee par un digest de contenu non auto-referent.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GAP_METRICS = ROOT / "audit" / "QCM_GAP_METRICS.json"


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(GAP_METRICS.read_text(encoding="utf-8"))


def test_no_report_artifact_pins_a_bare_source_sha(payload: dict) -> None:
    assert "source_sha" not in payload
    assert payload["freshness_authority"] == "source_digest"
    assert isinstance(payload["observed_source_sha"], str)
    assert len(payload["observed_source_sha"]) == 40


def test_the_freshness_digest_is_computed_over_declared_inputs(payload: dict) -> None:
    import hashlib

    inputs = payload["source_inputs"]
    assert inputs, "la provenance doit nommer ses entrees"
    for row in inputs:
        source = ROOT / row["path"]
        assert source.is_file(), row["path"]
        assert row["sha256"] == "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()

    recomputed = hashlib.sha256(
        json.dumps(inputs, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()
    assert payload["source_digest"] == "sha256:" + recomputed


def test_the_freshness_digest_is_not_self_referential(payload: dict) -> None:
    declared = {row["path"] for row in payload["source_inputs"]}

    assert "audit/QCM_GAP_METRICS.json" not in declared
    assert not any(path.startswith("audit/QCM_GAP") for path in declared)
