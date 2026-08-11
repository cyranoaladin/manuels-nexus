#!/usr/bin/env python3
"""Validate the versioned doctrine for the nested NSI repositories."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import subprocess
import tarfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PARENT_ROOT = ROOT.parent

PARENT_NESTED_REPO = "nsi-enseignement"
EXPECTED_REMOTE_FRAGMENT = "cyranoaladin/NSI"
MIRROR_PATHS = [
    "scrapping_NSI/ressources_nsi_centralisees",
    "scrapping_NSI/ressources_nsi_extraites",
    "scrapping_NSI/ressources_nsi_extraites_v2",
    "scrapping_NSI/sqlite_data",
]
DELIVERABLE_ARCHIVES = [
    Path("dist/source_clean.tar.gz"),
    Path("dist/nsi-enseignement_source_clean.zip"),
]


@dataclass
class TopologyResult:
    errors: list[str] = field(default_factory=list)


def _git_lines(root: Path, args: list[str]) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return []
    return [line for line in completed.stdout.splitlines() if line]


def _has_git_repo(root: Path) -> bool:
    return bool(_git_lines(root, ["rev-parse", "--show-toplevel"]))


def _is_tracked(root: Path, path: str) -> bool:
    return bool(_git_lines(root, ["ls-files", "--", path]))


def _is_expected_canonical_repo(repo_root: Path) -> bool:
    if repo_root.name == PARENT_NESTED_REPO:
        return True
    return any(EXPECTED_REMOTE_FRAGMENT in line for line in _git_lines(repo_root, ["remote", "-v"]))


def _versioned_policy_text(repo_root: Path, parent_root: Path) -> str:
    texts: list[str] = []
    for path in (
        repo_root / "docs" / "repo_topology.md",
        repo_root / "docs" / "local_excludes_required.md",
        parent_root / ".gitignore",
    ):
        if path.exists():
            texts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(texts)


def _has_versioned_policy(repo_root: Path, parent_root: Path, path: str) -> bool:
    text = _versioned_policy_text(repo_root, parent_root)
    return path in text or f"{path}/" in text


def _archive_entries(path: Path) -> list[str]:
    if not path.exists():
        return []
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            return archive.namelist()
    if path.name.endswith((".tar", ".tar.gz", ".tgz")):
        with tarfile.open(path) as archive:
            return archive.getnames()
    return []


def _path_has_prefix(entry: str, prefix: str) -> bool:
    normalized = entry.replace("\\", "/").strip("/")
    normalized_prefix = prefix.replace("\\", "/").strip("/")
    return normalized == normalized_prefix or normalized.startswith(f"{normalized_prefix}/")


def _check_archives(repo_root: Path, errors: list[str]) -> None:
    forbidden_prefixes = [
        "nsi-enseignement/.git",
        *[f"nsi-enseignement/{path}" for path in MIRROR_PATHS],
    ]
    for relative in DELIVERABLE_ARCHIVES:
        archive = repo_root / relative
        try:
            entries = _archive_entries(archive)
        except (tarfile.TarError, zipfile.BadZipFile, OSError) as exc:
            errors.append(f"{relative}: archive livrable illisible: {exc}")
            continue
        for forbidden in forbidden_prefixes:
            if any(_path_has_prefix(entry, forbidden) for entry in entries):
                errors.append(f"{relative}: contient {forbidden}")


def analyze_topology(repo_root: Path = ROOT, parent_root: Path = PARENT_ROOT) -> TopologyResult:
    result = TopologyResult()
    errors = result.errors
    if not _is_expected_canonical_repo(repo_root):
        errors.append(f"dépôt canonique inattendu: {repo_root}")
    if not (repo_root / ".git").exists():
        errors.append("dépôt canonique sans .git local")

    if _has_git_repo(parent_root):
        if _is_tracked(parent_root, PARENT_NESTED_REPO):
            errors.append("nsi-enseignement/ est suivi par Git dans le dépôt parent")
        if not _has_versioned_policy(repo_root, parent_root, PARENT_NESTED_REPO):
            errors.append("nsi-enseignement/ absent de .gitignore ou d'une politique versionnée")
        for mirror in MIRROR_PATHS:
            if _is_tracked(parent_root, mirror):
                errors.append(f"{mirror} est suivi par Git dans le dépôt parent")
            if not _has_versioned_policy(repo_root, parent_root, mirror):
                errors.append(f"{mirror} absent de .gitignore ou d'une politique versionnée")

    for mirror in MIRROR_PATHS:
        if _is_tracked(repo_root, mirror):
            errors.append(f"{mirror} est suivi par Git dans le dépôt canonique")

    _check_archives(repo_root, errors)
    return result


def main() -> int:
    result = analyze_topology()
    if result.errors:
        print("check_repo_topology: KO")
        for error in result.errors:
            print(f"- {error}")
        return 1
    print("check_repo_topology: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
