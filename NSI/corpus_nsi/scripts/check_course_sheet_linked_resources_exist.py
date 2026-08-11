#!/usr/bin/env python3
"""Check course sheet linked resources are real or explicitly registered."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scripts._qa_common import ROOT
from scripts._course_sheets_common import (
    THEORETICAL_LINK_STATUSES,
    course_sheet_links,
    link_is_registered,
    resource_exists,
    session_ids,
    sheet_files,
)


@dataclass
class CourseSheetLinkedResourcesResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0
    existing_links: int = 0
    registered_links: int = 0
    theoretical_links: int = 0


def analyze_course_sheet_links(root: Path = ROOT) -> CourseSheetLinkedResourcesResult:
    result = CourseSheetLinkedResourcesResult()
    sessions = session_ids(root)
    files = sheet_files(root)
    if not files:
        result.errors.append("aucune fiche de cours")
        return result
    for path in files:
        result.checked_files += 1
        links = course_sheet_links(path)
        if not links:
            result.errors.append(f"{path}: table de liens absente")
            continue
        resource_links = [link for link in links if link.is_resource]
        theoretical_for_sheet = 0
        for link in links:
            status = link.normalized_status
            if link.is_session:
                if link.file not in sessions:
                    result.errors.append(f"{path}: séance inexistante -> {link.file}")
                continue
            if not link.is_resource:
                continue
            exists = resource_exists(root, link.file)
            registered = link_is_registered(root, link.file)
            if exists:
                result.existing_links += 1
            elif registered:
                result.registered_links += 1
            else:
                result.errors.append(f"{path}: ressource absent non inscrit au registre -> {link.file}")
            if status in THEORETICAL_LINK_STATUSES or (not exists and not registered):
                theoretical_for_sheet += 1
        if resource_links:
            ratio = theoretical_for_sheet / len(resource_links)
            if ratio > 0.2:
                result.errors.append(f"{path}: trop de liens théoriques ({theoretical_for_sheet}/{len(resource_links)})")
                result.theoretical_links += theoretical_for_sheet
    return result


def main() -> int:
    result = analyze_course_sheet_links()
    if result.errors:
        print("check_course_sheet_linked_resources_exist: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(
        "check_course_sheet_linked_resources_exist: PASS "
        f"({result.checked_files} fiches, {result.existing_links} liens existants, "
        f"{result.registered_links} liens registre)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
