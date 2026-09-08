"""Régressions des affirmations imprimées, y compris leurs domaines limites."""

from __future__ import annotations

import math
import re
from pathlib import Path

import pytest
import sympy

ROOT = Path(__file__).resolve().parents[1]
REMEDIATION = ROOT / "Mathematiques/manuel-maths/chapitres/TEXP-ARITHMETIQUE/remediation"


def _rendered(name: str) -> str:
    text = (REMEDIATION / name).read_text(encoding="utf-8")
    return " ".join(line for line in text.splitlines() if not line.lstrip().startswith("%"))


@pytest.mark.parametrize("integer", [-120, -12, -1, 1, 12, 120])
def test_printed_gcd_zero_identity_handles_both_signs(integer: int) -> None:
    text = _rendered("TEXP-ARITHMETIQUE-RE-C1.tex")
    # Lire le membre droit publié, et non un résultat recopié dans le test.
    match = re.search(r"\\mathrm\{PGCD\}\(n\\,;\\,0\)\s*=([^$]+)\$", text)
    assert match, "identité PGCD(n;0) absente"
    expression = match.group(1).strip().replace(r"\lvert n\rvert", "Abs(n)")
    n = sympy.Symbol("n", integer=True)
    actual = sympy.sympify(expression, locals={"n": n, "Abs": sympy.Abs}).subs(n, integer)
    assert actual == math.gcd(integer, 0)
    assert "pour tout entier non nul $n$" in text, "PGCD(0;0) est exclu par la définition du cours"


def test_printed_congruence_count_states_existence_before_multiplicity() -> None:
    text = _rendered("TEXP-ARITHMETIQUE-RE-C2.tex")
    assert r"d\mid b" in text, "le PGCD doit diviser le second membre"
    assert r"d\nmid b" in text and "aucune solution" in text
    assert r"n\geq2" in text, "domaine du module annoncé dans la remédiation"
    assert r"6x\equiv8\ [15]" in text, "contre-exemple au faux critère d>1"


def test_congruence_existence_and_count_against_independent_residue_enumeration() -> None:
    # Finite adversarial check of the printed rule, not a substitute for its proof.
    for modulus in range(2, 17):
        for coefficient in range(-17, 18):
            divisor = math.gcd(coefficient, modulus)
            for target in range(-17, 18):
                residues = [x for x in range(modulus) if (coefficient * x - target) % modulus == 0]
                expected = divisor if target % divisor == 0 else 0
                assert len(residues) == expected, (coefficient, target, modulus)
    assert [x for x in range(15) if (6 * x - 8) % 15 == 0] == []
    assert [x for x in range(15) if (6 * x - 9) % 15 == 0] == [4, 9, 14]
