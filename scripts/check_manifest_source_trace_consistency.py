#!/usr/bin/env python3
"""Check that manifest.csv agrees with support_source_trace.yml."""

from __future__ import annotations

from dataclasses import dataclass, field
import csv
import sys
from pathlib import Path

import yaml

from scripts._qa_common import ROOT

TRACE_TO_MANIFEST = {
    "adaptation_drive": "adapted_from_drive",
    "adapted_from_drive": "adapted_from_drive",
    "adaptation": "adapted_from_drive",
    "import_partiel": "import_partiel",
    "inspiration_drive": "inspiration_drive",
    "inspiration_only": "inspiration_drive",
    "création originale": "generated",
}


@dataclass
class ManifestSourceTraceResult:
    errors: list[str] = field(default_factory=list)


def load_manifest(root: Path) -> dict[str, dict[str, str]]:
    path = root / "manifest.csv"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as handle:
        return {row.get("chemin", ""): row for row in csv.DictReader(handle)}


def load_trace(root: Path) -> list[dict[str, str]]:
    path = root / "support_source_trace.yml"
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = data.get("supports", []) if isinstance(data, dict) else []
    return [
        {str(key): "" if value is None else str(value).strip() for key, value in row.items()}
        for row in rows
        if isinstance(row, dict)
    ]


def analyze_manifest_source_trace_consistency(root: Path = ROOT) -> ManifestSourceTraceResult:
    result = ManifestSourceTraceResult()
    manifest = load_manifest(root)
    trace_rows = load_trace(root)
    if not manifest:
        result.errors.append("manifest.csv absent ou vide")
    if not trace_rows:
        result.errors.append("support_source_trace.yml absent ou vide")
    if result.errors:
        return result

    for row in trace_rows:
        support = row.get("support", "")
        reuse = row.get("type_reprise", "")
        expected = TRACE_TO_MANIFEST.get(reuse)
        if not support or expected is None:
            continue
        manifest_row = manifest.get(support)
        if manifest_row is None:
            if (root / support).exists():
                result.errors.append(f"{support}: absent du manifest.csv")
            continue
        actual = manifest_row.get("source", "")
        if actual != expected:
            result.errors.append(f"{support}: source manifest {actual!r} incohérente avec {reuse} -> {expected}")

    for support, row in manifest.items():
        if row.get("source") == "generated" and (root / support).exists():
            path = root / support
            parts = Path(support).parts
            if not parts or parts[0] not in {"03_progressions", "premiere", "terminale"}:
                continue
            if path.is_file() and path.suffix in {".md", ".csv", ".py", ".yml", ".yaml"}:
                text = path.read_text(encoding="utf-8", errors="replace")
                if "Documents_DRIVE/" in text:
                    result.errors.append(f"{support}: source generated mentionne Documents_DRIVE")
    return result


def main() -> int:
    result = analyze_manifest_source_trace_consistency()
    if result.errors:
        print("check_manifest_source_trace_consistency: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print("check_manifest_source_trace_consistency: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
