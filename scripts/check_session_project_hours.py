
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
        project_plan = parse_project_plan(Path(str(cfg['project'])), str(cfg['prefix']))
        by_seq: dict[str, float] = {}
        by_month: dict[str, float] = {}
        monthly = parse_table_hours(Path(str(cfg['monthly'])))
        for session in sessions:
            if session.get('Nature') == 'projet':
                hours = float(session.get('hours', 0.0))
                seq = str(session.get('sequence'))
                month = str(session.get('Mois', '')).lower()
                by_seq[seq] = by_seq.get(seq, 0.0) + hours
                by_month[month] = by_month.get(month, 0.0) + hours
        for seq, (_, project) in progression.items():
            if abs(by_seq.get(seq, 0.0) - project) > 0.01:
                errors.append(f"{level}: {seq} project sessions {by_seq.get(seq, 0.0):g} h != progression {project:g} h")
            if abs(by_seq.get(seq, 0.0) - project_plan.get(seq, -999)) > 0.01:
                errors.append(f"{level}: {seq} project sessions {by_seq.get(seq, 0.0):g} h != project plan {project_plan.get(seq)} h")
        for month, row in monthly.items():
            if abs(by_month.get(month, 0.0) - float(row['project'])) > 0.01:
                errors.append(f"{level}: {month} project subtotal mismatch")
        total = sum(by_seq.values())
        expected_project = float(str(cfg['project_total']))
        if abs(total - expected_project) > 0.01:
            errors.append(f"{level}: annual project total {total:g} h != expected {expected_project:g} h")
    return fail_or_pass('check_session_project_hours', errors)

if __name__ == '__main__':
    sys.exit(main())
