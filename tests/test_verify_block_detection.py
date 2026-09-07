"""Un bloc de vérification se lit avec un analyseur, pas avec un motif.

`^\\s*assert` ne voit pas `E = p; assert E == Rational(3, 10)` : l'assertion
suit un point-virgule, elle ne commence pas la ligne. Quatorze objets sur les
vingt-deux signalés « bloc présent mais sans assertion exécutable » en
contenaient, et le compteur les présentait comme des blocs vides.

C'est la même faute que partout ailleurs dans ce dépôt : résoudre par
ressemblance au lieu de résoudre par structure. Python sait analyser du Python.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_dimension_mathematics as maths  # noqa: E402


def test_an_assertion_after_a_semicolon_is_seen() -> None:
    programme = "from sympy import Rational\np = Rational(3, 10)\nE = p; assert E == Rational(3, 10)"
    assert maths.assertion_count(programme) == 1


def test_an_assertion_at_line_start_is_still_seen() -> None:
    assert maths.assertion_count("x = 1\nassert x == 1") == 1


def test_several_assertions_on_one_line_are_counted() -> None:
    assert maths.assertion_count("assert True; assert 1 == 1") == 2


def test_an_assertion_inside_a_loop_is_seen() -> None:
    programme = "for k in range(3):\n    assert k < 3"
    assert maths.assertion_count(programme) == 1


def test_a_block_without_assertion_counts_zero() -> None:
    assert maths.assertion_count("x = 1\ny = x + 1\nprint(y)") == 0


def test_the_word_assert_in_a_string_is_not_an_assertion() -> None:
    """Un motif textuel s'y tromperait ; un analyseur non."""
    assert maths.assertion_count('message = "assert x == 1"') == 0
    assert maths.assertion_count("# assert x == 1") == 0


def test_an_unparsable_block_is_not_silently_declared_empty() -> None:
    """Un bloc qui ne compile pas est un défaut, pas un zéro."""
    assert maths.assertion_count("def f(:\n    pass") is None


def test_no_deposited_object_is_wrongly_called_empty() -> None:
    """Les quatorze faux positifs ne doivent plus apparaître."""
    import json

    payload = json.loads(
        (ROOT / "audit/DIMENSION_MATHEMATICS.json").read_text(encoding="utf-8")
    )
    flagged = {f["target"] for f in payload["findings"]
               if f["code"] == "EMPTY_VERIFY_BLOCK"}
    faux_positifs = {
        "1SPE-DERLOCAL-EX-006", "1SPE-VARALEA-CO-020", "1SPE-VARALEA-CO-023",
        "1SPE-VARALEA-CO-034", "1SPE-VARALEA-CO-038", "1SPE-VARALEA-EX-029",
    }
    assert not (flagged & faux_positifs), sorted(flagged & faux_positifs)
