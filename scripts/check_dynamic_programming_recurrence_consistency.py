#!/usr/bin/env python3
"""Check dynamic-programming examples for state, initialization and recurrence."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT


TARGETS = [
    ROOT / "03_progressions" / "supports" / "terminale" / "T17",
    ROOT / "03_progressions" / "fiches_cours" / "terminale" / "T17",
]


@dataclass
class DynamicProgrammingResult:
    errors: list[str] = field(default_factory=list)
    files_checked: int = 0


def fibonacci_table(n: int) -> list[int]:
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return [0]
    values = [0, 1]
    for index in range(2, n + 1):
        values.append(values[index - 1] + values[index - 2])
    return values


def parse_first_integer_list(text: str) -> list[int]:
    matches = re.findall(r"\[([0-9,\s]+)\]", text)
    if not matches:
        return []
    lists = [[int(value) for value in re.findall(r"\d+", match)] for match in matches]
    long_lists = [values for values in lists if len(values) >= 3]
    return long_lists[-1] if long_lists else lists[-1]


def dp_block_errors(text: str) -> list[str]:
    errors: list[str] = []
    lowered = text.lower()
    if re.search(r"\bdp\[|programmation dynamique|mémoïsation|memoisation|tabulation", lowered):
        has_state = bool(re.search(r"état|etat|dp\[", lowered))
        has_init = bool(re.search(r"initialisation|cas de base|dp\[0\]|base", lowered))
        has_rec = bool(re.search(r"relation|récurrence|recurrence|dp\[.*\]\s*=", lowered))
        has_table = bool(re.search(r"table|tabulation|\[[0-9,\s]+\]", lowered))
        if not has_state:
            errors.append("programmation dynamique sans état défini")
        if not has_init:
            errors.append("programmation dynamique sans initialisation")
        if not has_rec:
            errors.append("programmation dynamique sans relation de récurrence")
        if "résultat final" in lowered and not has_table:
            errors.append("résultat final annoncé sans table ou trace")
        table = parse_first_integer_list(text)
        fib_table_context = bool(re.search(r"fib(?:onacci)?[^.\n]{0,160}\[[0-9,\s]+\]", text, re.I | re.S))
        if table and fib_table_context:
            expected = fibonacci_table(len(table) - 1)
            if table != expected:
                errors.append(f"table Fibonacci incohérente: annoncé {table}, attendu {expected}")
        if table and re.search(r"dp\[i\]\s*=\s*dp\[i-1\]\s*\+\s*dp\[i-2\]", lowered):
            expected = fibonacci_table(len(table) - 1)
            if table != expected:
                errors.append(f"relation dp[i]=dp[i-1]+dp[i-2] contredite par la table {table}")
    return errors


def dp_block_is_consistent(text: str) -> bool:
    return not dp_block_errors(text)


def candidate_files(root: Path = ROOT) -> list[Path]:
    files: list[Path] = []
    for base in TARGETS:
        if base.exists():
            files.extend(sorted(base.glob("*.md")))
    return files


def analyze_dynamic_programming_recurrence_consistency(root: Path = ROOT) -> DynamicProgrammingResult:
    result = DynamicProgrammingResult()
    for path in candidate_files(root):
        result.files_checked += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for error in dp_block_errors(text):
            result.errors.append(f"{path.relative_to(root).as_posix()}: {error}")
    return result


def main() -> int:
    result = analyze_dynamic_programming_recurrence_consistency()
    if result.errors:
        print("check_dynamic_programming_recurrence_consistency: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(f"check_dynamic_programming_recurrence_consistency: PASS ({result.files_checked} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
