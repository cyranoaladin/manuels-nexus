#!/usr/bin/env python3
"""Check coarse pedagogical coherence inside each sequence package."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT


CAPACITY_RE = re.compile(r"\b[PT](?:-[A-Z]+)+-\d{2}[A-Z]?\b")


@dataclass
class SequencePedagogicalCoherenceResult:
    errors: list[str] = field(default_factory=list)
    checked_sequences: int = 0


def capacities(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(CAPACITY_RE.findall(path.read_text(encoding="utf-8", errors="replace")))


def files_by_kind(sequence_dir: Path, prefix: str, token: str) -> list[Path]:
    return sorted(path for path in sequence_dir.glob(f"{prefix}_*.md") if token.lower() in path.name.lower())


def joined_text(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths)


def analyze_sequence_pedagogical_coherence(root: Path = ROOT) -> SequencePedagogicalCoherenceResult:
    result = SequencePedagogicalCoherenceResult()
    for level in ["premiere", "terminale"]:
        base = root / "03_progressions" / "supports" / level
        if not base.exists():
            continue
        for sequence_dir in sorted(path for path in base.iterdir() if path.is_dir() and re.fullmatch(r"[PT]\d{2}", path.name)):
            prefix = sequence_dir.name
            result.checked_sequences += 1
            cours = files_by_kind(sequence_dir, prefix, "cours")
            tds = files_by_kind(sequence_dir, prefix, "td")
            tps = files_by_kind(sequence_dir, prefix, "tp")
            evaluations = files_by_kind(sequence_dir, prefix, "evaluation")
            remediations = files_by_kind(sequence_dir, prefix, "remediation")
            versions = files_by_kind(sequence_dir, prefix, "version_amenagee")
            worked_caps = set().union(*(capacities(path) for path in cours + tds + tps))
            assessed_caps = set().union(*(capacities(path) for path in evaluations))
            if assessed_caps and not (assessed_caps & worked_caps):
                result.errors.append(f"{prefix}: évaluation sans capacité préparée dans cours/TD/TP")
            td_text = joined_text(tds).lower()
            tp_text = joined_text(tps).lower()
            if tps and tds and not (set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]{3,}\b", td_text)) & set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]{3,}\b", tp_text))):
                result.errors.append(f"{prefix}: TD et TP sans vocabulaire commun détectable")
            remediation_text = joined_text(remediations).lower()
            if remediations and not re.search(r"erreur|remédiation|corriger|confusion|oubli", remediation_text):
                result.errors.append(f"{prefix}: remédiation sans erreur fréquente ciblée")
            version_caps = set().union(*(capacities(path) for path in versions))
            if versions and assessed_caps and not (version_caps & assessed_caps):
                result.errors.append(f"{prefix}: version aménagée sans capacité évaluée conservée")
    return result


def main() -> int:
    result = analyze_sequence_pedagogical_coherence()
    print(f"Séquences vérifiées : {result.checked_sequences}")
    if result.errors:
        print("check_sequence_pedagogical_coherence: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print("check_sequence_pedagogical_coherence: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
