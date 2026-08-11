#!/usr/bin/env python3
"""Check that remaining Drive work is actionable and release-scoped."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import csv

from scripts._qa_common import ROOT


PLAN = "drive_remaining_action_plan.md"
REQUIRED_COLUMNS = {
    "Ressource",
    "Décision actuelle",
    "Indispensable",
    "Impact P/T",
    "Action",
    "RGPD",
    "Statut release",
    "Responsable",
    "Priorité",
    "Date cible",
}
OPEN_DECISIONS = {"missing_local_copy", "deferred", "rejected_sensitive", "quarantined"}


@dataclass
class DriveActionPlanResult:
    errors: list[str] = field(default_factory=list)
    expected: set[str] = field(default_factory=set)
    rows: dict[str, dict[str, str]] = field(default_factory=dict)


def unsold_drive_resources(root: Path) -> set[str]:
    path = root / "drive_inventory.csv"
    if not path.exists():
        return set()
    resources: set[str] = set()
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("decision", "") in OPEN_DECISIONS:
                resources.add((row.get("name") or row.get("file_name") or row.get("Ressource") or "").strip())
    return {resource for resource in resources if resource}


def parse_markdown_table(text: str) -> tuple[list[str], list[dict[str, str]]]:
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return [], []
    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        values = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        if len(values) != len(headers):
            continue
        rows.append(dict(zip(headers, values)))
    return headers, rows


def analyze_drive_action_plan(root: Path = ROOT) -> DriveActionPlanResult:
    result = DriveActionPlanResult(expected=unsold_drive_resources(root))
    path = root / PLAN
    if not path.exists():
        result.errors.append(f"{PLAN} absent")
        return result
    headers, rows = parse_markdown_table(path.read_text(encoding="utf-8", errors="replace"))
    missing_columns = sorted(REQUIRED_COLUMNS - set(headers))
    for column in missing_columns:
        result.errors.append(f"colonne obligatoire absente -> {column.lower()}")
    for row in rows:
        resource = row.get("Ressource", "").strip("`")
        if resource:
            result.rows[resource] = row
        for column in REQUIRED_COLUMNS:
            if column in headers and not row.get(column, "").strip():
                result.errors.append(f"{resource}: champ obligatoire vide -> {column.lower()}")
    for resource in sorted(result.expected - set(result.rows)):
        result.errors.append(f"{resource}: absent du plan d'action Drive")
    for resource, row in result.rows.items():
        if row.get("Décision actuelle", "") in OPEN_DECISIONS:
            if row.get("Statut release", "") != "NON_RELEASE_READY":
                result.errors.append(f"{resource}: statut release doit rester NON_RELEASE_READY")
            if row.get("RGPD", "").lower() in {"", "ok", "validé", "valide"} and row.get("Décision actuelle") == "rejected_sensitive":
                result.errors.append(f"{resource}: RGPD incohérent avec rejected_sensitive")
    return result


def main() -> int:
    result = analyze_drive_action_plan()
    print(f"Ressources Drive non soldées attendues : {len(result.expected)}")
    print(f"Lignes plan Drive : {len(result.rows)}")
    if result.errors:
        print("check_drive_action_plan_completeness: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print("check_drive_action_plan_completeness: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
