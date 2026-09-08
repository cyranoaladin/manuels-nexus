"""Forensics resolves provenance, without crediting unbound historical passes."""
from pathlib import Path
import sys
import json

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_validation_evidence_bindings as gate  # noqa: E402


def test_internal_identity_can_bind_a_renamed_receipt_but_not_certify_its_bytes():
    base = 'NSI/chapitres/TNSI-FIX'
    source = b'% META: {"id":"TNSI-FIX-EX-001"}\nActual source.\n'
    files = {base + '/exercices/new_filename.tex': source,
             base + '/validations/old_filename.similarity.json': json.dumps({
                 'objet_id': 'TNSI-FIX-EX-001', 'verdict': 'pass'}).encode()}
    row = gate.classify(files, {})[0]
    assert row['binding'] == 'INTERNAL_CANONICAL_OBJECT_ID'
    assert row['status'] == 'VALIDATION_STALE'
    assert row['current_binding_valid'] is False


def test_retired_id_reused_with_new_content_cannot_inherit_old_digest():
    base = 'NSI/chapitres/TNSI-FIX'
    path = base + '/exercices/FIX.tex'
    old = b'% META: {"id":"FIX"}\nOld content.\n'
    files = {path: old.replace(b'Old', b'New'), base + '/validations/FIX.execution.json': json.dumps({
        'objet_id': 'FIX', 'verdict': 'pass', 'source_path': path, 'source_sha256': gate.sha(old)}).encode()}
    row = gate.classify(files, {path: old})[0]
    assert row['status'] == 'VALIDATION_STALE'
    assert row['reason'] == 'SOURCE_DIGEST_CHANGED'
    assert row['current_binding_valid'] is False


def test_deleted_source_remains_bound_to_its_historical_version():
    base = 'NSI/chapitres/TNSI-FIX'
    path = base + '/cours/old_name.tex'
    files = {base + '/validations/old_name.similarity.json': json.dumps({'objet_id': 'old_name', 'verdict': 'pass'}).encode()}
    old = b'% META: {"id":"TNSI-FIX-COURS"}\nOld content.\n'
    row = gate.classify(files, {path: old})[0]
    assert row['status'] == 'VALIDATION_HISTORICAL'
    assert row['sources'][0]['source_sha256'] == gate.sha(old)
    assert row['current_binding_valid'] is False


@pytest.mark.parametrize('mutation', ['identity', 'source_path', 'source_bytes'])
def test_current_explicit_binding_rejects_changed_scope_or_bytes(mutation):
    base = 'NSI/chapitres/TNSI-FIX'
    path = base + '/exercices/FIX.tex'
    receipt = base + '/validations/FIX.execution.json'
    source = b'% META: {"id":"FIX"}\nVerified original statement.\n'
    record = {'objet_id': 'FIX', 'verdict': 'pass',
              'source_path': path, 'source_sha256': gate.sha(source)}
    files = {path: source, receipt: json.dumps(record).encode()}
    assert gate.classify(files, {})[0]['status'] == 'VALIDATION_BOUND_CURRENT'
    if mutation == 'identity':
        record['objet_id'] = 'UNRELATED'
    elif mutation == 'source_path':
        # An explicit missing path must not fall back to the matching ID.
        record['source_path'] = base + '/exercices/missing.tex'
    else:
        files[path] = source.replace(b'original', b'changed')
    files[receipt] = json.dumps(record).encode()
    assert gate.classify(files, {})[0]['current_binding_valid'] is False


def test_ambiguous_internal_id_does_not_choose_a_source_by_filename():
    base = 'NSI/chapitres/TNSI-FIX'
    source = b'% META: {"id":"FIX"}\nAmbiguous identity.\n'
    files = {base + '/exercices/FIX.tex': source,
             base + '/methodes/different_name.tex': source,
             base + '/validations/FIX.similarity.json': json.dumps({
                 'objet_id': 'FIX', 'verdict': 'pass'}).encode()}
    assert gate.classify(files, {})[0]['status'] == 'VALIDATION_UNBOUND'
