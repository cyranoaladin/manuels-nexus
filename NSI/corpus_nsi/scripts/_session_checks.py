#!/usr/bin/env python3
"""Shared parsing helpers for annual session planning checks."""
from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
NATURES = {"cours", "TD", "TP", "projet", "évaluation", "remédiation"}
LEVELS = {
    "premiere": {"session": ROOT / "03_progressions/seances_premiere.md", "monthly": ROOT / "03_progressions/monthly_load_premiere.md", "progression": ROOT / "03_progressions/progression_premiere.md", "project": ROOT / "project_plan_premiere.md", "prefix": "P", "count": 15, "total": 140.0, "project_total": 43.0},
    "terminale": {"session": ROOT / "03_progressions/seances_terminale.md", "monthly": ROOT / "03_progressions/monthly_load_terminale.md", "progression": ROOT / "03_progressions/progression_terminale.md", "project": ROOT / "project_plan_terminale.md", "prefix": "T", "count": 20, "total": 210.0, "project_total": 60.0},
}
MONTH_WEEK_RANGES = {
    "septembre": range(1, 5),
    "octobre": range(5, 8),
    "novembre": range(8, 13),
    "décembre": range(13, 16),
    "janvier": range(16, 20),
    "février": range(20, 23),
    "mars": range(23, 28),
    "avril": range(28, 32),
    "mai": range(32, 35),
    "juin": range(35, 39),
}
MONTH_STATUSES = {
    "septembre": "normal",
    "octobre": "férié",
    "novembre": "normal",
    "décembre": "férié",
    "janvier": "férié",
    "février": "Ramadan",
    "mars": "Ramadan / Aïd al-Fitr / férié",
    "avril": "férié",
    "mai": "férié / Aïd al-Adha",
    "juin": "fin d’année",
}
GENERIC_PHRASES = [
    "travailler ",
    "avec une tâche limitée et observable",
    "progression annuelle, support de",
    "ressources candidates non publiées",
    "situation courte, activité guidée, formalisation, entraînement, bilan de sortie",
    "aide pas à pas pour le socle ; extension bornée pour élèves avancés",
    "trace ou production associée",
    "reprise courte ou préparation de la séance suivante",
]
CONCRETE_TOKENS = ["exercice", "exercices", "question", "questions", "TP", "activité", "fichier", ".py", ".csv", ".md", "QCM", "quiz", "sujet", "problème", "conversion", "requête", "graphe", "table", "trace", "diagnostic", "évaluation", "evaluation", "code", "données", "carnet", "livrable projet"]


def parse_hours(value: str) -> float:
    match = re.search(r"(-?[0-9]+(?:[,.][0-9]+)?)\s*h", value)
    if not match:
        raise ValueError(f"missing hour value: {value}")
    return float(match.group(1).replace(',', '.'))


def parse_sessions(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding='utf-8', errors='replace')
    blocks = re.split(r"(?=^### Séance )", text, flags=re.M)
    sessions: list[dict[str, Any]] = []
    for block in blocks:
        if not block.startswith('### Séance '):
            continue
        header = block.splitlines()[0].strip()
        session_id = header.replace('### Séance ', '').strip()
        item: dict[str, Any] = {'id': session_id, 'raw': block}
        for line in block.splitlines()[1:]:
            if line.startswith('- ') and ' : ' in line:
                key, value = line[2:].split(' : ', 1)
                item[key.strip()] = value.strip()
        if 'Durée' in item:
            item['hours'] = parse_hours(str(item['Durée']))
        match = re.match(r'([PT]\d{2})-S\d+', session_id)
        item['sequence'] = match.group(1) if match else ''
        sessions.append(item)
    return sessions


def parse_table_hours(path: Path) -> dict[str, dict[str, float | str]]:
    rows: dict[str, dict[str, float | str]] = {}
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        if not line.startswith('| ') or '---' in line or 'Mois' in line:
            continue
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if len(cells) < 8:
            continue
        rows[cells[0].lower()] = {
            'available': parse_hours(cells[1]),
            'planned': parse_hours(cells[2]),
            'margin': parse_hours(cells[3]),
            'project': parse_hours(cells[4]),
            'evaluation': parse_hours(cells[5]),
            'remediation': parse_hours(cells[6]),
            'status': cells[7],
        }
    return rows


def parse_progression_projects(path: Path, prefix: str) -> dict[str, tuple[float, float]]:
    data: dict[str, tuple[float, float]] = {}
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        if not line.startswith('| ') or '---' in line or 'Total' in line:
            continue
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if len(cells) < 4:
            continue
        match = re.match(rf'({prefix}\d{{2}})\b', cells[0])
        if not match:
            continue
        data[match.group(1)] = (parse_hours(cells[2]), parse_hours(cells[3]))
    return data


def parse_project_plan(path: Path, prefix: str) -> dict[str, float]:
    data: dict[str, float] = {}
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        if not line.startswith('| ') or '---' in line or 'Total' in line:
            continue
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if len(cells) >= 2 and re.fullmatch(rf'{prefix}\d{{2}}', cells[0]):
            data[cells[0]] = parse_hours(cells[1])
    return data


def session_week(session: dict[str, Any]) -> int | None:
    raw = str(session.get('Semaine scolaire', ''))
    match = re.search(r"\b([0-9]+)\b", raw)
    if not match:
        return None
    return int(match.group(1))


def fail_or_pass(name: str, errors: list[str]) -> int:
    if errors:
        print(f'{name}: KO')
        for error in errors:
            print(f'- {error}')
        return 1
    print(f'{name}: PASS')
    return 0


def by_sequence(sessions: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for session in sessions:
        grouped[str(session.get('sequence', ''))].append(session)
    return grouped


def count_values(sessions: list[dict[str, Any]], field: str) -> Counter[str]:
    return Counter(str(session.get(field, '')).strip() for session in sessions)
