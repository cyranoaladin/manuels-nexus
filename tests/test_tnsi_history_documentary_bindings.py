"""History regressions exercise bindings and rendering, not historical truth.

Dates and attributions require the independent documentary review linked in
2026-09-08-tnsi-history-chronology-review.md. These tests grant no such credit.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / 'NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE'
sys.path.insert(0, str(ROOT / 'scripts'))
import build_qcm_review_proof_reconciliation as reconciliation


@pytest.fixture
def renderer():
    spec = importlib.util.spec_from_file_location(
        'tnsi_history_qcm_renderer',
        ROOT / 'Mathematiques/manuel-maths/scripts/build_qcm_tex.py',
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def document():
    return json.loads((CHAPTER / 'qcm/TNSI-HISTOIRE-INFORMATIQUE-QCM.json').read_text())


@pytest.mark.parametrize('question_id, option', [('Q1', 'D'), ('Q2', 'A'), ('Q2', 'C')])
def test_historical_diagnostic_changes_identity_without_changing_the_answer(question_id, option):
    question = next(q for q in document()['questions'] if q['id'] == question_id)
    changed = copy.deepcopy(question)
    changed['diagnostics'][option]['erreur'] = 'Affirmation documentaire différente, non relue.'
    assert changed['correcte'] == question['correcte']
    assert changed['options'] == question['options']
    assert reconciliation.current_question_digest(changed) != reconciliation.current_question_digest(question)


def test_current_history_qcm_is_exactly_its_canonical_render(renderer):
    data = document()
    target = CHAPTER / 'qcm/TNSI-HISTOIRE-INFORMATIQUE-QCM.tex'
    meta = renderer.meta_existante(target)
    data['questions'], official = renderer.resoudre_capacites_questions(data['chapitre'], data['questions'])
    data.update(_source='chapitres/TNSI-HISTOIRE-INFORMATIQUE/qcm/TNSI-HISTOIRE-INFORMATIQUE-QCM.json',
                _identifiant=meta['id'], _statut=meta['status'],
                _capacites=official if 'capacites' in meta else None)
    assert renderer.rendre(data) == target.read_text()


def test_changed_historical_diagnostic_is_detected_by_canonical_check(renderer, tmp_path, monkeypatch):
    chapter = tmp_path / 'chapitres/TNSI-HISTOIRE-INFORMATIQUE'
    qcm = chapter / 'qcm'
    qcm.mkdir(parents=True)
    (chapter / 'contrat.yaml').write_bytes((CHAPTER / 'contrat.yaml').read_bytes())
    for source in (CHAPTER / 'qcm').iterdir():
        (qcm / source.name).write_bytes(source.read_bytes())
    monkeypatch.setattr(renderer, 'RACINES_CHAPITRES', (tmp_path / 'chapitres',))
    monkeypatch.setattr(sys, 'argv', ['build_qcm_tex.py', '--chap', chapter.name, '--check'])
    assert renderer.main() == 0
    source = qcm / 'TNSI-HISTOIRE-INFORMATIQUE-QCM.json'
    data = json.loads(source.read_text())
    data['questions'][0]['diagnostics']['D']['erreur'] = 'Cette autre affirmation demande une nouvelle revue.'
    source.write_text(json.dumps(data, ensure_ascii=False))
    assert renderer.main() == 1
