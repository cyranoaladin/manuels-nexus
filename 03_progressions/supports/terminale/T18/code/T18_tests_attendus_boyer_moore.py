"""Tests attendus TP T18. Statut pédagogique: needs_review."""
from __future__ import annotations
import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "T18_starter_boyer_moore"))


def test_nominal_table_et_indice() -> None:
    assert MODULE.table_mauvais_caractere("ABA") == {"A": 2, "B": 1}
    assert MODULE.boyer_moore("NSI_ABA_TEST", "ABA") == 4
    assert MODULE.trace_decalages("NSI_ABA_TEST", "ABA")[0] == 0


def test_limite_absent() -> None:
    assert MODULE.boyer_moore("AAAAAC", "BA") == -1
    assert MODULE.trace_decalages("AAAAAC", "BA") == [0, 1, 2, 3, 4]


def test_entrees_invalides() -> None:
    try:
        MODULE.boyer_moore("texte", "")
    except ValueError:
        return
    raise AssertionError("ValueError attendue")


if __name__ == "__main__":
    test_nominal_table_et_indice()
    test_limite_absent()
    test_entrees_invalides()
    print("tests attendus OK")
