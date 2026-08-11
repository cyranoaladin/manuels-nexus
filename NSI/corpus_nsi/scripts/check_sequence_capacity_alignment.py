#!/usr/bin/env python3
"""Check capacity alignment for focused sequence packs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scripts._qa_common import ROOT, strip_frontmatter


@dataclass
class SequenceCapacityAlignmentResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


P05_CAPACITIES = ["P-TABLE-01", "P-TABLE-02"]
P05_REQUIRED_KINDS = [
    "fiche_cours",
    "cours",
    "trace",
    "td",
    "tp",
    "corrige",
    "bareme",
    "evaluation",
    "remediation",
    "version_amenagee",
]


def p05_files(root: Path) -> list[Path]:
    files: list[Path] = []
    supports = root / "03_progressions" / "supports" / "premiere" / "P05"
    fiches = root / "03_progressions" / "fiches_cours" / "premiere" / "P05"
    if supports.exists():
        files.extend(sorted(supports.glob("P05_*.md")))
    if fiches.exists():
        files.extend(sorted(fiches.glob("P05_*.md")))
    return files


def kind_for(path: Path) -> str:
    name = path.name
    if "fiche_cours" in name:
        return "fiche_cours"
    for kind in P05_REQUIRED_KINDS:
        if f"_{kind}_" in name or name.startswith(f"P05_{kind}_"):
            return kind
    return "autre"


def analyze_p05(root: Path) -> list[str]:
    errors: list[str] = []
    seen_kinds: set[str] = set()
    for path in p05_files(root):
        if path.name.endswith(".md"):
            seen_kinds.add(kind_for(path))
        body = strip_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        rel = path.relative_to(root) if path.is_relative_to(root) else path
        for capacity in P05_CAPACITIES:
            if capacity not in body:
                errors.append(f"{rel}: capacité P05 absente -> {capacity}")
    for kind in P05_REQUIRED_KINDS:
        if kind not in seen_kinds:
            errors.append(f"P05: support attendu absent pour alignement capacité -> {kind}")
    return errors


def analyze_sequence_capacity_alignment(root: Path = ROOT, prefixes: list[str] | None = None) -> SequenceCapacityAlignmentResult:
    prefixes = prefixes or ["P05"]
    result = SequenceCapacityAlignmentResult()
    for prefix in prefixes:
        if prefix == "P05":
            files = p05_files(root)
            result.checked_files += len(files)
            result.errors.extend(analyze_p05(root))
    return result


def main() -> int:
    result = analyze_sequence_capacity_alignment()
    if result.errors:
        print("check_sequence_capacity_alignment: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(f"check_sequence_capacity_alignment: PASS ({result.checked_files} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
