#!/usr/bin/env python3
"""Reject residual generic generated scaffolding in student-facing supports."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT, read_frontmatter


FORBIDDEN_PHRASES = [
    "Lire la situation sans modifier les données",
    "Appliquer une méthode explicitement liée aux capacités",
    "Produire un résultat contrôlable",
    "On modifie une seule donnée",
    "la méthode reste valable",
    "construire un cas limite générique",
]

EXCLUDED_TYPES = {"corrige", "bareme", "guide_professeur", "guide_prof", "sources"}
EXCLUDED_NAME_PARTS = {"corrige", "bareme", "barème", "guide"}


@dataclass
class TemplateResidueResult:
    errors: list[str] = field(default_factory=list)
    files_checked: int = 0


def is_student_support(path: Path) -> bool:
    if path.suffix != ".md":
        return False
    if "03_progressions" not in path.parts:
        return False
    lower_name = path.name.lower()
    if any(part in lower_name for part in EXCLUDED_NAME_PARTS):
        return False
    metadata = read_frontmatter(path)
    document_type = str(metadata.get("document_type", "")).strip().lower()
    return document_type not in EXCLUDED_TYPES


def analyze_generated_template_residue(root: Path = ROOT) -> TemplateResidueResult:
    result = TemplateResidueResult()
    for path in sorted((root / "03_progressions").rglob("*.md")):
        if not is_student_support(path):
            continue
        result.files_checked += 1
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            normalized = re.sub(r"\s+", " ", line).strip()
            for phrase in FORBIDDEN_PHRASES:
                if phrase.lower() in normalized.lower():
                    rel = path.relative_to(root).as_posix()
                    result.errors.append(f"{rel}:{lineno}: formulation gabarit interdite -> {phrase}")
    return result


def main() -> int:
    result = analyze_generated_template_residue()
    if result.errors:
        print("check_generated_template_residue: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(f"check_generated_template_residue: PASS ({result.files_checked} supports élèves)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
