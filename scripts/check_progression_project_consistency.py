#!/usr/bin/env python3
"""Check project hours consistency between annual progressions and project plans."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = {
    "premiere": (ROOT / "03_progressions/progression_premiere.md", ROOT / "project_plan_premiere.md", "P", 15),
    "terminale": (ROOT / "03_progressions/progression_terminale.md", ROOT / "project_plan_terminale.md", "T", 20),
}


def parse_progression(path: Path, prefix: str) -> dict[str, float]:
    data: dict[str, float] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("| ") or "---" in line or "Total" in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        match = re.match(rf"({prefix}\d{{2}})\b", cells[0])
        if not match:
            continue
        hour = re.search(r"([0-9]+(?:[.,][0-9]+)?)\s*h", cells[3])
        if hour:
            data[match.group(1)] = float(hour.group(1).replace(",", "."))
    return data


def parse_project_plan(path: Path, prefix: str) -> dict[str, float]:
    data: dict[str, float] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("| ") or "---" in line or "Total" in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        if re.fullmatch(rf"{prefix}\d{{2}}", cells[0]):
            hour = re.search(r"([0-9]+(?:[.,][0-9]+)?)\s*h", cells[1])
            if hour:
                data[cells[0]] = float(hour.group(1).replace(",", "."))
    return data


def main() -> int:
    errors: list[str] = []
    for level, (progression, project, prefix, count) in CONFIG.items():
        expected = {f"{prefix}{index:02d}" for index in range(count)}
        progression_hours = parse_progression(progression, prefix)
        project_hours = parse_project_plan(project, prefix)
        for seq in sorted(expected):
            if seq not in progression_hours:
                errors.append(f"{level}: progression missing project hours for {seq}")
            if seq not in project_hours:
                errors.append(f"{level}: project plan missing project hours for {seq}")
            if seq in progression_hours and seq in project_hours and abs(progression_hours[seq] - project_hours[seq]) > 0.01:
                errors.append(f"{level}: {seq} progression={progression_hours[seq]:g}h project_plan={project_hours[seq]:g}h")
        if abs(sum(progression_hours.values()) - sum(project_hours.values())) > 0.01:
            errors.append(f"{level}: project total mismatch progression={sum(progression_hours.values()):g}h plan={sum(project_hours.values()):g}h")
    if errors:
        print("check_progression_project_consistency: KO")
        for error in errors:
            print(f"- {error}")
        return 1
    print("check_progression_project_consistency: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
