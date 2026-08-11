#!/usr/bin/env python3
"""Build a local inventory of the Documents_DRIVE mirror."""

from __future__ import annotations

from dataclasses import dataclass
import csv
import hashlib
import mimetypes
import re
import sys
from pathlib import Path

from scripts._drive_paths import documents_drive_root
from scripts._qa_common import ROOT

REPORT = ROOT / "reports" / "drive_local_inventory.csv"
SENSITIVE_NAME = re.compile(r"(élève|eleve|notes|rendus|correction.?m[ée]lang[ée]e?|\.git|\.venv)", re.I)
FIELDS = ["relative_path", "file_name", "extension", "mime_type", "sha256", "size_bytes", "sensitive"]


@dataclass(frozen=True)
class LocalDriveEntry:
    relative_path: str
    file_name: str
    extension: str
    mime_type: str
    sha256: str
    size_bytes: int
    sensitive: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_local_inventory(drive_root: Path) -> list[LocalDriveEntry]:
    if not drive_root.exists():
        return []
    entries: list[LocalDriveEntry] = []
    for path in sorted(item for item in drive_root.rglob("*") if item.is_file()):
        relative = path.relative_to(drive_root).as_posix()
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        entries.append(
            LocalDriveEntry(
                relative_path=f"Documents_DRIVE/{relative}",
                file_name=path.name,
                extension=path.suffix.lower().lstrip("."),
                mime_type=mime_type,
                sha256=sha256_file(path),
                size_bytes=path.stat().st_size,
                sensitive="oui" if SENSITIVE_NAME.search(path.as_posix()) else "non",
            )
        )
    return entries


def write_report(entries: list[LocalDriveEntry], output: Path = REPORT) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for entry in entries:
            writer.writerow(
                {
                    "relative_path": entry.relative_path,
                    "file_name": entry.file_name,
                    "extension": entry.extension,
                    "mime_type": entry.mime_type,
                    "sha256": entry.sha256,
                    "size_bytes": str(entry.size_bytes),
                    "sensitive": entry.sensitive,
                }
            )


def main() -> int:
    drive_root = documents_drive_root(ROOT)
    if not drive_root.exists():
        print(f"drive_local_inventory: KO - Documents_DRIVE introuvable: {drive_root}")
        return 1
    entries = collect_local_inventory(drive_root)
    write_report(entries)
    sensitive = sum(1 for entry in entries if entry.sensitive == "oui")
    print(f"drive_local_inventory: wrote {REPORT.relative_to(ROOT)} ({len(entries)} fichiers, {sensitive} sensibles)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
