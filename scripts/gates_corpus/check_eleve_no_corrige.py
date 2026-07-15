#!/usr/bin/env python3
"""Gate : les variantes eleve (complet, amenagee) ne contiennent pas de corriges.

Adapte depuis corpus_nsi check_eleve_no_corrige.py.
Scanne les fichiers .tex des chapitres et du build/ pour les motifs interdits.
"""
from __future__ import annotations

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

# Fichiers qui DOIVENT contenir des corriges (exclus du scan)
ALLOWED_DIRS = {"corriges", "coups_de_pouce", "_harvest"}
ALLOWED_SUFFIXES = {"corrige", "corrigé", "CO-", "CDP", "professeur"}


def is_allowed(path: Path) -> bool:
    if any(d in path.parts for d in ALLOWED_DIRS):
        return True
    return any(s in path.stem for s in ALLOWED_SUFFIXES)


def main() -> int:
    scan_dirs = [ROOT / "chapitres", ROOT / "build"]
    violations: list[str] = []
    checked = 0
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for path in sorted(scan_dir.rglob("*.tex")):
            if is_allowed(path):
                continue
            checked += 1
            content = path.read_text(encoding="utf-8", errors="replace")
            for pattern in FORBIDDEN:
                matches = pattern.findall(content)
                if matches:
                    rel = path.relative_to(ROOT)
                    violations.append(f"  {rel}: found '{matches[0]}'")

    if violations:
        print("ROUGE -- contenu corrige detecte dans des fichiers eleve :")
        for v in violations:
            print(v)
        return 1

    print(f"VERT -- {checked} fichiers verifies, aucune fuite de corrige.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
