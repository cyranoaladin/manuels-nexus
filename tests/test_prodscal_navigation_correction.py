"""Navigation statement/correction alignment and adversarial oracle checks."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from sympy import Matrix, Rational, cos, pi, simplify, sqrt

from tests.test_prodscal_remaining_scientific_regressions import _run_fixture

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE"
SOURCE = "cours/07_td_contextualise.tex"


def source() -> str:
    return (CHAPTER / SOURCE).read_text()


def correction() -> str:
    match = re.search(
        r"\\ifnxVersionProfesseur\s*"
        r"\\begin\{corrige\}\{1SPE-PRODSCAL-TD-CONTEXTUALISE\}(.*?)"
        r"\\end\{corrige\}\s*\\fi", source(), re.S,
    )
    assert match, "The existing ten-question navigation TD needs its teacher correction."
    return match.group(1)


def test_navigation_angles_have_an_explicit_origin_orientation_and_metric() -> None:
    text = source()
    assert "origine $P$" in text and "repère orthonormé" in text
    assert "vers l'est" in text and "vers le nord" in text
    assert "sens trigonométrique" in text
    assert "30" in text and "au sud de l'est" in text
    assert "cap sud-est" not in text  # Exact southeast is -pi/4, not -pi/6.


def test_navigation_separates_travel_distance_and_resultant_distance() -> None:
    text = source()
    assert "distance totale au port" not in text
    assert "point d'arrivée au port" in text
    answers = correction()
    assert "13" in answers and "distance parcourue" in answers
    result = sqrt(89+20*sqrt(6)-20*sqrt(2))
    assert result < 13


def test_navigation_geometric_angle_is_found_before_using_its_cosine() -> None:
    statement = source()
    assert "Déterminer l'angle géométrique" in statement
    assert r"\theta\in[0,\pi]" in statement
    assert "En déduire le produit scalaire" in statement
    assert r"\frac{5\pi}{12}" in correction()
    assert r"\frac{7\pi}{12}" in correction()
    assert simplify(cos(7*pi/12)+cos(5*pi/12)) == 0


def test_each_navigation_question_has_an_explicit_teacher_answer() -> None:
    assert re.findall(r"\\textbf\{Question (\d+)\.\}", correction()) == [
        str(i) for i in range(1, 11)
    ]


def test_printed_navigation_rounding_agrees_with_exact_algebraic_bounds() -> None:
    answers = correction()
    assert "10{,}5" in answers
    length = sqrt(89+20*sqrt(6)-20*sqrt(2))
    assert Rational(209, 20) < length < Rational(211, 20)
    assert "abs(PQ_num - 10.46) < 0.1" not in source()


def test_return_course_has_the_opposite_direction_not_just_a_unit_norm() -> None:
    answers = correction()
    assert r"\cos\alpha=-" in answers and r"\sin\alpha=-" in answers
    assert "négatifs" in answers
    u = Matrix([4*sqrt(2), 4*sqrt(2)])
    v = Matrix([5*sqrt(3)/2, -Rational(5, 2)])
    back = -(u+v)
    assert back[0] < 0 and back[1] < 0
    assert u+v+back == Matrix([0, 0])


@pytest.mark.parametrize(("old", "new"), [
    ("rounded_PQ = Rational(105,10)", "rounded_PQ = Rational(104,10)"),
    ("QP = -(u+v)", "QP = u+v"),
])
def test_navigation_oracle_rejects_rounding_and_return_direction_mutations(
    tmp_path: Path, old: str, new: str,
) -> None:
    text = source()
    assert _run_fixture(tmp_path, SOURCE, text).returncode == 0
    assert old in text
    assert _run_fixture(tmp_path, SOURCE, text.replace(old, new, 1)).returncode == 1
