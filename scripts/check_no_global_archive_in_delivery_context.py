#!/usr/bin/env python3
"""Reject forbidden global repository archives in the delivery context."""

from __future__ import annotations

from dataclasses import dataclass, field
import sys
from pathlib import Path

from scripts.check_uploaded_archive_policy import archive_entries, path_has_segment

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_GLOBAL_NAMES = {
    "nsi-enseignement.tar",
    "nsi-enseignement.tar.gz",
    "NSI.tar",
    "NSI.tar.gz",
}
ARCHIVE_SUFFIXES = (".tar", ".tar.gz", ".tgz", ".zip")


@dataclass
class NoGlobalArchiveResult:
    errors: list[str] = field(default_factory=list)


def is_archive_name(name: str) -> bool:
    return name.endswith(ARCHIVE_SUFFIXES)


def delivery_context_candidates(root: Path = ROOT) -> list[Path]:
    candidates: list[Path] = []
    for directory in [root, root.parent]:
        if not directory.exists():
            continue
        for path in directory.iterdir():
            if path.is_file() and path.name in FORBIDDEN_GLOBAL_NAMES:
                candidates.append(path)
    return sorted(candidates, key=lambda item: item.as_posix())


def inspect_global_archive(path: Path) -> list[str]:
    entries = archive_entries(path)
    if entries is None:
        return [f"{path.name}: archive globale illisible"]
    errors: list[str] = []
    if any(path_has_segment(entry, ".git") for entry in entries):
        errors.append(f"{path.name}: archive globale contient .git/")
    if any(path_has_segment(entry, "dist") for entry in entries):
        errors.append(f"{path.name}: archive globale contient dist/")
    if any(entry.replace("\\", "/").endswith("dist/git_bundle.bundle") for entry in entries):
        errors.append(f"{path.name}: archive globale contient dist/git_bundle.bundle")
    for entry in entries:
        entry_name = Path(entry.replace("\\", "/")).name
        if is_archive_name(entry_name):
            errors.append(f"{path.name}: archive imbriquée interdite -> {entry}")
    return errors


def analyze_no_global_archive_in_delivery_context(root: Path = ROOT) -> NoGlobalArchiveResult:
    result = NoGlobalArchiveResult()
    for candidate in delivery_context_candidates(root):
        result.errors.extend(inspect_global_archive(candidate))
    return result


def main() -> int:
    result = analyze_no_global_archive_in_delivery_context()
    if result.errors:
        print("check_no_global_archive_in_delivery_context: KO")
        for error in result.errors[:120]:
            print(f"- {error}")
        return 1
    print("check_no_global_archive_in_delivery_context: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
