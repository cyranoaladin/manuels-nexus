
from __future__ import annotations
from typing import Any

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NATURES = {"cours", "TD", "TP", "projet", "évaluation", "remédiation"}
LEVELS = {
    "premiere": {"session": ROOT / "03_progressions/seances_premiere.md", "monthly": ROOT / "03_progressions/monthly_load_premiere.md", "progression": ROOT / "03_progressions/progression_premiere.md", "project": ROOT / "project_plan_premiere.md", "prefix": "P", "count": 15, "total": 140.0, "project_total": 43.0},
    "terminale": {"session": ROOT / "03_progressions/seances_terminale.md", "monthly": ROOT / "03_progressions/monthly_load_terminale.md", "progression": ROOT / "03_progressions/progression_terminale.md", "project": ROOT / "project_plan_terminale.md", "prefix": "T", "count": 20, "total": 210.0, "project_total": 60.0},
}

def parse_hours(value: str) -> float:
    m = re.search(r"(-?[0-9]+(?:[,.][0-9]+)?)\s*h", value)
    if not m:
        raise ValueError(f"missing hour value: {value}")
    return float(m.group(1).replace(',', '.'))

def parse_sessions(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding='utf-8', errors='replace')
    blocks = re.split(r"(?=^### Séance )", text, flags=re.M)
    sessions = []
    for block in blocks:
        if not block.startswith('### Séance '):
            continue
        header = block.splitlines()[0].strip()
        sid = header.replace('### Séance ', '').strip()
        item = {'id': sid, 'raw': block}
        for line in block.splitlines()[1:]:
            if line.startswith('- ') and ' : ' in line:
                key, value = line[2:].split(' : ', 1)
                item[key.strip()] = value.strip()
        if 'Durée' in item:
            item['hours'] = parse_hours(str(item['Durée']))
        m = re.match(r'([PT]\d{2})-S\d+', sid)
        item['sequence'] = m.group(1) if m else ''
        sessions.append(item)
    return sessions

def parse_table_hours(path: Path) -> dict[str, dict[str, Any]]:
    rows = {}
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        if not line.startswith('| ') or '---' in line or 'Mois' in line:
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 8:
            continue
        month = cells[0].lower()
        rows[month] = {
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
    data = {}
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        if not line.startswith('| ') or '---' in line or 'Total' in line:
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 4:
            continue
        m = re.match(rf'({prefix}\d{{2}})\b', cells[0])
        if not m:
            continue
        try:
            volume = parse_hours(cells[2])
            project = parse_hours(cells[3])
        except ValueError:
            continue
        data[m.group(1)] = (volume, project)
    return data

def parse_project_plan(path: Path, prefix: str) -> dict[str, float]:
    data = {}
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        if not line.startswith('| ') or '---' in line or 'Total' in line:
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 2:
            continue
        if re.fullmatch(rf'{prefix}\d{{2}}', cells[0]):
            data[cells[0]] = parse_hours(cells[1])
    return data

def fail_or_pass(name: str, errors: list[str]) -> int:
    if errors:
        print(f'{name}: KO')
        for error in errors:
            print(f'- {error}')
        return 1
    print(f'{name}: PASS')
    return 0

import sys

def main() -> int:
    errors = []
    for level, cfg in LEVELS.items():
        sessions = parse_sessions(Path(str(cfg['session'])))
        progression = parse_progression_projects(Path(str(cfg['progression'])), str(cfg['prefix']))
        totals: dict[str, float] = {}
        for session in sessions:
            sid = session['id']
            if session.get('hours', 0) > 2.5:
                errors.append(f"{level}: {sid} exceeds 2 h 30 ({session.get('hours')} h)")
            if session.get('Nature') not in NATURES:
                errors.append(f"{level}: {sid} invalid or missing Nature")
            for field in ['Durée','Semaine scolaire','Semaine civile','Période','Mois','Nature','Objectif','Capacité officielle','Document utilisé','Déroulé','Différenciation','Livrable','Trace écrite','Devoir ou préparation','Remédiation']:
                if field not in session:
                    errors.append(f"{level}: {sid} missing field {field}")
            if 'Date ou semaine' in session:
                errors.append(f"{level}: {sid} still uses obsolete Date ou semaine field")
            if 'Date ou semaine' in session:
                errors.append(f"{level}: {sid} still uses obsolete Date ou semaine field")
            if 'Date ou semaine' in session:
                errors.append(f"{level}: {sid} still uses obsolete Date ou semaine field")
            if 'Date ou semaine' in session:
                errors.append(f"{level}: {sid} still uses obsolete Date ou semaine field")
            if 'Date ou semaine' in session:
                errors.append(f"{level}: {sid} still uses obsolete Date ou semaine field")
            seq = str(session.get('sequence', ''))
            totals[seq] = totals.get(seq, 0.0) + float(session.get('hours', 0.0))
            if session.get('Nature') == 'projet':
                for field in ['Jalon projet','Rôle dans le carnet de bord','Livrable projet','Évaluation projet']:
                    if field not in session:
                        errors.append(f"{level}: {sid} project session missing {field}")
        for seq, (volume, _) in progression.items():
            if abs(totals.get(seq, 0.0) - volume) > 0.01:
                errors.append(f"{level}: {seq} session total {totals.get(seq, 0.0):g} h != progression {volume:g} h")
        total = sum(float(s.get('hours', 0.0)) for s in sessions)
        if abs(total - float(str(cfg['total']))) > 0.01:
            errors.append(f"{level}: annual session total {total:g} h != expected {cfg['total']:g} h")
    return fail_or_pass('check_session_duration_consistency', errors)

if __name__ == '__main__':
    sys.exit(main())
