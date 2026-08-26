#!/usr/bin/env python3
"""Les quatre metriques distinctes de lacune QCM.

Le terme « QCM gaps » est interdit : il a designe successivement deux mesures
differentes sur deux arbres differents. Ce controle nomme et calcule quatre
grandeurs distinctes, sur un seul SOURCE_SHA :

UNIQUE_CAPACITY_IDS_WITHOUT_ANY_QCM
    identifiants de capacite canoniques qu'aucune question de QCM n'interroge,
    nulle part dans le corpus ;

CHAPTER_CAPACITY_PAIRS_WITHOUT_ANY_QCM
    couples (chapitre, code de capacite) sans aucune question ;

MANDATORY_ASSESSED_CAPACITY_PAIRS_WITHOUT_QCM
    les memes couples, restreints aux capacites rattachees a un atome officiel
    declare obligatoire par la matrice de couverture ;

PEDAGOGICALLY_REQUIRED_QCM_GAPS
    le sous-ensemble que le cahier des charges Nexus impose de combler ; c'est
    la seule des quatre qui doit tendre vers zero.

S'y ajoute la dette de diagnostic : tout distracteur incorrect doit porter une
erreur documentee ET un renvoi de remediation.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"
COVERAGE = ROOT / "audit" / "OFFICIAL_PROGRAM_COVERAGE_2026_2027.json"


def _source_sha() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def _contract(chapter: Path) -> dict[str, Any] | None:
    path = chapter / "contrat.yaml"
    if not path.is_file():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _questions(chapter: Path) -> list[dict[str, Any]]:
    directory = chapter / "qcm"
    questions: list[dict[str, Any]] = []
    if directory.is_dir():
        for path in sorted(directory.glob("*.json")):
            questions += json.loads(path.read_text(encoding="utf-8")).get("questions", [])
    return questions


def _mandatory_capacities() -> set[str]:
    """Capacites rattachees a au moins un atome officiel obligatoire."""

    if not COVERAGE.is_file():
        return set()
    payload = json.loads(COVERAGE.read_text(encoding="utf-8"))
    return {
        str(row.get("contract_capacity"))
        for row in payload.get("rows", [])
        if row.get("mandatory") and row.get("contract_capacity")
    }


def build_report() -> dict[str, Any]:
    mandatory = _mandatory_capacities()
    pairs_without: list[dict[str, str]] = []
    pairs_total = 0
    capacity_ids: dict[str, bool] = {}
    distractors_total = 0
    distractors_without_diagnostic: list[dict[str, str]] = []
    questions_total = 0
    chapters = 0

    for chapter in sorted(path for path in CHAPTERS.iterdir() if path.is_dir()):
        contract = _contract(chapter)
        if contract is None:
            continue
        chapters += 1
        questions = _questions(chapter)
        questions_total += len(questions)
        asked = {str(item.get("capacite")) for item in questions}
        for entry in contract.get("capacites", []):
            code, reference = entry["code"], entry.get("ref_capacite", "")
            pairs_total += 1
            covered = code in asked
            capacity_ids[reference] = capacity_ids.get(reference, False) or covered
            if not covered:
                pairs_without.append(
                    {
                        "chapter": chapter.name,
                        "capacity_code": code,
                        "capacity_id": reference,
                        "mandatory": reference in mandatory,
                    }
                )
        for question in questions:
            correct = question.get("correcte")
            diagnostics = question.get("diagnostics") or {}
            for option in question.get("options", {}):
                if option == correct:
                    continue
                distractors_total += 1
                entry = diagnostics.get(option) or {}
                if not (entry.get("erreur") and entry.get("renvoi")):
                    distractors_without_diagnostic.append(
                        {
                            "chapter": chapter.name,
                            "question": str(question.get("id")),
                            "option": option,
                            "has_erreur": bool(entry.get("erreur")),
                            "has_renvoi": bool(entry.get("renvoi")),
                        }
                    )

    unique_without = sorted(
        reference for reference, covered in capacity_ids.items() if not covered
    )
    mandatory_without = [row for row in pairs_without if row["mandatory"]]
    by_chapter: dict[str, list[str]] = defaultdict(list)
    for row in pairs_without:
        by_chapter[row["chapter"]].append(row["capacity_code"])

    return {
        "artifact_type": "qcm_gap_metrics",
        "schema_version": 1,
        "generated_by": "scripts/build_qcm_gap_metrics.py",
        "source_sha": _source_sha(),
        "inventory": {
            "chapters": chapters,
            "questions": questions_total,
            "contract_capacity_pairs": pairs_total,
            "distractors": distractors_total,
        },
        "UNIQUE_CAPACITY_IDS_WITHOUT_ANY_QCM": {
            "count": len(unique_without),
            "ids": unique_without,
        },
        "CHAPTER_CAPACITY_PAIRS_WITHOUT_ANY_QCM": {
            "count": len(pairs_without),
            "by_chapter": {key: sorted(value) for key, value in sorted(by_chapter.items())},
        },
        "MANDATORY_ASSESSED_CAPACITY_PAIRS_WITHOUT_QCM": {
            "count": len(mandatory_without),
            "pairs": mandatory_without,
            "authority": "audit/OFFICIAL_PROGRAM_COVERAGE_2026_2027.json, colonne mandatory",
        },
        "PEDAGOGICALLY_REQUIRED_QCM_GAPS": {
            "count": len(mandatory_without),
            "definition": (
                "couple (chapitre, capacite) sans aucune question alors que la capacite "
                "porte un atome officiel obligatoire ; seule metrique dont l'objectif "
                "contractuel est zero"
            ),
            "objective": 0,
        },
        "REQUIRED_DISTRACTOR_WITHOUT_DIAGNOSTIC": {
            "count": len(distractors_without_diagnostic),
            "rule": "tout distracteur incorrect exige une erreur documentee ET un renvoi",
            "objective": 0,
            "entries": distractors_without_diagnostic,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", help="ecrire le rapport JSON")
    args = parser.parse_args(argv)

    report = build_report()
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(
            f"unique={report['UNIQUE_CAPACITY_IDS_WITHOUT_ANY_QCM']['count']} "
            f"pairs={report['CHAPTER_CAPACITY_PAIRS_WITHOUT_ANY_QCM']['count']} "
            f"mandatory={report['MANDATORY_ASSESSED_CAPACITY_PAIRS_WITHOUT_QCM']['count']} "
            f"distractors={report['REQUIRED_DISTRACTOR_WITHOUT_DIAGNOSTIC']['count']}"
        )
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
