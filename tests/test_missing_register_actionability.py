from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_missing_register_actionability as register_actionability


HEADER = """| Fichier | Niveau | Séquence | Séance(s) | Type | Priorité | Statut | Responsable | Date cible | Source possible | Lien Drive éventuel | Dépendance | Décision | Blocage si absent | Fiche(s) concernée(s) | Impact pédagogique |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
"""


class MissingRegisterActionabilityTest(unittest.TestCase):
    def test_absent_support_requires_impacted_sheet_and_pedagogical_impact(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "missing_documents_register_v2.md").write_text(
                HEADER
                + "| P09_TD_os.md | premiere | P09 | P09-S1 | td | haute | absent | equipe NSI | 2027-06-30 | Documents_DRIVE | NA | fiche P09 | créer | oui |  |  |\n",
                encoding="utf-8",
            )

            result = register_actionability.analyze_missing_register_actionability(root)

            self.assertTrue(any("fiche(s) concernée(s)" in error.lower() for error in result.errors))
            self.assertTrue(any("impact pédagogique" in error.lower() for error in result.errors))

    def test_linked_sheet_with_three_absent_supports_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "03_progressions").mkdir()
            (root / "03_progressions" / "seances_premiere.md").write_text("### Séance P09-S1\n", encoding="utf-8")
            register_rows = [
                f"| P09_{kind}.md | premiere | P09 | P09-S1 | {kind.lower()} | haute | absent | equipe NSI | 2027-06-30 | Documents_DRIVE | NA | fiche P09 | créer | oui | P09_fiche_cours_os.md | Support {kind} absent, fiche liée non opérationnelle |"
                for kind in ["TD", "TP", "evaluation"]
            ]
            (root / "missing_documents_register_v2.md").write_text(HEADER + "\n".join(register_rows) + "\n", encoding="utf-8")
            sheet = root / "03_progressions" / "fiches_cours" / "premiere" / "P09" / "P09_fiche_cours_os.md"
            sheet.parent.mkdir(parents=True)
            sheet.write_text(
                """---
title: "P09"
sequence_id: "P09"
readiness: linked
---
# Fiche

## Lien avec la progression
| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | P09-S1 | réelle | séance réelle |
| TD | P09_TD.md | à créer | registre |
| TP | P09_TP.md | à créer | registre |
| Évaluation | P09_evaluation.md | à créer | registre |
""",
                encoding="utf-8",
            )

            result = register_actionability.analyze_missing_register_actionability(root)

            self.assertTrue(any("dépend de plus de deux supports absents" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
