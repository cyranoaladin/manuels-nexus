"""Le cas f(ax+b) ne se déduit pas d'une remédiation sur les quotients."""

import re
from pathlib import Path

import pytest
from sympy import diff, simplify, symbols

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / (
    "Mathematiques/manuel-maths/chapitres/TCOMPL-MODELES-FONCTION/"
    "cours/10_C1_etude_fonction.tex"
)


def _affine_section():
    text = COURSE.read_text(encoding="utf-8")
    start = text.index(r"\subsection*{Dériver après un changement affine de variable}")
    end = text.index("% STRATE 2", start)
    return text[start:end]


def test_affine_rule_has_its_domain_and_zero_case():
    section = _affine_section()
    assert r"g'(x)=a\,f'(ax+b)" in section
    assert r"ax+b\in I" in section
    assert "intervalle ouvert" in section
    assert r"Si $a=0$" in section
    assert r"$b\in I$" in section
    assert r"$g'(x)=0$" in section
    assert r"\frac{f(ax+b+ah)-f(ax+b)}{ah}" in section


def test_printed_negative_factor_example_is_exact():
    section = _affine_section()
    # Lecture des expressions réellement imprimées, indépendante de l'oracle.
    g = re.search(r"g\(x\)=\(([-0-9+x]+)\)\^2", section)
    gp = re.search(r"g'\(x\)=(-?\d+)\(([-0-9+x]+)\)", section)
    assert g is not None and gp is not None
    from sympy.parsing.sympy_parser import (
        implicit_multiplication_application, parse_expr, standard_transformations,
    )
    transformations = standard_transformations + (implicit_multiplication_application,)
    x = symbols("x")
    expr = parse_expr(g[1], transformations=transformations) ** 2
    printed = int(gp[1]) * parse_expr(gp[2], transformations=transformations)
    assert simplify(diff(expr, x) - printed) == 0


def test_affine_oracle_exercises_a_zero_and_negative_factor():
    section = _affine_section()
    block = re.search(r"% BEGIN-VERIFY\n(.*?)% END-VERIFY", section, re.S)
    assert block is not None
    script = "\n".join(re.sub(r"^%\s?", "", line)
                       for line in block[1].splitlines())
    assert "subs(a, 0)" in script
    assert "a: -2" in script
    exec(compile(script, str(COURSE), "exec"), {})
    # Un signe faux dans la formule proposée doit rendre l'oracle rouge.
    mutant = script.replace("claimed = 2*a*(a*x+b)", "claimed = -2*a*(a*x+b)")
    assert mutant != script
    with pytest.raises(AssertionError):
        exec(compile(mutant, "mutated_affine_oracle", "exec"), {})
