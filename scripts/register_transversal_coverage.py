#!/usr/bin/env python3
"""Rattacher les capacites transversales aux annexes qui les enseignent.

Les capacites de logique, d'algorithmique sur les listes et d'automatismes ne
relevent d'aucun chapitre disciplinaire : le programme les veut transversales.
Elles etaient declarees sur un chapitre inexistant, donc sans source. Elles
pointent desormais sur les annexes transversales du manuel, qui les enseignent.

Le rattachement ne prouve rien a lui seul : c'est `check_coverage_chain.py` qui
exige ensuite de retrouver le contenu sur une page imprimee.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
MATRIX_ROOT = ROOT / "audit/official_program_coverage"
JSON_TARGET = ROOT / "audit/TRANSVERSAL_COVERAGE_REGISTRATION.json"

#: Chapitre transversal declare -> annexe qui porte la capacite.
TRANSVERSAL_SOURCE = {
    "TRANSVERSAL-LOGIQUE-ENSEMBLES": "Mathematiques/manuel-maths/transversal/logique_raisonnement.tex",
    "TRANSVERSAL-ALGORITHMIQUE-LISTES": "Mathematiques/manuel-maths/transversal/memo_python.tex",
    "TRANSVERSAL-AUTOMATISMES": "Mathematiques/manuel-maths/transversal/statistiques_automatismes.tex",
}
FIELD = "course_sources"


def build(root: Path, *, apply: bool) -> dict[str, Any]:
    registered: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for matrix in sorted(MATRIX_ROOT.glob("*.json")):
        payload = json.loads(matrix.read_text(encoding="utf-8"))
        touched = False
        for row in payload.get("rows", []):
            chapter = str(row.get("chapter") or "")
            source = next(
                (s for key, s in TRANSVERSAL_SOURCE.items() if key in chapter), None
            )
            if source is None:
                continue
            if not (root / source).is_file():
                skipped.append({
                    "atom_id": row.get("atom_id"), "chapter": chapter,
                    "why": f"annexe absente : {source}",
                })
                continue
            if source not in row.get(FIELD, []):
                row.setdefault(FIELD, []).append(source)
                touched = True
            evidence = row.setdefault("evidence_paths", [])
            if source not in evidence:
                evidence.append(source)
                touched = True
            row["gap_type"] = None
            row["source_content_state"] = "PRESENT"
            row["gap_reason"] = (
                "Capacite transversale : le programme la veut enseignee au fil de "
                f"l'annee, elle est portee par l'annexe {Path(source).name}."
            )
            registered.append({
                "atom_id": row.get("atom_id"), "manual": row.get("manual"),
                "chapter": chapter, "source": source,
            })
        if touched and apply:
            matrix.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    return {
        "artifact_type": "transversal_coverage_registration",
        "generated_by": "scripts/register_transversal_coverage.py",
        "registered": registered,
        "skipped": skipped,
        "summary": {
            "REGISTERED": len(registered),
            "SKIPPED_MISSING_ANNEX": len(skipped),
            "BY_MANUAL": dict(collections.Counter(r["manual"] for r in registered)),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    report = build(args.root, apply=args.apply)
    JSON_TARGET.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
