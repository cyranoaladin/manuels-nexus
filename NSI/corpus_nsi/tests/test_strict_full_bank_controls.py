from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_full_sequence_resource_matrix as matrix
import scripts.check_generated_template_residue as template_residue
import scripts.check_question_capacity_alignment as question_capacity
import scripts.check_support_pedagogical_depth as pedagogical_depth


def write(path: Path, content: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class StrictFullBankControlsTest(unittest.TestCase):
    def test_matrix_counts_registered_missing_without_treating_it_as_produced(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root / "03_progressions/fiches_cours/premiere/P10/P10_fiche_cours_reseaux_protocoles_paquets.md")
            write(root / "03_progressions/supports/premiere/P10/P10_TD_reseaux_protocoles_paquets.md")
            write(
                root / "missing_sequence_resources_register.md",
                "| Niveau | Séquence | Ressource manquante | Type | Priorité | Justification | Action prévue | Date cible | Responsable | Blocage pédagogique | Impact pédagogique |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| Première | P10 | P10_cours_reseaux_protocoles_paquets.md | cours | haute | absent | produire | 2026-07-15 | équipe NSI | oui | cours inexploitable |\n",
            )

            result = matrix.analyze_full_sequence_resource_matrix(root, sequences=["P10"])

            self.assertEqual(result.counts["produced"], 2)
            self.assertGreater(result.counts["missing_registered"], 0)
            self.assertTrue(result.errors)
            self.assertLess(result.completeness_percent, 100.0)

    def test_template_residue_rejects_generic_student_phrases(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            support = root / "03_progressions/supports/premiere/P06/P06_cours_tables_recherche_tri_fusion.md"
            write(
                support,
                "---\ndocument_type: cours\nstatus: needs_review\n---\n"
                "# Cours\n"
                "- Lire la situation sans modifier les données.\n"
                "- Appliquer une méthode explicitement liée aux capacités.\n"
                "On modifie une seule donnée pour tester le cas limite du chapitre.\n",
            )

            result = template_residue.analyze_generated_template_residue(root)

            self.assertEqual(len(result.errors), 3)

    def test_p05_question_capacity_alignment_rejects_filter_as_ptable01(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            evaluation = root / "03_progressions/supports/premiere/P05/P05_evaluation_tables_csv.md"
            write(
                evaluation,
                "### Question 2\n"
                "- Capacité officielle : P-TABLE-01.\n"
                "- Énoncé : filtrer les pays européens valides.\n",
            )

            result = question_capacity.analyze_question_capacity_alignment(root)

            self.assertTrue(any("Question 2" in error and "P-TABLE-02" in error for error in result.errors))

    def test_pedagogical_depth_rejects_structural_shell_without_concrete_content(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            course = root / "03_progressions/supports/premiere/P07/P07_cours_fonctions_tests_specifications.md"
            write(
                course,
                "---\ndocument_type: cours\nsequence_id: P07\nstatus: needs_review\n"
                "official_program:\n  capacities:\n    - P-LANG-01\n---\n"
                "# Cours\n"
                "## Exemple corrigé\n"
                "Exemple sans donnée concrète.\n"
                "## Erreurs fréquentes\n"
                "- erreur générique.\n",
            )

            result = pedagogical_depth.analyze_support_pedagogical_depth(root, files=[course])

            self.assertTrue(any("exemples concrets" in error for error in result.errors))
            self.assertTrue(any("cas limites" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
