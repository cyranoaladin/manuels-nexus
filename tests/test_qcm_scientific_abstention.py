"""Controlled scientific counterexamples; no real corpus is executed."""
import sys
from pathlib import Path
from fractions import Fraction
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import qcm_independent_solver as S
import pytest


def test_unreadable_numeric_option_is_not_proven_false():
    assert S._numeric_truths({'A':'$2$','B':'deux'},Fraction(2)) is None


def test_unreadable_symbolic_option_is_not_proven_false():
    x=S._sympy().Symbol('x',real=True)
    assert S._symbolic_truths({'A':'$2x$','B':'le double de x'},2*x) is None


def test_degenerate_minimum_cannot_be_omitted_from_all_extrema():
    inp=S.sanitize({'id':'FIXTURE-EXTREMA',
        'enonce':r'Quels sont les extrema locaux de $f(x)=x^4-\frac{2}{3}x^6$ ?',
        'options':{'A':'maximum local en $x=-1$ et maximum local en $x=1$',
                   'B':'maximum local en $x=-1$, minimum local en $x=0$ et maximum local en $x=1$'}})
    result=S._polynomial_local_extrema(inp)
    assert result is None or result.status=='NOT_MACHINE_RESOLVABLE' or result.unique_answer=='B'


def test_undecidable_root_reality_cannot_remove_other_real_extrema():
    inp = S.sanitize({'id': 'FIXTURE-UNDECIDED-ROOTS',
        'enonce': r'Quels sont les extrema locaux de $f(x)=x^5/5-x^3+x^2/2$ ?',
        'options': {'A': 'minimum local en $x=0$', 'B': 'aucun extremum'}})
    # f'=x(x^3-3x+1). The cubic has three distinct real roots in
    # (-2,-1), (0,1), (1,2), in addition to the root0 of f'.
    result = S._polynomial_local_extrema(inp)
    assert result is None or result.status == 'NOT_MACHINE_RESOLVABLE'


def test_initial_value_cannot_be_created_by_cancellation():
    inp=S.sanitize({'id':'FIXTURE-DOMAIN',
        'enonce':r'Soit $f(x)=x^3/x$. Quelle est sa valeur initiale ?',
        'options':{'A':'$0$','B':'$1$'}})
    result=S._symbolic_expression_question(inp)
    assert result is None or result.status=='NOT_MACHINE_RESOLVABLE'



def test_simplification_cannot_claim_equal_domains_after_cancellation():
    inp=S.sanitize({'id':'FIXTURE-SIMPLIFY-DOMAIN',
        'enonce':r'Simplifier $x^3/x$.',
        'options':{'A':'$x^2$','B':'$x$'}})
    result=S._symbolic_expression_question(inp)
    assert result is None or result.status=='NOT_MACHINE_RESOLVABLE'


def test_fraction_zero_power_zero_needs_an_explicit_convention():
    from latex_arith import evaluate, UnsupportedExpression
    with pytest.raises(UnsupportedExpression):
        evaluate('0^0')


def test_symbolic_zero_power_zero_needs_an_explicit_convention():
    assert S.latex_to_sympy('0^0') is None


def test_option_domain_cannot_be_erased_by_cancellation():
    x = S._sympy().Symbol('x', real=True)
    assert S._symbolic_truths({'A': '$x^3/x$', 'B': '$x$'}, x**2) is None


def test_extrema_input_cannot_erase_a_hole_in_its_domain():
    inp = S.sanitize({'id': 'FIXTURE-EXTREMA-DOMAIN',
        'enonce': r'Quels sont les extrema locaux de $f(x)=x^3/x$ ?',
        'options': {'A': 'minimum local en $x=0$', 'B': 'aucun extremum'}})
    result = S._polynomial_local_extrema(inp)
    assert result is None or result.status == 'NOT_MACHINE_RESOLVABLE'


def test_unit_shift_ratio_cannot_create_an_untracked_exclusion():
    inp = S.sanitize({'id': 'FIXTURE-SHIFT-DOMAIN',
        'enonce': r'Soit $f(x)=x$. Simplifier $f(x+1)/f(x)$.',
        'options': {'A': '$1+1/x$', 'B': '$1$'}})
    result = S._symbolic_expression_question(inp)
    assert result is None or result.status == 'NOT_MACHINE_RESOLVABLE'


def test_fully_readable_numeric_options_still_have_exact_truths():
    assert S._numeric_truths({'A':'$2$','B':'$3$'},Fraction(2))==({'A':True,'B':False},2)


def test_fully_readable_symbolic_options_still_have_exact_truths():
    x=S._sympy().Symbol('x',real=True)
    assert S._symbolic_truths({'A':'$2x$','B':'$3x$'},2*x)==({'A':True,'B':False},2)


def test_total_polynomial_initial_value_is_still_resolved():
    inp=S.sanitize({'id':'FIXTURE-TOTAL',
        'enonce':r'Soit $f(x)=x^3+2$. Quelle est sa valeur initiale ?',
        'options':{'A':'$2$','B':'$3$'}})
    result=S._symbolic_expression_question(inp)
    assert result is not None and result.status=='MACHINE_RESOLVED' and result.unique_answer=='A'


@pytest.mark.parametrize('expression', ['x^3/x', 'x^0', 'x^{-2}', r'\sqrt{x}', r'\sqrt{x^2}'])
def test_unsupported_domain_or_regularity_is_refused_before_simplification(expression):
    assert S.latex_to_sympy(expression, require_total=True) is None


@pytest.mark.parametrize('expression, expected', [
    ('1/(x^2+1)', lambda x: 1/(x*x+1)),
    ('0^2', lambda x: S._sympy().Integer(0)),
    ('2^0', lambda x: S._sympy().Integer(1)),
    (r'\sqrt{0}', lambda x: S._sympy().Integer(0)),
    (r'\sqrt{x^2+1}', lambda x: S._sympy().sqrt(x*x+1)),
    (r'\mathrm{e}^{2x}', lambda x: S._sympy().exp(2*x)),
])
def test_proved_total_operations_retain_their_exact_value(expression, expected):
    x = S._sympy().Symbol('x', real=True)
    actual = S.latex_to_sympy(expression, require_total=True)
    assert actual is not None
    assert S._sympy().simplify(actual - expected(x)) == 0


def test_exponential_unit_shift_ratio_still_resolves():
    inp = S.sanitize({'id': 'FIXTURE-TOTAL-SHIFT',
        'enonce': r'Soit $f(x)=\mathrm{e}^{2x}$. Simplifier $f(x+1)/f(x)$.',
        'options': {'A': r'$\mathrm{e}^{2}$', 'B': '$1$'}})
    result = S._symbolic_expression_question(inp)
    assert result is not None and result.status == 'MACHINE_RESOLVED'
    assert result.unique_answer == 'A'
