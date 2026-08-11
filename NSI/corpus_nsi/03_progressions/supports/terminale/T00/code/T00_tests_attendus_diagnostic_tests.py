"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "T00_starter_diagnostic_tests"))
maximum_controle = MODULE.maximum_controle

def test_nominal() -> None:
    result = maximum_controle([3, 8, 2])
    assert result == 8

def test_limite() -> None:
    result = maximum_controle([-5, -2, -9])
    assert result == -2

def test_invalide() -> None:
    try:
        maximum_controle([])
    except (ValueError, TypeError, IndexError):
        return
    raise AssertionError("exception attendue")

if __name__ == "__main__":
    test_nominal()
    test_limite()
    test_invalide()
    print("tests attendus OK")
