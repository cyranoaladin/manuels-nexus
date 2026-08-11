#!/usr/bin/env python3
"""Check that Drive integration is planned and traceable, without claiming completion."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import csv
import re

import yaml

from scripts._qa_common import ROOT, read_frontmatter
from scripts._drive_paths import resolve_drive_reference

INVENTORY = "drive_inventory.csv"
QUARANTINE = "drive_quarantine_manifest.csv"
TRACE = "support_source_trace.yml"
REQUIRED_CSV_COLUMNS = {
    "drive_url",
    "drive_folder",
    "file_name",
    "mime_type",
    "local_copy",
    "sha256",
    "niveau",
    "theme",
    "sequence_possible",
    "qualite_initiale",
    "decision",
    "raison",
}


@dataclass
class DriveIntegrationPlanResult:
    errors: list[str] = field(default_factory=list)
    inventory_rows: int = 0
    quarantine_rows: int = 0
    trace_rows: int = 0


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], set[str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), set(reader.fieldnames or [])


def load_trace(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = data.get("supports", []) if isinstance(data, dict) else []
    cleaned = []
    for row in rows:
        if isinstance(row, dict):
            cleaned.append({str(key): "" if value is None else str(value) for key, value in row.items()})
    return cleaned


def resolve_drive_path(value: str) -> Path | None:
    return resolve_drive_reference(value, ROOT)


def support_files(root: Path) -> list[Path]:
    bases = [root / "03_progressions" / "supports", root / "03_progressions" / "fiches_cours"]
    files: list[Path] = []
    for base in bases:
        if base.exists():
            files.extend(path for path in base.rglob("*.md") if path.is_file())
    return sorted(files)


def analyze_drive_integration_plan(root: Path = ROOT) -> DriveIntegrationPlanResult:
    result = DriveIntegrationPlanResult()
    inventory_path = root / INVENTORY
    quarantine_path = root / QUARANTINE
    trace_path = root / TRACE

    if not inventory_path.exists():
        result.errors.append(f"{INVENTORY} absent")
    if not quarantine_path.exists():
        result.errors.append(f"{QUARANTINE} absent")
    if not trace_path.exists():
        result.errors.append(f"{TRACE} absent")
    if result.errors:
        return result

    for label, csv_path in [(INVENTORY, inventory_path), (QUARANTINE, quarantine_path)]:
        rows, columns = read_csv_rows(csv_path)
        if label == INVENTORY:
            result.inventory_rows = len(rows)
        else:
            result.quarantine_rows = len(rows)
        missing = REQUIRED_CSV_COLUMNS - columns
        if missing:
            result.errors.append(f"{label}: colonnes manquantes -> {', '.join(sorted(missing))}")
        if not rows:
            result.errors.append(f"{label}: aucun élément classé")
        for index, row in enumerate(rows, start=2):
            for key in ["qualite_initiale", "decision", "raison"]:
                if not (row.get(key) or "").strip():
                    result.errors.append(f"{label}:{index}: champ de classification vide -> {key}")

    trace_rows = load_trace(trace_path)
    result.trace_rows = len(trace_rows)
    if not trace_rows:
        result.errors.append(f"{TRACE}: aucune entrée support")
    trace_by_support = {row.get("support", ""): row for row in trace_rows if row.get("support")}

    for row in trace_rows:
        support_name = row.get("support", "")
        source = row.get("source_locale_drive", "")
        reprise = row.get("type_reprise", "")
        rgpd = row.get("statut_rgpd", "")
        if not rgpd:
            result.errors.append(f"{support_name}: statut_rgpd absent dans {TRACE}")
        if source:
            drive_path = resolve_drive_path(source)
            if drive_path is None:
                result.errors.append(f"{support_name}: source_locale_drive non résoluble -> {source}")
            elif not drive_path.exists():
                result.errors.append(f"{support_name}: source_locale_drive absente -> {source}")
            if reprise == "création originale":
                result.errors.append(f"{support_name}: source Drive renseignée mais type_reprise création originale")
        elif reprise != "création originale":
            result.errors.append(f"{support_name}: reprise Drive déclarée sans source_locale_drive")

    for support in support_files(root):
        rel = support.relative_to(root).as_posix() if support.is_relative_to(root) else support.as_posix()
        metadata = read_frontmatter(support)
        text = support.read_text(encoding="utf-8", errors="replace")
        mentions = re.findall(r"(?:[A-Za-z0-9_./-]+/)?Documents_DRIVE/[^\s)`]+", text)
        source_creation = str(metadata.get("source_creation") or "")
        trace = trace_by_support.get(rel) or trace_by_support.get(support.name)
        if mentions or source_creation == "adapted_from_drive":
            if trace is None:
                result.errors.append(f"{rel}: ressource Drive utilisée sans trace dans {TRACE}")
            elif not trace.get("source_locale_drive"):
                result.errors.append(f"{rel}: adaptation Drive sans source_locale_drive tracée")
    return result


def main() -> int:
    result = analyze_drive_integration_plan()
    if result.errors:
        print("check_drive_integration_plan: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(
        "check_drive_integration_plan: PASS "
        f"({result.inventory_rows} inventaire, {result.quarantine_rows} quarantaine, {result.trace_rows} traces)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
