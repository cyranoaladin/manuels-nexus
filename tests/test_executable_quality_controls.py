from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_boyer_moore_trace_consistency as boyer_moore
import scripts.check_capacity_status_ladder as capacity_ladder
import scripts.check_course_explanatory_quality as course_quality
import scripts.check_dynamic_programming_recurrence_consistency as dynamic_programming
import scripts.check_graph_algorithm_trace_consistency as graph_trace
import scripts.check_network_packet_trace_consistency as network_trace
import scripts.check_paper_tp_justification as paper_tp
import scripts.check_session_to_resource_alignment as session_alignment
import scripts.check_sql_query_result_consistency as sql_consistency
import scripts.check_tree_bst_invariant_consistency as bst_consistency


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class ExecutableQualityControlsTest(unittest.TestCase):
    def test_sql_executes_select_and_rejects_wrong_announced_result(self) -> None:
        query = (
            "SELECT Eleve.nom, Note.note FROM Eleve "
            "JOIN Note ON Eleve.id_eleve = Note.id_eleve "
            "WHERE note >= 15 ORDER BY Note.note DESC"
        )
        self.assertEqual(
            sql_consistency.execute_sql_query(query),
            [("Grace", 18), ("Ada", 17), ("Grace", 15)],
        )

        bad_block = (
            f"Requête : `{query}`\n"
            "Résultat attendu :\n"
            "| nom | note |\n"
            "|---|---|\n"
            "| Ada | 17 |\n"
            "| Linus | 13 |\n"
        )
        self.assertFalse(sql_consistency.sql_block_is_consistent(bad_block))

    def test_sql_update_delete_simulation_is_targeted(self) -> None:
        update = "UPDATE Note SET note = 18 WHERE id_note = 10"
        delete = "DELETE FROM Note WHERE id_note = 11"

        self.assertEqual(
            sql_consistency.execute_sql_update_summary(update),
            {10: 18, 11: 13, 12: 15, 13: 14, 14: 9, 15: 18},
        )
        self.assertEqual(
            sql_consistency.execute_sql_delete_summary(delete),
            {10: 17, 12: 15, 13: 14, 14: 9, 15: 18},
        )

    def test_sql_insert_simulation_returns_inserted_row(self) -> None:
        insert = (
            "INSERT INTO Note(id_note, id_eleve, matiere, note) "
            "VALUES (16, 4, 'MATHS', 12)"
        )

        self.assertEqual(
            sql_consistency.execute_sql_inserted_row(insert, 16),
            (16, 4, "MATHS", 12),
        )

    def test_graph_bfs_predecessors_and_path_are_executable(self) -> None:
        graph = graph_trace.parse_undirected_edges("Graphe non orienté : A-B, B-C, A-D.")
        self.assertEqual(graph_trace.bfs_order(graph, "A"), ["A", "B", "D", "C"])
        self.assertEqual(graph_trace.reconstruct_path({"B": "A", "D": "A", "C": "B"}, "A", "C"), ["A", "B", "C"])
        self.assertFalse(graph_trace.graph_block_is_consistent(
            "Graphe non orienté : A-B, B-C. BFS avec file. Prédécesseurs : B <- A, C <- A."
        ))

    def test_bst_reconstruction_checks_infix_and_search(self) -> None:
        root = bst_consistency.build_bst([5, 3, 8, 4])
        self.assertEqual(bst_consistency.inorder(root), [3, 4, 5, 8])
        self.assertTrue(bst_consistency.search_bst(root, 4))
        self.assertFalse(bst_consistency.search_bst(root, 7))
        self.assertFalse(bst_consistency.tree_block_is_consistent(
            "ABR insertion : 5, 3, 8, 4. Parcours infixe : 3, 5, 4, 8."
        ))

    def test_network_simulation_checks_ttl_ports_and_prefixes(self) -> None:
        self.assertEqual(network_trace.decrement_ttl(1), (0, "drop"))
        self.assertEqual(network_trace.route_decision("192.168.1.42", "192.168.1.0/24"), "local")
        self.assertEqual(network_trace.route_decision("8.8.8.8", "192.168.1.0/24"), "gateway")
        self.assertFalse(network_trace.network_block_is_consistent("HTTPS vers port 80 uniquement."))

    def test_dynamic_programming_table_is_recomputed(self) -> None:
        table = dynamic_programming.fibonacci_table(6)
        self.assertEqual(table, [0, 1, 1, 2, 3, 5, 8])
        self.assertFalse(dynamic_programming.dp_block_is_consistent(
            "État dp[i] = fib(i). Initialisation dp[0]=0, dp[1]=1. "
            "Relation dp[i]=dp[i-1]+dp[i-2]. Table : [0, 1, 1, 2, 4]. Résultat final 4."
        ))

    def test_boyer_moore_simulation_checks_table_and_found_index(self) -> None:
        self.assertEqual(boyer_moore.bad_character_table("ANA"), {"A": 2, "N": 1})
        self.assertEqual(boyer_moore.boyer_moore_search("BANANA", "ANA"), 1)
        self.assertEqual(boyer_moore.boyer_moore_search("BBBB", "ANA"), -1)
        self.assertFalse(boyer_moore.boyer_moore_block_is_consistent(
            "Texte BANANA, motif ANA. Table mauvais caractère : A->0, N->1. "
            "Comparaison droite-gauche. Décalage 2. Indice trouvé 2."
        ))

    def test_course_quality_rejects_heading_only_course(self) -> None:
        text = (
            "---\ndocument_type: cours\nstatus: needs_review\n---\n"
            "# Cours\n## Objectifs spécifiques\n## À savoir\n## Méthodes\n"
            "## Exemples corrigés\n## Critères\n"
        )
        self.assertTrue(course_quality.course_quality_errors(text, "cours_test.md"))

    def test_paper_tp_requires_explicit_non_executable_contract(self) -> None:
        bad = "---\ndocument_type: tp_papier\nstatus: needs_review\n---\n# TP papier\nTrace rapide.\n"
        self.assertTrue(paper_tp.paper_tp_errors(bad, "tp_papier_test.md"))

    def test_capacity_ladder_never_equates_assessed_with_covered(self) -> None:
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

            result = capacity_ladder.analyze_capacity_status_ladder(root)

            self.assertEqual(result.rows["P-TEST-01"]["documented"], "oui")
            self.assertEqual(result.rows["P-TEST-01"]["practiced"], "oui")
            self.assertEqual(result.rows["P-TEST-01"]["assessed"], "oui")
            self.assertEqual(result.rows["P-TEST-01"]["covered"], "non")

    def test_session_alignment_flags_theoretical_when_supports_exist(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(
                root / "03_progressions/seances_premiere.md",
                "### Séance P10-S1\n"
                "- Statut support : théorique non prêt\n"
                "- Document utilisé : P10_cours_reseaux.md, P10_trace_reseaux.md\n",
            )
            write(root / "03_progressions/supports/premiere/P10/P10_cours_reseaux.md", "cours")
            write(root / "03_progressions/supports/premiere/P10/P10_trace_reseaux.md", "trace")

            result = session_alignment.analyze_session_to_resource_alignment(root)

            self.assertEqual(result.theoretical_with_existing_supports, 1)
            self.assertTrue(result.errors)


if __name__ == "__main__":
    unittest.main()
