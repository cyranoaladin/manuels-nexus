#!/usr/bin/env python3
"""Verify direct script execution does not leave Python bytecode caches."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def remove_caches() -> None:
    for path in ROOT.rglob("__pycache__"):
        if path.is_dir():
            shutil.rmtree(path)


def cache_paths() -> list[Path]:
    return sorted(path.relative_to(ROOT) for path in ROOT.rglob("__pycache__"))


def main() -> int:
    remove_caches()
    env = os.environ.copy()
    env.pop("PYTHONDONTWRITEBYTECODE", None)
    result = subprocess.run(
        [sys.executable, "scripts/check_metadata.py"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    caches = cache_paths()
    if result.returncode != 0 or caches:
        print("check_python_cache_stability: KO")
        if result.returncode != 0:
            print(result.stdout.strip())
        for path in caches:
            print(f"- cache créé: {path}")
        remove_caches()
        return 1
    print("check_python_cache_stability: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
