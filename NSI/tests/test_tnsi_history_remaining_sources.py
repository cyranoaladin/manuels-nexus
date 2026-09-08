"""Documentary prose needs review; only the stated barème is executable.

No test of dates, keywords or attribution pretends to validate history.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from NSI.scripts import verify_python as execution

ROOT = Path(__file__).resolve().parents[2]
CHAPTER = ROOT / 'NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE'
sys.path.insert(0, str(ROOT / 'scripts'))
import scientific_receipt_binding as binding


@pytest.mark.parametrize('relative', [
    'exercices/TNSI-HIST-EX-001.tex',
    'corriges/TNSI-HIST-CO-001.tex',
    'exercices/TNSI-HIST-EX-002.tex',
    'corriges/TNSI-HIST-CO-002.tex',
])
def test_documentary_exercise_pair_requires_review_and_invalidates_old_receipt(relative):
    source = CHAPTER / relative
    result = execution.check_object(source)
    assert result['verdict'] == 'manual_review'
    assert result['certifies_documentary_claims'] is False
    receipt = CHAPTER / 'validations' / (source.stem + '.execution.json')
    historical = json.loads(subprocess.check_output([
        'git', 'show',
        '6da7f7637e34a3f7f4aba91eb765ee92ce7fc1d9:' + receipt.relative_to(ROOT).as_posix(),
    ], cwd=ROOT, text=True))
    current = binding.bind(historical, CHAPTER, ROOT)
    assert not binding.usable(current)
    assert current['state'] == 'STALE'
    assert current['reason'] == 'SOURCE_DIGEST_CHANGED'


@pytest.mark.parametrize('name', ['TNSI-HIST-EVAL-A.tex', 'TNSI-HIST-EVAL-A-corrige.tex'])
def test_eval_a_only_checks_arithmetic_and_rejects_an_incorrect_component(tmp_path, name):
    source = CHAPTER / 'evaluations' / name
    before = execution.check_object(source)
    assert before['verdict'] == 'verified'
    assert before['certifies_documentary_claims'] is False
    program = execution.strip_percent(execution.VERIFY.findall(source.read_text())[0])
    lines = program.splitlines()
    i = next(i for i, line in enumerate(lines) if line.startswith('points_exercice_1 ='))
    lines.insert(i + 1, 'points_exercice_1 = (points_exercice_1[0] + 1,) + points_exercice_1[1:]')
    target = tmp_path / 'changed_bareme.tex'
    target.write_text('% BEGIN-VERIFY\n' + '\n'.join('% ' + line for line in lines) + '\n% END-VERIFY\n')
    after = execution.check_object(target)
    assert after['verdict'] == 'fail'
    assert after['certifies_documentary_claims'] is False
