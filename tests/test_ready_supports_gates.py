from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_ready_supports_depth as ready_depth
import scripts.check_ready_supports_required_sections as ready_sections


class ReadySupportsGatesTest(unittest.TestCase):
    def test_ready_support_without_required_sections_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            support = root / "P01_cours_test.md"
            support.write_text("# Support\n\n## Objectifs\nTexte.\n", encoding="utf-8")

            result = ready_sections.analyze_ready_sections(root, prefixes=["P01"])

            self.assertTrue(any("section manquante" in error for error in result.errors))

    def test_ready_support_depth_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            support = root / "P01_cours_test.md"
            support.write_text("\n".join(f"Ligne {i}" for i in range(20)), encoding="utf-8")

            result = ready_depth.analyze_ready_depth(root, prefixes=["P01"])

            self.assertTrue(any("profondeur insuffisante" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
