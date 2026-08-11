#!/usr/bin/env python3
"""Check that SKILLS.md lists the essential production skills."""

from __future__ import annotations

from scripts._qa_common import ROOT, print_result


REQUIRED_MARKERS = [
    "inventorier les ressources",
    "mapper le programme officiel",
    "rédiger cours",
    "rédiger trace",
    "rédiger TD",
    "rédiger TP",
    "rédiger évaluation",
    "rédiger corrigé",
    "produire QCM",
    "produire guide professeur",
    "contrôler la qualité pédagogique",
    "contrôler la qualité technique",
    "publier",
    "juger la substance",
    "connecter le corpus au RAG",
    "intégrer `/AUDIT`",
    "réconcilier couverture programme",
    "rendre une unité chartée",
    "piloter les gates",
    "scraper/classifier les sources",
    "nsi_corpus",
]

FORBIDDEN_MARKERS = [
    "recherche " + "sém" + "antique dans `rag_education`",
]


def main() -> None:
    path = ROOT / "SKILLS.md"
    errors: list[str] = []
    if not path.exists():
        print_result("check_skills_governance", ["SKILLS.md absent"])
    text = path.read_text(encoding="utf-8")
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"SKILLS.md: skill ou marqueur manquant -> {marker}")
    for marker in FORBIDDEN_MARKERS:
        if marker in text:
            errors.append(f"SKILLS.md: doctrine RAG obsolète -> {marker}")
    print_result("check_skills_governance", errors)


if __name__ == "__main__":
    main()
