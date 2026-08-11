#!/usr/bin/env python3
"""Check that correction blocks contain concrete disciplinary answers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT, strip_frontmatter
from scripts.check_linked_td_substance import correction_has_substance


@dataclass
class ConcreteCorrectionResult:
    errors: list[str] = field(default_factory=list)
    checked_blocks: int = 0


CORRECTION_BLOCK_RE = re.compile(
    r"^###\s+(Corrigé exercice|Corrig[eé] question|Réponse rapide|Reponse rapide)\s*(\d+)?\b"
    r"(.*?)(?=^###\s+|\n##\s+|\Z)",
    flags=re.M | re.S | re.I,
)

GENERIC_ONLY_RE = re.compile(
    r"(réponse correcte|démarche claire|conclusion correcte|production vérifiable|réponse structurée|"
    r"résultat indicatif|solution explicite|réponse explicite)",
    flags=re.I,
)

RESULT_MARKER_RE = re.compile(
    r"(résultat attendu|resultat attendu|valeur attendue|valeurs attendues|réponse attendue|reponse attendue|"
    r"renvoie|vaut|donne|milieu|clé primaire|cle primaire|clé étrangère|cle etrangere|contrainte)",
    flags=re.I,
)

CONCRETE_EVIDENCE_RE = re.compile(
    r"(`[^`]+`|\[[^\]]+\]|\{[^}]+\}|\([^)]+,[^)]+\)|\b\d+(?:[.,]\d+)?\b|->|"
    r"\bSELECT\b|\bFROM\b|\bIP\b|\bTTL\b|\bACK\b|\bLIFO\b|\bFIFO\b|\bO\([^)]+\)|"
    r"\btrace\b|\balignement\b|\bdécalage\b|\bdecalage\b|\bmotif\b|\bEleve\.|"
    r"\bNote\.|\bid_eleve\b|\bid_note\b|\bPOPULATION\b|\bCONTINENT\b)",
    flags=re.I | re.S,
)


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


def correction_blocks(text: str) -> list[tuple[str, str]]:
    body = strip_frontmatter(text)
    blocks: list[tuple[str, str]] = []
    for match in CORRECTION_BLOCK_RE.finditer(body):
        title = " ".join(part for part in [match.group(1), match.group(2) or ""] if part)
        blocks.append((title, match.group(3).strip()))
    return blocks


def analyze_one_file(path: Path, root: Path = ROOT) -> tuple[int, list[str]]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = correction_blocks(text)
    rel = path.relative_to(root) if path.is_relative_to(root) else path
    for title, block in blocks:
        has_direct_concrete_answer = bool(RESULT_MARKER_RE.search(block) and CONCRETE_EVIDENCE_RE.search(block))
        if GENERIC_ONLY_RE.search(block) and not has_direct_concrete_answer and not correction_has_substance(path, title, block):
            errors.append(f"{rel}: {title} sans résultat disciplinaire concret")
        elif not has_direct_concrete_answer and not correction_has_substance(path, title, block):
            errors.append(f"{rel}: {title} sans résultat disciplinaire concret")
    return len(blocks), errors


def analyze_corrected_answers(root: Path = ROOT, files: list[Path] | None = None) -> ConcreteCorrectionResult:
    result = ConcreteCorrectionResult()
    paths = files if files is not None else target_files(root)
    for path in paths:
        checked, errors = analyze_one_file(path, root)
        result.checked_blocks += checked
        result.errors.extend(errors)
    return result


def main() -> int:
    result = analyze_corrected_answers()
    if result.errors:
        print("check_corrected_answers_are_concrete: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(f"check_corrected_answers_are_concrete: PASS ({result.checked_blocks} blocs corrigés)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
