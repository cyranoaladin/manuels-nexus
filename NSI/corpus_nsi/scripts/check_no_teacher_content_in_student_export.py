#!/usr/bin/env python3
"""Release check: student exports must not contain teacher/correction content."""

from __future__ import annotations

from typing import List

from scripts._qa_common import ROOT, print_result

EXPORT_DIRS = [ROOT / "exports" / "eleves", ROOT / "publication" / "eleves"]
FORBIDDEN = ("corrige", "corrigé", "guide_prof", "professeur", "barème", "bareme")


def main() -> None:
    errors: List[str] = []
    for directory in EXPORT_DIRS:
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_dir():
                continue
            rel = path.relative_to(ROOT)
            lower_name = path.name.lower()
            if any(token in lower_name for token in FORBIDDEN):
                errors.append(f"{rel}: contenu professeur dans export élève")
                continue
            if path.suffix.lower() in {".md", ".tex", ".txt", ".json"}:
                text = path.read_text(encoding="utf-8", errors="replace").lower()
                if any(token in text for token in FORBIDDEN):
                    errors.append(f"{rel}: marqueur professeur/corrigé détecté")
    print_result("check_no_teacher_content_in_student_export", errors)


if __name__ == "__main__":
    main()
