#!/usr/bin/env python3
"""Check qa_report.md reflects current manifest and coverage counts."""
from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "qa_report.md"
MANIFEST = ROOT / "manifest.csv"
COVERAGE = ROOT / "coverage.md"
DRIVE_INVENTORY = ROOT / "drive_inventory.csv"


def manifest_counts() -> tuple[int, Counter[str], Counter[str], int]:
    statuses: Counter[str] = Counter()
    sources: Counter[str] = Counter()
    publishable = 0
    total = 0
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            total += 1
            statuses[row.get("statut", "")] += 1
            sources[row.get("source", "")] += 1
            if row.get("publishable") == "oui":
                publishable += 1
    return total, statuses, sources, publishable


def coverage_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for line in COVERAGE.read_text(encoding="utf-8").splitlines():
        match = re.match(r"- (covered|needs_review|partial|absent|Total capacités) : ([0-9]+)", line)
        if match:
            counts[match.group(1)] = int(match.group(2))
    return counts


def drive_count() -> int:
    if not DRIVE_INVENTORY.exists():
        return 0
    with DRIVE_INVENTORY.open(encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    if not REPORT.exists():
        errors.append("qa_report.md absent")
        print_result(errors)
        return 1
    text = REPORT.read_text(encoding="utf-8")
    total, statuses, sources, publishable = manifest_counts()
    cov = coverage_counts()
    expected = {
        "Ressources inventoriées": total,
        "Ressources needs_review": statuses.get("needs_review", 0),
        "Ressources publiables": publishable,
        "Source generated": sources.get("generated", 0),
        "Source drive": sources.get("drive", 0),
        "Lignes drive_inventory.csv": drive_count(),
        "Couverture covered": cov.get("covered", 0),
        "Couverture needs_review": cov.get("needs_review", 0),
        "Couverture partial": cov.get("partial", 0),
        "Couverture absent": cov.get("absent", 0),
    }
    for label, value in expected.items():
        if f"- {label} : {value}" not in text:
            errors.append(f"qa_report mismatch for {label}: expected {value}")
    if "NON PUBLIABLE" not in text:
        errors.append("qa_report missing NON PUBLIABLE status")
    if errors:
        print_result(errors)
        return 1
    print("check_qa_report_freshness: PASS")
    return 0


def print_result(errors: list[str]) -> None:
    print("check_qa_report_freshness: KO")
    for error in errors:
        print(f"- {error}")


if __name__ == "__main__":
    sys.exit(main())
