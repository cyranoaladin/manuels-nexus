#!/usr/bin/env python3
"""Contrôle des rapports de substance rendus."""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts._qa_common import print_result
from scripts.substance_report_renderer import NON_VALIDATION_BANNER, REPORT_META_TAG


def check_reports_dir(reports_dir: Path) -> list[str]:
    errors: list[str] = []
    if not reports_dir.exists():
        return [f"dossier absent: {reports_dir}"]

    html_files = sorted(reports_dir.glob("*.html"))
    if not html_files:
        errors.append(f"aucun rapport HTML dans {reports_dir}")
    for html_path in html_files:
        text = html_path.read_text(encoding="utf-8", errors="replace")
        md_path = html_path.with_suffix(".md")
        if not md_path.exists():
            errors.append(f"{html_path.name}: Markdown associé absent")
        if REPORT_META_TAG not in text:
            errors.append(f"{html_path.name}: meta-tag de charte absent")
        if NON_VALIDATION_BANNER not in text:
            errors.append(f"{html_path.name}: bandeau de non-validation absent")
        if "<script src=" in text:
            errors.append(f"{html_path.name}: script externe interdit")
        if '<link rel="stylesheet"' in text:
            errors.append(f"{html_path.name}: feuille de style externe interdite")
        if "validated_pedagogy" in text and "Verdict déclaré: validated_pedagogy" not in text:
            errors.append(f"{html_path.name}: statut validé affiché hors verdict déclaré")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Vérifier les rapports de substance rendus")
    parser.add_argument("--reports-dir", type=Path, default=Path("01_build_reports/substance_reports"))
    args = parser.parse_args()
    print_result("check_substance_report_artifacts", check_reports_dir(args.reports_dir))


if __name__ == "__main__":
    main()
