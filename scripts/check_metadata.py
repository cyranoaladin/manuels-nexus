#!/usr/bin/env python3
"""Contrôle de présence et de validité minimale des métadonnées pédagogiques."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import sys
import json

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
from scripts._inventory_utils import (
    STATUT_ALLOWED,
    parse_frontmatter,
    normalize_status,
    iter_files,
)

REQUIRED_FIELDS = {
    'title_or_titre',
    'niveau_or_level',
    'source',
    'statut',
    'version',
    'notion',
    'objectifs',
    'sequence_or_sequence_id',
}


def has_any(meta: Dict[str, object], keys: List[str]) -> bool:
    for key in keys:
        if key in meta and str(meta[key]).strip():
            return True
    return False


def validate_frontmatter(path: Path, fm: Dict[str, object], errors: List[str]) -> None:
    missing = []
    if not has_any(fm, ['title', 'titre', 'name', 'titre_document']):
        missing.append('title|titre')
    if not has_any(fm, ['niveau', 'level']):
        missing.append('niveau|level')
    if not has_any(fm, ['source', 'official_program']):
        missing.append('source')
    if not has_any(fm, ['statut', 'status']):
        missing.append('statut')
    if not has_any(fm, ['version']):
        missing.append('version')
    if not has_any(fm, ['notion', 'notions', 'rubrique', 'rubriques', 'theme']):
        missing.append('notion')
    if not has_any(fm, ['objectifs', 'learning_objectives', 'objectives', 'objectif']):
        missing.append('objectifs')
    if not has_any(fm, ['sequence', 'sequence_id']):
        missing.append('sequence')

    if missing:
        errors.append(f"{path}: champs manquants -> {', '.join(sorted(missing))}")

    status = normalize_status(str(fm.get('statut') or fm.get('status', 'needs_review')))
    if status not in STATUT_ALLOWED:
        errors.append(f"{path}: statut invalide '{fm.get('statut') or fm.get('status')}', attendus: {', '.join(sorted(STATUT_ALLOWED))}")


def validate_json_qcm(path: Path, errors: List[str]) -> None:
    try:
        payload = json.loads(path.read_text(encoding='utf-8', errors='replace'))
    except Exception as exc:
        errors.append(f"{path}: JSON invalide ({exc})")
        return

    if not isinstance(payload, dict) or 'metadata' not in payload or 'questions' not in payload:
        errors.append(f"{path}: JSON QCM incomplet (metadata/questions manquants)")
        return

    metadata = payload.get('metadata')
    if not isinstance(metadata, dict):
        errors.append(f"{path}: metadata QCM non-objet")
        return

    validate_frontmatter(path, metadata, errors)

    if not isinstance(payload.get('questions'), list) or not payload['questions']:
        errors.append(f"{path}: JSON QCM sans questions")
        return

    for i, question in enumerate(payload['questions'], 1):
        if not isinstance(question, dict):
            errors.append(f"{path}: question {i} mal formée")
            continue
        for key in ['id', 'question', 'propositions', 'bonne_reponse', 'explications']:
            if key not in question:
                errors.append(f"{path}: question {i} -> {key} manquant")


def is_pedagogical_target(path: Path) -> bool:
    if 'sequences' in path.parts or 'banques' in path.parts:
        return True
    if path.parent.name in {'premiere', 'terminale'} and path.name.endswith('.md'):
        return True
    return False


def main() -> None:
    errors: List[str] = []
    for path in iter_files(ROOT):
        if not is_pedagogical_target(path):
            # documents techniques ou rapports
            continue

        if path.suffix == '.json':
            validate_json_qcm(path, errors)
        elif path.suffix in {'.md', '.tex'}:
            fm = parse_frontmatter(path)
            if not fm:
                errors.append(f"{path}: frontmatter inexistant")
            else:
                validate_frontmatter(path, fm, errors)
        elif path.suffix in {'.yml', '.yaml'}:
            # les ressources pédagogiques yaml hors banque/séquence sont ignorées dans ce lot
            continue
        elif path.suffix == '.py':
            # ignoré, contrôlé par check_quality_gates
            continue

    if errors:
        print('check_metadata: KO')
        for item in errors[:120]:
            print(f'- {item}')
        raise SystemExit(1)

    print('check_metadata: PASS')


if __name__ == '__main__':
    main()
