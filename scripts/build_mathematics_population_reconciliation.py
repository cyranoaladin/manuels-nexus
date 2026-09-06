#!/usr/bin/env python3
"""Réconciliation des populations mathématiques.

Deux chiffres coexistaient dans mes rapports sans être comparables :
`MISSING_ORACLE = 91` et « oracle 25 GAP + 17 sans reçu ». Ils ne comptaient pas
la même chose, et les juxtaposer laissait croire à une contradiction.

    MISSING_ORACLE          compte des **objets** : contenu mathématique d'un
                            type qui pourrait porter un bloc % BEGIN-VERIFY et
                            n'en porte pas. Mesuré en exécutant les blocs.

    oracle GAP / NO_RECEIPTS
                            compte des **chapitres** : le gate y lit des reçus
                            `validations/*.sympy.json` déposés, pas une
                            exécution. Un chapitre sans reçu est NO_RECEIPTS ;
                            un chapitre dont des verdicts `manual_review` ne
                            sont pas routés par le registre de disposition est
                            GAP.

L'écart entre les deux n'est donc pas une incohérence : c'est la distance entre
ce que la machine sait exécuter et ce que le dépôt a conservé comme preuve.
Ce producteur l'expose et vérifie que chaque objet n'est compté qu'une fois.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import evidence_freshness as freshness  # noqa: E402

INVENTORY = "audit/INVENTAIRE_COLLECTION.json"
MATHEMATICS = "audit/DIMENSION_MATHEMATICS.json"
MATRIX = "audit/PUBLISH_READINESS_CHAPTER_MATRIX.json"
OUTPUT_JSON = ROOT / "audit/MATHEMATICS_POPULATION_RECONCILIATION.json"
OUTPUT_MD = ROOT / "audit/MATHEMATICS_POPULATION_RECONCILIATION.md"


def build() -> dict[str, Any]:
    inventory = json.loads((ROOT / INVENTORY).read_text(encoding="utf-8"))
    maths = json.loads((ROOT / MATHEMATICS).read_text(encoding="utf-8"))["summary"]
    matrix = json.loads((ROOT / MATRIX).read_text(encoding="utf-8"))
    rows = matrix.get("chapters") or matrix.get("rows") or []
    rows = list(rows.values()) if isinstance(rows, dict) else rows

    total_objects = sum(
        len(chapter["objects"])
        for manual in inventory["manuals"].values()
        for chapter in manual["chapters"].values()
    )
    partition = maths["NOT_APPLICABLE_PARTITION"]

    receipts = Counter()
    for row in rows:
        oracle = row.get("oracle") or {}
        for key in ("pass", "manual_review", "machine_unclassified",
                    "human_science_required", "fail", "receipts"):
            receipts[key] += oracle.get(key) or 0
    statuses = Counter(row["machine_dimensions"]["oracle"] for row in rows)

    objects = {
        "MATHEMATICS_OBJECTS_TOTAL": total_objects,
        "FORMAL_ASSERTION_OBJECTS": maths["OBJECTS_WITH_VERIFIABLE_ASSERTIONS"],
        "OBJECTS_MISSING_ORACLE": partition.get("MISSING_ORACLE", 0),
        "NON_FORMALIZABLE_OBJECTS": partition.get("MATHEMATICAL_NON_FORMALIZABLE", 0),
        "TRULY_NOT_MATHEMATICAL": partition.get("TRULY_NOT_MATHEMATICAL", 0),
    }
    accounted = (
        objects["FORMAL_ASSERTION_OBJECTS"]
        + objects["OBJECTS_MISSING_ORACLE"]
        + objects["NON_FORMALIZABLE_OBJECTS"]
        + objects["TRULY_NOT_MATHEMATICAL"]
    )
    unreconciled = objects["MATHEMATICS_OBJECTS_TOTAL"] - accounted

    chapters = {
        "CHAPTERS_TOTAL": len(rows),
        "CHAPTER_ORACLE_COMPLETE": statuses.get("COMPLETE", 0),
        "CHAPTER_ORACLE_GAPS": statuses.get("GAP", 0),
        "ORACLE_EVIDENCE_MISSING_RECEIPT": statuses.get("NO_RECEIPTS", 0),
    }
    stored = {
        "STORED_SYMPY_RECEIPTS": receipts["receipts"],
        "RECEIPT_PASS": receipts["pass"],
        "RECEIPT_MANUAL_REVIEW": receipts["manual_review"],
        "RECEIPT_FAIL": receipts["fail"],
        "MACHINE_UNCLASSIFIED": receipts["machine_unclassified"],
        "HUMAN_SCIENCE_REQUIRED": receipts["human_science_required"],
        "EXECUTED_BUT_UNRECEIPTED": (
            maths["OBJECTS_WITH_VERIFIABLE_ASSERTIONS"] - receipts["receipts"]
        ),
    }

    summary = {
        **objects,
        **chapters,
        **stored,
        "MATHEMATICS_POPULATION_UNRECONCILED": unreconciled,
        "RECONCILIATION_EQUATION": (
            f"{objects['FORMAL_ASSERTION_OBJECTS']} exécutés "
            f"+ {objects['OBJECTS_MISSING_ORACLE']} sans oracle "
            f"+ {objects['NON_FORMALIZABLE_OBJECTS']} non formalisables "
            f"+ {objects['TRULY_NOT_MATHEMATICAL']} non mathématiques "
            f"= {accounted} / {objects['MATHEMATICS_OBJECTS_TOTAL']} objets"
        ),
        "WHY_THE_TWO_ORACLE_FIGURES_DIFFER": (
            "MISSING_ORACLE compte des objets sans bloc de vérification ; "
            "GAP et NO_RECEIPTS comptent des chapitres selon les reçus déposés. "
            "Le chapitre exige une preuve conservée, l'objet une preuve "
            "exécutable : fermer l'un ne ferme pas l'autre."
        ),
    }
    return {
        "artifact_type": "mathematics_population_reconciliation",
        "schema_version": 1,
        "generated_by": "scripts/build_mathematics_population_reconciliation.py",
        "freshness": freshness.stamp([INVENTORY, MATHEMATICS, MATRIX]),
        "summary": summary,
    }


def render_md(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Réconciliation des populations mathématiques",
        "",
        s["WHY_THE_TWO_ORACLE_FIGURES_DIFFER"],
        "",
        "## Objets",
        "",
        f"- Total inventaire : `{s['MATHEMATICS_OBJECTS_TOTAL']}`",
        f"- Portant une assertion formelle : `{s['FORMAL_ASSERTION_OBJECTS']}`",
        f"- Sans oracle alors qu'ils pourraient en porter : `{s['OBJECTS_MISSING_ORACLE']}`",
        f"- Non formalisables : `{s['NON_FORMALIZABLE_OBJECTS']}`",
        f"- Non mathématiques : `{s['TRULY_NOT_MATHEMATICAL']}`",
        "",
        f"`{s['RECONCILIATION_EQUATION']}`",
        "",
        f"- `MATHEMATICS_POPULATION_UNRECONCILED` : `{s['MATHEMATICS_POPULATION_UNRECONCILED']}`",
        "",
        "## Chapitres et preuves conservées",
        "",
        f"- Chapitres : `{s['CHAPTERS_TOTAL']}` — complets `{s['CHAPTER_ORACLE_COMPLETE']}`, "
        f"lacunaires `{s['CHAPTER_ORACLE_GAPS']}`, sans reçu `{s['ORACLE_EVIDENCE_MISSING_RECEIPT']}`",
        f"- Reçus SymPy déposés : `{s['STORED_SYMPY_RECEIPTS']}` "
        f"(pass `{s['RECEIPT_PASS']}`, revue humaine `{s['RECEIPT_MANUAL_REVIEW']}`, "
        f"échec `{s['RECEIPT_FAIL']}`)",
        f"- Verdicts non routés : `{s['MACHINE_UNCLASSIFIED']}`",
        f"- Objets exécutés sans reçu conservé : `{s['EXECUTED_BUT_UNRECEIPTED']}`",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if OUTPUT_JSON.is_file() and OUTPUT_JSON.read_text(encoding="utf-8") == rendered:
            print("MATHEMATICS_POPULATION_RECONCILIATION check: OK")
            return 0
        print("MATHEMATICS_POPULATION_RECONCILIATION check: STALE")
        return 1
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
