#!/usr/bin/env python3
"""Validate evidence-based programme coverage output."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from scripts._qa_common import ROOT, print_result

COVERAGE = ROOT / "coverage.md"
VALID_STATUS = {"absent", "partial", "needs_review", "covered"}


def parse_table(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("| ") or line.startswith("| ---") or line.startswith("| niveau"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 10:
            continue
        rows.append(
            {
                "niveau": cells[0],
                "rubrique": cells[1],
                "contenu": cells[2],
                "capacite": cells[3],
                "cours": cells[4],
                "td_tp": cells[5],
                "evaluation": cells[6],
                "corrige": cells[7],
                "statut": cells[8],
                "blocker": cells[9],
            }
        )
    return rows


def main() -> None:
    errors: List[str] = []
    if not COVERAGE.exists():
        errors.append("coverage.md absent")
        print_result("check_coverage_evidence", errors)
        return

    for row in parse_table(COVERAGE):
        status = row["statut"]
        cap = f"{row['niveau']} | {row['capacite']}"
        if status not in VALID_STATUS:
            errors.append(f"{cap}: statut invalide -> {status}")
            continue

        has_any = any(row[key] != "-" for key in ["cours", "td_tp", "evaluation", "corrige"])
        has_all = all(row[key] != "-" for key in ["cours", "td_tp", "evaluation", "corrige"])

        if status == "absent" and has_any:
            errors.append(f"{cap}: absent avec preuves listées")
        if status == "partial" and not has_any:
            errors.append(f"{cap}: partial sans preuve")
        if status == "needs_review" and not has_all:
            errors.append(f"{cap}: needs_review sans toutes les familles de preuves")
        if status == "covered":
            if not has_all:
                errors.append(f"{cap}: covered sans preuves complètes")
            if row["blocker"] != "-":
                errors.append(f"{cap}: covered avec blocker")

    print_result("check_coverage_evidence", errors)


if __name__ == "__main__":
    main()
