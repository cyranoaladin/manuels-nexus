"""The Fraction API must return exact rationals or explicitly abstain."""
from fractions import Fraction
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from latex_arith import evaluate, UnsupportedExpression


@pytest.mark.parametrize('source,expected',[
    ('-2^2',Fraction(-4)), ('(-2)^2',Fraction(4)),
    ('-2^{-2}',Fraction(-1,4)), ('(-2)^{-2}',Fraction(1,4)),
    (r'\frac{-2^2}{4}',Fraction(-1)),
    (r'-3\cdot2^2',Fraction(-12)), ('2^{3^2}',Fraction(512)),
    (r'\sqrt{\frac{9}{16}}',Fraction(3,4)),
    (r'\sqrt{0{,}25}',Fraction(1,2)),
    (r'\sqrt{0}',Fraction(0)), (r'\sqrt{25}',Fraction(5)),
    (r'\frac{1}{3}+0{,}1',Fraction(13,30)),
])
def test_exact_rational_values_and_power_precedence(source,expected):
    actual=evaluate(source)
    assert isinstance(actual,Fraction)
    assert actual==expected


@pytest.mark.parametrize('source',[r'\sqrt{2}',r'\sqrt{\frac{2}{3}}',r'\sqrt{0{,}2}'])
def test_irrational_square_roots_cannot_be_reported_as_exact_fractions(source):
    with pytest.raises(UnsupportedExpression,match='ration'):
        evaluate(source)


@pytest.mark.parametrize('source',[r'\sqrt{-1}',r'\frac{1}{0}','0^{-1}'])
def test_undefined_fraction_values_are_refused(source):
    with pytest.raises((UnsupportedExpression,ZeroDivisionError)):
        evaluate(source)
