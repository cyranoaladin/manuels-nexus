#!/usr/bin/env python3
"""Ce qu'il faut ecrire, capacite par capacite, et POURQUOI.

Un plan d'ecriture qui dirait « ajouter deux exercices » serait une cible de
volume. Celui-ci ne prescrit que des FONCTIONS PEDAGOGIQUES manquantes : la
capacite C4 de TCOMPL-CALCULS-AIRES dispose de deux applications directes et
d'aucune situation de transfert, donc il lui manque une situation de
transfert -- une, pas deux, et pas « au moins deux ».

Chaque entree porte les champs que le mandat exige de tout nouvel objet :

`PEDAGOGICAL_GAP_ID`      identifiant stable de la lacune comblee ;
`CAPACITY_ID`             la capacite visee, avec son enonce officiel ;
`EXERCISE_ROLE`           la fonction pedagogique a produire ;
`DIFFICULTY`              le parcours vise, deduit de ce que le chapitre a
                          deja et de ce qui lui manque ;
`AUTHORING_REASON`        la phrase qui dit ce que l'eleve ne peut pas faire
                          aujourd'hui ;
`ORIGINALITY_PROVENANCE`  d'ou vient la situation.

`AUTHORING_REASON` ne peut jamais valoir `increase_count` ni
`satisfy_diversity_metric` : un producteur qui ecrirait cela avouerait
ecrire pour un compteur. Le contrat de ce fichier l'interdit et un test le
verifie.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from exercise_function_taxonomy import (  # noqa: E402
    CONTEXT,
    DIRECT,
    EDGE,
    MODELLING,
    PROBLEM,
    REASONING,
    SYNTHESIS,
    TRANSFER,
)

VERDICTS = ROOT / "audit/CHAPTER_PEDAGOGICAL_VERDICT.json"
JSON_TARGET = ROOT / "audit/EXERCISE_DIVERSITY_BLUEPRINT.json"
MD_TARGET = ROOT / "audit/EXERCISE_DIVERSITY_BLUEPRINT.md"
GENERATED_BY = "scripts/build_exercise_diversity_blueprint.py"

#: Motifs d'ecriture interdits : ils avouent qu'on ecrit pour un compteur.
FORBIDDEN_REASONS = frozenset({"increase_count", "satisfy_diversity_metric"})

#: Quelle fonction produire, selon ce qui manque et ce qui est deja la.
#: L'ordre compte : on complete d'abord le geste absent, puis le registre.
TRANSFER_PREFERENCE = (CONTEXT, REASONING, PROBLEM, TRANSFER, MODELLING, EDGE)


def _role_manquant(analyse: dict[str, Any]) -> list[str]:
    """Les fonctions a produire pour cette capacite. Souvent une seule."""

    presentes = set(analyse["EXERCISE_NATURES"])
    entree = analyse["ENTRY_FUNCTION"]
    roles: list[str] = []
    if entree not in presentes:
        roles.append(entree)
    if not (presentes | set(roles)) - {entree, SYNTHESIS}:
        # Il manque un second registre. On choisit celui qui complete le
        # mieux ce que la capacite fait deja, en evitant de redemander la
        # fonction d'entree.
        roles.append(
            next(f for f in TRANSFER_PREFERENCE if f != entree and f not in presentes)
        )
    return roles


def _difficulte(analyse: dict[str, Any], role: str) -> int:
    """Le parcours vise : on comble ce que l'etalement ne couvre pas.

    Un geste de base absent s'installe au parcours 1. Une situation de
    transfert se place au-dessus de ce que la capacite propose deja, sans
    depasser le parcours 3.
    """

    if role in {DIRECT, REASONING} and role == analyse["ENTRY_FUNCTION"]:
        return 1
    deja = analyse["DIFFICULTY_SPREAD"] or [1]
    return min(3, max(deja) + 1) if max(deja) < 3 else 3


def _raison(analyse: dict[str, Any], role: str) -> str:
    """Ce que l'eleve ne peut pas faire aujourd'hui. Jamais un compteur."""

    enonce = analyse.get("CAPACITY_STATEMENT") or analyse["CAPACITY_ID"]
    if analyse["CURRENT_EXERCISES"] == 0:
        return (
            f"aucun exercice n'entraine « {enonce} » : l'eleve n'a jamais"
            " l'occasion de l'exercer"
        )
    if role == analyse["ENTRY_FUNCTION"]:
        geste = "demontrer" if role == REASONING else "executer le calcul"
        return (
            f"l'eleve rencontre « {enonce} » sans avoir jamais eu a {geste}"
            " seul : le geste de base n'est installe nulle part"
        )
    return (
        f"« {enonce} » n'est travaille que sous un seul mode"
        f" ({', '.join(sorted(analyse['EXERCISE_NATURES'])).lower()}) :"
        " l'eleve apprend une procedure et ne peut pas la transferer"
    )


def _gap_id(chapter: str, capacity: str, role: str) -> str:
    graine = f"{chapter}:{capacity}:{role}".encode("utf-8")
    return "GAP-" + hashlib.sha256(graine).hexdigest()[:12].upper()


def build() -> dict[str, Any]:
    payload = json.loads(VERDICTS.read_text(encoding="utf-8"))
    chapitres = []
    for row in payload["chapters"]:
        # Un chapitre evalue par projet n'a pas de banque d'exercices : ses
        # capacites apparaissent « sans exercice » parce que le mode
        # d'evaluation en a decide ainsi, pas parce qu'un objet manque.
        if row["EXERCISE_DIVERSITY"] == "NOT_APPLICABLE_PROJECT_ASSESSMENT":
            continue
        lacunes = [a for a in row["per_capacity"] if a["REAL_DIVERSITY_GAP"]]
        if not lacunes:
            continue
        entrees = []
        for analyse in lacunes:
            for role in _role_manquant(analyse):
                entrees.append({
                    "PEDAGOGICAL_GAP_ID": _gap_id(
                        row["CHAPTER_ID"], analyse["CAPACITY_ID"], role
                    ),
                    "CAPACITY_ID": analyse["CAPACITY_ID"],
                    "CAPACITY_STATEMENT": analyse.get("CAPACITY_STATEMENT", ""),
                    "EXERCISE_ROLE": role,
                    "DIFFICULTY": _difficulte(analyse, role),
                    "AUTHORING_REASON": _raison(analyse, role),
                    "ORIGINALITY_PROVENANCE": "ex_nihilo",
                    "CURRENT_EXERCISES": analyse["CURRENT_EXERCISES"],
                    "CURRENT_FUNCTIONS": sorted(analyse["EXERCISE_NATURES"]),
                    "STATUS": "TO_AUTHOR",
                })
        chapitres.append({
            "CHAPTER_ID": row["CHAPTER_ID"],
            "PEDAGOGICAL_VERDICT": row["PEDAGOGICAL_VERDICT"],
            "CURRENT_EXERCISES": row["counts"]["exercices"],
            "OBJECTS_TO_AUTHOR": len(entrees),
            "blueprint": entrees,
        })

    total = sum(c["OBJECTS_TO_AUTHOR"] for c in chapitres)
    roles = collections.Counter(
        e["EXERCISE_ROLE"] for c in chapitres for e in c["blueprint"]
    )
    return {
        "artifact_type": "exercise_diversity_blueprint",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "rule": (
            "le plan ne prescrit que des fonctions pedagogiques absentes ; "
            "aucun effectif cible n'y figure, et aucune entree ne peut avoir "
            "pour motif un compteur"
        ),
        "approves_nothing": True,
        "summary": {
            "CHAPTERS_WITH_BLUEPRINT": len(chapitres),
            "OBJECTS_TO_AUTHOR": total,
            "ROLES_TO_AUTHOR": dict(sorted(roles.items())),
            "FORBIDDEN_AUTHORING_REASONS_USED": 0,
        },
        "chapters": chapitres,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lignes = [
        "# Plan de diversite des exercices", "",
        payload["rule"].capitalize() + ".", "",
        f"{payload['summary']['OBJECTS_TO_AUTHOR']} objets a ecrire sur "
        f"{payload['summary']['CHAPTERS_WITH_BLUEPRINT']} chapitres.", "",
    ]
    for chapitre in payload["chapters"]:
        lignes += [
            f"## {chapitre['CHAPTER_ID']}",
            "",
            "| lacune | capacite | role | parcours | motif |",
            "| --- | --- | --- | ---: | --- |",
        ]
        for entree in chapitre["blueprint"]:
            lignes.append(
                f"| `{entree['PEDAGOGICAL_GAP_ID']}` | {entree['CAPACITY_ID']} | "
                f"{entree['EXERCISE_ROLE']} | {entree['DIFFICULTY']} | "
                f"{entree['AUTHORING_REASON']} |"
            )
        lignes.append("")
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
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
