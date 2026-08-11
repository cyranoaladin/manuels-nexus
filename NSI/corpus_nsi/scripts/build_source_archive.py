#!/usr/bin/env python3
"""Build portable delivery artifacts without packaging .git in source archive."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
SOURCE_TAR = DIST / 'source_clean.tar.gz'
BUNDLE = DIST / 'git_bundle.bundle'

# Source de vérité unique : réutilise CACHE_DIRS de cleanup_python_artifacts
# pour garantir que toute entrée de cache nettoyée à l'audit est aussi exclue
# de l'archive de livraison.
from scripts.cleanup_python_artifacts import CACHE_DIRS

EXCLUDED_PARTS = {'.git', '.venv', 'dist', 'build', '01_build_reports'} | CACHE_DIRS
EXCLUDED_SUFFIXES = {'.pyc', '.pyo', '.aux', '.log', '.toc', '.out', '.fls'}
EXCLUDED_NAMES = {'.DS_Store'}

def excluded(rel: Path) -> bool:
    if any(part in EXCLUDED_PARTS for part in rel.parts):
        return True
    if rel.name in EXCLUDED_NAMES or rel.suffix in EXCLUDED_SUFFIXES:
        return True
    if rel.name.startswith('.env') and rel.name != '.env.rag.example':
        return True
    if rel.name.endswith('.synctex.gz') or rel.name.endswith('.fdb_latexmk'):
        return True
    return False


def iter_source_paths(root: Path = ROOT) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode == 0:
        paths = [
            root / raw.decode("utf-8")
            for raw in result.stdout.split(b"\0")
            if raw
        ]
        return [path for path in paths if path.exists()]
    print(
        "build_source_archive: fallback sans git - périmètre rglob indicatif, "
        "à ne pas utiliser pour une release réelle sans revue",
        file=sys.stderr,
    )
    return sorted(path for path in root.rglob("*") if path.is_file())


def copy_tree(target: Path, root: Path = ROOT) -> None:
    root_target = target / 'nsi-enseignement'
    root_target.mkdir(parents=True)
    for path in iter_source_paths(root):
        rel = path.relative_to(root)
        if excluded(rel):
            continue
        dest = root_target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)


def has_git_metadata(root: Path = ROOT) -> bool:
    return (root / ".git").exists()


def build_source_tar(root: Path = ROOT, target: Path = SOURCE_TAR) -> Path:
    target.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        copy_tree(tmp_path, root=root)
        if target.exists():
            target.unlink()
        with tarfile.open(target, 'w:gz') as tar:
            tar.add(tmp_path / 'nsi-enseignement', arcname='nsi-enseignement')
    return target


def build_git_bundle() -> int:
    result = subprocess.run(['git', 'bundle', 'create', str(BUNDLE), '--all'], cwd=ROOT)
    return result.returncode


def main() -> int:
    build_source_tar(ROOT, SOURCE_TAR)
    print(f'build_source_archive: wrote {SOURCE_TAR.relative_to(ROOT)}')
    if not has_git_metadata(ROOT):
        if BUNDLE.exists():
            BUNDLE.unlink()
        print('build_source_archive: git bundle non généré car archive source sans .git')
        return 0
    bundle_status = build_git_bundle()
    if bundle_status != 0:
        return bundle_status
    print(f'build_source_archive: wrote {BUNDLE.relative_to(ROOT)}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
