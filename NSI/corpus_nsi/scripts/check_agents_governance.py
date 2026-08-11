#!/usr/bin/env python3
"""Check that AGENTS.md contains the non-negotiable governance sections."""

from __future__ import annotations

from scripts._qa_common import ROOT, print_result


REQUIRED_MARKERS = [
    "Mission générale",
    "Règles non négociables",
    "Statuts autorisés",
    "Source locale Drive",
    "Arbre canonique",
    "politique `/AUDIT`",
    "Agent Inventaire",
    "Agent Programme",
    "Agent Auteur pédagogique",
    "Agent Scientifique",
    "Agent Code",
    "Agent Évaluation",
    "Agent Différenciation",
    "Agent Édition",
    "Agent QA final",
    "Agent RAG",
    "Agent Juge de substance",
    "interdit et constitue une fraude de gate",
    "validation LLM seule",
    "séparation stricte juge / auteur",
    "03_progressions/supports/",
    "nsi_corpus",
]

FORBIDDEN_MARKERS = [
    "recherche " + "sém" + "antique dans `rag_education`",
    "collection `rag_education`), pas extraites",
]


def main() -> None:
    path = ROOT / "AGENTS.md"
    errors: list[str] = []
    if not path.exists():
        print_result("check_agents_governance", ["AGENTS.md absent"])
    text = path.read_text(encoding="utf-8")
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"AGENTS.md: marqueur manquant -> {marker}")
    for marker in FORBIDDEN_MARKERS:
        if marker in text:
            errors.append(f"AGENTS.md: doctrine RAG obsolète -> {marker}")
    print_result("check_agents_governance", errors)


if __name__ == "__main__":
    main()
