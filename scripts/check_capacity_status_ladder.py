#!/usr/bin/env python3
"""Separate documentary progression from human-reviewed and covered status."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import csv
import re

from scripts._qa_common import ROOT, sequence_id_from_path
from scripts.check_official_program_capacity_coverage_matrix import load_official_capacities
from scripts.check_session_referenced_files_exist import describe_session, session_blocks


CAPACITY_RE = re.compile(r"\b[PT](?:-[A-Z]+)+-\d{2}[A-Z]?\b")
VALIDATED_RE = re.compile(r"validated_|published|covered", re.I)


@dataclass
class CapacityLadderResult:
    rows: dict[str, dict[str, str]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def docs(root: Path) -> list[Path]:
    return sorted((root / "03_progressions").rglob("*.md"))


def contains_capacity(paths: list[Path], capacity_id: str) -> list[Path]:
    return [path for path in paths if capacity_id in path.read_text(encoding="utf-8", errors="replace")]


def sequence_ids(paths: list[Path]) -> set[str]:
    return {sequence for path in paths if (sequence := sequence_id_from_path(path))}


def files_in_sequences(paths: list[Path], sequences: set[str]) -> list[Path]:
    return [path for path in paths if sequence_id_from_path(path) in sequences]


def linked_session_exists(root: Path, capacity_id: str, sequences: set[str]) -> bool:
    for session_path in [
        root / "03_progressions" / "seances_premiere.md",
        root / "03_progressions" / "seances_terminale.md",
    ]:
        if not session_path.exists():
            continue
        for session_id, block in session_blocks(session_path):
            prefix = session_id.split("-", 1)[0]
            if prefix not in sequences and capacity_id not in block:
                continue
            info = describe_session(root, session_id, block)
            if info.existing_specific_refs and not info.theoretical:
                return True
    return False


def manifest_status_errors(root: Path) -> list[str]:
    manifest = root / "manifest.csv"
    if not manifest.exists():
        return []
    errors: list[str] = []
    with manifest.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            status = " ".join(str(row.get(key, "")) for key in ("statut", "status", "coverage", "publication"))
            if VALIDATED_RE.search(status):
                errors.append(f"statut interdit dans manifest.csv: {row.get('path') or row.get('fichier') or row}")
    return errors


def analyze_capacity_status_ladder(root: Path = ROOT) -> CapacityLadderResult:
    result = CapacityLadderResult()
    all_docs = docs(root)
    sheet_or_course = [path for path in all_docs if "_fiche_cours_" in path.name or "_cours_" in path.name]
    practice = [path for path in all_docs if re.search(r"_(?:TD|td|TP|tp)_", path.name)]
    assessments = [path for path in all_docs if "evaluation" in path.name.lower()]

    for entry in load_official_capacities(root):
        capacity_id = entry["id"]
        documented_hits = contains_capacity(sheet_or_course, capacity_id)
        practice_hits = contains_capacity(practice, capacity_id)
        assessment_hits = contains_capacity(assessments, capacity_id)
        sequences = sequence_ids(documented_hits + practice_hits + assessment_hits)
        if documented_hits and not practice_hits:
            practice_hits = files_in_sequences(practice, sequences)
        if documented_hits and not assessment_hits:
            assessment_hits = files_in_sequences(assessments, sequences)

        documented = bool(documented_hits)
        practiced = bool(practice_hits)
        assessed = bool(assessment_hits)
        linked_to_session = linked_session_exists(root, capacity_id, sequences)
        status = "documentary_ready" if documented and practiced and assessed else "incomplete_documentary"
        row = {
            "niveau": entry["niveau"],
            "thème officiel": entry["theme"],
            "documented": "oui" if documented else "non",
            "practiced": "oui" if practiced else "non",
            "assessed": "oui" if assessed else "non",
            "linked_to_session": "oui" if linked_to_session else "non",
            "reviewed_pedagogy": "non",
            "reviewed_science": "non",
            "covered": "non",
            "statut": status,
        }
        result.rows[capacity_id] = row
        if not documented:
            result.errors.append(f"{capacity_id}: documented=non")
        if documented and not practiced:
            result.errors.append(f"{capacity_id}: practiced=non")
        if documented and not assessed:
            result.errors.append(f"{capacity_id}: assessed=non")

    result.errors.extend(manifest_status_errors(root))
    return result


def main() -> int:
    result = analyze_capacity_status_ladder()
    print("| capacité | documented | practiced | assessed | linked_to_session | reviewed_pedagogy | reviewed_science | covered | statut |")
    print("|---|---|---|---|---|---|---|---|---|")
    for capacity_id, row in sorted(result.rows.items()):
        print(
            "| "
            + " | ".join(
                [
                    capacity_id,
                    row["documented"],
                    row["practiced"],
                    row["assessed"],
                    row["linked_to_session"],
                    row["reviewed_pedagogy"],
                    row["reviewed_science"],
                    row["covered"],
                    row["statut"],
                ]
            )
            + " |"
        )
    if result.errors:
        print("check_capacity_status_ladder: KO")
        for error in result.errors[:240]:
            print(f"- {error}")
        return 1
    print(f"check_capacity_status_ladder: PASS ({len(result.rows)} capacités, covered=non)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
