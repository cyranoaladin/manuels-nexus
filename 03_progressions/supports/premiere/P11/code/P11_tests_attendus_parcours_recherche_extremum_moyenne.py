"""Tests attendus TP P11. Statut pédagogique: needs_review."""
from __future__ import annotations
import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "P11_starter_parcours_recherche_extremum_moyenne"))


def test_nominal_parcours() -> None:
    valeurs = [12, 7, 19, 19, 5]
    assert MODULE.maximum(valeurs) == 19
    assert MODULE.indices_de(valeurs, 19) == [2, 3]
    assert MODULE.moyenne([10, 12, 14]) == 12.0


def test_limites_negatifs_et_zero() -> None:
    assert MODULE.maximum([-4, -2, -9]) == -2
    assert MODULE.indices_de([1, 2, 3], 8) == []
    assert MODULE.moyenne([0]) == 0.0


def test_entrees_invalides() -> None:
    for appel in [lambda: MODULE.maximum([]), lambda: MODULE.moyenne([])]:
        try:
            appel()
        except ValueError:
            continue
        raise AssertionError("ValueError attendue")


if __name__ == "__main__":
    test_nominal_parcours()
    test_limites_negatifs_et_zero()
    test_entrees_invalides()
    print("tests attendus OK")
