"""A fair die need not have six faces or the labels 1 through 6."""
from fractions import Fraction
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import qcm_independent_solver as S


def input_for(statement, expected=Fraction(9, 2)):
    values = [Fraction(7, 2), expected, Fraction(-99)]
    unique = list(dict.fromkeys(values))
    return S.sanitize({'id':'FIXTURE-DIE', 'enonce':statement,
                       'options':{chr(65+i):f'${value}$' for i,value in enumerate(unique)}})


@pytest.mark.parametrize('faces,start,stop', [(8,1,8), (6,0,5), (8,-3,4), (6,1,6)])
def test_uniform_expectation_uses_the_declared_face_labels(faces, start, stop):
    expected = Fraction(sum(range(start, stop + 1)), faces)
    inp = input_for(f"On lance un dé équilibré à {faces} faces numérotées de {start} à {stop}. Quelle est l'espérance $E(X)$ du résultat ?", expected)
    result = S._uniform_expectation(inp)
    assert result is not None and result.status == 'MACHINE_RESOLVED'
    assert result.computed_value == str(expected)
    assert result.true_option_count == 1
    assert S.option_value(inp.options[result.unique_answer]) == expected


@pytest.mark.parametrize('statement', [
    "On lance un dé équilibré. Quelle est l'espérance $E(X)$ du résultat ?",
    "On lance un dé équilibré à 8 faces. Quelle est l'espérance $E(X)$ du résultat ?",
    "On lance un dé équilibré à 4 faces numérotées de 1 à 6. Quelle est l'espérance $E(X)$ du résultat ?",
    "On lance un dé équilibré à 6 faces numérotées de 1 à 6. Quelle est l'espérance du carré du résultat ?",
    "On lance un dé équilibré à 6 faces numérotées de 1 à 6. Si le résultat est pair, on gagne 10 euros. Quelle est l'espérance du gain ?",
])
def test_unsupported_or_inconsistent_die_context_does_not_get_six_face_credit(statement):
    result = S._uniform_expectation(input_for(statement))
    assert result is not None and result.status == 'NOT_MACHINE_RESOLVABLE'
    assert result.unique_answer is None
    assert result.reason


def test_current_unspecified_die_is_left_for_source_specific_review():
    path = ROOT / 'Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/qcm/1SPE-VARALEA-QCM.json'
    question = next(q for q in json.loads(path.read_text())['questions'] if q['id']=='Q4')
    result = S._uniform_expectation(S.sanitize_canonical(question))
    assert result is not None and result.status == 'NOT_MACHINE_RESOLVABLE'
    assert result.unique_answer is None
