#!/usr/bin/env python3
"""Check pedagogical quality constraints for course sheets."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT, read_frontmatter
from scripts._course_sheets_common import (
    REQUIRED_FRONTMATTER,
    REQUIRED_SECTIONS,
    SHEET_NAME_RE,
    frontmatter_capacities,
    normalize,
    program_ids as load_program_ids,
    section_text,
    sheet_files,
    useful_lines,
)

GENERIC_PATTERNS = [
    "à compléter",
    "todo",
    "réponse cohérente",
    "production vérifiable",
    "variante contrôlée",
    "contenu substantiel",
    "fiche générique",
    "une fiche de cours sert",
    "le vocabulaire du chapitre",
    "un second exemple change les données",
    "la capacité associée se travaille",
]


@dataclass
class CourseSheetQualityResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


def bullet_count(block: str) -> int:
    return len(re.findall(r"^\s*[-*]\s+", block, flags=re.M))


def numbered_or_heading_count(block: str) -> int:
    headings = len(re.findall(r"^###\s+", block, flags=re.M))
    numbered = len(re.findall(r"^\s*(?:\d+[.)]|[-*])\s+", block, flags=re.M))
    return max(headings, numbered)


def repeated_content_errors(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    lines = []
    for line in useful_lines(text):
        if len(line) <= 50 or line.startswith("#"):
            continue
        normalized = normalize(line)
        if normalized.count("`code`") >= 1 and len(normalized.replace("`code`", "").strip(" .:-;0123456789n")) < 20:
            continue
        lines.append(normalized)
    counts = Counter(lines)
    for line, count in counts.items():
        if count >= 2:
            errors.append(f"{path}: paragraphe répété -> {line[:90]}")
            break
    return errors


def cross_sheet_repetition_errors(files: list[Path]) -> list[str]:
    repeated: dict[str, list[Path]] = {}
    ignored_prefixes = (
        "- séances :",
        "- td lié :",
        "- tp lié :",
        "- évaluation ou projet lié :",
        "- dossier de progression :",
        "- capacités travaillées",
    )
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw in useful_lines(text):
            line = raw.strip()
            lowered = line.lower()
            if len(line) < 70 or line.startswith("#") or lowered.startswith(ignored_prefixes):
                continue
            repeated.setdefault(normalize(line), []).append(path)
    errors: list[str] = []
    for line, paths in sorted(repeated.items(), key=lambda item: (-len(item[1]), item[0])):
        distinct_paths = sorted(set(paths))
        if len(distinct_paths) > 5:
            sample = ", ".join(path.name for path in distinct_paths[:5])
            errors.append(
                "répétition transversale excessive "
                f"({len(distinct_paths)} fiches) -> {line[:100]} ; exemples: {sample}"
            )
    return errors


def analyze_sheet(path: Path, program_ids: set[str]) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    lowered = text.lower()
    metadata = read_frontmatter(path)

    missing = [key for key in REQUIRED_FRONTMATTER if key not in metadata]
    if missing:
        errors.append(f"{path}: frontmatter incomplet -> {', '.join(missing)}")
    if metadata.get("document_type") != "fiche_cours":
        errors.append(f"{path}: document_type attendu fiche_cours")
    if metadata.get("status") != "needs_review":
        errors.append(f"{path}: status attendu needs_review")
    if metadata.get("source") != "BO 2019":
        errors.append(f"{path}: source attendue BO 2019")
    if metadata.get("source_creation") not in {"generated_from_program", "adapted_from_drive"}:
        errors.append(f"{path}: source_creation invalide")
    if metadata.get("private_data") is not False:
        errors.append(f"{path}: private_data doit être false")

    capacities = frontmatter_capacities(metadata)
    if not capacities:
        errors.append(f"{path}: capacité officielle atomique absente")
    for capacity in sorted(capacities):
        if capacity not in program_ids:
            errors.append(f"{path}: capacité absente du YAML officiel -> {capacity}")

    if not SHEET_NAME_RE.match(path.name):
        errors.append(f"{path}: nom de fiche non conforme")
    sequence_id = str(metadata.get("sequence_id") or "")
    if sequence_id and not path.name.startswith(f"{sequence_id}_fiche_cours_"):
        errors.append(f"{path}: nom non relié à sequence_id {sequence_id}")
    if f"{sequence_id}_{sequence_id}_" in path.name:
        errors.append(f"{path}: doublon de préfixe")

    lines = useful_lines(text)
    if len(lines) < 55:
        errors.append(f"{path}: fiche trop courte ({len(lines)} lignes utiles)")
    if len(lines) > 135:
        errors.append(f"{path}: fiche trop longue ({len(lines)} lignes utiles)")

    for section in REQUIRED_SECTIONS:
        if f"## {section}".lower() not in lowered:
            errors.append(f"{path}: section manquante -> {section}")

    examples = section_text(text, "Exemples corrigés")
    if numbered_or_heading_count(examples) < 2:
        errors.append(f"{path}: moins de 2 exemples corrigés")

    errors_block = section_text(text, "Erreurs fréquentes")
    if bullet_count(errors_block) < 3:
        errors.append(f"{path}: moins de 3 erreurs fréquentes")

    exercises = section_text(text, "Mini-exercices")
    if numbered_or_heading_count(exercises) < 3:
        errors.append(f"{path}: moins de 3 mini-exercices")

    answers = section_text(text, "Réponses rapides")
    if bullet_count(answers) < 3 and len(re.findall(r"^\s*\d+[.)]", answers, flags=re.M)) < 3:
        errors.append(f"{path}: réponses rapides insuffisantes")

    for pattern in GENERIC_PATTERNS:
        if pattern in lowered:
            errors.append(f"{path}: formulation générique interdite -> {pattern}")
    errors.extend(repeated_content_errors(path, text))
    return errors


def analyze_course_sheets_quality(root: Path = ROOT, program_ids: set[str] | None = None) -> CourseSheetQualityResult:
    result = CourseSheetQualityResult()
    ids = program_ids or load_program_ids()
    files = sheet_files(root)
    if not files:
        result.errors.append("aucune fiche de cours")
        return result
    for path in files:
        result.checked_files += 1
        result.errors.extend(analyze_sheet(path, ids))
    result.errors.extend(cross_sheet_repetition_errors(files))
    return result


def main() -> int:
    result = analyze_course_sheets_quality()
    if result.errors:
        print("check_course_sheets_quality: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(f"check_course_sheets_quality: PASS ({result.checked_files} fiches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
