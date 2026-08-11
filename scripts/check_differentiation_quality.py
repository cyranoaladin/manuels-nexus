#!/usr/bin/env python3
"""Generate a report on differentiation quality."""

from __future__ import annotations

from scripts._qa_common import ROOT, print_result
from scripts._pedagogy_reports import contains, line_count, pilot_sequences, rel, write_report


def main() -> None:
    lines = ["Ce contrôle vérifie l'existence de niveaux d'aide et d'extensions.", ""]
    errors: list[str] = []
    required = ["niveau 1", "niveau 2", "niveau 3", "extension", "auto-évaluation"]
    for level, seq in pilot_sequences():
        missing = contains(seq, "aides_progressives.md", required)
        lines.extend([
            f"## {level} - {rel(seq)}",
            f"- Lignes utiles aides : {line_count(seq, 'aides_progressives.md')}",
            f"- Marqueurs manquants : {', '.join(missing) if missing else 'aucun'}",
            "- Limite : la différenciation reste à observer en classe.",
            "",
        ])
        if missing:
            errors.append(f"{rel(seq / 'aides_progressives.md')}: différenciation insuffisamment structurée")
    write_report(ROOT / "differentiation_quality_report.md", "Differentiation Quality Report", lines)
    print_result("check_differentiation_quality", errors)


if __name__ == "__main__":
    main()
