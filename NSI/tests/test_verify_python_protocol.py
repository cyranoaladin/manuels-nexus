"""Mutation tests for executed NSI claims, independent from documentary review."""
from __future__ import annotations

import json

import pytest

from NSI.scripts import verify_python as gate


def verify(program):
    return '% BEGIN-VERIFY\n' + '\n'.join('% ' + line for line in program.splitlines()) + '\n% END-VERIFY\n'


def check(tmp_path, source):
    tex = tmp_path / 'object.tex'
    tex.write_text(source)
    return gate.check_object(tex, no_ruff=True)


@pytest.mark.parametrize('program', [
    'import math',
    'if False:\n    assert False',
    'try:\n    assert 1 == 2\nexcept AssertionError:\n    pass',
    'import sys\nsys.exit(0)',
])
def test_a_zero_return_code_is_not_an_exercised_proof(tmp_path, program):
    assert check(tmp_path, verify(program))['verdict'] == 'fail'


def test_every_verify_block_must_exercise_its_own_assertion(tmp_path):
    assert check(tmp_path, verify('assert 2 + 2 == 4') + verify('import math'))['verdict'] == 'fail'


def test_real_assertions_are_accepted(tmp_path):
    result = check(tmp_path, verify('def twice(x):\n    return 2*x\nassert twice(0) == 0\nassert twice(-1) == -2'))
    assert result['verdict'] == 'verified'
    assert result['checks'][0]['assertions_executed'] == 2


def test_no_ruff_cannot_certify_an_unexecuted_listing(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, 'ROOT', tmp_path)
    (tmp_path / 'print_value.py').write_text('print(2)\n')
    result = check(tmp_path, '% PYTHON-SOURCE: print_value.py\n\\begin{python}\nprint(2)\n\\end{python}\n')
    assert result['verdict'] == 'manual_review'
    assert any(row['type'] == 'listing_execution' and row['state'] == 'PENDING' for row in result['checks'])


def test_trace_spaces_are_not_removed_to_obtain_a_match(tmp_path):
    result = check(tmp_path, '% BEGIN-TRACE\n% print(" 2 ")\n% EXPECTED\n% 2\n% END-TRACE\n')
    assert result['verdict'] == 'fail'


def test_documentary_claims_are_not_certified_by_an_execution(tmp_path):
    result = check(tmp_path, 'En 9999, ce programme fut inventé.\n' + verify('assert 1 == 1'))
    assert result['certifies_documentary_claims'] is False


def test_receipt_binds_actual_method_and_explicit_python_dependency(tmp_path, monkeypatch):
    chapter = tmp_path / 'chapitres/TNSI-FIX'
    source = chapter / 'cours/object.tex'
    source.parent.mkdir(parents=True)
    code = chapter / 'code/value.py'
    code.parent.mkdir()
    code.write_text('value = 2\n')
    source.write_text('% META: {"id":"object"}\n% PYTHON-SOURCE: code/value.py\n'
                      '\\begin{python}\nvalue = 2\n\\end{python}\n' + verify('value = 2\nassert value == 2'))
    monkeypatch.setattr(gate, 'ROOT', tmp_path)
    assert gate.main('TNSI-FIX', True) == 0
    receipt = json.loads((chapter / 'validations/object.execution.json').read_text())
    assert receipt['verification_protocol'] == 'NSI_EXECUTED_CLAIMS_V1'
    assert receipt['verifier_sha256']
    assert receipt['dependency_digests']['chapitres/TNSI-FIX/code/value.py']
    assert receipt['certifies_documentary_claims'] is False
    code.write_text('value = 3\n')
    result = gate.check_object(source, no_ruff=True)
    assert result['verdict'] == 'fail'
    assert any(c['type'] == 'printed_source_alignment' and not c['pass'] for c in result['checks'])


def test_trace_requires_normal_completion(tmp_path):
    result = check(tmp_path, '% BEGIN-TRACE\n% print(2)\n% raise SystemExit(0)\n% EXPECTED\n% 2\n% END-TRACE\n')
    assert result['verdict'] == 'fail'


def test_wrapper_placeholders_inside_programs_are_preserved(tmp_path):
    result = check(tmp_path, verify('assert "COMPLETION_MARKER".startswith("COMP")'))
    assert result['verdict'] == 'verified'


def test_each_repeated_python_source_listing_is_compared(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, 'ROOT', tmp_path)
    code = tmp_path / 'value.py'
    code.write_text('value = 2\n')
    source = ('% PYTHON-SOURCE: value.py\n\\begin{python}\nvalue = 3\n\\end{python}\n'
              '% PYTHON-SOURCE: value.py\n\\begin{python}\nvalue = 2\n\\end{python}\n'
              + verify('value = 3\nvalue = 2\nassert value == 2'))
    assert check(tmp_path, source)['verdict'] == 'fail'


def test_receipt_never_binds_observation_to_changed_source(tmp_path, monkeypatch):
    chapter = tmp_path / 'chapitres/TNSI-FIX'
    source = chapter / 'cours/object.tex'
    source.parent.mkdir(parents=True)
    source.write_text(verify('assert 1 == 1'))
    monkeypatch.setattr(gate, 'ROOT', tmp_path)
    original = gate.check_object
    def change_after_check(tex, no_ruff):
        result = original(tex, no_ruff)
        tex.write_text(verify('assert 1 == 2'))
        return result
    monkeypatch.setattr(gate, 'check_object', change_after_check)
    assert gate.main('TNSI-FIX', True) > 0
    record = json.loads((chapter / 'validations/object.execution.json').read_text())
    assert record['verdict'] == 'fail'
    assert record['source_sha256'] != gate.protocol.digest(source.read_bytes())


