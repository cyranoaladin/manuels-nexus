#!/usr/bin/env python3
"""Gate : les variantes eleve (complet, amenagee) ne contiennent pas de corriges.

Adapte depuis corpus_nsi check_eleve_no_corrige.py.
Scanne les fichiers .tex des chapitres et du build/ pour les motifs interdits.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN = [
    re.compile(r"\\begin\{corrige\}"),
    re.compile(r"Réponse attendue", re.IGNORECASE),
    re.compile(r"\\section\*?\{Corrigé", re.IGNORECASE),
    re.compile(r"corrige_professeur", re.IGNORECASE),
]

# QCM : diagnostic adjacent a une option = fuite de reponse
QCM_DIAG_RE = re.compile(r"\\item\s.*?\\quad\s*\\textit\{Si", re.IGNORECASE | re.DOTALL)

# Fichiers qui DOIVENT contenir des corriges (exclus du scan)
ALLOWED_DIRS = {"corriges", "coups_de_pouce", "_harvest"}
ALLOWED_SUFFIXES = {"corrige", "corrigé", "CO-", "CDP", "professeur"}


def is_allowed(path: Path) -> bool:
    if any(d in path.parts for d in ALLOWED_DIRS):
        return True
    return any(s in path.stem for s in ALLOWED_SUFFIXES)


def _find_violations(root: Path, path: Path, content: str) -> list[str]:
    violations: list[str] = []
    for pattern in FORBIDDEN:
        matches = pattern.findall(content)
        if matches:
            rel = path.relative_to(root)
            violations.append(f"  {rel}: found '{matches[0]}'")
    # QCM : diagnostic adjacent a une option
    qcm_hits = QCM_DIAG_RE.findall(content)
    if qcm_hits and "qcm" in str(path).lower():
        rel = path.relative_to(root)
        violations.append(f"  {rel}: QCM diagnostic adjacent a une option (revele la reponse)")
    return violations


def scan(root: Path, prefix: str | None = None) -> tuple[int, list[str]]:
    """Scanne le corpus entier ou les chapitres et builds lies a ``prefix``."""
    if prefix is not None and not prefix.strip():
        raise ValueError("prefix vide ou compose uniquement d'espaces")

    chapters_root = root / "chapitres"
    if prefix is None:
        chapter_files = sorted(chapters_root.rglob("*.tex")) if chapters_root.exists() else []
    else:
        matching_chapters = (
            sorted(
                path
                for path in chapters_root.iterdir()
                if path.is_dir() and path.name.startswith(prefix)
            )
            if chapters_root.exists()
            else []
        )
        if not matching_chapters:
            raise ValueError(f"aucun chapitre ne correspond au prefix '{prefix}'")
        chapter_files = sorted(
            path for chapter in matching_chapters for path in chapter.rglob("*.tex")
        )

    selected: list[tuple[Path, str]] = []
    for path in chapter_files:
        if is_allowed(path):
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        selected.append((path, content))

    build_root = root / "build"
    if build_root.exists():
        for path in sorted(build_root.rglob("*.tex")):
            if is_allowed(path):
                continue
            content = path.read_text(encoding="utf-8", errors="replace")
            if prefix is not None:
                relative_build_path = str(path.relative_to(build_root))
                if prefix not in relative_build_path and prefix not in content:
                    continue
            selected.append((path, content))

    if prefix is not None and not selected:
        raise ValueError(f"aucun fichier effectivement verifie pour le prefix '{prefix}'")

    checked = 0
    violations: list[str] = []
    for path, content in selected:
        checked += 1
        violations.extend(_find_violations(root, path, content))
    return checked, violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", help="limite le scan aux chapitres et builds lies au prefix")
    args = parser.parse_args(argv)

    try:
        checked, violations = scan(ROOT, args.prefix)
    except ValueError as exc:
        print(f"ROUGE -- filtre invalide : {exc}", file=sys.stderr)
        return 2

    if violations:
        print("ROUGE -- contenu corrige detecte dans des fichiers eleve :")
        for v in violations:
            print(v)
        return 1

    print(f"VERT -- {checked} fichiers verifies, aucune fuite de corrige.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
