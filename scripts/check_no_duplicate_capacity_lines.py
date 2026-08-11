#!/usr/bin/env python3
"""Reject duplicate capacity lines in short capability sections."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT


@dataclass
class DuplicateCapacityResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


CAPACITY_RE = re.compile(r"\b[PT]-[A-Z]+-\d{2}[A-Z]?\b")
CAPABILITY_CONTEXT_RE = re.compile(
    r"(Capacit[ée]s\s+(?:[ée]valu[ée]es|travaill[ée]es|officielles)|"
    r"official_program\.capacities|capacities\s*:)",
    flags=re.I,
)


def support_files(root: Path) -> list[Path]:
    base = root / "03_progressions" / "supports"
    return sorted(base.rglob("*.md")) if base.exists() else []


def markdown_heading_capacity_sections(text: str) -> list[str]:
    sections: list[str] = []
    for match in re.finditer(r"^## .*Capacit[ée]s.*$", text, flags=re.M):
        start = match.end()
        next_match = re.search(r"^##\s+", text[start:], flags=re.M)
        end = start + next_match.start() if next_match else len(text)
        sections.append(text[start:end])
    return sections


def contextual_capacity_blocks(text: str) -> list[str]:
    lines = text.splitlines()
    blocks: list[str] = []
    for index, line in enumerate(lines):
        if not CAPABILITY_CONTEXT_RE.search(line):
            continue
        block = [line]
        for following in lines[index + 1 : index + 10]:
            stripped = following.strip()
            if not stripped:
                break
            if stripped.startswith("## ") and "Capacit" not in stripped:
                break
            if CAPACITY_RE.search(stripped) or stripped.startswith(("-", "*")) or ":" in stripped:
                block.append(following)
                continue
            break
        blocks.append("\n".join(block))
    return blocks


def capacity_sections(text: str) -> list[str]:
    seen: set[str] = set()
    sections: list[str] = []
    for block in markdown_heading_capacity_sections(text) + contextual_capacity_blocks(text):
        if block not in seen:
            seen.add(block)
            sections.append(block)
    return sections


def analyze_no_duplicate_capacity_lines(root: Path = ROOT) -> DuplicateCapacityResult:
    result = DuplicateCapacityResult()
    for path in support_files(root):
        result.checked_files += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()
        for block in capacity_sections(text):
            capacities = CAPACITY_RE.findall(block)
            seen: set[str] = set()
            for capacity in capacities:
                if capacity in seen:
                    result.errors.append(f"{rel}: capacité dupliquée dans une section courte -> {capacity}")
                seen.add(capacity)
        if path.name == "P05_evaluation_tables_csv.md":
            sections = "\n".join(capacity_sections(text))
            for expected in ["P-TABLE-01", "P-TABLE-02"]:
                if expected not in sections:
                    result.errors.append(f"{rel}: capacité attendue absente des capacités évaluées -> {expected}")
    return result


def main() -> int:
    result = analyze_no_duplicate_capacity_lines()
    if result.errors:
        print("check_no_duplicate_capacity_lines: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(f"check_no_duplicate_capacity_lines: PASS ({result.checked_files} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
