"""Le TD économique doit aligner unités, points critiques et treize réponses."""
from pathlib import Path
import re
import pytest
import sympy as s
from tests.test_prodscal_remaining_scientific_regressions import _run_fixture

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/cours/07_td_contextualise.tex'


def text():
    return SOURCE.read_text()


def correction():
    match=re.search(r'\\ifnxVersionProfesseur\s*\\begin\{corrige\}\{1SPE-DERGLOBAL-TD-CONTEXTUALISE\}(.*?)\\end\{corrige\}\s*\\fi',text(),re.S)
    assert match, 'Le TD courant a besoin de son corrigé professeur lié à son propre ID.'
    return match.group(1)


def test_profit_units_count_individual_pens_before_converting_to_hundreds_of_euros():
    visible='\n'.join(line for line in text().splitlines() if not line.startswith('%'))
    assert 'euros par stylo' in visible
    assert '$100x$ stylos' in visible
    assert 'euros par cent stylos' not in visible
    assert r'100x(45-6x)' in correction()


def test_critical_point_is_derived_without_the_false_admitted_root():
    assert 'On admet que $x = 5$' not in text()
    assert r'1-\sqrt6' in correction() and r'1+\sqrt6' in correction()
    x=s.symbols('x')
    polynomial=-x**3+3*x**2+15*x-5
    assert s.diff(polynomial,x).subs(x,5) == -30
    assert s.simplify(s.diff(polynomial,x).subs(x,1+s.sqrt(6))) == 0


def test_exact_optimum_and_euro_rounding_have_the_right_scale():
    answers=correction()
    assert r'12+12\sqrt6' in answers
    assert r'4\,139' in answers
    value=100*(12+12*s.sqrt(6))
    assert s.Rational(8277,2) < value < s.Rational(8279,2)


def test_economic_boundary_is_a_polynomial_extension_not_a_required_limit():
    assert r'\lim_{x \to 0^+}' not in text()
    assert 'polynôme' in correction() and '$P(0)=-5$' in correction()
    assert 'non admissible' in correction()


def test_hundred_pen_batches_are_an_explicit_extra_constraint():
    assert 'lots de $100$ stylos' in text()
    assert r'$x\in\{1,2,3,4,5,6\}$' in correction()
    assert '$P(3)=40$' in correction() and '$P(4)=39$' in correction()


def test_every_td_question_has_one_numbered_teacher_answer():
    assert re.findall(r'\\textbf\{Question (\d+)\.\}',correction()) == [str(n) for n in range(1,14)]


@pytest.mark.parametrize(('valid','invalid'),[
    ('revenue_euros = 100*x*price','revenue_euros = x*price'),
    ('xopt = 1+sqrt(6)','xopt = 5'),
    ('rounded_profit_euros = 4139','rounded_profit_euros = 41'),
])
def test_td_oracles_reject_units_critical_point_and_rounding_mutations(tmp_path,valid,invalid):
    original=text()
    assert _run_fixture(tmp_path,'cours/07_td_contextualise.tex',original).returncode==0
    assert valid in original
    assert _run_fixture(tmp_path,'cours/07_td_contextualise.tex',original.replace(valid,invalid,1)).returncode==1
