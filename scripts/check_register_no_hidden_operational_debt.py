#!/usr/bin/env python3
"""Ensure missing-document register does not hide debt for operational sheets."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scripts._qa_common import ROOT, read_frontmatter
from scripts._course_sheets_common import course_sheet_links, resource_exists, sheet_files
from scripts.check_missing_register_semantic_consistency import register_rows


@dataclass
class HiddenOperationalDebtResult:
    errors: list[str] = field(default_factory=list)
    checked_rows: int = 0


def operational_sheet_names(root: Path) -> set[str]:
    return {
        path.name
        for path in sheet_files(root)
        if str(read_frontmatter(path).get("readiness") or "").strip() == "operational"
    }


def operational_linked_files(root: Path) -> set[str]:
    files: set[str] = set()
    for sheet in sheet_files(root):
        if str(read_frontmatter(sheet).get("readiness") or "").strip() != "operational":
            continue
        for link in course_sheet_links(sheet):
            if link.is_resource:
                files.add(link.file)
                files.add(Path(link.file).name)
    return files


def cited_files(root: Path, filenames: set[str]) -> dict[str, list[str]]:
    citations: dict[str, list[str]] = {filename: [] for filename in filenames}
    if not filenames:
        return citations
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".yml", ".yaml", ".csv"}:
            continue
        if path.name == "missing_documents_register_v2.md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for filename in filenames:
            if filename and filename in text:
                citations[filename].append(path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix())
    return citations


def analyze_register_no_hidden_operational_debt(root: Path = ROOT) -> HiddenOperationalDebtResult:
    result = HiddenOperationalDebtResult()
    rows = register_rows(root)
    operational_names = operational_sheet_names(root)
    operational_links = operational_linked_files(root)
    abandoned: set[str] = set()

    for item in rows:
        row = item.values
        filename = row.get("Fichier", "").strip()
        if not filename:
            continue
        result.checked_rows += 1
        concerned = row.get("Fiche(s) concernée(s)", "")
        decision = (row.get("Décision") or row.get("Decision") or "").strip().lower()
        status = row.get("Statut", "").strip().lower()
        section = item.section

        if any(sheet in concerned for sheet in operational_names):
            result.errors.append(f"{filename}: fiche opérationnelle présente dans le registre -> {concerned}")
        if filename in operational_links or Path(filename).name in operational_links:
            result.errors.append(f"{filename}: support lié à une fiche opérationnelle encore listé au registre")
        if section in {"general", "archive"} and any(sheet in concerned for sheet in operational_names):
            result.errors.append(f"{filename}: dette générale/archive cache une fiche opérationnelle")
        if decision == "abandonner" or status in {"abandonné", "abandonne", "archivé", "archive"} or section == "archive":
            abandoned.add(filename)
            abandoned.add(Path(filename).name)

    for filename, locations in cited_files(root, abandoned).items():
        for location in locations[:20]:
            result.errors.append(f"{filename}: entrée abandonnée encore citée dans {location}")

    unresolved_operational = [
        filename for filename in operational_links if not resource_exists(root, filename) and filename not in {"NA", "na", "-"}
    ]
    for filename in sorted(unresolved_operational):
        result.errors.append(f"{filename}: support opérationnel absent hors registre actionnable")
    return result


def main() -> int:
    result = analyze_register_no_hidden_operational_debt()
    if result.errors:
        print("check_register_no_hidden_operational_debt: KO")
        for error in result.errors[:120]:
            print(f"- {error}")
        return 1
    print(f"check_register_no_hidden_operational_debt: PASS ({result.checked_rows} lignes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
