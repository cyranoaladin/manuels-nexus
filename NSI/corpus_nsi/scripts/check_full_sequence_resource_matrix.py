#!/usr/bin/env python3
"""Build and verify the full resource matrix for P00-P14 and T00-T19."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import FULL_SEQUENCE_CURRENT_LOT, FULL_SEQUENCE_SCOPE, ROOT


REQUIRED_TYPES = [
    "fiche",
    "cours",
    "trace",
    "td",
    "tp",
    "corrige",
    "bareme",
    "evaluation",
    "remediation",
    "version_amenagee",
    "contrat",
]
CURRENT_LOT_REQUIRED = set(FULL_SEQUENCE_CURRENT_LOT["premiere"]) | set(FULL_SEQUENCE_CURRENT_LOT["terminale"])


@dataclass
class MatrixResult:
    errors: list[str] = field(default_factory=list)
    matrix: dict[str, dict[str, str]] = field(default_factory=dict)
    registered_missing: set[tuple[str, str]] = field(default_factory=set)
    counts: dict[str, int] = field(
        default_factory=lambda: {
            "produced": 0,
            "missing_registered": 0,
            "missing_unregistered": 0,
        }
    )
    completeness_percent: float = 0.0


def all_sequences() -> list[str]:
    return list(FULL_SEQUENCE_SCOPE["premiere"]) + list(FULL_SEQUENCE_SCOPE["terminale"])


def level_for(sequence: str) -> str:
    return "premiere" if sequence.startswith("P") else "terminale"


def support_dir(root: Path, sequence: str) -> Path:
    return root / "03_progressions" / "supports" / level_for(sequence) / sequence


def sheet_dir(root: Path, sequence: str) -> Path:
    return root / "03_progressions" / "fiches_cours" / level_for(sequence) / sequence


def has_type(root: Path, sequence: str, resource_type: str) -> bool:
    if resource_type == "fiche":
        base = sheet_dir(root, sequence)
        return base.exists() and any(base.glob(f"{sequence}_fiche_cours_*.md"))
    if resource_type == "contrat":
        return (root / "03_progressions" / "supports" / "contracts" / f"{sequence}_contract.yml").exists()
    base = support_dir(root, sequence)
    if not base.exists():
        return False
    patterns = {
        "cours": ["cours"],
        "trace": ["trace"],
        "td": ["td", "TD"],
        "tp": ["tp", "TP"],
        "corrige": ["corrige", "corrigé"],
        "bareme": ["bareme", "barème"],
        "evaluation": ["evaluation", "évaluation"],
        "remediation": ["remediation", "remédiation"],
        "version_amenagee": ["version_amenagee", "version_aménagée"],
    }[resource_type]
    for path in base.glob(f"{sequence}_*.md"):
        lower = path.name.lower()
        if any(pattern.lower() in lower for pattern in patterns):
            return True
    return False


def parse_register(root: Path) -> set[tuple[str, str]]:
    register = root / "missing_sequence_resources_register.md"
    registered: set[tuple[str, str]] = set()
    if not register.exists():
        return registered
    for line in register.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 10 or cells[0].lower() == "niveau":
            continue
        sequence = cells[1]
        resource_type = cells[3]
        date_target = cells[7]
        owner = cells[8]
        blocked = cells[9]
        if not re.fullmatch(r"[PT]\d{2}", sequence):
            continue
        if not date_target or "définir" in date_target.lower():
            continue
        if not owner:
            continue
        if "oui" not in blocked.lower():
            continue
        registered.add((sequence, resource_type))
    return registered


def analyze_full_sequence_resource_matrix(
    root: Path = ROOT,
    sequences: list[str] | None = None,
) -> MatrixResult:
    result = MatrixResult(registered_missing=parse_register(root))
    seqs = sequences or all_sequences()
    for sequence in seqs:
        row: dict[str, str] = {}
        for resource_type in REQUIRED_TYPES:
            present = has_type(root, sequence, resource_type)
            if present:
                row[resource_type] = "produced"
                result.counts["produced"] += 1
                continue
            if (sequence, resource_type) in result.registered_missing:
                row[resource_type] = "missing_registered"
                result.counts["missing_registered"] += 1
                result.errors.append(f"{sequence}: ressource manquante enregistrée mais non produite -> {resource_type}")
                continue
            row[resource_type] = "missing_unregistered"
            result.counts["missing_unregistered"] += 1
            result.errors.append(f"{sequence}: ressource manquante non enregistrée -> {resource_type}")
        result.matrix[sequence] = row
    total = len(seqs) * len(REQUIRED_TYPES)
    result.completeness_percent = (result.counts["produced"] / total * 100.0) if total else 100.0
    return result


def format_matrix(result: MatrixResult) -> str:
    header = "| séquence | " + " | ".join(REQUIRED_TYPES) + " |"
    sep = "|---" * (len(REQUIRED_TYPES) + 1) + "|"
    lines = [header, sep]
    for sequence, row in result.matrix.items():
        values = [row.get(kind, "missing_unregistered") for kind in REQUIRED_TYPES]
        lines.append("| " + sequence + " | " + " | ".join(values) + " |")
    return "\n".join(lines)


def main() -> int:
    result = analyze_full_sequence_resource_matrix()
    print(format_matrix(result))
    total = sum(result.counts.values())
    print(
        "Ressources produites: "
        f"{result.counts['produced']}/{total} "
        f"({result.completeness_percent:.1f}%)"
    )
    print(f"Ressources manquantes enregistrées: {result.counts['missing_registered']}")
    print(f"Ressources manquantes non enregistrées: {result.counts['missing_unregistered']}")
    if result.errors:
        print("check_full_sequence_resource_matrix: KO")
        for error in result.errors[:180]:
            print(f"- {error}")
        return 1
    print(
        "check_full_sequence_resource_matrix: PASS "
        f"({len(result.matrix)} séquences, complétude réelle {result.completeness_percent:.1f}%)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
