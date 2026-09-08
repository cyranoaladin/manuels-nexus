"""A historical QCM review must never certify different current content."""
import copy
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_qcm_review_closure as C
import build_qcm_review_proof_reconciliation as R
import qcm_reviews as D
import build_qcm_independent_evidence_v2 as V2


@pytest.fixture
def evidence_fixture(tmp_path):
    source = "Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/qcm/test-QCM.json"
    question = {"id": "Q1", "capacite": "C1", "enonce": r"Sachant $V(X)=9$, que vaut $\sigma(X)$ ?",
                "options": {"A": "$3$", "B": "$9$"}, "correcte": "A",
                "diagnostics": {"B": {"erreur": "La variance a été prise pour son écart-type.", "renvoi": "C1"}}}
    path = tmp_path / source
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"chapitre": "1SPE-SECOND-DEGRE", "questions": [question]}))
    for relative in V2._proof_input_paths(ROOT):
        if relative not in V2.METHOD_PATHS and not relative.startswith('audit/qcm_review_evidence/'):
            continue
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    evidence = V2.build_evidence(tmp_path)
    target = tmp_path / "audit/QCM_INDEPENDENT_EVIDENCE_V2.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(evidence))
    return tmp_path, path, target


def test_closure_rejects_a_stored_population_different_from_current(evidence_fixture):
    root, source, evidence = evidence_fixture
    assert C._corpus_totals(root)['total'] == 1
    payload = json.loads(source.read_text())
    payload['questions'] = []
    source.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match='(?i)(stale|perim|current|courant)'):
        C._corpus_totals(root)


@pytest.mark.parametrize('field', ['enonce', 'capacite', 'options', 'diagnostics'])
def test_complete_current_binding_rejects_source_mutation(evidence_fixture, field):
    root, source, evidence = evidence_fixture
    assert C._corpus_totals(root)['total'] == 1
    payload = json.loads(source.read_text())
    q = payload['questions'][0]
    if field in {'enonce', 'capacite'}:
        q[field] += ' changed'
    elif field == 'options':
        q['options']['B'] = '$2$'
    else:
        q['diagnostics']['B']['renvoi'] = 'C999'
    source.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match='current content differs'):
        C._questions(root)


def test_proven_key_is_not_complete_scientific_or_human_approval(evidence_fixture):
    root, _source, _evidence = evidence_fixture
    payload = C.build(root)
    assert payload['summary']['QCM_ANSWER_KEY_PROVEN'] == 1
    assert payload['summary']['QCM_SCIENTIFIC_REVIEW_PENDING'] == 1
    assert payload['summary']['QCM_HUMAN_APPROVAL_PENDING'] == 1
    assert payload['questions'][0]['state'] == C.OPEN
    assert payload['questions'][0]['human_approval'] == 'PENDING'


def conceptual_question():
    q, _ = R._load_corpus()[('1NSI-ALGO-DICHO-GLOUTON-KNN', 'Q1')]
    return {'options': dict(q['options']), 'cle': q['correcte'], 'enonce': q['enonce'],
            'diagnostics': copy.deepcopy(q['diagnostics']), 'capacity': q['capacite']}


@pytest.mark.parametrize('mutation', ['statement', 'option', 'diagnostic', 'capacity'])
def test_legacy_conceptual_review_never_rebinds_itself(mutation):
    question = conceptual_question()
    if mutation == 'statement':
        question['enonce'] = 'Quelle précondition de la dichotomie est inutile ?'
    elif mutation == 'option':
        question['options']['B'] = 'Le tableau doit être trié.'
    elif mutation == 'diagnostic':
        question['diagnostics']['B']['erreur'] = 'Une liste non triée garantit la dichotomie.'
    else:
        question['capacity'] = 'C999'
    result = C._evaluer_conceptuelle(question, D.CONCEPTUAL_REVIEWS[('1NSI-ALGO-DICHO-GLOUTON-KNN', 'Q1')], ROOT)
    assert result['state'] == C.OPEN
    assert result['current_scientific_credit'] is False


