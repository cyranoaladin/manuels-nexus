#!/usr/bin/env python3
"""Reject vague expected outputs in P05 supports."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scripts._qa_common import ROOT


@dataclass
class P05ExpectedOutputsResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


BANNED_PHRASES = [
    "deux lignes européennes sélectionnées",
    "ligne invalide isolée avant conversion",
    "résultat correct",
    "méthode visible",
    "ligne exploitable",
    "réponse attendue non listée",
]


def iter_p05_md(root: Path) -> list[Path]:
    files: list[Path] = []
    for base in [
        root / "03_progressions" / "supports" / "premiere" / "P05",
        root / "03_progressions" / "fiches_cours" / "premiere" / "P05",
    ]:
        if base.exists():
            files.extend(sorted(base.rglob("*.md")))
    return files


def analyze_p05_expected_outputs_are_explicit(root: Path = ROOT) -> P05ExpectedOutputsResult:
    result = P05ExpectedOutputsResult()
    for path in iter_p05_md(root):
        result.checked_files += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()
        for phrase in BANNED_PHRASES:
            if phrase in text:
                result.errors.append(f"{rel}: réponse attendue vague interdite -> {phrase}")
    return result


def main() -> int:
    result = analyze_p05_expected_outputs_are_explicit()
    if result.errors:
        print("check_p05_expected_outputs_are_explicit: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(f"check_p05_expected_outputs_are_explicit: PASS ({result.checked_files} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
