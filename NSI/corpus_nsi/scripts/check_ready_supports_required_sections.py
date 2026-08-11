#!/usr/bin/env python3
"""Blocking required-section gate for supports attached to ready sessions."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scripts._qa_common import ROOT
from scripts.check_first_batch_document_quality import FIRST_BATCH_PREFIXES, REQUIRED_KINDS, find_kind_file

REQUIRED_BY_KIND = {
    "cours": ["Objectifs spécifiques", "Capacités officielles", "Situation-problème", "Activité d’entrée", "Exemple", "Exercices", "Corrigés", "Erreurs fréquentes", "Remédiation", "Différenciation"],
    "trace": ["Trace", "Exemple", "Exercices", "Corrigé", "Erreurs fréquentes", "Remédiation"],
    "td": ["Exercices numérotés", "Corrigé", "Erreurs fréquentes", "Remédiation", "Critères de réussite"],
    "tp": ["Consigne technique", "Starter code", "Tests attendus", "Livrable vérifiable", "Cas limite", "Corrigé"],
    "corrige": ["Corrigé exercice 1", "Corrigé exercice 8", "Barème", "Remédiation"],
    "evaluation": ["Question 1", "Question 4", "Barème", "Critères de réussite", "Corrigé"],
    "bareme": ["Barème question 1", "Barème question 4", "Critères de réussite"],
    "remediation": ["Erreur fréquente", "Activité corrective EF1", "Activité corrective EF4"],
    "version_amenagee": ["Énoncé élève", "Aide intégrée", "Espace de réponse", "Corrigé", "Version aménagée"],
}


@dataclass
class ReadySectionsResult:
    errors: list[str] = field(default_factory=list)


def analyze_ready_sections(root: Path = ROOT, prefixes: list[str] | None = None) -> ReadySectionsResult:
    prefixes = prefixes or FIRST_BATCH_PREFIXES
    result = ReadySectionsResult()
    for prefix in prefixes:
        for kind in REQUIRED_KINDS:
            path = find_kind_file(root, prefix, kind)
            if path is None:
                result.errors.append(f"{prefix}: support {kind} absent")
                continue
            text = path.read_text(encoding="utf-8", errors="replace").lower()
            for section in REQUIRED_BY_KIND.get(kind, []):
                if section.lower() not in text:
                    result.errors.append(f"{path}: section manquante -> {section}")
    return result


def main() -> int:
    result = analyze_ready_sections()
    if result.errors:
        print("check_ready_supports_required_sections: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print("check_ready_supports_required_sections: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
