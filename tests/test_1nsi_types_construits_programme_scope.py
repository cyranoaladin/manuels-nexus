from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "NSI/chapitres/1NSI-TYPES-CONSTRUITS/contrat.yaml"
MATRIX = ROOT / "audit/PROGRAM_COVERAGE_MATRIX_1NSI.json"
ATOMS = ROOT / "audit/OFFICIAL_PROGRAM_ATOMS_2026_2027.json"


def test_mutability_is_explicit_methodology_not_an_official_capacity() -> None:
    contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    c5 = next(item for item in contract["capacites"] if item["code"] == "C5")

    assert c5["programme_alignment"] == "METHODOLOGY"
    assert c5["mandatory_for_coverage"] is False
    assert c5["official_atom_ids"] == []

    rows = json.loads(MATRIX.read_text(encoding="utf-8"))
    row = next(item for item in rows if item["row_id"] == "1NSI-MATRIX-012")
    assert row["coverage_status"] == "AUDIT_METADATA_ONLY"
    assert row["mandatory"] is False
    assert row["obligation_type"] == "IMPLEMENTATION_GUIDANCE"

    registry = json.loads(ATOMS.read_text(encoding="utf-8"))
    assert "1NSI-ATOM-012" not in {atom["atom_id"] for atom in registry["atoms"]}
