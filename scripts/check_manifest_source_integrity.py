#!/usr/bin/env python3
"""Check that manifest source=drive is only used for quarantined Drive resources."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.csv"
QUARANTINE_MANIFEST = ROOT / "drive_quarantine_manifest.csv"


def quarantined_paths() -> set[str]:
    paths: set[str] = set()
    if not QUARANTINE_MANIFEST.exists():
        return paths
    with QUARANTINE_MANIFEST.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            local = (row.get("local_copy") or "").strip()
            digest = (row.get("sha256") or "").strip()
            if local and len(digest) == 64:
                paths.add(local)
    return paths


def main() -> int:
    errors: list[str] = []
    allowed = quarantined_paths()
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            path = row.get("chemin", "")
            source = row.get("source", "")
            digest = row.get("hash", "")
            if source != "drive":
                continue
            if path.startswith("scripts/"):
                errors.append(f"local script classified as drive: {path}")
            if len(digest) != 64:
                errors.append(f"drive row without real hash: {path}")
            if path not in allowed and not path.startswith("drive_quarantine/"):
                errors.append(f"drive row not present in quarantine manifest: {path}")
    return fail_or_pass("check_manifest_source_integrity", errors)


def fail_or_pass(name: str, errors: list[str]) -> int:
    if errors:
        print(f"{name}: KO")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"{name}: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
