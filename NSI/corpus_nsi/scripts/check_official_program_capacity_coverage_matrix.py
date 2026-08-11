#!/usr/bin/env python3
"""Build a documentary matrix for official programme capacities."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
import yaml

from scripts._qa_common import PROGRAM_FILE, ROOT


CAPACITY_RE = re.compile(r"\b[PT](?:-[A-Z]+)+-\d{2}[A-Z]?\b")
SEQUENCE_RE = re.compile(r"^([PT]\d{2})(?:_|$)")


@dataclass
class CapacityCoverageResult:
    errors: list[str] = field(default_factory=list)
    rows: list[dict[str, str]] = field(default_factory=list)


def load_official_capacities(root: Path = ROOT) -> list[dict[str, str]]:
    program_file = root / PROGRAM_FILE.relative_to(ROOT)
    data = yaml.safe_load(program_file.read_text(encoding="utf-8")) or {}
    rows: list[dict[str, str]] = []
    for level, entries in (data.get("programmes") or {}).items():
        for entry in entries or []:
            if not isinstance(entry, dict) or not entry.get("id"):
                continue
            rows.append(
                {
                    "id": str(entry["id"]),
                    "niveau": str(entry.get("niveau") or level),
                    "theme": str(entry.get("rubrique") or entry.get("theme") or ""),
                }
            )
    return rows


def files_containing(root: Path, capacity_id: str, paths: list[Path]) -> list[Path]:
    result: list[Path] = []
    for path in paths:
        if capacity_id in path.read_text(encoding="utf-8", errors="replace"):
            result.append(path)
    return result


def sequence_id_from_name(path: Path) -> str | None:
    match = SEQUENCE_RE.search(path.name)
    return match.group(1) if match else None


def analyze_official_program_capacity_coverage_matrix(root: Path = ROOT) -> CapacityCoverageResult:
    result = CapacityCoverageResult()
    docs = sorted((root / "03_progressions").rglob("*.md"))
    sheets = [path for path in docs if "_fiche_cours_" in path.name]
    supports = [
        path
        for path in docs
        if any(token in path.name.lower() for token in ["_td_", "_tp_", "_trace_", "_cours_"])
    ]
    evaluations = [path for path in docs if "evaluation" in path.name.lower()]
    all_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in docs)
    used_capacities = set(CAPACITY_RE.findall(all_text))
    official_ids = {row["id"] for row in load_official_capacities(root)}

    for invented in sorted(used_capacities - official_ids):
        result.errors.append(f"capacité inventée ou absente du YAML officiel: {invented}")

    for row in load_official_capacities(root):
        capacity_id = row["id"]
        sheet_hits = files_containing(root, capacity_id, sheets)
        support_hits = files_containing(root, capacity_id, supports)
        eval_hits = files_containing(root, capacity_id, evaluations)
        if not eval_hits:
            sequences = {seq for path in sheet_hits + support_hits if (seq := sequence_id_from_name(path))}
            eval_hits = [path for path in evaluations if sequence_id_from_name(path) in sequences]
        row_sequences = {
            seq
            for path in sheet_hits + support_hits + eval_hits
            if (seq := sequence_id_from_name(path))
        }
        matrix_row = {
            "niveau": row["niveau"],
            "thème officiel": row["theme"],
            "capacité officielle": capacity_id,
            "séquences": ", ".join(sorted(row_sequences)),
            "fiches": str(len(sheet_hits)),
            "supports": str(len(support_hits)),
            "évaluations": str(len(eval_hits)),
            "statut": "documented" if sheet_hits and support_hits and eval_hits else "incomplete",
        }
        result.rows.append(matrix_row)
        if not sheet_hits:
            result.errors.append(f"{capacity_id}: aucune fiche associée")
        if not support_hits:
            result.errors.append(f"{capacity_id}: aucun TD/TP/cours/trace associé")
        if not eval_hits:
            result.errors.append(f"{capacity_id}: aucune évaluation associée")
    return result


def format_matrix(result: CapacityCoverageResult) -> str:
    headers = ["niveau", "thème officiel", "capacité officielle", "séquences", "fiches", "supports", "évaluations", "statut"]
    lines = ["| " + " | ".join(headers) + " |", "|---" * len(headers) + "|"]
    for row in result.rows:
        lines.append("| " + " | ".join(row.get(header, "") for header in headers) + " |")
    return "\n".join(lines)


def main() -> int:
    result = analyze_official_program_capacity_coverage_matrix()
    print(format_matrix(result))
    if result.errors:
        print("check_official_program_capacity_coverage_matrix: KO")
        for error in result.errors[:260]:
            print(f"- {error}")
        return 1
    print(f"check_official_program_capacity_coverage_matrix: PASS ({len(result.rows)} capacités)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
