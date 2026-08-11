"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "T05_starter_arbres_binaires"))
parcours_infixe = MODULE.parcours_infixe

def test_nominal() -> None:
    result = parcours_infixe((4, (2, None, None), (7, None, None)))
    assert result == [2, 4, 7]

def test_limite() -> None:
    result = parcours_infixe(None)
    assert result == []

def test_invalide() -> None:
    try:
        parcours_infixe((4, None))
    except (ValueError, TypeError, IndexError):
        return
    raise AssertionError("exception attendue")

if __name__ == "__main__":
    test_nominal()
    test_limite()
    test_invalide()
    print("tests attendus OK")
