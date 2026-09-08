"""Régressions B2 : phrases, métadonnées et calculs réellement publiés.

Ces contrôles ciblés ne certifient ni les figures ni la totalité du chapitre.
Les blocs exécutés ici ont été lus : uniquement du calcul SymPy local.
"""
import json
import re
import sys
from pathlib import Path

import sympy as sp
import pytest

CHAPTER = Path(__file__).resolve().parents[1] / "Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from qcm_independent_solver import latex_to_sympy


def source(relative):
    return (CHAPTER / relative).read_text()


def oracle_namespace(text):
    namespace = {}
    blocks = re.findall(r"% BEGIN-VERIFY\n(.*?)% END-VERIFY", text, re.S)
    assert blocks
    for block in blocks:
        exec("\n".join(re.sub(r"^%\s?", "", line) for line in block.splitlines()), namespace)
    return namespace


def test_box_auxiliary_polynomial_and_physical_domain_are_distinct():
    text = source("cours/07_td_fil_rouge.tex")
    metadata = json.loads(text.splitlines()[0].split("% META: ", 1)[1])
    assert metadata['capacites_codes'] == ['C1', 'C2']
    statement = text.split(r"\begin{exercice}{1SPE-SECDEG-TD-FIL-B}", 1)[1].split(r"\end{exercice}", 1)[0]
    assert r"\mathbb{R}" in statement
    assert "aire" in statement and "volume ?" not in statement
    assert "valeurs aux bornes" in text
    assert "toutes les capacites" not in text


def test_box_numerical_search_is_a_conjecture_with_premiere_derivatives():
    text = source("cours/07_td_fil_rouge.tex")
    assert "consecutives" not in text
    assert "conjecture" in text
    assert "dérivation en Terminale" not in text
    assert "programme de Terminale" not in text
    assert "Première" in text
    x = sp.symbols("x")
    volume = x*(30-2*x)*(20-2*x)
    stationary = (50-sp.sqrt(700))/6
    assert sp.simplify(sp.diff(volume, x).subs(x, stationary)) == 0
    assert 0 < stationary < 10


def test_broken_notin_control_sequence_is_absent():
    for relative in ("cours/07_td_fil_rouge.tex", "corriges/1SPE-SECDEG-CO-027.tex"):
        text = source(relative)
        assert "\notin" not in text  # newline + otin from a broken escape
        assert r"\notin" in text


def test_basket_trajectory_starts_above_ground_and_is_parabolic():
    text = source("cours/07_td_contextualise.tex")
    assert "depuis le sol" not in text
    assert "arc de cercle" not in text
    assert "arc de parabole" in text
    assert "il n'a pas encore atteint son maximum" not in text
    assert "maximum est atteint en $x=10$" in text


def test_basket_exact_height_roots_and_ground_range_match_oracles():
    text = source("cours/07_td_contextualise.tex")
    assert r"10-4\sqrt{5}" in text and r"10+4\sqrt{5}" in text
    assert r"1{,}06" in text and r"18{,}94" in text
    assert r"x_1 = 10 - 11{,}8" not in text
    assert "== 21.9 or" not in text
    namespace = oracle_namespace(text)
    x, h = namespace['x'], namespace['h']
    assert {sp.simplify(r) for r in sp.solve(h-3, x)} == {10-4*sp.sqrt(5), 10+4*sp.sqrt(5)}
    assert round(float(10+2*sp.sqrt(35)), 1) == 21.8


def test_basket_does_not_presuppose_a_second_intersection_or_change_gravity():
    text = source("cours/07_td_contextualise.tex")
    assert "(autre que $x = 0$)" not in text
    assert "tir plus «vertical»" not in text
    assert "deceleration verticale due a la gravite" not in text
    assert "coefficient linéaire" in text and "terme constant" in text
    x = sp.symbols("x", real=True)
    h, k = -x*x/20+x+2, -2*x*x/25+x+2
    assert sp.expand(h-k) == 3*x*x/100
    assert sp.solve(h-k, x) == [0]


def test_box_base_table_endpoint_is_evaluated_from_its_polynomial():
    text = source("corriges/1SPE-SECDEG-CO-027.tex")
    row = re.search(r"\$A\(x\)\$ & \$(\d+)\$ & \$\\searrow\$ & \$(\d+)\$", text)
    assert row
    x = sp.symbols("x")
    area = (16-2*x)*(10-2*x)
    assert tuple(map(int, row.groups())) == tuple(area.subs(x, v) for v in (0, 5))


def test_box_027_does_not_claim_an_optimization_it_does_not_perform():
    for relative in ('exercices/1SPE-SECDEG-EX-027.tex', 'corriges/1SPE-SECDEG-CO-027.tex'):
        text = source(relative)
        metadata = json.loads(text.splitlines()[0].split('% META: ', 1)[1])
        assert 'C6' not in metadata['capacites_codes']
        assert 'M6' not in metadata.get('methodes', [])
        assert '(C6)' not in text


def test_box_027_correction_gives_both_vertex_coordinates():
    text = source('corriges/1SPE-SECDEG-CO-027.tex')
    assert r'S\left(\frac{13}{2}\,;\,-9\right)' in text
    statement = source('exercices/1SPE-SECDEG-EX-027.tex')
    assert '2.06' not in statement
    x = sp.symbols('x')
    volume = x*(16-2*x)*(10-2*x)
    assert sp.expand(sp.diff(volume, x)-4*(x-2)*(3*x-20)) == 0


