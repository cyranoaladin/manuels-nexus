from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_boyer_moore_trace_consistency as boyer_moore
import scripts.check_dynamic_programming_recurrence_consistency as dynamic_programming
import scripts.check_full_notional_resource_matrix as notional_matrix
import scripts.check_graph_algorithm_trace_consistency as graph_trace
import scripts.check_network_packet_trace_consistency as network_trace
import scripts.check_official_program_capacity_coverage_matrix as official_matrix
import scripts.check_session_operationalization_plan as session_plan
import scripts.check_sql_query_result_consistency as sql_consistency
import scripts.check_tree_bst_invariant_consistency as bst_consistency


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def support_frontmatter(sequence: str, document_type: str = "td") -> str:
    level = "premiere" if sequence.startswith("P") else "terminale"
    return (
        "---\n"
        f"title: \"{sequence} support\"\n"
        f"level: \"{level}\"\n"
        f"sequence_id: \"{sequence}\"\n"
        f"document_type: \"{document_type}\"\n"
        "status: \"needs_review\"\n"
        "---\n"
    )


class NotionalAndDisciplinaryControlsTest(unittest.TestCase):
    def test_sql_note_filter_rejects_linus_for_threshold_15(self) -> None:
        body = (
            "Données : `Eleve(1,Ada,T1), Eleve(2,Linus,T2) ; "
            "Note(10,1,NSI,17), Note(11,2,NSI,13)`.\n"
            "Consigne : filtrer note >= 15.\n"
            "Réponse attendue : JOIN -> Ada 17, Linus 13.\n"
        )

        self.assertFalse(sql_consistency.sql_block_is_consistent(body))

    def test_sql_note_filter_accepts_only_ada_for_threshold_15(self) -> None:
        body = (
            "Données : `Eleve(1,Ada,T1), Eleve(2,Linus,T2) ; "
            "Note(10,1,NSI,17), Note(11,2,NSI,13)`.\n"
            "Consigne : filtrer note >= 15.\n"
            "Réponse attendue : SELECT -> Ada 17.\n"
        )

        self.assertTrue(sql_consistency.sql_block_is_consistent(body))

    def test_sql_rejects_answer_labeled_with_another_operation(self) -> None:
        bad_filter = (
            "Consigne : filtrer les lignes pour lesquelles note >= 15.\n"
            "Réponse attendue : JOIN -> Ada 17.\n"
        )
        bad_join = (
            "Consigne : joindre Eleve et Note sur leur clé commune.\n"
            "Réponse attendue : UPDATE id_note=10 -> Ada 18.\n"
        )
        bad_update = (
            "Consigne : mettre à jour la note 10 puis vérifier la modification.\n"
            "Réponse attendue : DELETE WHERE id_note=11 retire Linus.\n"
        )

        self.assertFalse(sql_consistency.sql_block_is_consistent(bad_filter))
        self.assertFalse(sql_consistency.sql_block_is_consistent(bad_join))
        self.assertFalse(sql_consistency.sql_block_is_consistent(bad_update))

    def test_sql_update_and_delete_are_targeted(self) -> None:
        update = "UPDATE Note SET note = 18 WHERE id_note = 10; résultat : Ada 18."
        delete = "DELETE FROM Note WHERE id_note = 11; résultat : Linus retiré."

        self.assertTrue(sql_consistency.sql_block_is_consistent(update))
        self.assertTrue(sql_consistency.sql_block_is_consistent(delete))
        self.assertFalse(sql_consistency.sql_block_is_consistent("UPDATE Note SET note = 18;"))
        self.assertFalse(sql_consistency.sql_block_is_consistent("DELETE FROM Note;"))

    def test_sql_accepts_an_explicitly_analyzed_missing_where_counterexample(self) -> None:
        counterexample = (
            "Requête dangereuse à analyser :\n"
            "```sql\n"
            "UPDATE Note SET note = 10;\n"
            "```\n"
            "Sans WHERE, cette erreur modifie toutes les lignes.\n"
        )

        self.assertTrue(sql_consistency.sql_block_is_consistent(counterexample))

    def test_notional_matrix_rejects_two_notions_sharing_generic_support(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(
                root / "03_progressions/fiches_cours/terminale/T10/T10_fiche_cours_sql_select_where_join.md",
                "---\nsequence_id: T10\nnotion: \"SQL SELECT WHERE JOIN\"\nreadiness: operational\nstatus: needs_review\n---\n",
            )
            write(
                root / "03_progressions/fiches_cours/terminale/T10/T10_fiche_cours_sql_insert_update_delete.md",
                "---\nsequence_id: T10\nnotion: \"SQL INSERT UPDATE DELETE\"\nreadiness: operational\nstatus: needs_review\n---\n",
            )
            write(
                root / "03_progressions/supports/terminale/T10/T10_TD_sql_select_where_join.md",
                support_frontmatter("T10") + "SELECT WHERE JOIN uniquement.\n",
            )
            write(
                root / "03_progressions/supports/contracts/T10_contract.yml",
                "sequence: T10\nnotions:\n  - SQL SELECT WHERE JOIN\n",
            )

            result = notional_matrix.analyze_full_notional_resource_matrix(root)

            self.assertTrue(any("insert_update_delete" in error for error in result.errors))

    def test_official_capacity_matrix_rejects_missing_evaluation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(
                root / "00_programmes_officiels/programme_nsi_2019.yaml",
                "programmes:\n"
                "  premiere:\n"
                "    - id: P-TEST-01\n"
                "      theme: Test\n"
                "      capacite: capacité test\n",
            )
            write(
                root / "03_progressions/fiches_cours/premiere/P00/P00_fiche_cours_test.md",
                "---\nsequence_id: P00\nstatus: needs_review\nofficial_program:\n  capacities:\n    - P-TEST-01\n---\nP-TEST-01\n",
            )
            write(
                root / "03_progressions/supports/premiere/P00/P00_TD_test.md",
                support_frontmatter("P00") + "P-TEST-01\n",
            )

            result = official_matrix.analyze_official_program_capacity_coverage_matrix(root)

            self.assertTrue(any("P-TEST-01" in error and "évaluation" in error for error in result.errors))

    def test_graph_trace_rejects_invalid_reconstructed_path(self) -> None:
        bad = "Graphe non orienté : A-B, B-C. BFS avec file. Chemin reconstruit A -> C sans prédécesseur B."
        self.assertFalse(graph_trace.graph_block_is_consistent(bad))

    def test_bst_trace_rejects_unsorted_infix(self) -> None:
        bad = "ABR : racine 5, gauche 2, droite 8. Parcours infixe : 5, 2, 8."
        self.assertFalse(bst_consistency.tree_block_is_consistent(bad))

    def test_network_trace_rejects_wrong_ttl_decision(self) -> None:
        bad = "Paquet TTL=1. Route choisie : transmettre au prochain routeur avec TTL=1."
        self.assertFalse(network_trace.network_block_is_consistent(bad))

    def test_dynamic_programming_rejects_missing_initialization(self) -> None:
        bad = "État dp[i]. Relation dp[i] = max(dp[i-1], valeur). Résultat final 12."
        self.assertFalse(dynamic_programming.dp_block_is_consistent(bad))

    def test_boyer_moore_rejects_shift_without_bad_character_table(self) -> None:
        bad = "Motif ABA, texte CABA. Comparaison droite-gauche. Décalage 2. Indice trouvé 1."
        self.assertFalse(boyer_moore.boyer_moore_block_is_consistent(bad))

    def test_session_plan_reports_theoretical_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(
                root / "03_progressions/seances_premiere.md",
                "| Séance | Séquence | Statut | Document utilisé |\n"
                "|---|---|---|---|\n"
                "| P10-S1 | P10 | théorique | P10_cours.md |\n",
            )

            result = session_plan.analyze_session_operationalization_plan(root)

            self.assertEqual(result.theoretical_count, 1)
            self.assertTrue(result.theoretical_sessions)


if __name__ == "__main__":
    unittest.main()
