from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_math_student_teacher_key_audit.py"
AUDIT = ROOT / "audit/STUDENT_PDF_PUBLISH_PREFLIGHT_CURRENT_HEAD.json"


@pytest.mark.parametrize("mutation", ("fi_before_key", "key_removed"))
def test_teacher_only_source_guard_rejects_incomplete_block(mutation: str) -> None:
    probe = r"""
import sys
from pathlib import Path

root = Path(sys.argv[1])
sys.path.insert(0, str(root / "scripts"))
import build_math_student_teacher_key_audit as builder

source = (root / "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/qcm/1SPE-SUITES-QCM.tex").read_text(encoding="utf-8")
if sys.argv[2] == "fi_before_key":
    source = source.replace("\\fi\n% NEXUS-QCM-TEACHER-ONLY-END", "% NEXUS-QCM-TEACHER-ONLY-END", 1)
    source = source.replace("\\section*{Cle de correction", "\\fi\n\\section*{Cle de correction", 1)
else:
    source = source.replace("Cle de correction", "Corrige", 1)
raise SystemExit(0 if not builder._teacher_only_guard_is_complete(source) else 1)
"""
    result = subprocess.run(
        [sys.executable, "-c", probe, str(ROOT), mutation],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_math_student_teacher_key_audit_is_current() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_math_student_teacher_key_audit_closes_exactly_35_leaks() -> None:
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))

    assert payload["schema_version"] == 2
    assert payload["artifact_name"] == (
        "STUDENT_TEACHER_KEY_SOURCE_GUARD_AND_TRACKED_PDF_DIAGNOSTIC"
    )
    assert payload["source_evidence"]["qcm_guards_attest_current_sources"] is True
    assert payload["pdf_evidence_provenance"] == {
        "attests_current_head": False,
        "canonical_observed_build_count": 0,
        "release_evidence": False,
        "status": "UNATTESTED_TRACKED_PDF_DIAGNOSTIC",
    }
    assert len(payload["keys"]) == 35
    assert payload["summary"]["tracked_pdf_student_teacher_only_leaks"] == 0
    assert payload["summary"]["tracked_pdf_teacher_required_keys_present"] is True
    assert payload["summary"]["tracked_pdf_teacher_keys_by_manual"] == {
        "1SPE": {"expected": 10, "observed": 10},
        "TCOMPL": {"expected": 9, "observed": 9},
        "TEXPERTES": {"expected": 5, "observed": 5},
        "TSPE": {"expected": 11, "observed": 11},
    }
    assert all(row["student_visibility_before"] == "VISIBLE" for row in payload["keys"])
    assert all(row["student_visibility_current"] == "HIDDEN" for row in payload["keys"])
    assert all(row["teacher_visibility_current"] == "VISIBLE" for row in payload["keys"])
    assert all(row["source_guard_status"] == "PASS" for row in payload["keys"])
    assert all(
        evidence["evidence_scope"] == "TRACKED_PDF_DIAGNOSTIC_ONLY"
        and evidence["release_evidence"] is False
        for evidence in payload["build_evidence"].values()
    )
