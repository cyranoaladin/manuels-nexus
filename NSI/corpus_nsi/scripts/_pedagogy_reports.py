#!/usr/bin/env python3
"""Helpers for pedagogical QA report scripts."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from scripts._qa_common import ROOT, TARGET_SEQUENCES, useful_lines


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def line_count(sequence: Path, name: str) -> int:
    path = sequence / name
    return len(useful_lines(path)) if path.exists() else 0


def contains(sequence: Path, name: str, tokens: Iterable[str]) -> list[str]:
    path = sequence / name
    if not path.exists():
        return list(tokens)
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    return [token for token in tokens if token.lower() not in text]


def write_report(path: Path, title: str, lines: list[str]) -> None:
    path.write_text("\n".join([f"# {title}", "", *lines, ""]) , encoding="utf-8")
    print(f"{path.name}: rapport généré")


def pilot_sequences() -> list[tuple[str, Path]]:
    return [(level, path) for level, path in TARGET_SEQUENCES.items()]
