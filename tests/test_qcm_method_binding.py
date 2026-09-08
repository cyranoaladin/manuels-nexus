"""Current answer-key evidence binds the executed method as well as its input."""
import json
from pathlib import Path

import pytest

from tests.test_qcm_current_evidence_guard import C, ROOT, evidence_fixture


@pytest.mark.parametrize('method', [
    'scripts/qcm_independent_solver.py', 'scripts/latex_arith.py',
    'scripts/build_qcm_independent_evidence_v2.py',
    'scripts/build_qcm_review_proof_reconciliation.py',
])
def test_method_mutation_invalidates_an_unchanged_question(evidence_fixture, method):
    root, _source, _evidence = evidence_fixture
    assert C._corpus_totals(root)['total'] == 1
    path = root / method
    path.parent.mkdir(exist_ok=True)
    path.write_text((path.read_text() if path.is_file() else '') + '\n# controlled method mutation\n')
    with pytest.raises(ValueError, match='(?i)(method|dependency|proof)'):
        C._corpus_totals(root)


@pytest.mark.parametrize('mutation', ['output', 'verdict', 'binding'])
def test_a_full_question_digest_cannot_replace_the_proof(evidence_fixture, mutation):
    root, _source, evidence = evidence_fixture
    assert C._corpus_totals(root)['total'] == 1
    payload = json.loads(evidence.read_text())
    row = payload['questions'][0]
    if mutation == 'output':
        row['computed_unique_answer'] = 'B'
        row['solver_output_digest'] = 'sha256:' + '0' * 64
    elif mutation == 'verdict':
        row['verification'] = {'answer_key_verdict':'FAIL'}
    else:
        payload.pop('proof_method_binding', None)
    evidence.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match='(?i)(method|proof|result|verdict|integrity)'):
        C._corpus_totals(root)


def test_current_closure_recomputes_each_question_only_once(evidence_fixture, monkeypatch):
    from tests.test_qcm_current_evidence_guard import V2
    root, _source, _evidence = evidence_fixture
    original = V2.solver.solve
    calls = []
    def observed(inp):
        calls.append(inp.digest())
        return original(inp)
    monkeypatch.setattr(V2.solver, 'solve', observed)
    payload = C.build(root)
    assert payload['summary']['QCM_ANSWER_KEY_PROVEN'] == 1
    assert len(calls) == 1


@pytest.mark.parametrize('mutation', ['source', 'method', 'new_source'])
def test_mutating_an_input_during_computation_aborts(evidence_fixture, monkeypatch, mutation):
    from tests.test_qcm_current_evidence_guard import V2
    root, source, _evidence = evidence_fixture
    original = V2.solver.solve
    def mutate_after_calculation(inp):
        result = original(inp)
        if mutation == 'source':
            payload = json.loads(source.read_text())
            payload['questions'][0]['enonce'] += ' modified during computation'
            source.write_text(json.dumps(payload))
        elif mutation == 'method':
            path = root / 'scripts/latex_arith.py'
            path.write_text(path.read_text() + '\n# changed during computation\n')
        else:
            source.with_name('late-QCM.json').write_text(json.dumps({'chapitre':'EMPTY','questions':[]}))
        return result
    monkeypatch.setattr(V2.solver, 'solve', mutate_after_calculation)
    with pytest.raises(ValueError, match='changed during computation'):
        V2.build_evidence(root)


def test_head_change_during_computation_aborts(evidence_fixture, monkeypatch):
    from tests.test_qcm_current_evidence_guard import V2
    root, _source, _evidence = evidence_fixture
    calls = []
    def head(_root):
        calls.append(1)
        return 'a' * 40 if len(calls) == 1 else 'b' * 40
    monkeypatch.setattr(V2.freshness, 'head_sha', head)
    with pytest.raises(ValueError, match='HEAD changed during computation'):
        V2.build_evidence(root)


@pytest.mark.parametrize('part', ['runtime', 'historical_inputs'])
def test_runtime_and_historical_bindings_are_not_optional(evidence_fixture, part):
    root, _source, evidence = evidence_fixture
    payload = json.loads(evidence.read_text())
    payload['proof_method_binding'].pop(part)
    evidence.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match='proof method or dependency'):
        C._current_evidence(root)


def test_runtime_change_after_proof_replay_aborts_closure(evidence_fixture, monkeypatch):
    import mpmath
    root, _source, _evidence = evidence_fixture
    original = C._questions
    def change_runtime_after_validation(*args, **kwargs):
        rows = original(*args, **kwargs)
        monkeypatch.setattr(mpmath, '__version__', 'changed-after-proof-replay')
        return rows
    monkeypatch.setattr(C, '_questions', change_runtime_after_validation)
    with pytest.raises(ValueError, match='runtime|method|dependency'):
        C.build(root)
