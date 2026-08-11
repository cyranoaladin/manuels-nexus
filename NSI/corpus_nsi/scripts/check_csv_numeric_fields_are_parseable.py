#!/usr/bin/env python3
"""Reject invalid CSV numeric examples in the P05 pays_monde thread."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT


@dataclass
class CsvNumericResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


P05_DIRS = [
    ROOT / "03_progressions" / "supports" / "premiere" / "P05",
    ROOT / "03_progressions" / "fiches_cours" / "premiere" / "P05",
]


def iter_p05_text_files(root: Path) -> list[Path]:
    dirs = [
        root / "03_progressions" / "supports" / "premiere" / "P05",
        root / "03_progressions" / "fiches_cours" / "premiere" / "P05",
    ]
    files: list[Path] = []
    for directory in dirs:
        if directory.exists():
            files.extend(sorted(path for path in directory.rglob("*") if path.suffix in {".md", ".py", ".csv"}))
    return files


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()


def analyze_file(path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for index, line in enumerate(lines, start=1):
        stripped = line.strip().strip("`")
        if stripped.startswith("PAYS,CAPITALE,CONTINENT,POPULATION"):
            continue
        if re.match(r"^[A-ZÉÈÀÂÎÔÛÇA-Za-zéèàâîôûç\-]+,[^,]+,[^,]+,\d{1,3}(,\d{3})+", stripped):
            errors.append(f"{rel(path, root)}:{index}: ligne CSV population avec trop de colonnes -> {stripped}")
        if re.search(r'POPULATION["\']?\s*[:=]\s*["\']\d{1,3}(,\d{3})+["\']', line):
            errors.append(f"{rel(path, root)}:{index}: valeur POPULATION avec virgules non convertible par int()")
        if 'int(row["POPULATION"])' in line and re.search(r"\d{1,3}(,\d{3})+", line):
            errors.append(f"{rel(path, root)}:{index}: affirmation non convertible avec int(row[\"POPULATION\"])")
    return errors


def analyze_csv_numeric_fields_are_parseable(root: Path = ROOT) -> CsvNumericResult:
    result = CsvNumericResult()
    for path in iter_p05_text_files(root):
        result.checked_files += 1
        result.errors.extend(analyze_file(path, root))
    return result


def main() -> int:
    result = analyze_csv_numeric_fields_are_parseable()
    if result.errors:
        print("check_csv_numeric_fields_are_parseable: KO")
        for error in result.errors[:120]:
            print(f"- {error}")
        return 1
    print(f"check_csv_numeric_fields_are_parseable: PASS ({result.checked_files} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
