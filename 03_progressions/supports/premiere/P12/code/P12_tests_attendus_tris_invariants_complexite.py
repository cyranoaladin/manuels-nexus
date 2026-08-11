"""Tests attendus TP P12. Statut pédagogique: needs_review."""
from __future__ import annotations
import importlib, os
MODULE = importlib.import_module(os.environ.get("TP_MODULE", "P12_starter_tris_invariants_complexite"))


def test_nominal_insertion_selection() -> None:
    assert MODULE.inserer_dans_partie_triee([17, 42, 23, 17, 9], 2) == [17, 23, 42, 17, 9]
    assert MODULE.indice_minimum_suffixe([42, 17, 23, 17, 9], 1) == 4
    assert MODULE.tri_selection([42, 17, 23, 17, 9]) == [9, 17, 17, 23, 42]


def test_limite_liste_vide_et_deja_triee() -> None:
    assert MODULE.tri_selection([]) == []
    assert MODULE.tri_selection([1, 2, 3]) == [1, 2, 3]


def test_invalide_entrees_absentes() -> None:
    for func, args in [(MODULE.tri_selection, (None,)), (MODULE.indice_minimum_suffixe, ([1], 2)), (MODULE.inserer_dans_partie_triee, ([1], -1))]:
        try:
            func(*args)
        except ValueError:
            continue
        raise AssertionError("ValueError attendue")

if __name__ == "__main__":
    test_nominal_insertion_selection(); test_limite_liste_vide_et_deja_triee(); test_invalide_entrees_absentes(); print("tests attendus OK")
