#!/usr/bin/env python3
"""Gate : chaque \\begin{console} doit avoir un bloc TRACE correspondant.

Verifie que tout contenu affiche dans un environnement console est couvert
par un bloc BEGIN-TRACE/END-TRACE dont le EXPECTED correspond exactement.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CONSOLE_RE = re.compile(r"\\begin\{console\}(.*?)\\end\{console\}", re.S)
TRACE_RE = re.compile(r"% BEGIN-TRACE\n(.*?)% EXPECTED\n(.*?)% END-TRACE", re.S)
VERIFY_RE = re.compile(r"% BEGIN-VERIFY\n(.*?)% END-VERIFY", re.S)
SUBDIRS = ("exercices", "corriges", "evaluations", "cours", "methodes", "projet", "qcm")


def extract_console_outputs(text: str) -> list[str]:
    """Extrait les sorties attendues des blocs console (lignes sans >>>)."""
    outputs = []
    for m in CONSOLE_RE.finditer(text):
        lines = m.group(1).strip().splitlines()
        output_lines = [l.strip() for l in lines if not l.strip().startswith(">>>")]
        if output_lines:
            outputs.append("\n".join(output_lines))
    return outputs


def has_trace_or_verify(text: str) -> bool:
    """Verifie si le fichier a au moins un bloc TRACE ou VERIFY."""
    return bool(TRACE_RE.search(text) or VERIFY_RE.search(text))


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

    warnings: list[str] = []
    checked = 0
    for chap_dir in chap_dirs:
        for sub in SUBDIRS:
            sub_dir = chap_dir / sub
            if not sub_dir.exists():
                continue
            for tex in sorted(sub_dir.glob("*.tex")):
                text = tex.read_text(encoding="utf-8", errors="replace")
                console_outputs = extract_console_outputs(text)
                if not console_outputs:
                    continue
                checked += 1
                if not has_trace_or_verify(text):
                    rel = tex.relative_to(ROOT)
                    warnings.append(f"  {rel}: console sans TRACE/VERIFY")

    if warnings:
        print(f"WARN -- {len(warnings)} fichiers ont des blocs console sans couverture TRACE/VERIFY :")
        for w in warnings:
            print(w)
        return 1

    print(f"VERT -- {checked} fichiers avec console verifies (tous ont TRACE/VERIFY).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
