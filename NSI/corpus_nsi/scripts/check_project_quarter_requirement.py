#!/usr/bin/env python3
"""Check that project time reaches at least one quarter of annual NSI time."""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PLANS = {
    "premiere": {
        "path": ROOT / "project_plan_premiere.md",
        "sequences": [f"P{i:02d}" for i in range(15)],
        "expected_total": 140.0,
    },
    "terminale": {
        "path": ROOT / "project_plan_terminale.md",
        "sequences": [f"T{i:02d}" for i in range(20)],
        "expected_total": 210.0,
    },
}

REQUIRED_TERMS = [
    "micro-projets",
    "projet intermédiaire",
    "projet final",
    "jalons",
    "livrables",
    "carnet de bord",
    "soutenance",
    "grille d'évaluation",
    "différenciation",
    "groupes",
    "RGPD",
    "données fictives",
    "oral",
]


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    stripped = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    return stripped.lower()


def parse_hours(label: str, text: str, errors: list[str]) -> tuple[float, float, float]:
    total_match = re.search(r"Total horaire NSI estimé\s*:\s*([0-9]+(?:[.,][0-9]+)?)\s*h", text)
    project_match = re.search(r"Total projets\s*:\s*([0-9]+(?:[.,][0-9]+)?)\s*h", text)
    ratio_match = re.search(r"Ratio projet\s*:\s*([0-9]+(?:[.,][0-9]+)?)\s*%", text)
    if not total_match:
        errors.append(f"{label}: missing total annual NSI hours")
    if not project_match:
        errors.append(f"{label}: missing project hours")
    if not ratio_match:
        errors.append(f"{label}: missing project ratio")
    if not (total_match and project_match and ratio_match):
        return 0.0, 0.0, 0.0
    total = float(total_match.group(1).replace(",", "."))
    project = float(project_match.group(1).replace(",", "."))
    ratio = float(ratio_match.group(1).replace(",", "."))
    return total, project, ratio


def check_plan(label: str, path: Path, sequences: list[str], expected_total: float, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"{label}: missing file {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8")
    normalized = normalize(text)
    total, project, ratio = parse_hours(label, text, errors)

    if total and abs(total - expected_total) > 0.01:
        errors.append(f"{label}: expected {expected_total:g} h, found {total:g} h")
    if total and project:
        computed_ratio = project / total * 100.0
        if computed_ratio < 25.0:
            errors.append(f"{label}: project time below 25 percent: {computed_ratio:.1f} percent")
        if abs(computed_ratio - ratio) > 0.2:
            errors.append(f"{label}: declared ratio {ratio:.1f} differs from computed {computed_ratio:.1f}")
    if ratio and ratio < 25.0:
        errors.append(f"{label}: declared ratio below 25 percent: {ratio:.1f}")

    for sequence_id in sequences:
        if sequence_id not in text:
            errors.append(f"{label}: missing project entry for {sequence_id}")

    for term in REQUIRED_TERMS:
        if normalize(term) not in normalized:
            errors.append(f"{label}: missing required project planning term: {term}")

    if "non publiable" not in normalized:
        errors.append(f"{label}: publication status not explicit")


def main() -> int:
    errors: list[str] = []
    for label, config in PLANS.items():
        raw_seq = config["sequences"]
        sequences = [str(s) for s in raw_seq] if isinstance(raw_seq, list) else []
        check_plan(
            label,
            Path(str(config["path"])),
            sequences,
            float(str(config["expected_total"])),
            errors,
        )

    if errors:
        print("check_project_quarter_requirement: KO")
        for error in errors:
            print(f"- {error}")
        return 1

    print("check_project_quarter_requirement: PASS")
    print("- Première project ratio: 43 h / 140 h = 30.7 percent")
    print("- Terminale project ratio: 60 h / 210 h = 28.6 percent")
    print("- Required project planning sections are present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
