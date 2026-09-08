"""A published parameter role needs a bound general argument, not three calls.

The RED probes replace exec with a controlled Python test callable. No text
loaded from a manual is executed, even while exposing the old false inference.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import qcm_independent_solver as S


def question(**context):
    return S.sanitize({
        'id': 'FIXTURE-PUBLISHED',
        'enonce': r'Dans la fonction \code{simuler(n, graine)} du chapitre, que désigne $n$ ?',
        'options': {'A': "Le nombre de valeurs possibles.", 'B': 'La graine.',
                    'C': "La taille de l’échantillon.".replace('’', "'"),
                    'D': "Le nombre d'échantillons."},
        **context,
    })


def assert_abstains(result):
    assert result is not None
    assert result.status == 'NOT_MACHINE_RESOLVABLE'
    assert result.unique_answer is None
    assert result.option_truths == {}
    assert result.reason


def test_missing_context_cannot_trigger_global_source_lookup(monkeypatch):
    calls = []
    def lookup(*args):
        calls.append(args)
        return None
    monkeypatch.setattr(S, '_published_function_source', lookup, raising=False)
    result = S._published_function_parameter_role(question())
    assert_abstains(result)
    assert calls == []


@pytest.fixture
def chapters(tmp_path, monkeypatch):
    source_root = tmp_path / 'Mathematiques/manuel-maths/chapitres'
    sources = []
    for chapter, return_value in [('1SPE-AAA', '[0] * n'), ('1SPE-BBB', '[0] * (n + 1)')]:
        path = source_root / chapter / 'python/simuler.py'
        path.parent.mkdir(parents=True)
        path.write_text(f'def simuler(n, graine):\n    return {return_value}\n')
        sources.append(path)
    monkeypatch.setattr(S, '__file__', str(tmp_path / 'scripts/qcm_independent_solver.py'))
    return sources


def test_homonymous_functions_in_other_chapters_grant_no_credit(chapters, monkeypatch):
    calls = []
    def controlled_exec(_compiled, namespace):
        calls.append('would execute selected published code')
        namespace['simuler'] = lambda n, graine: [0] * n
    monkeypatch.setattr(S, 'exec', controlled_exec, raising=False)
    inp = question(chapter='1SPE-BBB', source_path='Mathematiques/manuel-maths/chapitres/1SPE-BBB/qcm/current-QCM.json')
    result = S._published_function_parameter_role(inp)
    assert_abstains(result)
    assert calls == []


def test_changing_source_cannot_reuse_a_parameter_role_key(chapters, monkeypatch):
    calls = []
    def controlled_exec(_compiled, namespace):
        calls.append('would execute selected published code')
        # A finite observation matching n below 12 cannot imply a general role.
        namespace['simuler'] = lambda n, graine: [0] * (n if n < 12 else n + 1)
    monkeypatch.setattr(S, 'exec', controlled_exec, raising=False)
    inp = question()
    before = S._published_function_parameter_role(inp)
    chapters[0].write_text('def simuler(n, graine):\n    return [0] * (n if n < 12 else n + 1)\n')
    after = S._published_function_parameter_role(inp)
    assert_abstains(before)
    assert_abstains(after)
    assert calls == []


def test_current_referential_question_is_not_certified_by_samples(monkeypatch):
    path = ROOT / 'Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/qcm/1SPE-VARALEA-QCM.json'
    raw = next(q for q in json.loads(path.read_text())['questions'] if q['id'] == 'Q16')
    calls = []
    def controlled_exec(_compiled, namespace):
        calls.append('would execute published code')
        namespace['simuler_variable'] = lambda n, graine: [0] * (n if n < 12 else n + 1)
    monkeypatch.setattr(S, 'exec', controlled_exec, raising=False)
    result = S._published_function_parameter_role(S.sanitize_canonical(raw))
    assert_abstains(result)
    assert calls == []
