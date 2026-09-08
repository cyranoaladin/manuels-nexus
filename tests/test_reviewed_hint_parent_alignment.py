"""Régressions des défauts trouvés en lisant aides, parents et corrections."""

from pathlib import Path
import re

import sympy
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application, parse_expr, standard_transformations,
)

ROOT = Path(__file__).resolve().parents[1] / "Mathematiques/manuel-maths/chapitres"


def _read(chapter, relative):
    return (ROOT / chapter / relative).read_text(encoding="utf-8")


def test_product_rule_correction_has_no_false_intermediate_equality():
    text = _read("1SPE-DERIVATION-GLOBAL", "corriges/1SPE-DERGLOBAL-CO-013.tex")
    chain = re.search(r"g'\(x\) = p'\(x\).*?\n", text).group()
    polynomial_steps = [step.strip().rstrip(".") for step in chain.split("=")
                        if not any(token in step for token in ("g'", "p(", "p'", "q("))]
    assert len(polynomial_steps) >= 3, "vérifier aussi le développement intermédiaire"
    x = sympy.Symbol("x")
    expected = sympy.diff(x * (x - 1) * (x + 1), x)
    for step in polynomial_steps:
        parsed = parse_expr(step.replace("^", "**"), transformations=(
            standard_transformations + (implicit_multiplication_application,)
        ))
        assert sympy.expand(parsed - expected) == 0, step


def test_sqrt_question_distinguishes_definition_and_differentiability_domains():
    exercise = _read("1SPE-DERIVATION-GLOBAL", "exercices/1SPE-DERGLOBAL-EX-002.tex")
    correction = _read("1SPE-DERIVATION-GLOBAL", "corriges/1SPE-DERGLOBAL-CO-002.tex")
    assert "domaine de définition" in exercise and "dérivabilité" in exercise
    assert "n'est pas dérivable en $0$" in correction
    assert r"\frac{\sqrt{h}-\sqrt{0}}{h}" in correction


def test_product_rule_instruction_keeps_the_second_term():
    exercise = _read("1SPE-DERIVATION-GLOBAL", "exercices/1SPE-DERGLOBAL-EX-013.tex")
    assert "puis multiplier" not in exercise
    assert "appliquer la règle du produit" in exercise


def test_proof_hint_starts_from_bilinearity_instead_of_its_target_identity():
    text = _read("1SPE-PRODUIT-SCALAIRE", "exercices/1SPE-PRODSCAL-EX-012-CDP.tex")
    assert "bilinéarité" in text
    assert "Utiliser l'identite" not in text
    assert r"(\vec{u}+\vec{v})\cdot(\vec{u}+\vec{v})" in text


def test_height_hint_uses_incidence_and_orthogonality_for_its_parent():
    text = _read("1SPE-PRODUIT-SCALAIRE", "exercices/1SPE-PRODSCAL-EX-032-CDP.tex")
    assert r"\overrightarrow{BH}=t\overrightarrow{BC}" in text
    assert r"\overrightarrow{AH}\cdot\overrightarrow{BC}=0" in text
    assert "mediatrice" not in text and "médiatrice" not in text


def test_stationary_hint_does_not_claim_a_general_necessary_sign_change():
    for number in (31, 32, 33, 34):
        text = _read("1SPE-DERIVATION-GLOBAL", f"exercices/1SPE-DERGLOBAL-EX-{number:03d}-CDP.tex")
        assert "n'est un extremum que si" not in text
        assert "permet de conclure" in text
