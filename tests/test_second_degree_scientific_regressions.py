"""Contre-exemples indépendants et liens aux phrases effectivement publiées."""

import re
import sys
from pathlib import Path

import sympy as sp
import yaml

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE"
sys.path.insert(0, str(ROOT / "scripts"))
from qcm_independent_solver import latex_to_sympy


def test_opening_does_not_call_a_box_volume_quadratic():
    opening = yaml.safe_load((CHAPTER / "contrat.yaml").read_text())["situation_accroche"]
    x = sp.symbols("x")
    assert sp.degree(x * (30 - 2*x) * (20 - 2*x), x) == 3
    assert not ("volume" in opening and "second degre" in opening), opening


def test_negative_discriminant_proof_divides_by_a_before_splitting_cases():
    text = (CHAPTER / "cours/12_C3_discriminant.tex").read_text()
    proof = text.split(r"\textbf{Démonstration exigible", 1)[1]
    before_negative_case = proof.split(r"\textbf{Cas 1", 1)[0]
    assert r"\frac{\Delta}{4a^2}" in before_negative_case
    # Avec a=-1, l'ancien « a fois un carré est positif » est faux.
    assert -1 * sp.Integer(1)**2 < 0
    a, b, c, x = sp.symbols("a b c x", real=True)
    delta = b*b - 4*a*c
    assert sp.simplify((a*x*x+b*x+c)/a - ((x+b/(2*a))**2-delta/(4*a*a))) == 0


def test_required_canonical_method_is_simple_completion_of_square():
    text = (CHAPTER / "cours/10_C1_formes_trinome.tex").read_text()
    required = text.split(r"\approfondissement{", 1)[0]
    assert "complétion du carré" in required
    assert r"-\frac{b}{2a}" not in required
    assert "pas un attendu" in text
    method = (CHAPTER / "methodes/1SPE-SECDEG-ME-001.tex").read_text()
    assert "complétion du carré" in method
    assert r"Je calcule l'abscisse du sommet : $\alpha = -\dfrac{b}{2a}$" not in method
    remediation = (CHAPTER / "remediation/1SPE-SECDEG-RE-C1.tex").read_text()
    assert r"Calculer $\alpha = -b/(2a)$" not in remediation
    for number in ("001", "043"):
        hint = (CHAPTER / f"exercices/1SPE-SECDEG-EX-{number}-CDP.tex").read_text()
        assert r"\alpha = -\dfrac{b}{2a}" not in hint
        assert "facteur" in hint and "carré" in hint


def test_discriminant_is_defined_before_first_use_in_forms_course():
    text = (CHAPTER / "cours/10_C1_formes_trinome.tex").read_text()
    first_delta = text.index(r"\Delta")
    assert re.match(r"\\Delta\s*=\s*b\^2\s*-\s*4ac", text[first_delta:])


def test_numeric_fraction_equalities_in_correction_025_are_true():
    text = (CHAPTER / "corriges/1SPE-SECDEG-CO-025.tex").read_text()
    fractions = re.findall(r"\\frac\{([-\d +]+)\}\{([-\d +]+)\}\s*=\s*(-?\d+)", text)
    assert fractions, "Aucune égalité numérique publiée n'a été exercée"
    for numerator, denominator, result in fractions:
        assert sp.sympify(numerator) / sp.sympify(denominator) == int(result), (numerator, denominator, result)


def test_parabola_self_check_orders_values_according_to_the_sign_of_a():
    text = (CHAPTER / "methodes/1SPE-SECDEG-ME-002.tex").read_text()
    assert r"supérieures à $\beta$ si $a > 0$" in text
    assert r"inférieures à $\beta$ si $a < 0$" in text
    a, alpha, beta, x = sp.symbols("a alpha beta x", real=True)
    f = a*(x-alpha)**2+beta
    assert sp.expand(f.subs(x, alpha+1)-beta) == a
    assert sp.expand(f.subs(x, alpha-1)-beta) == a


