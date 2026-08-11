#!/usr/bin/env python3
"""Release check: published resources require explicit pedagogy and science reviews."""

from __future__ import annotations

from typing import List
import csv

from scripts._qa_common import ROOT, print_result


def main() -> None:
    errors: List[str] = []
    manifest = ROOT / "manifest.csv"
    if not manifest.exists():
        errors.append("manifest.csv absent")
        print_result("check_validated_statuses", errors)
        return
    with manifest.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        if row.get("statut") == "published":
            comment = (row.get("commentaire") or "").lower()
            if "validated_pedagogy" not in comment:
                errors.append(f"{row.get('chemin')}: publication sans revue pédagogique tracée")
            if "validated_science" not in comment:
                errors.append(f"{row.get('chemin')}: publication sans revue scientifique tracée")
    print_result("check_validated_statuses", errors)


if __name__ == "__main__":
    main()
