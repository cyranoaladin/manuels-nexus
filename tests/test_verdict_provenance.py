"""Tests for check_verdict_provenance gate — monotone rule + fail-closed."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_verdict_provenance import check_provenance, _content_changed, _BaseCorrupt


def _make_verdict(
    judged_at: str,
    quote: str = "some quote",
    capacity_id: str = "P-TEST-01",
    official_label: str = "Test",
) -> dict:
    return {
        "schema_version": "1.0.0",
        "unit": "campaign",
        "level": "premiere",
        "judged_at": judged_at,
        "judge_model": "claude-sonnet-4-6",
        "author_model": "campaign-tooling",
        "capacities": [{
            "capacity_id": capacity_id,
            "official_label": official_label,
            "proof_course": {"present": True, "file": "f.md", "anchor": "#a", "quote": quote, "teaches": True},
            "proof_practice": {"present": False},
            "proof_correction": {"present": False},
            "verdict": "needs_review",
            "justification": "test justification",
            "scientific_flags": [],
        }],
    }


class MonotoneRuleTest(unittest.TestCase):
    """WDT-2: adverse matrix for monotone provenance rule."""

    def _run(self, base_data: dict | None, head_data: dict, head_path: Path) -> tuple[list[str], list[str], bool]:
        """Run check_provenance with mocked git operations."""
        rel = head_path.name
        head_path.write_text(json.dumps(head_data), encoding="utf-8")

        with patch("scripts.check_verdict_provenance._resolve_base", return_value="abc123"):
            with patch("scripts.check_verdict_provenance.get_changed_verdict_files", return_value=[rel]):
                with patch("scripts.check_verdict_provenance.get_base_version", return_value=base_data):
                    with patch("scripts.check_verdict_provenance.ROOT", head_path.parent):
                        return check_provenance()

    def test_a_quote_modified_judged_at_unchanged_rouge(self) -> None:
        """(a) Quote modified, judged_at unchanged → ROUGE."""
        ts = "2026-07-11T14:35:27Z"
        base = _make_verdict(ts, quote="old quote")
        head = _make_verdict(ts, quote="new quote")

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "P-TEST-01_substance_review.json"
            errors, inspected, executed = self._run(base, head, p)

        self.assertTrue(executed)
        self.assertEqual(len(errors), 1)
        self.assertIn("judged_at unchanged", errors[0])

    def test_b_quote_modified_judged_at_bumped_vert(self) -> None:
        """(b) Quote modified, judged_at bumped (pipeline behavior) → VERT."""
        base = _make_verdict("2026-07-11T14:35:27Z", quote="old quote")
        head = _make_verdict("2026-07-11T19:19:20Z", quote="new quote")

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "P-TEST-01_substance_review.json"
            errors, inspected, executed = self._run(base, head, p)

        self.assertTrue(executed)
        self.assertEqual(errors, [])

    def test_c_judged_at_regressed_rouge(self) -> None:
        """(c) judged_at went backwards → ROUGE (monotonicity violation)."""
        base = _make_verdict("2026-07-11T19:19:20Z", quote="old")
        head = _make_verdict("2026-07-11T14:35:27Z", quote="new")

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "P-TEST-01_substance_review.json"
            errors, inspected, executed = self._run(base, head, p)

        self.assertTrue(executed)
        self.assertEqual(len(errors), 1)
        self.assertIn("monotonicity violation", errors[0])

    def test_d_file_not_modified_ignored(self) -> None:
        """(d) File not in changed list → ignored (no error, no inspection)."""
        with patch("scripts.check_verdict_provenance._resolve_base", return_value="abc123"):
            with patch("scripts.check_verdict_provenance.get_changed_verdict_files", return_value=[]):
                errors, inspected, executed = check_provenance()

        self.assertTrue(executed)
        self.assertEqual(errors, [])
        self.assertEqual(inspected, [])

    def test_e_base_unavailable_fail_closed(self) -> None:
        """(e) Base ref unavailable → explicit failure, guard NOT executed."""
        with patch("scripts.check_verdict_provenance._resolve_base", return_value=None):
            errors, inspected, executed = check_provenance("nonexistent-ref")

        self.assertFalse(executed)
        self.assertEqual(len(errors), 1)
        self.assertIn("guard NON exécuté", errors[0])


class FailClosedTest(unittest.TestCase):
    """WDT-1: fail-closed behavior."""

    def test_git_diff_failure_is_not_pass(self) -> None:
        """If git diff returns non-zero, guard must NOT pass."""
        with patch("scripts.check_verdict_provenance._resolve_base", return_value="abc123"):
            with patch("scripts.check_verdict_provenance.get_changed_verdict_files", return_value=None):
                errors, inspected, executed = check_provenance()

        self.assertFalse(executed)
        self.assertIn("guard NON exécuté", errors[0])

    def test_missing_judged_at_fails(self) -> None:
        """Verdict without judged_at field → FAIL."""
        head = _make_verdict("2026-01-01T00:00:00Z")
        del head["judged_at"]

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "P-TEST-01_substance_review.json"
            p.write_text(json.dumps(head), encoding="utf-8")

            with patch("scripts.check_verdict_provenance._resolve_base", return_value="abc123"):
                with patch("scripts.check_verdict_provenance.get_changed_verdict_files", return_value=[p.name]):
                    with patch("scripts.check_verdict_provenance.get_base_version", return_value=None):
                        with patch("scripts.check_verdict_provenance.ROOT", Path(d)):
                            errors, inspected, executed = check_provenance()

        self.assertTrue(executed)
        self.assertEqual(len(errors), 1)
        self.assertIn("missing or invalid judged_at", errors[0])


class ContentChangedTest(unittest.TestCase):
    """Unit tests for _content_changed."""

    def test_identical_no_change(self) -> None:
        v = _make_verdict("2026-01-01T00:00:00Z")
        self.assertFalse(_content_changed(v, v))

    def test_quote_change_detected(self) -> None:
        base = _make_verdict("2026-01-01T00:00:00Z", quote="a")
        head = _make_verdict("2026-01-01T00:00:00Z", quote="b")
        self.assertTrue(_content_changed(base, head))

    def test_judged_at_only_change_not_content(self) -> None:
        base = _make_verdict("2026-01-01T00:00:00Z")
        head = _make_verdict("2026-07-11T00:00:00Z")
        self.assertFalse(_content_changed(base, head))

    def test_capacity_id_change_is_content(self) -> None:
        """capacity_id modified → content changed (reassignment)."""
        base = _make_verdict("2026-01-01T00:00:00Z", capacity_id="P-OLD-01")
        head = _make_verdict("2026-01-01T00:00:00Z", capacity_id="P-NEW-01")
        self.assertTrue(_content_changed(base, head))

    def test_official_label_change_is_content(self) -> None:
        """official_label modified alone → content changed."""
        base = _make_verdict("2026-01-01T00:00:00Z", official_label="Old label")
        head = _make_verdict("2026-01-01T00:00:00Z", official_label="New label")
        self.assertTrue(_content_changed(base, head))


class IdentityFieldsTest(unittest.TestCase):
    """Refinement 1: capacity_id/official_label are content fields."""

    def _run(self, base_data: dict | None, head_data: dict, head_path: Path) -> tuple[list[str], list[str], bool]:
        rel = head_path.name
        head_path.write_text(json.dumps(head_data), encoding="utf-8")
        with patch("scripts.check_verdict_provenance._resolve_base", return_value="abc123"):
            with patch("scripts.check_verdict_provenance.get_changed_verdict_files", return_value=[rel]):
                with patch("scripts.check_verdict_provenance.get_base_version", return_value=base_data):
                    with patch("scripts.check_verdict_provenance.ROOT", head_path.parent):
                        return check_provenance()

    def test_capacity_id_modified_judged_at_unchanged_rouge(self) -> None:
        """Reassignment without re-judgment → ROUGE."""
        ts = "2026-07-11T14:35:27Z"
        base = _make_verdict(ts, capacity_id="P-OLD-01")
        head = _make_verdict(ts, capacity_id="P-NEW-01")

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "P-NEW-01_substance_review.json"
            errors, _, executed = self._run(base, head, p)

        self.assertTrue(executed)
        self.assertEqual(len(errors), 1)
        self.assertIn("judged_at unchanged", errors[0])

    def test_official_label_modified_judged_at_unchanged_rouge(self) -> None:
        """Label change without re-judgment → ROUGE."""
        ts = "2026-07-11T14:35:27Z"
        base = _make_verdict(ts, official_label="Old")
        head = _make_verdict(ts, official_label="New")

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "P-TEST-01_substance_review.json"
            errors, _, executed = self._run(base, head, p)

        self.assertTrue(executed)
        self.assertEqual(len(errors), 1)
        self.assertIn("judged_at unchanged", errors[0])


class BaseCorruptTest(unittest.TestCase):
    """Refinement 2: base illisible ≠ fichier nouveau."""

    def test_corrupt_base_json_rouge(self) -> None:
        """Base file exists but is not valid JSON → ROUGE (fail-closed)."""
        head = _make_verdict("2026-07-11T19:19:20Z")

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "P-TEST-01_substance_review.json"
            p.write_text(json.dumps(head), encoding="utf-8")
            rel = p.name

            corrupt = _BaseCorrupt("JSON invalide dans la base")

            with patch("scripts.check_verdict_provenance._resolve_base", return_value="abc123"):
                with patch("scripts.check_verdict_provenance.get_changed_verdict_files", return_value=[rel]):
                    with patch("scripts.check_verdict_provenance.get_base_version", return_value=corrupt):
                        with patch("scripts.check_verdict_provenance.ROOT", Path(d)):
                            errors, inspected, executed = check_provenance()

        self.assertTrue(executed)
        self.assertEqual(len(errors), 1)
        self.assertIn("base illisible", errors[0])
        self.assertIn("comparaison impossible", errors[0])

    def test_genuinely_new_file_vert(self) -> None:
        """File did not exist at base (None) → VERT (skip)."""
        head = _make_verdict("2026-07-11T19:19:20Z")

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "P-TEST-01_substance_review.json"
            p.write_text(json.dumps(head), encoding="utf-8")
            rel = p.name

            with patch("scripts.check_verdict_provenance._resolve_base", return_value="abc123"):
                with patch("scripts.check_verdict_provenance.get_changed_verdict_files", return_value=[rel]):
                    with patch("scripts.check_verdict_provenance.get_base_version", return_value=None):
                        with patch("scripts.check_verdict_provenance.ROOT", Path(d)):
                            errors, inspected, executed = check_provenance()

        self.assertTrue(executed)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
