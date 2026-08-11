#!/usr/bin/env python3
"""Check missing_documents_register_v2.md is actionable, not a blanket waiver."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT, read_frontmatter
from scripts._course_sheets_common import course_sheet_links, parse_markdown_table, sheet_files

REGISTER = ROOT / "missing_documents_register_v2.md"
REQUIRED_COLUMNS = [
    "Fichier",
    "Niveau",
    "Séquence",
    "Séance(s)",
    "Type",
    "Priorité",
    "Statut",
    "Responsable",
    "Date cible",
    "Source possible",
    "Lien Drive éventuel",
    "Dépendance",
    "Décision",
    "Blocage si absent",
    "Fiche(s) concernée(s)",
    "Impact pédagogique",
]
CRITICAL_TYPES = {"cours", "td", "tp", "evaluation", "évaluation", "corrige", "corrigé", "trace", "bareme", "barème"}
DECISIONS = {"créer", "importer", "abandonner"}


@dataclass
class MissingRegisterActionabilityResult:
    errors: list[str] = field(default_factory=list)
    checked_rows: int = 0
    absent_rows: int = 0


def table_blocks(text: str) -> list[list[dict[str, str]]]:
    blocks: list[list[dict[str, str]]] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.startswith("|"):
            current.append(line)
        elif current:
            rows = parse_markdown_table("\n".join(current))
            if rows:
                blocks.append(rows)
            current = []
    if current:
        rows = parse_markdown_table("\n".join(current))
        if rows:
            blocks.append(rows)
    return blocks


def load_register_rows(root: Path = ROOT) -> tuple[list[dict[str, str]], list[str]]:
    path = root / "missing_documents_register_v2.md"
    if not path.exists():
        return [], [f"{path.name} absent"]
    rows: list[dict[str, str]] = []
    errors: list[str] = []
    for block in table_blocks(path.read_text(encoding="utf-8", errors="replace")):
        if not block or "Fichier" not in block[0]:
            continue
        header = list(block[0])
        missing_columns = [column for column in REQUIRED_COLUMNS if column not in header]
        if missing_columns:
            errors.append(f"{path.name}: colonnes actionnables manquantes -> {', '.join(missing_columns)}")
        rows.extend(block)
    return rows, errors


def linked_sheet_missing_counts(root: Path, registered_absent: set[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for sheet in sheet_files(root):
        metadata = read_frontmatter(sheet)
        if str(metadata.get("readiness") or "").strip() != "linked":
            continue
        missing = 0
        for link in course_sheet_links(sheet):
            if link.is_resource and (link.file in registered_absent or Path(link.file).name in registered_absent):
                missing += 1
        counts[sheet.name] = missing
    return counts


def analyze_missing_register_actionability(root: Path = ROOT) -> MissingRegisterActionabilityResult:
    result = MissingRegisterActionabilityResult()
    rows, errors = load_register_rows(root)
    result.errors.extend(errors)
    registered_absent: set[str] = set()
    for row in rows:
        if "Fichier" not in row:
            continue
        result.checked_rows += 1
        status = row.get("Statut", "").lower()
        if status != "absent":
            continue
        result.absent_rows += 1
        filename = row.get("Fichier", "")
        registered_absent.add(filename)
        registered_absent.add(Path(filename).name)
        for key in ["Date cible", "Responsable", "Fiche(s) concernée(s)", "Impact pédagogique"]:
            value = row.get(key, "").strip()
            if not value or value.lower() in {"na", "n/a", "à définir", "a definir"}:
                result.errors.append(f"{filename}: champ actionnable absent -> {key}")
        if row.get("Priorité", "").lower() == "haute" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row.get("Date cible", "")):
            result.errors.append(f"{filename}: priorité haute sans date cible précise")
        if row.get("Décision", "").lower() not in DECISIONS:
            result.errors.append(f"{filename}: décision invalide -> {row.get('Décision', '')}")
        critical = row.get("Type", "").lower() in CRITICAL_TYPES or row.get("Priorité", "").lower() == "haute"
        if critical and row.get("Blocage si absent", "").lower() not in {"oui", "yes", "true"}:
            result.errors.append(f"{filename}: support critique non bloquant")

    for sheet, missing_count in linked_sheet_missing_counts(root, registered_absent).items():
        if missing_count > 2:
            result.errors.append(f"{sheet}: fiche linked dépend de plus de deux supports absents ({missing_count})")
    return result


def main() -> int:
    result = analyze_missing_register_actionability()
    if result.errors:
        print("check_missing_register_actionability: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(
        "check_missing_register_actionability: PASS "
        f"({result.checked_rows} lignes registre, {result.absent_rows} supports absents actionnables)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
