"""Counterexamples and oracle mutations for the bounded PRODSCAL lot C."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from sympy import Matrix, Rational, sqrt, symbols

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "Mathematiques/manuel-maths"
CHAPTER = MANUAL / "chapitres/1SPE-PRODUIT-SCALAIRE"
TD = "cours/07_td_fil_rouge.tex"
ANGLES = "cours/12_C3_orthogonalite.tex"
ALKASHI = "cours/14_C5_al_kashi.tex"
METHOD1 = "methodes/1SPE-PRODSCAL-ME-001.tex"
METHOD4 = "methodes/1SPE-PRODSCAL-ME-004.tex"
METHOD5 = "methodes/1SPE-PRODSCAL-ME-005.tex"
SCALAR = "remediation/1SPE-PRODUIT-SCALAIRE-FR-R1.tex"


def visible(relative: str) -> str:
    return "\n".join(line for line in (CHAPTER / relative).read_text().splitlines()
                     if not line.lstrip().startswith("%"))


def test_trail_distance_distinguishes_segment_from_its_supporting_line() -> None:
    text = visible(TD)
    a, b, c = Matrix([5, 0]), Matrix([0, 0]), Matrix([-Rational(3, 2), 3*sqrt(3)/2])
    parameter = (a-b).dot(c-b) / (c-b).dot(c-b)
    assert parameter == -Rational(5, 6)
    # For every t in [0,1], the excess squared distance over AB² is nonnegative.
    t = symbols("t", nonnegative=True)
    distance_squared = ((b+t*(c-b))-a).dot((b+t*(c-b))-a).expand()
    assert (distance_squared - 25).factor() == 3*t*(3*t+5)
    assert (distance_squared - 25).is_nonnegative is True
    assert "distance minimale est exactement $h$" not in text
    assert "Depuis le refuge $A$" in text
    assert "segment $[BC]$" in text and "le plus proche" in text


def test_trail_context_does_not_impose_incompatible_compass_bearings() -> None:
    text = visible(TD)
    assert r"\frac{2\pi}{3}" in text  # Preserve the actual obtuse-triangle data.
    assert not ("vers le nord-est" in text and "vers le sud-est" in text)


def test_angle_course_defines_the_geometric_branch_and_metric_frame() -> None:
    text = visible(ANGLES)
    assert r"\theta\in[0,\pi]" in text
    assert "angle géométrique" in text
    assert "Le plan est rapporté à un repère orthonormé." in text


def test_projection_method_defines_the_origin_direction_and_null_case() -> None:
    text = visible(METHOD1)
    assert r"\overrightarrow{OA}=\vec{u}" in text
    assert r"\overrightarrow{OB}=\vec{v}" in text
    assert "de $O$ vers $A$" in text
    assert "mesure algébrique" in text and "négative" in text
    assert "Si l'un des vecteurs est nul" in text


def test_area_method_names_adjacent_sides_and_the_positive_sine_branch() -> None:
    text = visible(METHOD4)
    assert "non aplati" in text
    assert r"\vec{u}=\overrightarrow{AB}" in text
    assert r"\vec{v}=\overrightarrow{AC}" in text
    assert r"\theta=\widehat{BAC}\in]0,\pi[" in text
    assert r"H\in(BC)" in text
    assert r"A\neq B" in text


def test_bisector_method_uses_a_normal_vector_in_an_orthonormal_frame() -> None:
    text = visible(METHOD4)
    assert "vecteur directeur" not in text
    assert "vecteur normal" in text
    assert "repère orthonormé" in text
    assert "sauf si $A = B$" not in text


def test_method_alkashi_printed_rounding_is_supported_by_an_exact_interval() -> None:
    match = re.search(r"\\approx\s+(\d+)\{,\}(\d{2})", visible(METHOD5))
    assert match
    displayed = Rational(int(match.group(1))*100 + int(match.group(2)), 100)
    length = sqrt(52-24*sqrt(2))
    assert displayed-Rational(1, 200) < length < displayed+Rational(1, 200)


def _run_fixture(tmp_path: Path, relative: str, tex: str) -> subprocess.CompletedProcess[str]:
    scripts = tmp_path / "scripts"
    scripts.mkdir(exist_ok=True)
    for name in ("verify_sympy.py", "common.py"):
        shutil.copyfile(MANUAL / "scripts" / name, scripts / name)
    fixture = tmp_path / "chapitres/PROBE" / relative
    fixture.parent.mkdir(parents=True, exist_ok=True)
    fixture.write_text(tex)
    return subprocess.run(
        [sys.executable, str(scripts / "verify_sympy.py"), "--chap", "PROBE"],
        cwd=tmp_path, capture_output=True, text=True, timeout=15,
    )


@pytest.mark.parametrize(("relative", "valid", "invalid"), [
    (ALKASHI, "al_kashi = b**2 + c**2 - 2*b*c*cos(A_angle)",
     "al_kashi = b**2 + c**2 + 2*b*c*cos(A_angle)"),
    (ALKASHI, "a_sq = (AC-AB).dot(AC-AB)", "a_sq = (AC+AB).dot(AC+AB)"),
    (SCALAR, "triple = 3*u", "triple = 4*u"),
    (METHOD1, "signed_OH = t*r", "signed_OH = abs(t)*r"),
    (METHOD4, "normal = B-A", "normal = Matrix([0,1])"),
    (METHOD5, "BC = sqrt(BC_sq)", "BC = -sqrt(BC_sq)"),
    (TD, "projection_parameter = (A-B).dot(BC)/BC.dot(BC)",
     "projection_parameter = abs((A-B).dot(BC)/BC.dot(BC))"),
])
def test_repaired_oracles_reject_the_relevant_scientific_mutation(
    tmp_path: Path, relative: str, valid: str, invalid: str,
) -> None:
    original = (CHAPTER / relative).read_text()
    assert _run_fixture(tmp_path, relative, original).returncode == 0
    assert valid in original, "The changed scientific claim lacks its relevant oracle."
    mutated = original.replace(valid, invalid, 1)
    assert _run_fixture(tmp_path, relative, mutated).returncode == 1