def test_malformed_second_verify_block_is_not_silently_excluded(tmp_path):
    source = verify('assert 1 == 1') + '% BEGIN-VERIFY\n% assert False\n'
    assert check(tmp_path, source)['verdict'] == 'fail'


def test_private_assertion_instrumentation_cannot_be_shadowed(tmp_path):
    source = verify('__nexus_start__ = lambda: None\nassert 1 == 1')
    assert check(tmp_path, source)['verdict'] == 'fail'


def test_executed_inline_listing_requires_its_published_python_source(tmp_path):
    source = '\\begin{python}\nvalue = 2\n\\end{python}\n' + verify('value = 2\nassert value == 2')
    result = check(tmp_path, source)
    assert result['verdict'] != 'verified'
    assert any(c.get('reason') == 'MISSING_PUBLISHED_SOURCE' for c in result['checks'])


@pytest.mark.parametrize('reference', ['% PYTHON-SOURCE:', '% PYTHON-SOURCE : value.py', '%PYTHON-SOURCE: value.py'])
def test_malformed_python_source_is_not_silently_ignored(tmp_path, reference):
    result = check(tmp_path, reference + '\n' + verify('assert 1 == 1'))
    assert result['verdict'] == 'fail'
    assert any(c.get('reason') == 'MALFORMED_PYTHON_SOURCE' for c in result['checks'])


def test_explicit_python_source_can_wrap_an_identical_listing(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, 'ROOT', tmp_path)
    (tmp_path / 'value.py').write_text('value = 2\n')
    source = ('% PYTHON-SOURCE: value.py\n\\begin{codereference}{Example}\n'
              '\\begin{python}\nvalue = 2\n\\end{python}\n\\end{codereference}\n'
              + verify('value = 2\nassert value == 2'))
    assert check(tmp_path, source)['verdict'] == 'verified'


def test_referenced_unprinted_python_is_also_bound_to_executed_program(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, 'ROOT', tmp_path)
    (tmp_path / 'value.py').write_text('value = 2\n')
    assert check(tmp_path, '% PYTHON-SOURCE: value.py\n' + verify('value = 2\nassert value == 2'))['verdict'] == 'verified'
    result = check(tmp_path, '% PYTHON-SOURCE: value.py\n' + verify('assert 1 == 1'))
    assert result['verdict'] == 'manual_review'
    assert any(c.get('type') == 'python_source_execution' and c.get('state') == 'PENDING' for c in result['checks'])


@pytest.mark.parametrize('present', [False, True])
def test_missing_or_empty_chapter_never_reports_success(tmp_path, monkeypatch, capsys, present):
    monkeypatch.setattr(gate, 'ROOT', tmp_path)
    if present:
        (tmp_path / 'chapitres/TNSI-EMPTY/cours').mkdir(parents=True)
    assert gate.main('TNSI-EMPTY', True, check=True) > 0
    assert 'aucun objet' in capsys.readouterr().out.lower()


@pytest.mark.parametrize('mutation', ['added', 'removed'])
def test_changed_chapter_object_set_never_reports_success(tmp_path, monkeypatch, capsys, mutation):
    monkeypatch.setattr(gate, 'ROOT', tmp_path)
    chapter = tmp_path / 'chapitres/TNSI-SET'
    first = chapter / 'exercices/one.tex'
    first.parent.mkdir(parents=True)
    first.write_text(verify('assert 1 == 1'))
    second = chapter / 'remediation/two.tex'
    second.parent.mkdir()
    if mutation == 'removed':
        second.write_text(verify('assert 2 == 2'))
    original = gate.check_object
    def mutate_after_first(tex, no_ruff):
        result = original(tex, no_ruff)
        if tex == first:
            if mutation == 'added':
                (first.parent / 'unseen.tex').write_text(verify('assert False'))
            else:
                second.unlink()
        return result
    monkeypatch.setattr(gate, 'check_object', mutate_after_first)
    assert gate.main('TNSI-SET', True, check=True) > 0
    assert 'périmètre' in capsys.readouterr().out


@pytest.mark.parametrize('directory', ['banque_ecrite', 'banque_pratique', 'amenagee'])
def test_canonical_bank_and_adapted_oracles_cannot_be_silently_excluded(tmp_path, monkeypatch, directory):
    monkeypatch.setattr(gate, 'ROOT', tmp_path)
    chapter = tmp_path / 'chapitres/TNSI-PERIMETRE'
    baseline = chapter / 'cours/read.tex'
    baseline.parent.mkdir(parents=True)
    baseline.write_text(verify('assert 2 + 2 == 4'))
    false_oracle = chapter / directory / 'wrong.tex'
    false_oracle.parent.mkdir()
    false_oracle.write_text(verify('assert 2 + 2 == 5'))
    assert gate.main(chapter.name, True, check=True) > 0
    false_oracle.write_text(verify('assert 2 + 2 == 4'))
    assert gate.main(chapter.name, True, check=True) == 0
