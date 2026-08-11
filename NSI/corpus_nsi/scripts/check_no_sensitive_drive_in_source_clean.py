#!/usr/bin/env python3
"""Check that source_clean.tar.gz or extracted source contains no sensitive Drive artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
import sys
import tarfile
from pathlib import Path

from scripts._qa_common import ROOT

SENSITIVE_NAMES = {"noteseleves.csv", "fichier_eleves.csv", "fichiereleves.csv", "rendus_eleves"}
SENSITIVE_SEGMENTS = {".venv", ".git", "__pycache__"}


@dataclass
class SensitiveArchiveResult:
    errors: list[str] = field(default_factory=list)


def archive_entries(path: Path) -> list[str]:
    with tarfile.open(path, "r:gz") as archive:
        return [member.name for member in archive.getmembers()]


def sensitive_entry(entry: str) -> bool:
    parts = [part for part in entry.replace("\\", "/").split("/") if part and part != "."]
    lowered = [part.lower() for part in parts]
    if any(part in SENSITIVE_SEGMENTS for part in lowered):
        return True
    if any(part.endswith(".pyc") for part in lowered):
        return True
    names = {part.replace("-", "_") for part in lowered}
    return bool(names & SENSITIVE_NAMES)


def analyze_no_sensitive_drive_in_source_clean(root: Path = ROOT) -> SensitiveArchiveResult:
    result = SensitiveArchiveResult()
    archive = root / "dist/source_clean.tar.gz"
    if archive.exists():
        try:
            entries = archive_entries(archive)
        except Exception as exc:
            result.errors.append(f"dist/source_clean.tar.gz illisible: {exc}")
            return result
        for entry in entries:
            if sensitive_entry(entry):
                result.errors.append(f"entrée sensible dans source_clean: {entry}")
        return result

    for path in root.rglob("*"):
        rel = path.relative_to(root).as_posix()
        if sensitive_entry(rel):
            result.errors.append(f"entrée sensible dans source extraite: {rel}")
    return result


def main() -> int:
    result = analyze_no_sensitive_drive_in_source_clean()
    if result.errors:
        print("check_no_sensitive_drive_in_source_clean: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print("check_no_sensitive_drive_in_source_clean: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
