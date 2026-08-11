#!/usr/bin/env python3
"""Check that packaging artifacts match Git or source-clean mode."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import tarfile

from scripts._qa_common import ROOT


@dataclass
class PackagingModeResult:
    errors: list[str] = field(default_factory=list)
    mode: str = ""


def archive_contains_git(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        with tarfile.open(path, "r:gz") as archive:
            return any("/.git/" in name or name.endswith("/.git") for name in archive.getnames())
    except tarfile.TarError:
        return True


def analyze_packaging_mode(root: Path = ROOT) -> PackagingModeResult:
    result = PackagingModeResult()
    dist = root / "dist"
    source_tar = dist / "source_clean.tar.gz"
    bundle = dist / "git_bundle.bundle"
    has_git = (root / ".git").exists()
    result.mode = "git" if has_git else "source_clean"
    if not source_tar.exists():
        result.errors.append("dist/source_clean.tar.gz absent après packaging")
    elif archive_contains_git(source_tar):
        result.errors.append("dist/source_clean.tar.gz contient .git/")
    if has_git and not bundle.exists():
        result.errors.append("mode dépôt Git complet: dist/git_bundle.bundle attendu")
    if not has_git and bundle.exists():
        result.errors.append("mode source propre: dist/git_bundle.bundle ne doit pas être produit")
    return result


def main() -> int:
    result = analyze_packaging_mode()
    if result.errors:
        print(f"check_packaging_mode: KO ({result.mode})")
        for error in result.errors:
            print(f"- {error}")
        return 1
    print(f"check_packaging_mode: PASS ({result.mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
