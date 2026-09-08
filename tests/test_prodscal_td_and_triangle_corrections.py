"""Regression evidence for the missing TD solution and the signed angle at C."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from sympy import Matrix, Rational, acos, pi, simplify, sqrt

from tests.test_prodscal_remaining_scientific_regressions import _run_fixture

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE"
TD = "cours/07_td_fil_rouge.tex"
EX = "exercices/1SPE-PRODSCAL-EX-009.tex"
CO = "corriges/1SPE-PRODSCAL-CO-009.tex"


def td_solution() -> str:
    text = (CHAPTER / TD).read_text()
    match = re.search(
        r"\\ifnxVersionProfesseur\s*"
        r"\\begin\{corrige\}\{1SPE-PRODSCAL-TD-FIL-ROUGE\}(.*?)"
        r"\\end\{corrige\}\s*\\fi", text, re.S,
    )
    assert match, "The eleven-question TD needs a bound professor-only solution."
    return match.group(1)


def test_td_professor_solution_covers_each_of_the_eleven_actual_questions() -> None:
    solution = td_solution()
    assert re.findall(r"\\textbf\{Question (\d+)\.\}", solution) == [
        str(number) for number in range(1, 12)
    ]
    assembler = (ROOT / "Mathematiques/manuel-maths/scripts/assemble_manuel.py").read_text()
    # The source guard uses the real assembler's existing variant switch.
    assert '"\\\\nxVersionProfesseurtrue"' in assembler
    assert '"\\\\nxVersionProfesseurfalse"' in assembler
    assert '"\\\\RenewDocumentEnvironment{corrige}{m +b}{}{}"' in assembler


def test_td_q8_prints_the_general_identity_and_specializes_the_given_triangle() -> None:
    solution = td_solution()
    question8 = solution.split(r"\textbf{Question 8.}")[1].split(r"\textbf{Question 9.}")[0]
    assert "BC^2-AB^2" in question8
    assert r"\iff AB=BC" in question8
    assert "9-25=-16" in question8
    # Independent verification including equal lengths and the zero-vector edge.
    for u, v in [(Matrix([5, 0]), Matrix([-Rational(3, 2), 3*sqrt(3)/2])),
                 (Matrix([3, 4]), Matrix([0, 5])), (Matrix([0, 0]), Matrix([0, 0]))]:
        assert (u+v).dot(v-u) == v.dot(v)-u.dot(u)
        assert ((u+v).dot(v-u) == 0) == (u.norm() == v.norm())


def test_td_q11_proves_the_minimum_on_the_segment_not_just_the_line() -> None:
    solution = td_solution()
    question11 = solution.split(r"\textbf{Question 11.}")[1]
    assert r"t\in[0,1]" in question11
    assert "25+15t+9t^2" in question11
    assert "3t(5+3t)" in question11
    assert r"-\frac{5}{6}" in question11
    assert "5" in question11 and "km" in question11
    assert "strictement" in question11 and "seulement" in question11


def test_triangle_c_printed_cosine_agrees_with_the_vectors_at_that_vertex() -> None:
    text = (CHAPTER / CO).read_text().split(r"\begin{corrige}", 1)[1]
    displayed = re.search(r"\\dfrac\{(?P<sign>-?)1\}\{\\sqrt\{10\}\}", text)
    assert displayed, "The requested exact cosine at C must be printed."
    a, b, c = Matrix([0, 0]), Matrix([6, 0]), Matrix([2, 4])
    ca, cb = a-c, b-c
    value = (-1 if displayed.group("sign") else 1) / sqrt(10)
    assert simplify(ca.dot(cb)/(ca.norm()*cb.norm()) - value) == 0


def test_triangle_correction_actually_explains_the_requested_angle_sum() -> None:
    text = (CHAPTER / CO).read_text().split(r"\begin{corrige}", 1)[1]
    assert r"\arccos" in text
    assert "63{,}4" in text and "71{,}6" in text
    assert "théorème de la somme des angles" in text
    assert "arrondi" in text
    a, b, c = Matrix([0, 0]), Matrix([6, 0]), Matrix([2, 4])
    cosines = [(b-a).dot(c-a)/((b-a).norm()*(c-a).norm()),
               (a-b).dot(c-b)/((a-b).norm()*(c-b).norm()),
               (a-c).dot(b-c)/((a-c).norm()*(b-c).norm())]
    assert abs(float(sum(acos(value) for value in cosines)-pi)) < 1e-12


def test_triangle_statement_duration_agrees_with_its_printed_exercise_header() -> None:
    text = (CHAPTER / EX).read_text()
    metadata = json.loads(text.splitlines()[0].removeprefix("% META: "))
    printed = re.search(r"\\begin\{exercice\}\{[^}]+\}\{\d+\}\{(\d+)\}", text)
    assert printed
    assert metadata["duree_min"] == int(printed.group(1))


@pytest.mark.parametrize(("relative", "old", "new"), [
    (TD, "bd_dot_ac = (u+v).dot(v-u)", "bd_dot_ac = (u+v).dot(v+u)"),
    (EX, "CA, CB = A-C, B-C", "CA, CB = C-A, B-C"),
    (CO, "CA, CB = A-C, B-C", "CA, CB = C-A, B-C"),
])
def test_triangle_and_td_oracles_reject_the_repaired_sign_regression(
    tmp_path: Path, relative: str, old: str, new: str,
) -> None:
    original = (CHAPTER / relative).read_text()
    assert _run_fixture(tmp_path, relative, original).returncode == 0
    assert old in original, "The relevant missing oracle has not been repaired."
    assert _run_fixture(tmp_path, relative, original.replace(old, new, 1)).returncode == 1
