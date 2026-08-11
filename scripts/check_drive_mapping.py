#!/usr/bin/env python3
"""Prototype Drive check: accepts explicit blocker or referenced Drive sources."""

from __future__ import annotations

from typing import Any, List
import csv

import yaml

from scripts._qa_common import ROOT, print_result


def main() -> None:
    errors: List[str] = []
    sources = ROOT / "drive_sources.yml"
    inventory = ROOT / "drive_inventory.csv"
    mapping = ROOT / "drive_mapping.md"

    for path in [sources, inventory, mapping]:
        if not path.exists():
            errors.append(f"{path.name} absent")

    data: dict[str, Any] = {}
    if sources.exists():
        data = yaml.safe_load(sources.read_text(encoding="utf-8")) or {}
        if data.get("status") == "blocked":
            blocker = str(data.get("blocker") or "")
            if "BLOCKER:" not in blocker:
                errors.append("drive_sources.yml: blocker explicite absent")
        elif not data.get("ressources"):
            errors.append("drive_sources.yml: aucune source Drive référencée")

    if inventory.exists():
        with inventory.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        non_blocker_rows = [row for row in rows if row.get("drive_url") != "BLOCKER"]
        if data.get("status") == "blocked":
            if not rows or rows[0].get("drive_url") != "BLOCKER":
                errors.append("drive_inventory.csv: ligne blocker attendue")
        elif not non_blocker_rows:
            errors.append("drive_inventory.csv: aucune ressource Drive référencée")

    if mapping.exists():
        text = mapping.read_text(encoding="utf-8", errors="replace")
        if "Drive" not in text:
            errors.append("drive_mapping.md: cartographie Drive absente")

    print_result("check_drive_mapping", errors)


if __name__ == "__main__":
    main()
