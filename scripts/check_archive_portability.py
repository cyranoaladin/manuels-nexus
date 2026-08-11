#!/usr/bin/env python3
"""Check source_clean.tar.gz portability and absence of forbidden artifacts."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from scripts.archive_security import safe_extract_tar

ARCHIVE = ROOT / 'dist/source_clean.tar.gz'
BUNDLE = ROOT / 'dist/git_bundle.bundle'
FORBIDDEN_PARTS = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.venv'}
FORBIDDEN_SUFFIXES = {'.pyc', '.pyo', '.aux', '.log', '.toc', '.out', '.fls'}
REQUIRED_FILES = ['03_progressions/seances_premiere.md', '03_progressions/seances_terminale.md', '03_progressions/monthly_load_premiere.md', '03_progressions/monthly_load_terminale.md']
CHECKS = ['scripts/check_session_duration_consistency.py', 'scripts/check_session_monthly_total.py', 'scripts/check_session_project_hours.py']


@dataclass
class ArchivePortabilityResult:
    errors: list[str] = field(default_factory=list)
    mode: str = ""

def forbidden(rel: Path) -> bool:
    if any(part in FORBIDDEN_PARTS for part in rel.parts):
        return True
    if rel.suffix in FORBIDDEN_SUFFIXES or rel.name == '.DS_Store':
        return True
    if rel.name.endswith('.synctex.gz') or rel.name.endswith('.fdb_latexmk'):
        return True
    return False

def analyze_archive_portability(root: Path = ROOT) -> ArchivePortabilityResult:
    archive = root / 'dist/source_clean.tar.gz'
    bundle = root / 'dist/git_bundle.bundle'
    has_git = (root / '.git').exists()
    result = ArchivePortabilityResult(mode='git' if has_git else 'source_clean')
    errors = result.errors
    if not archive.exists():
        errors.append('dist/source_clean.tar.gz absent')
    if has_git and not bundle.exists():
        errors.append('dist/git_bundle.bundle absent')
    if errors:
        return result
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        try:
            safe_extract_tar(archive, tmp_path)
        except Exception as exc:
            errors.append(f'archive extraction failed: {exc}')
            return result
        repo = tmp_path / 'nsi-enseignement'
        for path in repo.rglob('*'):
            rel_path = path.relative_to(repo)
            if forbidden(rel_path):
                errors.append(f'forbidden artifact in archive: {rel_path}')
        for required in REQUIRED_FILES:
            path = repo / required
            if not path.exists() or not path.read_text(encoding='utf-8', errors='replace').strip():
                errors.append(f'required progression file unreadable: {required}')
        env = {'PYTHONDONTWRITEBYTECODE': '1'}
        for script in CHECKS:
            run = subprocess.run([sys.executable, script], cwd=repo, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            if run.returncode != 0:
                errors.append(f'{script} failed in extracted archive: {run.stdout.strip()}')
    return result


def main() -> int:
    result = analyze_archive_portability()
    errors = result.errors
    if errors:
        print(f'check_archive_portability: KO ({result.mode})')
        for error in errors:
            print(f'- {error}')
        return 1
    print(f'check_archive_portability: PASS ({result.mode})')
    return 0

if __name__ == '__main__':
    sys.exit(main())
