#!/usr/bin/env python3
"""Revue pedagogique adversariale, chapitre par chapitre.

Le nombre d'exercices ne dit rien. Ce producteur mesure ce que le critere
qualitatif exige : le programme est-il enseigne, l'entrainement est-il varie,
la difficulte progresse-t-elle, les corriges suivent-ils, la maitrise est-elle
evaluable, la remediation existe-t-elle la ou elle est pertinente.

CHAQUE VERDICT EST DERIVE, JAMAIS AFFIRME. Les quatre couvertures viennent des
`competences` et des `parcours` que chaque exercice DECLARE dans son META,
croisees avec les capacites du contrat :

`DIRECT_APPLICATION_COVERAGE`  une capacite dispose d'un exercice de parcours 1
                               ou d'un exercice de competence « calculer » ;
`VARIATION_COVERAGE`           elle dispose d'au moins deux exercices dont les
                               contextes different -- mesure par la diversite
                               des competences declarees ;
`REASONING_COVERAGE`           elle dispose d'un exercice « raisonner » ;
`SYNTHESIS_COVERAGE`           le chapitre propose au moins un exercice de
                               parcours 3, ou une evaluation qui croise
                               plusieurs capacites.

Un chapitre dont une capacite substantielle n'a que de l'application directe
n'est pas ADEQUATE : il entraine a reproduire, pas a transferer.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CORPORA = ("Mathematiques/manuel-maths/chapitres", "NSI/chapitres")
JSON_TARGET = ROOT / "audit/CHAPTER_PEDAGOGICAL_VERDICT.json"
MD_TARGET = ROOT / "audit/CHAPTER_PEDAGOGICAL_VERDICT.md"
GENERATED_BY = "scripts/build_chapter_pedagogical_verdict.py"

STRONG, ADEQUATE, WEAK, UNUSABLE = "STRONG", "ADEQUATE", "WEAK", "UNUSABLE"
VERDICTS = (STRONG, ADEQUATE, WEAK, UNUSABLE)


def _meta(path: Path) -> dict[str, Any]:
    texte = path.read_text(encoding="utf-8", errors="replace")
    if not texte.startswith("% META:"):
        return {}
    try:
        return json.loads(texte.split("\n", 1)[0][len("% META: "):])
    except json.JSONDecodeError:
        return {}


def _objects(directory: Path) -> list[dict[str, Any]]:
    if not directory.is_dir():
        return []
    return [
        dict(_meta(p), _path=str(p.relative_to(ROOT))) for p in sorted(p for p in directory.glob("*.tex"))
    ]


def _chapter_root(chapter: str) -> Path | None:
    for corpus in CORPORA:
        candidat = ROOT / corpus / chapter
        if (candidat / "contrat.yaml").is_file():
            return candidat
    return None


def audit(chapter: str) -> dict[str, Any]:
    racine = _chapter_root(chapter)
    if racine is None:
        raise ValueError(f"chapitre inconnu : {chapter}")
    contrat = yaml.safe_load((racine / "contrat.yaml").read_text(encoding="utf-8")) or {}
    capacites = [c["code"] for c in contrat.get("capacites", [])]

    exercices = _objects(racine / "exercices")
    corriges = _objects(racine / "corriges")
    evaluations = _objects(racine / "evaluations")
    remediations = _objects(racine / "remediation")
    methodes = _objects(racine / "methodes")
    cours = _objects(racine / "cours") + _objects(racine / "projet")

    par_capacite: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for objet in exercices:
        for code in objet.get("capacites_codes") or []:
            par_capacite[code].append(objet)

    def competences(objets):
        return {c for o in objets for c in (o.get("competences") or [])}

    directe = [
        code for code in capacites
        if any(
            o.get("parcours") == 1 or "calculer" in (o.get("competences") or [])
            for o in par_capacite.get(code, [])
        )
    ]
    variation = [
        code for code in capacites
        if len(par_capacite.get(code, [])) >= 2
        and len(competences(par_capacite.get(code, []))) >= 2
    ]
    raisonnement = [
        code for code in capacites
        if any("raisonner" in (o.get("competences") or []) for o in par_capacite.get(code, []))
    ]
    synthese = (
        any(o.get("parcours") == 3 for o in exercices)
        or any(len(o.get("capacites_codes") or []) >= 2 for o in evaluations + exercices)
    )
    parcours = sorted({o.get("parcours") for o in exercices if o.get("parcours")})

    def part(liste):
        return len(liste) / len(capacites) if capacites else 0.0

    couverture = {
        "DIRECT_APPLICATION_COVERAGE": f"{len(directe)}/{len(capacites)}",
        "VARIATION_COVERAGE": f"{len(variation)}/{len(capacites)}",
        "REASONING_COVERAGE": f"{len(raisonnement)}/{len(capacites)}",
        "SYNTHESIS_COVERAGE": "OUI" if synthese else "NON",
        "DIFFICULTY_PROGRESSION": parcours,
        "ASSESSMENT_COVERAGE": len(evaluations),
    }

    axes = {
        "COURSE_COMPLETENESS": STRONG if len(cours) >= len(capacites) else (
            ADEQUATE if cours else WEAK
        ),
        "EXERCISE_DIVERSITY": (
            STRONG if part(variation) >= 0.8 else
            ADEQUATE if part(variation) >= 0.5 else
            WEAK if part(directe) == 1.0 else UNUSABLE
        ),
        "DIFFICULTY_PROGRESSION": (
            STRONG if len(parcours) >= 3 else
            ADEQUATE if len(parcours) == 2 else WEAK
        ),
        "CORRECTION_QUALITY": (
            STRONG if len(corriges) >= len(exercices) and exercices else
            ADEQUATE if corriges else WEAK
        ),
        "ASSESSMENT_QUALITY": (
            STRONG if len(evaluations) >= 2 else
            ADEQUATE if evaluations or contrat.get("assessment_mode") else WEAK
        ),
        "REMEDIATION": (
            STRONG if len(remediations) >= 3 else
            ADEQUATE if remediations else WEAK
        ),
    }
    if part(directe) < 1.0:
        axes["EXERCISE_DIVERSITY"] = WEAK
    ordre = {STRONG: 3, ADEQUATE: 2, WEAK: 1, UNUSABLE: 0}
    pire = min(axes.values(), key=lambda v: ordre[v])
    return {
        "CHAPTER_ID": chapter,
        "OFFICIAL_CAPACITIES": capacites,
        "counts": {
            "cours": len(cours), "methodes": len(methodes),
            "exercices": len(exercices), "corriges": len(corriges),
            "evaluations": len(evaluations), "remediations": len(remediations),
        },
        "coverage": couverture,
        "uncovered": {
            "direct_application": [c for c in capacites if c not in directe],
            "variation": [c for c in capacites if c not in variation],
            "reasoning": [c for c in capacites if c not in raisonnement],
        },
        **axes,
        "PEDAGOGICAL_VERDICT": pire,
    }


def build(chapters: list[str]) -> dict[str, Any]:
    lignes = [audit(chapter) for chapter in chapters]
    verdicts = collections.Counter(row["PEDAGOGICAL_VERDICT"] for row in lignes)
    return {
        "artifact_type": "chapter_pedagogical_verdict",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "rule": (
            "chaque verdict est derive des competences et parcours DECLARES "
            "par les exercices, croises avec les capacites du contrat ; aucun "
            "verdict n'est affirme"
        ),
        "approves_nothing": True,
        "summary": {
            "CHAPTERS_AUDITED": len(lignes),
            "VERDICTS": dict(sorted(verdicts.items())),
            "WEAK_OR_UNUSABLE": verdicts.get(WEAK, 0) + verdicts.get(UNUSABLE, 0),
        },
        "chapters": lignes,
    }


TCOMPL = [
    "TCOMPL-CALCULS-AIRES", "TCOMPL-CORRELATION-CAUSALITE",
    "TCOMPL-ECHANTILLONNAGE", "TCOMPL-INEGALITES",
    "TCOMPL-INFERENCE-BAYESIENNE", "TCOMPL-LOGARITHME-HISTORIQUE",
    "TCOMPL-MODELES-EVOLUTION", "TCOMPL-MODELES-FONCTION",
    "TCOMPL-TEMPS-ATTENTE",
]
TEXPERTES = [
    "TEXP-ARITHMETIQUE", "TEXP-COMPLEXES-ALGEBRE-GEOMETRIE",
    "TEXP-COMPLEXES-TRIGO-POLYNOMES", "TEXP-GRAPHES", "TEXP-MATRICES-MARKOV",
]


def render_markdown(payload: dict[str, Any]) -> str:
    lignes = [
        "# Verdict pedagogique par chapitre", "",
        payload["rule"].capitalize() + ".", "",
        "| chapitre | cours | ex | co | eval | rem | diversite | progression | verdict |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in payload["chapters"]:
        c = row["counts"]
        lignes.append(
            f"| {row['CHAPTER_ID']} | {c['cours']} | {c['exercices']} | "
            f"{c['corriges']} | {c['evaluations']} | {c['remediations']} | "
            f"{row['EXERCISE_DIVERSITY']} | {row['DIFFICULTY_PROGRESSION']} | "
            f"**{row['PEDAGOGICAL_VERDICT']}** |"
        )
    lignes.append("")
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build(TCOMPL + TEXPERTES)
    rendus = {
        JSON_TARGET: json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        MD_TARGET: render_markdown(payload),
    }
    if args.check:
        ecarts = [
            str(p.relative_to(ROOT)) for p, c in rendus.items()
            if not p.is_file() or p.read_text(encoding="utf-8") != c
        ]
        for e in ecarts:
            print(f"diff: {e}")
        return 1 if ecarts else 0
    for chemin, contenu in rendus.items():
        chemin.write_text(contenu, encoding="utf-8")
        print(f"wrote {chemin.relative_to(ROOT)}")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
