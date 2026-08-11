#!/usr/bin/env python3
"""Check course sheets contain discipline-specific revision substance."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT, read_frontmatter
from scripts._course_sheets_common import normalize, section_text, sheet_files, useful_lines

GENERIC_PHRASES = [
    "on reprend le premier exemple",
    "avec une donnée différente",
    "doit être défini avec son rôle",
    "cas vide ou minimal",
    "la réponse doit montrer les étapes utiles",
    "hypothèse oubliée",
    "commencer par reconnaître la situation exacte",
]

VAGUE_ANSWER_PATTERNS = [
    "doit être défini",
    "étapes utiles",
    "hypothèse oubliée",
    "cas vide ou minimal",
    "réponse doit",
]


@dataclass
class CourseSheetSubstanceResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


def numbered_items(block: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    for line in block.splitlines():
        if re.match(r"^\s*(?:###|[0-9]+[.)]|[-*])\s+", line):
            if current:
                items.append("\n".join(current).strip())
            current = [line.strip()]
        elif current:
            current.append(line.strip())
    if current:
        items.append("\n".join(current).strip())
    return [item for item in items if item]


def section_signature(text: str, section: str) -> str:
    block = section_text(text, section)
    lines = [
        normalize(re.sub(r"\b[PT]-[A-Z]+(?:-[A-Z]+)*-\d{2}[A-Z]?\b", "CAP", line))
        for line in useful_lines(block)
        if not line.startswith("##")
    ]
    return "\n".join(lines)


def analyze_sheet(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    lowered = text.lower()
    metadata = read_frontmatter(path)
    notion = str(metadata.get("notion") or path.stem)

    for phrase in GENERIC_PHRASES:
        if phrase in lowered:
            errors.append(f"{path}: formulation générique -> {phrase}")

    examples = numbered_items(section_text(text, "Exemples corrigés"))
    if len(examples) < 2:
        errors.append(f"{path}: exemples corrigés insuffisants")
    for example in examples:
        low = example.lower()
        if "on reprend le premier exemple" in low or "donnée différente" in low:
            errors.append(f"{path}: exemple générique")
        if len(re.findall(r"\b\d+\b|`[^`]+`|[A-Z][A-Za-z_]*\(", example)) < 1 and len(example) < 110:
            errors.append(f"{path}: exemple trop peu concret -> {example[:80]}")
    normalized_examples = [normalize(example) for example in examples]
    if len(set(normalized_examples)) < len(normalized_examples):
        errors.append(f"{path}: exemples corrigés dupliqués")

    exercises = numbered_items(section_text(text, "Mini-exercices"))
    normalized_exercises = [normalize(re.sub(re.escape(notion.lower()), "NOTION", exercise.lower())) for exercise in exercises]
    if len(exercises) >= 2 and len(set(normalized_exercises)) < len(normalized_exercises):
        errors.append(f"{path}: mini-exercices trop proches")
    for exercise in exercises:
        if re.search(r"^(###\s*)?mini-exercice\s+\d+\s*$", exercise.lower()):
            errors.append(f"{path}: mini-exercice vide")

    answers = numbered_items(section_text(text, "Réponses rapides"))
    for answer in answers:
        low = answer.lower()
        if any(pattern in low for pattern in VAGUE_ANSWER_PATTERNS):
            errors.append(f"{path}: réponse rapide vague")
    if len(answers) >= 3 and sum(1 for answer in answers if len(answer) < 35) >= len(answers) - 1:
        errors.append(f"{path}: réponses rapides trop brèves")

    savoir = section_text(text, "À savoir").lower()
    if savoir.count(notion.lower()) >= 3 and len(set(normalize(line) for line in savoir.splitlines() if line.strip())) < 4:
        errors.append(f"{path}: fiche centrée sur le nom de notion sans substance")
    return errors


def analyze_course_sheets_substance(root: Path = ROOT) -> CourseSheetSubstanceResult:
    result = CourseSheetSubstanceResult()
    files = sheet_files(root)
    if not files:
        result.errors.append("aucune fiche de cours")
        return result
    signatures: dict[str, Counter[str]] = {"À retenir": Counter(), "Auto-évaluation": Counter()}
    for path in files:
        result.checked_files += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        result.errors.extend(analyze_sheet(path))
        for section in signatures:
            signature = section_signature(text, section)
            if signature:
                signatures[section][signature] += 1
    for section, counter in signatures.items():
        for signature, count in counter.items():
            if count > 5:
                result.errors.append(f"{section}: section copiée-collée dans {count} fiches -> {signature[:90]}")
    return result


def main() -> int:
    result = analyze_course_sheets_substance()
    if result.errors:
        print("check_course_sheets_substance: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(f"check_course_sheets_substance: PASS ({result.checked_files} fiches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
