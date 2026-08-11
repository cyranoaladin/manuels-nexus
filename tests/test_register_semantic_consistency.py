from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_missing_register_semantic_consistency as semantic_register


HEADER = """| Fichier | Niveau | Séquence | Séance(s) | Type | Priorité | Statut | Responsable | Date cible | Source possible | Lien Drive éventuel | Dépendance | Décision | Blocage si absent | Fiche(s) concernée(s) | Impact pédagogique |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
"""


class MissingRegisterSemanticConsistencyTest(unittest.TestCase):
    def test_rejects_theme_mismatch_between_absent_support_and_sheet(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            sheet = root / "03_progressions" / "fiches_cours" / "premiere" / "P07" / "P07_fiche_cours_fonctions_tests_specifications.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text(
                """---
title: P07
sequence_id: P07
theme: "Langages et programmation"
notion: "fonctions tests spécifications"
readiness: linked
---
# P07
""",
                encoding="utf-8",
            )
            (root / "missing_documents_register_v2.md").write_text(
                "# Registre\n\n"
                "## Supports absents bloquant une fiche liée\n\n"
                + HEADER
                + "| P07_supports_web_client.md | premiere | P07 | P07-S1 | tp | haute | absent | equipe | 2027-01-01 | BO | NA | P06 | créer | oui | P07_fiche_cours_fonctions_tests_specifications.md | Confusion thème web contre fonctions. |\n",
                encoding="utf-8",
            )

            result = semantic_register.analyze_missing_register_semantic_consistency(root)

            self.assertTrue(any("thème incohérent" in error for error in result.errors))

    def test_rejects_operational_sheet_in_blocking_absent_section(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            sheet = root / "03_progressions" / "fiches_cours" / "terminale" / "T06" / "T06_fiche_cours_arbres_binaires_recherche.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text(
                """---
title: T06
sequence_id: T06
theme: "Arbres"
notion: "arbres binaires de recherche"
readiness: operational
---
# T06
""",
                encoding="utf-8",
            )
            (root / "missing_documents_register_v2.md").write_text(
                "# Registre\n\n"
                "## Supports absents bloquant une fiche liée\n\n"
                + HEADER
                + "| T06_supports_graphes_parcours.md | terminale | T06 | T06-S1 | cours | haute | absent | equipe | 2027-01-01 | BO | NA | T05 | créer | oui | T06_fiche_cours_arbres_binaires_recherche.md | Graphes associé à ABR. |\n",
                encoding="utf-8",
            )

            result = semantic_register.analyze_missing_register_semantic_consistency(root)

            self.assertTrue(any("fiche opérationnelle" in error.lower() for error in result.errors))


if __name__ == "__main__":
    unittest.main()
