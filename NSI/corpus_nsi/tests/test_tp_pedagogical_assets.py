from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_tp_pedagogical_assets as tp_pedagogy


class TpPedagogicalAssetsTest(unittest.TestCase):
    def test_boundary_assertions_are_recognized_without_legacy_keywords(self) -> None:
        tests = """
def test_frontiere_incluse():
    assert calculer(18) == 18

def test_resultat_vide():
    assert rechercher(20) == []

def test_etat_impossible():
    assert reconstruire(7) is None
"""

        errors = tp_pedagogy.tests_are_substantive(tests)

        self.assertNotIn("tests insuffisants: cas limite absent", errors)

    def test_decorative_boundary_word_does_not_count_as_a_boundary_case(self) -> None:
        tests = """
def test_nominal_un():
    # limite décorative : aucun scénario frontière n'est exécuté.
    assert calculer(1) == 1

def test_nominal_deux():
    assert calculer(2) == 2

def test_nominal_trois():
    assert calculer(3) == 3
"""

        errors = tp_pedagogy.tests_are_substantive(tests)

        self.assertIn("tests insuffisants: cas limite absent", errors)

    def test_hardcoded_starter_and_constant_test_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            code = Path(raw) / "P01" / "code"
            code.mkdir(parents=True)
            (code / "P01_starter_demo.py").write_text(
                "def convert_base(value):\n    return '101101'\n",
                encoding="utf-8",
            )
            (code / "P01_corrige_professeur_demo.py").write_text(
                "def convert_base(value):\n    return '101101'\n",
                encoding="utf-8",
            )
            (code / "P01_tests_attendus_demo.py").write_text(
                "from P01_starter_demo import convert_base\n\n"
                "def test_nominal():\n    assert convert_base(45) == '101101'\n",
                encoding="utf-8",
            )

            result = tp_pedagogy.analyze_tp_pedagogy(Path(raw), prefixes=["P01"])

            self.assertTrue(any("starter hardcodé" in error for error in result.errors))
            self.assertTrue(any("tests insuffisants" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
