"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "T04_starter_recursivite"))
factorielle = MODULE.factorielle

def test_nominal() -> None:
    result = factorielle(5)
    assert result == 120

def test_limite() -> None:
    result = factorielle(0)
    assert result == 1

def test_invalide() -> None:
    try:
        factorielle(-1)
    except (ValueError, TypeError, IndexError):
        return
    raise AssertionError("exception attendue")

if __name__ == "__main__":
    test_nominal()
    test_limite()
    test_invalide()
    print("tests attendus OK")
