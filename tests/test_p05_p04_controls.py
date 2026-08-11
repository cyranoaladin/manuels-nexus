from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_course_sheet_exercise_answer_count as answer_count
import scripts.check_csv_numeric_fields_are_parseable as csv_numeric
import scripts.check_no_duplicate_capacity_lines as duplicate_capacity
import scripts.check_p04_key_consistency as p04_keys
import scripts.check_p05_expected_outputs_are_explicit as p05_outputs
import scripts.check_p05_pipeline_consistency as p05_pipeline
import scripts.check_t18_trace_table_quality as t18_trace
import scripts.check_paper_tp_contract as paper_tp
import scripts.check_p05_semantic_consistency as p05_semantic
import scripts.check_no_token_only_validation as token_only


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class P05P04ControlsTest(unittest.TestCase):
    def test_csv_numeric_rejects_unescaped_population_with_commas(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            support = root / "03_progressions/supports/premiere/P05/P05_td_tables_csv.md"
            write(
                support,
                "PAYS,CAPITALE,CONTINENT,POPULATION\n"
                "Espagne,Madrid,Europe,46,754,778\n"
                '`int(row["POPULATION"])` donne `46,754,778`.\n',
            )

            result = csv_numeric.analyze_csv_numeric_fields_are_parseable(root)

            self.assertTrue(any("trop de colonnes" in error for error in result.errors))
            self.assertTrue(any("non convertible" in error for error in result.errors))

    def test_p05_pipeline_requires_conversion_before_filtering_and_exact_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            support = root / "03_progressions/supports/premiere/P05/P05_td_tables_csv.md"
            write(
                support,
                "Filtrer l'Europe puis convertir la population. "
                "Résultat : deux lignes européennes sélectionnées.\n",
            )

            result = p05_pipeline.analyze_p05_pipeline_consistency(root)

            self.assertTrue(any("ordre logique" in error for error in result.errors))
            self.assertTrue(any('["Allemagne", "Albanie"]' in error for error in result.errors))

    def test_p05_expected_outputs_rejects_vague_phrases(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            support = root / "03_progressions/supports/premiere/P05/P05_corrige_tables_csv.md"
            write(
                support,
                "Réponse attendue : deux lignes européennes sélectionnées, "
                "ligne invalide isolée avant conversion, méthode visible, résultat correct.\n",
            )

            result = p05_outputs.analyze_p05_expected_outputs_are_explicit(root)

            self.assertGreaterEqual(len(result.errors), 3)

    def test_course_sheet_answer_count_rejects_missing_answer(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            sheet = root / "03_progressions/fiches_cours/premiere/P05/P05_fiche_cours_tables_csv_import_coherence.md"
            write(
                sheet,
                "# Fiche\n"
                "## Mini-exercices\n"
                "1. Exercice A\n"
                "2. Exercice B\n"
                "## Réponses rapides\n"
                "1. Réponse A\n",
            )

            result = answer_count.analyze_course_sheet_exercise_answer_count(root, files=[sheet])

            self.assertTrue(any("2 mini-exercices" in error and "1 réponses" in error for error in result.errors))

    def test_duplicate_capacity_lines_rejects_p05_duplicate_and_missing_ptable02(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            evaluation = root / "03_progressions/supports/premiere/P05/P05_evaluation_tables_csv.md"
            write(
                evaluation,
                "## Modalités de passation\n"
                "- Capacités évaluées :\n"
                "- P-TABLE-01\n"
                "- P-TABLE-01\n",
            )

            result = duplicate_capacity.analyze_no_duplicate_capacity_lines(root)

            self.assertTrue(any("P-TABLE-01" in error and "dupliquée" in error for error in result.errors))
            self.assertTrue(any("P-TABLE-02" in error for error in result.errors))

    def test_p04_key_consistency_rejects_temp_key_when_temperature_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            support = root / "03_progressions/supports/premiere/P04/P04_td_types_construits.md"
            write(support, 'stations = [{"nom": "A", "temp": 21}]\n')

            result = p04_keys.analyze_p04_key_consistency(root)

            self.assertTrue(any('"temp"' in error for error in result.errors))

    def test_t18_trace_requires_executable_trace_and_assets(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            trace = root / "03_progressions/supports/terminale/T18/T18_trace_boyer_moore.md"
            write(trace, "# Trace\n| Alignement | Fenêtre |\n|---|---|\n")

            result = t18_trace.analyze_t18_trace_table_quality(root)

            self.assertTrue(any("executable_trace" in error for error in result.errors))
            self.assertTrue(any("asset Python attendu absent" in error for error in result.errors))
            self.assertTrue(any("barème" in error.lower() for error in result.errors))

    def test_paper_tp_contract_rejects_incomplete_paper_tp(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            trace = root / "03_progressions/supports/premiere/P13/P13_tp_dichotomie_glouton_knn.md"
            write(
                trace,
                "---\n"
                "document_type: tp_papier\n"
                "sequence_id: P13\n"
                "---\n"
                "# Trace\n"
                "## Table du mauvais caractère\n",
            )

            result = paper_tp.analyze_paper_tp_contract(root)

            self.assertTrue(any("TP papier" in error for error in result.errors))
            self.assertTrue(any("barème" in error.lower() for error in result.errors))

    def test_p05_semantic_consistency_rejects_stale_body_contradictions(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            support = root / "03_progressions/supports/premiere/P05/P05_td_tables_csv.md"
            write(
                support,
                "# P05\n"
                "Brésil est conservé dans la sélection Europe.\n"
                "Andorre sert d'exemple de population.\n"
                "La ligne invalide est rejetée avant conversion.\n"
                "## Pipeline contrôlé P05\n"
                "1. Charger avec `csv.DictReader`.\n"
                "2. Convertir `POPULATION` avec `int(row[\"POPULATION\"])`.\n"
                "3. Séparer `valides` et `erreurs`.\n"
                "4. Filtrer les lignes valides par `CONTINENT`.\n"
                "5. Trier les lignes valides par `CONTINENT` puis `POPULATION`.\n"
                "- `valides = [\"Allemagne\", \"Albanie\", \"Brésil\"]`.\n"
                "- `Europe valide = [\"Allemagne\", \"Albanie\"]`.\n",
            )

            result = p05_semantic.analyze_p05_semantic_consistency(root)

            self.assertTrue(any("Brésil" in error for error in result.errors))
            self.assertTrue(any("Andorre" in error for error in result.errors))
            self.assertTrue(any("avant conversion" in error for error in result.errors))

    def test_no_token_only_validation_rejects_tail_pipeline_with_body_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            support = root / "03_progressions/supports/premiere/P05/P05_cours_tables_csv.md"
            write(
                support,
                "# P05\n"
                "On filtre d'abord l'Europe, puis on convertit les populations ensuite.\n"
                "## Pipeline contrôlé P05\n"
                "1. Charger avec `csv.DictReader`.\n"
                "2. Convertir `POPULATION` avec `int(row[\"POPULATION\"])`.\n"
                "3. Séparer `valides` et `erreurs`.\n"
                "4. Filtrer les lignes valides par `CONTINENT`.\n"
                "5. Trier les lignes valides par `CONTINENT` puis `POPULATION`.\n",
            )

            result = token_only.analyze_no_token_only_validation(root)

            self.assertTrue(any("bloc final" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
