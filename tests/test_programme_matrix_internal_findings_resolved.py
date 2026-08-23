from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
MANUALS = ("1SPE", "TSPE", "TCOMPL", "TEXPERTES", "1NSI", "TNSI")


def _rows() -> list[dict[str, object]]:
    return [
        row
        for manual in MANUALS
        for row in json.loads(
            (AUDIT / f"PROGRAM_COVERAGE_MATRIX_{manual}.json").read_text(
                encoding="utf-8"
            )
        )
    ]


def test_no_wrong_year_or_unsupported_claim_remains_in_current_matrices() -> None:
    unresolved = [
        row
        for row in _rows()
        if row["coverage_status"] in {"WRONG_YEAR", "UNSUPPORTED_CLAIM"}
    ]

    assert unresolved == []


def test_resolved_1spe_extensions_remain_audit_metadata_not_official_atoms() -> None:
    rows = {row["row_id"]: row for row in _rows()}
    resolved = {
        "1SPE-MATRIX-043",
        "1SPE-MATRIX-044",
        "1SPE-MATRIX-045",
        "1SPE-MATRIX-069",
        "1SPE-MATRIX-070",
    }

    assert {rows[row_id]["coverage_status"] for row_id in resolved} == {
        "AUDIT_METADATA_ONLY"
    }
    assert all(rows[row_id]["mandatory"] is False for row_id in resolved)

    atoms = json.loads(
        (AUDIT / "OFFICIAL_PROGRAM_ATOMS_2026_2027.json").read_text(encoding="utf-8")
    )["atoms"]
    atom_ids = {atom["atom_id"] for atom in atoms}
    assert not {row_id.replace("MATRIX", "ATOM") for row_id in resolved} & atom_ids


def test_wrong_year_revalidation_has_no_stale_human_gate() -> None:
    report = json.loads(
        (AUDIT / "WRONG_YEAR_REVALIDATION_CURRENT_HEAD.json").read_text(
            encoding="utf-8"
        )
    )

    assert report["requested_cases_remaining"] == 0
    assert report["distinct_current_regulatory_findings"] == []
    assert report["objective_counters"] == {
        "wrong_year": 0,
        "unsupported_claim": 0,
        "human_decision_required_for_resolved_scope": 0,
    }
