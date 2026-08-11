#!/usr/bin/env python3
"""Release check: programme coverage must have no absent/partial item and at least one covered item."""

from __future__ import annotations

from typing import List
from collections import Counter

from scripts._qa_common import ROOT, print_result


def main() -> None:
    errors: List[str] = []
    coverage = ROOT / "coverage.md"
    if not coverage.exists():
        errors.append("coverage.md absent")
        print_result("check_no_absent_coverage_for_release", errors)
        return

    counts: Counter[str] = Counter()
    offenders: List[str] = []
    for line in coverage.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("| ") or line.startswith("| ---") or line.startswith("| niveau"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 10:
            continue
        status = cells[8]
        counts[status] += 1
        if status in {"absent", "partial"}:
            offenders.append(f"{cells[0]} | {cells[3]} | {status}")

    if counts.get("covered", 0) == 0:
        errors.append("aucune capacité covered")
    if offenders:
        errors.append(f"{len(offenders)} capacités restent absent ou partial")
        errors.extend(offenders[:50])
    print_result("check_no_absent_coverage_for_release", errors)


if __name__ == "__main__":
    main()
