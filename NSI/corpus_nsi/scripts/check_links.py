#!/usr/bin/env python3
"""Vérifie les liens Markdown internes dans les documents markdown."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r'\[[^\]]+\]\(([^)]+)\)')


def is_internal(target: str) -> bool:
    return bool(
        target
        and not target.startswith(('http://', 'https://', 'mailto:', 'ftp://', '#'))
        and '.png' not in target.lower()
        and '.jpg' not in target.lower()
    )


def check_file(path: Path) -> list[tuple[str, int, str]]:
    bad: list[tuple[str, int, str]] = []
    for i, line in enumerate(path.read_text(encoding='utf-8', errors='replace').splitlines(), start=1):
        for match in LINK_RE.finditer(line):
            target = match.group(1).strip()
            if is_internal(target):
                target_path = (path.parent / target).resolve()
                if not target_path.exists():
                    bad.append((str(path.relative_to(ROOT)), i, target))
    return bad


def main() -> None:
    issues = []
    skip_dirs = {'.git', '.venv', 'scrapping_NSI', 'Documents_DRIVE', 'nsi-enseignement'}
    for path in sorted(ROOT.rglob('*.md')):
        if skip_dirs & set(path.parts):
            continue
        issues.extend(check_file(path))

    if issues:
        print('ERREUR: liens cassés détectés')
        for file, line, target in issues:
            print(f"{file}:{line} -> {target}")
        raise SystemExit(1)

    print('check_links: PASS')


if __name__ == '__main__':
    main()
