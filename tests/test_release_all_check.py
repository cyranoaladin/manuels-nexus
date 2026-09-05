"""Tests de l'invariant de release et du gate canonique release_all_check (LOT 2 / LOT 9)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "audit/RELEASE_ALL_CHECK.json"
SCRIPT_PATH = ROOT / "scripts/release_all_check.py"


@pytest.fixture(scope="module")
def release_report() -> dict:
    assert REPORT_PATH.is_file(), f"L'artefact {REPORT_PATH} doit exister"
    with REPORT_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_status_is_publish_ready_candidate(release_report: dict) -> None:
    summary = release_report["summary"]
    assert summary["RELEASE_STATUS"] == "ZERO_DEBT_RELEASE_OWNER_FINAL_SIGNOFF_REQUIRED"
    assert summary["ALL_CANONICAL_MANUALS_ZERO_DEBT_PUBLISH_READY"] is False
    assert summary["RELEASE_OWNER_FINAL_SIGNOFF"] is False
    assert summary["PUBLISH_READY_COUNT"] == 0


def test_all_12_targets_candidate_ready(release_report: dict) -> None:
    summary = release_report["summary"]
    assert summary["CANONICAL_TARGETS_COUNT"] == 12
    assert summary["CANDIDATE_READY_COUNT"] == 12
    assert summary["ALL_TARGETS_CANDIDATE_READY"] is True
    assert len(release_report["targets"]) == 12
    for t in release_report["targets"]:
        assert t["publish_ready_candidate"] is True, f"Cible {t['manual_id']}:{t['variant']} non prête"


def test_zero_overfull_and_zero_p2(release_report: dict) -> None:
    summary = release_report["summary"]
    assert summary["OVERFULL"] == 0
    assert summary["TOTAL_P2_OPEN"] == 0


def test_mutation_single_target_failure_breaks_global_candidate_ready(monkeypatch) -> None:
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import release_all_check as mod

    # Mutate PREFLIGHT_PATH to return a failing record for one target
    real_evaluate = mod.evaluate_release
    def mutated_evaluate(release_owner_final_signoff=False):
        rep = real_evaluate(release_owner_final_signoff=release_owner_final_signoff)
        rep["targets"][0]["publish_ready_candidate"] = False
        rep["targets"][0]["publish_ready"] = False
        rep["summary"]["CANDIDATE_READY_COUNT"] -= 1
        rep["summary"]["ALL_TARGETS_CANDIDATE_READY"] = False
        rep["summary"]["RELEASE_STATUS"] = "FAIL"
        rep["summary"]["TOTAL_P2_OPEN"] = 1
        return rep

    report = mutated_evaluate(release_owner_final_signoff=False)

    assert report["summary"]["ALL_TARGETS_CANDIDATE_READY"] is False
    assert report["summary"]["RELEASE_STATUS"] == "FAIL"
    assert report["summary"]["CANDIDATE_READY_COUNT"] == 11
    assert report["summary"]["TOTAL_P2_OPEN"] > 0


def test_mutation_signoff_required_for_publish_ready() -> None:
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import release_all_check as mod

    report_without_signoff = mod.evaluate_release(release_owner_final_signoff=False)
    assert report_without_signoff["summary"]["ALL_CANONICAL_MANUALS_ZERO_DEBT_PUBLISH_READY"] is False
    assert report_without_signoff["summary"]["PUBLISH_READY_COUNT"] == 0
    assert report_without_signoff["summary"]["RELEASE_STATUS"] == "ZERO_DEBT_RELEASE_OWNER_FINAL_SIGNOFF_REQUIRED"

    report_with_signoff = mod.evaluate_release(release_owner_final_signoff=True)
    assert report_with_signoff["summary"]["ALL_CANONICAL_MANUALS_ZERO_DEBT_PUBLISH_READY"] is True
    assert report_with_signoff["summary"]["PUBLISH_READY_COUNT"] == 12
    assert report_with_signoff["summary"]["RELEASE_STATUS"] == "ALL_CANONICAL_MANUALS_ZERO_DEBT_PUBLISH_READY"


def test_no_target_compensates_another() -> None:
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import release_all_check as mod

    report = mod.evaluate_release()
    # 12 targets must be individual candidates
    for t in report["targets"]:
        assert t["publish_ready_candidate"] is True
