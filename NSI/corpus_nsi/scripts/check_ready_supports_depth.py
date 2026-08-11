#!/usr/bin/env python3
"""Blocking depth gate for supports attached to ready sessions."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scripts._qa_common import ROOT
from scripts.check_first_batch_document_quality import FIRST_BATCH_PREFIXES, REQUIRED_KINDS, find_kind_file, useful_lines

MIN_LINES = {
    "cours": 180,
    "trace": 70,
    "td": 120,
    "tp": 100,
    "corrige": 100,
    "evaluation": 80,
    "bareme": 70,
    "remediation": 80,
    "version_amenagee": 85,
}


@dataclass
class ReadyDepthResult:
    errors: list[str] = field(default_factory=list)


def analyze_ready_depth(root: Path = ROOT, prefixes: list[str] | None = None) -> ReadyDepthResult:
    prefixes = prefixes or FIRST_BATCH_PREFIXES
    result = ReadyDepthResult()
    for prefix in prefixes:
        for kind in REQUIRED_KINDS:
            path = find_kind_file(root, prefix, kind)
            if path is None:
                result.errors.append(f"{prefix}: support {kind} absent")
                continue
            lines = useful_lines(path.read_text(encoding="utf-8", errors="replace"))
            minimum = MIN_LINES.get(kind, 60)
            if len(lines) < minimum:
                result.errors.append(f"{path}: profondeur insuffisante ({len(lines)} lignes utiles, minimum {minimum})")
    return result


def main() -> int:
    result = analyze_ready_depth()
    if result.errors:
        print("check_ready_supports_depth: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print("check_ready_supports_depth: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
