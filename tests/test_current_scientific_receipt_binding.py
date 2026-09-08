"""A historical machine pass cannot certify replacement content."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import chapter_readiness as dashboard  # noqa: E402
import build_publish_readiness_chapter_matrix as matrix  # noqa: E402


@pytest.fixture
def chapter(tmp_path, monkeypatch):
    directory = tmp_path / 'chapitres/1SPE-RECEIPT'
    source = directory / 'cours/object.tex'
    source.parent.mkdir(parents=True)
    source.write_text('% META: {"id":"FIX-COURS", "type_objet":"cours"}\n$f(x)=2x$.\n')
    (directory / 'contrat.yaml').write_text('chapitre: 1SPE-RECEIPT\ncapacites: []\n')
    verifier = tmp_path / 'Mathematiques/manuel-maths/scripts/verify_sympy.py'
    verifier.parent.mkdir(parents=True)
    verifier.write_bytes((ROOT / 'Mathematiques/manuel-maths/scripts/verify_sympy.py').read_bytes())
    receipt = {'objet_id': 'object', 'gate': 'sympy', 'verdict': 'pass',
               'verification_protocol': 'EXECUTED_ASSERTIONS_PER_BLOCK_V1',
               'verifier_sha256': 'sha256:' + hashlib.sha256(verifier.read_bytes()).hexdigest(),
               'source_path': str(source.relative_to(tmp_path)),
               'source_sha256': 'sha256:' + hashlib.sha256(source.read_bytes()).hexdigest()}
    (directory / 'validations').mkdir()
    target = directory / 'validations/object.sympy.json'
    target.write_text(json.dumps(receipt))
    monkeypatch.setattr(dashboard, 'RACINE', tmp_path)
    monkeypatch.setattr(matrix, 'ROOT', tmp_path)
    return directory, source, target


@pytest.mark.parametrize('mutation', ['changed_sign', 'removed', 'replacement', 'wrong_identity', 'wrong_path'])
def test_stale_receipts_cannot_enter_either_current_scientific_count(chapter, mutation):
    directory, source, receipt_path = chapter
    receipt = json.loads(receipt_path.read_text())
    if mutation == 'changed_sign':
        source.write_text(source.read_text().replace('2x', '-2x'))
    elif mutation == 'removed':
        source.unlink()
    elif mutation == 'replacement':
        source.write_text('% META: {"id":"FIX-COURS", "type_objet":"cours"}\n$g(x)=x^3$.\n')
    elif mutation == 'wrong_identity':
        receipt['objet_id'] = 'ANOTHER-OBJECT'
    else:
        receipt['source_path'] = 'chapitres/OTHER/cours/object.tex'
    receipt_path.write_text(json.dumps(receipt))
    result = dashboard.analyser(directory, {}, {})
    assert result.scientific_review.get('pass', 0) == 0
    assert result.rejected_receipts
    science = matrix._oracle(directory, {'objects': []})
    assert science['pass'] == 0
    assert science['status'] == 'GAP'
    if source.exists():
        assert matrix._machine_science_current(source, directory) is False


def test_an_exact_current_binding_remains_usable(chapter):
    directory, source, _ = chapter
    assert dashboard.analyser(directory, {}, {}).scientific_review == {'pass': 1}
    assert matrix._oracle(directory, {'objects': []})['pass'] == 1
    assert matrix._machine_science_current(source, directory) is True



@pytest.mark.parametrize('field,value', [('gate', 'similarity'), ('gate', 'adversarial'), ('verdict', 'banana')])
def test_an_unsupported_gate_or_verdict_never_becomes_scientific_pass(chapter, field, value):
    directory, source, receipt_path = chapter
    receipt = json.loads(receipt_path.read_text())
    receipt[field] = value
    receipt_path.write_text(json.dumps(receipt))
    assert dashboard.analyser(directory, {}, {}).scientific_review == {}
    assert matrix._oracle(directory, {'objects': []})['status'] == 'GAP'
    assert matrix._machine_science_current(source, directory) is False


@pytest.mark.parametrize('mutation', ['different_object_same_count', 'changed_digest', 'duplicate_route'])
def test_disposition_count_cannot_replace_an_exact_current_object_set(chapter, mutation):
    directory, source, receipt_path = chapter
    receipt = json.loads(receipt_path.read_text())
    receipt['verdict'] = 'manual_review'
    receipt_path.write_text(json.dumps(receipt))
    row = {'chapter': directory.name, 'object_id': 'FIX-COURS',
           'path': str(source.relative_to(directory.parent.parent)),
           'source_sha256': receipt['source_sha256'], 'disposition': 'SCIENCE_HUMAINE_REQUISE'}
    assert matrix._oracle(directory, {'objects': [row]})['status'] == 'COMPLETE'
    if mutation == 'different_object_same_count':
        row['object_id'] = 'DIFFERENT-OBJECT'
    elif mutation == 'changed_digest':
        row['source_sha256'] = 'sha256:' + '0' * 64
    routes = [row, row] if mutation == 'duplicate_route' else [row]
    result = matrix._oracle(directory, {'objects': routes})
    assert result['status'] == 'GAP'
    assert result['rejected_dispositions']


def test_disposition_producer_binds_the_source_and_rejects_changed_content(chapter, monkeypatch):
    import build_manual_review_disposition_ledger as producer
    directory, source, receipt_path = chapter
    receipt = json.loads(receipt_path.read_text())
    receipt['verdict'] = 'manual_review'
    receipt_path.write_text(json.dumps(receipt))
    monkeypatch.setattr(producer, 'ROOT', directory.parent.parent)
    monkeypatch.setattr(producer, 'CHAPTER_ROOTS', (directory.parent,))
    current = producer.build_ledger()
    assert current['objects'][0]['source_sha256'] == receipt['source_sha256']
    source.write_text(source.read_text().replace('2x', '-2x'))
    stale = producer.build_ledger()
    assert stale['objects'] == []
    assert stale['machine_unclassified'] == 1
    assert stale['rejected_receipts'][0]['reason'] == 'SOURCE_DIGEST_CHANGED'


@pytest.mark.parametrize('mutation', ['old_protocol', 'changed_verifier', 'missing_protocol'])
def test_current_source_binding_does_not_make_an_obsolete_method_trustworthy(chapter, mutation):
    from scientific_receipt_binding import bind
    directory, source, receipt_path = chapter
    receipt = json.loads(receipt_path.read_text())
    if mutation == 'old_protocol':
        receipt['verification_protocol'] = 'RETURN_CODE_ONLY_V0'
    elif mutation == 'missing_protocol':
        receipt.pop('verification_protocol', None)
        receipt.pop('verifier_sha256', None)
    else:
        verifier = directory.parent.parent / 'Mathematiques/manuel-maths/scripts/verify_sympy.py'
        verifier.write_bytes(verifier.read_bytes() + b'\n# changed verification implementation\n')
    receipt_path.write_text(json.dumps(receipt))
    binding = bind(receipt, directory, directory.parent.parent)
    assert binding['state'] == 'CURRENT_BOUND'
    assert binding['method_state'] != 'CURRENT_TRUSTED'
    assert dashboard.analyser(directory, {}, {}).scientific_review == {}
    assert matrix._oracle(directory, {'objects': []})['status'] == 'GAP'
    assert matrix._machine_science_current(source, directory) is False


def test_old_nsi_execution_is_source_bound_but_not_a_scientific_certificate(tmp_path):
    from scientific_receipt_binding import bind
    chapter = tmp_path / 'NSI/chapitres/TNSI-FIX'
    source = chapter / 'cours/one.tex'
    source.parent.mkdir(parents=True)
    source.write_text('% META: {"id":"one"}\n% BEGIN-VERIFY\n% import math\n% END-VERIFY\n')
    receipt = {'objet_id': 'one', 'gate': 'sympy', 'verdict': 'pass',
               'reviewer': 'verify_python.py', 'source_path': str(source.relative_to(tmp_path / 'NSI')),
               'source_sha256': 'sha256:' + hashlib.sha256(source.read_bytes()).hexdigest()}
    binding = bind(receipt, chapter, tmp_path)
    assert binding['state'] == 'CURRENT_BOUND'
    assert binding['method_state'] == 'UNTRUSTED_NSI_VERIFICATION_METHOD'
