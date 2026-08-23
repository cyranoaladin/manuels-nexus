from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_math_student_teacher_key_audit.py"
AUDIT = ROOT / "audit/STUDENT_PDF_PUBLISH_PREFLIGHT_CURRENT_HEAD.json"


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

    assert len(payload["keys"]) == 35
    assert payload["summary"]["student_teacher_only_leaks"] == 0
    assert payload["summary"]["teacher_required_keys_present"] is True
    assert payload["summary"]["teacher_keys_by_manual"] == {
        "1SPE": {"expected": 10, "observed": 10},
        "TCOMPL": {"expected": 9, "observed": 9},
        "TEXPERTES": {"expected": 5, "observed": 5},
        "TSPE": {"expected": 11, "observed": 11},
    }
    assert all(row["student_visibility_before"] == "VISIBLE" for row in payload["keys"])
    assert all(row["student_visibility_current"] == "HIDDEN" for row in payload["keys"])
    assert all(row["teacher_visibility_current"] == "VISIBLE" for row in payload["keys"])
    assert all(row["source_guard_status"] == "PASS" for row in payload["keys"])
