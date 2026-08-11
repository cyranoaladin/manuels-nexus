#!/usr/bin/env python3
"""Remove local Python bytecode artifacts before audit commands."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIRS = {"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"}


def cleanup(root: Path = ROOT) -> list[Path]:
    removed: list[Path] = []
    for path in sorted(candidate for name in CACHE_DIRS for candidate in root.rglob(name)):
        if ".git" in path.relative_to(root).parts:
            continue
        if path.is_dir():
            shutil.rmtree(path)
            removed.append(path)
    for path in sorted(root.rglob("*.py[co]")):
        if ".git" in path.relative_to(root).parts:
            continue
        if path.is_file():
            path.unlink()
            removed.append(path)
    return removed


def main() -> int:
    removed = cleanup()
    print(f"cleanup_python_artifacts: removed {len(removed)} path(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
