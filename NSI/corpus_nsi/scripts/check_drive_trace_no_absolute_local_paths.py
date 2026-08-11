#!/usr/bin/env python3
"""Reject personal absolute local paths in versioned Drive trace files."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
import sys
from pathlib import Path

from scripts._qa_common import ROOT
from scripts.check_drive_enrichment_traceability_portable import load_trace

IGNORED_PARTS = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "Documents_DRIVE"}
TEXT_SUFFIXES = {".md", ".txt", ".csv", ".yml", ".yaml", ".py", ".json", ".tex"}
PERSONAL_ABSOLUTE = re.compile(r"(/home/(?!nsi/)[A-Za-z0-9._-]+/[^\s`\"')]+|/Users/[A-Za-z0-9._-]+/[^\s`\"')]+)")
DRIVE_MENTION = re.compile(r"Documents_DRIVE/[^\s`\"')]+")


@dataclass
class DriveTraceNoAbsoluteResult:
    errors: list[str] = field(default_factory=list)


def iter_versioned_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir() or any(part in IGNORED_PARTS for part in path.relative_to(root).parts):
            continue
        if path.suffix in TEXT_SUFFIXES:
            files.append(path)
    return files


def analyze_drive_trace_no_absolute_local_paths(root: Path = ROOT) -> DriveTraceNoAbsoluteResult:
    result = DriveTraceNoAbsoluteResult()
    trace_rows = load_trace(root) if (root / "support_source_trace.yml").exists() else []
    traced_supports = {row.get("support", "") for row in trace_rows if row.get("source_locale_drive")}

    for path in iter_versioned_text_files(root):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in PERSONAL_ABSOLUTE.findall(text):
            result.errors.append(f"{rel}: chemin absolu personnel interdit -> {match}")
        is_support = path.parts and path.relative_to(root).parts[0] in {"03_progressions", "premiere", "terminale"}
        if is_support and DRIVE_MENTION.search(text) and rel not in traced_supports:
            result.errors.append(f"{rel}: mention Documents_DRIVE sans trace support_source_trace.yml")
    return result


def main() -> int:
    result = analyze_drive_trace_no_absolute_local_paths()
    if result.errors:
        print("check_drive_trace_no_absolute_local_paths: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print("check_drive_trace_no_absolute_local_paths: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