def test_optimization_rectangle_has_two_compatible_upper_vertices():
    text = (CHAPTER / "methodes/1SPE-SECDEG-ME-006.tex").read_text()
    assert "triangle" in text
    assert "ses deux sommets supérieurs\n  sur la droite" not in text
    x = sp.symbols("x", positive=True)
    # Droite gauche y=2t+8 et droite droite y=-2t+8 : même hauteur.
    assert (2*(-x)+8) == (-2*x+8)
    area = 2*x*(-2*x+8)
    assert sp.expand(area-(-4*(x-2)**2+16)) == 0


def test_optimization_method_checks_objective_and_excluded_boundaries():
    for relative in ("methodes/1SPE-SECDEG-ME-006.tex", "cours/15_C6_optimisation.tex"):
        text = (CHAPTER / relative).read_text()
        assert "minimum" in text and "maximum" in text
        assert "borne exclue" in text
        assert "pas être atteint" in text
    # Même sommet admissible : le minimum de -x² sur [-1,2] n'y est pas.
    x = sp.symbols("x")
    f = -x*x
    assert min(f.subs(x, t) for t in (-1, 0, 2)) == -4


def test_prerequisite_correction_keeps_the_inner_constant_ten():
    text = (CHAPTER / "remediation/1SPE-SECDEG-FR-R4.tex").read_text()
    assert r"\beta = 9 - 18 + 20 = 11" not in text
    assert r"x^2-6x+10=(x-3)^2+1" in text
    x = sp.symbols("x")
    assert sp.expand(2*((x-3)**2+1)) == 2*x*x-12*x+20


def test_profit_interval_uses_exact_endpoints_not_rounded_roots():
    text = (CHAPTER / "remediation/1SPE-SECDEG-RE-C6.tex").read_text()
    assert r"[25-5\sqrt{15}\,;\,25+5\sqrt{15}]" in text
    p = sp.symbols("p")
    profit = -2*p*p+100*p-500
    for root in (25-5*sp.sqrt(15), 25+5*sp.sqrt(15)):
        assert sp.simplify(profit.subs(p, root)) == 0
    assert profit.subs(p, sp.Rational(56, 10)) < 0


def test_article_count_optimization_is_discrete():
    statement = (CHAPTER / "exercices/1SPE-SECDEG-EX-017.tex").read_text()
    correction = (CHAPTER / "corriges/1SPE-SECDEG-CO-017.tex").read_text()
    assert "entier" in statement
    assert r"$12$ ou $13$ articles" in correction
    receipts = {x: x*(50-2*x) for x in range(26)}
    best = max(receipts.values())
    assert best == 312
    assert [x for x, value in receipts.items() if value == best] == [12, 13]


def test_upward_parabola_is_not_called_concave_down():
    correction = (CHAPTER / "corriges/1SPE-SECDEG-CO-035.tex").read_text()
    assert "concave vers le bas" not in correction
    x = sp.symbols("x")
    assert sp.diff(x*x-4*x+3, x, 2) > 0


def test_rewritten_canonical_identity_chains_are_read_from_the_corrections():
    numbers = ("001", "002", "003", "004", "006", "016", "019", "021",
               "022", "032", "033", "034", "035", "043", "048")
    for number in numbers:
        path = CHAPTER / f"corriges/1SPE-SECDEG-CO-{number}.tex"
        text = path.read_text()
        chains = re.findall(r"\\\[\s*[A-Za-z]+\(x\)\s*=(.*?)\\\]", text, re.S)
        exercised = 0
        for chain in chains:
            # Résolutions et inégalités sont des relations, pas des chaînes
            # d'identités. Ce test lit les réécritures du même polynôme.
            if ("=" not in chain or "^2" not in chain
                    or re.search(r"\\(?:iff|[lg]eq?(?:slant)?)(?![A-Za-z])|[<>]", chain)):
                continue
            parts = [re.sub(r"\\(?:bigl|bigr)", "", s).strip().rstrip(".")
                     for s in chain.split("=")]
            expressions = [latex_to_sympy(s) for s in parts]
            assert all(e is not None for e in expressions), (path, parts)
            assert all(sp.simplify(a-b) == 0 for a, b in zip(expressions, expressions[1:])), (path, parts)
            exercised += 1
        assert exercised, path


