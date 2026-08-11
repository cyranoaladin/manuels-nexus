from __future__ import annotations

import importlib
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_audit_extracted_runtime_budget as runtime_budget
import scripts.check_capacity_status_ladder as capacity_ladder
import scripts.check_course_explanatory_quality as course_quality
import scripts.check_human_review_register as human_review
import scripts.check_tp_executable_opportunity as tp_opportunity


def write(path: Path, content: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class FinalQualityHardeningTest(unittest.TestCase):
    def test_capacity_ladder_rejects_documented_without_practice_or_assessment(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(
                root / "00_programmes_officiels/programme_nsi_2019.yaml",
                "programmes:\n"
                "  premiere:\n"
                "    - id: P-TEST-01\n"
                "      theme: Test\n"
                "      capacite: tester une capacité\n",
            )
            write(root / "03_progressions/fiches_cours/premiere/P00/P00_fiche_cours_test.md", "P-TEST-01\n")

            result = capacity_ladder.analyze_capacity_status_ladder(root)

            self.assertEqual(result.rows["P-TEST-01"]["documented"], "oui")
            self.assertEqual(result.rows["P-TEST-01"]["practiced"], "non")
            self.assertEqual(result.rows["P-TEST-01"]["assessed"], "non")
            self.assertTrue(any("practiced=non" in error for error in result.errors))
            self.assertTrue(any("assessed=non" in error for error in result.errors))

    def test_capacity_ladder_reports_session_link_without_covering(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(
                root / "00_programmes_officiels/programme_nsi_2019.yaml",
                "programmes:\n"
                "  premiere:\n"
                "    - id: P-TEST-01\n"
                "      theme: Test\n"
                "      capacite: tester une capacité\n",
            )
            write(root / "03_progressions/fiches_cours/premiere/P00/P00_fiche_cours_test.md", "P-TEST-01\n")
            write(root / "03_progressions/supports/premiere/P00/P00_TD_test.md", "P-TEST-01\n")
            write(root / "03_progressions/supports/premiere/P00/P00_evaluation_test.md", "P-TEST-01\n")
            write(
                root / "03_progressions/seances_premiere.md",
                "### Séance P00-S1\n"
                "- Capacité officielle : P-TEST-01\n"
                "- Document utilisé : P00_TD_test.md, P00_evaluation_test.md\n",
            )

            result = capacity_ladder.analyze_capacity_status_ladder(root)

            self.assertEqual(result.rows["P-TEST-01"]["linked_to_session"], "oui")
            self.assertEqual(result.rows["P-TEST-01"]["covered"], "non")
            self.assertFalse(result.errors)

    def test_course_quality_rejects_course_with_only_two_examples(self) -> None:
        text = (
            "---\ndocument_type: cours\nstatus: needs_review\n---\n"
            "# Cours\n"
            "## Situation-problème\n"
            "Une explication conceptuelle substantielle relie la notion à P-TEST-01 avec vocabulaire disciplinaire.\n"
            "## À savoir\nDéfinition précise et rôle.\n"
            "## Méthodes\nSavoir-faire et méthode distingués.\n"
            "### Exemple corrigé 1\nDonnée 1, méthode, résultat 1.\n"
            "### Exemple corrigé 2\nDonnée 2, méthode, résultat 2.\n"
            "## Erreurs fréquentes\n- On confond A et B.\n- On oublie le cas vide.\n"
            "## Cas limites\n- cas vide.\n- cas invalide.\n"
            "## À retenir\nSynthèse finale.\n"
        )

        errors = course_quality.course_quality_errors(text, "cours_test.md")

        self.assertTrue(any("trois exemples" in error for error in errors))

    def test_tp_opportunity_flags_executable_paper_tp_without_assets(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            tp = root / "03_progressions/supports/terminale/T10/T10_tp_sql_select_where_join.md"
            write(
                tp,
                "---\ndocument_type: tp_papier\nstatus: needs_review\n---\n"
                "# TP SQL papier\n"
                "Ce TP papier porte sur SQL, SELECT, JOIN et tables.\n"
                "Aucune ressource Python ou SQLite n'est fournie.\n",
            )

            result = tp_opportunity.analyze_tp_executable_opportunity(root)

            self.assertTrue(result.opportunities)
            self.assertIn("T10", result.opportunities[0])

    def test_human_review_register_requires_one_pending_row_per_major_resource(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(
                root / "manifest.csv",
                "path,statut,source\n"
                "03_progressions/supports/premiere/P00/P00_cours_test.md,needs_review,generated\n",
            )
            write(root / "03_progressions/supports/premiere/P00/P00_cours_test.md", "---\nstatus: needs_review\n---\n")

            result = human_review.analyze_human_review_register(root)

            self.assertTrue(any("human_review_register.csv absent" in error for error in result.errors))

    def test_human_review_register_rejects_validation_without_reviewer_date(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            resource = "03_progressions/supports/premiere/P00/P00_cours_test.md"
            write(root / resource, "---\nstatus: needs_review\n---\n")
            write(root / "manifest.csv", f"path,statut,source\n{resource},needs_review,generated\n")
            register = root / "human_review_register.csv"
            register.write_text(
                "ressource,niveau,sequence,notion,reviewer,date,science_status,pedagogy_status,"
                "accessibility_status,technical_status,decision,blockers\n"
                f"{resource},premiere,P00,test,,,validated,validated,pending,pending,needs_review,\n",
                encoding="utf-8",
            )

            result = human_review.analyze_human_review_register(root)

            self.assertTrue(any("sans reviewer/date" in error for error in result.errors))

    def test_runtime_budget_requires_source_archive_extraction(self) -> None:
        self.assertTrue(runtime_budget.uses_source_archive_extraction(runtime_budget.analyze_audit_extracted_runtime_budget))

    def test_runtime_budget_runs_in_extracted_source_mode_without_archive(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(
                root / "Makefile",
                "audit-extracted-source:\n"
                "\tpython -c \"import os; assert 'NSI_DOCUMENTS_DRIVE_ROOT' not in os.environ; print('portable')\"\n",
            )

            result = runtime_budget.analyze_audit_extracted_runtime_budget(root)

            self.assertEqual(result.mode, "source_clean_extracted")
            self.assertFalse(result.errors)
            self.assertEqual(result.commands[0].returncode, 0)

    def test_tp_opportunity_strict_mode_blocks_above_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for index in range(9):
                prefix = f"P{index:02d}"
                write(
                    root / f"03_progressions/supports/premiere/{prefix}/{prefix}_tp_test.md",
                    "---\ndocument_type: tp_papier\nstatus: needs_review\n---\n"
                    "# TP papier\n"
                    "Ce TP papier porte sur fonction, test, algorithme et Python sans assets exécutables.\n",
                )

            result = tp_opportunity.analyze_tp_executable_opportunity(
                root,
                strict=True,
                max_opportunities=8,
            )

            self.assertEqual(len(result.opportunities), 9)
            self.assertTrue(any("plus de 8" in error for error in result.errors))

    def test_session_classroom_operationality_distinguishes_linked_from_ready(self) -> None:
        module = importlib.import_module("check_session_classroom_operationality")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(
                root / "03_progressions/seances_premiere.md",
                "### Séance P00-S1\n"
                "- Objectif : comprendre P-TEST-01\n"
                "- Document utilisé : P00_cours_test.md\n",
            )
            write(
                root / "03_progressions/supports/premiere/P00/P00_cours_test.md",
                "---\nstatus: needs_review\n---\nP-TEST-01\n",
            )

            result = module.analyze_session_classroom_operationality(root)

            self.assertEqual(result.linked_count, 1)
            self.assertEqual(result.classroom_ready_count, 0)
            self.assertEqual(result.human_review_pending_count, 1)

    def test_human_review_wave_plan_requires_twenty_existing_pending_resources(self) -> None:
        module = importlib.import_module("check_human_review_wave_plan")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root / "human_review_wave_1_plan.md", "# Plan\n- `03_progressions/supports/terminale/T10/missing.md` | T10 | priorité haute | pending\n")

            result = module.analyze_human_review_wave_plan(root)

            self.assertTrue(any("20 ressources" in error for error in result.errors))
            self.assertTrue(any("absente" in error for error in result.errors))

    def test_drive_action_plan_requires_complete_release_fields(self) -> None:
        module = importlib.import_module("check_drive_action_plan_completeness")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(
                root / "drive_inventory.csv",
                "name,decision\n"
                "missing.pdf,missing_local_copy\n",
            )
            write(
                root / "drive_remaining_action_plan.md",
                "| Ressource | Décision | Action |\n|---|---|---|\n| missing.pdf | missing_local_copy | retrouver |\n",
            )

            result = module.analyze_drive_action_plan(root)

            self.assertTrue(any("responsable" in error for error in result.errors))
            self.assertTrue(any("date cible" in error for error in result.errors))

    def test_sequence_pedagogical_coherence_rejects_unprepared_evaluation(self) -> None:
        module = importlib.import_module("check_sequence_pedagogical_coherence")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            base = root / "03_progressions/supports/premiere/P00"
            write(base / "P00_cours_test.md", "---\nstatus: needs_review\n---\nP-TEST-01\nnotion A\n")
            write(base / "P00_TD_test.md", "---\nstatus: needs_review\n---\nP-TEST-01\nnotion A\n")
            write(base / "P00_tp_test.md", "---\nstatus: needs_review\n---\nP-TEST-01\nnotion A\n")
            write(base / "P00_evaluation_test.md", "---\nstatus: needs_review\n---\nP-TEST-02\nnotion B\n")
            write(base / "P00_remediation_test.md", "---\nstatus: needs_review\n---\nerreur fréquente notion A\n")
            write(base / "P00_version_amenagee_test.md", "---\nstatus: needs_review\n---\nP-TEST-01\n")

            result = module.analyze_sequence_pedagogical_coherence(root)

            self.assertTrue(any("P00" in error and "évaluation" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
