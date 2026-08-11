from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_first_batch_tp_assets as tp_assets


class FirstBatchTpAssetsTest(unittest.TestCase):
    def test_missing_starter_code_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "P00" / "code").mkdir(parents=True)

            result = tp_assets.analyze_tp_assets(root, prefixes=["P00"])

            self.assertTrue(any("starter" in error for error in result.errors))

    def test_complete_assets_pass(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            code = root / "P00" / "code"
            code.mkdir(parents=True)
            (code / "P00_starter.py").write_text("def reponse():\n    return 1\n", encoding="utf-8")
            (code / "P00_tests_attendus.py").write_text("assert reponse() == 1\n", encoding="utf-8")
            (code / "P00_corrige_professeur.py").write_text("def reponse():\n    return 1\n", encoding="utf-8")

            result = tp_assets.analyze_tp_assets(root, prefixes=["P00"])

            self.assertEqual(result.errors, [])
            self.assertFalse((code / "__pycache__").exists())


if __name__ == "__main__":
    unittest.main()
