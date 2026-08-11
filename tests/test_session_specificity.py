from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_session_specificity as specificity


class SessionSpecificityTest(unittest.TestCase):
    def test_theoretical_session_is_not_checked_as_ready_session(self) -> None:
        session = {
            "id": "P03-S1",
            "Statut support": "théorique non prêt",
            "Document utilisé": "support spécifique non produit dans cette tranche",
            "Livrable": "intention de production à préciser",
            "Objectif": "introduire une notion future quand le support existera",
            "Déroulé": "scénario à cadrer après production du support",
            "raw": "Statut support : théorique non prêt",
        }
        self.assertEqual(specificity.session_specificity_errors("premiere", session), [])

    def test_ready_session_without_concrete_reference_is_rejected(self) -> None:
        session = {
            "id": "P03-S1",
            "Document utilisé": "support générique",
            "Livrable": "production",
            "Objectif": "introduire une notion future quand le support existera",
            "Déroulé": "scénario court",
            "raw": "support générique",
        }
        errors = specificity.session_specificity_errors("premiere", session)
        self.assertTrue(any("document used is not concrete" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
