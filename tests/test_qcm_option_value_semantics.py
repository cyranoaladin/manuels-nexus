"""The exact scalar reader must not erase units, percentages or conditions."""
from fractions import Fraction
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import qcm_independent_solver as S


@pytest.mark.parametrize('option', [
    r'$1/8\%$', r'$\frac{1}{8}\%$', '$12$ euros',
    r'$12\text{euros}$', r'$2\text{ et non 3}$',
    r'$2\text{ sauf si x=0}$', '$1$/$8$',
])
def test_semantic_qualifiers_are_not_erased_to_create_a_scalar(option):
    assert S.option_value(option) is None


@pytest.mark.parametrize('option', [r'$1/8\%$', r'$1/8\text{ si X=1}$'])
def test_qualified_option_cannot_become_the_proven_eight_face_key(option):
    inp = S.sanitize({'id': 'FIXTURE-QUALIFIED-OPTION',
        'enonce': 'On lance un dé équilibré à 8 faces numérotées de 1 à 8. '
                  'X désigne le résultat. Que vaut P(X=8) ?',
        'options': {'A': option, 'B': '$1/6$'}})
    result = S._uniform_outcome_probability(inp)
    assert result is None or result.status == 'NOT_MACHINE_RESOLVABLE'


@pytest.mark.parametrize('option, expected', [
    ('$1/8$', Fraction(1, 8)),
    (r'$\frac{1}{8}$', Fraction(1, 8)),
    (' 2 ', Fraction(2)),
    ('$0{,}125$', Fraction(1, 8)),
    ('$-2^2$', Fraction(-4)),
    (r'$1\,000$', Fraction(1000)),
])
def test_bare_exact_scalar_options_remain_supported(option, expected):
    assert S.option_value(option) == expected
