"""Tests attendus du TP T17. Statut pédagogique : needs_review."""
from __future__ import annotations

import importlib
import os


MODULE = importlib.import_module(
    os.environ.get("TP_MODULE", "T17_starter_programmation_dynamique")
)


def test_table_et_choix() -> None:
    table, choix = MODULE.construire_table(8, [1, 4, 5])
    assert table == [0, 1, 2, 3, 1, 1, 2, 3, 2]
    assert choix[4] == 4
    assert choix[5] == 5
    assert choix[8] == 4


def test_solution_nominale_et_contre_exemple_glouton() -> None:
    assert MODULE.rendu_monnaie_dp(8, [1, 4, 5]) == (2, [4, 4])
    assert MODULE.rendu_monnaie_dp(6, [1, 3, 4]) == (2, [3, 3])


def test_zero_et_impossible() -> None:
    assert MODULE.rendu_monnaie_dp(0, [4, 6]) == (0, [])
    assert MODULE.rendu_monnaie_dp(7, [4, 6]) is None


def test_entrees_invalides() -> None:
    for montant, pieces in ((-1, [1]), (5, []), (5, [0, 2]), (5, [-1, 2])):
        try:
            MODULE.rendu_monnaie_dp(montant, pieces)
        except ValueError:
            continue
        raise AssertionError(f"ValueError attendue pour {(montant, pieces)}")


if __name__ == "__main__":
    test_table_et_choix()
    test_solution_nominale_et_contre_exemple_glouton()
    test_zero_et_impossible()
    test_entrees_invalides()
    print("tests attendus T17 OK")
