"""A trusted execution result is not a documentary scientific review."""
import json

import pytest

from tests import test_current_scientific_receipt_binding as bindings

current_nsi_receipt = bindings.current_nsi_receipt
dashboard = bindings.dashboard


@pytest.fixture
def scope_receipt(current_nsi_receipt):
    _, chapter, _, _, _ = current_nsi_receipt
    (chapter / 'contrat.yaml').write_text('chapitre: TNSI-FIX\ncapacites: []\n')
    return current_nsi_receipt


def test_trusted_nsi_execution_remains_separate_from_scientific_review(scope_receipt, monkeypatch):
    root, chapter, _, _, _ = scope_receipt
    monkeypatch.setattr(dashboard, 'RACINE', root)
    result = dashboard.analyser(chapter, {}, {})
    assert result.scientific_review == {}
    assert result.execution_review == {'pass': 1}
    assert result.documentary_review == 'REQUIRES_CURRENT_INDEPENDENT_REVIEW'


@pytest.mark.parametrize('mutation', ['failed_execution', 'changed_source', 'forged_documentary_credit'])
def test_separate_execution_reporting_does_not_hide_failures_or_accept_false_scope(scope_receipt, monkeypatch, mutation):
    root, chapter, source, _, receipt = scope_receipt
    monkeypatch.setattr(dashboard, 'RACINE', root)
    target = chapter / 'validations/one.execution.json'
    if mutation == 'failed_execution':
        receipt['verdict'] = 'fail'
    elif mutation == 'changed_source':
        source.write_text(source.read_text() + '\nUn contenu documentaire nouveau.\n')
    else:
        receipt['certifies_documentary_claims'] = True
    target.write_text(json.dumps(receipt))
    result = dashboard.analyser(chapter, {}, {})
    assert result.scientific_review == {}
    if mutation == 'failed_execution':
        assert result.execution_review == {'fail': 1}
        assert any('exécution' in row and 'échec' in row for row in result.blocking_findings)
    else:
        assert result.execution_review == {}
        assert result.rejected_receipts
