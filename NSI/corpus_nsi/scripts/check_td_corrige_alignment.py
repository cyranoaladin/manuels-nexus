#!/usr/bin/env python3
"""Generate a report on TD/correction alignment."""

from __future__ import annotations

import re

from scripts._qa_common import ROOT, print_result
from scripts._pedagogy_reports import pilot_sequences, rel, write_report


def count_exercises(text: str) -> int:
    return len(re.findall(r"^#{2,3}\s*Exercice\s+\d+", text, flags=re.M))


def main() -> None:
    lines = ["Ce contrôle compte les exercices et vérifie les marqueurs de correction.", ""]
    errors: list[str] = []
    for level, seq in pilot_sequences():
        td = (seq / "td.md").read_text(encoding="utf-8", errors="replace")
        corrige = (seq / "corrige.md").read_text(encoding="utf-8", errors="replace")
        n_td = count_exercises(td)
        missing = []
        for idx in range(1, n_td + 1):
            if f"Exercice {idx}" not in corrige:
                missing.append(str(idx))
        lines.extend([
            f"## {level} - {rel(seq)}",
            f"- Exercices TD : {n_td}",
            f"- Corrections manquantes détectées : {', '.join(missing) if missing else 'aucune'}",
            "- Limite : l'alignement de fond reste à relire humainement.",
            "",
        ])
        if missing:
            errors.append(f"{rel(seq / 'corrige.md')}: corrections manquantes pour exercices {', '.join(missing)}")
    write_report(ROOT / "td_corrige_alignment_report.md", "TD Corrige Alignment Report", lines)
    print_result("check_td_corrige_alignment", errors)


if __name__ == "__main__":
    main()
