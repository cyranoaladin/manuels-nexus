#!/usr/bin/env python3
"""Recalcule la dette QCM à partir des sources JSON et des contrats courants."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
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

MATH_ROOT = ROOT / "Mathematiques" / "manuel-maths"
CHAPTER_ROOT = MATH_ROOT / "chapitres"
CHAPTER_ROOTS = (CHAPTER_ROOT, ROOT / "NSI" / "chapitres")
TARGET = ROOT / "audit" / "QCM_CAPACITY_COVERAGE_DEBT.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _display_path(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def _qcm_sources(chapter_root: Path | None = None) -> list[Path]:
    roots = (chapter_root,) if chapter_root is not None else CHAPTER_ROOTS
    paths = sorted(
        path for root in roots for path in root.glob("*/qcm/*-QCM.json")
    )
    counts: dict[str, int] = {}
    for path in paths:
        chapter = path.parent.parent.name
        counts[chapter] = counts.get(chapter, 0) + 1
    duplicates = sorted(chapter for chapter, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError("MULTIPLE_QCM_SOURCES: " + ", ".join(duplicates))
    return paths


def _contract_sources(chapter_root: Path | None = None) -> list[Path]:
    roots = (chapter_root,) if chapter_root is not None else CHAPTER_ROOTS
    return sorted(path for root in roots for path in root.glob("*/contrat.yaml"))


def _source_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(_display_path(path).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _distractor_gaps(question: dict[str, Any]) -> list[str]:
    """Retourne exactement les lacunes que contrôle le gate source-unique."""
    if "options" not in question:
        return []
    correct = question["correcte"]
    if correct not in question["options"]:
        raise ValueError(
            f"{question.get('id', '?')}: la réponse correcte ne figure pas parmi les options"
        )

    gaps: list[str] = []
    diagnostics = question.get("diagnostics", {})
    if correct in diagnostics:
        raise ValueError(f"{question.get('id', '?')}: diagnostic attaché à la bonne réponse")
    for option in question["options"]:
        if option == correct:
            continue
        diagnostic = diagnostics.get(option)
        if not diagnostic:
            gaps.append(f"{option}:absent")
            continue
        if not diagnostic.get("erreur", "").strip():
            gaps.append(f"{option}:erreur-vide")
        if not diagnostic.get("renvoi", "").strip():
            gaps.append(f"{option}:renvoi-vide")
    return sorted(gaps)


def build_debt(
    *,
    resolver: CapacityIdentityResolver | None = None,
    chapter_root: Path | None = None,
) -> dict[str, Any]:
    resolver = resolver or CapacityIdentityResolver.from_corpora()
    missing_by_chapter: dict[str, list[str]] = {}
    distractor_gaps_by_chapter: dict[str, dict[str, list[str]]] = {}
    source_inputs: list[dict[str, Any]] = []
    source_paths: list[Path] = []
    total_questions = 0

    qcm_paths = _qcm_sources(chapter_root)
    qcm_by_chapter = {path.parent.parent.name: path for path in qcm_paths}
    contract_paths = _contract_sources(chapter_root)
    contract_chapters = {path.parent.name for path in contract_paths}
    orphan_qcm = sorted(set(qcm_by_chapter) - contract_chapters)
    if orphan_qcm:
        raise FileNotFoundError(
            "QCM_WITHOUT_CONTRACT: " + ", ".join(orphan_qcm)
        )

    for contract_path in contract_paths:
        chapter = contract_path.parent.name
        qcm_path = qcm_by_chapter.get(chapter)
        contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
        if contract["chapitre"] != chapter:
            raise ValueError(f"identité de chapitre incohérente: {chapter}")

        qcm = (
            json.loads(qcm_path.read_text(encoding="utf-8"))
            if qcm_path is not None
            else {"chapitre": chapter, "questions": []}
        )
        if qcm["chapitre"] != chapter:
            raise ValueError(f"identité de chapitre incohérente: {chapter}")

        questions = qcm["questions"]
        total_questions += len(questions)
        expected = {
            identity.local_code for identity in resolver.capacities_of(chapter)
        }
        questioned: set[str] = set()
        for question in questions:
            resolution = resolver.resolve(chapter, question.get("capacite"))
            if resolution.rule == PREREQUISITE:
                raise UnresolvedCapacityIdentity(
                    f"{chapter}/{question.get('id')}: prerequis utilise "
                    "comme capacite QCM"
                )
            questioned.add(resolution.identity.local_code)
        missing = sorted(expected - questioned)
        if missing:
            missing_by_chapter[chapter] = missing

        chapter_gaps: dict[str, list[str]] = {}
        for question in questions:
            gaps = _distractor_gaps(question)
            if gaps:
                chapter_gaps[question["id"]] = gaps
        if chapter_gaps:
            distractor_gaps_by_chapter[chapter] = chapter_gaps

        source_paths.append(contract_path)
        if qcm_path is not None:
            source_paths.append(qcm_path)
        source_inputs.append(
            {
                "chapter": chapter,
                "qcm_path": _display_path(qcm_path) if qcm_path else None,
                "qcm_sha256": f"sha256:{_sha256(qcm_path)}" if qcm_path else None,
                "contract_path": _display_path(contract_path),
                "contract_sha256": f"sha256:{_sha256(contract_path)}",
                "question_count": len(questions),
                "contract_capacity_count": len(expected),
            }
        )

    total_missing = sum(len(items) for items in missing_by_chapter.values())
    total_distractor_gaps = sum(
        len(gaps)
        for questions in distractor_gaps_by_chapter.values()
        for gaps in questions.values()
    )
    debt_open = bool(total_missing or total_distractor_gaps)
    return {
        "schema_version": 2,
        "artifact_name": "QCM_CAPACITY_COVERAGE_DEBT",
        "status": "PENDING_CONTENT_LOT" if debt_open else "CLOSED_OBJECTIVE_ZERO",
        "reason": (
            "Registre déterministe des capacités contractuelles sans question QCM et "
            "des distracteurs sans diagnostic/renvoi complet. Une ligne disparaît "
            "uniquement lorsque la source et le contrat courants prouvent sa clôture."
        ),
        "no_go_carrier": (
            "release-strict — toute dette non nulle reste bloquante; "
            "un zéro objectif ne vaut pas approbation humaine"
        ),
        "methodology": {
            "capacity_debt": "contract capacites.code minus QCM questions.capacite",
            "distractor_debt": "every wrong option requires non-empty erreur and renvoi",
            "source_currentness": "whole-file SHA256 for every QCM JSON and contrat.yaml",
            "human_approval_inferred": False,
        },
        "source_digest": _source_digest(sorted(source_paths)),
        "source_inputs": source_inputs,
        "inventory": {
            "qcm_files": len(qcm_paths),
            "chapters": len(source_inputs),
            "questions": total_questions,
        },
        "missing_by_chapter": missing_by_chapter,
        "total_missing": total_missing,
        "distractor_gaps_by_chapter": distractor_gaps_by_chapter,
        "total_distractor_gaps": total_distractor_gaps,
        "objective_zero": not debt_open,
        "human_approval_complete": False,
    }


def _render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = _render(build_debt())
    if args.check:
        if not TARGET.is_file() or TARGET.read_text(encoding="utf-8") != rendered:
            print(f"stale: {TARGET.relative_to(ROOT)}")
            return 1
        print(f"current: {TARGET.relative_to(ROOT)}")
        return 0
    TARGET.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
