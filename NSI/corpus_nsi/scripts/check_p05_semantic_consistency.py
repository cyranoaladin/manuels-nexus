#!/usr/bin/env python3
"""Reject stale or contradictory semantic statements in the P05 CSV pack."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT
from scripts.check_p05_pipeline_consistency import EXPECTED_TOKENS, PIPELINE_TOKENS, p05_files, rel


@dataclass
class P05SemanticResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


FORBIDDEN_PATTERNS = [
    (re.compile(r"Br[ée]sil\s+(est|devient|reste)\s+(un\s+)?pays\s+europ", re.I), "Brésil ne doit jamais être classé comme pays européen"),
    (re.compile(r"Br[ée]sil\s+(est\s+)?(conserv[ée]|retenu|s[eé]lectionn[ée])", re.I), "Brésil ne doit jamais être retenu dans Europe"),
    (re.compile(r"inclu(?:re|t)?\s+Br[ée]sil\s+dans\s+Europe", re.I), "Brésil ne doit jamais être retenu dans Europe"),
    (re.compile(r"\bAndorre\b", re.I), "Andorre est absente de l’extrait P05 de référence"),
    (re.compile(r"(avant conversion|avant de convertir|rejet avant)", re.I), "les erreurs sont produites par conversion puis ValueError, pas avant conversion"),
    (re.compile(r"\bdeux lignes europ[ée]ennes s[eé]lectionn[ée]es\b", re.I), "résultat vague interdit"),
    (re.compile(r"\bligne invalide isol[ée]e\b", re.I), "résultat vague interdit"),
    (re.compile(r"\br[ée]sultat correct\b", re.I), "résultat vague interdit"),
    (re.compile(r"\bm[ée]thode visible\b", re.I), "critère vague interdit"),
]

ORDER_CONTRADICTIONS = [
    re.compile(r"filtrer[^.\n]{0,80}(puis|avant)[^.\n]{0,80}convert", re.I),
]


def has_pipeline_block(text: str) -> bool:
    return all(token in text for token in PIPELINE_TOKENS)


def analyze_p05_semantic_consistency(root: Path = ROOT) -> P05SemanticResult:
    result = P05SemanticResult()
    for path in p05_files(root):
        if path.suffix != ".md":
            continue
        result.checked_files += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        local: list[str] = []
        if not has_pipeline_block(text):
            local.append("bloc Pipeline contrôlé P05 absent ou incomplet")
        for token in EXPECTED_TOKENS:
            if token not in text:
                local.append(f"résultat exact absent -> {token}")
        for pattern, message in FORBIDDEN_PATTERNS:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                local.append(f"ligne {line}: {message}")
        for pattern in ORDER_CONTRADICTIONS:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                local.append(f"ligne {line}: consigne contradictoire avec conversion puis filtrage")
        for error in local:
            result.errors.append(f"{rel(path, root)}: {error}")
    return result


def main() -> int:
    result = analyze_p05_semantic_consistency()
    if result.errors:
        print("check_p05_semantic_consistency: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(f"check_p05_semantic_consistency: PASS ({result.checked_files} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