@pytest.mark.parametrize("relative", ("exercices/1SPE-SECDEG-EX-039.tex", "corriges/1SPE-SECDEG-CO-039.tex"))
def test_tariff_oracle_uses_the_actual_new_price_and_charges(relative):
    text = source(relative)
    namespace = oracle_namespace(text)
    assert "B2" in namespace, relative
    x = namespace['x']
    expected = x*(20-x/5)-(200+5*x)
    assert sp.expand(namespace['B2']-expected) == 0, relative
    assert sp.simplify(namespace['B2'].subs(x, sp.Rational(75, 2))) == sp.Rational(325, 4)


def test_tariff_profit_interval_preserves_profitable_rounded_boundary_values():
    text = source("corriges/1SPE-SECDEG-CO-039.tex")
    assert r"\left]28\,;\,72\right[" not in text
    assert r"]50-10\sqrt{5}\,;\,50+10\sqrt{5}[" in text
    assert "modèle continu" in source("exercices/1SPE-SECDEG-EX-039.tex")
    x = sp.symbols("x")
    profit = -x*x/10+10*x-200
    assert profit.subs(x, 28) == profit.subs(x, 72) == sp.Rational(8, 5)


def test_tariff_comparison_is_based_on_difference_not_each_separate_optimum():
    text = source("corriges/1SPE-SECDEG-CO-039.tex")
    assert "unités ou moins" not in text
    assert r"\frac{x(50-x)}{10}" in text
    assert r"0<x<50" in text and r"50<x\leq100" in text
    x = sp.symbols("x")
    original = x*(15-x/10)-(200+5*x)
    revised = x*(20-x/5)-(200+5*x)
    assert sp.expand(revised-original-x*(50-x)/10) == 0


def test_projectile_initial_height_metadata_agrees_with_statement_and_oracle():
    text = source("exercices/1SPE-SECDEG-EX-040.tex")
    metadata = json.loads(text.splitlines()[0].split("% META: ", 1)[1])
    namespace = oracle_namespace(text)
    assert metadata['parametres_sympy']['h0'] == namespace['h0'] == 2
    assert "depuis le sol" not in text


def test_thirty_degree_proposal_actually_clears_obstacle_and_has_shorter_range():
    text = source("corriges/1SPE-SECDEG-CO-040.tex")
    assert "moins haute mais plus longue" not in text
    assert r"10\sqrt{3}-13" in text
    assert "plus courte" in text
    x = sp.symbols("x")
    height = 2+x/sp.sqrt(3)-x*x/60
    assert sp.simplify(height.subs(x, 30)) == 10*sp.sqrt(3)-13
    assert height.subs(x, 30) > 3
    range30 = sp.sqrt(3)*(10+2*sp.sqrt(35))
    assert sp.simplify(height.subs(x, range30)) == 0
    assert 30 < range30 < 20+4*sp.sqrt(30)


def check_printed_identity_chains(text):
    names = set()
    # Deux équations juxtaposées par « et » ne forment pas une égalité entre
    # leurs membres : les traiter comme deux affichages distincts.
    text = text.replace(r"\qquad \text{et} \qquad", "\\]\n\\[")
    for name, variable, chain in re.findall(r"\\\[\s*([A-Za-z]+'?)\(([xt])\)\s*=(.*?)\\\]", text, re.S):
        if "=" not in chain or "^2" not in chain:
            continue
        if re.search(r"\\(?:iff|Leftrightarrow|Longleftrightarrow|[lg]eq?(?:slant)?)(?![A-Za-z])|[<>]", chain):
            continue  # Ces relations ne sont pas des identités de polynômes.
        expressions = []
        for part in chain.split("="):
            part = re.sub(r"\\(?:bigl|bigr)", "", part).strip().rstrip(".")
            # Une écriture décimale finie imprimée est une valeur exacte.
            part = re.sub(r"(\d+)\{,\}(\d+)",
                          lambda m: rf"\frac{{{int(m[1]+m[2])}}}{{{10**len(m[2])}}}", part)
            expression = latex_to_sympy(part, symbol=variable)
            assert expression is not None, part
            expressions.append(expression)
        assert all(sp.expand(a-b) == 0 for a, b in zip(expressions, expressions[1:])), chain
        names.add(name)
    return names


@pytest.mark.parametrize(("relative", "names"), [
    ("cours/07_td_fil_rouge.tex", {"W"}),
    ("cours/07_td_contextualise.tex", {"h", "k"}),
    ("corriges/1SPE-SECDEG-CO-027.tex", {"A"}),
    ("corriges/1SPE-SECDEG-CO-039.tex", {"B", "B'"}),
    ("corriges/1SPE-SECDEG-CO-040.tex", {"y"}),
])
def test_printed_polynomial_identity_chains_are_exact(relative, names):
    assert check_printed_identity_chains(source(relative)) == names


def test_printed_identity_check_rejects_a_changed_constant():
    current = source("cours/07_td_fil_rouge.tex")
    correct = r"=4\left(x-\frac{25}{2}\right)^2-25."
    assert correct in current
    mutated = current.replace(correct, r"=4\left(x-\frac{25}{2}\right)^2+25.")
    with pytest.raises(AssertionError):
        check_printed_identity_chains(mutated)
