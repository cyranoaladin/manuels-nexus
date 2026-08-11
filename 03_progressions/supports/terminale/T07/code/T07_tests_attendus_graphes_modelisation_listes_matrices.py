"""Tests attendus TP T07. Statut pédagogique: needs_review."""
from __future__ import annotations
import importlib, os
MODULE = importlib.import_module(os.environ.get("TP_MODULE", "T07_starter_graphes_modelisation_listes_matrices"))
ARETES = [("A", "B"), ("A", "C"), ("B", "D")]


def test_nominal_liste_matrice_degre() -> None:
    graphe = MODULE.liste_adjacence(ARETES)
    assert graphe["A"] == ["B", "C"]
    assert graphe["B"] == ["A", "D"]
    assert MODULE.degre(graphe, "A") == 2
    assert MODULE.matrice_adjacence(["A", "B", "C", "D"], ARETES)[0] == [0, 1, 1, 0]


def test_limite_oriente() -> None:
    graphe = MODULE.liste_adjacence([("A", "B")], oriente=True)
    assert graphe["A"] == ["B"] and graphe["B"] == []


def test_invalide_sommet_absent() -> None:
    try:
        MODULE.degre({"A": []}, "Z")
    except ValueError:
        return
    raise AssertionError("ValueError attendue")

if __name__ == "__main__":
    test_nominal_liste_matrice_degre(); test_limite_oriente(); test_invalide_sommet_absent(); print("tests attendus OK")
