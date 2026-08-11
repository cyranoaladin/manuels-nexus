#!/usr/bin/env python3
"""Check evaluation distribution across annual sessions and monthly load."""
from __future__ import annotations

import sys
from pathlib import Path
from scripts._session_checks import LEVELS, parse_sessions, parse_table_hours, fail_or_pass

PERIOD_MONTHS = [
    {"septembre", "octobre"},
    {"novembre", "décembre"},
    {"janvier", "février"},
    {"mars", "avril"},
    {"mai", "juin"},
]


def main() -> int:
    errors: list[str] = []
    for level, config in LEVELS.items():
        sessions = parse_sessions(Path(str(config["session"])))
        monthly = parse_table_hours(Path(str(config["monthly"])))
        evaluations = [s for s in sessions if s.get("Nature") == "évaluation"]
        if not any(s.get("Mois") == "septembre" and "diagnostic" in str(s.get("Objectif", "")).lower() for s in evaluations):
            errors.append(f"{level}: missing September diagnostic evaluation")
        for index, months in enumerate(PERIOD_MONTHS, 1):
            if not any(str(s.get("Mois", "")).lower() in months for s in evaluations):
                errors.append(f"{level}: missing short evaluation in period {index}")
        if not any("TP" in str(s.get("Document utilisé", "")) or "pratique" in str(s.get("Objectif", "")).lower() for s in evaluations):
            errors.append(f"{level}: missing practical evaluation")
        if not any("projet" in str(s.get("Objectif", "")).lower() or "projet" in str(s.get("Livrable", "")).lower() for s in evaluations):
            errors.append(f"{level}: missing project evaluation")
        for idx, session in enumerate(sessions[:-1]):
            if session.get("Nature") == "évaluation":
                following = sessions[idx + 1]
                if following.get("Nature") != "remédiation":
                    errors.append(f"{level}: {session.get('id')} not followed by remediation")
        monthly_eval = sum(float(row["evaluation"]) for row in monthly.values())
        session_eval = sum(float(s.get("hours", 0.0)) for s in evaluations)
        if abs(monthly_eval - session_eval) > 0.01:
            errors.append(f"{level}: monthly evaluation {monthly_eval:g} h != session evaluation {session_eval:g} h")
        if level == "premiere" and monthly_eval <= 0.0:
            errors.append("premiere: monthly evaluation total is zero")
    return fail_or_pass("check_evaluation_distribution", errors)


if __name__ == "__main__":
    sys.exit(main())
