#!/usr/bin/env python3
"""Diff sémantique entre le référentiel 2019 et l'autorité 2026 du second degré.

Migrer une autorité ne consiste pas à remplacer un NOR dans une métadonnée. Le
programme 2026 réorganise la rubrique : il énonce quatre capacités attendues là
où le référentiel 2019 en portait six, et il introduit des exigences qui
n'existaient pas. Remplacer un texte par un autre masquerait ces mouvements.

Chaque correspondance est donc classée, et les classes qui engagent du contenu
— `NEW_REQUIREMENT`, `SCOPE_CHANGED` — sont celles qui décident si le chapitre
doit être complété.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "audit/1SPE_SECOND_DEGRE_REFERENTIAL_DIFF.json"
OUTPUT_MD = ROOT / "audit/1SPE_SECOND_DEGRE_REFERENTIAL_DIFF.md"

#: Correspondance établie par lecture des deux textes officiels, puce à puce.
#: `evidence` cite ce qui, dans le texte 2026, porte l'exigence.
MAPPING: tuple[dict[str, Any], ...] = (
    {
        "legacy_id": "1SPE-SECOND-DEGRE-C1",
        "legacy_wording": "Determiner les fonctions polynomes du second degre definies sur R. Reconnaitre la forme developpee, factorisee et canonique.",
        "official_2026_ids": ["1SPE-SECOND-DEGRE-2026-C4"],
        "verdict": "WORDING_CHANGED_SAME_EXPECTATION",
        "evidence": "2026 demande de « choisir une forme adaptée (développée réduite, canonique, factorisée) » : la reconnaissance des trois formes reste requise, mais subordonnée à la résolution d'un problème.",
    },
    {
        "legacy_id": "1SPE-SECOND-DEGRE-C2",
        "legacy_wording": "Determiner l'axe de symetrie et le sommet de la parabole. Dresser le tableau de variations de la fonction polynome du second degre.",
        "official_2026_ids": ["1SPE-SECOND-DEGRE-2026-C4"],
        "verdict": "SCOPE_CHANGED",
        "evidence": "2026 ne fait plus de l'axe de symétrie et du sommet une capacité attendue propre à cette rubrique ; les variations n'apparaissent que comme contexte de la capacité C4, l'étude des variations relevant de la rubrique « Variations et courbes représentatives des fonctions ».",
    },
    {
        "legacy_id": "1SPE-SECOND-DEGRE-C3",
        "legacy_wording": "Calculer le discriminant d'une equation du second degre. Determiner les solutions reelles selon le signe du discriminant.",
        "official_2026_ids": ["1SPE-SECOND-DEGRE-2026-D1"],
        "verdict": "UNCHANGED_REQUIREMENT",
        "evidence": "« Discriminant. Résolution d'une équation du second degré » figure aux Contenus 2026, et « Résolution de l'équation du second degré » reste la démonstration exigible.",
    },
    {
        "legacy_id": "1SPE-SECOND-DEGRE-C4",
        "legacy_wording": "Factoriser, si possible, un polynome du second degre. Determiner le signe d'un polynome du second degre a partir de ses racines ou du discriminant.",
        "official_2026_ids": ["1SPE-SECOND-DEGRE-2026-C1", "1SPE-SECOND-DEGRE-2026-C3"],
        "verdict": "SCOPE_CHANGED",
        "evidence": "2026 scinde l'attendu : étudier le signe sous forme factorisée (C1) et factoriser « en diversifiant les stratégies : racine évidente, détection des racines par leur somme et leur produit, identité remarquable, application des formules générales » (C3). Les stratégies nommées sont plus larges qu'en 2019.",
    },
    {
        "legacy_id": "1SPE-SECOND-DEGRE-C5",
        "legacy_wording": "Resoudre une inequation du second degre. Resoudre une equation ou inequation se ramenant au second degre.",
        "official_2026_ids": ["1SPE-SECOND-DEGRE-2026-C4"],
        "verdict": "WORDING_CHANGED_SAME_EXPECTATION",
        "evidence": "L'inéquation est nommée en 2026 comme l'un des cadres de résolution de la capacité C4.",
    },
    {
        "legacy_id": "1SPE-SECOND-DEGRE-C6",
        "legacy_wording": "Modeliser un probleme a l'aide d'une fonction polynome du second degre. Problemes d'optimisation.",
        "official_2026_ids": ["1SPE-SECOND-DEGRE-2026-C4"],
        "verdict": "WORDING_CHANGED_SAME_EXPECTATION",
        "evidence": "L'optimisation est nommée en 2026 comme l'un des cadres de résolution de la capacité C4.",
    },
    {
        "legacy_id": None,
        "legacy_wording": None,
        "official_2026_ids": ["1SPE-SECOND-DEGRE-2026-C2"],
        "verdict": "NEW_REQUIREMENT",
        "evidence": "« Déterminer les fonctions polynômes du second degré s'annulant en deux nombres réels distincts » n'a aucun équivalent dans le référentiel 2019 ; elle repose sur l'expression de la somme et du produit des racines, également nouvelle aux Contenus 2026.",
    },
)


def build() -> dict[str, Any]:
    legacy_path = ROOT / "audit/historique/capacites_1SPE_SECOND_DEGRE_2019.json"
    current = json.loads(
        (ROOT / "Mathematiques/manuel-maths/referentiel/capacites_1SPE_SECOND_DEGRE.json")
        .read_text(encoding="utf-8")
    )
    official_ids = {c["id"] for c in current["capacites"]}

    unmapped = official_ids - {
        oid for entry in MAPPING for oid in entry["official_2026_ids"]
    }
    verdicts = Counter(entry["verdict"] for entry in MAPPING)

    return {
        "artifact_type": "referential_semantic_diff",
        "schema_version": 1,
        "generated_by": "scripts/build_1spe_second_degre_referential_diff.py",
        "chapter": "1SPE-SECOND-DEGRE",
        "legacy_authority": "BO spécial n°1 du 22 janvier 2019",
        "legacy_snapshot": str(legacy_path.relative_to(ROOT)),
        "current_authority": current["authority"],
        "summary": {
            "LEGACY_CAPACITIES": 6,
            "OFFICIAL_2026_CAPACITIES": len(official_ids),
            "UNCHANGED_REQUIREMENT": verdicts.get("UNCHANGED_REQUIREMENT", 0),
            "RENAMED_ONLY": verdicts.get("RENAMED_ONLY", 0),
            "WORDING_CHANGED_SAME_EXPECTATION": verdicts.get("WORDING_CHANGED_SAME_EXPECTATION", 0),
            "SCOPE_CHANGED": verdicts.get("SCOPE_CHANGED", 0),
            "NEW_REQUIREMENT": verdicts.get("NEW_REQUIREMENT", 0),
            "REMOVED_REQUIREMENT": verdicts.get("REMOVED_REQUIREMENT", 0),
            "UNMAPPED_OFFICIAL_CAPACITIES": sorted(unmapped),
            "CONTENT_IMPACTING_VERDICTS": (
                verdicts.get("NEW_REQUIREMENT", 0) + verdicts.get("SCOPE_CHANGED", 0)
            ),
        },
        "mapping": list(MAPPING),
    }


def render_md(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Migration d'autorité — 1SPE second degré",
        "",
        f"- Autorité abandonnée : {payload['legacy_authority']}",
        f"- Autorité applicable : {payload['current_authority']['bulletin']}, "
        f"arrêté `{payload['current_authority']['nor']}`, rentrée "
        f"{payload['current_authority']['effective_school_year']}",
        f"- Capacités 2019 : `{s['LEGACY_CAPACITIES']}` → capacités 2026 : "
        f"`{s['OFFICIAL_2026_CAPACITIES']}`",
        f"- Verdicts engageant du contenu : `{s['CONTENT_IMPACTING_VERDICTS']}`",
        f"- Capacités officielles non couvertes par le diff : "
        f"`{s['UNMAPPED_OFFICIAL_CAPACITIES'] or 'aucune'}`",
        "",
        "| 2019 | 2026 | Verdict |",
        "|---|---|---|",
    ]
    for entry in payload["mapping"]:
        lines.append(
            f"| `{entry['legacy_id'] or '—'}` | "
            f"{', '.join(f'`{i}`' for i in entry['official_2026_ids'])} | "
            f"`{entry['verdict']}` |"
        )
    lines.extend(["", "## Justifications", ""])
    for entry in payload["mapping"]:
        lines.append(f"- `{entry['legacy_id'] or 'NOUVEAU'}` — {entry['evidence']}")
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
            print("1SPE_SECOND_DEGRE_REFERENTIAL_DIFF check: OK")
            return 0
        print("1SPE_SECOND_DEGRE_REFERENTIAL_DIFF check: STALE")
        return 1
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
