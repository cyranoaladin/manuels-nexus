#!/usr/bin/env python3
"""Generate an actionable plan for capacities currently absent from coverage.md."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

import yaml

from scripts._qa_common import ROOT, load_program_entries
from scripts.check_coverage_gap_action_plan import REQUIRED_COLUMNS, absent_from_coverage


PLAN = ROOT / "coverage_gap_action_plan.md"
CONTRACTS = ROOT / "03_progressions" / "supports" / "contracts"
TYPE_BY_DIAGNOSTIC = {
    "trou de contenu": "content_gap",
    "trou d'étiquetage": "tagging_gap",
    "trou d’étiquetage": "tagging_gap",
    "contenu présent mal rattaché": "misaligned_evidence",
    "différé justifié": "deferred_with_blocker",
}


def parse_existing_plan(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    header: list[str] = []
    rows: dict[str, dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cols = [col.strip() for col in line.strip().strip("|").split("|")]
        if "capacity_id" in cols:
            header = cols
            continue
        if not header or set(cols) == {"---"} or cols[0] == "---":
            continue
        if len(cols) != len(header):
            continue
        row = dict(zip(header, cols))
        if row.get("capacity_id"):
            rows[row["capacity_id"]] = row
    return rows


def load_contract_capacity_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for path in sorted(CONTRACTS.glob("*_contract.yml")):
        payload: Any = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(payload, dict):
            continue
        sequence = str(payload.get("sequence") or path.name.split("_", 1)[0])
        for cap in payload.get("capacites_officielles", []) or []:
            mapping[str(cap)] = sequence
    return mapping


def normalize_diagnostic(value: str) -> str:
    lower = value.lower()
    if "étiquet" in lower or "etiquet" in lower or "non déclar" in lower:
        return "trou d'étiquetage"
    if "mal rattach" in lower or "rattachement" in lower:
        return "contenu présent mal rattaché"
    if "diff" in lower:
        return "différé justifié"
    return "trou de contenu"


def sequence_from_capacity(capacity_id: str, entry: dict[str, Any], existing: dict[str, str], contract_map: dict[str, str]) -> str:
    if existing.get("séquence cible") and existing["séquence cible"] != "-":
        return existing["séquence cible"]
    if capacity_id in contract_map:
        return contract_map[capacity_id]
    raw = str(entry.get("sequence_cible") or "")
    match = re.search(r"\b[PT]\d{2}\b", raw)
    return match.group(0) if match else "à créer"


def contract_for_sequence(sequence: str) -> str:
    if sequence == "à créer":
        return "à créer"
    path = CONTRACTS / f"{sequence}_contract.yml"
    return path.relative_to(ROOT).as_posix() if path.exists() else "à créer"


def priority_for(diagnostic: str) -> str:
    return "haute" if diagnostic in {"trou de contenu", "contenu présent mal rattaché"} else "moyenne"


def row_for_capacity(
    capacity_id: str,
    entry: dict[str, Any],
    existing: dict[str, str],
    contract_map: dict[str, str],
) -> dict[str, str]:
    diagnostic = normalize_diagnostic(existing.get("diagnostic", ""))
    sequence = sequence_from_capacity(capacity_id, entry, existing, contract_map)
    contract = contract_for_sequence(sequence)
    official = " / ".join(str(item) for item in entry.get("capacite_attendue", []) or [])
    type_ecart = TYPE_BY_DIAGNOSTIC[diagnostic]
    action = existing.get("action suivante", "").strip()
    if not action or action.lower() in {"todo", "tbd", "à définir"}:
        action = f"ouvrir une tâche ciblée {sequence} pour combler {capacity_id} sans promotion de statut"
    resources = existing.get("ressources existantes possibles", "").strip() or (
        f"supports {sequence} à auditer" if sequence != "à créer" else "aucune ressource interne identifiée"
    )
    to_create = existing.get("ressources à créer ou corriger", "").strip() or (
        "créer ou corriger cours, pratique, correction et évaluation ciblés"
    )
    return {
        "capacity_id": capacity_id,
        "niveau": str(entry.get("level") or entry.get("niveau") or ""),
        "rubrique": str(entry.get("rubrique") or ""),
        "contenu officiel": str(entry.get("contenu") or ""),
        "capacité officielle": official,
        "statut actuel": "absent",
        "type_ecart": type_ecart,
        "diagnostic": diagnostic,
        "séquence cible": sequence,
        "ressources existantes possibles": resources,
        "ressources à créer ou corriger": to_create,
        "contrat à enrichir": contract,
        "priorité": existing.get("priorité", priority_for(diagnostic)) if existing.get("priorité") in {"haute", "moyenne", "basse"} else priority_for(diagnostic),
        "action suivante": action,
    }


def main() -> None:
    program = load_program_entries()
    existing = parse_existing_plan(PLAN)
    contract_map = load_contract_capacity_map()
    absent_ids = sorted(absent_from_coverage(ROOT / "coverage.md"))
    rows = [row_for_capacity(capacity_id, program[capacity_id], existing.get(capacity_id, {}), contract_map) for capacity_id in absent_ids]
    # Preserve pinned verification_gap rows (partial capacities tracked across PRs)
    for cap_id, ex_row in sorted(existing.items()):
        if ex_row.get("type_ecart") == "verification_gap" and cap_id not in absent_ids:
            rows.append(ex_row)
    lines = [
        "# Plan d'action des écarts de couverture",
        "",
        "Statut : plan d'action généré, pas validation. `covered` reste à 0 tant qu'aucune revue humaine conforme n'est tracée.",
        "",
        "| " + " | ".join(REQUIRED_COLUMNS) + " |",
        "| " + " | ".join("---" for _ in REQUIRED_COLUMNS) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[column] for column in REQUIRED_COLUMNS) + " |")
    PLAN.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"generate_coverage_gap_action_plan: {len(rows)} capacités absentes documentées")


if __name__ == "__main__":
    main()
