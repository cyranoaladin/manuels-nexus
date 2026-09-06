#!/usr/bin/env python3
"""Pourquoi quatre dimensions de certification restent `not_covered`.

Le contrat (docs/superpowers/specs/2026-07-22-phase-0-1-collection-audit-design.md)
expose sept dimensions et exige, pour `publication_eligible`, que **les sept**
soient `passed`. Il ajoute : « Une dimension non vérifiée reste explicitement
`not_covered`, jamais implicitement verte. »

Or `_release_strict_gate` n'assigne que `structure`, `execution` et `pedagogy`.
`mathematics`, `print`, `regulation` et `visual` conservent la valeur par défaut
de `GATE_DIMENSION_TEMPLATE` et sont émises telles quelles comme
`dimension_non_couverte:`.

Ce n'est donc pas une valeur à basculer : ce sont quatre dimensions **sans
aucun producteur**. `release-strict` est aujourd'hui insatisfiable par
construction, et il a raison de l'être — il refuse de prétendre couvrir ce que
personne ne mesure. Ce producteur constate la situation ; il ne la déguise pas.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GATE_SOURCE = ROOT / "scripts/inventory_collection.py"
CONTRACT = "docs/superpowers/specs/2026-07-22-phase-0-1-collection-audit-design.md"
OUTPUT_JSON = ROOT / "audit/CERTIFICATION_DIMENSION_COVERAGE.json"
OUTPUT_MD = ROOT / "audit/CERTIFICATION_DIMENSION_COVERAGE.md"

REQUIRED_EVIDENCE = {
    "mathematics": {
        "required_evidence": "Audit scientifique indépendant du contenu mathématique imprimé",
        "raw_inputs": "énoncés, corrigés, barèmes et figures des six manuels",
        "candidate_producer": "scripts/audit_mathematical_correctness.py (inexistant)",
    },
    "print": {
        "required_evidence": "Preflight des PDF lié au HEAD de release",
        "raw_inputs": "les 12 PDF produits par le build canonique",
        "candidate_producer": "scripts/build_final_preflight_and_regression.py (non branché sur le gate)",
    },
    "regulation": {
        "required_evidence": "Couverture des programmes officiels, année applicable",
        "raw_inputs": "référentiels BO, capacités déclarées, inventaire",
        "candidate_producer": "scripts/build_official_program_coverage.py (non branché sur la dimension)",
    },
    "visual": {
        "required_evidence": "Inspection ou mesure visuelle réelle des PDF rendus",
        "raw_inputs": "rendu raster des pages, zones sûres d'impression",
        "candidate_producer": "aucun (les QA raster existants sont partiels et par manuel)",
    },
}


def _assigned_dimensions() -> set[str]:
    """Dimensions réellement assignées par `_release_strict_gate`, lues dans l'AST."""
    tree = ast.parse(GATE_SOURCE.read_text(encoding="utf-8"))
    assigned: set[str] = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef) and node.name == "_release_strict_gate"):
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Subscript) and isinstance(sub.value, ast.Name):
                if sub.value.id == "dimensions" and isinstance(sub.slice, ast.Constant):
                    assigned.add(str(sub.slice.value))
    return assigned


def _declared_dimensions() -> list[str]:
    tree = ast.parse(GATE_SOURCE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "GATE_DIMENSIONS":
                    return [ast.literal_eval(e) for e in node.value.elts]
    raise SystemExit("GATE_DIMENSIONS introuvable")


def build() -> dict[str, Any]:
    declared = _declared_dimensions()
    assigned = _assigned_dimensions()
    uncovered = [d for d in declared if d not in assigned]

    dimensions = []
    for name in declared:
        covered = name in assigned
        entry: dict[str, Any] = {
            "dimension": name,
            "declared_by_contract": CONTRACT,
            "assigned_by_gate": covered,
            "gate_status_if_unassigned": None if covered else "not_covered",
        }
        if not covered:
            entry.update(REQUIRED_EVIDENCE.get(name, {}))
            entry["why_missing"] = (
                "aucune ligne de `_release_strict_gate` n'assigne cette dimension ; "
                "elle conserve la valeur par défaut de GATE_DIMENSION_TEMPLATE"
            )
        dimensions.append(entry)

    return {
        "artifact_type": "certification_dimension_coverage",
        "schema_version": 1,
        "generated_by": "scripts/build_certification_dimension_coverage.py",
        "contract": CONTRACT,
        "summary": {
            "DECLARED_DIMENSIONS": len(declared),
            "DIMENSIONS_WITH_A_PRODUCER": len(assigned),
            "REQUIRED_DIMENSIONS_NOT_COVERED": len(uncovered),
            "UNCOVERED_DIMENSIONS": uncovered,
            "RELEASE_STRICT_SATISFIABLE_TODAY": not uncovered,
            "APPROVES_NOTHING": True,
        },
        "dimensions": dimensions,
    }


def render_md(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Couverture des dimensions de certification",
        "",
        f"Contrat : `{payload['contract']}`",
        "",
        f"- Dimensions déclarées : `{s['DECLARED_DIMENSIONS']}`",
        f"- Dimensions réellement assignées par le gate : `{s['DIMENSIONS_WITH_A_PRODUCER']}`",
        f"- `REQUIRED_DIMENSIONS_NOT_COVERED` : `{s['REQUIRED_DIMENSIONS_NOT_COVERED']}`",
        f"- `release-strict` satisfiable en l'état : `{s['RELEASE_STRICT_SATISFIABLE_TODAY']}`",
        "",
        "Le contrat exige les sept dimensions `passed` pour `publication_eligible`.",
        "Quatre n'ont aucun producteur : le gate ne peut pas passer aujourd'hui, et",
        "il a raison de refuser — « une dimension non vérifiée reste explicitement",
        "`not_covered`, jamais implicitement verte ».",
        "",
        "| Dimension | Producteur | Preuve requise |",
        "|---|---|---|",
    ]
    for entry in payload["dimensions"]:
        if entry["assigned_by_gate"]:
            lines.append(f"| `{entry['dimension']}` | assignée par `_release_strict_gate` | — |")
        else:
            lines.append(
                f"| `{entry['dimension']}` | **aucun** — {entry.get('candidate_producer', '?')} "
                f"| {entry.get('required_evidence', '?')} |"
            )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = build()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if OUTPUT_JSON.is_file() and OUTPUT_JSON.read_text(encoding="utf-8") == rendered:
            print("CERTIFICATION_DIMENSION_COVERAGE check: OK")
            return 0
        print("CERTIFICATION_DIMENSION_COVERAGE check: STALE")
        return 1

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
