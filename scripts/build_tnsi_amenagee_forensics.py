#!/usr/bin/env python3
"""État réel des variantes aménagées, avant toute rédaction.

Le rapport précédent affirmait deux choses incompatibles : que
`TNSI::version_amenagee` avait du contenu, et qu'aucun chapitre TNSI ne
possédait d'objet aménagé. La seconde est vraie.

La cause est une métrique fautive : la maturité lisait `included_files` de
l'assemblage, qui compte aussi les `contrat.yaml` relus pour composer les
ouvertures de chapitre. Une variante sans le moindre objet déclarait ainsi sept
fichiers. Ce producteur mesure les objets réellement présents, chapitre par
chapitre.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "audit/INVENTAIRE_COLLECTION.json"
OUTPUT_JSON = ROOT / "audit/TNSI_AMENAGEE_FORENSICS.json"
OUTPUT_MD = ROOT / "audit/TNSI_AMENAGEE_FORENSICS.md"

CONTENT_EXISTS_BUT_BUILD_FAILS = "CONTENT_EXISTS_BUT_BUILD_FAILS"
SKELETON_ONLY = "SKELETON_ONLY"
EMPTY_VARIANT = "EMPTY_VARIANT"
COMPLETE = "COMPLETE"


def _variant_state(manual: str, chapters: set[str]) -> dict[str, Any]:
    base = ROOT / "NSI/chapitres"
    per_chapter = {}
    for chapter in sorted(chapters):
        directory = base / chapter / "amenagee"
        sources = sorted(directory.glob("*.tex")) if directory.is_dir() else []
        per_chapter[chapter] = [p.name for p in sources]
    total = sum(len(v) for v in per_chapter.values())
    covered = sum(1 for v in per_chapter.values() if v)
    if total == 0:
        classification = EMPTY_VARIANT
    elif covered == len(chapters):
        classification = COMPLETE
    else:
        classification = SKELETON_ONLY
    return {
        "manual": manual,
        "source_objects": total,
        "chapters_with_content": covered,
        "chapters_total": len(chapters),
        "coverage_ratio": f"{covered}/{len(chapters)}",
        "classification": classification,
        "per_chapter": per_chapter,
    }


def build() -> dict[str, Any]:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    states = [
        _variant_state(manual, set(inventory["manuals"][manual]["chapters"]))
        for manual in ("1NSI", "TNSI")
        if manual in inventory["manuals"]
    ]
    tnsi = next((s for s in states if s["manual"] == "TNSI"), None)
    summary = {
        "TNSI_AMENAGEE_SOURCE_OBJECTS": tnsi["source_objects"] if tnsi else 0,
        "TNSI_AMENAGEE_ACTUAL_CONTENT_COVERAGE": tnsi["coverage_ratio"] if tnsi else "0/0",
        "TNSI_AMENAGEE_CLASSIFICATION": tnsi["classification"] if tnsi else EMPTY_VARIANT,
        "READINESS_METRIC_WAS_WRONG": True,
        "WHY": (
            "La maturité lisait included_files, qui compte les contrat.yaml des "
            "ouvertures de chapitre : une variante vide y déclarait sept fichiers."
        ),
    }
    return {
        "artifact_type": "amenagee_variant_forensics",
        "schema_version": 1,
        "generated_by": "scripts/build_tnsi_amenagee_forensics.py",
        "summary": summary,
        "variants": states,
    }


def render_md(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# État réel des variantes aménagées",
        "",
        f"- `TNSI_AMENAGEE_SOURCE_OBJECTS` : `{s['TNSI_AMENAGEE_SOURCE_OBJECTS']}`",
        f"- `TNSI_AMENAGEE_ACTUAL_CONTENT_COVERAGE` : `{s['TNSI_AMENAGEE_ACTUAL_CONTENT_COVERAGE']}`",
        f"- Classification : `{s['TNSI_AMENAGEE_CLASSIFICATION']}`",
        "",
        s["WHY"],
        "",
        "| Manuel | Objets | Chapitres couverts | Classification |",
        "|---|---|---|---|",
    ]
    for state in payload["variants"]:
        lines.append(
            f"| `{state['manual']}` | {state['source_objects']} | "
            f"{state['coverage_ratio']} | `{state['classification']}` |"
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
            print("TNSI_AMENAGEE_FORENSICS check: OK")
            return 0
        print("TNSI_AMENAGEE_FORENSICS check: STALE")
        return 1
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
