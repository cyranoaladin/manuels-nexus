#!/usr/bin/env python3
"""Gate: student artefacts (*_eleve.tex) must NOT contain answers or corrections.

Scans all *_eleve.tex files for forbidden patterns:
  - "Réponse attendue"
  - "Corrigé"
  - "\\section*{Corrigé}"

Exit 0 if clean, exit 1 with details if leaks are found.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LATEX_DIR = REPO / "latex"

FORBIDDEN = [
    re.compile(r"Réponse attendue", re.IGNORECASE),
    re.compile(r"Corrigé", re.IGNORECASE),
]


def main() -> int:
    eleve_files = sorted(LATEX_DIR.rglob("*_eleve.tex"))
    if not eleve_files:
        print("WARN: no *_eleve.tex files found — gate vacuously green.")
        return 0

    violations: list[str] = []
    for path in eleve_files:
        content = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN:
            matches = pattern.findall(content)
            if matches:
                rel = path.relative_to(REPO)
                violations.append(f"  {rel}: found '{matches[0]}'")

    if violations:
        print("ROUGE — student artefacts contain forbidden answer/correction patterns:")
        for v in violations:
            print(v)
        return 1

    print(f"VERT — {len(eleve_files)} student artefact(s) checked, no answers or corrections found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
