"""Tests attendus TP P07. Statut pédagogique: needs_review."""
from __future__ import annotations
import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "P07_starter_fonctions_tests_specifications"))


def test_nominal_prix_pair_nom() -> None:
    assert MODULE.prix_ttc(80.0, 0.20) == 96.0
    assert MODULE.est_pair(42) is True
    assert MODULE.normaliser_nom("  ada   lovelace ") == "Ada Lovelace"


def test_limites_zero_impair() -> None:
    assert MODULE.prix_ttc(0.0, 0.20) == 0.0
    assert MODULE.est_pair(0) is True
    assert MODULE.est_pair(7) is False


def test_entrees_invalides() -> None:
    for appel in [lambda: MODULE.prix_ttc(-5.0, 0.20), lambda: MODULE.prix_ttc(10.0, -0.1)]:
        try:
            appel()
        except ValueError:
            continue
        raise AssertionError("ValueError attendue")
    try:
        MODULE.normaliser_nom("")
    except ValueError:
        return
    raise AssertionError("ValueError attendue pour nom vide")


if __name__ == "__main__":
    test_nominal_prix_pair_nom()
    test_limites_zero_impair()
    test_entrees_invalides()
    print("tests attendus OK")
