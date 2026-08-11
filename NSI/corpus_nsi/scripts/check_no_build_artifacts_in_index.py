#!/usr/bin/env python3
"""Reject uncontrolled build artifacts while allowing required delivery archives."""

from __future__ import annotations

import sys
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_DIST = {
    Path('dist/source_clean.tar.gz'),
    Path('dist/git_bundle.bundle'),
    Path('dist/nsi-enseignement_source_clean.zip'),
}
REQUIRED_DIST = {
    Path('dist/source_clean.tar.gz'),
    Path('dist/git_bundle.bundle'),
}
FORBIDDEN_DIRS = {
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache',
    '.venv',
    'build',
}
FORBIDDEN_SUFFIXES = {
    '.pyc',
    '.pyo',
    '.aux',
    '.log',
    '.toc',
    '.out',
    '.fls',
}
FORBIDDEN_NAMES = {'.DS_Store'}


def is_allowed_validation_log(rel: Path) -> bool:
    return (
        len(rel.parts) >= 3
        and rel.parts[0] == "reports"
        and rel.parts[1].startswith("lot")
        and rel.suffix == ".log"
    )


def is_forbidden(path: Path, root: Path = ROOT) -> bool:
    rel = path.relative_to(root)
    if rel in ALLOWED_DIST:
        return False
    if is_allowed_validation_log(rel):
        return False
    if rel == Path('dist'):
        return False
    if rel.parts and rel.parts[0] == 'dist':
        return True
    if any(part in FORBIDDEN_DIRS for part in rel.parts):
        return True
    if path.name in FORBIDDEN_NAMES:
        return True
    if path.suffix in FORBIDDEN_SUFFIXES:
        return True
    if path.name.endswith('.synctex.gz') or path.name.endswith('.fdb_latexmk'):
        return True
    return False


def git_tracked_paths(root: Path = ROOT) -> list[Path] | None:
    if not (root / ".git").exists():
        return None
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return None
    return [root / raw.decode("utf-8") for raw in result.stdout.split(b"\0") if raw]


def candidate_paths(root: Path = ROOT) -> list[Path]:
    tracked = git_tracked_paths(root)
    if tracked is not None:
        paths: list[Path] = []
        seen: set[Path] = set()
        for path in tracked:
            if not path.exists():
                continue
            for candidate in [path, *path.parents]:
                if candidate == root:
                    break
                if root not in candidate.parents:
                    continue
                if candidate not in seen:
                    paths.append(candidate)
                    seen.add(candidate)
        dist = root / "dist"
        if dist.exists():
            paths.extend(path for path in dist.rglob("*") if path.exists())
        return paths
    return [path for path in root.rglob("*") if path.exists()]


def find_artifacts(root: Path = ROOT, require_archives: bool = True) -> list[Path]:
    artifacts: list[Path] = []
    for path in candidate_paths(root):
        if path == root / '.git':
            continue
        if '.git' in path.relative_to(root).parts:
            continue
        if path.exists() and is_forbidden(path, root):
            artifacts.append(path)
    if require_archives:
        artifacts.extend(root / item for item in REQUIRED_DIST if not (root / item).exists())
    return artifacts


def main() -> int:
    errors: list[str] = []
    require_archives = (ROOT / ".git").exists()
    artifacts = find_artifacts(ROOT, require_archives=require_archives)
    for path in artifacts:
        if path.exists():
            errors.append(f"{path.relative_to(ROOT)}: artefact interdit")
    if require_archives:
        missing = [str(item) for item in REQUIRED_DIST if not (ROOT / item).exists()]
        if missing:
            errors.append('archives de livraison absentes: ' + ', '.join(sorted(missing)))
    if errors:
        print('check_no_build_artifacts_in_index: KO')
        for error in errors:
            print(f'- {error}')
        return 1
    print('check_no_build_artifacts_in_index: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
