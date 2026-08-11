#!/usr/bin/env python3
"""Check explicit official-program evidence declared in frontmatter."""

from __future__ import annotations

from pathlib import Path
from typing import List

from scripts._qa_common import ROOT, iter_declared_evidence, load_program_entries, normalize_text, print_result

VALID_EVIDENCE_TYPES = {"cours", "trace", "td", "tp", "evaluation", "corrige", "qcm", "projet", "fiche_methode", "aides"}


def anchor_exists(path: Path, anchor: str) -> bool:
    if not anchor:
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    needle = normalize_text(anchor.lstrip("#"))
    headings = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            headings.append(normalize_text(line.lstrip("#").strip()))
    return needle in headings or anchor.lstrip("#").lower() in text.lower()


def main() -> None:
    program = load_program_entries()
    errors: List[str] = []
    seen = set()

    for evidence in iter_declared_evidence():
        seen.add(evidence.capacity_id)
        rel = evidence.document_path.relative_to(ROOT)
        if evidence.capacity_id not in program:
            errors.append(f"{rel}: capacité inconnue -> {evidence.capacity_id}")
        if evidence.evidence_type not in VALID_EVIDENCE_TYPES:
            errors.append(f"{rel}: type de preuve inconnu -> {evidence.evidence_type}")
        target = ROOT / evidence.file
        if not target.exists():
            errors.append(f"{rel}: fichier preuve absent -> {evidence.file}")
        elif not anchor_exists(target, evidence.anchor):
            errors.append(f"{rel}: ancre non retrouvée -> {evidence.file}{evidence.anchor}")

    if not seen:
        errors.append("aucune preuve official_program.capacities détectée")

    print_result("check_pedagogical_alignment", errors)


if __name__ == "__main__":
    main()
