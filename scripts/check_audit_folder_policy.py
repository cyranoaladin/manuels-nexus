#!/usr/bin/env python3
"""Verify that the external AUDIT folder guides QA without entering the corpus."""

from __future__ import annotations

from pathlib import Path
import tarfile
import zipfile

from scripts._qa_common import ROOT, print_result


AUDIT_CANDIDATES = [ROOT / "AUDIT", ROOT.parent / "AUDIT"]
TEXT_REPORTS = [
    ROOT / "manifest.csv",
    ROOT / "coverage.md",
    ROOT / "coverage_sources.md",
    ROOT / "programme_matrix_premiere.md",
    ROOT / "programme_matrix_terminale.md",
]
STUDENT_EXPORT_PATTERNS = ["*_eleve.pdf", "*_eleve.html", "*version_eleve.pdf", "*version_eleve.html"]


def audit_dirs() -> list[Path]:
    return [path for path in AUDIT_CANDIDATES if path.exists() and path.is_dir()]


def archive_contains_audit(path: Path) -> bool:
    try:
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as archive:
                return any("/AUDIT/" in name or name.startswith("AUDIT/") for name in archive.namelist())
        if path.suffix in {".gz", ".tgz", ".tar"} or path.name.endswith(".tar.gz"):
            with tarfile.open(path) as archive:
                return any("/AUDIT/" in member.name or member.name.startswith("AUDIT/") for member in archive.getmembers())
    except Exception:
        return False
    return False


def main() -> None:
    errors: list[str] = []
    found = audit_dirs()
    if found:
        print("Dossier /AUDIT détecté : " + ", ".join(path.as_posix() for path in found))
    else:
        print("Dossier /AUDIT absent : politique vérifiée en mode portable.")

    for report in TEXT_REPORTS:
        if not report.exists():
            continue
        text = report.read_text(encoding="utf-8", errors="replace")
        if "/AUDIT" in text or "AUDIT/" in text:
            errors.append(f"{report.relative_to(ROOT)} référence /AUDIT comme corpus ou preuve")

    for pattern in STUDENT_EXPORT_PATTERNS:
        for path in ROOT.rglob(pattern):
            if "dist" not in path.parts and "rendered_units" not in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore") if path.suffix == ".html" else ""
            if "/AUDIT" in text or "AUDIT/" in text:
                errors.append(f"{path.relative_to(ROOT)} expose /AUDIT dans une version élève")

    for archive in [ROOT / "dist" / "source_clean.tar.gz", ROOT / "dist" / "nsi-enseignement_source_clean.zip"]:
        if archive.exists() and archive_contains_audit(archive):
            errors.append(f"{archive.relative_to(ROOT)} contient AUDIT ; décision non documentée")

    if not errors:
        print("AUDIT hors corpus pédagogique, hors coverage.md et hors livrables élèves.")
    print_result("check_audit_folder_policy", errors)


if __name__ == "__main__":
    main()
