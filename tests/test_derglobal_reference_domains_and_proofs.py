"""Régressions des domaines et démonstrations publiés du cours de référence."""
from pathlib import Path
import re

import sympy as s

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/cours/10_C1_derivees_reference.tex'


def printed() -> str:
    return '\n'.join(line for line in SOURCE.read_text().splitlines() if not line.lstrip().startswith('%'))


def test_table_distinguishes_definition_and_differentiability_domains():
    text = printed()
    assert 'dérivables sur leur domaine de définition' not in text
    assert r'\textbf{Dérivabilité}' in text
    assert r'f(x) = \sqrt{x} & ]0\,;\,+\infty[' in text
    assert r'définie sur $[0\,;\,+\infty[$' in text


def test_root_at_zero_uses_difference_quotient_not_derivative_limit():
    match = re.search(r'\[ROOT-ZERO-PROOF\](.*?)\[/ROOT-ZERO-PROOF\]', SOURCE.read_text(), re.S)
    assert match, 'La preuve doit porter sur le taux entre 0 et h, pas sur f′(h).'
    proof = '\n'.join(line for line in match.group(1).splitlines() if not line.lstrip().startswith('%'))
    assert r'\frac{\sqrt{h}-\sqrt{0}}{h-0}' in proof
    assert r'\frac{1}{\sqrt{h}}' in proof and '$h>0$' in proof
    assert 'aucun réel' in proof
    h = s.symbols('h', positive=True)
    assert s.simplify((s.sqrt(h) - s.sqrt(0))/h - 1/s.sqrt(h)) == 0
    assert s.limit(s.sqrt(h)/h, h, 0, dir='+') == s.oo


def test_zero_power_does_not_evaluate_zero_times_undefined_inverse():
    text = printed()
    assert r'0 \cdot x^{-1} = 0' not in text
    assert 'fonction constante $1$' in text
    assert 'sans utiliser $0^0$' in text
    assert 'Le cas $n=1$' in text and 'Le cas $n=0$' in text


def test_inverse_proof_is_general_with_both_denominators_nonzero():
    text = printed()
    assert r'$a\neq0$' in text and r'$a+h\neq0$' in text
    assert r'\frac{\frac{1}{a+h}-\frac{1}{a}}{h}' in text
    assert r'-\frac{1}{a(a+h)}' in text
    assert r'-\frac{1}{a^2}' in text
    a,h = s.symbols('a h', nonzero=True)
    quotient = (1/(a+h)-1/a)/h
    assert s.cancel(quotient + 1/(a*(a+h))) == 0
    assert s.limit(quotient,h,0) == -1/a**2


def test_positive_power_argument_separates_zero_and_negative_exponents():
    text = printed()
    assert r'Pour $n\geqslant2$ et $a\neq0$' in text
    assert r'\frac{h^n-0}{h}=h^{n-1}' in text
    assert 'Pour $n=-m<0$' in text
    assert r'\frac{1}{x^m}' in text
    assert 'règle de dérivation de l’inverse' in text


def test_required_square_proof_is_printed_for_arbitrary_a():
    text = printed()
    assert r'\frac{(a+h)^2-a^2}{h}=2a+h' in text
    assert 'pour tout réel $a$' in text
