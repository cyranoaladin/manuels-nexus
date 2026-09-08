"""A singleton event uses the declared support and its membership, never six by default."""
from fractions import Fraction
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import qcm_independent_solver as S


def make_input(statement):
    return S.sanitize({'id': 'FIXTURE-DIE-PROBABILITY', 'enonce': statement,
                      'options': {'A': '$1/8$', 'B': '$1/6$', 'C': '$0$', 'D': '$1$'}})


@pytest.mark.parametrize('faces,start,stop,event,expected', [
    (8, 1, 8, 8, Fraction(1, 8)),
    (8, 1, 8, 9, Fraction(0)),
    (8, -3, 4, -3, Fraction(1, 8)),
    (8, -3, 4, -4, Fraction(0)),
    (6, 0, 5, 0, Fraction(1, 6)),
    (1, 7, 7, 7, Fraction(1)),
])
def test_singleton_probability_uses_exact_support_membership(faces, start, stop, event, expected):
    statement = (f'On lance un dé équilibré à {faces} faces numérotées de {start} à {stop}. '
                 f'$X$ désigne le résultat. Que vaut $P(X={event})$ ?')
    result = S._uniform_outcome_probability(make_input(statement))
    assert result is not None and result.status == 'MACHINE_RESOLVED'
    assert result.computed_value == str(expected)
    assert result.true_option_count == 1
    assert S.option_value(make_input(statement).options[result.unique_answer]) == expected


@pytest.mark.parametrize('statement', [
    'On lance un dé équilibré. Que vaut P(X=1) ?',
    'On lance un dé équilibré à 8 faces. X désigne le résultat. Que vaut P(X=1) ?',
    'On lance un dé équilibré à 4 faces numérotées de 1 à 8. X désigne le résultat. Que vaut P(X=1) ?',
    'On lance un dé équilibré à 8 faces numérotées de 1 à 8. Que vaut P(X=8) ?',
    'On lance un dé équilibré à 8 faces numérotées de 1 à 8. X désigne le carré du résultat. Que vaut P(X=4) ?',
    'On lance un dé équilibré à 8 faces numérotées de 1 à 8. X désigne le résultat. Sachant X>4, que vaut P(X=8) ?',
])
def test_missing_or_different_random_variable_model_is_not_guessed(statement):
    result = S._uniform_outcome_probability(make_input(statement))
    assert result is not None and result.status == 'NOT_MACHINE_RESOLVABLE'
    assert result.reason
    assert result.unique_answer is None