def test_factorization_method_covers_double_and_absent_real_roots():
    text = (CHAPTER / "methodes/1SPE-SECDEG-ME-001.tex").read_text()
    procedure = text.split(r"\pasApas{", 1)[1].split(r"\exempleRedige{", 1)[0]
    assert r"\Delta=0" in procedure and r"a(x-x_0)^2" in procedure
    assert r"\Delta<0" in procedure and "facteurs du premier degré réels" in procedure
    x = sp.symbols("x", real=True)
    assert sp.factor(2*x*x-4*x+2) == 2*(x-1)**2
    assert sp.solveset(-x*x-1, x, domain=sp.S.Reals) == sp.S.EmptySet


def test_optimization_method_distinguishes_real_intervals_and_integer_candidates():
    text = (CHAPTER / "methodes/1SPE-SECDEG-ME-006.tex").read_text()
    assert "intervalle réel" in text
    assert "entiers admissibles les plus proches" in text
    assert "repère orthonormé" in text
    # Un sommet non entier n'est pas une réponse réalisable; les deux voisins
    # peuvent donner le même optimum, et les bornes restent nécessaires.
    values = {n: -2*(sp.Integer(n)-sp.Rational(25, 2))**2+sp.Rational(625, 2)
              for n in range(26)}
    assert [n for n, v in values.items() if v == max(values.values())] == [12, 13]


def test_course_article_example_requires_integer_quantity():
    text = (CHAPTER / "cours/15_C6_optimisation.tex").read_text()
    example = text.split("Une entreprise vend", 1)[1].split(r"\margeAppui", 1)[0]
    assert "entier" in example
    assert "admissible" in example
    assert max(n*(-sp.Rational(1, 2)*n+100) for n in range(201)) == 5000


def test_prerequisite_correction_answers_both_curve_transformations():
    text = (CHAPTER / "remediation/1SPE-SECDEG-FR-R4.tex").read_text()
    answer = text.split(r"\begin{corrige}{1SPE-SECDEG-FR-R4-EX2}", 1)[1].split(r"\end{corrige}", 1)[0]
    third = answer.split(r"\textbf{Question 3.}", 1)[1].split(r"\textbf{Question 4.}", 1)[0]
    fourth = answer.split(r"\textbf{Question 4.}", 1)[1]
    assert "translation" in third and r"(-1\,;\,-4)" in third
    assert "symétrie" in fourth and "axe des abscisses" in fourth
    assert "translation" in fourth and r"(3\,;\,5)" in fourth
    x = sp.symbols("x")
    square = x*x
    assert sp.expand(square.subs(x, x+1)-4) == x*x+2*x-3
    assert sp.expand((-square).subs(x, x-3)+5) == -x*x+6*x-4


def test_remediation_c2_last_question_has_its_variation_table():
    text = (CHAPTER / "remediation/1SPE-SECDEG-RE-C2.tex").read_text()
    answer = text.split(r"\begin{corrige}{1SPE-SECDEG-RE-C2-EX3}", 1)[1].split(r"\end{corrige}", 1)[0]
    last = answer.split(r"\textbf{Question 3.}", 1)[1]
    assert r"\begin{tabular}" in last
    assert r"$r(x)$ & $+\infty$ & $\searrow$ & $3$ & $\nearrow$ & $+\infty$" in last
    assert r"$x$ & $-\infty$ & & $1$ & & $+\infty$" in last


def test_remediation_c6_distinguishes_strict_demand_from_nonnegative_profit():
    text = (CHAPTER / "remediation/1SPE-SECDEG-RE-C6.tex").read_text()
    statement = text.split(r"\begin{exercice}{1SPE-SECDEG-RE-C6-EX3}", 1)[1].split(r"\end{exercice}", 1)[0]
    assert "moyenne" in statement and "réel" in statement
    assert "strictement positive" in statement
    assert "positif ou nul" in statement
    p = sp.symbols("p")
    profit = -2*p*p+100*p-500
    assert sp.simplify(profit.subs(p, 25-5*sp.sqrt(15))) == 0
    assert (100-2*sp.Integer(50)) == 0
