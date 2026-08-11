"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "T02_starter_classes_objets"))
creer_compte = MODULE.creer_compte

def test_nominal() -> None:
    result = creer_compte(20)
    assert result.retirer(7) is None and result.solde == 13

def test_limite() -> None:
    result = creer_compte(0)
    assert result.solde == 0

def test_invalide() -> None:
    try:
        creer_compte(-1)
    except (ValueError, TypeError, IndexError):
        return
    raise AssertionError("exception attendue")

if __name__ == "__main__":
    test_nominal()
    test_limite()
    test_invalide()
    print("tests attendus OK")
