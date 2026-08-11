from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def evidence(quote: str, *, teaches: bool = True) -> dict[str, object]:
    return {
        "present": True,
        "file": "source.md",
        "anchor": "#section",
        "quote": quote,
        "teaches": teaches,
    }


def absent_evidence(note: str = "preuve absente") -> dict[str, object]:
    return {
        "present": False,
        "file": None,
        "anchor": None,
        "quote": None,
        "teaches": False,
        "note": note,
    }


class SubstanceReportRendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "00_programmes_officiels").mkdir()
        (self.repo / "00_programmes_officiels" / "programme_nsi_2019.yaml").write_text(
            "programmes:\n"
            "  premiere:\n"
            "    - id: P-DATA-BASE-01\n"
            "      capacite_attendue:\n"
            "        - Passer de la représentation d'une base dans une autre.\n"
            "      niveau: premiere\n"
            "  terminale: []\n",
            encoding="utf-8",
        )
        (self.repo / "substance_verdict.schema.json").write_text(
            (ROOT / "substance_verdict.schema.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (self.repo / "source.md").write_text(
            "# Section\n\n"
            "Passer de la représentation d'une base dans une autre avec une méthode explicite.\n"
            "L'élève s'entraîne sur une conversion vérifiable.\n"
            "Le corrigé donne la base de départ et la base d'arrivée.\n",
            encoding="utf-8",
        )
        self.status_files = {
            "coverage.md": "# Coverage\n\ncovered = 0\n",
            "manifest.csv": "id,statut\nP-DATA-BASE-01,needs_review\n",
            "INDEX.md": "# Index\n\npublished = 0\n",
            "substance_reviews_index.md": "# Substance\n\nvalidated_* = 0\n",
        }
        for name, content in self.status_files.items():
            (self.repo / name).write_text(content, encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def verdict(
        self,
        *,
        declared: str = "needs_content",
        flags: list[str] | None = None,
        course: dict[str, object] | None = None,
        practice: dict[str, object] | None = None,
        correction: dict[str, object] | None = None,
    ) -> dict[str, object]:
        return {
            "schema_version": "1.0.0",
            "unit": "P01",
            "level": "premiere",
            "judged_at": "2026-06-29T08:00:00Z",
            "judge_model": "test-judge",
            "author_model": "test-author",
            "capacities": [
                {
                    "capacity_id": "P-DATA-BASE-01",
                    "official_label": "Passer de la représentation d'une base dans une autre.",
                    "proof_course": course or absent_evidence("cours absent"),
                    "proof_practice": practice or absent_evidence("pratique absente"),
                    "proof_correction": correction or absent_evidence("correction absente"),
                    "verdict": declared,
                    "justification": "Pré-jugement outillé destiné à une revue humaine ultérieure.",
                    "scientific_flags": flags or [],
                }
            ],
        }

    def test_needs_content_report_contains_charter_marker_and_no_promotion(self) -> None:
        import scripts.substance_report_renderer as renderer

        model = renderer.build_report_model(self.verdict(), self.repo)
        html = renderer.render_html(model)

        self.assertIn('<meta name="nsi-report-kind" content="substance-audit">', html)
        self.assertIn("pré-jugement outillé, non validation humaine", html)
        self.assertNotIn("covered = 1", html)
        self.assertNotIn("published = 1", html)

    def test_scientific_flags_are_visible_in_markdown_and_html(self) -> None:
        import scripts.substance_report_renderer as renderer

        model = renderer.build_report_model(
            self.verdict(flags=["human_review_required"]),
            self.repo,
        )

        self.assertIn("human_review_required", renderer.render_markdown(model))
        html = renderer.render_html(model)
        self.assertIn("human_review_required", html)
        self.assertIn("scientific-flags", html)

    def test_downgraded_validated_pedagogy_is_rendered_as_alert(self) -> None:
        import scripts.substance_report_renderer as renderer

        model = renderer.build_report_model(
            self.verdict(
                declared="validated_pedagogy",
                course=evidence(
                    "Passer de la représentation d'une base dans une autre avec une méthode explicite."
                ),
                practice=evidence("Citation absente mais suffisamment longue."),
                correction=evidence("Le corrigé donne la base de départ et la base d'arrivée."),
            ),
            self.repo,
        )
        html = renderer.render_html(model)

        self.assertIn("status-downgraded", html)
        self.assertIn("Verdict déclaré: validated_pedagogy", html)
        self.assertIn("Verdict effectif: needs_content (DÉGRADÉ)", html)

    def test_invalid_schema_raises_without_report(self) -> None:
        import scripts.substance_report_renderer as renderer

        with self.assertRaises(renderer.SchemaError):
            renderer.build_report_model({"schema_version": "1.0.0"}, self.repo)

    def test_html_is_standalone_without_external_script_or_stylesheet(self) -> None:
        import scripts.substance_report_renderer as renderer

        html = renderer.render_html(renderer.build_report_model(self.verdict(), self.repo))

        self.assertNotIn("<script src=", html)
        self.assertNotIn('<link rel="stylesheet"', html)
        self.assertIn("<style>", html)

    def test_renderer_does_not_modify_repository_status_files(self) -> None:
        import scripts.substance_report_renderer as renderer

        before = {
            name: (self.repo / name).read_text(encoding="utf-8")
            for name in self.status_files
        }
        model = renderer.build_report_model(self.verdict(), self.repo)
        out_dir = self.repo / "01_build_reports" / "substance_reports"
        renderer.write_report_outputs(model, out_dir / "P01.md", out_dir / "P01.html")
        after = {
            name: (self.repo / name).read_text(encoding="utf-8")
            for name in self.status_files
        }

        self.assertEqual(after, before)
        self.assertTrue((out_dir / "P01.md").exists())
        self.assertTrue((out_dir / "P01.html").exists())


if __name__ == "__main__":
    unittest.main()
