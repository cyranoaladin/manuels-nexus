"""Tests de l'invariant de release et du gate canonique release_all_check (LOT 2)."""

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
    assert summary["RELEASE_STATUS"] == "PUBLISH_READY_CANDIDATE"
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
        assert t["publish_ready_candidate"] is True, f"Cible {t[manual_id]}:{t[variant]} non prête"


def test_zero_overfull_and_zero_p2(release_report: dict) -> None:
    summary = release_report["summary"]
    assert summary["OVERFULL"] == 0
    assert summary["TOTAL_P2_OPEN"] == 0


def test_mutation_single_target_failure_breaks_global_candidate_ready(monkeypatch) -> None:
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import release_all_check as mod

    # Mutate check_target_build_clean to fail for TSPE:professeur
    real_clean = mod.check_target_build_clean
    def mutated_clean(log_path):
        if "MANUEL_TSPE_2026-2027_professeur" in str(log_path):
            return False, 1
        return real_clean(log_path)

    monkeypatch.setattr(mod, "check_target_build_clean", mutated_clean)
    report = mod.evaluate_release(release_owner_final_signoff=False)

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

    report_with_signoff = mod.evaluate_release(release_owner_final_signoff=True)
    assert report_with_signoff["summary"]["ALL_CANONICAL_MANUALS_ZERO_DEBT_PUBLISH_READY"] is True
    assert report_with_signoff["summary"]["PUBLISH_READY_COUNT"] == 12
    assert report_with_signoff["summary"]["RELEASE_STATUS"] == "PUBLISH_READY"


def test_no_target_compensates_another(monkeypatch) -> None:
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import release_all_check as mod

    # When 11 targets pass and 1 fails, global must fail
    def fail_one(log_path):
        if "1NSI_eleve" in str(log_path):
            return False, 5
        return True, 0

    monkeypatch.setattr(mod, "check_target_build_clean", fail_one)
    report = mod.evaluate_release()
    assert report["summary"]["ALL_TARGETS_CANDIDATE_READY"] is False
    assert report["summary"]["RELEASE_STATUS"] != "PUBLISH_READY"
    assert report["summary"]["RELEASE_STATUS"] != "PUBLISH_READY_CANDIDATE"
