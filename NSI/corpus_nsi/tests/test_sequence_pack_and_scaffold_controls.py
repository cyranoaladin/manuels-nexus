from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_corrected_answers_are_concrete as concrete_answers
import scripts.check_no_generic_scaffold_overuse as scaffold
import scripts.check_sequence_pack_consistency as pack_consistency
import scripts.check_sequence_capacity_alignment as capacity_alignment
import scripts.check_student_supports_no_scaffold_language as student_scaffold


def write_support(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
title: "{path.stem}"
level: "premiere"
sequence_id: "P05"
document_type: "td"
status: "needs_review"
---
{body}
""",
        encoding="utf-8",
    )


class SequencePackAndScaffoldControlsTest(unittest.TestCase):
    def test_sequence_pack_rejects_contradictory_csv_scenarios(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            base = root / "03_progressions" / "supports" / "premiere" / "P05"
            write_support(
                base / "P05_td_tables_csv.md",
                "# TD\nLe fichier `pays_monde.csv` contient `PAYS,CAPITALE,CONTINENT,POPULATION`.\n",
            )
            write_support(
                base / "P05_trace_tables_csv.md",
                "# Trace\nOn part de `ville,temp` puis `Tunis,24` pour calculer une moyenne.\n",
            )

            result = pack_consistency.analyze_sequence_pack_consistency(root, prefixes=["P05"])

            self.assertTrue(any("ville,temp" in error and "pays_monde" in error for error in result.errors))

    def test_sequence_pack_accepts_pays_monde_thread_across_pack(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            base = root / "03_progressions" / "supports" / "premiere" / "P05"
            for kind in ["cours", "trace", "td", "tp", "corrige", "bareme", "evaluation", "remediation", "version_amenagee"]:
                write_support(
                    base / f"P05_{kind}_tables_csv.md",
                    "# Support\n"
                    "Fil conducteur : `pays_monde.csv` avec champs `PAYS`, `CAPITALE`, `CONTINENT`, `POPULATION`.\n"
                    "On utilise `csv.reader`, `csv.DictReader`, un filtrage par `CONTINENT`, "
                    "la conversion `int(row[\"POPULATION\"])`, un tri numérique, un tri lexicographique, "
                    "un tri par continent puis population et une ligne invalide.\n"
                    "Capacités : P-TABLE-01 et P-TABLE-02.\n",
                )

            result = pack_consistency.analyze_sequence_pack_consistency(root, prefixes=["P05"])

            self.assertEqual([], result.errors)

    def test_sequence_pack_rejects_pays_monde_file_missing_required_thread_terms(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            support = root / "03_progressions" / "supports" / "premiere" / "P05" / "P05_td_tables_csv.md"
            write_support(
                support,
                "# TD\n"
                "On utilise `pays_monde.csv` avec `PAYS`, `CAPITALE`, `CONTINENT`, `POPULATION`.\n"
                "On filtre des lignes mais sans `csv.DictReader`, sans tri lexicographique et sans P-TABLE-02.\n",
            )

            result = pack_consistency.analyze_sequence_pack_consistency(root, prefixes=["P05"])

            self.assertTrue(any("fil pays_monde incomplet" in error for error in result.errors))

    def test_student_scaffold_language_rejects_generic_td_phrase(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            support = root / "03_progressions" / "supports" / "premiere" / "P05" / "P05_td_tables_csv.md"
            write_support(
                support,
                "# TD\n"
                "### Exercice 1\n"
                "- Production attendue : une réponse structurée en donnée, méthode, résultat et contrôle.\n",
            )

            result = student_scaffold.analyze_student_supports_no_scaffold_language(root)

            self.assertTrue(any("P05_td_tables_csv.md" in error for error in result.errors))

    def test_student_scaffold_language_allows_teacher_guide(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            guide = root / "03_progressions" / "supports" / "premiere" / "P05" / "P05_guide_professeur_tables_csv.md"
            write_support(
                guide,
                "# Guide\n"
                "Phrase modèle interne : réponse structurée en donnée, méthode, résultat et contrôle.\n",
            )

            result = student_scaffold.analyze_student_supports_no_scaffold_language(root)

            self.assertEqual([], result.errors)

    def test_sequence_capacity_alignment_requires_p05_capacities_in_each_pack_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            base = root / "03_progressions" / "supports" / "premiere" / "P05"
            write_support(
                base / "P05_td_tables_csv.md",
                "# TD\npays_monde.csv ; P-TABLE-01 seulement.\n",
            )

            result = capacity_alignment.analyze_sequence_capacity_alignment(root, prefixes=["P05"])

            self.assertTrue(any("P-TABLE-02" in error for error in result.errors))

    def test_generic_scaffold_rejects_massive_phrase_without_concrete_result(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            base = root / "03_progressions" / "supports" / "terminale" / "T17"
            for index in range(6):
                write_support(
                    base / f"T17_TD_demo_{index}.md",
                    "# TD\n"
                    "### Exercice 1\n"
                    "- Production attendue : une réponse structurée en donnée, méthode, résultat et contrôle.\n"
                    "- Critère de réussite : un pair peut vérifier le résultat à partir de la donnée.\n",
                )

            result = scaffold.analyze_no_generic_scaffold_overuse(root)

            self.assertTrue(any("apparaît 6 fois" in error for error in result.errors))

    def test_generic_scaffold_allows_phrase_with_local_disciplinary_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            base = root / "03_progressions" / "supports" / "terminale" / "T17"
            for index in range(6):
                write_support(
                    base / f"T17_TD_demo_{index}.md",
                    "# TD\n"
                    "### Exercice 1\n"
                    "- Données : valeurs [2, 5, 9], capacité 7.\n"
                    "- Production attendue : une réponse structurée en donnée, méthode, résultat et contrôle.\n"
                    "- Résultat concret : état `dp[7] = 12`, trace `[0, 2, 5, 7, 10, 12]`, complexité `O(n*C)`.\n",
                )

            result = scaffold.analyze_no_generic_scaffold_overuse(root)

            self.assertEqual([], result.errors)

    def test_corrected_answers_rejects_correction_without_concrete_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            support = root / "03_progressions" / "supports" / "premiere" / "P10" / "P10_corrige_demo.md"
            write_support(
                support,
                "# Corrigé\n"
                "### Corrigé exercice 1\n"
                "La réponse est correcte si la démarche est claire et complète.\n",
            )

            result = concrete_answers.analyze_corrected_answers(root, files=[support])

            self.assertTrue(any("sans résultat disciplinaire concret" in error for error in result.errors))

    def test_corrected_answers_accepts_trace_and_result(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            support = root / "03_progressions" / "supports" / "terminale" / "T18" / "T18_corrige_demo.md"
            write_support(
                support,
                "# Corrigé\n"
                "### Corrigé exercice 1\n"
                "Motif `ABA`, texte `CABAABABA`. Table mauvais caractère : A -> 2, B -> 1. "
                "Trace : alignement 0, mismatch B, décalage 1 ; alignement 1, occurrence trouvée. "
                "Résultat attendu : indice 1.\n",
            )

            result = concrete_answers.analyze_corrected_answers(root, files=[support])

            self.assertEqual([], result.errors)


if __name__ == "__main__":
    unittest.main()
