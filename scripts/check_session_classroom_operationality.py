#!/usr/bin/env python3
"""Classify sessions beyond simple file links."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT
from scripts.check_session_referenced_files_exist import describe_session, session_blocks


SESSION_FILES = [
    "03_progressions/seances_premiere.md",
    "03_progressions/seances_terminale.md",
]


@dataclass
class SessionClassroomOperationalityResult:
    errors: list[str] = field(default_factory=list)
    linked_count: int = 0
    classroom_ready_count: int = 0
    human_review_pending_count: int = 0
    validated_count: int = 0
    rows: list[dict[str, str]] = field(default_factory=list)


def contains_any(text: str, patterns: list[str]) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in patterns)


def teacher_only_refs(refs: list[str]) -> list[str]:
    return [
        ref for ref in refs
        if re.search(r"corrige|corrigé|bareme|barème|guide_professeur", ref, re.I)
    ]


def classroom_ready(block: str, refs: list[str]) -> tuple[bool, list[str]]:
    missing: list[str] = []
    if teacher_only_refs(refs):
        missing.append("support professeur cité côté élève")
    if not re.search(r"-\s*Objectif\s*:", block, re.I):
        missing.append("objectif absent")
    if not re.search(r"-\s*Déroulé\s*:", block, re.I):
        missing.append("déroulé absent")
    if not re.search(r"-\s*Livrable\s*:", block, re.I):
        missing.append("production attendue absente")
    if not re.search(r"-\s*Différenciation\s*:", block, re.I):
        missing.append("différenciation absente")
    if not contains_any(block, ["devoir ou préparation", "préparation", "prérequis", "rappel"]):
        missing.append("prérequis ou préparation absents")
    if not contains_any(block, ["remédiation", "remediation"]):
        missing.append("remédiation absente")
    if re.search(r"Documents_DRIVE|drive brut|rendus_eleves|NotesEleves|Fichier_Eleves", block, re.I):
        missing.append("ressource sensible ou Drive brute citée")
    return not missing, missing


def analyze_session_classroom_operationality(root: Path = ROOT) -> SessionClassroomOperationalityResult:
    result = SessionClassroomOperationalityResult()
    for relative in SESSION_FILES:
        path = root / relative
        if not path.exists():
            continue
        for session_id, block in session_blocks(path):
            info = describe_session(root, session_id, block)
            linked = bool(info.existing_specific_refs and not info.theoretical)
            ready, missing = classroom_ready(block, info.refs)
            status = "unlinked"
            if linked:
                result.linked_count += 1
                status = "linked"
            if linked and ready:
                result.classroom_ready_count += 1
                status = "classroom_ready"
            if linked:
                result.human_review_pending_count += 1
            result.rows.append(
                {
                    "séance": session_id,
                    "statut": status,
                    "supports": ", ".join(info.existing_specific_refs) if info.existing_specific_refs else "-",
                    "revue": "human_review_pending" if linked else "-",
                    "blocage": "; ".join(missing),
                }
            )
            if not linked:
                result.errors.append(f"{relative}: {session_id}: aucun support existant exploitable")
            elif teacher_only_refs(info.refs):
                result.errors.append(f"{relative}: {session_id}: support professeur cité côté élève")
    return result


def main() -> int:
    result = analyze_session_classroom_operationality()
    print(f"séances linked : {result.linked_count}")
    print(f"séances classroom_ready : {result.classroom_ready_count}")
    print(f"séances human_review_pending : {result.human_review_pending_count}")
    print(f"séances validated : {result.validated_count}")
    print("| séance | statut | supports cités existants | revue | blocage |")
    print("|---|---|---|---|---|")
    for row in result.rows[:260]:
        print(
            "| "
            + " | ".join(row[key].replace("|", "/") for key in ["séance", "statut", "supports", "revue", "blocage"])
            + " |"
        )
    if result.errors:
        print("check_session_classroom_operationality: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print("check_session_classroom_operationality: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
