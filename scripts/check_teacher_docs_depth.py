#!/usr/bin/env python3
"""Check teacher documents contain actual corrected questions and criteria."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEQUENCES = [ROOT / "premiere/sequences/s01_representation_donnees", ROOT / "terminale/sequences/s01_structures_donnees_interfaces_implementations"]
FILES = ["corrige_professeur.md", "evaluation_corrigee.md", "grille_competences.md", "version_amenagee.md", "bareme.md", "sources.md"]
REQUIRED = {
    "corrige_professeur.md": ["Réponse attendue", "Justification", "Barème question par question", "Variante acceptable", "Erreurs fréquentes", "Remédiation associée", "Critère de réussite", "Capacité officielle associée"],
    "evaluation_corrigee.md": ["Durée standard", "Matériel", "Correction complète", "Barème", "Erreur fréquente", "Remédiation"],
    "grille_competences.md": ["Capacité", "Critères observables", "Niveau fragile", "Niveau attendu", "Niveau avancé", "Erreurs typiques", "Remédiation", "Lien évaluation"],
    "version_amenagee.md": ["Version élève aménagée", "Consigne réécrite", "Aide intégrée", "Barème adapté", "Durée aménagée", "Objectif conservé"],
    "bareme.md": ["Total : 20 points", "Question", "Capacité visée", "Erreur typique pénalisante"],
    "sources.md": ["Sources institutionnelles", "Sources techniques", "Ressources Drive", "Séparation élève/professeur", "Capacités atomiques citées"],
}

def count_questions(text: str) -> int:
    return len(re.findall(r"^## (?:Question|Exercice) \d+", text, flags=re.M)) + len(re.findall(r"^### Question \d+", text, flags=re.M))

def main() -> int:
    errors = []
    for seq in SEQUENCES:
        for name in FILES:
            path = seq / name
            if not path.exists():
                errors.append(f"missing {path.relative_to(ROOT)}")
                continue
            text = path.read_text(encoding='utf-8', errors='replace')
            if 'status: needs_review' not in text:
                errors.append(f"{path.relative_to(ROOT)}: status needs_review missing")
            for term in REQUIRED[name]:
                if term not in text:
                    errors.append(f"{path.relative_to(ROOT)}: missing {term}")
            if name in {"corrige_professeur.md", "evaluation_corrigee.md", "version_amenagee.md", "bareme.md"} and count_questions(text) < 8:
                errors.append(f"{path.relative_to(ROOT)}: fewer than 8 question-level entries")
            if name == "grille_competences.md" and text.count('|') < 90:
                errors.append(f"{path.relative_to(ROOT)}: competency grid too thin")
    if errors:
        print('check_teacher_docs_depth: KO')
        for error in errors:
            print(f'- {error}')
        return 1
    print('check_teacher_docs_depth: PASS')
    return 0

if __name__ == '__main__':
    sys.exit(main())
