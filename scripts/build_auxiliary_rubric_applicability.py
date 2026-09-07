#!/usr/bin/env python3
"""Applicabilité d'une rubrique auxiliaire, chapitre par chapitre.

« 3 chapitres sur 10 » n'est pas automatiquement un défaut. Un livret de
méthodes n'a pas besoin d'une fiche artificielle dans un chapitre qui n'enseigne
aucune procédure autonome, et une remédiation n'a de sens que là où des erreurs
récurrentes sont identifiées.

Ce producteur rend ce jugement explicite et vérifiable, au lieu de le laisser
implicite dans une règle de complétude. Chaque chapitre sans objet de la
rubrique reçoit un verdict motivé, et seul `REAL_CONTENT_GAP` bloque.

Aucun verdict n'est déduit d'un compteur : chacun s'appuie sur ce que le
chapitre contient réellement.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "audit/INVENTAIRE_COLLECTION.json"
OUTPUT_JSON = ROOT / "audit/AUXILIARY_RUBRIC_APPLICABILITY.json"
OUTPUT_MD = ROOT / "audit/AUXILIARY_RUBRIC_APPLICABILITY.md"

REAL_GAP = "REAL_CONTENT_GAP"
NOT_REQUIRED = "NOT_PEDAGOGICALLY_REQUIRED"
COVERED_ELSEWHERE = "COVERED_BY_ANOTHER_OBJECT"

#: Verdicts motivés pour chaque chapitre dépourvu d'objet de la rubrique.
#: La motivation cite ce que le chapitre contient, jamais un quota.
VERDICTS: dict[tuple[str, str], dict[str, str]] = {
    ("TNSI-HISTOIRE-INFORMATIQUE", "remediation"): {
        "verdict": COVERED_ELSEWHERE,
        "evidence": (
            "Chapitre de culture : deux cours, deux exercices, aucune procédure "
            "à automatiser. Les erreurs visées sont des confusions de repères "
            "historiques, que les diagnostics du QCM du chapitre traitent déjà "
            "option par option."
        ),
    },
    ("TNSI-PROJET", "remediation"): {
        "verdict": NOT_REQUIRED,
        "evidence": (
            "Le chapitre ne porte ni cours ni exercice : il porte le projet "
            "annuel. La remédiation d'un projet passe par ses jalons et sa "
            "grille critériée, qui existent et sont vérifiés par le gate "
            "d'évaluation. Une fiche de remédiation y serait sans objet."
        ),
    },
    ("TNSI-PROJET", "banque_ecrite"): {
        "verdict": NOT_REQUIRED,
        "evidence": (
            "ASSESSMENT_MODE = PROJECT_ASSESSMENT, décision humaine du "
            "2026-09-06. L'épreuve écrite de spécialité ne demande à personne "
            "de conduire un projet sur copie : les deux capacités du chapitre "
            "sont évaluées par le projet annuel et sa grille critériée."
        ),
    },
    ("TNSI-PROJET", "banque_pratique"): {
        "verdict": NOT_REQUIRED,
        "evidence": (
            "Même raison qu'à l'écrit. Le projet annuel dure l'année ; il ne "
            "se traite pas en une heure sur machine."
        ),
    },
    ("TNSI-HISTOIRE-INFORMATIQUE", "banque_pratique"): {
        "verdict": COVERED_ELSEWHERE,
        "evidence": (
            "MENE2516123N définit l'épreuve pratique comme « résolution de "
            "problèmes et programmation sur machine ». Les deux capacités du "
            "chapitre — situer une évolution dans le temps, en expliquer les "
            "conséquences — ne se programment pas. Elles sont évaluées à "
            "l'écrit, par TNSI-ECRIT-S6-EX3."
        ),
    },
}


def _rubric_objects(chapter: str, rubric: str) -> list[str]:
    directory = ROOT / "NSI/chapitres" / chapter / rubric
    if not directory.is_dir():
        directory = ROOT / "Mathematiques/manuel-maths/chapitres" / chapter / rubric
    return sorted(p.name for p in directory.glob("*.tex")) if directory.is_dir() else []


def _object_types(inventory: dict[str, Any], manual: str, chapter: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    entry = inventory["manuals"][manual]["chapters"].get(chapter, {})
    for obj in entry.get("objects", []):
        path = ROOT / obj["path"]
        if not path.is_file():
            continue
        first = path.read_text(encoding="utf-8", errors="replace").split("\n", 1)[0]
        if not first.startswith("% META:"):
            continue
        kind = json.loads(first[len("% META:"):]).get("type_objet")
        counts[kind] = counts.get(kind, 0) + 1
    return counts


DEFAULT_RUBRICS = (
    ("1NSI", "methodes"),
    ("TNSI", "remediation"),
    ("TNSI", "banque_ecrite"),
    ("TNSI", "banque_pratique"),
)


def build(rubrics: tuple[tuple[str, str], ...] = DEFAULT_RUBRICS) -> dict[str, Any]:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    records: list[dict[str, Any]] = []
    for manual, rubric in rubrics:
        for chapter in sorted(inventory["manuals"][manual]["chapters"]):
            objects = _rubric_objects(chapter, rubric)
            if objects:
                continue
            declared = VERDICTS.get((chapter, rubric))
            records.append({
                "manual": manual,
                "rubric": rubric,
                "chapter": chapter,
                "chapter_object_types": _object_types(inventory, manual, chapter),
                "verdict": declared["verdict"] if declared else REAL_GAP,
                "evidence": declared["evidence"] if declared else (
                    "Aucun verdict motivé n'a été rendu : le chapitre est traité "
                    "comme une lacune tant que l'absence n'est pas justifiée."
                ),
            })

    blocking = [r for r in records if r["verdict"] == REAL_GAP]
    summary = {
        "CHAPTERS_WITHOUT_RUBRIC_OBJECT": len(records),
        "REAL_CONTENT_GAP": len(blocking),
        "NOT_PEDAGOGICALLY_REQUIRED": sum(1 for r in records if r["verdict"] == NOT_REQUIRED),
        "COVERED_BY_ANOTHER_OBJECT": sum(1 for r in records if r["verdict"] == COVERED_ELSEWHERE),
        "UNJUSTIFIED_ABSENCES_ARE_GAPS": True,
    }
    return {
        "artifact_type": "auxiliary_rubric_applicability",
        "schema_version": 1,
        "generated_by": "scripts/build_auxiliary_rubric_applicability.py",
        "summary": summary,
        "chapters": records,
    }


def applicable_chapters(manual: str, rubric: str, chapters: set[str]) -> set[str]:
    """Chapitres pour lesquels la rubrique est réellement attendue."""
    payload = build()
    excused = {
        record["chapter"] for record in payload["chapters"]
        if record["manual"] == manual and record["rubric"] == rubric
        and record["verdict"] != REAL_GAP
    }
    return chapters - excused


def render_md(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Applicabilité des rubriques auxiliaires",
        "",
        "Un chapitre sans objet d'une rubrique n'est un défaut que si la rubrique",
        "y est pédagogiquement attendue. Une absence non motivée reste une lacune.",
        "",
        f"- Chapitres sans objet : `{s['CHAPTERS_WITHOUT_RUBRIC_OBJECT']}`",
        f"- `REAL_CONTENT_GAP` : `{s['REAL_CONTENT_GAP']}`",
        f"- `NOT_PEDAGOGICALLY_REQUIRED` : `{s['NOT_PEDAGOGICALLY_REQUIRED']}`",
        f"- `COVERED_BY_ANOTHER_OBJECT` : `{s['COVERED_BY_ANOTHER_OBJECT']}`",
        "",
        "| Manuel | Rubrique | Chapitre | Verdict |",
        "|---|---|---|---|",
    ]
    for record in payload["chapters"]:
        lines.append(
            f"| `{record['manual']}` | `{record['rubric']}` | "
            f"`{record['chapter']}` | `{record['verdict']}` |"
        )
    lines.extend(["", "## Motivations", ""])
    for record in payload["chapters"]:
        lines.append(f"- `{record['chapter']}` / `{record['rubric']}` — {record['evidence']}")
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
            print("AUXILIARY_RUBRIC_APPLICABILITY check: OK")
            return 0
        print("AUXILIARY_RUBRIC_APPLICABILITY check: STALE")
        return 1
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    for record in payload["chapters"]:
        print(f"  {record['verdict']:28s} {record['manual']}/{record['rubric']}/{record['chapter']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
