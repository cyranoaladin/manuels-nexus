#!/usr/bin/env python3
"""Detect validation obtained by adding a keyword block while the body contradicts it."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT
from scripts.check_p05_pipeline_consistency import p05_files, rel


@dataclass
class TokenOnlyResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


TAIL_MARKER = "## Pipeline contrôlé P05"
BODY_CONTRADICTIONS = [
    re.compile(r"filtr(?:er|e|age)[^.\n]{0,80}(puis|avant)[^.\n]{0,80}convert", re.I),
    re.compile(r"Br[ée]sil\s+(est|devient|reste)\s+(un\s+)?pays\s+europ", re.I),
    re.compile(r"Br[ée]sil\s+(est\s+)?(conserv[ée]|retenu|s[eé]lectionn[ée])", re.I),
    re.compile(r"\bAndorre\b", re.I),
    re.compile(r"(avant conversion|avant de convertir|rejet avant)", re.I),
]


def analyze_no_token_only_validation(root: Path = ROOT) -> TokenOnlyResult:
    result = TokenOnlyResult()
    for path in p05_files(root):
        if path.suffix != ".md":
            continue
        result.checked_files += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        marker_index = text.find(TAIL_MARKER)
        if marker_index == -1:
            continue
        body = text[:marker_index]
        for pattern in BODY_CONTRADICTIONS:
            for match in pattern.finditer(body):
                line = body.count("\n", 0, match.start()) + 1
                result.errors.append(
                    f"{rel(path, root)}:{line}: bloc final P05 ne peut pas compenser une contradiction du corps"
                )
    return result


def main() -> int:
    result = analyze_no_token_only_validation()
    if result.errors:
        print("check_no_token_only_validation: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(f"check_no_token_only_validation: PASS ({result.checked_files} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
