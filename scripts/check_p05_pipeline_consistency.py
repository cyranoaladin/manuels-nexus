#!/usr/bin/env python3
"""Check the single P05 CSV pipeline across documents and tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scripts._qa_common import ROOT


@dataclass
class P05PipelineResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


PIPELINE_TOKENS = [
    "1. Charger avec `csv.DictReader`",
    "2. Convertir `POPULATION` avec `int(row[\"POPULATION\"])`",
    "3. Séparer `valides` et `erreurs`",
    "4. Filtrer les lignes valides par `CONTINENT`",
    "5. Trier les lignes valides par `CONTINENT` puis `POPULATION`",
]
EXPECTED_TOKENS = [
    'valides = ["Allemagne", "Albanie", "Brésil"]',
    'erreurs = [{"PAYS": "Erreur", "CAPITALE": "NA", "CONTINENT": "Europe", "POPULATION": "invalide"}]',
    'Europe valide = ["Allemagne", "Albanie"]',
]
FORBIDDEN_ORDER_HINTS = [
    "Filtrer l'Europe puis convertir",
    "filtrer avant conversion",
    "ligne invalide isolée avant conversion",
]


def p05_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for base in [
        root / "03_progressions" / "supports" / "premiere" / "P05",
        root / "03_progressions" / "fiches_cours" / "premiere" / "P05",
    ]:
        if base.exists():
            files.extend(sorted(path for path in base.rglob("*") if path.suffix in {".md", ".py"}))
    return files


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()


def analyze_p05_pipeline_consistency(root: Path = ROOT) -> P05PipelineResult:
    result = P05PipelineResult()
    for path in p05_files(root):
        result.checked_files += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        local_errors: list[str] = []
        if path.suffix == ".md":
            for token in PIPELINE_TOKENS:
                if token not in text:
                    local_errors.append(f"ordre logique absent -> {token}")
            for token in EXPECTED_TOKENS:
                if token not in text:
                    local_errors.append(f"résultat attendu absent -> {token}")
            for marker in FORBIDDEN_ORDER_HINTS:
                if marker in text:
                    local_errors.append(f"ordre logique contradictoire -> {marker}")
        if path.name == "P05_tests_attendus_tables_csv.py":
            if 'valides, erreurs = convertir_populations(EXTRAIT)' not in text:
                local_errors.append("tests: conversion/séparation avant filtrage absente")
            if 'europe = filtrer_par_continent(valides, "Europe")' not in text:
                local_errors.append("tests: filtrage Europe doit porter sur les lignes valides")
            if '["Allemagne", "Albanie"]' not in text:
                local_errors.append('tests: résultat Europe valide attendu absent -> ["Allemagne", "Albanie"]')
        for error in local_errors:
            result.errors.append(f"{rel(path, root)}: {error}")
    return result


def main() -> int:
    result = analyze_p05_pipeline_consistency()
    if result.errors:
        print("check_p05_pipeline_consistency: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(f"check_p05_pipeline_consistency: PASS ({result.checked_files} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
