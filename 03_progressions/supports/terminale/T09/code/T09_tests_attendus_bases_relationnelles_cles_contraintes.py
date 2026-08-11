"""Tests attendus TP T09. Statut pédagogique: needs_review."""
from __future__ import annotations
import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "T09_starter_bases_relationnelles_cles_contraintes"))
ELEVES = [{"id_eleve": 1, "nom": "Ada"}, {"id_eleve": 2, "nom": "Linus"}]
NOTES = [{"id_note": 10, "id_eleve": 1, "note": 17}, {"id_note": 11, "id_eleve": 2, "note": 13}]


def test_nominal_contraintes_relationnelles() -> None:
    assert MODULE.cles_primaires_uniques(ELEVES, "id_eleve") is True
    assert MODULE.references_valides(NOTES, ELEVES, "id_eleve", "id_eleve") is True
    assert MODULE.violations_domaine(NOTES, "note", 0, 20) == []


def test_limites_doublon_reference_absente() -> None:
    assert MODULE.cles_primaires_uniques(ELEVES + [{"id_eleve": 1, "nom": "Grace"}], "id_eleve") is False
    assert MODULE.references_valides([{"id_note": 12, "id_eleve": 99, "note": 10}], ELEVES, "id_eleve", "id_eleve") is False


def test_entrees_invalides_domaine() -> None:
    erreurs = MODULE.violations_domaine([{"note": -1}, {"note": 21}, {"note": 12}], "note", 0, 20)
    assert erreurs == [{"note": -1}, {"note": 21}]


if __name__ == "__main__":
    test_nominal_contraintes_relationnelles()
    test_limites_doublon_reference_absente()
    test_entrees_invalides_domaine()
    print("tests attendus OK")
