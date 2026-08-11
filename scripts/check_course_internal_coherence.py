#!/usr/bin/env python3
"""Generate a readable report on course internal coherence."""

from __future__ import annotations

from scripts._qa_common import ROOT, print_result
from scripts._pedagogy_reports import contains, line_count, pilot_sequences, rel, write_report


def main() -> None:
    lines = [
        "Ce contrôle est qualitatif assisté. Il ne valide pas la pédagogie.",
        "",
    ]
    errors: list[str] = []
    for level, seq in pilot_sequences():
        missing = contains(seq, "cours_eleve.md", ["situation-problème", "objectifs", "à retenir", "auto-évaluation"])
        lines.extend([
            f"## {level} - {rel(seq)}",
            f"- Lignes utiles du cours : {line_count(seq, 'cours_eleve.md')}",
            f"- Sections structurantes manquantes : {', '.join(missing) if missing else 'aucune détectée'}",
            "- Décision : revue humaine requise avant publication.",
            "",
        ])
        if missing:
            errors.append(f"{rel(seq / 'cours_eleve.md')}: sections structurantes manquantes")
    write_report(ROOT / "course_internal_coherence_report.md", "Course Internal Coherence Report", lines)
    print_result("check_course_internal_coherence", errors)


if __name__ == "__main__":
    main()
