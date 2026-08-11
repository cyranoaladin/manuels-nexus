from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_ready_session_operationality as operationality


class ReadySessionOperationalityTest(unittest.TestCase):
    def test_ready_session_without_concrete_livrable_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session_file = root / "seances.md"
            session_file.write_text(
                "### Séance P01-S1\n"
                "- Document utilisé : P01_cours_test.md, P01_trace_test.md\n"
                "- Livrable : production élève vérifiable.\n"
                "- Remédiation : utiliser P01_remediation_test.md.\n",
                encoding="utf-8",
            )
            for name in ["P01_cours_test.md", "P01_trace_test.md", "P01_remediation_test.md"]:
                (root / name).write_text("## Erreurs fréquentes\n- Erreur fréquente EF1\n", encoding="utf-8")

            result = operationality.analyze_ready_sessions(root, session_files=[session_file], prefixes=["P01"])

            self.assertTrue(any("livrable non concret" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
