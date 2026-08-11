#!/usr/bin/env python3
"""Check that bank folders do not contain manual resource copies."""

from __future__ import annotations

from typing import List

from scripts._qa_common import ROOT, print_result

ALLOWED_BANK_FILES = {"index.md", ".gitkeep"}
BANK_ROOTS = [ROOT / "premiere" / "banques", ROOT / "terminale" / "banques"]


def main() -> None:
    errors: List[str] = []
    if not (ROOT / "bank_strategy.md").exists():
        errors.append("bank_strategy.md absent")

    for bank_root in BANK_ROOTS:
        if not bank_root.exists():
            errors.append(f"{bank_root.relative_to(ROOT)} absent")
            continue
        for path in sorted(bank_root.rglob("*")):
            if path.is_dir():
                continue
            if path.name not in ALLOWED_BANK_FILES:
                errors.append(f"{path.relative_to(ROOT)}: copie manuelle interdite dans les banques")

    print_result("check_bank_strategy", errors)


if __name__ == "__main__":
    main()
