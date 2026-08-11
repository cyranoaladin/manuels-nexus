#!/usr/bin/env python3
"""Check that session weeks are realistic and consistent with months."""
from __future__ import annotations

import sys
from pathlib import Path
from scripts._session_checks import LEVELS, MONTH_WEEK_RANGES, parse_sessions, session_week, fail_or_pass

REQUIRED_PERIOD_MARKERS = {
    "octobre": ["15 octobre"],
    "décembre": ["17 décembre"],
    "janvier": ["1er janvier"],
    "février": ["Ramadan"],
    "mars": ["Ramadan", "Aïd al-Fitr", "20 mars"],
    "avril": ["9 avril"],
    "mai": ["1er mai", "Aïd al-Adha"],
}


def main() -> int:
    errors: list[str] = []
    for level, config in LEVELS.items():
        for session in parse_sessions(Path(str(config["session"]))):
            sid = str(session.get("id"))
            for field in ["Semaine scolaire", "Semaine civile", "Période", "Mois"]:
                if field not in session:
                    errors.append(f"{level}: {sid} missing {field}")
            if "Date ou semaine" in session:
                errors.append(f"{level}: {sid} still uses obsolete Date ou semaine field")
            week = session_week(session)
            month = str(session.get("Mois", "")).lower()
            if week is None:
                errors.append(f"{level}: {sid} missing numeric school week")
                continue
            if week < 1 or week > 38:
                errors.append(f"{level}: {sid} school week out of range: {week}")
            if month not in MONTH_WEEK_RANGES:
                errors.append(f"{level}: {sid} unknown month: {month}")
            elif week not in MONTH_WEEK_RANGES[month]:
                errors.append(f"{level}: {sid} week {week} inconsistent with month {month}")
            if month == "juin" and week > 38:
                errors.append(f"{level}: {sid} June week exceeds school year range")
            period = str(session.get("Période", ""))
            for marker in REQUIRED_PERIOD_MARKERS.get(month, []):
                if marker not in period:
                    errors.append(f"{level}: {sid} period missing marker {marker}")
    return fail_or_pass("check_session_week_calendar_consistency", errors)


if __name__ == "__main__":
    sys.exit(main())
