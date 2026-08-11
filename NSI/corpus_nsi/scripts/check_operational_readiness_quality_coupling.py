#!/usr/bin/env python3
"""Ensure operational course-sheet readiness is coupled to real support quality."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scripts._qa_common import ROOT
from scripts._operational_links import operational_resource_links
from scripts.check_linked_evaluation_quality import analyze_linked_evaluation_quality
from scripts.check_linked_evaluation_substance import analyze_linked_evaluation_substance
from scripts.check_linked_td_quality import analyze_linked_td_quality
from scripts.check_linked_td_substance import analyze_linked_td_substance
from scripts.check_operational_supports_no_indicative_debt import analyze_operational_supports_no_indicative_debt


@dataclass
class ReadinessQualityCouplingResult:
    errors: list[str] = field(default_factory=list)
    checked_links: int = 0


def analyze_operational_readiness_quality_coupling(root: Path = ROOT) -> ReadinessQualityCouplingResult:
    result = ReadinessQualityCouplingResult()
    for resource in operational_resource_links(root):
        result.checked_links += 1
        if resource.path is None:
            result.errors.append(f"{resource.sheet}: operational avec support absent -> {resource.link.file}")

    checks = [
        ("qualité TD", analyze_linked_td_quality(root).errors),
        ("substance TD", analyze_linked_td_substance(root).errors),
        ("qualité évaluation", analyze_linked_evaluation_quality(root).errors),
        ("substance évaluation", analyze_linked_evaluation_substance(root).errors),
        ("dette indicative support opérationnel", analyze_operational_supports_no_indicative_debt(root).errors),
    ]
    for label, errors in checks:
        for error in errors:
            result.errors.append(f"{label}: {error}")
    return result


def main() -> int:
    result = analyze_operational_readiness_quality_coupling()
    if result.errors:
        print("check_operational_readiness_quality_coupling: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(f"check_operational_readiness_quality_coupling: PASS ({result.checked_links} liens opérationnels)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
