"""P0_VERIFICATION_INVARIANT_BLINDNESS : le test de sensibilite.

Ce fichier doit demontrer UNE chose avant tout : le nouvel oracle attrape
exactement la faute que l'ancien controle ne pouvait pas voir.

L'ancien controle etait « la somme des feuilles vaut 1 ». Il est invariant
sous permutation : echanger deux valeurs entre deux etiquettes le laisse
vrai. Il ne pouvait donc pas etablir l'association etiquette -> valeur.
"""

from __future__ import annotations

import importlib.util
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CORRECTION = (
    ROOT
    / "Mathematiques/manuel-maths/chapitres/1SPE-PROBA-COND"
    / "corriges/1SPE-PROBCOND-CO-015.tex"
)

#: Donnees de l'enonce EX-015, lues dans l'exercice et non dans le corrige :
#: un oracle qui reutiliserait les expressions du corrige ne prouverait rien.
FIRST_LEVEL = {"R": Fraction(3, 5), "~R": Fraction(2, 5)}
CONDITIONAL = {
    "R": {"S": Fraction(9, 10), "~S": Fraction(1, 10)},
    "~R": {"S": Fraction(7, 10), "~S": Fraction(3, 10)},
}


@pytest.fixture(scope="module")
def oracle():
    spec = importlib.util.spec_from_file_location(
        "probability_path_oracle", ROOT / "scripts/probability_path_oracle.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _body(path: Path) -> str:
    return path.read_text(encoding="utf-8").split("\n", 1)[1]


def test_the_published_correction_matches_label_by_label(oracle) -> None:
    printed = oracle.printed_paths(_body(CORRECTION))
    expected = oracle.expected_paths(FIRST_LEVEL, CONDITIONAL)
    assert oracle.compare(printed, expected) == {}


def test_the_sum_is_one_but_only_as_a_secondary_control(oracle) -> None:
    expected = oracle.expected_paths(FIRST_LEVEL, CONDITIONAL)
    assert oracle.sum_of_paths(expected) == 1


def test_swapping_two_labels_keeps_the_sum_but_fails_the_oracle(oracle) -> None:
    """LE test de la classe.

    On part de la verite, on echange deux valeurs entre deux etiquettes --
    la faute exacte qui etait publiee. La somme reste 1, donc l'ancien
    controle passe encore. Le nouvel oracle, lui, doit echouer.
    """
    expected = oracle.expected_paths(FIRST_LEVEL, CONDITIONAL)
    mutated = dict(expected)
    mutated["S&~R"], mutated["~S&R"] = expected["~S&R"], expected["S&~R"]

    # L'invariant global ne bouge pas : il est aveugle a la permutation.
    assert oracle.sum_of_paths(mutated) == oracle.sum_of_paths(expected) == 1

    # L'oracle sensible aux etiquettes, lui, voit la faute.
    mismatches = oracle.compare(mutated, expected)
    assert set(mismatches) == {"S&~R", "~S&R"}
    assert mismatches["S&~R"] == {"expected": "7/25", "printed": "3/50"}


def test_a_missing_path_is_reported_not_silently_tolerated(oracle) -> None:
    expected = oracle.expected_paths(FIRST_LEVEL, CONDITIONAL)
    partial = {k: v for k, v in expected.items() if k != "S&R"}
    assert oracle.compare(partial, expected)["S&R"]["printed"] is None


def test_the_historic_defect_would_be_caught_today(oracle) -> None:
    """Le texte exact qui etait publie doit echouer.

    Il imprimait 3/50 sous $P(S \\cap \\overline{R})$ et 14/50 sous
    $P(\\overline{S} \\cap R)$.
    """
    published_defect = (
        r"$P(S \cap R) = \frac{3}{5} \times \frac{9}{10} = \frac{27}{50}$. "
        r"$P(S \cap \overline{R}) = \frac{3}{5} \times \frac{1}{10} = \frac{3}{50}$. "
        r"$P(\overline{S} \cap R) = \frac{2}{5} \times \frac{7}{10} = \frac{14}{50}$. "
        r"$P(\overline{S} \cap \overline{R}) = \frac{2}{5} \times \frac{3}{10} = \frac{6}{50}$."
    )
    printed = oracle.printed_paths(published_defect)
    expected = oracle.expected_paths(FIRST_LEVEL, CONDITIONAL)
    assert oracle.sum_of_paths(printed) == 1, "la somme passait : c'est tout le probleme"
    assert set(oracle.compare(printed, expected)) == {"S&~R", "~S&R"}
