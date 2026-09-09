"""The coupled debt observer must use actual NSI scope and current evidence."""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from tests import test_current_scientific_receipt_binding as bindings
import build_nsi_coupled_review_debt as coupled

current_nsi_receipt = bindings.current_nsi_receipt


@pytest.fixture
def current(current_nsi_receipt, monkeypatch):
    monkeypatch.setattr(coupled, 'ROOT', current_nsi_receipt[0])
    return current_nsi_receipt


def observe(current):
    _, chapter, source, _, _ = current
    return coupled._execution_evidence(chapter, source, coupled._sha256_text(source.read_text()))


def test_discovery_uses_the_canonical_verifier_directories():
    from NSI.scripts.verify_python import SUBDIRS
    assert coupled.EXECUTABLE_SUBDIRS == frozenset(SUBDIRS)


@pytest.mark.parametrize('directory', ['cours', 'banque_ecrite', 'banque_pratique', 'amenagee'])
def test_a_real_current_execution_in_each_bank_can_be_credited(current, directory):
    from NSI.scripts import verify_python as verifier
    root, chapter, source, code, _ = current
    target = chapter / directory / source.name
    if target != source:
        target.parent.mkdir()
        source.rename(target)
    assert verifier.main(chapter.name, True) == 0
    result = observe((root, chapter, target, code, None))
    assert result['executable_scope'] is True
    assert result['source_bound_current'] is True
    assert result['execution_passed'] is True
    assert result['evidence_gap'] is False
    assert result['certifies_documentary_claims'] is False


@pytest.mark.parametrize('mutation', ['source', 'python', 'verifier', 'unreadable', 'manual', 'fail', 'different_source'])
def test_noncurrent_or_unexecuted_evidence_cannot_be_machine_credit(current, mutation):
    root, chapter, source, code, record = current
    receipt = chapter / 'validations/one.execution.json'
    if mutation == 'source':
        source.write_text(source.read_text() + 'Changed content.\n')
    elif mutation == 'python':
        code.write_text('value = 3\n')
    elif mutation == 'verifier':
        verifier = root / 'NSI/scripts/verify_python.py'
        verifier.write_text(verifier.read_text() + '\n# changed method\n')
    elif mutation == 'unreadable':
        receipt.write_text('{invalid')
    elif mutation == 'different_source':
        other = chapter / 'cours/other.tex'
        other.write_bytes(source.read_bytes())
        record['source_path'] = str(other.relative_to(root / 'NSI'))
        receipt.write_text(json.dumps(record))
    else:
        record['verdict'] = 'manual_review' if mutation == 'manual' else 'fail'
        receipt.write_text(json.dumps(record))
    result = observe(current)
    assert result['execution_passed'] is False
    assert result['evidence_gap'] is True
    assert coupled._execution_summary([{'execution_evidence': result}])['status'] != 'COMPLETE'


def test_a_qcm_with_code_is_unchecked_instead_of_declared_inapplicable(current):
    root, chapter, source, code, _ = current
    qcm = chapter / 'qcm/one.tex'
    qcm.parent.mkdir()
    source.rename(qcm)
    result = observe((root, chapter, qcm, code, None))
    assert result['executable_scope'] is False
    assert result['execution_applicability'] == 'EXECUTION_REQUIRED'
    assert result['execution_state'] == 'UNCHECKED_EXECUTABLE_SOURCE'
    assert result['evidence_gap'] is True


def test_an_actual_code_free_source_needs_no_fake_execution(current):
    root, chapter, source, code, _ = current
    source.write_text('% META: {"id":"one"}\nUn texte documentaire sans code.\n')
    result = observe((root, chapter, source, code, None))
    assert result['execution_applicability'] == 'EXECUTION_NOT_APPLICABLE'
    assert result['execution_passed'] is False
    assert result['evidence_gap'] is False
    assert result['scientific_review_state'] == 'NOT_EVALUATED_BY_EXECUTION'


def test_summary_distinguishes_present_receipts_from_current_successes(current):
    ok = observe(current)
    assert coupled._execution_summary([{'execution_evidence': ok}])['status'] == 'COMPLETE'
    current[3].write_text('value = 9\n')
    stale = observe(current)
    summary = coupled._execution_summary([{'execution_evidence': stale}])
    assert summary['receipts_found'] == 1
    assert summary['missing_receipts'] == 0
    assert summary['execution_passed'] == 0
    assert summary['evidence_gaps'] == 1
    assert summary['status'] != 'COMPLETE'


