#!/usr/bin/env python3
"""Require stronger documentary gates for validated or published resources."""

from __future__ import annotations

import sys
from pathlib import Path

from scripts._qa_common import ROOT, pedagogical_documents, read_frontmatter, strip_frontmatter, useful_lines
from scripts.check_document_depth import MIN_LINES, count_pattern
from scripts.check_document_style import REQUIRED_BY_DOC
from scripts.check_required_sections import REQUIRED

VALIDATING_STATUSES = {
    "validated_pedagogy",
    "validated_science",
    "validated_technical",
    "published",
}


def status_of(path: Path) -> str:
    metadata = read_frontmatter(path)
    return str(metadata.get("status") or metadata.get("statut") or "needs_review").strip()


def has_minimal_pedagogical_coherence(text: str) -> list[str]:
    lowered = text.lower()
    missing: list[str] = []
    for marker in ["objectif", "prérequis", "capacité", "exercice", "corrigé"]:
        if marker not in lowered:
            missing.append(marker)
    return missing


def check_path(path: Path) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8", errors="replace")
    body = strip_frontmatter(text).lower()
    lines = useful_lines(path)

    for section in REQUIRED.get(path.name, []):
        if section.lower() not in body:
            errors.append(f"{rel}: section requise absente -> {section}")

    minimum = MIN_LINES.get(path.name)
    if minimum and len(lines) < minimum:
        errors.append(f"{rel}: profondeur insuffisante ({len(lines)} lignes utiles, minimum {minimum})")

    if path.name == "cours_eleve.md":
        if count_pattern(lines, r"\bDéfinition\b") < 3:
            errors.append(f"{rel}: moins de 3 définitions formelles")
        if count_pattern(lines, r"\bExemple corrigé\b") < 5:
            errors.append(f"{rel}: moins de 5 exemples corrigés")
        if count_pattern(lines, r"\bErreur fréquente\b") < 3:
            errors.append(f"{rel}: moins de 3 erreurs fréquentes")
        if count_pattern(lines, r"\bExercice intégré\b") < 3:
            errors.append(f"{rel}: moins de 3 exercices intégrés")

    if path.name == "td.md":
        exercises = count_pattern(lines, r"^#{2,3}\s*Exercice\s+\d+")
        if exercises < 8 or exercises > 12:
            errors.append(f"{rel}: nombre d'exercices attendu entre 8 et 12, trouvé {exercises}")

    missing_style: list[str] = []
    if not text.lstrip().startswith("---"):
        missing_style.append("frontmatter")
    if "\n# " not in "\n" + text:
        missing_style.append("titre niveau 1")
    if "\n## " not in text:
        missing_style.append("titres niveau 2")
    for marker in REQUIRED_BY_DOC.get(path.name, []):
        if marker.lower() not in text.lower():
            missing_style.append(marker)
    if missing_style:
        errors.append(f"{rel}: marqueurs de style manquants -> {', '.join(missing_style)}")

    coherence_missing = has_minimal_pedagogical_coherence(text)
    if coherence_missing:
        errors.append(f"{rel}: cohérence pédagogique minimale absente -> {', '.join(coherence_missing)}")

    return errors


def main() -> int:
    errors: list[str] = []
    for path in pedagogical_documents():
        if path.suffix != ".md":
            continue
        if status_of(path) not in VALIDATING_STATUSES:
            continue
        errors.extend(check_path(path))

    if errors:
        print("check_validated_documents_quality_gates: KO")
        for error in errors:
            print(f"- {error}")
        return 1
    print("check_validated_documents_quality_gates: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
