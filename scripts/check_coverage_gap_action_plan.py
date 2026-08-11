#!/usr/bin/env python3
"""Ensure every absent programme capacity has an actionable remediation row."""

from __future__ import annotations

from pathlib import Path
import re

from scripts._qa_common import ROOT, load_program_entries, print_result


PLAN = ROOT / "coverage_gap_action_plan.md"
REQUIRED_COLUMNS = [
    "capacity_id",
    "niveau",
    "rubrique",
    "contenu officiel",
    "capacité officielle",
    "statut actuel",
    "type_ecart",
    "diagnostic",
    "séquence cible",
    "ressources existantes possibles",
    "ressources à créer ou corriger",
    "contrat à enrichir",
    "priorité",
    "action suivante",
]
DIAGNOSTICS = {"trou de contenu", "trou d’étiquetage", "trou d’étiquetage", "contenu présent mal rattaché", "différé justifié", "vérification hors périmètre"}
TYPES = {"content_gap", "tagging_gap", "misaligned_evidence", "deferred_with_blocker", "verification_gap"}
PRIORITIES = {"haute", "moyenne", "basse"}


def absent_from_coverage(path: Path) -> set[str]:
    ids: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if "| absent |" not in line:
            continue
        cols = [col.strip() for col in line.strip().strip("|").split("|")]
        if len(cols) >= 4:
            ids.add(cols[3].split(" - ", 1)[0].strip())
    return ids


def parse_plan(path: Path) -> tuple[list[str], dict[str, dict[str, str]]]:
    header: list[str] = []
    rows: dict[str, dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cols = [col.strip() for col in line.strip().strip("|").split("|")]
        if cols == REQUIRED_COLUMNS:
            header = cols
            continue
        if not header or cols[0] == "---" or set(cols) == {"---"}:
            continue
        if len(cols) != len(header):
            continue
        row = dict(zip(header, cols))
        rows[row["capacity_id"]] = row
    return header, rows


def main() -> None:
    errors: list[str] = []
    if not PLAN.exists():
        print_result("check_coverage_gap_action_plan", ["coverage_gap_action_plan.md absent"])
    header, rows = parse_plan(PLAN)
    absent_ids = absent_from_coverage(ROOT / "coverage.md")
    program = load_program_entries()
    if header != REQUIRED_COLUMNS:
        errors.append("colonnes du plan absentes ou non conformes")
    for capacity_id in sorted(absent_ids):
        row = rows.get(capacity_id)
        if row is None:
            errors.append(f"{capacity_id}: aucune ligne d'action")
            continue
        if capacity_id not in program:
            errors.append(f"{capacity_id}: absent du programme officiel YAML")
        for key in REQUIRED_COLUMNS:
            if not row.get(key) or row[key] == "-":
                errors.append(f"{capacity_id}: colonne vide -> {key}")
        expected_status = "partial" if row.get("type_ecart") == "verification_gap" else "absent"
        if row.get("statut actuel") != expected_status:
            errors.append(f"{capacity_id}: statut actuel doit être {expected_status}")
        if row.get("type_ecart") not in TYPES:
            errors.append(f"{capacity_id}: type_ecart invalide")
        if row.get("diagnostic") not in DIAGNOSTICS:
            errors.append(f"{capacity_id}: diagnostic invalide")
        if row.get("priorité") not in PRIORITIES:
            errors.append(f"{capacity_id}: priorité invalide")
        sequence = row.get("séquence cible", "")
        if sequence != "à créer" and not re.fullmatch(r"[PT]\d{2}", sequence):
            errors.append(f"{capacity_id}: séquence cible invalide")
        contract = row.get("contrat à enrichir", "")
        if contract != "à créer" and not (ROOT / contract).exists():
            errors.append(f"{capacity_id}: contrat à enrichir absent")
        action = row.get("action suivante", "")
        if not action.strip() or action.lower() in {"à définir", "todo", "tbd"}:
            errors.append(f"{capacity_id}: action suivante non actionnable")
        if any(marker in action.lower() for marker in ("todo", "tbd", "à définir")):
            errors.append(f"{capacity_id}: action suivante contient un marqueur interdit")
    for capacity_id, row in sorted(rows.items()):
        if capacity_id not in absent_ids and row.get("type_ecart") != "verification_gap" and row.get("statut actuel") != "résolu":
            errors.append(f"{capacity_id}: ligne présente alors que la capacité n'est plus absent")
    print_result("check_coverage_gap_action_plan", errors)


if __name__ == "__main__":
    main()
