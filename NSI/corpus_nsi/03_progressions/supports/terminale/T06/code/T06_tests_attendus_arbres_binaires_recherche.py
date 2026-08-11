"""Tests attendus TP T06. Statut pédagogique: needs_review."""
from __future__ import annotations
import importlib, os
MODULE = importlib.import_module(os.environ.get("TP_MODULE", "T06_starter_arbres_binaires_recherche"))


def construire():
    arbre = None
    for valeur in [8, 3, 10, 1, 6]:
        arbre = MODULE.inserer_abr(arbre, valeur)
    return arbre


def test_nominal_insertion_recherche_infixe() -> None:
    arbre = construire()
    assert MODULE.parcours_infixe(arbre) == [1, 3, 6, 8, 10]
    assert MODULE.rechercher_abr(arbre, 6) is True
    assert MODULE.rechercher_abr(arbre, 7) is False


def test_limite_arbre_vide_et_doublon() -> None:
    assert MODULE.parcours_infixe(None) == []
    arbre = construire()
    MODULE.inserer_abr(arbre, 6)
    assert MODULE.parcours_infixe(arbre) == [1, 3, 6, 8, 10]


def test_invalide_valeur_absente() -> None:
    for func, args in [(MODULE.inserer_abr, (None, None)), (MODULE.rechercher_abr, (None, None))]:
        try:
            func(*args)
        except ValueError:
            continue
        raise AssertionError("ValueError attendue")

if __name__ == "__main__":
    test_nominal_insertion_recherche_infixe(); test_limite_arbre_vide_et_doublon(); test_invalide_valeur_absente(); print("tests attendus OK")
