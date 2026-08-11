#!/usr/bin/env python3
"""Reconstruit le manifest et les rapports d’inventaire.

Sorties:
- manifest.csv
- inventory_report.md
- duplicates_report.md
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Dict, List
import csv
import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / 'manifest.csv'
MANIFEST_TOOLING_PATH = ROOT / 'manifest_tooling.csv'

TOOLING_PREFIXES = ('scripts/', 'tests/', 'reports/', 'scrapping_NSI/', 'docs/', '.github/')

# Root-level directories that contain actual pedagogical content.
# Files outside these directories (at root) are classified as tooling/config.
PEDAGOGICAL_DIRS = (
    '00_programmes_officiels/',
    '02_modeles_documents/',
    '03_progressions/',
    'premiere/',
    'terminale/',
)
REPORT_PATH = ROOT / 'inventory_report.md'
DUPLICATES_PATH = ROOT / 'duplicates_report.md'
TRACE_PATH = ROOT / 'support_source_trace.yml'

from scripts._inventory_utils import (
    IGNORED_SUFFIXES,
    STATUT_ALLOWED,
    SOURCE_TYPE_GENERATED,
    parse_frontmatter,
    extract_theme_and_notion,
    detect_level,
    detect_sequence_id,
    detect_source_type,
    classify_resource_type,
    normalize_status,
    resource_audience,
    is_pedagogical,
    is_publishable,
    sha256_file,
    iter_files,
    evidence_category,
)


DRIVE_TRACE_SOURCE_TYPES = {
    'adaptation_drive': 'adapted_from_drive',
    'adapted_from_drive': 'adapted_from_drive',
    'adaptation': 'adapted_from_drive',
    'import_partiel': 'import_partiel',
    'inspiration_drive': 'inspiration_drive',
    'inspiration_only': 'inspiration_drive',
}

_SOURCE_TRACE_CACHE: Dict[str, str] | None = None


def support_source_types() -> Dict[str, str]:
    global _SOURCE_TRACE_CACHE
    if _SOURCE_TRACE_CACHE is not None:
        return _SOURCE_TRACE_CACHE
    result: Dict[str, str] = {}
    if TRACE_PATH.exists():
        payload = yaml.safe_load(TRACE_PATH.read_text(encoding='utf-8')) or {}
        rows = payload.get('supports', []) if isinstance(payload, dict) else []
        for row in rows:
            if not isinstance(row, dict):
                continue
            support = str(row.get('support') or '').strip()
            reuse = str(row.get('type_reprise') or '').strip()
            source = DRIVE_TRACE_SOURCE_TYPES.get(reuse)
            if support and source:
                result[support] = source
    _SOURCE_TRACE_CACHE = result
    return result


def row_from_path(path: Path, idx: int) -> Dict[str, str]:
    relative = path.relative_to(ROOT).as_posix()
    fm = parse_frontmatter(path)
    status = normalize_status(str(fm.get('statut') or fm.get('status') or 'needs_review'))
    if status not in STATUT_ALLOWED:
        status = 'needs_review'

    theme, notion = extract_theme_and_notion(path, fm)
    sequence = detect_sequence_id(path, fm)
    resource_type = classify_resource_type(path)
    audience = resource_audience(path, fm)
    publishable = 'oui' if status == 'published' and is_publishable(path) else 'non'

    source = support_source_types().get(relative) or detect_source_type(path, fm)
    if source == SOURCE_TYPE_GENERATED:
        source = 'generated'

    source_path = fm.get('source')
    if isinstance(source_path, list):
        source_path = ', '.join(str(x) for x in source_path)

    reus = 'oui' if path.suffix in {'.md', '.tex', '.json', '.py'} else 'non'
    needs_refactoring = 'oui' if status in {'needs_content', 'needs_review', 'draft'} else 'non'

    quality = 'basse' if needs_refactoring == 'oui' else 'bonne'
    if status in {'validated_pedagogy', 'validated_science', 'validated_technical', 'published'}:
        quality = 'haute'

    return {
        'id': f'{detect_level(path)[:1].upper()}{idx:02d}-{path.stem}'.replace('_', '-'),
        'nom': path.name,
        'chemin': relative,
        'type': resource_type,
        'niveau': detect_level(path),
        'theme': theme,
        'notion': notion,
        'sequence_possible': sequence,
        'statut': status,
        'qualite': quality,
        'reutilisable': reus,
        'a_refondre': needs_refactoring,
        'commentaire': (str(source_path) if source_path else '').strip(),
        'source': source,
        'audience': audience,
        'publishable': publishable,
        'copie_dans_banques': 'oui'
        if '/banques/' in relative and path.name not in {'index.md', '.gitkeep'} and not path.is_symlink()
        else 'non',
        'symlink': 'oui' if path.is_symlink() else 'non',
        'evidence_category': evidence_category(path, fm) or 'autre',
        'hash': sha256_file(path),
    }


def build_manifest() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    counters: Dict[str, int] = defaultdict(int)

    for path in sorted(iter_files(ROOT), key=lambda p: p.as_posix()):
        if path.suffix in IGNORED_SUFFIXES:
            continue
        if path.suffix == '.csv' and path.name == 'manifest.csv':
            continue
        if path.name == 'AGENTS.md' and path.parent == ROOT:
            continue
        if path.name == 'SKILLS.md' and path.parent == ROOT:
            continue
        counters[path.as_posix()] += 1
        idx = counters[path.as_posix()]
        rows.append(row_from_path(path, idx))

    rows.sort(key=lambda row: (row['niveau'], row['type'], row['chemin']))
    return rows


def write_manifest(rows: List[Dict[str, str]]) -> None:
    fieldnames = [
        'id',
        'nom',
        'chemin',
        'type',
        'niveau',
        'theme',
        'notion',
        'sequence_possible',
        'statut',
        'qualite',
        'reutilisable',
        'a_refondre',
        'commentaire',
        'source',
        'audience',
        'publishable',
        'copie_dans_banques',
        'evidence_category',
        'hash',
        'symlink',
    ]
    def is_tooling(chemin: str) -> bool:
        if chemin.startswith(TOOLING_PREFIXES):
            return True
        # Root-level files not under pedagogical dirs are config/tooling.
        if '/' not in chemin or not chemin.startswith(PEDAGOGICAL_DIRS):
            return not chemin.startswith(PEDAGOGICAL_DIRS)
        return False

    pedagogical = [r for r in rows if not is_tooling(r['chemin'])]
    tooling = [r for r in rows if is_tooling(r['chemin'])]
    for path, subset in [(MANIFEST_PATH, pedagogical), (MANIFEST_TOOLING_PATH, tooling)]:
        with path.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\n')
            writer.writeheader()
            for row in subset:
                writer.writerow({k: row.get(k, '') for k in fieldnames})


def write_reports(rows: List[Dict[str, str]]) -> None:
    total = len(rows)
    by_source: dict[str, int] = defaultdict(int)
    by_audience: dict[str, int] = defaultdict(int)
    by_level: dict[str, int] = defaultdict(int)
    by_type: dict[str, int] = defaultdict(int)
    by_status: dict[str, int] = defaultdict(int)
    by_sequence: dict[str, int] = defaultdict(int)
    missing_metadata = []
    high_quality = []
    incomplete = []
    pedagogical = []
    technical = []
    publishable = []
    bank_copy = []

    hash_map: Dict[str, List[str]] = defaultdict(list)

    for row in rows:
        path = ROOT / row['chemin']
        by_source[row['source']] += 1
        by_audience[row['audience']] += 1
        by_level[row['niveau']] += 1
        by_type[row['type']] += 1
        by_status[row['statut']] += 1
        by_sequence[row['sequence_possible']] += 1

        if is_pedagogical(path):
            pedagogical.append(row['chemin'])
        else:
            technical.append(row['chemin'])

        if row['publishable'] == 'oui':
            publishable.append(row['chemin'])

        if row['copie_dans_banques'] == 'oui':
            bank_copy.append(row['chemin'])

        if row['statut'] in {'validated_pedagogy', 'validated_science', 'validated_technical', 'published'}:
            high_quality.append(row['chemin'])
        else:
            incomplete.append(row['chemin'])

        if row['niveau'] != 'interne' and row['type'] == 'document' and not (row['theme'] and row['notion']):
            missing_metadata.append(f"{row['chemin']} (niveau={row['niveau']}, statut={row['statut']})")

        hash_map[row['hash']].append(row['chemin'])

    duplicate_lines = [paths for paths in hash_map.values() if len(paths) > 1]

    text: List[str] = []
    text.append('# Inventaire ressources NSI')
    text.append('')
    text.append(f'- Total ressources : {total}')
    text.append(f'- Ressources pédagogiques : {len(pedagogical)}')
    text.append(f'- Ressources techniques : {len(technical)}')
    text.append(f'- Ressources copiées dans banques : {len(bank_copy)}')

    text.extend([
        '',
        '## Répartition par source',
        *[f"- {source}: {count}" for source, count in sorted(by_source.items())],
        '',
        '## Répartition par niveau',
    ])
    for level, count in sorted(by_level.items()):
        text.append(f'- {level}: {count}')

    text.extend(['', '## Répartition par type'])
    for kind, count in sorted(by_type.items()):
        text.append(f'- {kind}: {count}')

    text.extend(['', '## Répartition par statut'])
    for status, count in sorted(by_status.items()):
        text.append(f'- {status}: {count}')

    text.extend([
        '',
        '## Répartition audience',
    ])
    for audience, count in sorted(by_audience.items()):
        text.append(f'- {audience}: {count}')

    text.extend([
        '',
        '## Catégories (distinguer exigences)',
        '- Sources issues du Drive ou adaptées depuis Drive :',
    ])
    for entry in sorted(r['chemin'] for r in rows if r['source'] in {'drive', 'adapted_from_drive', 'import_partiel', 'inspiration_drive'}):
        text.append(f'  - {entry}')
    text.append('- Sources générées :')
    for entry in sorted(r['chemin'] for r in rows if r['source'] == 'generated'):
        text.append(f'  - {entry}')
    text.append('- Ressources pédagogiques :')
    for entry in sorted(pedagogical):
        text.append(f'  - {entry}')
    text.append('- Ressources techniques :')
    for entry in sorted(technical):
        text.append(f'  - {entry}')
    text.append('- Ressources copiées dans banques :')
    for entry in sorted(bank_copy):
        text.append(f'  - {entry}')

    text.extend([
        '',
        '## Séquences détectées',
    ])
    for seq, count in sorted(by_sequence.items()):
        if seq == 'NA':
            continue
        text.append(f'- {seq}: {count}')

    text.extend([
        '',
        '## Ressources publiables',
    ])
    for entry in sorted(publishable):
        text.append(f'- {entry}')

    text.extend([
        '',
        '## Ressources professeur',
    ])
    for row in sorted((r for r in rows if r['audience'] == 'professeur'), key=lambda e: e['chemin']):
        text.append(f'- {row["chemin"]}')

    text.extend([
        '',
        '## Ressources élève',
    ])
    for row in sorted((r for r in rows if r['audience'] in {'eleve', 'mixte'}), key=lambda e: e['chemin']):
        text.append(f'- {row["chemin"]}')

    text.extend([
        '',
        '## Ressources haute qualité',
    ])
    if high_quality:
        for entry in sorted(high_quality):
            text.append(f'- {entry}')
    else:
        text.append('- Aucune ressource avec statut final pour l’instant.')

    text.extend([
        '',
        '## Ressources à corriger / compléter',
    ])
    for entry in sorted(incomplete):
        text.append(f'- {entry}')

    if missing_metadata:
        text.extend(['', '## Métadonnées incomplètes'])
        for entry in sorted(missing_metadata):
            text.append(f'- {entry}')

    text.extend([
        '',
        '## Doublons (même hash SHA256)',
    ])
    if not duplicate_lines:
        text.append('- Aucun doublon détecté.')
    else:
        for group in sorted(duplicate_lines):
            text.append(f'- Groupe ({len(group)}):')
            for entry in sorted(group):
                text.append(f'  - {entry}')

    REPORT_PATH.write_text('\n'.join(text) + '\n', encoding='utf-8')

    duplicate_text = ['# Doublons détectés par SHA256', '']
    if not duplicate_lines:
        duplicate_text.append('- Aucun doublon.')
    else:
        for i, group in enumerate(sorted(duplicate_lines), start=1):
            duplicate_text.append(f'## Groupe {i}')
            has_bank = any('/banques/' in entry for entry in group)
            has_sequence = any('/sequences/' in entry for entry in group)
            has_symlink = any((ROOT / entry).is_symlink() for entry in group)
            if has_symlink:
                duplicate_text.append('- Classification : symlink intentionnel à vérifier dans `bank_strategy.md`.')
            elif has_bank and has_sequence:
                duplicate_text.append('- Classification : copie interdite entre banque et séquence.')
            elif has_bank:
                duplicate_text.append('- Classification : doublon de banque à traiter.')
            else:
                duplicate_text.append('- Classification : doublon non classé, revue nécessaire.')
            for entry in sorted(group):
                duplicate_text.append(f'- {entry}')
    DUPLICATES_PATH.write_text('\n'.join(duplicate_text) + '\n', encoding='utf-8')


def main() -> None:
    rows = build_manifest()
    write_manifest(rows)
    write_reports(rows)
    print('rebuild_inventory: manifest=', MANIFEST_PATH)
    print('rebuild_inventory: inventory=', REPORT_PATH)
    print('rebuild_inventory: duplicates=', DUPLICATES_PATH)


if __name__ == '__main__':
    main()
