#!/usr/bin/env python3
"""Release Drive check: fails with classified Drive blockers."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from scripts._qa_common import ROOT, print_result

NON_BLOCKING_DECISIONS = {"integrated_adapted", "inspiration_only"}
BLOCKING_DECISIONS = {"missing_local_copy", "deferred", "quarantined", "rejected_sensitive"}


def analyze_drive_mapping_release(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    inventory = root / "drive_inventory.csv"
    if not inventory.exists():
        return ["drive_inventory.csv absent"]

    with inventory.open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row.get("drive_url") != "BLOCKER"]

    if not rows:
        return ["drive = 0: aucune ressource Drive référencée"]

    decisions = Counter(row.get("decision", "") for row in rows)
    unknown = sorted(decision for decision in decisions if decision not in NON_BLOCKING_DECISIONS | BLOCKING_DECISIONS)
    if unknown:
        errors.append("décisions Drive non classées pour release: " + ", ".join(unknown))

    blockers = [row for row in rows if row.get("decision") in BLOCKING_DECISIONS]
    if blockers:
        counts = Counter(row.get("decision", "") for row in blockers)
        errors.append(
            "Drive partiellement intégré: "
            + ", ".join(f"{key}={counts[key]}" for key in sorted(counts))
        )
        for row in blockers[:20]:
            errors.append(
                f"{row.get('file_name', 'NA')}: {row.get('decision')} - {row.get('raison', '').strip()}"
            )
    return errors


def main() -> None:
    print_result("check_drive_mapping_release", analyze_drive_mapping_release(ROOT))


if __name__ == "__main__":
    main()
