#!/usr/bin/env python3
"""Check course sheets are aligned with progression and do not validate coverage."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT, read_frontmatter, sequence_id_from_path
from scripts._course_sheets_common import (
    course_sheet_links,
    frontmatter_capacities,
    link_is_registered,
    planned_sequences,
    program_ids as load_program_ids,
    resource_exists,
    section_text,
    session_ids,
    sheet_files,
)

FORBIDDEN_COVERAGE_CLAIMS = [
    "capacité couverte",
    "capacite couverte",
    "covered",
    "published",
    "validated_pedagogy",
    "validated_science",
    "validated_technical",
    "remplace le cours",
    "remplace le td",
    "remplace le corrigé",
    "remplace le corrige",
    "remplace une évaluation",
    "remplace une evaluation",
    "remplace un tp",
]


@dataclass
class CourseSheetAlignmentResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


def link_block_errors(path: Path, text: str, sequence_id: str, root: Path) -> list[str]:
    errors: list[str] = []
    block = section_text(text, "Lien avec la progression")
    if not block:
        return [f"{path}: lien avec la progression absent"]
    links = course_sheet_links(path)
    if not links:
        errors.append(f"{path}: table de liens structurée absente")
        return errors
    real_sessions = session_ids(root)
    if not any(link.is_session and re.fullmatch(rf"{sequence_id}-S\d+", link.file) and link.file in real_sessions for link in links):
        errors.append(f"{path}: aucune séance réelle liée")
    resource_links = [link for link in links if link.is_resource]
    if not any(link.element.lower() in {"td", "tp", "évaluation", "evaluation", "projet"} for link in resource_links):
        errors.append(f"{path}: aucun TD, TP, évaluation ou projet lié")
    for link in resource_links:
        if not resource_exists(root, link.file) and not link_is_registered(root, link.file):
            errors.append(f"{path}: ressource liée absente du dépôt et du registre -> {link.file}")
    return errors


def capacity_context(text: str) -> str:
    return "\n".join(
        [
            section_text(text, "Méthodes"),
            section_text(text, "Exemples corrigés"),
            section_text(text, "Mini-exercices"),
        ]
    )


def analyze_sheet_alignment(path: Path, program_ids: set[str], planned_ids: set[str], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    lowered = text.lower()
    metadata = read_frontmatter(path)
    sequence_id = str(metadata.get("sequence_id") or sequence_id_from_path(path))
    if sequence_id not in planned_ids:
        errors.append(f"{path}: sequence_id absent de la progression -> {sequence_id}")
    errors.extend(link_block_errors(path, text, sequence_id, root))

    capacities = frontmatter_capacities(metadata)
    context = capacity_context(text)
    for capacity in sorted(capacities):
        if capacity not in program_ids:
            errors.append(f"{path}: capacité absente du YAML officiel -> {capacity}")
        if context.count(capacity) == 0:
            errors.append(f"{path}: capacité seulement présente en frontmatter ou hors activité -> {capacity}")

    for phrase in FORBIDDEN_COVERAGE_CLAIMS:
        if phrase in lowered:
            errors.append(f"{path}: prétention de couverture ou remplacement interdite -> {phrase}")
    return errors


def analyze_course_sheets_alignment(root: Path = ROOT, program_ids: set[str] | None = None) -> CourseSheetAlignmentResult:
    result = CourseSheetAlignmentResult()
    ids = program_ids or load_program_ids()
    planned_ids = set(planned_sequences(root))
    files = sheet_files(root)
    if not files:
        result.errors.append("aucune fiche de cours")
        return result
    for path in files:
        result.checked_files += 1
        result.errors.extend(analyze_sheet_alignment(path, ids, planned_ids, root))
    return result


def main() -> int:
    result = analyze_course_sheets_alignment()
    if result.errors:
        print("check_course_sheets_alignment: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(f"check_course_sheets_alignment: PASS ({result.checked_files} fiches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
