#!/usr/bin/env python3
"""Reject placeholder markers in documentation and structured resources."""

from __future__ import annotations

from typing import List
import re

from scripts._qa_common import ROOT, print_result

TEXT_SUFFIXES = {".md", ".tex", ".json", ".yml", ".yaml", ".csv", ".txt"}
PLACEHOLDER_RE = re.compile(
    r"(?<!`)(TO[ \t]*DO|TBD|A[ \t]+COMPLETER|À[ \t]+COMPLETER|X[ \t]*X[ \t]*X|FIX[ \t]*ME|A[ \t]+FAIRE|À[ \t]+FAIRE)(?!`)",
    re.IGNORECASE,
)


def main() -> None:
    errors: List[str] = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_dir() or path.suffix not in TEXT_SUFFIXES:
            continue
        if {".git", ".venv", "__pycache__", "scrapping_NSI", "Documents_DRIVE", "nsi-enseignement"} & set(path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if PLACEHOLDER_RE.search(text):
            errors.append(str(path.relative_to(ROOT)))

    print_result("check_no_placeholders_docs", errors)


if __name__ == "__main__":
    main()
