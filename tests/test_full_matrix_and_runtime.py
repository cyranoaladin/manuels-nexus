from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_audit_extracted_runtime_budget as runtime_budget
import scripts.check_full_sequence_resource_matrix as matrix


def write(path: Path, content: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class FullMatrixAndRuntimeTest(unittest.TestCase):
    def test_matrix_requires_unregistered_missing_resource(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root / "03_progressions/fiches_cours/premiere/P06/P06_fiche_cours_tables_recherche_tri_fusion.md")
            write(root / "03_progressions/supports/premiere/P06/P06_cours_tables_recherche_tri_fusion.md")
            write(root / "03_progressions/supports/contracts/P06_contract.yml")

            result = matrix.analyze_full_sequence_resource_matrix(root, sequences=["P06"])

            self.assertTrue(any("trace" in error for error in result.errors))

    def test_matrix_reports_registered_debt_without_treating_it_as_complete(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root / "03_progressions/fiches_cours/premiere/P10/P10_fiche_cours_reseaux_protocoles_paquets.md")
            write(root / "03_progressions/supports/premiere/P10/P10_TD_reseaux_protocoles_paquets.md")
            write(root / "03_progressions/supports/premiere/P10/P10_evaluation_reseaux_protocoles_paquets.md")
            write(
                root / "missing_sequence_resources_register.md",
                "| Niveau | Séquence | Ressource manquante | Type | Priorité | Justification | Action prévue | Date cible | Responsable | Blocage pédagogique |\n"
                "|---|---|---|---|---|---|---|---|---|---|\n"
                "| Première | P10 | P10_cours_reseaux_protocoles_paquets.md | cours | haute | lot ultérieur | produire | 2026-07-15 | équipe NSI | oui |\n"
                "| Première | P10 | P10_trace_reseaux_protocoles_paquets.md | trace | haute | lot ultérieur | produire | 2026-07-15 | équipe NSI | oui |\n"
                "| Première | P10 | P10_TP_reseaux_protocoles_paquets.md | tp | haute | lot ultérieur | produire | 2026-07-15 | équipe NSI | oui |\n"
                "| Première | P10 | P10_corrige_reseaux_protocoles_paquets.md | corrige | haute | lot ultérieur | produire | 2026-07-15 | équipe NSI | oui |\n"
                "| Première | P10 | P10_bareme_reseaux_protocoles_paquets.md | bareme | haute | lot ultérieur | produire | 2026-07-15 | équipe NSI | oui |\n"
                "| Première | P10 | P10_remediation_reseaux_protocoles_paquets.md | remediation | haute | lot ultérieur | produire | 2026-07-15 | équipe NSI | oui |\n"
                "| Première | P10 | P10_version_amenagee_reseaux_protocoles_paquets.md | version_amenagee | haute | lot ultérieur | produire | 2026-07-15 | équipe NSI | oui |\n"
                "| Première | P10 | P10_contract.yml | contrat | haute | lot ultérieur | produire | 2026-07-15 | équipe NSI | oui |\n",
            )

            result = matrix.analyze_full_sequence_resource_matrix(root, sequences=["P10"])

            self.assertTrue(result.errors)
            self.assertGreaterEqual(len(result.registered_missing), 1)
            self.assertLess(result.completeness_percent, 100.0)

    def test_runtime_budget_fails_when_total_exceeds_budget(self) -> None:
        commands = [runtime_budget.MeasuredCommand("fake", 181.0, 0)]
        result = runtime_budget.evaluate_runtime_budget(commands, total_budget=180.0)

        self.assertTrue(any("180" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
