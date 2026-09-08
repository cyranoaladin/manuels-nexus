"""Regressions for hypotheses, parent-aligned hints and the Al-Kashi oracle."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "Mathematiques/manuel-maths"
CHAPTER = MANUAL / "chapitres/1SPE-PRODUIT-SCALAIRE"
COORDINATE_TRIPLETS = (1, 3, 13, 21, 22, 23, 24, 31, 32, 33, 34)


def source(number: int, role: str) -> Path:
    if role == "CO":
        return CHAPTER / f"corriges/1SPE-PRODSCAL-CO-{number:03d}.tex"
    suffix = "-CDP" if role == "CDP" else ""
    return CHAPTER / f"exercices/1SPE-PRODSCAL-EX-{number:03d}{suffix}.tex"


def visible(number: int, role: str) -> str:
    return "\n".join(line for line in source(number, role).read_text().splitlines()
                     if not line.lstrip().startswith("%"))


def test_coordinate_objects_state_the_hypothesis_needed_for_metric_formulas() -> None:
    missing = [(number, role) for number in COORDINATE_TRIPLETS
               for role in ("EX", "CO", "CDP")
               if "repère orthonormé" not in visible(number, role)]
    assert not missing, f"metric coordinate formulas lack their hypothesis: {missing}"


def test_nonorthogonal_parent_hint_does_not_instruct_to_prove_zero() -> None:
    assert 2 * (-3) + 4 * 6 == 18
    text = visible(21, "CDP")
    assert "vérifier qu'il vaut" not in text
    assert "sinon" in text and "orthogonaux" in text


def test_angle_triplet_defines_geometric_angle_and_nonzero_denominator() -> None:
    assert all("géométrique" in visible(23, role) for role in ("EX", "CO", "CDP"))
    hint = visible(23, "CDP")
    assert r"\theta\in[0,\pi]" in hint
    assert "normes" in hint and "strictement positives" in hint
    assert "Pour montrer l'orthogonal" not in hint


def test_area_hint_defines_vectors_and_interior_angle_from_its_parent() -> None:
    hint = visible(33, "CDP")
    assert all(term in hint for term in (
        r"\overrightarrow{AB}", r"\overrightarrow{AC}", r"\widehat{BAC}", r"\mathcal{A}",
    ))
    assert "médiatrice" not in hint and "mediatrice" not in hint


def test_bisector_hints_do_not_offer_an_unrelated_area_formula() -> None:
    for number in (31, 34):
        hint = visible(number, "CDP")
        assert "Pour l'aire" not in hint
        assert r"\overrightarrow{IM}" in hint and r"\overrightarrow{AB}" in hint


def _run_fixture(tmp_path: Path, tex: str) -> subprocess.CompletedProcess[str]:
    scripts = tmp_path / "scripts"
    scripts.mkdir(exist_ok=True)
    for name in ("verify_sympy.py", "common.py"):
        shutil.copyfile(MANUAL / "scripts" / name, scripts / name)
    fixture = tmp_path / "chapitres/PROBE/exercices/ALKASHI.tex"
    fixture.parent.mkdir(parents=True, exist_ok=True)
    fixture.write_text(tex)
    return subprocess.run(
        [sys.executable, str(scripts / "verify_sympy.py"), "--chap", "PROBE"],
        cwd=tmp_path, text=True, capture_output=True, timeout=15,
    )


@pytest.mark.parametrize("role", ["EX", "CO"])
@pytest.mark.parametrize("wrong_candidate", ["-sqrt(39)", "sqrt(40)"])
def test_alkashi_oracle_rejects_negative_or_wrong_length(
    tmp_path: Path, role: str, wrong_candidate: str,
) -> None:
    original = source(41, role).read_text()
    assert _run_fixture(tmp_path, original).returncode == 0
    # Mutate only the claimed length in the actual oracle. The former
    # sqrt(39) == sqrt(39) assertion accepted both of these wrong candidates.
    block = re.search(r"% BEGIN-VERIFY\n.*?% END-VERIFY", original, re.S).group()
    assert "sqrt(39)" in block
    changed = original.replace(block, block.replace("sqrt(39)", wrong_candidate))
    result = _run_fixture(tmp_path, changed)
    assert result.returncode == 1, "the canonical gate accepted an invalid length"
