from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_support_substance as substance


GENERIC_COURSE = """
# Cours

## Objectif O1
- Exemple corrigé 1 : 45 donne 101101.
- Étape : résoudre une variante contrôlée avec réponse cohérente.
- Étape : produire une production vérifiable.

## Objectif O2
- Exemple corrigé 2 : 45 donne 101101.
- Étape : résoudre une variante contrôlée avec réponse cohérente.
- Étape : produire une production vérifiable.

## Objectif O3
- Exemple corrigé 3 : 45 donne 101101.
- Étape : résoudre une variante contrôlée avec réponse cohérente.
- Étape : produire une production vérifiable.

## Objectif O4
- Exemple corrigé 4 : 45 donne 101101.
- Étape : résoudre une variante contrôlée avec réponse cohérente.
- Étape : produire une production vérifiable.
"""


DISTINCT_TD = """
# TD

## Exercices numérotés
### Exercice 1
- Objectif travaillé : O1.
- Donnée : convertir 13 en binaire.
### Exercice 2
- Objectif travaillé : O2.
- Donnée : convertir 42 en base 2 par divisions.
### Exercice 3
- Objectif travaillé : O3.
- Donnée : décoder 101101 en décimal.
### Exercice 4
- Objectif travaillé : O4.
- Donnée : convertir 1111 0000 en hexadécimal.
### Exercice 5
- Objectif travaillé : O1.
- Donnée : traiter le cas 0.
### Exercice 6
- Objectif travaillé : O2.
- Donnée : détecter le chiffre 2 dans une écriture binaire.
### Exercice 7
- Objectif travaillé : O3.
- Donnée : comparer 0b1010 et 0xA.
### Exercice 8
- Objectif travaillé : O4.
- Donnée : expliquer pourquoi 255 vaut FF en hexadécimal.
"""


class SupportSubstanceTest(unittest.TestCase):
    def test_generic_objective_blocks_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "P01_cours_test.md"
            path.write_text(GENERIC_COURSE, encoding="utf-8")

            errors = substance.analyze_support(path, "cours")

            self.assertTrue(any("objectifs trop répétitifs" in error for error in errors))
            self.assertTrue(any("formulation générique" in error for error in errors))

    def test_distinct_td_exercises_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "P01_td_test.md"
            path.write_text(DISTINCT_TD, encoding="utf-8")

            errors = substance.analyze_support(path, "td")

            self.assertFalse([error for error in errors if "exercices quasi identiques" in error])


if __name__ == "__main__":
    unittest.main()
