#!/usr/bin/env python3
"""Génère l’INDEX.md en excluant les artefacts de build et répertoires techniques."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'INDEX.md'

EXCLUDED_DIRS = {
    '.git',
    '.venv',
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache',
    '01_build_reports',
    'build',
    'dist',
}
EXCLUDED_SUFFIXES = {
    '.pyc',
    '.aux',
    '.log',
    '.out',
    '.toc',
    '.synctex.gz',
    '.fdb_latexmk',
    '.fls',
    '.bbl',
    '.blg',
    '.tmp',
}


def should_include(path: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    if path.name.endswith('~') or path.name.startswith('.'):
        return False
    if 'quality_audit_s01.md' in path.name:
        return False
    return True


def list_files_by_level(level: str) -> list[Path]:
    root = ROOT / level / 'sequences'
    if not root.exists():
        return []
    docs = []
    for p in sorted(root.rglob('*')):
        if p.is_file() and should_include(p) and p.suffix in {'.md', '.json', '.py', '.tex', '.yml', '.yaml'}:
            if 'tests' in p.parts:
                continue
            docs.append(p.relative_to(ROOT))
    return docs


def main() -> None:
    lines = ['# Index pédagogique NSI', '']
    for level in ['premiere', 'terminale']:
        lines.append(f'## {level.capitalize()}')
        files = list_files_by_level(level)
        if not files:
            lines.append('- aucune séquence pour le moment')
            lines.append('')
            continue

        grouped: dict[str, list[Path]] = {}
        for f in files:
            seq = f.parts[1] if len(f.parts) > 1 else 'root'
            grouped.setdefault(seq, []).append(f)

        for seq, docs in sorted(grouped.items()):
            lines.append(f'- {seq}')
            for doc in docs:
                lines.append(f'  - `{doc}`')
        lines.append('')

    INDEX.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('generate_index: done ->', INDEX)


if __name__ == '__main__':
    main()
