from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_no_line_padding as padding


class LinePaddingTest(unittest.TestCase):
    def test_repeated_objective_bodies_are_rejected(self) -> None:
        text = """
## Objectif O1
- Étape 1 : lire la donnée.
- Étape 2 : appliquer la méthode.
- Étape 3 : vérifier le résultat.
## Objectif O2
- Étape 1 : lire la donnée.
- Étape 2 : appliquer la méthode.
- Étape 3 : vérifier le résultat.
"""

        errors = padding.analyze_text("P01_cours_test.md", text)

        self.assertTrue(any("O1-O4 presque identiques" in error for error in errors))

    def test_sentence_repeated_across_many_supports_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repeated = "La trace doit pouvoir être relue sans support oral supplémentaire."
            for index in range(6):
                (root / f"P0{index}_cours_test.md").write_text(repeated + "\n", encoding="utf-8")

            result = padding.analyze_padding(root)

            self.assertTrue(any("phrase répétée dans plus de 5 supports" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
