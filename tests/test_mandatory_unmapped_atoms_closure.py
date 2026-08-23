from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_mandatory_unmapped_atoms_closure.py"
REPORT = ROOT / "audit" / "MANDATORY_UNMAPPED_ATOMS_CLOSURE.json"


def test_closure_report_is_current() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_every_structural_gap_has_an_explicit_closure() -> None:
    payload = json.loads(REPORT.read_text(encoding="utf-8"))

    assert payload["summary"]["mandatory_unmapped_remaining"] == 0
    assert payload["summary"]["structural_closures"] == len(payload["closures"])
    assert payload["summary"]["structural_closures"] > 0
    for row in payload["closures"]:
        assert row["gap_type"] not in {"", "UNKNOWN", None}
        assert row["correct_action"]
        assert row["mapped_chapter"]
        assert row["contract_capacity"]
        assert row["closure_status"] == "STRUCTURALLY_MAPPED"
        assert row["full_claim"] is False
