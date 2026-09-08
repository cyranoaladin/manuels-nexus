"""Closed symbolic grammar: mathematical objects, never evaluated Python text.

All statements here are controlled fixtures. Memory probes only append to a
list; no real QCM, published program, file operation or network call is run.
"""
import builtins
from fractions import Fraction
from pathlib import Path
import sys

import pytest
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import qcm_independent_solver as S


def extrema_input(expression):
    return S.SolverInput('FIXTURE-PARSER', f'Quels sont les extrema locaux de $f(x)={expression}$ ?',
                         {'A':'minimum local en $x=0$', 'B':'maximum local en $x=0$'})


@pytest.mark.parametrize('consumer', ['extrema','latex','gram'])
def test_expression_text_cannot_invoke_a_python_function(monkeypatch, consumer):
    calls=[]
    def hook():
        calls.append('memory-only')
        return sp.Symbol('x',real=True)**2
    monkeypatch.setattr(builtins,'NEXUS_READONLY_PROBE',hook,raising=False)
    module_name='+'.join(f'chr({ord(c)})' for c in 'builtins')
    payload=f'__import__({module_name}).NEXUS_READONLY_PROBE()'
    if consumer=='extrema':
        result=S._polynomial_local_extrema(extrema_input(payload))
    elif consumer=='latex':
        result=S.latex_to_sympy(payload)
    else:
        result=S._gram_combination(payload,['u'])
    assert calls==[], 'the expression invoked a Python function before rejection'
    assert result is None or getattr(result,'status',None)=='NOT_MACHINE_RESOLVABLE'


@pytest.mark.parametrize('payload', [
    'x.__class__', '__import__(str())', 'print(1)', 'Symbol(1)',
    'sin(x)', 'sum(x)', 'x[0]', '[x]', 'x if 1 else 0',
    'lambda:x', 'True', 'x//2', 'x%2', '(x,2)', 'sqrt(x,2)',
    'unknown(x)', 'x.__class__.__base__.__subclasses__()',
])
def test_unsupported_python_or_symbolic_syntax_is_refused(payload):
    assert S.latex_to_sympy(payload) is None


@pytest.mark.parametrize('source,expected', [
    ('2x(x-1)', lambda x:2*x*(x-1)),
    ('-x^2', lambda x:-x**2),
    ('(-x)^2', lambda x:x**2),
    ('2^{-3}',lambda x:sp.Rational(1,8)),
    (r'\frac{x^2-1}{x-1}',lambda x:(x**2-1)/(x-1)),
    ('3{,}14x',lambda x:sp.Rational(157,50)*x),
    (r'\mathrm{e}^{2x}',lambda x:sp.exp(2*x)),
    (r'\sqrt{12}/2',lambda x:sp.sqrt(3)),
    (r'\pi/4',lambda x:sp.pi/4),
])
def test_supported_math_stays_exact(source, expected):
    x=sp.Symbol('x',real=True)
    actual=S.latex_to_sympy(source)
    assert actual is not None
    assert not actual.atoms(sp.Float)
    assert sp.simplify(actual-expected(x))==0


def test_declared_vector_combination_uses_only_its_symbols():
    assert S._gram_combination(r'2\vec{u}-\frac{3}{2}\vec{v}', ['u','v']) == [sp.Integer(2),sp.Rational(-3,2)]


def test_valid_polynomial_extremum_fixture_is_resolved():
    result=S._polynomial_local_extrema(extrema_input('x^2'))
    assert result is not None and result.status=='MACHINE_RESOLVED'
    assert result.unique_answer=='A'


@pytest.mark.parametrize('source,expected', [
    ('-2^2',sp.Integer(-4)), ('(-2)^2',sp.Integer(4)),
    ('2^3^2',sp.Integer(512)), ('2^{-3}',sp.Rational(1,8)),
    ('sqrt(sqrt(16))',sp.Integer(2)),
])
def test_power_precedence_and_fixed_sqrt_constructor(source,expected):
    assert S.latex_to_sympy(source)==expected


@pytest.mark.parametrize('source', [
    '1/0', 'sqrt()', '2 3', 'x+', 'x**', '2^1000',
    '(' * 65 + 'x' + ')' * 65, '9' * 25, 'x' * 4097,
])
def test_invalid_or_excessive_expressions_are_refused(source):
    assert S.latex_to_sympy(source) is None


def test_symbol_followed_by_parentheses_is_multiplication_not_python_call():
    x=sp.Symbol('x',real=True)
    assert S.latex_to_sympy('x(2)')==2*x


@pytest.mark.parametrize('expression',['1/x',r'\mathrm{e}^x'])
def test_polynomial_family_rejects_nonpolynomial_expressions(expression):
    assert S._polynomial_local_extrema(extrema_input(expression)) is None


def test_no_dynamic_python_expression_evaluator_remains():
    import ast
    tree=ast.parse((ROOT/'scripts/qcm_independent_solver.py').read_text())
    forbidden={'eval','exec','compile','parse_expr','sympify'}
    called={node.func.id for node in ast.walk(tree)
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name)}
    called|={node.func.attr for node in ast.walk(tree)
             if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute)
             and not (isinstance(node.func.value,ast.Name) and node.func.value.id=='re'
                      and node.func.attr=='compile')}
    assert called.isdisjoint(forbidden)
