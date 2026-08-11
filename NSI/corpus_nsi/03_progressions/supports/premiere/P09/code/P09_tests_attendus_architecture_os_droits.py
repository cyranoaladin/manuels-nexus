"""Tests attendus TP P09. Statut pédagogique: needs_review."""
from __future__ import annotations
import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "P09_starter_architecture_os_droits"))


def test_nominal_chmod_permissions() -> None:
    assert MODULE.droits_symboliques(640) == "rw-r-----"
    assert MODULE.peut_lire(640, "user") is True
    assert MODULE.peut_lire(640, "other") is False
    assert MODULE.chmod_ajouter_execution(640, "user") == 740


def test_limites_permissions_zero() -> None:
    assert MODULE.droits_symboliques(0) == "---------"
    assert MODULE.chmod_ajouter_execution(0, "other") == 1


def test_entrees_invalides() -> None:
    for appel in [lambda: MODULE.droits_symboliques(888), lambda: MODULE.peut_lire(640, "admin")]:
        try:
            appel()
        except ValueError:
            continue
        raise AssertionError("ValueError attendue")


if __name__ == "__main__":
    test_nominal_chmod_permissions()
    test_limites_permissions_zero()
    test_entrees_invalides()
    print("tests attendus OK")
