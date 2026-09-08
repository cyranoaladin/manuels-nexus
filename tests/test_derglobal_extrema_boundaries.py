"""Contre-exemples discriminants aux conditions d'extremum imprimées."""
from pathlib import Path
import re
import sympy as s
import yaml

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL'
C3=D/'cours/12_C3_signe_variations.tex'
C4=D/'cours/13_C4_extremums.tex'
M4=D/'methodes/1SPE-DERGLOBAL-ME-004.tex'
LOGIC=ROOT/'Mathematiques/manuel-maths/transversal/logique_raisonnement.tex'


def printed(path):
    return '\n'.join(line for line in path.read_text().splitlines() if not line.lstrip().startswith('%'))


def test_fermat_hypothesis_requires_an_interior_point_in_both_courses():
    c4=printed(C4)
    theorem=re.search(r'\\begin\{nxthm\}.*?\\end\{nxthm\}',c4,re.S).group()
    assert 'intérieur' in theorem
    c3=printed(C3).split(r'\propriete[Condition nécessaire')[1].split(r'\contreexemple')[0]
    assert 'intérieur' in c3
    assert r'$f(x)=x$ sur $[0\,;\,1]$' in c4
    assert r"$f'(x)=1$" in c4
    x=s.symbols('x')
    assert s.diff(x,x) == 1
    assert x.subs(x,0) < x.subs(x,1)


def test_constant_extrema_do_not_require_a_sign_change():
    text=printed(C4)
    assert 'maximum et un minimum' in text and 'constante' in text
    assert 'non stricts' in text
    assert 'critères suffisants' in text
    assert "Il faut toujours vérifier le changement de signe" not in text
    assert r"$f$ \textbf{n'admet pas" not in text.split('Critère du changement de signe')[1].split(r'\end{nxprop}')[0]
    assert s.diff(s.Integer(7),s.Symbol('x')) == 0


def test_zero_derivative_is_not_sufficient_and_method_does_not_invent_inflection():
    text=printed(M4)
    assert 'point d\'inflexion' not in text
    assert 'fonction constante' in text and '$x^3$' in text
    t=s.symbols('t',positive=True)
    assert (-t)**3 < 0 and t**3 > 0
    assert s.diff(s.Symbol('x')**3,s.Symbol('x')).subs(s.Symbol('x'),0) == 0


def test_global_candidates_include_domain_boundaries_and_contract_matches():
    for path in [C3,C4,M4]:
        assert 'bornes' in printed(path),path
    contract=yaml.safe_load((D/'contrat.yaml').read_text())
    wording=next(c['libelle_eleve'] for c in contract['capacites'] if c['code']=='C4')
    assert 'variations' in wording and 'bornes' in wording
    assert wording in printed(C4)


def test_non_strict_variations_and_constant_characterization_are_explicit():
    text=printed(C3)
    assert r"$f'(x)\geqslant0$" in text
    assert r"$f'(x)\leqslant0$" in text
    assert 'constante' in text and 'si et seulement si' in text
    assert 'suffisantes' in text


def test_parity_reduction_stays_inside_the_actual_domain():
    assert r'$D\cap[0\,;\,+\infty[$' in printed(C3)
    # The constant function on [-1,1] is even; it is not defined at 2.
    assert 2 not in s.Interval(-1,1)


def test_c4_table_places_each_arrow_in_the_correct_interval():
    text=printed(C4)
    assert r'f(x) & & \nearrow & 3 & \searrow & 2 & \nearrow & ' in text
    x=s.symbols('x')
    f=2*x**3-9*x**2+12*x-2
    assert s.expand(s.diff(f,x)-6*(x-2)*(x-1)) == 0
    assert [f.subs(x,a) for a in [0,1,2,3]] == [-2,3,2,7]
    assert '$f(0)=-2<2$' in text and '$f(3)=7>3$' in text


def test_fermat_example_in_logic_keeps_the_same_ambient_hypotheses():
    text=printed(LOGIC).split(r"\contreexemple{L'implication")[1].split(r'\definition[Contraposée')[0]
    assert 'intérieur' in text and 'mêmes hypothèses' in text


def test_second_derivative_optional_criterion_also_requires_interior_point():
    text=printed(C4).split(r'\approfondissement{')[1]
    assert 'intérieur' in text
    assert 'dépasse le programme de Première' in text


def test_method_does_not_leave_local_versus_global_ambiguous():
    text=printed(M4)
    assert '$f(-2)=19>3$' in text and '$f(4)=-17<-1$' in text
    x=s.symbols('x')
    f=-x**3+3*x**2-1
    assert [f.subs(x,a) for a in [-2,0,2,4]] == [19,-1,3,-17]
