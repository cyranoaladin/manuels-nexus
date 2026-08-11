#!/usr/bin/env python3
"""Ensure course sheets have one quick answer per mini-exercise."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT, strip_frontmatter


@dataclass
class CourseSheetAnswerCountResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


def course_sheet_files(root: Path) -> list[Path]:
    base = root / "03_progressions" / "fiches_cours"
    if not base.exists():
        return []
    return sorted(base.rglob("*_fiche_cours_*.md"))


def section(text: str, title: str) -> str:
    match = re.search(rf"^## {re.escape(title)}\s*$", text, flags=re.M)
    if not match:
        return ""
    start = match.end()
    next_match = re.search(r"^##\s+", text[start:], flags=re.M)
    end = start + next_match.start() if next_match else len(text)
    return text[start:end]


def count_items(block: str) -> int:
    numbered = re.findall(r"^\s*\d+\.\s+\S", block, flags=re.M)
    if numbered:
        return len(numbered)
    titled = re.findall(r"^### Mini-exercice\b", block, flags=re.M)
    return len(titled)


def analyze_course_sheet_exercise_answer_count(
    root: Path = ROOT, files: list[Path] | None = None
) -> CourseSheetAnswerCountResult:
    result = CourseSheetAnswerCountResult()
    for path in files or course_sheet_files(root):
        result.checked_files += 1
        body = strip_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        mini = count_items(section(body, "Mini-exercices"))
        answers = len(re.findall(r"^\s*\d+\.\s+\S", section(body, "Réponses rapides"), flags=re.M))
        rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()
        if mini == 0:
            result.errors.append(f"{rel}: aucune section Mini-exercices dénombrable")
        if mini != answers:
            result.errors.append(f"{rel}: {mini} mini-exercices mais {answers} réponses rapides")
    return result


def main() -> int:
    result = analyze_course_sheet_exercise_answer_count()
    if result.errors:
        print("check_course_sheet_exercise_answer_count: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(f"check_course_sheet_exercise_answer_count: PASS ({result.checked_files} fiches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
