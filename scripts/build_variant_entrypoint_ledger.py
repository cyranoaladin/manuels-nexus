#!/usr/bin/env python3
"""Quels points d'entree produisent un artefact destine a l'eleve.

La classe LaTeX laisse l'environnement `corrige` visible par defaut ; c'est
l'assembleur de manuel qui le neutralise dans le preambule eleve. La garde est
donc dependante du chemin de build, et il faut nommer explicitement quels
points d'entree sont de production pour l'eleve et lesquels ne le sont pas.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MATH_SCRIPTS = ROOT / "Mathematiques" / "manuel-maths" / "scripts"
PRODUCERS = ROOT / "audit" / "BUILD_PRODUCERS.yaml"
OUTPUT = ROOT / "audit" / "VARIANT_ENTRYPOINT_LEDGER.json"

NEUTRALISATION = "RenewDocumentEnvironment{corrige}"


def _declared_assemblers() -> set[str]:
    registry = yaml.safe_load(PRODUCERS.read_text(encoding="utf-8"))
    return {row["assembler"] for row in registry["producers"]}


def build_ledger() -> dict[str, Any]:
    declared = _declared_assemblers()
    rows: list[dict[str, Any]] = []
    for path in sorted(MATH_SCRIPTS.glob("assemble*.py")):
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT).as_posix()
        audience_variants = sorted(
            {name for name in ("eleve", "professeur") if f'"{name}"' in text}
        )
        rows.append({
            "entrypoint": relative,
            "declared_producer": relative in declared,
            "audience_variants": audience_variants,
            "produces_student_artifact": "eleve" in audience_variants,
            "neutralises_corrige": NEUTRALISATION in text,
            "classification": (
                "PRODUCTION_STUDENT_ENTRYPOINT"
                if "eleve" in audience_variants and relative in declared
                else "NON_PRODUCTION_STUDENT_ENTRYPOINT"
            ),
        })
    leaks = [
        row["entrypoint"]
        for row in rows
        if row["classification"] == "PRODUCTION_STUDENT_ENTRYPOINT"
        and not row["neutralises_corrige"]
    ]
    return {
        "artifact_type": "variant_entrypoint_ledger",
        "schema_version": 1,
        "generated_by": "scripts/build_variant_entrypoint_ledger.py",
        "guard_location": "preambule de l'assembleur de manuel, pas la classe",
        "guard_class": "BUILD_PATH_DEPENDENT_VARIANT_GUARD",
        "entrypoints": rows,
        "SUPPORTED_STUDENT_ENTRYPOINT_LEAKS": len(leaks),
        "leaking_entrypoints": leaks,
        "non_production_note": (
            "les variantes de assemble.py (complet, methodes, parcours1, "
            "remediation) selectionnent des rubriques, pas une audience : ce "
            "point d'entree n'a aucune variante eleve et n'est pas un "
            "producteur declare. Ses sorties parcours1 et remediation "
            "contiennent des corriges et ne doivent pas etre remises a un "
            "eleve."
        ),
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build_ledger()
    rendered = render_json(payload)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("STALE: audit/VARIANT_ENTRYPOINT_LEDGER.json")
        print(f"leaks={payload['SUPPORTED_STUDENT_ENTRYPOINT_LEAKS']}")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"leaks={payload['SUPPORTED_STUDENT_ENTRYPOINT_LEAKS']}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
