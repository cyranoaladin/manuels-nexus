import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=120,
    )


class AuditStrategicIntegrationTests(unittest.TestCase):
    def test_program_coverage_indexes_supports_and_writes_sources(self):
        result = run_script("scripts.check_program_coverage")
        self.assertEqual(result.returncode, 0, result.stdout)
        coverage = (ROOT / "coverage.md").read_text(encoding="utf-8")
        sources = (ROOT / "coverage_sources.md").read_text(encoding="utf-8")
        self.assertIn("03_progressions/supports/", coverage)
        self.assertIn("03_progressions/supports/", sources)
        self.assertIn("- covered : 0", coverage)

    def test_audit_folder_policy_excludes_audit_from_pedagogical_corpus(self):
        result = run_script("scripts.check_audit_folder_policy")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("corpus pédagogique", result.stdout)

    def test_substance_anchor_checker_global_mode_and_poisoned_fixture(self):
        result = run_script("scripts.check_substance_anchors")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("test adverse", result.stdout.lower())

    def test_gate_policy_has_small_blocking_core(self):
        result = run_script("scripts.check_gate_policy_consistency")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("bloquants hors tests", result.stdout)

    def test_rendered_unit_checker_builds_temp_student_and_teacher_outputs(self):
        result = run_script("scripts.check_rendered_unit_artifacts", "--unit", "P05")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("version élève", result.stdout)
        self.assertIn("version prof", result.stdout)

    def test_substance_review_files_never_self_promote(self):
        """No verdict file may contain validated_pedagogy (promotion = lead only)."""
        reviews = sorted(ROOT.glob("substance_reviews/**/*_substance_review.json"))
        reviews += sorted(ROOT.glob("03_progressions/supports/**/_substance_review.json"))
        self.assertTrue(reviews, "aucun verdict de substance")
        for review in reviews:
            payload = json.loads(review.read_text(encoding="utf-8"))
            verdicts = {cap["verdict"] for cap in payload.get("capacities", [])}
            self.assertNotIn("validated_pedagogy", verdicts,
                             f"{review}: verdict validated_pedagogy interdit (promotion lead)")
