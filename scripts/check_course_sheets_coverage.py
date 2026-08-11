#!/usr/bin/env python3
"""Check every annual progression sequence has course sheets."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scripts._qa_common import ROOT
from scripts._course_sheets_common import DENSE_MIN_SHEETS, frontmatter_capacities, planned_sequences, read_frontmatter, sheets_by_sequence


@dataclass
class CourseSheetCoverageResult:
    errors: list[str] = field(default_factory=list)
    expected_sequences: int = 0
    created_sheets: int = 0


def analyze_course_sheet_coverage(root: Path = ROOT, program_ids: set[str] | None = None) -> CourseSheetCoverageResult:
    del program_ids  # Coverage checks planned capacity presence in fiches; YAML validity is alignment's job.
    result = CourseSheetCoverageResult()
    plans = planned_sequences(root)
    by_sequence = sheets_by_sequence(root)
    result.expected_sequences = len(plans)
    result.created_sheets = sum(len(paths) for paths in by_sequence.values())

    for sequence_id, plan in plans.items():
        sheets = by_sequence.get(sequence_id, [])
        if not sheets:
            result.errors.append(f"{sequence_id}: aucune fiche de cours")
            continue
        expected_count = DENSE_MIN_SHEETS.get(sequence_id, 1)
        if len(sheets) < expected_count:
            result.errors.append(
                f"{sequence_id}: chapitre dense avec {len(sheets)} fiche(s), minimum {expected_count}"
            )
        declared: set[str] = set()
        for sheet in sheets:
            declared.update(frontmatter_capacities(read_frontmatter(sheet)))
        for capacity in sorted(plan.capacities):
            if capacity not in declared:
                result.errors.append(f"{sequence_id}: capacité sans fiche -> {capacity}")
    return result


def main() -> int:
    result = analyze_course_sheet_coverage()
    if result.errors:
        print("check_course_sheets_coverage: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(
        "check_course_sheets_coverage: PASS "
        f"({result.expected_sequences} séquences, {result.created_sheets} fiches)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
