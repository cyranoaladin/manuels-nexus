#!/usr/bin/env python3
"""Check truthful traceability for local Documents_DRIVE sources."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import re

import yaml

from scripts._qa_common import ROOT, read_frontmatter
from scripts.check_first_batch_document_quality import FIRST_BATCH_PREFIXES
from scripts._drive_paths import resolve_drive_reference

TRACE_FILE = ROOT / "support_source_trace.yml"


@dataclass
class DriveTraceResult:
    errors: list[str] = field(default_factory=list)


def support_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for prefix in FIRST_BATCH_PREFIXES:
        files.extend(sorted(root.rglob(f"{prefix}_*.md")))
    return files


def resolve_drive_path(value: str, root: Path = ROOT) -> Path | None:
    return resolve_drive_reference(value, root)


def drive_mentions(text: str) -> list[str]:
    backticked = re.findall(r"`(Documents_DRIVE/[^`]+)`", text)
    scrubbed = re.sub(r"`Documents_DRIVE/[^`]+`", "", text)
    bare = re.findall(r"(?:[A-Za-z0-9_./-]+/)?Documents_DRIVE/[^\s\"`)]+", scrubbed)
    return backticked + bare


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_trace(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = data.get("supports", []) if isinstance(data, dict) else []
    trace: dict[str, dict[str, str]] = {}
    for row in rows:
        if isinstance(row, dict) and row.get("support"):
            trace[str(row["support"])] = {str(k): "" if v is None else str(v) for k, v in row.items()}
    return trace


def analyze_drive_traceability(root: Path = ROOT, trace_path: Path = TRACE_FILE) -> DriveTraceResult:
    result = DriveTraceResult()
    trace = load_trace(trace_path)
    for path in support_files(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        metadata = read_frontmatter(path)
        source = str(metadata.get("source", ""))
        rel = str(path.relative_to(root)) if path.is_relative_to(root) else path.name
        row = trace.get(rel) or trace.get(path.name)

        if "ressource locale candidate" in source.lower() or "ressource locale candidate" in text.lower():
            result.errors.append(f"{rel}: mention interdite 'ressource locale candidate'")

        drive_values = drive_mentions(text)
        for value in drive_values:
            drive_path = resolve_drive_path(value.strip(), root)
            if drive_path is None or not drive_path.exists():
                result.errors.append(f"{rel}: chemin Documents_DRIVE inexistant -> {value}")

        if not drive_values and metadata.get("source_creation") != "generated_from_program":
            result.errors.append(f"{rel}: source_creation generated_from_program attendu")

        if row is None:
            result.errors.append(f"{rel}: absent de support_source_trace.yml")
            continue

        for key in ["source_officielle", "type_reprise", "statut_rgpd", "statut_relecture"]:
            if not row.get(key):
                result.errors.append(f"{rel}: champ trace vide -> {key}")

        drive_source = row.get("source_locale_drive", "")
        if drive_source:
            drive_path = resolve_drive_path(drive_source, root)
            if drive_path is None or not drive_path.exists():
                result.errors.append(f"{rel}: source locale Drive absente -> {drive_source}")
            if row.get("type_reprise") != "création originale" and drive_path and drive_path.is_file():
                expected_hash = row.get("hash_source", "")
                if not expected_hash:
                    result.errors.append(f"{rel}: hash_source requis pour reprise depuis Drive")
                elif expected_hash != sha256(drive_path):
                    result.errors.append(f"{rel}: hash_source incohérent")
        elif row.get("type_reprise") != "création originale":
            result.errors.append(f"{rel}: type_reprise incohérent sans source Drive")
    return result


def main() -> int:
    result = analyze_drive_traceability()
    if result.errors:
        print("check_local_drive_traceability: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print("check_local_drive_traceability: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
