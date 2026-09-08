"""History regressions exercise bindings and rendering, not historical truth.

Dates and attributions require the independent documentary review linked in
2026-09-08-tnsi-history-chronology-review.md. These tests grant no such credit.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
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


@pytest.mark.parametrize('name', ['TNSI-HIST-EVAL-B.tex', 'TNSI-HIST-EVAL-B-corrige.tex'])
def test_bareme_arithmetic_fails_when_a_component_changes(tmp_path, name):
    from NSI.scripts import verify_python as execution

    source = CHAPTER / 'evaluations' / name
    before = execution.check_object(source)
    assert before['verdict'] == 'verified'
    assert before['certifies_documentary_claims'] is False
    program = execution.strip_percent(execution.VERIFY.findall(source.read_text())[0])
    # Change one awarded component, not the expected total; the real assertion
    # must fail. No date or prose claim is evaluated by this mutation.
    variable = 'points_q1' if 'corrige' in name else 'points_exercice_1'
    lines = program.splitlines()
    assignment = next(i for i, line in enumerate(lines) if line.startswith(variable + ' ='))
    lines.insert(assignment + 1, f'{variable} = ({variable}[0] + 1,) + {variable}[1:]')
    mutated = '% BEGIN-VERIFY\n' + '\n'.join('% ' + line for line in lines) + '\n% END-VERIFY\n'
    target = tmp_path / 'changed_arithmetic.tex'
    target.write_text(mutated)
    after = execution.check_object(target)
    assert after['verdict'] == 'fail'
    assert after['certifies_documentary_claims'] is False


@pytest.mark.parametrize('number', ['01', '02'])
def test_documentary_remediation_has_no_artificial_execution_credit(number):
    from NSI.scripts import verify_python as execution
    import scientific_receipt_binding as binding

    source = CHAPTER / f'remediation/TNSI-HISTOIRE-INFORMATIQUE-RE-C{number}.tex'
    result = execution.check_object(source)
    assert result['verdict'] == 'manual_review'
    assert result['certifies_documentary_claims'] is False
    historical_path = f'NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/validations/TNSI-HISTOIRE-INFORMATIQUE-RE-C{number}.execution.json'
    historical = json.loads(subprocess.check_output(
        ['git', 'show', '6da7f7637e34a3f7f4aba91eb765ee92ce7fc1d9:' + historical_path],
        cwd=ROOT, text=True,
    ))
    bound = binding.bind(historical, CHAPTER, ROOT)
    assert not binding.usable(bound)
    assert bound['state'] == 'STALE'
    assert bound['reason'] == 'SOURCE_DIGEST_CHANGED'


def test_history_cross_capacity_diagnostics_are_explicitly_justified(tmp_path):
    import build_qcm_diagnostic_renvoi_audit as audit

    chapter = tmp_path / 'NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE'
    (chapter / 'qcm').mkdir(parents=True)
    (chapter / 'cours').mkdir()
    (chapter / 'contrat.yaml').write_bytes((CHAPTER / 'contrat.yaml').read_bytes())
    for source in (CHAPTER / 'cours').glob('*.tex'):
        (chapter / 'cours' / source.name).write_bytes(source.read_bytes())
    source = CHAPTER / 'qcm/TNSI-HISTOIRE-INFORMATIQUE-QCM.json'
    (chapter / 'qcm' / source.name).write_bytes(source.read_bytes())
    result = audit.build(tmp_path)
    rows = result['cross_capacity']
    assert {(r['question_id'], r['option']) for r in rows} == {('Q4', 'B'), ('Q4', 'C')}
    assert all(r['state'] == 'RESOLVED' and r['justification'] for r in rows)
