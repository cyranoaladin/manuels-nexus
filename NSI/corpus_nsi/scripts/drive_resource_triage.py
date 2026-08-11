#!/usr/bin/env python3
"""Cross drive_inventory.csv with the local Documents_DRIVE mirror."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

from scripts._drive_paths import documents_drive_root
from scripts._qa_common import ROOT
from scripts.drive_local_inventory import sha256_file

INVENTORY = ROOT / "drive_inventory.csv"
MISSING = "NA_REMOTE_NOT_DOWNLOADED"
SENSITIVE_NAME = re.compile(r"(notes?[_ -]?eleves?|fichier[_ -]?eleves?|rendus?[_ -]?eleves?|\.git|\.venv)", re.I)


def local_reference(path: Path, drive_root: Path) -> str:
    return "Documents_DRIVE/" + path.relative_to(drive_root).as_posix()


def exact_matches(drive_root: Path, file_name: str) -> list[Path]:
    if not drive_root.exists():
        return []
    return sorted(path for path in drive_root.rglob("*") if path.name == file_name)


def update_row(row: dict[str, str], drive_root: Path) -> dict[str, str]:
    updated = dict(row)
    name = updated.get("file_name", "")
    matches = exact_matches(drive_root, name)
    sensitive = bool(SENSITIVE_NAME.search(name) or updated.get("theme") == "donnees_eleves")

    if sensitive:
        updated["decision"] = "rejected_sensitive"
        updated["qualite_initiale"] = "non_publiable"
        updated["raison"] = "Ressource sensible ou technique exclue de toute intégration pédagogique."
        if len(matches) == 1 and matches[0].is_file():
            updated["local_copy"] = local_reference(matches[0], drive_root)
            updated["sha256"] = sha256_file(matches[0])
        else:
            updated["local_copy"] = MISSING
            updated["sha256"] = MISSING
        return updated

    if not matches:
        updated["decision"] = "missing_local_copy"
        updated["local_copy"] = MISSING
        updated["sha256"] = MISSING
        updated["raison"] = "Copie locale absente dans Documents_DRIVE ; contenu non inventé."
        return updated

    if len(matches) > 1:
        updated["decision"] = "deferred"
        updated["local_copy"] = MISSING
        updated["sha256"] = MISSING
        updated["raison"] = "Plusieurs copies locales homonymes ; sélection pédagogique manuelle requise."
        return updated

    match = matches[0]
    updated["local_copy"] = local_reference(match, drive_root)
    updated["sha256"] = sha256_file(match) if match.is_file() else MISSING
    updated["decision"] = "deferred"
    updated["raison"] = "copie locale trouvée ; audit pédagogique et RGPD requis avant reprise."
    return updated


def triage_inventory(root: Path = ROOT, write: bool = False) -> list[dict[str, str]]:
    inventory = root / "drive_inventory.csv"
    drive_root = documents_drive_root(root)
    with inventory.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = [update_row({key: value or "" for key, value in row.items()}, drive_root) for row in reader]

    if write:
        with inventory.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="mettre à jour drive_inventory.csv")
    args = parser.parse_args()
    rows = triage_inventory(ROOT, write=args.write)
    decisions: dict[str, int] = {}
    for row in rows:
        decisions[row["decision"]] = decisions.get(row["decision"], 0) + 1
    mode = "updated" if args.write else "dry-run"
    print(f"drive_resource_triage: {mode} {len(rows)} rows {decisions}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
