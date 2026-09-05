#!/usr/bin/env python3
"""Ecrire dans le corrige le bareme indicatif que le sujet et la revue etablissent.

Deux evaluations de geometrie reperee ne valuent aucune de leurs questions :
leur sujet annonce quatre points par exercice, sans dire comment les repartir.
Leurs corriges etaient donc les deux seuls du manuel professeur a ne porter
aucun bareme, et c'est tout ce qui restait sous
`TEACHER_MISSING_REQUIRED_CONTENT`.

Ce module materialise cette repartition. Il ne l'invente pas : il la lit dans
`audit/1SPE_EXTERNAL_REVIEW_PROPOSALS.json`, ou elle a deja ete confrontee au
manuel -- chaque question existe, chaque somme tombe sur le total que
l'exercice declare, chaque evaluation totalise vingt points.

Ce qui est ecrit s'appelle « Barème indicatif », et le porteur est celui de la
charte : `\\baremeIndicatif`, que l'edition eleve vide et que l'edition
professeur imprime. Dix-huit corriges d'evaluation sur vingt en portaient deja
un ; ces deux-la rejoignent la regle commune.

La provenance ne ment pas. Cette repartition vient d'une revue externe
automatisee, pas d'un expert humain : elle est enregistree
`DERIVED_FROM_EXTERNAL_REVIEW`, et rien ici ne la qualifie d'approuvee.

Metriques bloquantes : `ALLOCATION_NOT_MATCHING_DECLARED_TOTAL`,
`QUESTION_WITHOUT_ALLOCATION`, `NEGATIVE_OR_NULL_ALLOCATION`,
`QUESTION_COUNTED_TWICE`, `UNKNOWN`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_1spe_bareme_commentary_proposal as proposal  # noqa: E402
from manual_source_surface import MATH, ROOT  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_INDICATIVE_BAREME_MATERIALISATION.json"
MD_TARGET = ROOT / "audit/1SPE_INDICATIVE_BAREME_MATERIALISATION.md"
GENERATED_BY = "scripts/materialise_indicative_baremes.py"
PROPOSALS = ROOT / "audit/1SPE_EXTERNAL_REVIEW_PROPOSALS.json"

PROVENANCE = "DERIVED_FROM_EXTERNAL_REVIEW"
CARRIER = "baremeIndicatif"

#: Le titre d'exercice tel que les corriges d'evaluation l'ecrivent.
# `\\s*$` avalerait la ligne vide qui suit le titre : `\\s` couvre le saut de
# ligne, et l'insertion se retrouverait decalee d'une ligne. Seuls les blancs
# HORIZONTAUX sont donc consommes.
EXERCISE_HEADING = re.compile(
    r"^\\textbf\{Exercice (?P<number>\d+)\b[^}]*\}[^\S\n]*$", re.M
)


class MaterialisationError(RuntimeError):
    """Une preuve manque : le bareme ne peut pas etre materialise."""


def points(value: str) -> Fraction:
    return Fraction(value.split()[0].replace(",", "."))


def render(value: Fraction) -> str:
    number = f"{float(value):g}".replace(".", ",")
    return f"{number} {'pt' if value < 2 else 'pts'}"


def allocations() -> dict[str, dict[int, list[dict[str, Any]]]]:
    """La repartition proposee, groupee par evaluation puis par exercice."""

    if not PROPOSALS.is_file():
        raise MaterialisationError(f"propositions absentes : {PROPOSALS}")
    payload = json.loads(PROPOSALS.read_text(encoding="utf-8"))
    grouped: dict[str, dict[int, list[dict[str, Any]]]] = {}
    for row in payload["georep_allocations"]:
        grouped.setdefault(row["object_id"], {}).setdefault(
            row["exercise"], []
        ).append(row)
    if not grouped:
        raise MaterialisationError("aucune repartition a materialiser")
    return grouped


def current_assessments() -> dict[str, dict[int, dict[str, Any]]]:
    payload = proposal.build()
    return {
        row["object_id"]: {ex["exercise"]: ex for ex in row["exercises"]}
        for row in payload["assessments"]
    }


def correction_path(object_id: str) -> Path:
    chapter = {
        "1SPE-GEOREP-EV-A": "1SPE-GEOMETRIE-REPEREE",
        "1SPE-GEOREP-EV-B": "1SPE-GEOMETRIE-REPEREE",
    }.get(object_id)
    if chapter is None:
        raise MaterialisationError(f"chapitre inconnu pour {object_id}")
    return MATH / "chapitres" / chapter / "evaluations" / f"{object_id}-corrige.tex"


def bareme_line(rows: list[dict[str, Any]]) -> str:
    body = " ; ".join(f"{row['question']} : {row['points']}" for row in rows)
    return "\\" + CARRIER + "{" + body + "}"


def build(write: bool = False) -> dict[str, Any]:
    grouped = allocations()
    current = current_assessments()

    mismatched: list[dict[str, Any]] = []
    unallocated: list[dict[str, Any]] = []
    non_positive: list[dict[str, Any]] = []
    duplicated: list[dict[str, Any]] = []
    materialised: list[dict[str, Any]] = []

    for object_id, exercises in sorted(grouped.items()):
        subject = current.get(object_id)
        if subject is None:
            raise MaterialisationError(f"evaluation absente du manuel : {object_id}")
        path = correction_path(object_id)
        if not path.is_file():
            raise MaterialisationError(f"corrige absent : {path}")
        text = path.read_text(encoding="utf-8")
        if f"\\{CARRIER}" in text:
            # Deja porteur : ce module n'ecrase jamais un bareme existant.
            continue

        total = Fraction(0)
        lines: dict[int, str] = {}
        for number, rows in sorted(exercises.items()):
            declared = [row["question"] for row in subject[number]["questions"]]
            seen = Counter(row["question"] for row in rows)
            twice = [label for label, count in seen.items() if count > 1]
            if twice:
                duplicated.append(
                    {"object_id": object_id, "exercise": number, "questions": twice}
                )
                continue
            missing = [label for label in declared if label not in seen]
            if missing:
                unallocated.append(
                    {"object_id": object_id, "exercise": number, "questions": missing}
                )
                continue
            values = [points(row["points"]) for row in rows]
            if any(value <= 0 for value in values):
                non_positive.append({"object_id": object_id, "exercise": number})
                continue
            allocated = sum(values)
            expected = Fraction(subject[number]["declared_total"].replace(",", "."))
            if allocated != expected:
                mismatched.append(
                    {
                        "object_id": object_id,
                        "exercise": number,
                        "allocated": str(allocated),
                        "declared_total": subject[number]["declared_total"],
                    }
                )
                continue
            total += allocated
            ordered = sorted(rows, key=lambda row: declared.index(row["question"]))
            lines[number] = bareme_line(ordered)

        if len(lines) != len(exercises):
            continue
        if total != 20:
            mismatched.append(
                {"object_id": object_id, "allocated": str(total), "declared_total": "20"}
            )
            continue

        updated = text
        for number, line in sorted(lines.items(), reverse=True):
            heading = next(
                (
                    match
                    for match in EXERCISE_HEADING.finditer(updated)
                    if int(match.group("number")) == number
                ),
                None,
            )
            if heading is None:
                raise MaterialisationError(
                    f"titre d'exercice {number} introuvable dans {path.name}"
                )
            # La convention du corpus : une ligne vide, le bareme, une ligne
            # vide. Le titre d'exercice est deja suivi d'une ligne vide ; on
            # insere donc le bareme puis on en rend une.
            # Le titre est deja suivi d'une ligne vide : inserer « saut, saut,
            # bareme » donne titre / vide / bareme / vide / contenu, la
            # disposition que les dix-huit autres corriges emploient.
            updated = (
                updated[: heading.end()] + "\n\n" + line + updated[heading.end() :]
            )
        if write:
            path.write_text(updated, encoding="utf-8")
        materialised.append(
            {
                "object_id": object_id,
                "correction": path.relative_to(ROOT).as_posix(),
                "carrier": f"\\{CARRIER}",
                "provenance": PROVENANCE,
                "total_points": str(total),
                "lines": [lines[key] for key in sorted(lines)],
            }
        )

    return {
        "artifact_type": "1spe_indicative_bareme_materialisation",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "provenance": PROVENANCE,
        "this_is_not_a_human_expert_approval": (
            "Cette repartition vient d'une revue externe automatisee, deja "
            "confrontee au sujet. Elle est publiee comme « Barème indicatif », "
            "pas comme un bareme approuve par un expert humain, et rien ici ne "
            "la qualifie ainsi."
        ),
        "an_existing_bareme_is_never_overwritten": (
            "Dix-huit corriges d'evaluation sur vingt portaient deja leur "
            "bareme. Ce module n'ecrit que la ou le porteur de charte est "
            "absent."
        ),
        "the_carrier_is_the_charter_one": (
            "`\\baremeIndicatif` est le porteur de la charte : l'edition eleve "
            "le vide, l'edition professeur l'imprime. Aucun nouveau mecanisme "
            "n'est invente."
        ),
        "materialised": materialised,
        "allocations_not_matching_declared_total": mismatched,
        "questions_without_allocation": unallocated,
        "non_positive_allocations": non_positive,
        "questions_counted_twice": duplicated,
        "summary": {
            "ASSESSMENTS_MATERIALISED": len(materialised),
            "ALLOCATION_NOT_MATCHING_DECLARED_TOTAL": len(mismatched),
            "QUESTION_WITHOUT_ALLOCATION": len(unallocated),
            "NEGATIVE_OR_NULL_ALLOCATION": len(non_positive),
            "QUESTION_COUNTED_TWICE": len(duplicated),
            "HUMAN_EXPERT_APPROVALS_CLAIMED": 0,
            "UNKNOWN": 0,
        },
    }


BLOCKING = (
    "ALLOCATION_NOT_MATCHING_DECLARED_TOTAL",
    "QUESTION_WITHOUT_ALLOCATION",
    "NEGATIVE_OR_NULL_ALLOCATION",
    "QUESTION_COUNTED_TWICE",
    "HUMAN_EXPERT_APPROVALS_CLAIMED",
    "UNKNOWN",
)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Barèmes indicatifs matérialisés — 1SPE",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"> {payload['this_is_not_a_human_expert_approval']}",
        "",
        f"> {payload['an_existing_bareme_is_never_overwritten']}",
        "",
        f"> {payload['the_carrier_is_the_charter_one']}",
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    for row in payload["materialised"]:
        lines += [
            "",
            f"## `{row['object_id']}` — {row['total_points']} points",
            "",
            f"Corrigé : `{row['correction']}` · provenance `{row['provenance']}`",
            "",
        ]
        lines += [f"- `{line}`" for line in row["lines"]]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="ne rien ecrire : constater seulement"
    )
    arguments = parser.parse_args(argv)

    try:
        payload = build(write=not arguments.check)
    except (MaterialisationError, proposal.ProposalError) as error:
        print(f"1SPE-BAREME-MATERIALISATION-ERROR: {error}", file=sys.stderr)
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
