#!/usr/bin/env python3
"""Check quarantined Drive exports for obvious private data before reuse."""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUARANTINE = ROOT / "drive_quarantine"
MANIFEST = ROOT / "drive_quarantine_manifest.csv"
TEXT_SUFFIXES = {".txt", ".md", ".tex", ".csv", ".json", ".py", ".yaml", ".yml"}
EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?:(?:\+|00)216\s*)?(?:[24579]\d)(?:[\s().-]?\d){6}\b|(?:(?:\+|00)33|0)\s*[1-9](?:[\s().-]?\d){8}\b")
SENSITIVE_NAME = re.compile(r"notes|eleves|élèves|rendus|copies", re.IGNORECASE)


def main() -> int:
    errors: list[str] = []
    if not QUARANTINE.exists():
        errors.append("drive_quarantine directory missing")
    if not MANIFEST.exists():
        errors.append("drive_quarantine_manifest.csv missing")
    else:
        with MANIFEST.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("decision") not in {"reuse", "refactor", "archive", "reject"}:
                    errors.append(f"invalid quarantine decision for {row.get('file_name')}")
                if SENSITIVE_NAME.search(row.get("file_name") or "") and row.get("decision") != "reject":
                    errors.append(f"sensitive-looking file not rejected: {row.get('file_name')}")
    if QUARANTINE.exists():
        for path in QUARANTINE.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                text = path.read_text(encoding="utf-8", errors="replace")
                if EMAIL.search(text):
                    errors.append(f"email-like data in {path.relative_to(ROOT)}")
                if PHONE.search(text):
                    errors.append(f"phone-like data in {path.relative_to(ROOT)}")
    if errors:
        print("check_drive_quarantine_privacy: KO")
        for error in errors:
            print(f"- {error}")
        return 1
    print("check_drive_quarantine_privacy: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
