"""Tests attendus TP T16. Statut pédagogique: needs_review."""
from __future__ import annotations
import importlib, os
MODULE = importlib.import_module(os.environ.get("TP_MODULE", "T16_starter_diviser_pour_regner_tri_fusion"))


def test_nominal_fusion_tri() -> None:
    assert MODULE.fusionner([1, 4], [2, 3, 5]) == [1, 2, 3, 4, 5]
    assert MODULE.tri_fusion([5, 1, 4, 1]) == [1, 1, 4, 5]


def test_limite_vide_un_element_niveaux() -> None:
    assert MODULE.tri_fusion([]) == []
    assert MODULE.tri_fusion([7]) == [7]
    assert MODULE.nombre_niveaux(8) == 3


def test_invalide_liste_absente() -> None:
    try:
        MODULE.tri_fusion(None)
    except ValueError:
        return
    raise AssertionError("ValueError attendue")

if __name__ == "__main__":
    test_nominal_fusion_tri(); test_limite_vide_un_element_niveaux(); test_invalide_liste_absente(); print("tests attendus OK")
