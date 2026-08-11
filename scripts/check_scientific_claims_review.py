#!/usr/bin/env python3
"""Generate a report on scientific review status."""

from __future__ import annotations

from scripts._qa_common import ROOT, print_result
from scripts._pedagogy_reports import pilot_sequences, rel, write_report


def main() -> None:
    lines = [
        "Ce contrôle vérifie que l'absence de revue scientifique finale est explicite.",
        "",
    ]
    errors: list[str] = []
    for level, seq in pilot_sequences():
        audit = seq / "quality_audit_s01.md"
        text = audit.read_text(encoding="utf-8", errors="replace").lower() if audit.exists() else ""
        explicit = "scientifique" in text and "needs_review" in text
        lines.extend([
            f"## {level} - {rel(seq)}",
            f"- Revue scientifique finale déclarée absente : {'oui' if explicit else 'non'}",
            "- Décision : revue scientifique humaine requise.",
            "",
        ])
        if not explicit:
            errors.append(f"{rel(seq)}: absence de revue scientifique finale non explicitée")
    write_report(ROOT / "scientific_claims_review_report.md", "Scientific Claims Review Report", lines)
    print_result("check_scientific_claims_review", errors)


if __name__ == "__main__":
    main()
