#!/usr/bin/env python3
"""Check required pedagogical sections in pilot sequence documents."""

from __future__ import annotations

from typing import Dict, List

from scripts._qa_common import ROOT, pedagogical_documents, print_result, strip_frontmatter

REQUIRED: Dict[str, List[str]] = {
    "cours_eleve.md": [
        "situation-problème",
        "objectifs",
        "prérequis",
        "activité d'introduction",
        "formalisation",
        "définitions",
        "exemples corrigés",
        "exercices intégrés",
        "erreurs fréquentes",
        "à retenir",
        "auto-évaluation",
        "extension",
        "aides progressives",
    ],
    "trace_ecrite.md": [
        "notions essentielles",
        "définitions",
        "méthodes",
        "exemples minimaux",
        "points de vigilance",
        "à savoir refaire",
        "auto-positionnement",
    ],
    "td.md": [
        "situation-problème",
        "objectifs",
        "exercices",
        "socle",
        "standard",
        "expert",
        "analyse de code",
        "écriture de code",
        "justification",
        "corrigé associé",
    ],
    "tp.md": [
        "contexte",
        "objectif",
        "fichiers fournis",
        "travail demandé",
        "étapes",
        "tests",
        "livrable",
        "critères de réussite",
        "aides progressives",
        "extension experte",
    ],
    "corrige.md": [
        "réponse attendue",
        "justification",
        "variante acceptable",
        "erreurs fréquentes",
        "barème",
        "code testé",
    ],
    "guide_professeur.md": [
        "objectifs",
        "durée",
        "scénario séance par séance",
        "difficultés prévisibles",
        "remédiation",
        "différenciation",
        "questions orales",
        "critères d'évaluation",
        "prolongements",
    ],
    "evaluation.md": [
        "durée",
        "matériel autorisé",
        "compétences évaluées",
        "barème",
        "questions progressives",
        "programmation",
        "justification",
        "analyse de code",
        "corrigé lié",
    ],
    "fiche_methode.md": [
        "situation-problème",
        "méthode",
        "exemple",
        "erreurs fréquentes",
        "auto-évaluation",
    ],
    "aides_progressives.md": [
        "situation-problème",
        "aides progressives",
        "niveau 1",
        "niveau 2",
        "niveau 3",
        "erreurs fréquentes",
        "extension",
        "auto-évaluation",
    ],
    "projet_associe.md": [
        "cahier des charges",
        "jalons",
        "livrables",
        "critères d'évaluation",
        "grille de soutenance",
        "version minimale",
        "version standard",
        "version experte",
    ],
}


def main() -> None:
    errors: List[str] = []
    for path in pedagogical_documents():
        if path.suffix != ".md":
            continue
        rel = path.relative_to(ROOT)
        body = strip_frontmatter(path.read_text(encoding="utf-8", errors="replace")).lower()
        for section in REQUIRED.get(path.name, []):
            if section.lower() not in body:
                errors.append(f"{rel}: section manquante -> {section}")

    print_result("check_required_sections", errors)


if __name__ == "__main__":
    main()
