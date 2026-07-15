#!/usr/bin/env python3
"""Gate : aucun marqueur placeholder dans les fichiers de production.

Adapte depuis corpus_nsi check_no_placeholders_docs.py.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TEXT_SUFFIXES = {".md", ".tex", ".json", ".yml", ".yaml", ".csv", ".txt"}
PLACEHOLDER_RE = re.compile(
    r"(?<!`)(TO\s*DO|TBD|A\s+COMPLETER|À\s+COMPLETER|X\s*X\s*X|FIX\s*ME|A\s+FAIRE|À\s+FAIRE)(?!`)",
    re.IGNORECASE,
)
SKIP_DIRS = {".git", ".venv", "__pycache__", "_harvest", "raw", "corpus", "build", "docs", "prompts"}


def main() -> int:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_dir() or path.suffix not in TEXT_SUFFIXES:
            continue
        if SKIP_DIRS & set(path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        matches = PLACEHOLDER_RE.findall(text)
        if matches:
            errors.append(f"  {path.relative_to(ROOT)}: '{matches[0]}'")

    if errors:
        print(f"WARN -- {len(errors)} fichiers contiennent des placeholders :")
        for e in errors[:20]:
            print(e)
        return 1

    print("VERT -- aucun placeholder detecte.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
