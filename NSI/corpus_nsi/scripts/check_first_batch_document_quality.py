#!/usr/bin/env python3
"""Blocking quality gate for the currently usable batch P00-P05 and T00-T05."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from pathlib import Path

from scripts._qa_common import load_pilot_scope, load_program_entries

ROOT = Path(__file__).resolve().parents[1]
FIRST_BATCH_PREFIXES = load_pilot_scope().get("first_batch_prefixes", [])
REQUIRED_KINDS = [
    "cours",
    "trace",
    "td",
    "tp",
    "corrige",
    "evaluation",
    "bareme",
    "remediation",
    "version_amenagee",
]
REQUIRED_MARKERS = [
    "Objectifs",
    "Capacités officielles",
    "Prérequis",
    "Situation-problème",
    "Activité d’entrée",
    "Exemple",
    "Exercices",
    "Corrigé",
    "Erreurs fréquentes",
    "Remédiation",
    "Différenciation",
    "Critères de réussite",
    "Séance(s) correspondante(s)",
]
CAPACITY_RE = re.compile(r"\b[PT]-[A-Z]+(?:-[A-Z]+)*-\d{2}[A-Z]?\b")
GENERIC_PHRASES = [
    "contenu substantiel",
    "réponse attendue avec justification",
    "support spécifique non produit",
    "à préciser",
    "simple liste d'aides",
    "document réel de première tranche",
]
MIN_LINES = {
    "cours": 180,
    "trace": 60,
    "td": 100,
    "tp": 90,
    "corrige": 90,
    "evaluation": 70,
    "bareme": 60,
    "remediation": 70,
    "version_amenagee": 75,
}


@dataclass
class FirstBatchResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


def find_kind_file(root: Path, prefix: str, kind: str) -> Path | None:
    # Try exact case first, then uppercase variant (TD, TP)
    for variant in [kind, kind.upper()]:
        pattern = f"{prefix}_{variant}_*.md"
        matches = sorted(root.rglob(pattern))
        if matches:
            return matches[0]
    return None


def find_all_kind_files(root: Path, prefix: str, kind: str) -> list[Path]:
    """Return ALL files matching {prefix}_{kind}_*.md (both cases)."""
    results: list[Path] = []
    for variant in [kind, kind.upper()]:
        pattern = f"{prefix}_{variant}_*.md"
        results.extend(root.rglob(pattern))
    return sorted(set(results))


def useful_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def extract_exercise_numbers(text: str) -> set[int]:
    return {int(value) for value in re.findall(r"^###\s+Exercice\s+(\d+)\b", text, flags=re.M)}


def extract_question_numbers(text: str) -> set[int]:
    return {int(value) for value in re.findall(r"^#{2,3}\s+Question\s+(\d+)\b", text, flags=re.M)}


def analyze_file(path: Path, prefix: str, kind: str, program_ids: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    program_ids = program_ids or set(load_program_entries())
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = useful_lines(text)
    minimum = MIN_LINES.get(kind, 60)
    if len(lines) < minimum:
        errors.append(f"{path}: profondeur insuffisante ({len(lines)} lignes utiles, minimum {minimum})")
    if "status: \"needs_review\"" not in text and "status: needs_review" not in text:
        errors.append(f"{path}: statut attendu needs_review")
    for marker in REQUIRED_MARKERS:
        if marker.lower() not in text.lower():
            errors.append(f"{path}: marqueur manquant -> {marker}")
    if not CAPACITY_RE.search(text):
        errors.append(f"{path}: aucune capacité officielle atomique")
    for capacity in CAPACITY_RE.findall(text):
        if capacity not in program_ids:
            errors.append(f"{path}: capacité inconnue -> {capacity}")
    for phrase in GENERIC_PHRASES:
        if phrase.lower() in text.lower():
            errors.append(f"{path}: formulation générique interdite -> {phrase}")
    if kind == "td" and len(extract_exercise_numbers(text)) < 8:
        errors.append(f"{path}: TD avec moins de 8 exercices")
    if kind == "tp":
        if "Starter code" not in text and "Consigne technique détaillée" not in text:
            errors.append(f"{path}: TP sans starter code ni consigne technique détaillée")
        for marker in ["Tests attendus", "Exemple d’exécution", "Livrable vérifiable", "Cas limite"]:
            if marker.lower() not in text.lower():
                errors.append(f"{path}: TP incomplet -> {marker}")
    if kind == "corrige" and "Corrigé exercice 8" not in text:
        errors.append(f"{path}: correction de chaque exercice non vérifiable")
    if kind == "evaluation":
        if not extract_question_numbers(text):
            errors.append(f"{path}: évaluation sans questions numérotées")
        if "Barème" not in text or "Critères de réussite" not in text:
            errors.append(f"{path}: évaluation sans barème ou critères de réussite")
    if kind == "bareme":
        if "Barème question 1" not in text or "Barème question 4" not in text:
            errors.append(f"{path}: barème non détaillé question par question")
    if kind == "remediation":
        if "Activité corrective" not in text:
            errors.append(f"{path}: remédiation sans activité corrective")
    if kind == "version_amenagee":
        for marker in ["Énoncé élève", "Aide intégrée", "Espace de réponse", "Version aménagée"]:
            if marker.lower() not in text.lower():
                errors.append(f"{path}: version aménagée incomplète -> {marker}")
    if prefix not in path.name:
        errors.append(f"{path}: préfixe de tranche absent du nom")
    return errors


def analyze_first_batch(root: Path = ROOT) -> FirstBatchResult:
    result = FirstBatchResult()
    program_ids = set(load_program_entries()) if root == ROOT else set()
    for prefix in FIRST_BATCH_PREFIXES:
        for kind in REQUIRED_KINDS:
            paths = find_all_kind_files(root, prefix, kind)
            if not paths:
                result.errors.append(f"{prefix}: support {kind} absent")
                continue
            for path in paths:
                result.checked_files += 1
                result.errors.extend(analyze_file(path, prefix, kind, program_ids or None))
    return result


def main() -> int:
    result = analyze_first_batch()
    if result.errors:
        print("check_first_batch_document_quality: KO")
        for error in result.errors[:120]:
            print(f"- {error}")
        return 1
    print(f"check_first_batch_document_quality: PASS ({result.checked_files} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
