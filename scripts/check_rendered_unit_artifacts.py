#!/usr/bin/env python3
"""Render a unit to a temporary directory and verify student/prof separation."""

from __future__ import annotations

import argparse
import html
import re
import tempfile
from pathlib import Path

from scripts._qa_common import print_result
from scripts.render_unit import CHARTER, TEACHER_TOKENS, is_teacher_section_title, render


HEADING = re.compile(r"<h[1-4][^>]*>(.*?)</h[1-4]>", re.I | re.S)
SOURCE = re.compile(r'<section\s+data-source="([^"]+)"', re.I)
INLINE_TEACHER_CONTENT = re.compile(
    r"\b(?:r[ée]ponses?\s+attendues?\s*:|corrig[ée]\s+(?:professeur|complet)|"
    r"bar[èe]me\s+correcteur|[ée]l[ée]ments?\s+de\s+correction)\b",
    re.I,
)
NUMBERED_ANSWER_KEY = re.compile(
    r"\br[ée]ponse\s+\d+\s*:", re.I,
)
DIRECT_FINAL_ANSWER = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:r[ée]sultat\s+(?:final|de\s+r[ée]f[ée]rence)|"
    r"r[ée]ponse\s+attendue|livrable\s+pr[ée]rempli)\s*:\s*"
    r"(?!(?:à\s+(?:d[ée]terminer|compl[ée]ter)|v[ée]rifier|[ée]crire|produire|justifier)\b).+",
)


def plain_html(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def location(text: str, offset: int) -> str:
    line = text.count("\n", 0, offset) + 1
    excerpt = plain_html(text[offset : text.find("\n", offset) if "\n" in text[offset:] else len(text)])
    return f"ligne {line} : {excerpt[:120]}"


def student_leak_errors(student: str) -> list[str]:
    """Report teacher-only content visible in a rendered student document.

    The checks are structural and contextual.  A prose scenario mentioning a
    teacher is acceptable; a teacher-only heading, an answer-key phrase or a
    dedicated correction source is not.
    """
    errors: list[str] = []
    for heading in HEADING.finditer(student):
        title = plain_html(heading.group(1))
        if is_teacher_section_title(title):
            errors.append(f"section professeur visible ({location(student, heading.start())})")
    for source in SOURCE.finditer(student):
        filename = Path(source.group(1)).name.lower()
        if any(token in filename for token in TEACHER_TOKENS):
            errors.append(f"ressource professeur visible ({location(student, source.start())})")
    for match in INLINE_TEACHER_CONTENT.finditer(plain_html(student)):
        errors.append(f"contenu de correction visible : {match.group(0)}")
    for match in NUMBERED_ANSWER_KEY.finditer(plain_html(student)):
        errors.append(f"réponse numérotée visible : {match.group(0)}")
    for match in DIRECT_FINAL_ANSWER.finditer(plain_html(student)):
        errors.append(f"résultat final prérempli visible : {match.group(0)[:120]}")
    return errors


def check_unit(unit: str) -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="nsi_render_") as tmp:
        out = render(unit, Path(tmp))
        expected = {
            "version élève HTML": out / f"{unit}_eleve.html",
            "version prof HTML": out / f"{unit}_prof.html",
            "version élève PDF": out / f"{unit}_eleve.pdf",
            "version prof PDF": out / f"{unit}_prof.pdf",
        }
        for label, path in expected.items():
            if not path.exists() or path.stat().st_size < 80:
                errors.append(f"{unit}: {label} absent ou vide")
        student = (out / f"{unit}_eleve.html").read_text(encoding="utf-8", errors="replace")
        teacher = (out / f"{unit}_prof.html").read_text(encoding="utf-8", errors="replace")
        if CHARTER not in student or CHARTER not in teacher:
            errors.append(f"{unit}: marqueur de charte absent")
        for error in student_leak_errors(student):
            errors.append(f"{unit}: version élève contient {error}")
        lower_teacher = teacher.lower()
        if not any(token in lower_teacher for token in ["corrige", "corrigé", "bareme", "barème"]):
            errors.append(f"{unit}: version prof ne contient pas corrigé/barème")
        print(f"{unit}: version élève et version prof vérifiées dans un rendu temporaire")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", required=True)
    args = parser.parse_args()
    print_result("check_rendered_unit_artifacts", check_unit(args.unit))


if __name__ == "__main__":
    main()
