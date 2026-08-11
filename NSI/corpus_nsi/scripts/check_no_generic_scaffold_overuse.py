#!/usr/bin/env python3
"""Reject repeated scaffold phrases when they are not backed by concrete content."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
import unicodedata

from scripts._qa_common import ROOT


@dataclass
class ScaffoldResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


SCAFFOLD_PHRASES = [
    "Production attendue : une réponse structurée en donnée, méthode, résultat et contrôle.",
    "Production attendue : réponse structurée avec donnée, méthode, résultat et contrôle.",
    "Critère de réussite : un pair peut vérifier le résultat à partir de la donnée.",
    "Critère de réussite : la conclusion est vérifiable par un pair.",
    "Contrôle : comparer la réponse avec la donnée de départ et expliciter le cas limite si l’exercice le demande.",
]

CONCRETE_STRONG_RE = re.compile(
    r"(`[^`]+`|\bSELECT\b|\bFROM\b|\bTTL\b|\bACK\b|\bIP\b|\broute\b|\bpaquet\b|"
    r"\bdp\[|\btrace\b|\binvariant\b|\bcomplexit[eé]\b|\btable\b|\bPAYS\b|\bCONTINENT\b|"
    r"\bPOPULATION\b|\bCAPITALE\b|->|\|.+\|)",
    flags=re.I,
)


def normalize_line(line: str) -> str:
    value = unicodedata.normalize("NFKD", line.strip().lower())
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"\s+", " ", value)
    return value


def has_concrete_context(lines: list[str], index: int) -> bool:
    start = index
    while start > 0 and not re.match(r"^#{2,3}\s+", lines[start]):
        start -= 1
    window = "\n".join(lines[start: index + 4])
    if not CONCRETE_STRONG_RE.search(window) and len(re.findall(r"\b\d+(?:[.,]\d+)?\b", window)) < 2:
        return False
    useful_words = re.findall(r"[A-Za-zÀ-ÿ0-9_]+", window)
    return len(useful_words) >= 18


def target_files(root: Path) -> list[Path]:
    bases = [
        root / "03_progressions" / "supports",
        root / "03_progressions" / "fiches_cours",
        root / "premiere" / "sequences",
        root / "terminale" / "sequences",
    ]
    files: list[Path] = []
    for base in bases:
        if base.exists():
            files.extend(sorted(base.rglob("*.md")))
    return files


def analyze_no_generic_scaffold_overuse(root: Path = ROOT, files: list[Path] | None = None) -> ScaffoldResult:
    result = ScaffoldResult()
    occurrences: dict[str, list[str]] = {phrase: [] for phrase in SCAFFOLD_PHRASES}
    paths = files if files is not None else target_files(root)
    normalized_phrases = {phrase: normalize_line(phrase) for phrase in SCAFFOLD_PHRASES}
    for path in paths:
        result.checked_files += 1
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for index, line in enumerate(lines):
            normalized = normalize_line(line.lstrip("- "))
            for phrase, normalized_phrase in normalized_phrases.items():
                if normalized_phrase in normalized and not has_concrete_context(lines, index):
                    rel = path.relative_to(root) if path.is_relative_to(root) else path
                    occurrences[phrase].append(f"{rel}:{index + 1}")

    for phrase, locations in occurrences.items():
        if len(locations) > 5:
            result.errors.append(
                f"phrase gabarit apparaît {len(locations)} fois sans preuve disciplinaire locale -> {phrase}"
            )
            result.errors.extend(f"  {location}" for location in locations[:12])
    return result


def main() -> int:
    result = analyze_no_generic_scaffold_overuse()
    if result.errors:
        print("check_no_generic_scaffold_overuse: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(f"check_no_generic_scaffold_overuse: PASS ({result.checked_files} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
