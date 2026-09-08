"""Execution, current independent reading and historical dispositions are distinct."""
from __future__ import annotations

import copy
import json
from types import SimpleNamespace

import pytest

from tests import test_current_scientific_receipt_binding as bindings
from tests.test_current_review_index import review_for

import build_current_review_index as current_review
import build_programme_content_validation as programme

current_nsi_receipt = bindings.current_nsi_receipt


@pytest.fixture
def history(current_nsi_receipt, monkeypatch):
    from NSI.scripts import verify_python as verifier

    root, old_chapter, old_source, _, _ = current_nsi_receipt
    chapter = old_chapter.with_name('TNSI-HISTOIRE-INFORMATIQUE')
    old_chapter.rename(chapter)
    source = chapter / 'cours' / old_source.name
    meta = {'id': 'one', 'chapitre': chapter.name, 'type_objet': 'cours',
            'status': 'generated', 'capacites_codes': ['C1']}
    body = source.read_text().split('\n', 1)[1]
    source.write_text('% META: ' + json.dumps(meta) + '\nUne date reste à documenter.\n' + body)
    contract = chapter / 'contrat.yaml'
    contract.write_text('chapitre: TNSI-HISTOIRE-INFORMATIQUE\ncapacites: []\n')
    assert verifier.main(chapter.name, True) == 0
    receipt = chapter / 'validations/one.execution.json'
    inventory = {'manuals': {'TNSI': {'chapters': {chapter.name: {
        'contract_path': str(contract.relative_to(root)),
        'objects': [{'id': meta['id'], 'path': str(source.relative_to(root)), 'metadata': meta}],
    }}}}}
    reviews = []

    def build_actual_index(*_args, **_kwargs):
        return current_review.build(root, inventory, reviews=reviews, retired=[], new_paths=set())

    monkeypatch.setattr(current_review, 'build_fresh', build_actual_index)
    audit = root / 'audit'
    audit.mkdir()
    atoms = audit / 'atoms.json'
    atoms.write_text(json.dumps({'atoms': [{'atom_id': 'A1', 'mandatory': 'YES'}]}))
    coverage = audit / 'coverage.json'
    coverage.write_text(json.dumps({'rows': [{
        'atom_id': 'A1', 'coverage_status': 'MAPPED',
        'course_sources': [str(source.relative_to(root))],
    }]}))
    monkeypatch.setattr(programme, 'ROOT', root)
    monkeypatch.setattr(programme, 'ATOMS_PATH', atoms)
    monkeypatch.setattr(programme, 'COVERAGE_PATH', coverage)
    monkeypatch.setattr(programme, 'JSON_TARGET', audit / 'report.json')
    monkeypatch.setattr(programme, 'MD_TARGET', audit / 'report.md')
    return SimpleNamespace(root=root, chapter=chapter, source=source, receipt=receipt,
                           reviews=reviews, index=build_actual_index)


def test_execution_does_not_review_a_date_or_the_whole_object(history):
    report = programme.validate_programme_and_content()
    assert report['summary']['PASSED_INDEPENDENT_VALIDATIONS'] == 0
    assert report['summary']['CURRENT_EXECUTION_PASSED'] == 1
    assert report['summary']['INDEPENDENT_REVIEW_PENDING'] == 1
    assert 'DOCUMENTARY_HISTORICAL_REVIEW' in report['current_objects'][0]['pending_dimensions']


def test_exact_current_independent_dimensions_can_close_scientific_scope(history):
    history.reviews.append(review_for(history.index()))
    report = programme.validate_programme_and_content()
    assert report['summary']['PASSED_INDEPENDENT_VALIDATIONS'] == 1
    assert report['summary']['INDEPENDENT_REVIEW_PENDING'] == 0
    assert programme.main() == 0


def test_science_without_required_documentary_reading_remains_pending(history):
    review = review_for(history.index())
    review['dimensions']['DOCUMENTARY_HISTORICAL_REVIEW']['state'] = 'PENDING'
    history.reviews.append(review)
    assert programme.validate_programme_and_content()['summary']['PASSED_INDEPENDENT_VALIDATIONS'] == 0
    assert programme.main() == 1


@pytest.mark.parametrize('mutation', ['source', 'verifier', 'python', 'forged_documentary', 'unknown_verdict', 'unreadable'])
def test_unusable_receipt_cannot_be_current_execution_or_science(history, mutation):
    history.reviews.append(review_for(history.index()))
    receipt = json.loads(history.receipt.read_text())
    if mutation == 'source':
        history.source.write_text(history.source.read_text().replace('Une date', 'Une autre date'))
    elif mutation == 'verifier':
        helper = history.root / 'NSI/scripts/verify_python.py'
        helper.write_text(helper.read_text() + '\n# changed verifier\n')
    elif mutation == 'python':
        (history.chapter / 'code/value.py').write_text('value = 3\n')
    elif mutation == 'forged_documentary':
        receipt['certifies_documentary_claims'] = True
    elif mutation == 'unknown_verdict':
        receipt['verdict'] = 'verified'
    if mutation in {'forged_documentary', 'unknown_verdict'}:
        history.receipt.write_text(json.dumps(receipt))
    elif mutation == 'unreadable':
        history.receipt.write_text('{invalid')
    result = programme.validate_programme_and_content()
    assert result['summary']['PASSED_INDEPENDENT_VALIDATIONS'] == 0
    assert result['summary']['CURRENT_EXECUTION_PASSED'] == 0
    assert result['summary']['REJECTED_VALIDATION_RECEIPTS'] == 1
    assert result['rejected_validations']
    assert programme.main() == 1


