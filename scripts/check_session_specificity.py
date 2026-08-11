#!/usr/bin/env python3
"""Reject repetitive or generic session descriptions."""
from __future__ import annotations
from typing import Any

import sys
from pathlib import Path
from scripts._session_checks import LEVELS, CONCRETE_TOKENS, GENERIC_PHRASES, count_values, fail_or_pass, parse_sessions


def has_concrete_reference(text: str) -> bool:
    return any(token in text for token in CONCRETE_TOKENS)


def is_theoretical_session(session: dict[str, Any]) -> bool:
    return str(session.get("Statut support", "")).strip().lower() == "théorique non prêt"


def session_specificity_errors(level: str, session: dict[str, Any]) -> list[str]:
    if is_theoretical_session(session):
        return []
    errors: list[str] = []
    sid = str(session.get("id"))
    raw = str(session.get("raw", ""))
    for phrase in GENERIC_PHRASES:
        if phrase in raw:
            errors.append(f"{level}: {sid} contains generic phrase: {phrase}")
    if not has_concrete_reference(str(session.get("Document utilisé", ""))):
        errors.append(f"{level}: {sid} document used is not concrete")
    if not has_concrete_reference(str(session.get("Livrable", ""))):
        errors.append(f"{level}: {sid} deliverable is not concrete")
    objective = str(session.get("Objectif", ""))
    if len(objective.split()) < 8 or not has_concrete_reference(objective + " " + str(session.get("Déroulé", ""))):
        errors.append(f"{level}: {sid} objective lacks precise task")
    if not has_concrete_reference(raw):
        errors.append(f"{level}: {sid} names no exercise, TP, file or concrete activity")
    return errors


def main() -> int:
    errors: list[str] = []
    for level, config in LEVELS.items():
        sessions = parse_sessions(Path(str(config["session"])))
        if not sessions:
            errors.append(f"{level}: no sessions parsed")
            continue
        threshold = max(1, int(len(sessions) * 0.20))
        for field in ["Déroulé", "Différenciation"]:
            for value, count in count_values(sessions, field).items():
                if count > threshold:
                    errors.append(f"{level}: {count} sessions share same {field}: {value[:80]}")
        for session in sessions:
            errors.extend(session_specificity_errors(level, session))
    return fail_or_pass("check_session_specificity", errors)


if __name__ == "__main__":
    sys.exit(main())
