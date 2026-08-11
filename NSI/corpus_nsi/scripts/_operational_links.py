#!/usr/bin/env python3
"""Discover resources linked from operational course sheets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
import unicodedata
import re

from scripts._qa_common import ROOT, read_frontmatter
from scripts._course_sheets_common import CourseSheetLink, course_sheet_links, sheet_files


@dataclass(frozen=True)
class ReferenceResolution:
    reference: str
    path: Path | None
    candidates: Sequence[Path] = ()

    @property
    def absent(self) -> bool:
        return self.path is None and not self.candidates

    @property
    def ambiguous(self) -> bool:
        return len(self.candidates) > 1


@dataclass(frozen=True)
class OperationalLinkedResource:
    sheet: Path
    link: CourseSheetLink
    path: Path | None
    resolution: ReferenceResolution


def normalize_label(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.lower())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", normalized).strip()


def resolve_reference(root: Path, reference: str) -> ReferenceResolution:
    candidate = root / reference
    if candidate.exists():
        return ReferenceResolution(reference=reference, path=candidate, candidates=(candidate,))
    if "/" in reference:
        return ReferenceResolution(reference=reference, path=None, candidates=())
    matches = sorted(root.rglob(reference))
    if len(matches) == 1:
        return ReferenceResolution(reference=reference, path=matches[0], candidates=tuple(matches))
    if len(matches) > 1:
        return ReferenceResolution(reference=reference, path=None, candidates=tuple(matches))
    return ReferenceResolution(reference=reference, path=None, candidates=())


def operational_sheets(root: Path = ROOT) -> list[Path]:
    return [
        path
        for path in sheet_files(root)
        if str(read_frontmatter(path).get("readiness") or "").strip() == "operational"
    ]


def operational_resource_links(
    root: Path = ROOT,
    element_prefixes: set[str] | None = None,
    existing_only: bool = False,
) -> list[OperationalLinkedResource]:
    prefixes = {normalize_label(prefix) for prefix in element_prefixes} if element_prefixes else None
    resources: list[OperationalLinkedResource] = []
    for sheet in operational_sheets(root):
        for link in course_sheet_links(sheet):
            if link.is_session or not link.is_resource:
                continue
            element = normalize_label(link.element)
            if prefixes and not any(element.startswith(prefix) for prefix in prefixes):
                continue
            resolution = resolve_reference(root, link.file)
            path = resolution.path
            if existing_only and path is None:
                continue
            resources.append(OperationalLinkedResource(sheet=sheet, link=link, path=path, resolution=resolution))
    return sorted(resources, key=lambda item: (item.sheet.as_posix(), item.link.file))
