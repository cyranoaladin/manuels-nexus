#!/usr/bin/env python3
"""Ingest a local Drive export into drive_quarantine without publishing it."""
from __future__ import annotations

import csv
import hashlib
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUARANTINE = ROOT / "drive_quarantine"
MANIFEST = ROOT / "drive_quarantine_manifest.csv"
SENSITIVE_NAMES = ["notes", "eleves", "élèves", "rendus", "copies"]
FIELDS = ["drive_url", "drive_folder", "file_name", "mime_type", "local_copy", "sha256", "niveau", "theme", "sequence_possible", "qualite_initiale", "decision", "raison"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decision_for(path: Path) -> tuple[str, str]:
    lowered = path.name.lower()
    if any(token in lowered for token in SENSITIVE_NAMES):
        return "reject", "nom de fichier suggérant données élèves ou copies"
    if path.suffix.lower() in {".pdf", ".tex", ".md", ".py", ".csv", ".json", ".odt", ".docx"}:
        return "refactor", "ressource à auditer en quarantaine"
    return "archive", "type non prioritaire ou à identifier"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python scripts/ingest_drive_export.py /path/to/export")
        return 2
    source = Path(sys.argv[1]).expanduser().resolve()
    if not source.exists() or not source.is_dir():
        print(f"ingest_drive_export: KO - export directory missing: {source}")
        return 1
    raw = QUARANTINE / "raw_export"
    raw.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for path in sorted(source.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(source)
        target = raw / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        decision, reason = decision_for(target)
        rows.append({"drive_url":"local_export", "drive_folder":str(source), "file_name":target.name, "mime_type":target.suffix.lower().lstrip("."), "local_copy":target.relative_to(ROOT).as_posix(), "sha256":sha256(target), "niveau":"a_determiner", "theme":"a_determiner", "sequence_possible":"a_determiner", "qualite_initiale":"non_auditee", "decision":decision, "raison":reason})
    with MANIFEST.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"ingest_drive_export: quarantined files={len(rows)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
