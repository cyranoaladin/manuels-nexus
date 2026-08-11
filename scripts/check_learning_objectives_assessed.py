#!/usr/bin/env python3
"""Generate a report on learning objectives assessment."""

from __future__ import annotations

from scripts._qa_common import ROOT, print_result
from scripts._pedagogy_reports import contains, pilot_sequences, rel, write_report


def main() -> None:
    lines = ["Ce contrôle vérifie que les objectifs sont reliés à des évaluations.", ""]
    errors: list[str] = []
    for level, seq in pilot_sequences():
        missing_eval = contains(seq, "evaluation.md", ["compétences évaluées", "barème"])
        missing_qcm = contains(seq, "qcm.json", ["capacite_officielle", "erreur_ciblee"])
        lines.extend([
            f"## {level} - {rel(seq)}",
            f"- Évaluation : {', '.join(missing_eval) if missing_eval else 'marqueurs présents'}",
            f"- QCM : {', '.join(missing_qcm) if missing_qcm else 'marqueurs présents'}",
            "- Limite : les objectifs doivent être confrontés à une passation réelle.",
            "",
        ])
        if missing_eval or missing_qcm:
            errors.append(f"{rel(seq)}: objectifs insuffisamment évalués")
    write_report(ROOT / "learning_objectives_assessed_report.md", "Learning Objectives Assessed Report", lines)
    print_result("check_learning_objectives_assessed", errors)


if __name__ == "__main__":
    main()
