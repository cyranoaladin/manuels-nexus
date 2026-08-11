#!/usr/bin/env python3
"""Check required files and directories for the two pilot sequences."""

from __future__ import annotations

from typing import List

from scripts._qa_common import ROOT, TARGET_SEQUENCES, REQUIRED_SEQUENCE_FILES, print_result


def main() -> None:
    errors: List[str] = []
    for level, seq in TARGET_SEQUENCES.items():
        if not seq.exists():
            errors.append(f"{level}: dossier pilote absent -> {seq.relative_to(ROOT)}")
            continue
        for name in sorted(REQUIRED_SEQUENCE_FILES):
            path = seq / name
            if not path.exists():
                errors.append(f"{seq.relative_to(ROOT)}: fichier requis absent -> {name}")
        if not list((seq / "python").glob("*.py")):
            errors.append(f"{seq.relative_to(ROOT)}: aucun fichier Python dans python/")
        if not list((seq / "tests").glob("test*.py")):
            errors.append(f"{seq.relative_to(ROOT)}: aucun test dans tests/")

    print_result("check_sequence_completeness", errors)


if __name__ == "__main__":
    main()
