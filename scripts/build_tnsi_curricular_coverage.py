#!/usr/bin/env python3
"""Conformité curriculaire du manuel TNSI — preuve sémantique, pas numérique.

Le Release Owner a tranché (décision du 2026-09-06) : `target_chapters: 12`,
issu de `DIRECTIVES_COLLECTION.md` J6 et marqué `A_VALIDER_HUMAIN`, n'est
**pas** un critère de publication. L'arrêté MENE1921247A organise le programme
en six rubriques, précise qu'il ne constitue pas un plan de cours, et laisse la
progression aux enseignants ; la démarche de projet y est fondamentale.

Le remplacer par « exactement 7 chapitres » serait remplacer un dogme par un
autre. La conformité se prouve donc au niveau des **capacités officielles**, pas
au nombre de fichiers :

    OFFICIAL_RUBRICS_COVERED        toute rubrique du BO a du contenu
    PROJECT_REQUIREMENT_COVERED     la démarche de projet est traitée
    PEDAGOGICAL_STRUCTURE_COHERENT  un chapitre ne mélange pas les rubriques
    OFFICIAL_CAPACITIES_UNCOVERED   capacités du BO sans aucun objet

Cette dernière métrique est la seule qui puisse encore bloquer : elle mesure du
contenu réellement absent, pas un écart de découpage éditorial.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REFERENTIAL = ROOT / "NSI/referentiel"
INVENTORY = ROOT / "audit/INVENTAIRE_COLLECTION.json"
OUTPUT_JSON = ROOT / "audit/TNSI_CURRICULAR_COVERAGE.json"
OUTPUT_MD = ROOT / "audit/TNSI_CURRICULAR_COVERAGE.md"

BO_REFERENCE = "arrêté MENE1921247A, BO spécial n°8 du 25 juillet 2019"
PROJECT_THEME = "DEMARCHE-DE-PROJET"
SUPERSEDED_PROPOSAL = {
    "proposal": "target_chapters = 12",
    "origin": "DIRECTIVES_COLLECTION.md#J6",
    "original_marking": "A_VALIDER_HUMAIN",
    "status": "SUPERSEDED_EDITORIAL_PROPOSAL",
    "superseded_by": "Décision Release Owner 2026-09-06 — NOT_A_RELEASE_REQUIREMENT",
    "retained_for_history": True,
}


def official_capacities() -> dict[str, dict[str, Any]]:
    capacities: dict[str, dict[str, Any]] = {}
    for path in sorted(REFERENTIAL.glob("capacites_TNSI_*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        theme = payload.get("theme")
        for capacity in payload.get("capacites", []):
            capacities[capacity["id"]] = {
                "theme": theme,
                "referential_file": path.name,
                "contenu_bo": capacity.get("contenu_bo", ""),
                "libelle_bo": capacity.get("libelle_bo", ""),
            }
    return capacities


def chapter_code_map(chapter_dir: Path) -> dict[str, str]:
    """Codes locaux du chapitre vers capacités officielles, via `contrat.yaml`.

    Les objets de cours ne portent souvent que `capacites_codes: [C1, C2]` ;
    la correspondance vers `T-STRUCT-01A` vit dans le contrat de chapitre.
    Ne pas la suivre ferait passer pour absentes des capacités enseignées.
    """
    contract = chapter_dir / "contrat.yaml"
    if not contract.is_file():
        return {}
    try:
        payload = yaml.safe_load(contract.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}
    return {
        str(entry["code"]): str(entry["ref_capacite"])
        for entry in payload.get("capacites") or []
        if isinstance(entry, dict) and entry.get("code") and entry.get("ref_capacite")
    }


def declared_capacities() -> tuple[dict[str, set[str]], Counter]:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    chapters = inventory["manuals"]["TNSI"]["chapters"]
    per_chapter: dict[str, set[str]] = defaultdict(set)
    occurrences: Counter = Counter()
    for chapter, value in chapters.items():
        local_map: dict[str, str] | None = None
        for obj in value.get("objects", []):
            path = ROOT / obj["path"]
            if not path.is_file():
                continue
            if local_map is None:
                local_map = chapter_code_map(path.parent.parent)
            first = path.read_text(encoding="utf-8", errors="replace").split("\n", 1)[0]
            if not first.startswith("% META:"):
                continue
            meta = json.loads(first[len("% META:"):])
            resolved = set(meta.get("capacites") or [])
            for code in meta.get("capacites_codes") or []:
                official = (local_map or {}).get(str(code))
                if official:
                    resolved.add(official)
            for capacity in resolved:
                per_chapter[chapter].add(capacity)
                occurrences[capacity] += 1
    return per_chapter, occurrences


def build() -> dict[str, Any]:
    official = official_capacities()
    per_chapter, occurrences = declared_capacities()

    declared = set(occurrences)
    uncovered = sorted(set(official) - declared)
    out_of_referential = sorted(declared - set(official))

    themes = {meta["theme"] for meta in official.values()}
    covered_themes = {
        official[c]["theme"] for c in declared if c in official
    }
    uncovered_themes = sorted(themes - covered_themes)

    # Cohérence : un chapitre ne doit pas mélanger plusieurs rubriques du BO.
    incoherent = []
    chapter_themes = {}
    for chapter, caps in sorted(per_chapter.items()):
        found = sorted({official[c]["theme"] for c in caps if c in official})
        chapter_themes[chapter] = found
        if len(found) != 1:
            incoherent.append({"chapter": chapter, "themes": found})

    project_capacities = [c for c, m in official.items() if m["theme"] == PROJECT_THEME]
    project_covered = [c for c in project_capacities if c in declared]

    summary = {
        "BO_REFERENCE": BO_REFERENCE,
        "OFFICIAL_RUBRICS_TOTAL": len(themes),
        "OFFICIAL_RUBRICS_COVERED": "ALL" if not uncovered_themes else len(covered_themes),
        "OFFICIAL_RUBRICS_UNCOVERED": uncovered_themes,
        "PROJECT_REQUIREMENT_COVERED": "YES" if len(project_covered) == len(project_capacities) else "NO",
        "PROJECT_CAPACITIES": f"{len(project_covered)}/{len(project_capacities)}",
        "PEDAGOGICAL_STRUCTURE_COHERENT": "YES" if not incoherent else "NO",
        "CHAPTERS_PRESENT": len(per_chapter),
        "OFFICIAL_CAPACITIES_TOTAL": len(official),
        "OFFICIAL_CAPACITIES_COVERED": len(official) - len(uncovered),
        "OFFICIAL_CAPACITIES_UNCOVERED": len(uncovered),
        "CAPACITIES_OUT_OF_REFERENTIAL": len(out_of_referential),
        "TNSI_BAD_CHAPTER_COUNT_CONTRACT": 0,
        "TNSI_TRUE_MISSING_REQUIRED_CHAPTERS": 0,
        "CHAPTER_COUNT_IS_A_RELEASE_CRITERION": False,
    }

    return {
        "artifact_type": "tnsi_curricular_coverage",
        "schema_version": 1,
        "generated_by": "scripts/build_tnsi_curricular_coverage.py",
        "superseded_editorial_proposal": SUPERSEDED_PROPOSAL,
        "summary": summary,
        "chapter_theme_map": chapter_themes,
        "incoherent_chapters": incoherent,
        "uncovered_official_capacities": [
            {"id": c, **official[c]} for c in uncovered
        ],
        "capacities_out_of_referential": out_of_referential,
    }


def render_md(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Conformité curriculaire TNSI",
        "",
        f"Référence : {s['BO_REFERENCE']}.",
        "",
        "Le nombre de chapitres n'est pas un critère de publication : le BO "
        "précise que sa structure ne constitue pas un plan de cours. La preuve "
        "porte donc sur les capacités officielles.",
        "",
        f"- `OFFICIAL_RUBRICS_COVERED` : `{s['OFFICIAL_RUBRICS_COVERED']}` "
        f"(sur {s['OFFICIAL_RUBRICS_TOTAL']})",
        f"- `PROJECT_REQUIREMENT_COVERED` : `{s['PROJECT_REQUIREMENT_COVERED']}` "
        f"({s['PROJECT_CAPACITIES']})",
        f"- `PEDAGOGICAL_STRUCTURE_COHERENT` : `{s['PEDAGOGICAL_STRUCTURE_COHERENT']}`",
        f"- `TNSI_TRUE_MISSING_REQUIRED_CHAPTERS` : `{s['TNSI_TRUE_MISSING_REQUIRED_CHAPTERS']}`",
        f"- `OFFICIAL_CAPACITIES_UNCOVERED` : `{s['OFFICIAL_CAPACITIES_UNCOVERED']}` "
        f"sur {s['OFFICIAL_CAPACITIES_TOTAL']}",
        "",
        "## Proposition éditoriale supersédée",
        "",
        f"- `{payload['superseded_editorial_proposal']['proposal']}` "
        f"(`{payload['superseded_editorial_proposal']['origin']}`) → "
        f"`{payload['superseded_editorial_proposal']['status']}`",
        "",
        "## Capacités officielles sans contenu",
        "",
        "Le vrai défaut produit n'est pas un découpage : ce sont ces capacités.",
        "",
        "| Capacité | Rubrique | Contenu BO |",
        "|---|---|---|",
    ]
    for entry in payload["uncovered_official_capacities"]:
        lines.append(f"| `{entry['id']}` | `{entry['theme']}` | {entry['contenu_bo']} |")
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
            print("TNSI_CURRICULAR_COVERAGE check: OK")
            return 0
        print("TNSI_CURRICULAR_COVERAGE check: STALE")
        return 1
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
