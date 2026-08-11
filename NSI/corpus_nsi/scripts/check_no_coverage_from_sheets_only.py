#!/usr/bin/env python3
"""Prevent course sheets from becoming the sole evidence for covered capacities."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scripts._qa_common import ROOT

COVERAGE = ROOT / "coverage.md"
PROOF_COLUMNS = {
    "preuve cours": 4,
    "preuve TD/TP": 5,
    "preuve évaluation": 6,
    "preuve corrigé": 7,
}
REQUIRED_HUMAN_RELEASE_MARKERS = [
    "revue pédagogique humaine",
    "revue scientifique humaine",
    "décision explicite de publication",
]


@dataclass
class NoCoverageFromSheetsOnlyResult:
    errors: list[str] = field(default_factory=list)
    checked_rows: int = 0
    covered_rows: int = 0


def proof_is_empty(value: str) -> bool:
    return not value.strip() or value.strip() == "-"


def proof_is_sheet_only(value: str) -> bool:
    if proof_is_empty(value):
        return False
    parts = [part.strip() for part in value.split(",") if part.strip()]
    return bool(parts) and all("/fiches_cours/" in part or "fiches_cours/" in part for part in parts)


def analyze_no_coverage_from_sheets_only(root: Path = ROOT) -> NoCoverageFromSheetsOnlyResult:
    result = NoCoverageFromSheetsOnlyResult()
    path = root / "coverage.md"
    if not path.exists():
        result.errors.append("coverage.md absent")
        return result
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("| ") or line.startswith("| ---") or line.startswith("| niveau"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 10:
            continue
        result.checked_rows += 1
        status = cells[8]
        if status != "covered":
            continue
        result.covered_rows += 1
        proofs = [cells[index] for index in PROOF_COLUMNS.values()]
        non_empty = [proof for proof in proofs if not proof_is_empty(proof)]
        if non_empty and all(proof_is_sheet_only(proof) for proof in non_empty):
            result.errors.append(f"{cells[3]}: covered avec preuve seulement fiche")
        missing_required = []
        if proof_is_empty(cells[5]):
            missing_required.append("TD ou TP")
        if proof_is_empty(cells[6]):
            missing_required.append("évaluation")
        if proof_is_empty(cells[7]):
            missing_required.append("corrigé")
        if missing_required:
            result.errors.append(f"{cells[3]}: covered sans {', '.join(missing_required)}")
        blocker = cells[9].lower()
        for marker in REQUIRED_HUMAN_RELEASE_MARKERS:
            if marker not in blocker:
                result.errors.append(f"{cells[3]}: covered sans {marker}")
    return result


def main() -> int:
    result = analyze_no_coverage_from_sheets_only()
    if result.errors:
        print("check_no_coverage_from_sheets_only: KO")
        for error in result.errors[:120]:
            print(f"- {error}")
        return 1
    print(
        "check_no_coverage_from_sheets_only: PASS "
        f"({result.checked_rows} capacités vérifiées, {result.covered_rows} covered)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
