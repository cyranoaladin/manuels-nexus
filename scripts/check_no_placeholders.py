#!/usr/bin/env python3
"""Compatibility wrapper for document and code placeholder checks."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CHECKS = [
    "scripts/check_no_placeholders_docs.py",
    "scripts/check_no_placeholders_code.py",
]


def main() -> None:
    for script in CHECKS:
        result = subprocess.run([sys.executable, script], cwd=ROOT)
        if result.returncode != 0:
            raise SystemExit(result.returncode)
    print("check_no_placeholders: PASS")


if __name__ == "__main__":
    main()
