"""Execute the small published interpreter; no historical claim is certified."""
from pathlib import Path

import pytest

from NSI.scripts import verify_python as gate

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/banque_ecrite/TNSI-ECRIT-S6-EX3.tex'


def interpreter():
    # The actual printed function is the program exercised. The separate
    # canonical gate below also requires its identical explicit .py source.
    return gate.PYENV.findall(SOURCE.read_text())[1]


def test_history_bank_code_is_executed_and_bound_to_published_sources():
    result = gate.check_object(SOURCE)
    assert result['verdict'] == 'verified'
    assert result['certifies_documentary_claims'] is False
    bindings = [c for c in result['checks'] if c['type'] == 'printed_source_alignment']
    assert len(bindings) == 4
    assert all(c['pass'] for c in bindings)


@pytest.mark.parametrize('probe', [
    'assert executer({}) == []',
    'assert executer({8: "AFFICHER"}) == [0]',
    'assert executer({20: "AFFICHER", 5: "CHARGER -4", 11: "AJOUTER -3"}) == [-7]',
    'm = {9: "AFFICHER", 2: "CHARGER 6"}\nsaved = m.copy()\nassert executer(m) == [6]\nassert m == saved',
    'assert executer({0: "CHARGER 10", 1: "AFFICHER"}) == [10]\nassert executer({0: "AFFICHER"}) == [0]',
])
def test_published_interpreter_boundaries(probe):
    assert gate.protocol.checked_assertions(interpreter() + '\n' + probe, gate.run_sandbox)['pass']


@pytest.mark.parametrize('instruction', ['INCONNU', 'CHARGER', 'CHARGERX 1', 'AFFICHER 1', 'AJOUTER texte'])
def test_published_interpreter_rejects_malformed_instructions(instruction):
    probe = (f'failed = False\ntry:\n    executer({{0: {instruction!r}}})\n'
             'except ValueError:\n    failed = True\nassert failed')
    assert gate.protocol.checked_assertions(interpreter() + '\n' + probe, gate.run_sandbox)['pass']


@pytest.mark.parametrize('also_change_printed_and_verify', [False, True])
def test_changed_addition_cannot_keep_an_execution_credit(tmp_path, monkeypatch, also_change_printed_and_verify):
    manual = tmp_path / 'NSI'
    chapter = manual / 'chapitres/TNSI-HISTOIRE-INFORMATIQUE'
    (chapter / 'banque_ecrite').mkdir(parents=True)
    (chapter / 'code').mkdir()
    copied = chapter / 'banque_ecrite' / SOURCE.name
    text = SOURCE.read_text()
    if also_change_printed_and_verify:
        text = text.replace('accumulateur += int', 'accumulateur -= int')
    copied.write_text(text)
    for source in (SOURCE.parent.parent / 'code').glob('tnsi_hist_s6_ex3_*.py'):
        body = source.read_text().replace('accumulateur += int', 'accumulateur -= int')
        (chapter / 'code' / source.name).write_text(body)
    monkeypatch.setattr(gate, 'ROOT', manual)
    result = gate.check_object(copied)
    assert result['verdict'] == 'fail'
    if also_change_printed_and_verify:
        # Every representation contains the same bad operator; the actual
        # expected results, independently calculated, still reject it.
        assert all(c['pass'] for c in result['checks'] if c['type'] == 'printed_source_alignment')
        assert any(c['type'] == 'verify' and not c['pass'] for c in result['checks'])
    else:
        assert any(c['type'] == 'printed_source_alignment' and not c['pass'] for c in result['checks'])
