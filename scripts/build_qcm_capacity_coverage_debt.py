#!/usr/bin/env python3
"""Recalcule la dette QCM à partir des sources JSON et des contrats courants."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
MATH_ROOT = ROOT / "Mathematiques" / "manuel-maths"
CHAPTER_ROOT = MATH_ROOT / "chapitres"
TARGET = ROOT / "audit" / "QCM_CAPACITY_COVERAGE_DEBT.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _qcm_sources() -> list[Path]:
    return sorted(CHAPTER_ROOT.glob("*/qcm/*-QCM.json"))


def _source_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
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


def build_debt() -> dict[str, Any]:
    missing_by_chapter: dict[str, list[str]] = {}
    distractor_gaps_by_chapter: dict[str, dict[str, list[str]]] = {}
    source_inputs: list[dict[str, Any]] = []
    source_paths: list[Path] = []
    total_questions = 0

    for qcm_path in _qcm_sources():
        chapter = qcm_path.parent.parent.name
        contract_path = qcm_path.parent.parent / "contrat.yaml"
        if not contract_path.is_file():
            raise FileNotFoundError(f"contrat absent pour {chapter}: {contract_path}")

        qcm = json.loads(qcm_path.read_text(encoding="utf-8"))
        contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
        if qcm["chapitre"] != chapter or contract["chapitre"] != chapter:
            raise ValueError(f"identité de chapitre incohérente: {chapter}")

        questions = qcm["questions"]
        total_questions += len(questions)
        expected = {item["code"] for item in (contract.get("capacites") or [])}
        questioned = {item["capacite"] for item in questions}
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

        source_paths.extend((qcm_path, contract_path))
        source_inputs.append(
            {
                "chapter": chapter,
                "qcm_path": str(qcm_path.relative_to(ROOT)),
                "qcm_sha256": f"sha256:{_sha256(qcm_path)}",
                "contract_path": str(contract_path.relative_to(ROOT)),
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
            "qcm_files": len(source_inputs),
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
