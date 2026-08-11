#!/usr/bin/env python3
"""Check that T18 has a complete Boyer-Moore trace linked to executable assets."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scripts._qa_common import ROOT, read_frontmatter


@dataclass
class T18TraceResult:
    errors: list[str] = field(default_factory=list)


TRACE = ROOT / "03_progressions" / "supports" / "terminale" / "T18" / "T18_trace_boyer_moore.md"
CODE_PATTERNS = [
    "T18_starter_boyer_moore.py",
    "T18_corrige_professeur_boyer_moore.py",
    "T18_tests_attendus_boyer_moore.py",
]


def analyze_t18_trace_table_quality(root: Path = ROOT) -> T18TraceResult:
    result = T18TraceResult()
    trace = root / TRACE.relative_to(ROOT)
    if not trace.exists():
        result.errors.append("T18: T18_trace_boyer_moore.md absent")
        return result
    text = trace.read_text(encoding="utf-8", errors="replace")
    metadata = read_frontmatter(trace)
    document_type = str(metadata.get("document_type", ""))
    tp_mode = str(metadata.get("tp_mode", ""))
    if document_type != "trace":
        result.errors.append(f"T18: document_type attendu trace -> {document_type}")
    if tp_mode != "executable_trace":
        result.errors.append(f"T18: tp_mode attendu executable_trace -> {tp_mode}")
    for token in [
        "Table de trace algorithmique",
        "Table du mauvais caractère",
        "| Alignement |",
        "Décalage calculé",
        "Pseudo-code de référence",
        "Barème associé",
        "Corrigé question par question",
        "T18_TD_boyer_moore.md",
        "T18_evaluation_boyer_moore.md",
        "T18_tp_boyer_moore.md",
        "T18_tests_attendus_boyer_moore.py",
    ]:
        if token not in text:
            result.errors.append(f"T18: élément de trace algorithmique absent -> {token}")
    code_dir = trace.parent / "code"
    for pattern in CODE_PATTERNS:
        if not (code_dir / pattern).exists():
            result.errors.append(f"T18: asset Python attendu absent -> {pattern}")
    return result


def main() -> int:
    result = analyze_t18_trace_table_quality()
    if result.errors:
        print("check_t18_trace_table_quality: KO")
        for error in result.errors:
            print(f"- {error}")
        return 1
    print("check_t18_trace_table_quality: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
