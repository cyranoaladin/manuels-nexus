from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_no_coverage_from_sheets_only as coverage_guard


class NoCoverageFromSheetsOnlyTest(unittest.TestCase):
    def test_covered_capacity_with_only_fiche_proof_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "coverage.md").write_text(
                "# Couverture\n\n"
                "| niveau | rubrique officielle | contenu officiel | capacité officielle | preuve cours | preuve TD/TP | preuve évaluation | preuve corrigé | statut | blocker |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| premiere | Données | Bases | P-DATA-BASE-01 - représenter | 03_progressions/fiches_cours/premiere/P01/P01_fiche_cours_conversions.md | - | - | - | covered | - |\n",
                encoding="utf-8",
            )

            result = coverage_guard.analyze_no_coverage_from_sheets_only(root)

            self.assertTrue(any("preuve seulement fiche" in error for error in result.errors))

    def test_current_zero_covered_state_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "coverage.md").write_text(
                "# Couverture\n\n"
                "| niveau | rubrique officielle | contenu officiel | capacité officielle | preuve cours | preuve TD/TP | preuve évaluation | preuve corrigé | statut | blocker |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| premiere | Données | Bases | P-DATA-BASE-01 - représenter | 03_progressions/fiches_cours/premiere/P01/P01_fiche_cours_conversions.md | - | - | - | needs_review | ressources présentes mais statuts non validants |\n",
                encoding="utf-8",
            )

            result = coverage_guard.analyze_no_coverage_from_sheets_only(root)

            self.assertEqual(result.errors, [])

    def test_covered_capacity_requires_human_reviews_and_publication_decision(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "coverage.md").write_text(
                "# Couverture\n\n"
                "| niveau | rubrique officielle | contenu officiel | capacité officielle | preuve cours | preuve TD/TP | preuve évaluation | preuve corrigé | statut | blocker |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| premiere | Réseaux | Paquets | P-ARCH-02A - décrire un paquet | 03_progressions/fiches_cours/premiere/P10/P10_fiche_cours_reseaux_protocoles_paquets.md | 03_progressions/supports/premiere/P10/P10_TD_reseaux_protocoles_paquets.md | 03_progressions/supports/premiere/P10/P10_evaluation_reseaux_protocoles_paquets.md | 03_progressions/supports/premiere/P10/P10_TD_reseaux_protocoles_paquets.md#corrigé | covered | ressources présentes |\n",
                encoding="utf-8",
            )

            result = coverage_guard.analyze_no_coverage_from_sheets_only(root)

            self.assertTrue(any("revue pédagogique humaine" in error for error in result.errors))
            self.assertTrue(any("décision explicite de publication" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
