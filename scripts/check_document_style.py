#!/usr/bin/env python3
"""Check shared documentary style markers for pilot sequence documents."""

from __future__ import annotations

from scripts._qa_common import ROOT, pedagogical_documents, print_result

REQUIRED_BY_DOC = {
    "cours_eleve.md": ["Objectifs", "Erreurs fréquentes", "Auto-évaluation"],
    "trace_ecrite.md": ["Notions essentielles", "Auto-positionnement"],
    "td.md": ["Objectifs", "Corrigé associé"],
    "tp.md": ["Objectif", "Critères de réussite"],
    "fiche_methode.md": ["Méthode", "Erreurs fréquentes"],
    "aides_progressives.md": ["Aides progressives", "Auto-évaluation"],
    "corrige.md": ["Réponse attendue", "Barème"],
    "guide_professeur.md": ["Objectifs", "Différenciation"],
    "evaluation.md": ["Compétences évaluées", "Barème"],
    "projet_associe.md": ["Cahier des charges", "Critères d'évaluation"],
}


def main() -> None:
    errors: list[str] = []
    for path in pedagogical_documents():
        if path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        missing = []
        if not text.lstrip().startswith("---"):
            missing.append("frontmatter")
        if "\n# " not in "\n" + text:
            missing.append("titre niveau 1")
        if "\n## " not in text:
            missing.append("titres niveau 2")
        for marker in REQUIRED_BY_DOC.get(path.name, []):
            if marker.lower() not in text.lower():
                missing.append(marker)
        if missing:
            errors.append(f"{path.relative_to(ROOT)}: marqueurs de style manquants -> {', '.join(missing)}")
    print_result("check_document_style", errors)


if __name__ == "__main__":
    main()
