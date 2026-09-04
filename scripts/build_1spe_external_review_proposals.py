#!/usr/bin/env python3
"""Ce que la revue externe a recommande — enregistre comme proposition, pas comme verdict.

Une revue externe a examine le kit exporte et rendu deux sortes de
recommandations que la machine ne pouvait pas deriver seule :

* une repartition de points pour les deux evaluations de geometrie reperee,
  dont le sujet ne value aucune question ;
* trois attendus de probabilites conditionnelles, sur des questions dont
  l'enonce ne porte pas de verbe que l'extracteur sache lire.

Ces recommandations entrent ici, et nulle part ailleurs. Elles ne sont pas
ecrites dans les corriges, elles ne deviennent pas un barème materialise, et
surtout elles ne deviennent pas un verdict humain : le champ de provenance dit
`AI_REVIEW_RECOMMENDATION`, aucune identite n'est creee, aucun recu n'est
fabrique. Un enseignant garde la main.

Ce module ne se contente pas de recopier. Il CONFRONTE chaque recommandation
au manuel courant : la question doit exister, sa valeur en points doit etre
celle que la revue a lue, et une repartition doit tomber exactement sur le
total que l'exercice declare. Une recommandation qui ne retrouve pas son objet
est refusee -- c'est la seule facon de ne pas transcrire dans le vide.

Metriques bloquantes : `RECOMMENDATION_WITHOUT_A_QUESTION`,
`ALLOCATION_NOT_MATCHING_DECLARED_TOTAL`, `POINTS_DISAGREEING_WITH_SUBJECT`,
`UNKNOWN`.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_1spe_bareme_commentary_proposal as proposal  # noqa: E402
from manual_source_surface import ROOT  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_EXTERNAL_REVIEW_PROPOSALS.json"
MD_TARGET = ROOT / "audit/1SPE_EXTERNAL_REVIEW_PROPOSALS.md"
GENERATED_BY = "scripts/build_1spe_external_review_proposals.py"

PROVENANCE = "AI_REVIEW_RECOMMENDATION"
REVIEWED_KIT_SHA256 = (
    "cccb36e8f7c9c160c5a86df47fc4fce66a270503487dddd9fe2cd74b7d063fef"
)

# La grille de geometrie reperee, telle que la revue l'a rendue : la meme pour
# les deux variantes, quatre points par exercice, vingt en tout. L'ordre des
# valeurs suit l'ordre des questions de l'exercice.
GEOREP_ALLOCATION = {
    1: ["1", "1", "1,5", "0,5"],
    2: ["1", "2", "1"],
    3: ["1", "0,5", "0,5", "2"],
    4: ["1,5", "0,5", "2"],
    5: ["1,5", "1,5", "1"],
}
GEOREP_RATIONALE = (
    "Les taches directes portent moins de poids que les constructions, les "
    "deductions, les systemes, les completions de carre ou le projete "
    "orthogonal."
)
GEOREP_OBJECTS = ("1SPE-GEOREP-EV-A", "1SPE-GEOREP-EV-B")

# Les trois attendus de probabilites conditionnelles, avec le geste que la
# revue leur reconnait et le resultat qu'elle attend.
PROBABILITY_EXPECTATIONS = (
    {
        "object_id": "1SPE-PROBCOND-EV-A",
        "exercise": 1,
        "question": "Q4",
        "points": "1 pt",
        "gesture": "calculer",
        "expected": (
            "calculer une probabilite conditionnelle inverse et obtenir "
            "$P_G(R) = \\dfrac{3}{4}$"
        ),
    },
    {
        "object_id": "1SPE-PROBCOND-EV-A",
        "exercise": 2,
        "question": "Q4",
        "points": "1 pt",
        "gesture": "interpréter",
        "expected": (
            "interpreter la valeur predictive positive, environ $41\\,\\%$ : un "
            "test positif seul ne suffit pas a poser un diagnostic individuel, "
            "une confirmation est necessaire"
        ),
    },
    {
        "object_id": "1SPE-PROBCOND-EV-B",
        "exercise": 1,
        "question": "Q4",
        "points": "1 pt",
        "gesture": "calculer",
        "expected": (
            "calculer la probabilite conditionnelle inverse et obtenir "
            "$P_G(B) = \\dfrac{3}{5}$"
        ),
    },
)


class ExternalReviewError(RuntimeError):
    """Une preuve manque : la recommandation ne peut pas etre confrontee."""


def points(value: str) -> Fraction:
    return Fraction(value.replace(",", "."))


def current_assessments() -> dict[str, dict[int, list[dict[str, Any]]]]:
    """Le manuel courant, tel que le producteur de propositions le lit."""

    payload = proposal.build()
    current: dict[str, dict[int, list[dict[str, Any]]]] = {}
    for assessment in payload["assessments"]:
        current[assessment["object_id"]] = {
            exercise["exercise"]: exercise for exercise in assessment["exercises"]
        }
    if not current:
        raise ExternalReviewError("aucune evaluation lue dans le manuel courant")
    return current


def build() -> dict[str, Any]:
    current = current_assessments()

    missing: list[dict[str, Any]] = []
    mismatched_total: list[dict[str, Any]] = []
    disagreeing_points: list[dict[str, Any]] = []
    allocations: list[dict[str, Any]] = []
    expectations: list[dict[str, Any]] = []

    for object_id in GEOREP_OBJECTS:
        exercises = current.get(object_id)
        if exercises is None:
            missing.append({"object_id": object_id})
            continue
        assessment_total = Fraction(0)
        for number, values in GEOREP_ALLOCATION.items():
            exercise = exercises.get(number)
            if exercise is None:
                missing.append({"object_id": object_id, "exercise": number})
                continue
            questions = [row["question"] for row in exercise["questions"]]
            if len(questions) != len(values):
                mismatched_total.append(
                    {
                        "object_id": object_id,
                        "exercise": number,
                        "questions": questions,
                        "allocation": values,
                        "why": "la repartition ne couvre pas les memes questions",
                    }
                )
                continue
            total = sum(points(value) for value in values)
            declared = Fraction(exercise["declared_total"].replace(",", "."))
            if total != declared:
                mismatched_total.append(
                    {
                        "object_id": object_id,
                        "exercise": number,
                        "allocated": str(total),
                        "declared_total": exercise["declared_total"],
                        "why": "la somme ne tombe pas sur le total declare",
                    }
                )
                continue
            assessment_total += total
            for label, value in zip(questions, values):
                allocations.append(
                    {
                        "object_id": object_id,
                        "exercise": number,
                        "question": label,
                        "points": f"{value} pt" + ("s" if points(value) >= 2 else ""),
                        "provenance": PROVENANCE,
                        "status": "PROPOSED_BY_EXTERNAL_REVIEW",
                    }
                )
        if assessment_total and assessment_total != 20:
            mismatched_total.append(
                {
                    "object_id": object_id,
                    "allocated": str(assessment_total),
                    "declared_total": "20",
                    "why": "l'evaluation ne totalise pas vingt points",
                }
            )

    for row in PROBABILITY_EXPECTATIONS:
        exercises = current.get(row["object_id"])
        exercise = (exercises or {}).get(row["exercise"])
        question = next(
            (
                candidate
                for candidate in (exercise or {}).get("questions", [])
                if candidate["question"] == row["question"]
            ),
            None,
        )
        if question is None:
            missing.append(
                {
                    "object_id": row["object_id"],
                    "exercise": row["exercise"],
                    "question": row["question"],
                }
            )
            continue
        if question["points"] != row["points"]:
            disagreeing_points.append(
                {
                    "object_id": row["object_id"],
                    "question": row["question"],
                    "subject_says": question["points"],
                    "review_says": row["points"],
                }
            )
            continue
        expectations.append(
            {
                **row,
                "provenance": PROVENANCE,
                "status": "PROPOSED_BY_EXTERNAL_REVIEW",
                "machine_verdict_before": question["verdict"],
            }
        )

    return {
        "artifact_type": "1spe_external_review_proposals",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "approves_nothing": True,
        "provenance": PROVENANCE,
        "reviewed_kit_sha256": REVIEWED_KIT_SHA256,
        "this_is_not_a_human_verdict": (
            "Ces recommandations viennent d'une revue externe automatisee. "
            "Elles ne portent aucune identite humaine, ne valent aucun recu, "
            "et ne sont ecrites dans aucun corrige. Elles entrent dans le "
            "dossier de revue comme propositions, au meme titre que celles que "
            "la machine derive du sujet et du corrige."
        ),
        "nothing_is_materialised": (
            "Aucun barème n'est materialise ici : la materialisation attend une "
            "cloture humaine reelle."
        ),
        "each_recommendation_is_confronted_to_the_manual": (
            "Une recommandation qui ne retrouve pas sa question, dont la somme "
            "ne tombe pas sur le total declare, ou dont la valeur en points "
            "contredit le sujet, est refusee plutot qu'enregistree."
        ),
        "georep_rationale": GEOREP_RATIONALE,
        "georep_allocations": allocations,
        "probability_expectations": expectations,
        "recommendations_without_a_question": missing,
        "allocations_not_matching_declared_total": mismatched_total,
        "points_disagreeing_with_subject": disagreeing_points,
        "summary": {
            "GEOREP_ALLOCATIONS": len(allocations),
            "PROBABILITY_EXPECTATIONS": len(expectations),
            "RECOMMENDATION_WITHOUT_A_QUESTION": len(missing),
            "ALLOCATION_NOT_MATCHING_DECLARED_TOTAL": len(mismatched_total),
            "POINTS_DISAGREEING_WITH_SUBJECT": len(disagreeing_points),
            "MATERIALISED_BAREMES": 0,
            "HUMAN_RECEIPTS_CREATED": 0,
            "UNKNOWN": 0,
        },
    }


BLOCKING = (
    "RECOMMENDATION_WITHOUT_A_QUESTION",
    "ALLOCATION_NOT_MATCHING_DECLARED_TOTAL",
    "POINTS_DISAGREEING_WITH_SUBJECT",
    "MATERIALISED_BAREMES",
    "HUMAN_RECEIPTS_CREATED",
    "UNKNOWN",
)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Recommandations de la revue externe — 1SPE",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"> {payload['this_is_not_a_human_verdict']}",
        "",
        f"> {payload['nothing_is_materialised']}",
        "",
        f"> {payload['each_recommendation_is_confronted_to_the_manual']}",
        "",
        f"Kit examine : `{payload['reviewed_kit_sha256'][:24]}…`",
        "",
        "## Metriques",
        "",
        "| Metrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    lines += [
        "",
        "## Geometrie reperee — repartition proposee",
        "",
        f"> {payload['georep_rationale']}",
        "",
        "| Evaluation | Exercice | Question | Points |",
        "|---|---:|---|---:|",
    ]
    for row in payload["georep_allocations"]:
        lines.append(
            f"| `{row['object_id']}` | {row['exercise']} | `{row['question']}` | "
            f"{row['points']} |"
        )
    lines += ["", "## Probabilites conditionnelles — attendus proposes", ""]
    for row in payload["probability_expectations"]:
        lines += [
            f"### `{row['object_id']}` / Ex{row['exercise']} / `{row['question']}`"
            f" — {row['points']}",
            "",
            row["expected"],
            "",
            f"Verdict machine avant cette proposition : `{row['machine_verdict_before']}`.",
            "",
        ]
    for title, rows in (
        ("Recommandations sans question", payload["recommendations_without_a_question"]),
        (
            "Repartitions ne tombant pas sur le total",
            payload["allocations_not_matching_declared_total"],
        ),
        ("Points en desaccord avec le sujet", payload["points_disagreeing_with_subject"]),
    ):
        if rows:
            lines += ["", f"## {title}", ""]
            lines += [f"- `{json.dumps(row, ensure_ascii=False)}`" for row in rows]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien ecrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build()
    except (ExternalReviewError, proposal.ProposalError) as error:
        print(f"1SPE-EXTERNAL-REVIEW-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"ecrit {JSON_TARGET.name} et {MD_TARGET.name}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    return 1 if any(payload["summary"][name] for name in BLOCKING) else 0


if __name__ == "__main__":
    raise SystemExit(main())
