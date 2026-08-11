#!/usr/bin/env python3
"""Check minimum depth of pilot documents."""

from __future__ import annotations

from typing import Dict, List
import re

from scripts._qa_common import ROOT, pedagogical_documents, print_result, useful_lines

MIN_LINES: Dict[str, int] = {
    "cours_eleve.md": 250,
    "trace_ecrite.md": 35,
    "td.md": 90,
    "tp.md": 70,
    "corrige.md": 90,
    "guide_professeur.md": 70,
    "evaluation.md": 60,
    "fiche_methode.md": 35,
    "aides_progressives.md": 45,
    "projet_associe.md": 45,
}


def count_pattern(lines: List[str], pattern: str) -> int:
    regex = re.compile(pattern, re.IGNORECASE)
    return sum(1 for line in lines if regex.search(line))


def main() -> None:
    errors: List[str] = []
    for path in pedagogical_documents():
        if path.suffix != ".md":
            continue
        rel = path.relative_to(ROOT)
        lines = useful_lines(path)
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

    print_result("check_document_depth", errors)


if __name__ == "__main__":
    main()
