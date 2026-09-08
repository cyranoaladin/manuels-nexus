"""Actual domain counterexamples for the scalar-product methods and QCM."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from sympy import Matrix, Rational, cos, pi, sin, sqrt

from tests.test_prodscal_remaining_scientific_regressions import _run_fixture

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE"


def questions() -> dict:
    data = json.loads((CHAPTER / "qcm/1SPE-PRODUIT-SCALAIRE-QCM.json").read_text())
    return {question["id"]: question for question in data["questions"]}


@pytest.mark.parametrize("relative", [
    "cours/11_C2_proprietes.tex",
    "methodes/1SPE-PRODSCAL-ME-003.tex",
    "remediation/1SPE-PRODUIT-SCALAIRE-FR-R2.tex",
    "remediation/1SPE-PRODUIT-SCALAIRE-RE-C1.tex",
    "remediation/1SPE-PRODUIT-SCALAIRE-RE-C3.tex",
    "remediation/1SPE-PRODUIT-SCALAIRE-RE-C4.tex",
])
def test_coordinate_rules_declare_their_metric_in_their_own_scope(relative: str) -> None:
    text = (CHAPTER / relative).read_text()
    # An anisotropic orthogonal frame is already a counterexample to xx'+yy'.
    u, v, gram = Matrix([1, 1]), Matrix([1, -1]), Matrix.diag(4, 1)
    assert u.dot(v) == 0 and (u.T*gram*v)[0] == 3
    assert "Le plan est rapporté à un repère orthonormé." in text


def test_method_checks_nonzero_vectors_before_defining_the_geometric_angle() -> None:
    text = (CHAPTER / "methodes/1SPE-PRODSCAL-ME-003.tex").read_text()
    assert text.index("deux vecteurs non nuls") < text.index(r"\dfrac")
    assert r"\theta\in[0,\pi]" in text
    assert "angle géométrique" in text and "angle orienté" in text
    assert "vecteurs directeurs non nuls" in text


def test_analytic_proof_is_not_promoted_to_an_official_required_demonstration() -> None:
    text = (CHAPTER / "cours/11_C2_proprietes.tex").read_text()
    assert "expression analytique (exigible)" not in text
    assert "Justification de l'expression analytique" in text
    official = (ROOT / "Mathematiques/manuel-maths/sources/txt/BO2026_1SPE_specialite.txt").read_text()
    section = official.split("\nCalcul vectoriel et produit scalaire\nContenus", 1)[1].split("Approfondissements possibles", 1)[0]
    demonstrations = section.split("Démonstrations", 1)[1]
    assert "Formule d’Al-Kashi" in demonstrations and "Ensemble des points M" in demonstrations
    assert "expression du produit scalaire" not in demonstrations


@pytest.mark.parametrize("qid", ["Q1", "Q8", "Q9"])
def test_coordinate_qcm_stems_are_self_contained_about_the_frame(qid: str) -> None:
    assert "repère orthonormé" in questions()[qid]["enonce"]


def test_bisector_qcm_excludes_the_degenerate_segment() -> None:
    assert r"A\neq B" in questions()["Q10"]["enonce"]
    a = b = Matrix([0, 0])
    assert (Matrix([7, 3])-a).norm() == (Matrix([7, 3])-b).norm()
    # Equidistance to coincident endpoints gives the entire plane, not a bisector line.


@pytest.mark.parametrize("qid", ["Q4", "Q5", "Q11", "Q12", "Q15"])
def test_formula_or_invariant_qcm_questions_state_their_universal_scope(qid: str) -> None:
    text = questions()[qid]["enonce"]
    assert "pour tous" in text or "pour tout" in text or "toujours" in text


def test_qcm_universal_scope_is_necessary_in_null_and_special_angle_cases() -> None:
    qs = questions()
    # For the zero vector, Q5's four numerical options coincide. It asks an identity.
    assert "pour tout" in qs["Q5"]["enonce"]
    zero = Matrix([0, 0])
    assert zero.dot(zero) == zero.norm() == 2*zero.norm() == 0
    # For theta=pi/4, Q11's sine and cosine formula options coincide locally.
    assert "pour tout" in qs["Q11"]["enonce"]
    assert Rational(1, 2)*sin(pi/4) == Rational(1, 2)*cos(pi/4)
    assert Rational(1, 2)*sin(pi/2) != Rational(1, 2)*cos(pi/2)
    # A=90°, b=c=1 makes Q15's C and D equal, but the C equality is not universal.
    assert "toujours" in qs["Q15"]["enonce"]
    assert 1**2 + 1**2 == 2*1*1
    assert 1**2 + 2**2 != 2*1*2
    assert "isocèle" in qs["Q15"]["diagnostics"]["C"]["erreur"]


def test_qcm_area_names_the_interior_angle_and_lengths_at_its_vertex() -> None:
    text = questions()["Q11"]["enonce"]
    assert r"a=AB" in text and r"b=AC" in text
    assert r"\theta=\widehat{BAC}\in]0,\pi[" in text
    assert sin(-pi/3) < 0 < sin(pi/3)


def test_qcm_fixed_numeric_answers_preserve_their_actual_values() -> None:
    qs = questions()
    assert qs["Q1"]["correcte"] == "A" and qs["Q1"]["options"]["A"] == "$-5$"
    assert Matrix([3, -2]).dot(Matrix([1, 4])) == -5
    assert qs["Q6"]["correcte"] == "C" and qs["Q6"]["options"]["C"] == r"$\sqrt{35}$"
    assert sqrt(3**2+2*5+4**2) == sqrt(35)
    assert abs(5) <= 3*4  # The announced norms and product are feasible.
    assert qs["Q14"]["correcte"] == "C" and qs["Q14"]["options"]["C"] == "$49$"
    assert 5**2+8**2-2*5*8*cos(pi/3) == 49


def test_method_angle_oracle_rejects_the_wrong_geometric_branch(tmp_path: Path) -> None:
    relative = "methodes/1SPE-PRODSCAL-ME-003.tex"
    text = (CHAPTER / relative).read_text()
    assert _run_fixture(tmp_path, relative, text).returncode == 0
    assert "theta = acos(" in text
    changed = text.replace("theta = acos(", "theta = -acos(", 1)
    assert _run_fixture(tmp_path, relative, changed).returncode == 1
