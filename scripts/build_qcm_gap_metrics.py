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
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
from capacity_identity import (  # noqa: E402
    CapacityIdentityResolver,
    PREREQUISITE,
    UnresolvedCapacityIdentity,
)

CHAPTERS = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"
CHAPTER_ROOTS = (CHAPTERS, ROOT / "NSI" / "chapitres")
COVERAGE = ROOT / "audit" / "OFFICIAL_PROGRAM_COVERAGE_2026_2027.json"
OUTPUT = ROOT / "audit" / "QCM_GAP_METRICS.json"


def _observed_source_sha() -> str:
    """Constat informatif du HEAD au moment de la mesure.

    Ce champ ne dit PAS que l'artefact serait perime des que HEAD avance :
    epingler un artefact de rapport a un SHA le rend auto-perime au commit
    suivant, y compris au commit qui le publie. L'autorite de fraicheur est le
    digest de contenu ci-dessous, non auto-referent.
    """

    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def _chapter_roots(chapters_root: Path | None = None) -> tuple[Path, ...]:
    return (chapters_root,) if chapters_root is not None else CHAPTER_ROOTS


def _source_inputs(chapters_root: Path | None = None) -> list[dict[str, str]]:
    """Les entrees reelles de la mesure : QCM, contrats, couverture officielle."""

    rows: list[dict[str, str]] = []
    inputs = [
        path
        for root in _chapter_roots(chapters_root)
        for path in (
            sorted(root.glob("*/qcm/*-QCM.json"))
            + sorted(root.glob("*/contrat.yaml"))
        )
    ] + [COVERAGE]
    for path in inputs:
        if not path.is_file():
            continue
        rows.append(
            {
                "path": (
                    path.relative_to(ROOT).as_posix()
                    if path.is_relative_to(ROOT)
                    else path.as_posix()
                ),
                "sha256": "sha256:"
                + hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    return rows


def _source_digest(inputs: list[dict[str, str]]) -> str:
    payload = json.dumps(inputs, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _contract(chapter: Path) -> dict[str, Any] | None:
    path = chapter / "contrat.yaml"
    if not path.is_file():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _questions(chapter: Path) -> list[dict[str, Any]]:
    directory = chapter / "qcm"
    questions: list[dict[str, Any]] = []
    if directory.is_dir():
        sources = sorted(directory.glob("*-QCM.json"))
        if len(sources) > 1:
            raise ValueError(f"{chapter.name}: MULTIPLE_QCM_SOURCES")
        for path in sources:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("chapitre") != chapter.name:
                raise ValueError(
                    f"{chapter.name}: QCM_CHAPTER_MISMATCH "
                    f"({payload.get('chapitre')!r})"
                )
            questions += payload.get("questions", [])
    return questions


def _capacity_tokens(raw: Any) -> tuple[str, ...]:
    """Split only the two composite formats documented by the authority."""

    if not isinstance(raw, str) or not raw.strip():
        raise UnresolvedCapacityIdentity("matrice officielle: capacite vide")
    tokens = tuple(part.strip() for part in re.split(r"\s+\+\s+|/", raw))
    if not tokens or any(not token for token in tokens):
        raise UnresolvedCapacityIdentity(
            f"matrice officielle: liste de capacites invalide {raw!r}"
        )
    return tokens


def _mandatory_capacities(resolver: CapacityIdentityResolver) -> set[str]:
    """Canonical UIDs attached to at least one mandatory official atom."""

    if not COVERAGE.is_file():
        return set()
    payload = json.loads(COVERAGE.read_text(encoding="utf-8"))
    mandatory: set[str] = set()
    active_chapters = set(resolver.chapters)
    for row in payload.get("rows", []):
        mandatory_flag = row.get("mandatory")
        if not (
            mandatory_flag is True
            or (
                isinstance(mandatory_flag, str)
                and mandatory_flag.strip().upper() == "YES"
            )
        ):
            continue
        declared_chapters = {
            part.strip()
            for part in str(row.get("chapter") or "").split(" + ")
            if part.strip()
        }
        if declared_chapters and declared_chapters.isdisjoint(active_chapters):
            continue
        if not row.get("contract_capacity"):
            continue
        for token in _capacity_tokens(row["contract_capacity"]):
            mandatory.add(resolver.resolve_collection_alias(token).identity.uid)
    return mandatory


def build_report(
    *,
    resolver: CapacityIdentityResolver | None = None,
    chapters_root: Path | None = None,
) -> dict[str, Any]:
    resolver = resolver or CapacityIdentityResolver.from_corpora()
    mandatory = _mandatory_capacities(resolver)
    pairs_without: list[dict[str, str]] = []
    pairs_total = 0
    capacity_ids: dict[str, bool] = {}
    distractors_total = 0
    distractors_without_diagnostic: list[dict[str, str]] = []
    questions_total = 0
    chapters = 0

    for root in _chapter_roots(chapters_root):
        for chapter in sorted(path for path in root.iterdir() if path.is_dir()):
            contract = _contract(chapter)
            if contract is None:
                continue
            chapters += 1
            questions = _questions(chapter)
            questions_total += len(questions)
            asked: set[str] = set()
            for question in questions:
                resolution = resolver.resolve(chapter.name, question.get("capacite"))
                if resolution.rule == PREREQUISITE:
                    raise UnresolvedCapacityIdentity(
                        f"{chapter.name}/{question.get('id')}: prerequis utilise "
                        "comme capacite QCM"
                    )
                asked.add(resolution.identity.local_code)
            for identity in resolver.capacities_of(chapter.name):
                code = identity.local_code
                reference = identity.official_ref or identity.uid
                pairs_total += 1
                covered = code in asked
                capacity_ids[reference] = capacity_ids.get(reference, False) or covered
                if not covered:
                    pairs_without.append(
                        {
                            "chapter": chapter.name,
                            "capacity_code": code,
                            "capacity_id": reference,
                            "mandatory": identity.uid in mandatory,
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
        "observed_source_sha": _observed_source_sha(),
        "source_digest": _source_digest(_source_inputs(chapters_root)),
        "source_inputs": _source_inputs(chapters_root),
        "freshness_authority": "source_digest",
        "freshness_note": (
            "observed_source_sha est un constat ; il n'est jamais une condition "
            "de fraicheur. Un artefact de rapport epingle a un SHA serait "
            "perime par le commit qui le publie."
        ),
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
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    report = build_report()
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != payload:
            print(f"STALE: {OUTPUT.relative_to(ROOT)}")
            return 1
        print(f"current: {OUTPUT.relative_to(ROOT)}")
    elif args.out:
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
