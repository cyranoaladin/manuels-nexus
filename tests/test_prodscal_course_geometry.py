"""Source-facing counterexamples for the scalar-product geometry courses."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from sympy import Matrix, Rational

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "Mathematiques/manuel-maths"
COURSES = MANUAL / "chapitres/1SPE-PRODUIT-SCALAIRE/cours"
APPLICATIONS = "13_C4_applications.tex"
PROJECTION = "10_C1_produit_scalaire.tex"


def visible(name: str) -> str:
    return "\n".join(line for line in (COURSES / name).read_text().splitlines()
                     if not line.lstrip().startswith("%"))


def bisector_statements() -> str:
    # The original first oracle followed both purported bisector statements.
    return (COURSES / APPLICATIONS).read_text().split("% BEGIN-VERIFY", 1)[0]


def test_universal_polarization_is_not_a_bisector_characterization() -> None:
    a, b, m = Matrix([0, 0]), Matrix([2, 0]), Matrix([0, 0])
    ma, mb, ab = a - m, b - m, b - a
    assert ma.dot(ma) != mb.dot(mb)  # M=A is not on the bisector.
    assert ma.dot(mb) == (ma.dot(ma) + mb.dot(mb) - ab.dot(ab)) / 2
    false_iff = re.compile(
        r"\\iff\s+\\overrightarrow\{MA\}\s*\\cdot\s*"
        r"\\overrightarrow\{MB\}\s*=\s*\\frac",
    )
    assert not false_iff.search(bisector_statements())


def test_printed_ma_dot_ab_condition_has_the_correct_sign() -> None:
    text = bisector_statements()
    formula = re.search(
        r"\\overrightarrow\{MA\}\s*\\cdot\s*\\overrightarrow\{AB\}"
        r"\s*=\s*(?P<sign>[-+]?)\\[d]?frac\{1\}\{2\}"
        r"\\\|\\overrightarrow\{AB\}\\\|\^2", text,
    )
    assert formula, "The equivalent signed MA·AB condition must remain explicit."
    a, b, m = Matrix([0, 0]), Matrix([2, 0]), Matrix([1, 3])
    ma, mb, ab = a - m, b - m, b - a
    assert ma.dot(ma) == mb.dot(mb)
    printed_sign = -1 if formula.group("sign") == "-" else 1
    assert ma.dot(ab) == printed_sign * Rational(1, 2) * ab.dot(ab)


def test_bisector_does_not_use_the_diameter_circle_condition() -> None:
    text = bisector_statements()
    a, b = Matrix([0, 0]), Matrix([2, 0])
    m = (a + b) / 2
    assert (a - m).dot(a - m) == (b - m).dot(b - m)
    assert (a - m).dot(b - m) == -1  # Midpoint is not on diameter circle.
    assert not re.search(
        r"\\overrightarrow\{MA\}\s*\\cdot\s*\\overrightarrow\{MB\}\s*=\s*0", text,
    )
    assert re.search(
        r"\\overrightarrow\{IM\}\s*\\cdot\s*\\overrightarrow\{AB\}\s*=\s*0", text,
    )
    assert r"A\neq B" in text, "The segment must define a unique bisector."


def test_diameter_circle_is_distinguished_and_includes_its_endpoints() -> None:
    text = visible(APPLICATIONS)
    assert r"MI^2 - \frac{AB^2}{4}" in text
    assert "cercle de diamètre" in text
    assert "$A$ et $B$" in text and "appartiennent" in text
    a, b = Matrix([0, 0]), Matrix([2, 0])
    midpoint = (a + b) / 2
    for m, on_circle in [(a, True), (b, True), (midpoint, False), (Matrix([1, 1]), True)]:
        ma_mb = (a - m).dot(b - m)
        mi = midpoint - m
        assert ma_mb == mi.dot(mi) - (b - a).dot(b - a) / 4
        assert (ma_mb == 0) == on_circle


def test_projection_defines_common_origin_and_signed_orientation() -> None:
    text = visible(PROJECTION).split(r"\definition[Produit scalaire par projection]{", 1)[1]
    text = text.split(r"\definition[Expression analytique]", 1)[0]
    assert r"\overrightarrow{OA}=\vec{u}" in text
    assert r"\overrightarrow{OB}=\vec{v}" in text
    assert "de $O$ vers $A$" in text
    assert "négative" in text and "opposé" in text
    assert "$(OA)$" in text and "projeté orthogonal de $B$" in text
    # Positive distance OH would give +6, while the signed projection gives -6.
    assert Matrix([2, 0]).dot(Matrix([-3, 4])) == -6


def test_geometric_angle_is_defined_only_for_two_nonzero_vectors() -> None:
    definition = visible(PROJECTION).split(r"\definition[Produit scalaire (définition géométrique)]{", 1)[1]
    before_formula = definition.split(r"\[", 1)[0]
    assert "deux vecteurs non nuls" in before_formula
    assert r"Si l'un des deux vecteurs est nul" in definition


def _run_fixture(tmp_path: Path, tex: str) -> subprocess.CompletedProcess[str]:
    scripts = tmp_path / "scripts"
    scripts.mkdir(exist_ok=True)
    for name in ("verify_sympy.py", "common.py"):
        shutil.copyfile(MANUAL / "scripts" / name, scripts / name)
    fixture = tmp_path / "chapitres/PROBE/cours/GEOMETRY.tex"
    fixture.parent.mkdir(parents=True, exist_ok=True)
    fixture.write_text(tex)
    return subprocess.run(
        [sys.executable, str(scripts / "verify_sympy.py"), "--chap", "PROBE"],
        cwd=tmp_path, text=True, capture_output=True, timeout=15,
    )


@pytest.mark.parametrize(("name", "valid", "invalid"), [
    (APPLICATIONS, "MA_dot_AB + AB_sq/2 + IM_dot_AB", "MA_dot_AB - AB_sq/2 + IM_dot_AB"),
    (APPLICATIONS, "circle_identity = MI_sq - AB_sq/4", "circle_identity = MI_sq + AB_sq/4"),
    (PROJECTION, "signed_OH = t * norm_u", "signed_OH = abs(t) * norm_u"),
])
def test_current_oracles_reject_the_geometric_sign_regressions(
    tmp_path: Path, name: str, valid: str, invalid: str,
) -> None:
    original = (COURSES / name).read_text()
    assert _run_fixture(tmp_path, original).returncode == 0
    assert valid in original, "The corrected printed claim needs an exercised oracle."
    result = _run_fixture(tmp_path, original.replace(valid, invalid))
    assert result.returncode == 1, "The canonical oracle accepted a geometric sign error."


def test_realness_oracle_rejects_complex_term_invisible_at_its_numeric_examples(
    tmp_path: Path,
) -> None:
    original = (COURSES / PROJECTION).read_text()
    assignment = "% ps = u_norm * v_norm * cos(theta)"
    assert assignment in original
    assert _run_fixture(tmp_path, original).returncode == 0
    # This imaginary term vanishes at both old examples (0 and pi/2).
    # Accepting "is_real or is_complex" silently accepted this invalid product.
    mutated = original.replace(assignment, assignment + " + I*sin(theta)*cos(theta)", 1)
    assert _run_fixture(tmp_path, mutated).returncode == 1
