#!/usr/bin/env python3
"""Provenance de chaque assemblage de livrable auxiliaire requis.

Avant d'écrire un nouveau master, il fallait chercher : un assemblage
historique, un ancien master, un générateur, une cible supprimée. Ce producteur
consigne le résultat de cette recherche pour les six auxiliaires qui n'avaient
aucun assemblage, afin que la décision reste vérifiable.

Aucun master n'a été rédigé là où une recette canonique existait : quatre des
six se dérivent des sources courantes par le moteur d'assemblage déjà en place.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "audit/DELIVERABLE_ASSEMBLY_FORENSICS.json"
OUTPUT_MD = ROOT / "audit/DELIVERABLE_ASSEMBLY_FORENSICS.md"

RESTORE = "RESTORE_HISTORICAL_ASSEMBLY"
DERIVE = "DERIVE_FROM_CURRENT_CANONICAL_SOURCES"
NEW = "NEW_ASSEMBLY_REQUIRED"

FINDINGS: tuple[dict[str, Any], ...] = (
    *[
        {
            "deliverable_id": f"{manual}::{variant}",
            "historical_master_found": False,
            "historical_generator_found": True,
            "historical_generator": "Mathematiques/manuel-maths/scripts/assemble_manuel.py",
            "canonical_source_set": f"chapitres/{manual}-*/{directory}/*.tex",
            "assembly_decision": DERIVE,
            "rationale": (
                "Les sources existent chapitre par chapitre et l'assembleur du "
                "manuel sait déjà parcourir les chapitres, poser les ouvertures "
                "et marquer les rubriques. Il manquait la déclaration de la "
                "variante, pas une recette."
            ),
            "assembly_id": None,
        }
        for manual, variant, directory in (
            ("1SPE", "livret_methodes", "methodes"),
            ("1SPE", "livret_remediation", "remediation"),
            ("TSPE_2026_2027", "livret_methodes", "methodes"),
            ("TSPE_2026_2027", "livret_remediation", "remediation"),
        )
    ],
    {
        "deliverable_id": "TNSI::banque_ecrite",
        "historical_master_found": False,
        "historical_generator_found": False,
        "canonical_source_set": None,
        "assembly_decision": NEW,
        "rationale": (
            "L'assembleur NSI prévoit déjà un répertoire `ece` dans ses ordres "
            "`eleve` et `professeur`, mais aucun chapitre TNSI n'en possède : "
            "le créneau est déclaré, le contenu n'existe pas. Ce n'est donc pas "
            "un assemblage manquant mais du contenu manquant."
        ),
        "assembly_id": None,
    },
    {
        "deliverable_id": "TNSI::banque_pratique",
        "historical_master_found": False,
        "historical_generator_found": False,
        "canonical_source_set": None,
        "assembly_decision": NEW,
        "rationale": (
            "Même constat que la banque écrite. Une banque pratique exige en "
            "outre un environnement d'exécution, des jeux de données, des cas "
            "de test et des corrigés exécutables : elle ne peut pas être "
            "dérivée des chapitres existants."
        ),
        "assembly_id": None,
    },
)


def build() -> dict[str, Any]:
    inventory = json.loads((ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8"))
    declared = {a["assembly_id"] for a in inventory.get("declared_assemblies", [])}

    variant_alias = {
        "livret_methodes": "methodes",
        "livret_remediation": "remediation",
    }
    records = []
    for finding in FINDINGS:
        manual, variant = finding["deliverable_id"].split("::")
        alias = variant_alias.get(variant, variant)
        project = "math" if manual in {"1SPE", "TSPE_2026_2027", "TCOMPL", "TEXPERTES"} else "nsi"
        assembly_id = f"{project}:manual:{manual}:{alias}"
        record = dict(finding)
        record["assembly_id"] = assembly_id
        record["assembly_declared"] = assembly_id in declared
        records.append(record)

    resolved = [r for r in records if r["assembly_declared"]]
    summary = {
        "INVESTIGATED_DELIVERABLES": len(records),
        "RESTORE_HISTORICAL_ASSEMBLY": sum(1 for r in records if r["assembly_decision"] == RESTORE),
        "DERIVE_FROM_CURRENT_CANONICAL_SOURCES": sum(
            1 for r in records if r["assembly_decision"] == DERIVE
        ),
        "NEW_ASSEMBLY_REQUIRED": sum(1 for r in records if r["assembly_decision"] == NEW),
        "ASSEMBLIES_NOW_DECLARED": len(resolved),
        "ASSEMBLIES_STILL_MISSING": len(records) - len(resolved),
        "NEW_MASTERS_WRITTEN": 0,
    }
    return {
        "artifact_type": "deliverable_assembly_forensics",
        "schema_version": 1,
        "generated_by": "scripts/build_deliverable_assembly_forensics.py",
        "summary": summary,
        "deliverables": records,
    }


def render_md(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Provenance des assemblages de livrables auxiliaires",
        "",
        f"- Livrables investigués : `{s['INVESTIGATED_DELIVERABLES']}`",
        f"- Dérivés des sources canoniques : `{s['DERIVE_FROM_CURRENT_CANONICAL_SOURCES']}`",
        f"- Nouveaux assemblages requis : `{s['NEW_ASSEMBLY_REQUIRED']}`",
        f"- Assemblages désormais déclarés : `{s['ASSEMBLIES_NOW_DECLARED']}`",
        f"- Masters rédigés de zéro : `{s['NEW_MASTERS_WRITTEN']}`",
        "",
        "| Livrable | Décision | Assemblage déclaré |",
        "|---|---|---|",
    ]
    for record in payload["deliverables"]:
        lines.append(
            f"| `{record['deliverable_id']}` | `{record['assembly_decision']}` | "
            f"{'oui' if record['assembly_declared'] else '**non**'} |"
        )
    lines.extend(["", "## Justifications", ""])
    for record in payload["deliverables"]:
        lines.append(f"- `{record['deliverable_id']}` — {record['rationale']}")
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
            print("DELIVERABLE_ASSEMBLY_FORENSICS check: OK")
            return 0
        print("DELIVERABLE_ASSEMBLY_FORENSICS check: STALE")
        return 1
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
