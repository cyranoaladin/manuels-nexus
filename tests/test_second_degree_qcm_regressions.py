"""Régressions du lot QCM ; les diagnostics sont aussi relus sémantiquement."""
import json
import re
from pathlib import Path

import pytest
import sympy as sp

from scripts.qcm_independent_solver import latex_to_sympy

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/qcm/1SPE-SECDEG-QCM.json'


def questions():
    return {q['id']: q for q in json.loads(SOURCE.read_text())['questions']}


def diagnostic(qid, option):
    return questions()[qid]['diagnostics'][option]['erreur']


def statement_polynomial(qid, name='f', symbol='x'):
    statement = questions()[qid]['enonce']
    expression = re.search(r'\$'+name+r'\('+symbol+r'\)\s*=\s*([^$]+)\$', statement)[1]
    return latex_to_sympy(expression, symbol)


def test_capacity_bindings_describe_the_tasks_and_retirement_keeps_identity():
    qs = questions()
    assert qs['Q11']['capacite'] == 'C8'
    assert qs['Q12']['capacite'] == 'C5'
    assert qs['Q15']['capacite'] == 'C3'
    assert 'Q16' not in qs  # Image d'un volume cubique : prérequis R3, aucune optimisation C6.
    assert list(qs) == [f'Q{n}' for n in range(1, 21) if n != 16]
    for qid in ('Q11', 'Q12', 'Q15'):
        assert all(d['renvoi'].startswith(qs[qid]['capacite']) for d in qs[qid]['diagnostics'].values())


@pytest.mark.parametrize('qid', ['Q2', 'Q4', 'Q5', 'Q12', 'Q17', 'Q18'])
def test_simple_square_completion_is_the_explained_procedure(qid):
    text = json.dumps(questions()[qid], ensure_ascii=False)
    assert '-b/(2a)' not in text and '-b/(4a)' not in text
    assert ')^2' in ' '.join(d['erreur'] for d in questions()[qid]['diagnostics'].values())


def test_q4_c_diagnostic_checks_the_actual_wrong_abscissa():
    wrong = int(re.search(r'=\s*(-?\d+)', questions()['Q4']['options']['C'])[1])
    f = statement_polynomial('Q4'); x = sp.Symbol('x', real=True)
    assert wrong == -4
    value = f.subs(x, wrong)
    assert f'f({wrong})={value}' in diagnostic('Q4', 'C')
    assert value < f.subs(x, 2)


def test_q5_b_does_not_name_an_unrelated_ordinate():
    d = diagnostic('Q5', 'B')
    assert 'ordonnée' not in d and 'f(3)=-4' in d and 'f(5)=0' in d
    f = statement_polynomial('Q5'); x = sp.Symbol('x', real=True)
    assert f.subs(x, 3) == -4 < f.subs(x, 5) == 0


def test_q6_does_not_give_a_parabola_a_constant_slope():
    assert 'coefficient directeur' not in questions()['Q6']['options']['B']


def test_q9_diagnostics_preserve_the_one_correct_root():
    d = diagnostic('Q9', 'A')
    assert '$-1$ est bien une racine' in d
    assert 'mauvais signes aux deux racines' not in d
    f = latex_to_sympy('x^2-3x-4'); x = sp.Symbol('x', real=True)
    assert f.subs(x, -1) == 0 and f.subs(x, -4) == 24
    d = diagnostic('Q9', 'D')
    assert 'f(1)=-6' in d and 'f(4)=0' in d
    assert f.subs(x, 1) == -6 and f.subs(x, 4) == 0


def test_q12_has_all_reals_as_strict_positivity_solutions():
    q = questions()['Q12']
    assert 'Résoudre' in q['enonce'] and 'f(x)>0' in q['enonce']
    f = statement_polynomial('Q12'); x = sp.Symbol('x', real=True)
    assert sp.expand(f-((x+1)**2+4)) == 0
    result = sp.solve_univariate_inequality(f>0, x, relational=False)
    assert result == sp.S.Reals
    assert q['options'][q['correcte']] == r'$\mathbb{R}$'
    assert 'f(-1)=4' in diagnostic('Q12', 'D')


def test_q13_a_is_a_truncation_without_claim_of_rounding():
    d = diagnostic('Q13', 'A')
    assert 'arrond' not in d and '$]0' in d


def test_q14_c_addresses_both_the_wrong_root_and_outside_interval():
    d = diagnostic('Q14', 'C')
    assert '$-1$' in d and 'extérieur' in d and '$[1' in d


def test_q18_seconds_are_an_instant_and_optimum_is_admissible():
    q = questions()['Q18']
    assert '$0\\leq t\\leq4$' in q['enonce']
    assert 'retour au sol' in diagnostic('Q18', 'A')
    assert 'portee' not in diagnostic('Q18', 'A') and 'portée' not in diagnostic('Q18', 'A')
    h = statement_polynomial('Q18', 'h', 't'); t = sp.Symbol('t', real=True)
    assert sp.expand(h-(-5*(t-2)**2+20)) == 0
    assert 0 <= 2 <= 4 and h.subs(t, 4) == 0


def test_q19_requires_sum_and_product_from_coefficients_without_given_roots():
    q = questions()['Q19']; f = statement_polynomial('Q19'); x = sp.Symbol('x', real=True)
    assert 'Sans résoudre' in q['enonce']
    a, b, c = sp.Poly(f, x).all_coeffs()
    total, product = -b/a, c/a
    assert b*b-4*a*c > 0
    truth = {letter: tuple(map(int, re.findall(r'[SP]=(-?\d+)', value))) == (total, product)
             for letter, value in q['options'].items()}
    assert [letter for letter, valid in truth.items() if valid] == [q['correcte']]
    assert 'signes des racines ont été inversés' not in diagnostic('Q19', 'D')
    assert 'racine $4$ a été changé' not in diagnostic('Q19', 'A')


def test_q20_does_not_generalize_sign_change_to_double_roots():
    d = diagnostic('Q20', 'A')
    assert 'Un trinôme change de signe' not in d
    f = statement_polynomial('Q20'); x = sp.Symbol('x', real=True)
    assert f.subs(x, 2) == -10 < 0
    # Cas adversarial : la généralisation supprimée échoue pour une racine double.
    assert sp.solve_univariate_inequality((x-1)**2 < 0, x, relational=False) == sp.EmptySet


def assert_q2_distractor_identity(text):
    identity = re.search(r'\$([^$]+)\$', text)[1]
    left, right = identity.split('=')
    assert sp.expand(latex_to_sympy(left)-latex_to_sympy(right)) == 0


def test_q2_explains_the_actual_distractor_polynomial_and_rejects_mutation():
    text = diagnostic('Q2', 'A')
    assert_q2_distractor_identity(text)
    mutated = text.replace('-16x', '-15x')
    assert mutated != text
    with pytest.raises(AssertionError):
        assert_q2_distractor_identity(mutated)


def test_printed_editorial_corrections_and_mathematical_remediation_labels():
    qs = questions()
    assert 'développe' in qs['Q3']['enonce']
    assert 'représentant' in qs['Q4']['enonce']
    assert 'considère' in qs['Q7']['enonce']
    assert 'factorisée' in qs['Q10']['enonce']
    assert 'cherche à' in qs['Q17']['enonce']
    assert all('égale à' in qs['Q8']['options'][letter] for letter in ('B', 'D'))
    for d in qs['Q12']['diagnostics'].values():
        assert r'$\Delta<0$' in d['renvoi']
    for q in qs.values():
        for d in q['diagnostics'].values():
            assert "L'élève a" not in d['erreur'] and "L'élève n'a" not in d['erreur']
