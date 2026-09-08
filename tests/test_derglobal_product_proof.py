"""La règle du produit doit être prouvée, y compris quand un facteur s'annule."""
from pathlib import Path
import re
import pytest
import sympy as s

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / 'Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL'
COURSE = CHAPTER / 'cours/11_C2_regles_derivation.tex'
METHOD = CHAPTER / 'methodes/1SPE-DERGLOBAL-ME-002.tex'


def printed(path):
    return '\n'.join(line for line in path.read_text().splitlines() if not line.lstrip().startswith('%'))


def parsed_integer_quadratic(expression: str):
    """Lecture fermée de a x² + b x + c, sans évaluateur d'expression."""
    match = re.fullmatch(r'([+-]?\d+)x\^2([+-]\d+)x([+-]\d+)', expression)
    if match is None:
        raise ValueError('Expected an integer quadratic in the printed grammar')
    a, b, c = map(int, match.groups())
    x = s.symbols('x')
    return a*x*x+b*x+c


@pytest.mark.parametrize('expression', ['6*x**2+2*x-6', '__import__("os")', '6x^2+2x-6;0'])
def test_polynomial_reader_refuses_everything_outside_integer_grammar(expression):
    with pytest.raises(ValueError):
        parsed_integer_quadratic(expression)


def test_product_rule_has_general_increment_proof_in_current_course():
    text = printed(COURSE)
    assert 'Démonstration de la règle du produit' in text
    assert r'\frac{u(a+h)v(a+h)-u(a)v(a)}{h}' in text
    assert r'\frac{u(a+h)-u(a)}{h}\,v(a+h)' in text
    assert r'u(a)\,\frac{v(a+h)-v(a)}{h}' in text
    assert r'$v(a+h)$ tend vers $v(a)$' in text
    # Independent algebra; this identity does not divide by either value.
    a,b,c,d,h = s.symbols('a b c d h')
    assert s.cancel((c*d-a*b)/h - ((c-a)*d/h+a*(d-b)/h)) == 0


def test_product_proof_handles_zero_factor_without_illicit_division():
    text = printed(COURSE)
    assert 'même si $u(a)=0$ ou $v(a)=0$' in text
    x=s.symbols('x')
    # Derivatives of x*x at 0 and (x+1)*x at 0 differ.
    assert s.diff(x*x,x).subs(x,0) == 0
    assert s.diff((x+1)*x,x).subs(x,0) == 1


def test_reciprocal_function_rule_and_nonzero_domain_are_explicit():
    text=printed(COURSE)
    assert r"\left(\frac{1}{v}\right)'=-\frac{v'}{v^2}" in text
    assert 'ne s’annule pas sur $I$' in text


def test_nonidentities_are_counterexamples_at_explicit_admissible_points():
    text=printed(COURSE)
    assert 'pas valable en général' in text
    assert text.count('en $x=1$') >= 2
    assert r'$x\neq0$' in text
    assert 'toute combinaison de fonctions' not in text


def test_method_states_hypotheses_before_operations():
    text=printed(METHOD)
    assert 'dérivables sur cet intervalle' in text
    assert r'$v(x)\neq0$' in text
    assert text.index('dérivables sur cet intervalle') < text.index('Somme :')
    assert r'$n\geqslant1$' in text
    assert 'fonction constante' in text and 'polynôme nul' in text


def test_oracle_does_not_call_two_fixed_polynomials_arbitrary_functions():
    text=COURSE.read_text()
    assert 'fonctions\n% # quelconques' not in text
    assert 'Identité algébrique générale du taux du produit' in text
    # Published polynomial derivative in M2 is independently recovered from its input.
    text=printed(METHOD)
    match=re.search(r"f'\(x\)=2x\^2-6\+4x\^2\+2x=([^.]*)\.\\\]",text)
    assert match
    x=s.symbols('x')
    assert s.expand(parsed_integer_quadratic(match.group(1))-s.diff((2*x+1)*(x*x-3),x)) == 0
