#!/usr/bin/env python3
"""Quelles fiches methode manquent vraiment, capacite par capacite.

Sept chapitres de 1NSI n'ont aucune fiche methode : le livret est a 3/10, et
la tentation evidente est d'en ecrire sept pour atteindre 10/10. Ce serait du
remplissage. Une fiche qui ne decrit aucune demarche, ou qui recopie une
demarche deja ecrite dans le cours, n'apprend rien et gonfle un compteur.

Le jugement — telle capacite appelle-t-elle une fiche ? — est editorial. Il
est ecrit dans `method_sheet_decisions.py`, capacite par capacite, avec sa
raison. Ce producteur ne le devine pas : il le VERIFIE.

  * la table couvre exactement les capacites du contrat de chaque chapitre,
    ni plus ni moins — une capacite ajoutee au contrat sans decision fait
    echouer la construction ;
  * chaque capacite `PROCEDURAL_UNCOVERED` est servie par exactement une
    fiche planifiee, et chaque fiche sert au moins une telle capacite —
    une fiche qui ne sert rien serait du remplissage, et le compteur
    `METHOD_BOOKLET_FILLER_OBJECTS` la verrait ;
  * chaque capacite `PROCEDURAL_COVERED` nomme le fichier qui la couvre, et
    ce fichier existe.

VERDICT DE CHAPITRE, DEDUIT DES CAPACITES.

`METHOD_ALREADY_EXISTS_NOT_ASSEMBLED`  le chapitre porte deja des fiches.
`METHOD_NOT_PEDAGOGICALLY_JUSTIFIED`   aucune capacite procedurale.
`TRANSVERSAL_METHOD_ALREADY_COVERS`    toutes deja ecrites ailleurs.
`METHOD_SHEET_REQUIRED`                il reste des demarches a ecrire.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import evidence_freshness as freshness  # noqa: E402
from method_sheet_decisions import (  # noqa: E402
    CAPACITY_VERDICTS,
    DECLARATIVE,
    PLANNED_SHEETS,
    PROCEDURAL_COVERED,
    PROCEDURAL_UNCOVERED,
)

OUTPUT_JSON = ROOT / "audit/METHOD_SHEET_REQUIREMENT_AUDIT.json"
OUTPUT_MD = ROOT / "audit/METHOD_SHEET_REQUIREMENT_AUDIT.md"
CHAPTERS_DIR = Path("NSI/chapitres")

REQUIRED = "METHOD_SHEET_REQUIRED"
ALREADY_EXISTS = "METHOD_ALREADY_EXISTS_NOT_ASSEMBLED"
NOT_JUSTIFIED = "METHOD_NOT_PEDAGOGICALLY_JUSTIFIED"
COVERED = "TRANSVERSAL_METHOD_ALREADY_COVERS"

VALID = {PROCEDURAL_UNCOVERED, DECLARATIVE, PROCEDURAL_COVERED}


def audit_chapter(root: Path, chapter_dir: Path) -> dict[str, Any]:
    chapter = chapter_dir.name
    contract = yaml.safe_load(
        (chapter_dir / "contrat.yaml").read_text(encoding="utf-8")
    ) or {}
    declared = {
        str(c["code"]): str(c.get("libelle_eleve") or "")
        for c in (contract.get("capacites") or [])
        if isinstance(c, dict) and isinstance(c.get("code"), str)
    }
    decisions = CAPACITY_VERDICTS.get(chapter)
    if decisions is None:
        raise ValueError(f"aucune decision declaree pour {chapter}")
    if set(decisions) != set(declared):
        missing = sorted(set(declared) - set(decisions))
        extra = sorted(set(decisions) - set(declared))
        raise ValueError(
            f"{chapter}: decisions sans capacite {extra}, "
            f"capacites sans decision {missing}"
        )

    capacities = []
    for code, libelle in sorted(declared.items()):
        verdict, why, covering = decisions[code]
        if verdict not in VALID:
            raise ValueError(f"{chapter}/{code}: verdict inconnu {verdict}")
        if verdict == PROCEDURAL_COVERED:
            if not covering:
                raise ValueError(f"{chapter}/{code}: couverture sans objet nomme")
            if not (root / covering).exists():
                raise ValueError(f"{chapter}/{code}: {covering} absent du depot")
        capacities.append({
            "code": code,
            "libelle_eleve": libelle,
            "verdict": verdict,
            "evidence": why,
            "covered_by": covering,
        })

    uncovered = {c["code"] for c in capacities if c["verdict"] == PROCEDURAL_UNCOVERED}
    planned = PLANNED_SHEETS.get(chapter, [])
    served: set[str] = set()
    sheets = []
    for sheet_id, title, covers in planned:
        unknown = sorted(set(covers) - set(declared))
        if unknown:
            raise ValueError(f"{chapter}/{sheet_id}: capacites inconnues {unknown}")
        not_needing = sorted(set(covers) - uncovered)
        if not_needing:
            raise ValueError(
                f"{chapter}/{sheet_id}: sert des capacites qui n'appellent "
                f"aucune fiche {not_needing}"
            )
        overlap = sorted(served & set(covers))
        if overlap:
            raise ValueError(f"{chapter}/{sheet_id}: capacites deja servies {overlap}")
        served |= set(covers)
        sheets.append({
            "sheet_id": sheet_id,
            "titre": title,
            "covers": list(covers),
            "path": f"{CHAPTERS_DIR}/{chapter}/methodes/{_object_id(chapter, sheet_id)}.tex",
            "authored": (
                root / CHAPTERS_DIR / chapter / "methodes"
                / f"{_object_id(chapter, sheet_id)}.tex"
            ).is_file(),
        })
    unserved = sorted(uncovered - served)
    if unserved:
        raise ValueError(f"{chapter}: capacites sans fiche planifiee {unserved}")

    existing = sorted(
        p.relative_to(root).as_posix()
        for p in (chapter_dir / "methodes").glob("*.tex")
    ) if (chapter_dir / "methodes").is_dir() else []
    planned_paths = {sheet["path"] for sheet in sheets}
    filler = [path for path in existing if path not in planned_paths and planned]

    if not uncovered:
        verdict = (
            ALREADY_EXISTS if existing
            else COVERED if any(
                c["verdict"] == PROCEDURAL_COVERED for c in capacities
            )
            else NOT_JUSTIFIED
        )
    else:
        verdict = REQUIRED

    return {
        "chapter": chapter,
        "titre": contract.get("titre"),
        "verdict": verdict,
        "existing_method_objects": existing,
        "planned_sheets": sheets,
        "sheets_still_to_author": [s["sheet_id"] for s in sheets if not s["authored"]],
        "filler_candidates": filler,
        "capacities": capacities,
    }


def _object_id(chapter: str, sheet_id: str) -> str:
    """Identifiant d'objet, sur le modele du chapitre deja pourvu.

    `1NSI-TYPES-CONSTRUITS` nomme ses fiches `1NSI-TC-M1`. Le prefixe court
    est repris du prefixe des objets existants du chapitre.
    """
    return f"{SHORT_PREFIX[chapter]}-{sheet_id}"


SHORT_PREFIX = {
    "1NSI-ALGO-DICHO-GLOUTON-KNN": "1NSI-ADGK",
    "1NSI-ALGO-PARCOURS-TRIS": "1NSI-APT",
    "1NSI-ARCHITECTURE-OS": "1NSI-ARCHOS",
    "1NSI-LANGAGE": "1NSI-LANG",
    "1NSI-PROJET-METHODES": "1NSI-PM",
    "1NSI-RESEAUX": "1NSI-RES",
    "1NSI-TABLES": "1NSI-TAB",
    "1NSI-TYPES-BASE": "1NSI-TB",
    "1NSI-TYPES-CONSTRUITS": "1NSI-TC",
    "1NSI-WEB-IHM": "1NSI-WEB",
}


def build(root: Path = ROOT) -> dict[str, Any]:
    chapters = []
    inputs: list[str] = []
    for chapter_dir in sorted((root / CHAPTERS_DIR).iterdir()):
        if not chapter_dir.name.startswith("1NSI-"):
            continue
        if not (chapter_dir / "contrat.yaml").is_file():
            continue
        chapters.append(audit_chapter(root, chapter_dir))
        inputs.append((chapter_dir / "contrat.yaml").relative_to(root).as_posix())

    counts: dict[str, int] = {}
    for row in chapters:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    planned = sum(len(row["planned_sheets"]) for row in chapters)
    remaining = sum(len(row["sheets_still_to_author"]) for row in chapters)
    filler = sum(len(row["filler_candidates"]) for row in chapters)

    summary = {
        "CHAPTERS_AUDITED": len(chapters),
        "METHOD_SHEET_REQUIRED": counts.get(REQUIRED, 0),
        "METHOD_ALREADY_EXISTS_NOT_ASSEMBLED": counts.get(ALREADY_EXISTS, 0),
        "METHOD_NOT_PEDAGOGICALLY_JUSTIFIED": counts.get(NOT_JUSTIFIED, 0),
        "TRANSVERSAL_METHOD_ALREADY_COVERS": counts.get(COVERED, 0),
        "PROCEDURAL_CAPACITIES_UNCOVERED": sum(
            1 for row in chapters for c in row["capacities"]
            if c["verdict"] == PROCEDURAL_UNCOVERED
        ),
        "DECLARATIVE_CAPACITIES": sum(
            1 for row in chapters for c in row["capacities"]
            if c["verdict"] == DECLARATIVE
        ),
        "PROCEDURAL_CAPACITIES_ALREADY_COVERED": sum(
            1 for row in chapters for c in row["capacities"]
            if c["verdict"] == PROCEDURAL_COVERED
        ),
        "SHEETS_PLANNED": planned,
        "SHEETS_STILL_TO_AUTHOR": remaining,
        "METHOD_BOOKLET_FILLER_OBJECTS": filler,
    }
    payload = {
        "artifact_type": "method_sheet_requirement_audit",
        "schema_version": 2,
        "generated_by": "scripts/build_method_sheet_requirement_audit.py",
        "decision_table": "scripts/method_sheet_decisions.py",
        "approves_nothing": True,
        "summary": summary,
        "chapters": chapters,
    }
    payload["freshness"] = freshness.stamp(inputs, root=root)
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Fiches méthode 1NSI : ce qui manque vraiment",
        "",
        f"- `METHOD_SHEET_REQUIRED` : `{s['METHOD_SHEET_REQUIRED']}`",
        f"- `METHOD_ALREADY_EXISTS_NOT_ASSEMBLED` : `{s['METHOD_ALREADY_EXISTS_NOT_ASSEMBLED']}`",
        f"- `METHOD_NOT_PEDAGOGICALLY_JUSTIFIED` : `{s['METHOD_NOT_PEDAGOGICALLY_JUSTIFIED']}`",
        f"- `TRANSVERSAL_METHOD_ALREADY_COVERS` : `{s['TRANSVERSAL_METHOD_ALREADY_COVERS']}`",
        f"- `METHOD_BOOKLET_FILLER_OBJECTS` : `{s['METHOD_BOOKLET_FILLER_OBJECTS']}`",
        "",
        f"Sur {s['PROCEDURAL_CAPACITIES_UNCOVERED'] + s['DECLARATIVE_CAPACITIES'] + s['PROCEDURAL_CAPACITIES_ALREADY_COVERED']} "
        f"capacités jugées : {s['PROCEDURAL_CAPACITIES_UNCOVERED']} appellent une démarche non écrite, "
        f"{s['DECLARATIVE_CAPACITIES']} sont déclaratives, "
        f"{s['PROCEDURAL_CAPACITIES_ALREADY_COVERED']} sont déjà couvertes. "
        f"{s['SHEETS_PLANNED']} fiches planifiées, dont {s['SHEETS_STILL_TO_AUTHOR']} restent à écrire.",
        "",
        "| Chapitre | Verdict | Fiches planifiées | Restent à écrire |",
        "|---|---|---|---|",
    ]
    for row in payload["chapters"]:
        lines.append(
            f"| `{row['chapter']}` | `{row['verdict']}` | "
            f"{len(row['planned_sheets'])} | "
            f"{', '.join(row['sheets_still_to_author']) or '—'} |"
        )
    lines += ["", "## Capacités jugées déclaratives ou déjà couvertes", ""]
    for row in payload["chapters"]:
        for capacity in row["capacities"]:
            if capacity["verdict"] == PROCEDURAL_UNCOVERED:
                continue
            lines.append(
                f"- `{row['chapter']}::{capacity['code']}` — "
                f"`{capacity['verdict']}` : {capacity['evidence']}"
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
        if not OUTPUT_JSON.is_file():
            print("METHOD_SHEET_REQUIREMENT_AUDIT check: MISSING")
            return 1
        if OUTPUT_JSON.read_text(encoding="utf-8") != rendered:
            print("METHOD_SHEET_REQUIREMENT_AUDIT check: STALE")
            return 1
        print("METHOD_SHEET_REQUIREMENT_AUDIT check: OK")
        return 0
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
