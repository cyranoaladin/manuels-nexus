#!/usr/bin/env python3
"""Generate a report on evaluation/bareme alignment."""

from __future__ import annotations

from scripts._qa_common import ROOT, print_result
from scripts._pedagogy_reports import contains, pilot_sequences, rel, write_report


def main() -> None:
    lines = ["Ce contrôle vérifie les marqueurs minimaux d'une évaluation exploitable.", ""]
    errors: list[str] = []
    required = ["durée", "matériel", "compétences", "barème", "corrigé lié", "analyse de code", "programmation"]
    for level, seq in pilot_sequences():
        missing = contains(seq, "evaluation.md", required)
        extra_files = [seq / "bareme.md", seq / "grille_competences.md", seq / "evaluation_corrigee.md", seq / "version_amenagee.md"]
        absent = [rel(path) for path in extra_files if not path.exists()]
        lines.extend([
            f"## {level} - {rel(seq)}",
            f"- Marqueurs manquants dans evaluation.md : {', '.join(missing) if missing else 'aucun'}",
            f"- Documents complémentaires absents : {', '.join(absent) if absent else 'aucun'}",
            "- Limite : le barème doit être testé sur copies anonymisées avant publication.",
            "",
        ])
        if missing or absent:
            errors.append(f"{rel(seq)}: évaluation ou documents complémentaires incomplets")
    write_report(ROOT / "evaluation_bareme_alignment_report.md", "Evaluation Bareme Alignment Report", lines)
    print_result("check_evaluation_bareme_alignment", errors)


if __name__ == "__main__":
    main()
