from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_session_referenced_files_exist as sessions


REGISTER_HEADER = """| Fichier | Niveau | Séquence | Séance(s) | Type | Priorité | Statut | Responsable | Date cible | Source possible | Lien Drive éventuel | Dépendance | Décision | Blocage si absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
"""


class SessionReferenceAnalysisTest(unittest.TestCase):
    def test_generic_only_session_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session_file = root / "seances.md"
            session_file.write_text(
                """### Séance P00-S1
- Nature : cours
- Document utilisé : cours_eleve.md, td.md
- Livrable : trace complétée cours_eleve.md
""",
                encoding="utf-8",
            )
            register = root / "missing_documents_register_v2.md"
            register.write_text(REGISTER_HEADER, encoding="utf-8")

            result = sessions.analyze_sessions(root, [session_file], register)

            self.assertTrue(any("fichiers génériques" in error for error in result.errors))
            self.assertEqual(result.ready_sessions, 0)
            self.assertEqual(result.theoretical_sessions, 1)

    def test_specific_existing_support_counts_as_ready(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for name in ["P00_cours_intro.md", "P00_TD_intro.md", "P00_trace_intro.md"]:
                (root / name).write_text("# Support\n\nContenu substantiel.", encoding="utf-8")
            session_file = root / "seances.md"
            session_file.write_text(
                """### Séance P00-S1
- Nature : TD
- Document utilisé : P00_cours_intro.md, P00_TD_intro.md
- Livrable : P00_trace_intro.md
""",
                encoding="utf-8",
            )
            register = root / "missing_documents_register_v2.md"
            register.write_text(REGISTER_HEADER, encoding="utf-8")

            result = sessions.analyze_sessions(root, [session_file], register)

            self.assertEqual(result.errors, [])
            self.assertEqual(result.ready_sessions, 1)
            self.assertEqual(result.theoretical_sessions, 0)
            self.assertEqual(result.usable_percent, 100.0)

    def test_abandoned_referenced_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session_file = root / "seances.md"
            session_file.write_text(
                """### Séance P03-S1
- Nature : cours
- Document utilisé : P03_cours_abandonne.md
- Livrable : P03_trace_abandonnee.md
""",
                encoding="utf-8",
            )
            register = root / "missing_documents_register_v2.md"
            register.write_text(
                REGISTER_HEADER
                + "| P03_cours_abandonne.md | premiere | P03 | P03-S1 | cours | haute | absent | equipe NSI | 2026-10-15 | Documents_DRIVE | NA | aucune | abandonner | oui |\n"
                + "| P03_trace_abandonnee.md | premiere | P03 | P03-S1 | trace | haute | absent | equipe NSI | 2026-10-15 | Documents_DRIVE | P03_cours_abandonne.md | créer | oui |\n",
                encoding="utf-8",
            )

            result = sessions.analyze_sessions(root, [session_file], register)

            self.assertTrue(any("abandonner" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
