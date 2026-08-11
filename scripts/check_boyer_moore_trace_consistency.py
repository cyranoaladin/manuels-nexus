#!/usr/bin/env python3
"""Check Boyer-Moore traces for bad-character table and shifts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT


TARGETS = [
    ROOT / "03_progressions" / "supports" / "terminale" / "T18",
    ROOT / "03_progressions" / "fiches_cours" / "terminale" / "T18",
]


@dataclass
class BoyerMooreResult:
    errors: list[str] = field(default_factory=list)
    files_checked: int = 0


def bad_character_table(pattern: str) -> dict[str, int]:
    return {char: index for index, char in enumerate(pattern)}


def boyer_moore_search(text: str, pattern: str) -> int:
    if pattern == "":
        return 0
    table = bad_character_table(pattern)
    i = 0
    m = len(pattern)
    n = len(text)
    while i <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[i + j]:
            j -= 1
        if j < 0:
            return i
        bad_char = text[i + j]
        i += max(1, j - table.get(bad_char, -1))
    return -1


def parse_declared_table(text: str) -> dict[str, int]:
    result: dict[str, int] = {}
    for char, raw_index in re.findall(r"\b([A-Z])\s*(?:->|:)\s*(-?\d+)", text):
        result[char] = int(raw_index)
    return result


def boyer_moore_block_errors(text: str) -> list[str]:
    errors: list[str] = []
    lowered = text.lower()
    if "boyer" in lowered or ("motif" in lowered and "décalage" in lowered):
        has_table = bool(re.search(r"mauvais caractère|mauvais caractere|table", lowered))
        has_right_left = bool(re.search(r"droite\s*(?:à|a|-)\s*gauche|depuis\s+la\s+droite", lowered))
        has_shift = "décalage" in lowered or "decalage" in lowered
        has_index = bool(re.search(r"indice\s+(?:trouvé|trouve|absent|\d+)", lowered))
        if not has_table:
            errors.append("Boyer-Moore sans table du mauvais caractère")
        if not has_right_left:
            errors.append("Boyer-Moore sans comparaison de droite à gauche")
        if not has_shift:
            errors.append("Boyer-Moore sans décalage calculé")
        if "cas absent" in lowered and "absent" not in lowered:
            errors.append("cas absent annoncé sans résultat absent")
        if "motif trouvé" in lowered and not has_index:
            errors.append("motif trouvé sans indice")
        data = re.search(r"texte\s*=\s*\"([^\"]+)\".*?motif\s*=\s*\"([^\"]+)\"", text, re.I | re.S)
        if not data:
            data = re.search(r"texte\s+([A-Z]+).*?motif\s+([A-Z]+)", text, re.I | re.S)
        if data:
            haystack, pattern = data.groups()
            expected_table = bad_character_table(pattern)
            declared_table = parse_declared_table(text)
            if declared_table and any(declared_table.get(char) != index for char, index in expected_table.items()):
                errors.append(f"table du mauvais caractère incohérente: annoncé {declared_table}, attendu {expected_table}")
            expected_index = boyer_moore_search(haystack, pattern)
            segment = text[data.end() : data.end() + 320]
            index_match = re.search(r"indice\s+(?:trouv[ée]|=|:)?\s*(-?\d+)", segment, re.I)
            if index_match and int(index_match.group(1)) != expected_index:
                errors.append(f"indice Boyer-Moore annoncé {index_match.group(1)}, attendu {expected_index}")
    return errors


def boyer_moore_block_is_consistent(text: str) -> bool:
    return not boyer_moore_block_errors(text)


def candidate_files(root: Path = ROOT) -> list[Path]:
    files: list[Path] = []
    for base in TARGETS:
        if base.exists():
            files.extend(sorted(base.glob("*.md")))
    return files


def analyze_boyer_moore_trace_consistency(root: Path = ROOT) -> BoyerMooreResult:
    result = BoyerMooreResult()
    for path in candidate_files(root):
        result.files_checked += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for error in boyer_moore_block_errors(text):
            result.errors.append(f"{path.relative_to(root).as_posix()}: {error}")
    return result


def main() -> int:
    result = analyze_boyer_moore_trace_consistency()
    if result.errors:
        print("check_boyer_moore_trace_consistency: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(f"check_boyer_moore_trace_consistency: PASS ({result.files_checked} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
