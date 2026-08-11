from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_sequence_contracts as contracts


class SequenceContractsTest(unittest.TestCase):
    def test_missing_contract_item_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            contract_dir = root / "contracts"
            support_dir = root / "P01"
            contract_dir.mkdir()
            support_dir.mkdir()
            (contract_dir / "P01_contract.yml").write_text(
                "sequence: P01\n"
                "must_include:\n"
                "  - conversion décimal vers binaire par divisions successives\n"
                "must_not:\n"
                "  - hardcoder 101101 comme preuve de conversion\n",
                encoding="utf-8",
            )
            (support_dir / "P01_cours_test.md").write_text("cours sans item attendu", encoding="utf-8")

            result = contracts.analyze_contracts(root, contract_dir=contract_dir, prefixes=["P01"])

            self.assertTrue(any("élément obligatoire absent" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
