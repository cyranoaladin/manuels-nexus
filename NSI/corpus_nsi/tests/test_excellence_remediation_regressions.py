from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P08 = ROOT / "03_progressions" / "supports" / "premiere" / "P08"
T17 = ROOT / "03_progressions" / "supports" / "terminale" / "T17"


class ExcellenceRemediationRegressionsTest(unittest.TestCase):
    def test_p08_evaluations_have_distinct_disciplinary_scopes(self) -> None:
        html_dom = (P08 / "P08_evaluation_html_css_dom.md").read_text(encoding="utf-8")
        http = (P08 / "P08_evaluation_http_get_post_formulaires.md").read_text(encoding="utf-8")

        for marker in ("<header", "querySelector", "addEventListener", "preventDefault"):
            self.assertIn(marker, html_dom)
        for marker in ("method=\"get\"", "method=\"post\"", "HTTPS", "localStorage", "Cookie"):
            self.assertIn(marker, http)
        self.assertNotEqual(html_dom.split("---", 2)[-1], http.split("---", 2)[-1])

    def test_p08_evaluations_link_distinct_baremes_and_corriges(self) -> None:
        expected = {
            "P08_evaluation_html_css_dom.md": (
                "P08_bareme_html_css_dom.md",
                "P08_corrige_html_css_dom.md",
            ),
            "P08_evaluation_http_get_post_formulaires.md": (
                "P08_bareme_http_get_post_formulaires.md",
                "P08_corrige_http_get_post_formulaires.md",
            ),
        }
        for evaluation, (bareme, corrige) in expected.items():
            body = (P08 / evaluation).read_text(encoding="utf-8")
            self.assertIn(f'bareme: "{bareme}"', body)
            self.assertIn(f'corrige: "{corrige}"', body)
            self.assertTrue((P08 / bareme).is_file())
            self.assertTrue((P08 / corrige).is_file())

    def test_p08_assessment_materials_reject_generic_point_labels(self) -> None:
        assessment_files = list(P08.glob("P08_evaluation_*.md")) + list(
            P08.glob("P08_bareme_*.md")
        )
        for path in assessment_files:
            body = path.read_text(encoding="utf-8")
            self.assertNotIn("1 point donnée", body, path.name)
            self.assertNotIn("1 point méthode", body, path.name)

    def test_t17_td_uses_six_distinct_dynamic_programming_tasks(self) -> None:
        td = (T17 / "T17_TD_programmation_dynamique.md").read_text(encoding="utf-8")
        for forbidden in ("jeu_exercice=", "cas_alpha", "cas_beta", "if cas_"):
            self.assertNotIn(forbidden, td)
        for marker in (
            "### Exercice 1",
            "### Exercice 6",
            "table de trace",
            "contre-exemple glouton",
            "grille",
            "Complexité",
        ):
            self.assertIn(marker, td)

    def test_t17_evaluation_uses_unseen_data_and_requires_an_algorithm(self) -> None:
        evaluation = (T17 / "T17_evaluation_programmation_dynamique.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("pieces = [1, 4, 6]", evaluation)
        self.assertIn("montant = 8", evaluation)
        self.assertIn("Écrire l'algorithme", evaluation)
        self.assertIn("montant impossible", evaluation)
        self.assertNotIn("n=6, f0=0, f1=1", evaluation)
        self.assertNotIn("1 point donnée", evaluation)

    def test_t17_supports_hide_answers_in_the_adapted_version(self) -> None:
        adapted = (T17 / "T17_version_amenagee_programmation_dynamique.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("Réponses rapides", adapted)
        self.assertNotIn("dp[8] = 2", adapted)
        self.assertIn("Aides à dévoilement progressif", adapted)


if __name__ == "__main__":
    unittest.main()
