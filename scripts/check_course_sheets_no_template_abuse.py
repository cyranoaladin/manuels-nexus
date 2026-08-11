#!/usr/bin/env python3
"""Detect template abuse in course sheets."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from scripts._qa_common import ROOT
from scripts._course_sheets_common import normalize, section_text, sheet_files, useful_lines

FORBIDDEN_TEMPLATE_LINES = [
    "on reprend le premier exemple",
    "doit être défini avec son rôle",
    "la réponse doit montrer les étapes utiles",
    "cas vide ou minimal",
]

GENERIC_METHOD_STARTS = (
    "identifier le cas limite",
    "relier la conclusion",
    "écrire un exemple minimal",
    "appliquer la méthode",
)


@dataclass
class CourseSheetTemplateResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


def normalized_section_lines(text: str, section: str) -> list[str]:
    return [normalize(line) for line in useful_lines(section_text(text, section)) if not line.startswith("##")]


def analyze_course_sheets_no_template_abuse(root: Path = ROOT) -> CourseSheetTemplateResult:
    result = CourseSheetTemplateResult()
    files = sheet_files(root)
    if not files:
        result.errors.append("aucune fiche de cours")
        return result
    all_lines: Counter[str] = Counter()
    retain_sections: Counter[str] = Counter()
    auto_sections: Counter[str] = Counter()
    for path in files:
        result.checked_files += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        lowered = text.lower()
        for phrase in FORBIDDEN_TEMPLATE_LINES:
            if phrase in lowered:
                result.errors.append(f"{path}: phrase de gabarit interdite -> {phrase}")
        for line in useful_lines(text):
            if len(line) >= 70 and not line.startswith("|") and not line.startswith("#"):
                all_lines[normalize(line)] += 1
        retain_sections["\n".join(normalized_section_lines(text, "À retenir"))] += 1
        auto_sections["\n".join(normalized_section_lines(text, "Auto-évaluation"))] += 1
        methods = normalized_section_lines(text, "Méthodes")
        generic_methods = [line for line in methods if line.lstrip("1234567890. ").startswith(GENERIC_METHOD_STARTS)]
        if methods and len(generic_methods) >= max(2, len(methods) - 1):
            result.errors.append(f"{path}: méthodes trop génériques")
        examples = section_text(text, "Exemples corrigés").lower()
        if "reprend le premier exemple" in examples or "donnée différente" in examples:
            result.errors.append(f"{path}: exemples corrigés limités à une variation superficielle")
    for line, count in all_lines.items():
        if count > 5:
            result.errors.append(f"phrase apparaît dans {count} fiches -> {line[:100]}")
    for section_name, counter in [("À retenir", retain_sections), ("Auto-évaluation", auto_sections)]:
        for signature, count in counter.items():
            if signature and count > 5:
                label = "auto-évaluation trop similaire" if section_name == "Auto-évaluation" else "à retenir trop similaire"
                result.errors.append(f"{label} dans {count} fiches -> {signature[:100]}")
    return result


def main() -> int:
    result = analyze_course_sheets_no_template_abuse()
    if result.errors:
        print("check_course_sheets_no_template_abuse: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(f"check_course_sheets_no_template_abuse: PASS ({result.checked_files} fiches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
