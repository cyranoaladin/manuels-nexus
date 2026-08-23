from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_official_source_atom_crosswalk.py"
REGISTRY = ROOT / "audit" / "OFFICIAL_SOURCE_ATOM_CROSSWALK_2026_2027.json"


def test_official_source_atom_crosswalk_is_current() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_official_source_atom_crosswalk_is_complete_and_fail_closed() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    summary = payload["summary"]

    assert payload["namespace"] == "PROGRAMME_D_ENSEIGNEMENT"
    assert payload["methodology"]["fuzzy_matches_are_proof"] is False
    assert payload["methodology"]["internal_capacities_are_source"] is False
    assert summary["status"] == "PASS"
    assert summary["official_authorities"] == 6
    assert summary["mandatory_atoms"] == summary["mapped_mandatory_atoms"]
    assert summary["unparsed_mandatory_segments"] == 0
    assert summary["duplicate_atoms"] == 0
    assert summary["ambiguous_atoms"] == 0
    assert summary["wrong_year_atoms"] == 0
    assert summary["unclassified_source_segments"] == 0


def test_deleting_a_mandatory_atom_would_reopen_its_source_segment() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    mandatory_rows = [row for row in payload["rows"] if row["mandatory"] == "YES"]
    assert mandatory_rows
    assert all(row["disposition"] == "OFFICIAL_ATOM" for row in mandatory_rows)
    assert all(len(row["atom_ids"]) == 1 for row in mandatory_rows)
