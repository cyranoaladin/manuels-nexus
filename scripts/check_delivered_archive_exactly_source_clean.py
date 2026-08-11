#!/usr/bin/env python3
"""Verify that the delivered pedagogical archive is exactly source_clean.tar.gz."""

from __future__ import annotations

import os
import sys
import tarfile
from pathlib import Path

from scripts.check_uploaded_archive_policy import archive_entries, path_has_segment

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_GLOBAL_NAMES = {
    "nsi-enseignement.tar",
    "nsi-enseignement.tar.gz",
    "nsi-enseignement.zip",
    "NSI.tar",
    "archive.tar",
}
ARCHIVE_SUFFIXES = (".tar", ".tar.gz", ".tgz", ".zip")


def is_archive(path: Path) -> bool:
    return path.name.endswith(ARCHIVE_SUFFIXES)


def delivered_path(root: Path, delivered_archive: Path | str | None = None) -> Path:
    value = str(delivered_archive or os.environ.get("DELIVERED_ARCHIVE", "dist/source_clean.tar.gz")).strip()
    path = Path(value)
    return path if path.is_absolute() else root / path


def source_clean_entries(path: Path) -> list[str]:
    try:
        with tarfile.open(path, "r:gz") as archive:
            return [member.name for member in archive.getmembers()]
    except Exception:
        return []


def archive_has_git(path: Path) -> bool:
    entries = archive_entries(path) or []
    return any(path_has_segment(entry, ".git") for entry in entries)


def analyze_delivered_archive_exactly_source_clean(
    root: Path = ROOT,
    delivered_archive: Path | str | None = None,
) -> list[str]:
    errors: list[str] = []
    expected = (root / "dist/source_clean.tar.gz").resolve()
    delivered = delivered_path(root, delivered_archive)
    if delivered.resolve() != expected:
        errors.append(f"livrable transmis interdit: {delivered}; attendu: dist/source_clean.tar.gz")
    if not delivered.exists():
        errors.append(f"livrable transmis absent: {delivered}")
        return errors

    entries = source_clean_entries(delivered)
    if not entries:
        errors.append("dist/source_clean.tar.gz illisible ou vide")
        return errors
    for entry in entries:
        if path_has_segment(entry, ".git"):
            errors.append(f"livrable contient .git/: {entry}")
        if entry.endswith("dist/git_bundle.bundle"):
            errors.append(f"livrable contient dist/git_bundle.bundle: {entry}")
        if Path(entry).name in FORBIDDEN_GLOBAL_NAMES:
            errors.append(f"livrable contient une archive globale interdite: {entry}")

    parent = root.parent
    for candidate in parent.iterdir() if parent.exists() else []:
        if not candidate.is_file() or not is_archive(candidate):
            continue
        if candidate.resolve() == expected:
            continue
        if candidate.name in FORBIDDEN_GLOBAL_NAMES and archive_has_git(candidate):
            errors.append(f"archive parent interdite contenant .git/: {candidate.name}")
    return errors


def main() -> int:
    errors = analyze_delivered_archive_exactly_source_clean()
    if errors:
        print("check_delivered_archive_exactly_source_clean: KO")
        for error in errors[:120]:
            print(f"- {error}")
        return 1
    print("check_delivered_archive_exactly_source_clean: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