def test_an_id_only_historical_disposition_never_closes_manual_review(history):
    # Genuine writer, no executable claims: the source is documentary only.
    from NSI.scripts import verify_python as verifier
    history.source.write_text(history.source.read_text().split('\n', 1)[0] + '\nUne date à documenter.\n')
    assert verifier.main(history.chapter.name, True) == 0
    disposition = {'entries': [{'object_id': 'one', 'classification': 'NON_FORMALIZABLE_NO_CONCRETE_DEFECT',
                                'defects': [], 'review_method': 'old unbound declaration'}]}
    (history.root / 'audit/MANUAL_REVIEW_ADVERSARIAL_DISPOSITION.json').write_text(json.dumps(disposition))
    result = programme.validate_programme_and_content()
    assert result['summary']['UNREVIEWED_MANUAL_OBJECTS'] == 1
    assert result['summary']['NON_FORMALIZABLE_NO_CONCRETE_DEFECT'] == 0
    assert result['summary']['CONCRETE_DEFECTS_FOUND'] is None
    assert result['historical_dispositions']['entries'] == disposition['entries']
    assert result['historical_dispositions']['current_credit'] is False


def test_receipt_aliases_cannot_double_count_one_current_source(history):
    history.reviews.append(review_for(history.index()))
    alias = history.receipt.with_name('alias.execution.json')
    alias.write_bytes(history.receipt.read_bytes())
    result = programme.validate_programme_and_content()
    assert result['summary']['PASSED_INDEPENDENT_VALIDATIONS'] == 0
    assert result['summary']['DUPLICATE_VALIDATION_BINDINGS'] == 1
    assert len(result['current_objects']) == 1
    assert programme.main() == 1


def test_current_execution_failure_is_not_hidden_by_a_review(history):
    history.reviews.append(review_for(history.index()))
    record = json.loads(history.receipt.read_text())
    record['verdict'] = 'fail'
    history.receipt.write_text(json.dumps(record))
    result = programme.validate_programme_and_content()
    assert result['summary']['INDEPENDENT_ANSWER_MISMATCH'] == 1
    assert result['summary']['PASSED_INDEPENDENT_VALIDATIONS'] == 0
    assert programme.main() == 1


def test_pending_review_blocks_cli_even_with_no_answer_mismatch(history):
    assert programme.main() == 1
    report = json.loads(programme.JSON_TARGET.read_text())
    assert report['summary']['INDEPENDENT_ANSWER_MISMATCH'] == 0


def test_changed_review_supporting_note_cannot_retain_science(history):
    note = history.root / 'audit/independent-note.json'
    note.write_text('{"scope":"fixture reading"}')
    review = review_for(history.index())
    review['evidence_note'] = {'path': str(note.relative_to(history.root)),
                               'sha256': current_review.sha256(note.read_bytes())}
    history.reviews.append(copy.deepcopy(review))
    assert programme.validate_programme_and_content()['summary']['PASSED_INDEPENDENT_VALIDATIONS'] == 1
    note.write_text('{"scope":"different reading"}')
    assert programme.validate_programme_and_content()['summary']['PASSED_INDEPENDENT_VALIDATIONS'] == 0


def test_manual_review_cannot_satisfy_an_actual_execution_requirement(history):
    history.reviews.append(review_for(history.index()))
    record = json.loads(history.receipt.read_text())
    record['verdict'] = 'manual_review'
    history.receipt.write_text(json.dumps(record))
    result = programme.validate_programme_and_content()
    assert result['summary']['PASSED_INDEPENDENT_VALIDATIONS'] == 0
    assert result['current_objects'][0]['execution_requirement_state'] == 'CURRENT_EXECUTION_REQUIRED'


def test_documentary_only_object_needs_reading_but_no_fake_execution(history):
    from NSI.scripts import verify_python as verifier
    history.source.write_text(history.source.read_text().split('\n', 1)[0] + '\nUne date à documenter.\n')
    assert verifier.main(history.chapter.name, True) == 0
    history.reviews.append(review_for(history.index()))
    result = programme.validate_programme_and_content()
    assert result['summary']['CURRENT_EXECUTION_PASSED'] == 0
    assert result['summary']['PASSED_INDEPENDENT_VALIDATIONS'] == 1
    assert result['current_objects'][0]['execution_requirement_state'] == 'NO_EXECUTABLE_CLAIMS_IN_SOURCE'


@pytest.mark.parametrize('mutation', ['receipt_content', 'receipt_set', 'coverage_input', 'review_source'])
def test_inputs_cannot_change_during_the_consumer_observation(history, monkeypatch, mutation):
    original = programme._validation_evidence

    def race(*args):
        result = original(*args)
        if mutation == 'receipt_content':
            history.receipt.write_text(history.receipt.read_text() + '\n')
        elif mutation == 'receipt_set':
            history.receipt.with_name('added.execution.json').write_bytes(history.receipt.read_bytes())
        elif mutation == 'coverage_input':
            programme.COVERAGE_PATH.write_text(programme.COVERAGE_PATH.read_text() + '\n')
        else:
            history.source.write_text(history.source.read_text() + '\n')
        return result

    monkeypatch.setattr(programme, '_validation_evidence', race)
    with pytest.raises(ValueError, match='changed'):
        programme.validate_programme_and_content()
