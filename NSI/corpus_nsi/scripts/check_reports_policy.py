#!/usr/bin/env python3
"""Validate that reports/lot* remain non-pedagogical validation logs."""

from __future__ import annotations

import csv
from pathlib import Path


from scripts._qa_common import ROOT, print_result


MAX_REPORTS_BYTES = 2 * 1024 * 1024
FORBIDDEN_NAMES = {".env", ".env.rag", ".env.local", "NotesEleves.csv", "Fichier_Eleves.csv", "id_rsa"}
SECRET_MARKERS = ("RAG_API_KEY=", "Authorization: Bearer ", "BEGIN PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY")


def lot_report_files() -> list[Path]:
    reports = ROOT / "reports"
    if not reports.exists():
        return []
    files: list[Path] = []
    for path in sorted(reports.glob("lot*")):
        if path.is_dir():
            files.extend(item for item in path.rglob("*") if item.is_file())
    return files


def main() -> None:
    errors: list[str] = []
    policy = ROOT / "reports_policy.md"
    if not policy.exists():
        errors.append("reports_policy.md absent")
    files = lot_report_files()
    total_size = sum(path.stat().st_size for path in files)
    if total_size > MAX_REPORTS_BYTES:
        errors.append(f"reports/lot*/ dépasse 2 Mo ({total_size} octets)")
    manifest_rows: list[dict[str, str]] = []
    with (ROOT / "manifest.csv").open(encoding="utf-8", newline="") as handle:
        manifest_rows = list(csv.DictReader(handle))
    coverage = (ROOT / "coverage.md").read_text(encoding="utf-8", errors="replace") if (ROOT / "coverage.md").exists() else ""
    sources = (ROOT / "coverage_sources.md").read_text(encoding="utf-8", errors="replace") if (ROOT / "coverage_sources.md").exists() else ""
    rag_config = (ROOT / "rag_config.example.yml").read_text(encoding="utf-8", errors="replace") if (ROOT / "rag_config.example.yml").exists() else ""
    for marker in ("reports/lot1/", "reports/lot2/", "reports/lot3/"):
        for row in manifest_rows:
            if not row.get("chemin", "").startswith(marker):
                continue
            if row.get("niveau") != "interne" or row.get("publishable") != "non" or row.get("evidence_category") != "autre":
                errors.append(f"{row.get('chemin')}: classification pédagogique interdite dans le manifest")
        if marker in coverage or marker in sources:
            errors.append(f"{marker}: ne doit pas être preuve de couverture")
        if marker in rag_config:
            errors.append(f"{marker}: ne doit pas être source RAG")
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if path.name in FORBIDDEN_NAMES or path.suffix == ".env":
            errors.append(f"{rel}: fichier sensible interdit")
        text = path.read_text(encoding="utf-8", errors="replace")
        for marker in SECRET_MARKERS:
            if marker in text:
                errors.append(f"{rel}: marqueur secret interdit")
                break
    print_result("check_reports_policy", errors)


if __name__ == "__main__":
    main()
