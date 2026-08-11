"""Tests attendus TP T01. Statut pédagogique: needs_review."""

from __future__ import annotations

import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "T01_starter_interfaces_structures"))
Pile = MODULE.Pile
File = MODULE.File

def test_nominal() -> None:
    pile = Pile()
    pile.empiler("A")
    pile.empiler("B")
    assert pile.sommet() == "B"
    assert pile.depiler() == "B"
    assert pile.depiler() == "A"
    assert pile.est_vide()

    file = File()
    file.enfiler("A")
    file.enfiler("B")
    assert file.premier() == "A"
    assert file.defiler() == "A"
    assert file.defiler() == "B"
    assert file.est_vide()

def test_limite() -> None:
    pile = Pile()
    try:
        pile.depiler()
    except (IndexError, ValueError):
        return
    else:
        raise AssertionError("depiler sur pile vide doit lever une erreur")

def test_invalide() -> None:
    file = File()
    try:
        file.premier()
    except (ValueError, TypeError, IndexError):
        return
    raise AssertionError("exception attendue")

if __name__ == "__main__":
    test_nominal()
    test_limite()
    test_invalide()
    print("tests attendus OK")
