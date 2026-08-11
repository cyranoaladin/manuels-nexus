"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "T03_starter_piles_files_dictionnaires"))
jouer_operations = MODULE.jouer_operations

def test_nominal() -> None:
    result = jouer_operations([("push", "A"), ("push", "B"), ("pop", None)])
    assert result == ["B"]

def test_limite() -> None:
    result = jouer_operations([("push", "A"), ("pop", None)])
    assert result == ["A"]

def test_invalide() -> None:
    try:
        jouer_operations([("pop", None)])
    except (ValueError, TypeError, IndexError):
        return
    raise AssertionError("exception attendue")

if __name__ == "__main__":
    test_nominal()
    test_limite()
    test_invalide()
    print("tests attendus OK")
