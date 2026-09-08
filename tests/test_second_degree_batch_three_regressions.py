"""Lot B3 : modèle contraint, corrigés, et preuve C6 des évaluations."""
import json
import re
from pathlib import Path

import pytest
import sympy as sp

CHAPTER = Path(__file__).resolve().parents[1] / "Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE"


def read(relative):
    return (CHAPTER / relative).read_text()


def execute_read_oracles(text):
    # Sources mathématiques de ce lot lues avant cette exécution locale.
    namespace = {}
    blocks = re.findall(r"% BEGIN-VERIFY\n(.*?)% END-VERIFY", text, re.S)
    assert blocks
    for block in blocks:
        exec("\n".join(re.sub(r"^%\s?", "", line) for line in block.splitlines()), namespace)
    return namespace


def test_correction_038_reported_double_root_is_a_root_of_its_own_polynomial():
    text = read("corriges/1SPE-SECDEG-CO-038.tex")
    ns = execute_read_oracles(text)
    printed = int(re.search(r"Racine double : \$x_0 = (-?\d+)\$", text)[1])
    assert ns['x0_m2'] == printed == -2
    assert ns['f_m2'].subs(ns['x'], ns['x0_m2']) == 0


@pytest.mark.parametrize("kind", ['exercices', 'corriges'])
def test_supplement_oracle_keeps_the_wall_length_constraint(kind):
    prefix = 'EX' if kind == 'exercices' else 'CO'
    text = read(f"{kind}/1SPE-SECDEG-{prefix}-042.tex")
    ns = execute_read_oracles(text)
    assert 'A_max_L' in ns
    L = ns['L']
    assert sp.expand(ns['A_max_L']-(450+15*L)) == 0
    assert ns['L_min'] == 10
    assert ns['A_max_L'].subs(L, 40*sp.sqrt(3)-60) < 600


@pytest.mark.parametrize(('version', 'length', 'bound'), [('A', 80, 15), ('B', 100, 20)])
@pytest.mark.parametrize('suffix', ['', '-corrige'])
def test_evaluation_c6_is_quadratic_optimization_with_a_real_boundary(version, length, bound, suffix):
    text = read(f"evaluations/1SPE-SECDEG-EV-{version}{suffix}.tex")
    ns = execute_read_oracles(text)
    assert 'A_enclos' in ns, 'Le volume cubique ne prouve pas C6'
    x = ns['x']
    expected_area = x*(length-2*x)
    assert sp.expand(ns['A_enclos']-expected_area) == 0
    assert sp.degree(ns['A_enclos'], x) == 2
    assert ns['x_opt'] == length//4
    assert ns['x_limite'] == bound < ns['x_opt']
    assert ns['aire_limitee'] == expected_area.subs(x, bound)
    exercise4 = text.split(r"\section*{Exercice 4", 1)[1]
    assert "(4 points)" in exercise4
    assert "clôture" in exercise4 and "volume" not in exercise4
    assert str(length) in exercise4 and str(bound) in exercise4
    if suffix == '':
        metadata = json.loads(text.splitlines()[0].split('% META: ', 1)[1])
        assert metadata['bareme_total'] == 20


@pytest.mark.parametrize('relative', [
    'corriges/1SPE-SECDEG-CO-028.tex', 'corriges/1SPE-SECDEG-CO-037.tex',
    'corriges/1SPE-SECDEG-CO-038.tex', 'corriges/1SPE-SECDEG-CO-042.tex',
    'evaluations/1SPE-SECDEG-EV-A-corrige.tex', 'evaluations/1SPE-SECDEG-EV-B-corrige.tex',
])
def test_remaining_canonical_procedures_use_completion_of_square(relative):
    text = read(relative)
    assert 'complét' in text.lower(), relative
    assert r"\alpha = -\frac{b}{2a}" not in text
    assert r"\alpha = -b/(2a)" not in text


def test_article_profitability_is_an_integer_set():
    statement = read('exercices/1SPE-SECDEG-EX-028.tex')
    correction = read('corriges/1SPE-SECDEG-CO-028.tex')
    assert 'entier' in statement and 'entiers' in correction
    assert '$11$' in correction and '$29$' in correction
    profits = {n: -2*n*n+80*n-600 for n in range(41)}
    assert [n for n, p in profits.items() if p > 0] == list(range(11, 30))
    assert max(profits, key=profits.get) == 20


def test_wall_variant_explicitly_lifts_the_previous_extra_constraint():
    statement = read('exercices/1SPE-SECDEG-EX-037.tex')
    variant = statement.split(r'\textbf{Question ouverte.}', 1)[1]
    assert 'contrainte' in variant and 'levée' in variant
    assert 'longueur maximale réalisable' not in variant
    correction = read('corriges/1SPE-SECDEG-CO-037.tex')
    assert r'$0<x<20$' in correction
    x = sp.symbols('x')
    area = x*(10-x/2)
    assert sp.expand(area-(-(x-10)**2/2+50)) == 0
    assert area.subs(x, 8) == 48 < area.subs(x, 10) == 50


def test_without_wall_comparison_proves_the_admissible_maximum():
    text = read('corriges/1SPE-SECDEG-CO-042.tex')
    comparison = text.split(r"\textbf{3. Comparaison sans mur.}", 1)[1].split(r"\textbf{Apport du mur :}", 1)[0]
    assert '$0<x<30$' in comparison
    assert "A'(x) = x(30-x) = -(x-15)^2+225" in comparison
    assert 'admissible' in comparison
    ns = execute_read_oracles(text)
    x = ns['x']
    assert sp.expand(ns['A_sm']-(-(x-15)**2+225)) == 0
    assert 0 < 15 < 30
