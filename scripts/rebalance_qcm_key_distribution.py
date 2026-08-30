#!/usr/bin/env python3
"""Reequilibre la distribution des cles d'un QCM sans toucher aux mathematiques.

Politique editoriale Nexus, et non exigence du B.O. : les quatre positions sont
employees, l'ecart entre la plus et la moins frequente vaut au plus 1, et deux
bonnes reponses consecutives au plus portent la meme lettre.

La seule operation autorisee est la PERMUTATION : le contenu de l'option
correcte et celui d'une autre option echangent leur lettre, en emportant leur
diagnostic. Aucun enonce, aucune valeur, aucune bonne reponse n'est modifie ;
seule sa position change. Les invariants sont verifies question par question,
et le solveur independant retrouve ensuite la bonne reponse a sa nouvelle
lettre, ce qui prouve que la permutation a preserve la verite.

Une question dont la bonne reponse est designee par son contenu -- "la reponse
A", "les deux premieres" -- ne peut pas etre permutee sans changer de sens :
elle est refusee, jamais permutee au jugé.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import qcm_independent_solver as solver  # noqa: E402

LETTERS = ("A", "B", "C", "D")
SPREAD_MAX = 1
RUN_MAX = 2

#: Une option qui NOMME une lettre ne peut pas changer de place sans mentir.
_SELF_REFERENTIAL = re.compile(
    r"\b(?:r[ée]ponses?|propositions?|affirmations?|items?)\s+[A-D]\b"
    r"|\b[A-D]\s+et\s+[A-D]\b"
    r"|\bpremi[èe]re\s+(?:r[ée]ponse|proposition)\b"
    r"|\btoutes\s+les\s+(?:r[ée]ponses|propositions)\b"
    r"|\baucune\s+des\b",
    re.I,
)


class RebalanceRefused(RuntimeError):
    """Levee quand la permutation ne peut pas preserver le sens."""


def _plain(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", str(text))
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn").lower()


def is_permutable(question: dict[str, Any]) -> bool:
    """Une question dont aucune option ne designe une lettre est permutable."""

    if sorted(question.get("options", {})) != list(LETTERS):
        return False
    haystack = " ".join(
        [question.get("enonce", "")]
        + list(question["options"].values())
        + [
            str((entry or {}).get("erreur", ""))
            for entry in (question.get("diagnostics") or {}).values()
        ]
    )
    return not _SELF_REFERENTIAL.search(haystack)


def target_distribution(count: int) -> Counter:
    """Repartition cible la plus plate possible sur les quatre lettres."""

    base, extra = divmod(count, len(LETTERS))
    return Counter({letter: base + (1 if index < extra else 0)
                    for index, letter in enumerate(LETTERS)})


def _swap(question: dict[str, Any], target: str) -> None:
    source = question["correcte"]
    if source == target:
        return
    options = question["options"]
    diagnostics = question.get("diagnostics") or {}
    options[source], options[target] = options[target], options[source]
    moved_source = diagnostics.pop(source, None)
    moved_target = diagnostics.pop(target, None)
    if moved_source is not None:
        diagnostics[target] = moved_source
    if moved_target is not None:
        diagnostics[source] = moved_target
    question["correcte"] = target
    if diagnostics:
        question["diagnostics"] = {k: diagnostics[k] for k in sorted(diagnostics)}


def plan(
    questions: list[dict[str, Any]], fixed: set[str] | None = None
) -> dict[str, str]:
    """Lettre cible de chaque question.

    Les questions non permutables gardent leur lettre : elles sont posees
    d'abord, et le reste s'organise autour d'elles. Sans cela, le planificateur
    croit disposer de toutes les positions et laisse passer des series de trois
    bonnes reponses identiques.
    """

    fixed = fixed or set()
    wanted = target_distribution(len(questions))
    assigned: Counter = Counter()
    plan_by_id: dict[str, str] = {}

    for question in questions:
        if question["id"] in fixed:
            plan_by_id[question["id"]] = question["correcte"]
            assigned[question["correcte"]] += 1

    for index, question in enumerate(questions):
        if question["id"] in fixed:
            continue
        previous = [
            plan_by_id[questions[position]["id"]]
            for position in range(max(0, index - RUN_MAX), index)
            if questions[position]["id"] in plan_by_id
        ]
        following = [
            questions[position]["correcte"]
            for position in range(index + 1, min(len(questions), index + 1 + RUN_MAX))
            if questions[position]["id"] in fixed
        ]
        forbidden = set()
        if len(previous) >= RUN_MAX and len(set(previous[-RUN_MAX:])) == 1:
            forbidden.add(previous[-1])
        if len(following) >= RUN_MAX and len(set(following[:RUN_MAX])) == 1:
            forbidden.add(following[0])

        # Deficitaires d'abord : on comble les lettres les moins servies.
        candidates = sorted(
            (l for l in LETTERS if l not in forbidden),
            key=lambda letter: (assigned[letter] - wanted[letter], letter),
        )
        if not candidates:
            candidates = sorted(LETTERS, key=lambda l: assigned[l] - wanted[l])
        available = [l for l in candidates if assigned[l] < wanted[l]] or candidates
        current = question["correcte"]
        choice = current if current in available[:1] else available[0]
        plan_by_id[question["id"]] = choice
        assigned[choice] += 1
    return plan_by_id


def rebalance(path: Path, *, apply: bool = False) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    questions = document.get("questions", [])
    if not questions:
        return {"chapter": document.get("chapitre"), "status": "EMPTY_QCM"}

    refused = [q["id"] for q in questions if not is_permutable(q)]
    before = Counter(q["correcte"] for q in questions)
    for letter in LETTERS:
        before.setdefault(letter, 0)

    original = {q["id"]: (dict(q["options"]), q["correcte"],
                          {k: dict(v) for k, v in (q.get("diagnostics") or {}).items()})
                for q in questions}
    targets = plan(questions, set(refused))
    moved = []
    for question in questions:
        target = targets[question["id"]]
        if target == question["correcte"]:
            continue
        if question["id"] in refused:
            continue
        _swap(question, target)
        moved.append(question["id"])

    for question in questions:
        options, key, diagnostics = original[question["id"]]
        assert sorted(options.values()) == sorted(question["options"].values())
        assert options[key] == question["options"][question["correcte"]]
        assert {options[k]: diagnostics.get(k) for k in options} == {
            question["options"][k]: (question.get("diagnostics") or {}).get(k)
            for k in question["options"]
        }
        assert question["correcte"] not in (question.get("diagnostics") or {})

    after = Counter(q["correcte"] for q in questions)
    for letter in LETTERS:
        after.setdefault(letter, 0)
    sequence = [q["correcte"] for q in questions]
    run = longest = 1
    for index in range(1, len(sequence)):
        run = run + 1 if sequence[index] == sequence[index - 1] else 1
        longest = max(longest, run)

    disagreements = []
    for question in questions:
        result = solver.solve(solver.sanitize_canonical(question))
        if result.status == "MACHINE_RESOLVED" and result.unique_answer != question["correcte"]:
            disagreements.append(question["id"])
    if disagreements:
        raise RebalanceRefused(
            f"{path.name}: le calcul independant contredit la permutation sur "
            f"{disagreements}"
        )

    spread = max(after.values()) - min(after.values())
    contract_met = (
        spread <= SPREAD_MAX and longest <= RUN_MAX and all(after[l] for l in LETTERS)
    )
    if apply and moved:
        path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return {
        "chapter": document.get("chapitre"),
        "questions": len(questions),
        "before": dict(sorted(before.items())),
        "after": dict(sorted(after.items())),
        "spread": spread,
        "longest_identical_run": longest,
        "moved": moved,
        "refused_self_referential": refused,
        "distribution_contract_met": contract_met,
        "independent_disagreements": 0,
        "status": "COMPLETE" if contract_met else "STILL_OUT_OF_POLICY",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapter", action="append")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    roots = (
        ROOT / "Mathematiques" / "manuel-maths" / "chapitres",
        ROOT / "NSI" / "chapitres",
    )
    paths = [p for root in roots for p in sorted(root.glob("*/qcm/*-QCM.json"))]
    if args.chapter:
        paths = [p for p in paths if p.parts[-3] in set(args.chapter)]
    complete = out = 0
    for path in paths:
        report = rebalance(path, apply=args.apply)
        if report["status"] == "EMPTY_QCM":
            continue
        complete += report["distribution_contract_met"]
        out += not report["distribution_contract_met"]
        print(
            f"{report['chapter']:<34} {report['before']} -> {report['after']} "
            f"spread {report['spread']} serie {report['longest_identical_run']} "
            f"| {len(report['moved'])} permutations | {report['status']}"
        )
        if report["refused_self_referential"]:
            print(f"    refusees (auto-referentielles) : {report['refused_self_referential']}")
    print(f"\nconformes {complete} | hors politique {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