def test_stored_quality_counters_are_not_newly_certified(current):
    root = current[0]
    audit = root / 'audit'
    audit.mkdir()
    records = {
        'TRUE_PEDAGOGICAL_COVERAGE.json': {'rows': []},
        'P0_CONTENT_CLONE_LEDGER.json': {'objects_on_invalid_credit': [], 'objects_with_indeterminate_credit': []},
        'NSI_CROSS_DISCIPLINE_CONTENT_LEDGER.json': {'condemned_count': 0, 'unknown': 0},
    }
    for filename, value in records.items():
        (audit / filename).write_text(json.dumps(value))
    result = coupled._machine_verification([{'execution_evidence': observe(current)}])
    for name in ('clone_capacity_integrity', 'cross_discipline', 'role_coverage'):
        assert result[name]['status'] == 'HISTORICAL_NOT_RECHECKED'
        assert result[name]['current_credit'] is False
        assert result[name]['source_sha256'].startswith('sha256:')


@pytest.mark.parametrize('mutation', ['omitted', 'changed_metadata', 'duplicate'])
def test_an_inventory_cannot_change_the_actual_current_source_population(current, monkeypatch, mutation):
    root, chapter, source, _, _ = current
    monkeypatch.setattr(coupled, 'CHAPTERS', (chapter.name,))
    meta = {'id': 'one'}
    row = {'path': source.relative_to(root).as_posix(), 'metadata': meta}
    inventory = {'manuals': {'TNSI': {'chapters': {chapter.name: {'objects': [row]}}}}}
    assert coupled._reconcile_source_inventory(inventory) == (source,)
    if mutation == 'omitted':
        inventory['manuals']['TNSI']['chapters'][chapter.name]['objects'] = []
    elif mutation == 'changed_metadata':
        row['metadata'] = {'id': 'another-object'}
    else:
        inventory['manuals']['TNSI']['chapters'][chapter.name]['objects'].append(row)
    with pytest.raises(ValueError, match='inventory'):
        coupled._reconcile_source_inventory(inventory)


@pytest.fixture
def ledger_fixture(current, monkeypatch):
    root, chapter, source, _, _ = current
    monkeypatch.setattr(coupled, 'CHAPTERS', (chapter.name,))
    audit = root / 'audit'
    audit.mkdir()
    for filename, payload in {
        'TRUE_PEDAGOGICAL_COVERAGE.json': {'rows': []},
        'P0_CONTENT_CLONE_LEDGER.json': {'objects_on_invalid_credit': [], 'objects_with_indeterminate_credit': []},
        'NSI_CROSS_DISCIPLINE_CONTENT_LEDGER.json': {'condemned_count': 0, 'unknown': 0},
    }.items():
        (audit / filename).write_text(json.dumps(payload))
    relative = source.relative_to(root).as_posix()
    inventory = {'manuals': {'TNSI': {'chapters': {chapter.name: {'objects': [
        {'path': relative, 'metadata': {'id': 'one'}}
    ]}}}}, 'anomalies': {'blocking_statuses': [
        {'id': 'one', 'path': relative, 'chapter': chapter.name, 'scope': 'object', 'status': 'generated'}
    ]}}
    return current, inventory


def test_default_build_requests_fresh_inventory_and_ignores_the_deposited_snapshot(ledger_fixture, monkeypatch):
    current, inventory = ledger_fixture
    old = current[0] / 'audit/INVENTAIRE_COLLECTION.json'
    old.write_text('{invalid historical snapshot')
    implementation = coupled._inventory_module()
    calls = []

    def fresh(root, **kwargs):
        calls.append((root, kwargs))
        return inventory

    monkeypatch.setattr(coupled, '_inventory_module', lambda: SimpleNamespace(
        build_inventory=fresh, _anomaly_fingerprint=implementation._anomaly_fingerprint))
    result = coupled.build_ledger()
    assert calls == [(current[0], {'require_git_provenance': True})]
    assert result['count'] == 1
    assert result['entries'][0]['machine_verified_by_execution'] is True
    assert result['release_acceptance'] is False
    assert result['entries'][0]['human_review_required'] is True


@pytest.mark.parametrize('mutation', ['python', 'new_receipt', 'historical_quality'])
def test_end_to_end_observation_refuses_changed_inputs(ledger_fixture, monkeypatch, mutation):
    current, inventory = ledger_fixture
    original = coupled._machine_verification

    def race(entries):
        result = original(entries)
        if mutation == 'python':
            current[3].write_text('value = 3\n')
        elif mutation == 'new_receipt':
            (current[1] / 'validations/extra.execution.json').write_text('{}')
        else:
            (current[0] / 'audit/TRUE_PEDAGOGICAL_COVERAGE.json').write_text('{"rows":[],"changed":true}')
        return result

    monkeypatch.setattr(coupled, '_machine_verification', race)
    with pytest.raises(ValueError, match='changed'):
        coupled.build_ledger(inventory=inventory)
