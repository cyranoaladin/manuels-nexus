#!/usr/bin/env python3
"""Check annual progression alignment with the Tunisia 2026-2027 calendar."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CALENDAR = ROOT / "calendar_2026_2027_tunisia.md"
PREMIERE = ROOT / "03_progressions" / "progression_premiere.md"
TERMINALE = ROOT / "03_progressions" / "progression_terminale.md"
PROGRAMME = ROOT / "00_programmes_officiels" / "programme_nsi_2019.yaml"
AUDIT = ROOT / "progression_audit.md"

MONTHS = [
    "septembre",
    "octobre",
    "novembre",
    "décembre",
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
]

CALENDAR_MARKERS = [
    "898",
    "173",
    "Ramadan",
    "Aïd al-Fitr",
    "Aïd al-Adha",
    "estimation heures NSI Première",
    "estimation heures NSI Terminale",
]

PREMIERE_SEQUENCES = [f"P{i:02d}" for i in range(15)]
TERMINALE_SEQUENCES = [f"T{i:02d}" for i in range(20)]


def read_text(path: Path, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"missing file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def official_ids(programme_text: str, prefix: str) -> set[str]:
    pattern = rf"\b{prefix}-[A-Z]+(?:-[A-Z]+)*-\d+[A-Z]?\b"
    return set(re.findall(pattern, programme_text))


def require_markers(name: str, text: str, markers: list[str], errors: list[str]) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        errors.append(f"{name}: missing markers: {', '.join(missing)}")


def check_progression(
    label: str,
    text: str,
    sequence_ids: list[str],
    ids: set[str],
    expected_total: str,
    expected_project: str,
    errors: list[str],
) -> None:
    lower_text = text.lower()
    require_markers(
        label,
        text,
        [
            "calendar_2026_2027_tunisia.md",
            "Tunisie 2026-2027",
            "NON PUBLIABLE" if label == "progression_audit" else "non publiable",
            expected_total,
            expected_project,
        ],
        errors,
    )
    for month in MONTHS:
        if month not in lower_text:
            errors.append(f"{label}: month not planned: {month}")
    for sequence_id in sequence_ids:
        if sequence_id not in text:
            errors.append(f"{label}: sequence not planned: {sequence_id}")
    for capacity_id in sorted(ids):
        if capacity_id not in text:
            errors.append(f"{label}: official capacity not planned: {capacity_id}")
    if "covered" in lower_text and "aucune capacité n'est déclarée `covered`" not in lower_text:
        errors.append(f"{label}: suspicious coverage wording using covered")


def main() -> int:
    errors: list[str] = []

    calendar_text = read_text(CALENDAR, errors)
    premiere_text = read_text(PREMIERE, errors)
    terminale_text = read_text(TERMINALE, errors)
    programme_text = read_text(PROGRAMME, errors)
    audit_text = read_text(AUDIT, errors)

    require_markers("calendar", calendar_text, CALENDAR_MARKERS, errors)
    for month in MONTHS:
        if month not in calendar_text.lower():
            errors.append(f"calendar: missing month {month}")

    premiere_ids = official_ids(programme_text, "P")
    terminale_ids = official_ids(programme_text, "T")
    if not premiere_ids:
        errors.append("programme YAML: no Première capacity id found")
    if not terminale_ids:
        errors.append("programme YAML: no Terminale capacity id found")

    check_progression(
        "progression_premiere",
        premiere_text,
        PREMIERE_SEQUENCES,
        premiere_ids,
        "140 h",
        "43 h",
        errors,
    )
    check_progression(
        "progression_terminale",
        terminale_text,
        TERMINALE_SEQUENCES,
        terminale_ids,
        "210 h",
        "60 h",
        errors,
    )

    if "s01_structures_graphiques" in terminale_text:
        errors.append("progression_terminale: old folder name still referenced")
    if "s01_structures_donnees_interfaces_implementations" not in terminale_text:
        errors.append("progression_terminale: renamed pilot folder not referenced")
    if "s01_representation_donnees" not in premiere_text:
        errors.append("progression_premiere: pilot folder not referenced")

    require_markers(
        "progression_audit",
        audit_text,
        [
            "NON PUBLIABLE",
            "140 h",
            "210 h",
            "43 h",
            "60 h",
            "Ressources Drive intégrées localement | non",
            "ne pas générer de nouvelles séquences",
        ],
        errors,
    )

    if errors:
        print("check_progression_calendar_alignment: KO")
        for error in errors:
            print(f"- {error}")
        return 1

    print("check_progression_calendar_alignment: PASS")
    print(f"- Première capacity ids planned: {len(premiere_ids)}")
    print(f"- Terminale capacity ids planned: {len(terminale_ids)}")
    print("- Calendar months and sensitive periods are referenced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
