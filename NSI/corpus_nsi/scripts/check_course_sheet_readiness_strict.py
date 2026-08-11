#!/usr/bin/env python3
"""Strict course sheet readiness audit with missing-support details."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from scripts._qa_common import ROOT, read_frontmatter
from scripts._course_sheets_common import (
    CourseSheetLink,
    VALID_READINESS,
    course_sheet_links,
    link_is_registered,
    resource_exists,
    session_ids,
    sheet_files,
)

KEY_RESOURCE_ELEMENTS = {"td", "tp", "evaluation", "évaluation"}


@dataclass
class StrictReadinessResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0
    counts: Counter[str] = field(default_factory=Counter)
    linked_missing: dict[str, list[str]] = field(default_factory=dict)


def key_resource_missing(root: Path, links: list[CourseSheetLink]) -> list[str]:
    missing: list[str] = []
    for link in links:
        if not link.is_resource:
            continue
        element = link.element.lower().strip()
        is_key = any(element.startswith(kind) for kind in KEY_RESOURCE_ELEMENTS)
        if is_key and not resource_exists(root, link.file):
            missing.append(link.file)
    return missing


def strict_computed_readiness(root: Path, links: list[CourseSheetLink]) -> str:
    sessions = session_ids(root)
    has_session = any(link.is_session and link.file in sessions for link in links)
    resources = [link for link in links if link.is_resource]
    if not has_session or not resources:
        return "theoretical"
    unresolved = [
        link.file
        for link in resources
        if not resource_exists(root, link.file) and not link_is_registered(root, link.file)
    ]
    if unresolved:
        return "theoretical"
    missing = key_resource_missing(root, resources)
    if missing:
        return "linked"
    return "operational"


def analyze_course_sheet_readiness_strict(root: Path = ROOT) -> StrictReadinessResult:
    result = StrictReadinessResult()
    files = sheet_files(root)
    if not files:
        result.errors.append("aucune fiche de cours")
        return result
    for path in files:
        result.checked_files += 1
        declared = str(read_frontmatter(path).get("readiness") or "").strip()
        if declared not in VALID_READINESS:
            result.errors.append(f"{path}: readiness invalide ou absente -> {declared or 'absent'}")
            continue
        links = course_sheet_links(path)
        computed = strict_computed_readiness(root, links)
        result.counts[computed] += 1
        missing = key_resource_missing(root, links)
        if computed == "linked":
            result.linked_missing[path.as_posix()] = missing
        if declared == "operational" and missing:
            result.errors.append(f"{path}: operational interdit avec support absent -> {', '.join(missing)}")
        if declared != computed:
            result.errors.append(f"{path}: readiness déclarée {declared} mais calculée strictement {computed}")
    return result


def main() -> int:
    result = analyze_course_sheet_readiness_strict()
    print(f"Nombre de fiches théoriques strictes : {result.counts.get('theoretical', 0)}")
    print(f"Nombre de fiches liées strictes : {result.counts.get('linked', 0)}")
    print(f"Nombre de fiches opérationnelles strictes : {result.counts.get('operational', 0)}")
    if result.linked_missing:
        print("Fiches liées non opérationnelles :")
        for sheet, missing in sorted(result.linked_missing.items()):
            print(f"- {sheet}: {', '.join(missing) if missing else 'support manquant non identifié'}")
    if result.errors:
        print("check_course_sheet_readiness_strict: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(f"check_course_sheet_readiness_strict: PASS ({result.checked_files} fiches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
