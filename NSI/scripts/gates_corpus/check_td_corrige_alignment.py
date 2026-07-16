#!/usr/bin/env python3
"""Gate : chaque exercice a un corrige correspondant.

Adapte depuis corpus_nsi check_td_corrige_alignment.py.
Compare les IDs d'exercices dans exercices/ aux IDs dans corriges/.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

EX_ID_RE = re.compile(r"\\begin\{exercice\}\{([^}]+)\}")
CO_ID_RE = re.compile(r"\\begin\{corrige\}\{([^}]+)\}")


def main() -> int:
    chap_arg = None
    strict = "--strict" in sys.argv
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

    total_ex, total_co, missing_all = 0, 0, []
    for chap_dir in chap_dirs:
        ex_dir = chap_dir / "exercices"
        co_dir = chap_dir / "corriges"
        if not ex_dir.exists():
            continue

        ex_ids = set()
        for f in sorted(ex_dir.glob("*.tex")):
            for m in EX_ID_RE.finditer(f.read_text(encoding="utf-8", errors="replace")):
                ex_ids.add(m.group(1))

        co_ids = set()
        if co_dir.exists():
            for f in sorted(co_dir.glob("*.tex")):
                for m in CO_ID_RE.finditer(f.read_text(encoding="utf-8", errors="replace")):
                    co_ids.add(m.group(1))

        missing = sorted(ex_ids - co_ids)
        total_ex += len(ex_ids)
        total_co += len(co_ids)
        if missing:
            chap_name = chap_dir.name
            missing_all.extend(f"  {chap_name}: corrige manquant pour {eid}" for eid in missing)

    if missing_all:
        print(f"WARN -- {len(missing_all)} corriges manquants sur {total_ex} exercices :")
        for m in missing_all[:20]:
            print(m)
        if len(missing_all) > 20:
            print(f"  ... et {len(missing_all) - 20} autres")
    else:
        print(f"VERT -- {total_co}/{total_ex} exercices ont un corrige.")

    if strict and missing_all:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