def test_legacy_mechanical_constants_cannot_prove_a_changed_statement():
    q, _ = R._load_corpus()[('TCOMPL-ECHANTILLONNAGE', 'Q6')]
    question = {'options': dict(q['options']), 'cle': q['correcte'],
                'enonce': 'X suit B(6,1/2) : quelle est son espérance ?',
                'diagnostics': q['diagnostics'], 'capacity': q['capacite']}
    family, derivation = D.MECHANICAL_DERIVATIONS[('TCOMPL-ECHANTILLONNAGE', 'Q6')]
    result = C._evaluer_mecanique(question, family, derivation)
    assert result['state'] == C.OPEN
    assert result['current_scientific_credit'] is False
    assert result['computed'] is None


def test_removed_question_has_historical_evidence_but_no_current_row():
    result = R.build_reconciliation()
    old = R._load_proof()
    current = R._load_corpus()
    retired = {(row['chapter'], row['question_id']) for row in result['historical_not_current']}
    assert retired == set(old) - set(current)
    key = ('1SPE-SECOND-DEGRE', 'Q16')
    assert key in old and key in retired and key not in current
    assert key not in {(r['chapter'], r['question_id']) for r in result['carried_forward'] + result['reproof_required']}
    row = next(row for row in result['historical_not_current'] if (row['chapter'],row['question_id']) == key)
    assert row['current_scientific_credit'] is False
    assert row['proof_semantic_digest'] == R.semantic_question_digest(R._semantic_fields_from_proof(old[key]))


def test_current_question_digest_includes_remediation_refs():
    question = R._load_corpus()[('1SPE-SECOND-DEGRE', 'Q12')][0]
    changed = copy.deepcopy(question)
    changed['diagnostics']['A']['renvoi'] = 'C999'
    assert R.current_question_digest(question) != R.current_question_digest(changed)


def test_current_payload_binding_detects_consistent_letter_permutation(evidence_fixture):
    root, source, _evidence = evidence_fixture
    assert C._corpus_totals(root)['total'] == 1
    payload = json.loads(source.read_text())
    q = payload['questions'][0]
    before_semantic = R.semantic_question_digest(R._semantic_fields_from_source(q))
    q['options'] = {'A': q['options']['B'], 'B': q['options']['A']}
    q['correcte'] = 'B'
    q['diagnostics'] = {'A': q['diagnostics']['B']}
    assert R.semantic_question_digest(R._semantic_fields_from_source(q)) == before_semantic
    source.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match='current content differs'):
        C._questions(root)


def test_current_payload_binding_detects_accents_and_option_order():
    q = {'id':'Q1', 'capacite':'C1', 'enonce':'derivee',
         'options':{'A':'0','B':'1'}, 'correcte':'A', 'diagnostics':{'B':{'erreur':'x','renvoi':'C1'}}}
    accented = copy.deepcopy(q)
    accented['enonce'] = 'dérivée'
    reordered = copy.deepcopy(q)
    reordered['options'] = dict(reversed(list(q['options'].items())))
    assert R.current_question_digest(q) != R.current_question_digest(accented)
    assert R.current_question_digest(q) != R.current_question_digest(reordered)


def test_unbound_historical_answer_does_not_create_current_key_disagreement():
    question = conceptual_question()
    question['cle'] = 'B'
    result = C._evaluer_conceptuelle(question, D.CONCEPTUAL_REVIEWS[('1NSI-ALGO-DICHO-GLOUTON-KNN', 'Q1')], ROOT)
    assert result['state'] == C.OPEN
    assert result['current_scientific_credit'] is False


def test_new_qcm_source_created_late_cannot_escape_the_input_set(evidence_fixture, monkeypatch):
    root, source, _evidence = evidence_fixture
    stamp = C.freshness.stamp
    calls = 0
    def insert_at_end(paths, root):
        nonlocal calls
        calls += 1
        if calls == 2:
            new_source = source.with_name('new-QCM.json')
            new_source.write_text(json.dumps({'chapitre':'1SPE-SECOND-DEGRE','questions':[]}))
        return stamp(paths, root)
    monkeypatch.setattr(C.freshness, 'stamp', insert_at_end)
    with pytest.raises(ValueError, match='(?i)(set|sources|ensemble)'):
        C.build(root)
