#!/usr/bin/env python3
"""Check the human review register without promoting any resource."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import csv
import re

from scripts._qa_common import ROOT


REGISTER = ROOT / "human_review_register.csv"
REQUIRED_COLUMNS = [
    "ressource",
    "niveau",
    "sequence",
    "notion",
    "reviewer",
    "date",
    "science_status",
    "pedagogy_status",
    "accessibility_status",
    "technical_status",
    "decision",
    "blockers",
]
MAJOR_TYPES = {
    "cours",
    "trace",
    "td",
    "tp",
    "corrige",
    "bareme",
    "evaluation",
    "remediation",
    "version_amenagee",
    "fiche_cours",
    "contrat",
}
REVIEW_STATUSES = {"pending", "blocked", "reviewed", "validated"}


@dataclass
class HumanReviewRegisterResult:
    errors: list[str] = field(default_factory=list)
    expected_count: int = 0
    registered_count: int = 0


def manifest_major_resources(root: Path = ROOT) -> dict[str, dict[str, str]]:
    manifest = root / "manifest.csv"
    if not manifest.exists():
        return {}
    rows: dict[str, dict[str, str]] = {}
    with manifest.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            path = row.get("chemin") or row.get("path") or ""
            if not path.startswith("03_progressions/"):
                continue
            if path.endswith("_substance_review.json"):
                continue
            if not (path.endswith(".md") or path.endswith(".json") or path.endswith(".py") or path.endswith(".yml")):
                continue
            resource_type = row.get("type", "")
            evidence_category = row.get("evidence_category", "")
            if resource_type in MAJOR_TYPES or evidence_category in MAJOR_TYPES or "fiches_cours" in path or "/supports/" in path:
                rows[path] = row
    return rows


def load_register(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        return [], [f"{path.name} absent"]
    errors: list[str] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != REQUIRED_COLUMNS:
            errors.append(f"{path.name}: colonnes invalides")
            return [], errors
        rows = list(reader)
    return rows, errors


def analyze_human_review_register(root: Path = ROOT) -> HumanReviewRegisterResult:
    result = HumanReviewRegisterResult()
    expected = manifest_major_resources(root)
    result.expected_count = len(expected)
    rows, errors = load_register(root / REGISTER.relative_to(ROOT))
    result.errors.extend(errors)
    seen: set[str] = set()

    for row in rows:
        resource = row.get("ressource", "").strip()
        result.registered_count += 1
        if not resource:
            result.errors.append("ligne registre sans ressource")
            continue
        if resource in seen:
            result.errors.append(f"{resource}: doublon dans human_review_register.csv")
        seen.add(resource)
        if resource not in expected and resource.startswith("03_progressions/"):
            result.errors.append(f"{resource}: ressource absente du manifest.csv")
        if row.get("decision", "") == "published":
            result.errors.append(f"{resource}: décision published interdite")
        statuses = [
            row.get("science_status", ""),
            row.get("pedagogy_status", ""),
            row.get("accessibility_status", ""),
            row.get("technical_status", ""),
        ]
        for status in statuses:
            if status and status not in REVIEW_STATUSES:
                result.errors.append(f"{resource}: statut de revue invalide -> {status}")
        validated = any(status in {"reviewed", "validated"} for status in statuses)
        if validated and (not row.get("reviewer") or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row.get("date", ""))):
            result.errors.append(f"{resource}: revue validée sans reviewer/date")

    missing = sorted(set(expected) - seen)
    for resource in missing[:240]:
        result.errors.append(f"{resource}: absent du human_review_register.csv")
    if len(missing) > 240:
        result.errors.append(f"{len(missing) - 240} autres ressources absentes du registre humain")
    return result


def main() -> int:
    result = analyze_human_review_register()
    print(f"Ressources majeures attendues : {result.expected_count}")
    print(f"Lignes de revue humaine : {result.registered_count}")
    if result.errors:
        print("check_human_review_register: KO")
        for error in result.errors[:260]:
            print(f"- {error}")
        return 1
    print("check_human_review_register: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
