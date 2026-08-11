from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RenderSubstanceReportCliTests(unittest.TestCase):
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
            "Passer de la représentation d'une base dans une autre avec une méthode explicite.\n",
            encoding="utf-8",
        )
        self.verdict = self.repo / "verdict.json"
        self.verdict.write_text(
            json.dumps(
                {
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
                            "proof_course": {
                                "present": True,
                                "file": "source.md",
                                "anchor": "#section",
                                "quote": (
                                    "Passer de la représentation d'une base dans une autre "
                                    "avec une méthode explicite."
                                ),
                                "teaches": False,
                            },
                            "proof_practice": {
                                "present": False,
                                "file": None,
                                "anchor": None,
                                "quote": None,
                                "teaches": False,
                            },
                            "proof_correction": {
                                "present": False,
                                "file": None,
                                "anchor": None,
                                "quote": None,
                                "teaches": False,
                            },
                            "verdict": "needs_content",
                            "justification": "Pré-jugement outillé destiné à une revue humaine ultérieure.",
                            "scientific_flags": ["human_review_required"],
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "scripts.render_substance_report", *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=60,
        )

    def test_cli_writes_markdown_and_html_reports(self) -> None:
        out_md = self.repo / "01_build_reports" / "substance_reports" / "P01.md"
        out_html = self.repo / "01_build_reports" / "substance_reports" / "P01.html"

        result = self.run_cli(
            "--verdict",
            str(self.verdict),
            "--repo-root",
            str(self.repo),
            "--out-md",
            str(out_md),
            "--out-html",
            str(out_html),
        )

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("substance_report: wrote", result.stdout)
        self.assertIn("human_review_required", out_md.read_text(encoding="utf-8"))
        self.assertIn(
            '<meta name="nsi-report-kind" content="substance-audit">',
            out_html.read_text(encoding="utf-8"),
        )

    def test_cli_rejects_missing_verdict_without_outputs(self) -> None:
        out_md = self.repo / "missing.md"
        out_html = self.repo / "missing.html"

        result = self.run_cli(
            "--verdict",
            str(self.repo / "absent.json"),
            "--repo-root",
            str(self.repo),
            "--out-md",
            str(out_md),
            "--out-html",
            str(out_html),
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("verdict introuvable", result.stdout)
        self.assertFalse(out_md.exists())
        self.assertFalse(out_html.exists())

    def test_artifact_check_accepts_valid_pair_and_rejects_broken_html(self) -> None:
        out_dir = self.repo / "01_build_reports" / "substance_reports"
        out_md = out_dir / "P01.md"
        out_html = out_dir / "P01.html"
        result = self.run_cli(
            "--verdict",
            str(self.verdict),
            "--repo-root",
            str(self.repo),
            "--out-md",
            str(out_md),
            "--out-html",
            str(out_html),
        )
        self.assertEqual(result.returncode, 0, result.stdout)

        check_ok = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.check_substance_report_artifacts",
                "--reports-dir",
                str(out_dir),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=60,
        )
        self.assertEqual(check_ok.returncode, 0, check_ok.stdout)

        out_html.write_text("<html><body>rapport sans charte</body></html>", encoding="utf-8")
        check_ko = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.check_substance_report_artifacts",
                "--reports-dir",
                str(out_dir),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=60,
        )
        self.assertNotEqual(check_ko.returncode, 0)
        self.assertIn("meta-tag", check_ko.stdout)


if __name__ == "__main__":
    unittest.main()
