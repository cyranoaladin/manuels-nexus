#!/usr/bin/env python3
"""Release check: no resource may remain in needs_review."""

from __future__ import annotations

from typing import List
import csv

from scripts._qa_common import ROOT, print_result


def main() -> None:
    errors: List[str] = []
    manifest = ROOT / "manifest.csv"
    if not manifest.exists():
        errors.append("manifest.csv absent")
        print_result("check_no_needs_review_for_release", errors)
        return
    with manifest.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    remaining = [row["chemin"] for row in rows if row.get("statut") == "needs_review"]
    if remaining:
        errors.append(f"{len(remaining)} ressources restent needs_review")
        errors.extend(remaining[:40])
    print_result("check_no_needs_review_for_release", errors)


if __name__ == "__main__":
    main()
