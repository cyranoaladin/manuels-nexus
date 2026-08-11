#!/usr/bin/env python3
"""Generate a report on depth of explicit official-program evidence."""

from __future__ import annotations

from collections import defaultdict

from scripts._qa_common import ROOT, iter_declared_evidence, print_result
from scripts._pedagogy_reports import write_report


def main() -> None:
    by_capacity: dict[str, set[str]] = defaultdict(set)
    for item in iter_declared_evidence():
        by_capacity[item.capacity_id].add(item.evidence_type)

    lines = [
        "Ce contrôle mesure la profondeur déclarative des preuves.",
        "Il ne transforme aucune capacité en statut covered.",
        "",
    ]
    errors: list[str] = []
    for capacity_id, types in sorted(by_capacity.items()):
        lines.append(f"- {capacity_id}: {', '.join(sorted(types))}")
        if capacity_id in {"T-ALGO-02A", "T-ALGO-02B", "T-ALGO-02C", "T-ALGO-02D"}:
            lines.append("  - Décision : partial, parcours de graphes en application seulement.")
        if len(types) < 3:
            errors.append(f"{capacity_id}: moins de trois familles de preuves")
    write_report(ROOT / "program_capacity_evidence_depth_report.md", "Program Capacity Evidence Depth Report", lines)
    print_result("check_program_capacity_evidence_depth", errors)


if __name__ == "__main__":
    main()
