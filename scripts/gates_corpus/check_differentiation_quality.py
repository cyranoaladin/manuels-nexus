#!/usr/bin/env python3
"""Gate : verifie la qualite de la differenciation par parcours.

Adapte depuis corpus_nsi check_differentiation_quality.py.
Verifie que les exercices couvrent les 3 parcours et le ratio 40/40/20.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PARCOURS_RE = re.compile(r'"parcours"\s*:\s*(\d)')


def main() -> int:
    chap_arg = None
    for i, a in enumerate(sys.argv):
        if a == "--chap" and i + 1 < len(sys.argv):
            chap_arg = sys.argv[i + 1]

    chap_dirs = []
    if chap_arg:
        d = ROOT / "chapitres" / chap_arg
        if d.exists():
            chap_dirs = [d]
    else:
        chap_dirs = sorted(d for d in (ROOT / "chapitres").iterdir() if d.is_dir())

    errors: list[str] = []
    for chap_dir in chap_dirs:
        ex_dir = chap_dir / "exercices"
        if not ex_dir.exists():
            continue

        counts = {1: 0, 2: 0, 3: 0}
        for f in sorted(ex_dir.glob("*.tex")):
            first_line = f.read_text(encoding="utf-8", errors="replace").split("\n")[0]
            m = PARCOURS_RE.search(first_line)
            if m:
                p = int(m.group(1))
                if p in counts:
                    counts[p] += 1

        total = sum(counts.values())
        chap_name = chap_dir.name
        if total == 0:
            errors.append(f"{chap_name}: aucun exercice avec parcours")
            continue

        for p in (1, 2, 3):
            if counts[p] == 0:
                errors.append(f"{chap_name}: parcours {p} sans exercice")

        ratios = {p: counts[p] / total * 100 for p in (1, 2, 3)}
        if total >= 10:
            if ratios[1] < 25:
                errors.append(f"{chap_name}: parcours 1 sous-represente ({ratios[1]:.0f}%, cible ~40%)")
            if ratios[2] < 25:
                errors.append(f"{chap_name}: parcours 2 sous-represente ({ratios[2]:.0f}%, cible ~40%)")

        print(f"{chap_name}: {total} exercices -- "
              f"P1={counts[1]} ({ratios[1]:.0f}%) "
              f"P2={counts[2]} ({ratios[2]:.0f}%) "
              f"P3={counts[3]} ({ratios[3]:.0f}%)")

    if errors:
        print(f"\nWARN -- {len(errors)} problemes de differenciation :")
        for e in errors:
            print(f"  {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
