#!/usr/bin/env python3
"""Check delivery policy: only source_clean.tar.gz is a pedagogical archive."""
from __future__ import annotations

import sys
import tarfile
import zipfile
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "delivery_policy.md"
ALLOWED = {
    ROOT / "dist/source_clean.tar.gz",
    ROOT / "dist/git_bundle.bundle",
    ROOT / "dist/nsi-enseignement_source_clean.zip",
}
DELIVERY_ARCHIVE = ROOT / "dist/source_clean.tar.gz"
FORBIDDEN_NAMES = {
    "nsi-enseignement.tar",
    "nsi-enseignement.tar.gz",
    "nsi-enseignement.zip",
    "NSI.tar",
    "NSI.tar.gz",
    "nsi.tar",
    "nsi.tar.gz",
    "archive.tar",
    "archive.tar.gz",
    "archive.zip",
}
ARCHIVE_SUFFIXES = (".tar", ".tar.gz", ".tgz", ".zip")
CACHE_MARKERS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
}


def is_archive(path: Path) -> bool:
    return path.name.endswith(ARCHIVE_SUFFIXES)


def archive_entries(path: Path) -> list[str] | None:
    try:
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as archive:
                return archive.namelist()
        if path.name.endswith(".tar") or path.name.endswith(".tar.gz") or path.name.endswith(".tgz"):
            with tarfile.open(path) as archive:
                return [member.name for member in archive.getmembers()]
    except Exception:
        return None
    return []


def path_has_segment(entry: str, segment: str) -> bool:
    parts = [part for part in entry.replace("\\", "/").split("/") if part and part != "."]
    return segment in parts


def archive_content_errors(path: Path) -> list[str]:
    entries = archive_entries(path)
    if entries is None:
        return [f"archive illisible ou non fiable: {path.name}"]
    errors: list[str] = []
    if any(path_has_segment(entry, ".git") for entry in entries):
        errors.append(f"archive contient .git/: {path.name}")
    if any(entry.endswith(".pyc") for entry in entries):
        errors.append(f"archive contient .pyc: {path.name}")
    for marker in sorted(CACHE_MARKERS):
        if any(path_has_segment(entry, marker) for entry in entries):
            errors.append(f"archive contient {marker}/: {path.name}")
    if path.resolve() != DELIVERY_ARCHIVE.resolve() and any(path_has_segment(entry, "dist") for entry in entries):
        errors.append(f"archive globale contient dist/: {path.name}")
    return errors


def collect_archive_candidates(root: Path, scan_parent: bool = True) -> set[Path]:
    scan_dirs = [root]
    if scan_parent:
        scan_dirs.append(root.parent)
    candidates: set[Path] = set()
    for directory in scan_dirs:
        if directory.exists():
            candidates.update(path for path in directory.iterdir() if path.is_file() and is_archive(path))
    return candidates


def normalize_delivered(root: Path, delivered_archive: Path | str | None) -> Path | None:
    if delivered_archive is None:
        value = os.environ.get("DELIVERED_ARCHIVE", "").strip()
        if not value:
            return None
        delivered_archive = value
    path = Path(delivered_archive)
    return path if path.is_absolute() else root / path


def analyze_uploaded_archive_policy(
    root: Path = ROOT,
    delivered_archive: Path | str | None = None,
    scan_parent: bool = True,
    require_delivery_files: bool = False,
) -> list[str]:
    errors: list[str] = []
    policy = root / "delivery_policy.md"
    delivery_archive = root / "dist/source_clean.tar.gz"
    allowed = {
        delivery_archive.resolve(),
        (root / "dist/git_bundle.bundle").resolve(),
        (root / "dist/nsi-enseignement_source_clean.zip").resolve(),
    }

    if require_delivery_files:
        if not policy.exists():
            errors.append("delivery_policy.md absent")
        for required in [delivery_archive, root / "dist/git_bundle.bundle"]:
            if not required.exists():
                errors.append(f"required delivery artifact absent: {required.relative_to(root)}")

    delivered = normalize_delivered(root, delivered_archive)
    candidates = collect_archive_candidates(root, scan_parent=scan_parent)
    if delivered is not None:
        candidates.add(delivered)
        if delivered.resolve() != delivery_archive.resolve():
            errors.append(f"DELIVERED_ARCHIVE doit être dist/source_clean.tar.gz, reçu: {delivered}")
        if not delivered.exists():
            errors.append(f"DELIVERED_ARCHIVE absent: {delivered}")

    if delivery_archive.exists():
        candidates.add(delivery_archive)

    for path in sorted(candidates, key=lambda item: item.as_posix()):
        resolved = path.resolve()
        if path.name in FORBIDDEN_NAMES:
            errors.append(f"archive globale interdite: {path.name}")
        if resolved not in allowed:
            errors.append(f"archive non autorisée dans la livraison: {path.name}")
        if path.exists() and is_archive(path):
            errors.extend(archive_content_errors(path))
    return errors


def archive_contains_git(path: Path) -> bool:
    entries = archive_entries(path)
    if entries is None:
        return True
    return any(path_has_segment(entry, ".git") for entry in entries)


def main() -> int:
    errors = analyze_uploaded_archive_policy(ROOT, require_delivery_files=True)
    if errors:
        print("check_uploaded_archive_policy: KO")
        for error in errors:
            print(f"- {error}")
        return 1
    print("check_uploaded_archive_policy: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
