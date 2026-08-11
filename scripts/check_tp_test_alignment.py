#!/usr/bin/env python3
"""Generate a report on TP/test alignment."""

from __future__ import annotations

from scripts._qa_common import ROOT, print_result
from scripts._pedagogy_reports import contains, pilot_sequences, rel, write_report


def main() -> None:
    lines = ["Ce contrôle vérifie que le TP demande des tests et qu'un fichier de tests existe.", ""]
    errors: list[str] = []
    for level, seq in pilot_sequences():
        tests = sorted((seq / "tests").glob("test*.py"))
        missing = contains(seq, "tp.md", ["tests", "critères de réussite", "livrable"])
        lines.extend([
            f"## {level} - {rel(seq)}",
            f"- Fichiers de tests : {', '.join(rel(path) for path in tests) if tests else 'aucun'}",
            f"- Marqueurs TP manquants : {', '.join(missing) if missing else 'aucun'}",
            "- Limite : les tests techniques ne prouvent pas la qualité pédagogique du TP.",
            "",
        ])
        if not tests or missing:
            errors.append(f"{rel(seq)}: alignement TP/tests insuffisant")
    write_report(ROOT / "tp_test_alignment_report.md", "TP Test Alignment Report", lines)
    print_result("check_tp_test_alignment", errors)


if __name__ == "__main__":
    main()
