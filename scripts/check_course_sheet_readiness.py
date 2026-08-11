#!/usr/bin/env python3
"""Check course sheet readiness metadata is honest."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from scripts._qa_common import ROOT, read_frontmatter
from scripts._course_sheets_common import VALID_READINESS, compute_sheet_readiness, course_sheet_links, sheet_files


@dataclass
class CourseSheetReadinessResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0
    counts: Counter[str] = field(default_factory=Counter)
    without_linked_resource: list[str] = field(default_factory=list)


def analyze_course_sheet_readiness(root: Path = ROOT) -> CourseSheetReadinessResult:
    result = CourseSheetReadinessResult()
    files = sheet_files(root)
    if not files:
        result.errors.append("aucune fiche de cours")
        return result
    for path in files:
        result.checked_files += 1
        metadata = read_frontmatter(path)
        declared = str(metadata.get("readiness") or "").strip()
        if declared not in VALID_READINESS:
            result.errors.append(f"{path}: readiness invalide ou absente -> {declared or 'absent'}")
            continue
        links = course_sheet_links(path)
        computed = compute_sheet_readiness(root, links)
        result.counts[computed] += 1
        if computed == "theoretical":
            result.without_linked_resource.append(path.as_posix())
        if declared != computed:
            result.errors.append(f"{path}: readiness déclarée {declared} mais calculée {computed}")
    return result


def main() -> int:
    result = analyze_course_sheet_readiness()
    print(f"Nombre de fiches théoriques : {result.counts.get('theoretical', 0)}")
    print(f"Nombre de fiches liées : {result.counts.get('linked', 0)}")
    print(f"Nombre de fiches opérationnelles : {result.counts.get('operational', 0)}")
    if result.without_linked_resource:
        print("Fiches sans ressource liée :")
        for path in result.without_linked_resource[:80]:
            print(f"- {path}")
    if result.errors:
        print("check_course_sheet_readiness: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(f"check_course_sheet_readiness: PASS ({result.checked_files} fiches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
