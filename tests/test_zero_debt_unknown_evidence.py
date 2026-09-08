"""An unknown counter is evidence debt, never a zero-defect measurement."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_zero_technical_debt as gate  # noqa: E402


@pytest.fixture
def complete(tmp_path):
    audit = tmp_path / 'audit'
    audit.mkdir()
    records = {
        'PARITY_BAREMES_VALIDATION.json': {'summary': {key: 0 for key in (
            'STUDENT_WITHOUT_CORRECTION', 'ORPHAN_TEACHER_CORRECTION',
            'STUDENT_TEACHER_STATEMENT_DRIFT', 'TEACHER_CONTENT_LEAK_IN_STUDENT',
            'BAREME_TOTAL_MISMATCH', 'BAREME_SCOPE_AMBIGUOUS')}},
        'OPEN_FINDINGS.json': {'clone_finding_ids': [], 'summary': {
            'TRUE_PRODUCT_CLONES_OPEN': 0, 'STUDENT_TEACHER_STATEMENT_DRIFT': 0}},
        'PROGRAMME_CONTENT_VALIDATION.json': {'summary': {key: 0 for key in (
            'OFFICIAL_ATOMS_UNCOVERED', 'FALSE_COVERAGE', 'UNLABELLED_OUT_OF_PROGRAMME_CONTENT',
            'CONCRETE_DEFECTS_FOUND', 'UNREVIEWED_MANUAL_OBJECTS')}},
        'FINAL_PRINT_PREFLIGHT.json': {'summary': {'total_targets': 12, 'passed_targets': 12}},
        'BUILD_MANIFEST.json': {'builds': [{} for _ in range(12)]},
        'DOUBLE_BUILD_REPRODUCIBILITY.json': {'summary': {'total_targets': 12, 'reproducible_targets': 12}},
    }
    for filename, payload in records.items():
        (audit / filename).write_text(json.dumps(payload))
    return tmp_path


def test_a_complete_fixture_can_still_pass(complete):
    result = gate.audit_technical_debt(complete)
    assert result['all_product_debts_zero'] is True
    assert result['product_debt_summary']['EVIDENCE_DEBT_OPEN'] == 0


@pytest.mark.parametrize('unknown', [None, 'NOT_EVALUATED', False, -1, 0.5])
def test_unknown_or_invalid_programme_counter_blocks_without_inventing_product_defect(complete, unknown, monkeypatch):
    path = complete / 'audit/PROGRAMME_CONTENT_VALIDATION.json'
    record = json.loads(path.read_text())
    record['summary']['CONCRETE_DEFECTS_FOUND'] = unknown
    path.write_text(json.dumps(record))
    result = gate.audit_technical_debt(complete)
    assert result['all_product_debts_zero'] is False
    assert result['product_debt_summary']['EVIDENCE_DEBT_OPEN'] == 1
    assert result['product_debt_summary']['PROGRAMME_DEBT_OPEN'] == 0  # known subtotal only
    assert result['debt_measurement_status']['PROGRAMME_DEBT_OPEN'] == 'INCOMPLETE_EVIDENCE'
    assert result['missing_or_malformed_evidence'] == ['audit/PROGRAMME_CONTENT_VALIDATION.json#CONCRETE_DEFECTS_FOUND']
    markdown = (complete / 'audit/ZERO_TECHNICAL_DEBT_REPORT.md').read_text()
    programme_line = next(line for line in markdown.splitlines() if '| **Dette de Programme' in line)
    assert 'CLEARED' not in programme_line
    assert 'INCOMPLETE_EVIDENCE' in programme_line
    monkeypatch.setattr(sys, 'argv', ['build_zero_technical_debt', '--root', str(complete)])
    assert gate.main() == 1


def test_a_real_programme_defect_is_still_product_debt(complete):
    path = complete / 'audit/PROGRAMME_CONTENT_VALIDATION.json'
    record = json.loads(path.read_text())
    record['summary']['FALSE_COVERAGE'] = 2
    path.write_text(json.dumps(record))
    result = gate.audit_technical_debt(complete)
    assert result['product_debt_summary']['PROGRAMME_DEBT_OPEN'] == 2
    assert result['product_debt_summary']['EVIDENCE_DEBT_OPEN'] == 0
    assert result['all_product_debts_zero'] is False
    assert result['debt_measurement_status']['PROGRAMME_DEBT_OPEN'] == 'MEASURED_OPEN_DEBT'
