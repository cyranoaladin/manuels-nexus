#!/usr/bin/env python3
"""Ensure P04 station dictionaries use the `temperature` key consistently."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT


@dataclass
class P04KeyConsistencyResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


def p04_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for base in [
        root / "03_progressions" / "supports" / "premiere" / "P04",
        root / "03_progressions" / "fiches_cours" / "premiere" / "P04",
    ]:
        if base.exists():
            files.extend(sorted(path for path in base.rglob("*") if path.suffix in {".md", ".py"}))
    return files


TEMP_KEY_RE = re.compile(r'(["`])temp\1|\btemp\s*[:>=]')


def analyze_p04_key_consistency(root: Path = ROOT) -> P04KeyConsistencyResult:
    result = P04KeyConsistencyResult()
    for path in p04_files(root):
        result.checked_files += 1
        rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()
        for index, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            if TEMP_KEY_RE.search(line):
                result.errors.append(f'{rel}:{index}: clé "temp" interdite, utiliser "temperature"')
    return result


def main() -> int:
    result = analyze_p04_key_consistency()
    if result.errors:
        print("check_p04_key_consistency: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(f"check_p04_key_consistency: PASS ({result.checked_files} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
