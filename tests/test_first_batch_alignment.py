from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_first_batch_alignment as alignment


class FirstBatchAlignmentTest(unittest.TestCase):
    def test_missing_td_correction_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            directory = root / "P00"
            directory.mkdir()
            (directory / "P00_cours_test.md").write_text(
                "Objectif O1 - diagnostiquer une trace\nCapacité : P-LANG-01\nErreur fréquente EF1 - confondre affectation et égalité\n",
                encoding="utf-8",
            )
            (directory / "P00_trace_test.md").write_text("Objectif O1\nCapacité : P-LANG-01\n", encoding="utf-8")
            (directory / "P00_td_test.md").write_text("### Exercice 1 - O1\nCapacité : P-LANG-01\n", encoding="utf-8")
            (directory / "P00_tp_test.md").write_text("Objectif O1\nCapacité : P-LANG-01\n", encoding="utf-8")
            (directory / "P00_corrige_test.md").write_text("### Corrigé exercice 2\n", encoding="utf-8")
            (directory / "P00_evaluation_test.md").write_text("### Question 1 - O1\nCapacité : P-LANG-01\n", encoding="utf-8")
            (directory / "P00_bareme_test.md").write_text("### Barème question 1\n", encoding="utf-8")
            (directory / "P00_remediation_test.md").write_text("Activité corrective EF1\n", encoding="utf-8")

            result = alignment.analyze_alignment(root, prefixes=["P00"], program_ids={"P-LANG-01"})

            self.assertTrue(any("Exercice 1" in error and "corrigé" in error for error in result.errors))

    def test_complete_alignment_passes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            directory = root / "P00"
            directory.mkdir()
            (directory / "P00_cours_test.md").write_text(
                "Objectif O1 - diagnostiquer une trace\nCapacité : P-LANG-01\nErreur fréquente EF1 - confondre affectation et égalité\n",
                encoding="utf-8",
            )
            (directory / "P00_trace_test.md").write_text("Objectif O1\nCapacité : P-LANG-01\n", encoding="utf-8")
            (directory / "P00_td_test.md").write_text("### Exercice 1 - O1\nCapacité : P-LANG-01\n", encoding="utf-8")
            (directory / "P00_tp_test.md").write_text("Objectif O1\nCapacité : P-LANG-01\nLivrable vérifiable\n", encoding="utf-8")
            (directory / "P00_corrige_test.md").write_text("### Corrigé exercice 1\n", encoding="utf-8")
            (directory / "P00_evaluation_test.md").write_text("### Question 1 - O1\nCapacité : P-LANG-01\n", encoding="utf-8")
            (directory / "P00_bareme_test.md").write_text("### Barème question 1\n", encoding="utf-8")
            (directory / "P00_remediation_test.md").write_text("Activité corrective EF1\n", encoding="utf-8")

            result = alignment.analyze_alignment(root, prefixes=["P00"], program_ids={"P-LANG-01"})

            self.assertEqual(result.errors, [])


    def test_frontmatter_only_capacity_flagged(self) -> None:
        """Adverse: capacity declared in frontmatter but absent from TD/TP/eval → ROUGE."""
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            directory = root / "P00"
            directory.mkdir()
            # Course declares P-FAKE-99 in frontmatter only — NOT in body
            (directory / "P00_cours_test.md").write_text(
                "---\ntitle: test\nofficial_program:\n  capacities:\n    - P-FAKE-99\n---\n"
                "Objectif O1\nCapacité : P-LANG-01\nErreur fréquente EF1\n",
                encoding="utf-8",
            )
            (directory / "P00_trace_test.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
            (directory / "P00_td_test.md").write_text("### Exercice 1\nP-LANG-01\n", encoding="utf-8")
            (directory / "P00_tp_test.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
            (directory / "P00_corrige_test.md").write_text("### Corrigé exercice 1\n", encoding="utf-8")
            (directory / "P00_evaluation_test.md").write_text("### Question 1\nP-LANG-01\n", encoding="utf-8")
            (directory / "P00_bareme_test.md").write_text("### Barème question 1\n", encoding="utf-8")
            (directory / "P00_remediation_test.md").write_text("Activité corrective EF1\n", encoding="utf-8")

            result = alignment.analyze_alignment(root, prefixes=["P00"], program_ids={"P-LANG-01", "P-FAKE-99"})

            frontmatter_errors = [e for e in result.errors if "P-FAKE-99" in e]
            self.assertTrue(len(frontmatter_errors) >= 1, f"Expected P-FAKE-99 flagged, got: {result.errors}")
            self.assertTrue(any("non travaillée" in e or "non évaluée" in e for e in frontmatter_errors))

    def test_frontmatter_capacity_exercised_passes(self) -> None:
        """Capacity declared in frontmatter AND exercised in TD/eval → VERT."""
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            directory = root / "P00"
            directory.mkdir()
            (directory / "P00_cours_test.md").write_text(
                "---\ntitle: test\nofficial_program:\n  capacities:\n    - P-LANG-01\n---\n"
                "Objectif O1\nP-LANG-01\nErreur fréquente EF1\n",
                encoding="utf-8",
            )
            (directory / "P00_trace_test.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
            (directory / "P00_td_test.md").write_text("### Exercice 1\nP-LANG-01\n", encoding="utf-8")
            (directory / "P00_tp_test.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
            (directory / "P00_corrige_test.md").write_text("### Corrigé exercice 1\n", encoding="utf-8")
            (directory / "P00_evaluation_test.md").write_text("### Question 1\nP-LANG-01\n", encoding="utf-8")
            (directory / "P00_bareme_test.md").write_text("### Barème question 1\n", encoding="utf-8")
            (directory / "P00_remediation_test.md").write_text("Activité corrective EF1\n", encoding="utf-8")

            result = alignment.analyze_alignment(root, prefixes=["P00"], program_ids={"P-LANG-01"})

            self.assertEqual(result.errors, [])


    def test_known_failure_is_warning_not_error(self) -> None:
        """Known-failure listed in yml → WARNING, gate PASS (not KO)."""
        import scripts.check_first_batch_alignment as mod
        original = mod.KNOWN_FAILURES_PATH
        try:
            with tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                kf = root / "known.yml"
                kf.write_text(
                    "known_failures:\n  - id: P-FAKE-99\n    prefix: P00\n    reason: test\n    resolution: PR B\n",
                    encoding="utf-8",
                )
                mod.KNOWN_FAILURES_PATH = kf  # type: ignore[assignment]
                # Same fixture as frontmatter-only test
                directory = root / "P00"
                directory.mkdir()
                (directory / "P00_cours_test.md").write_text(
                    "---\ntitle: t\nofficial_program:\n  capacities:\n    - P-FAKE-99\n---\nObjectif O1\nP-LANG-01\nErreur fréquente EF1\n",
                    encoding="utf-8",
                )
                for kind, content in [
                    ("trace", "Objectif O1\nP-LANG-01\n"),
                    ("td", "### Exercice 1\nP-LANG-01\n"),
                    ("tp", "Objectif O1\nP-LANG-01\n"),
                    ("corrige", "### Corrigé exercice 1\n"),
                    ("evaluation", "### Question 1\nP-LANG-01\n"),
                    ("bareme", "### Barème question 1\n"),
                    ("remediation", "Activité corrective EF1\n"),
                ]:
                    (directory / f"P00_{kind}_test.md").write_text(content, encoding="utf-8")

                result = mod.analyze_alignment(root, prefixes=["P00"], program_ids={"P-LANG-01", "P-FAKE-99"})
                # Errors exist but main() should return 0 (all are known)
                self.assertTrue(len(result.errors) >= 1)
                # Simulate main() logic
                known = mod._load_known_failures()
                hard = [e for e in result.errors if not any(
                    e.startswith(f"{p}:") and cid in e for p, cid in known)]
                self.assertEqual(hard, [], f"Expected 0 hard errors, got: {hard}")
        finally:
            mod.KNOWN_FAILURES_PATH = original  # type: ignore[assignment]

    def test_unknown_failure_still_hard_error(self) -> None:
        """Failure NOT in known list → remains KO."""
        import scripts.check_first_batch_alignment as mod
        original = mod.KNOWN_FAILURES_PATH
        try:
            with tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                kf = root / "known.yml"
                # Known list is EMPTY
                kf.write_text("known_failures: []\n", encoding="utf-8")
                mod.KNOWN_FAILURES_PATH = kf  # type: ignore[assignment]
                directory = root / "P00"
                directory.mkdir()
                (directory / "P00_cours_test.md").write_text(
                    "---\ntitle: t\nofficial_program:\n  capacities:\n    - P-FAKE-99\n---\nObjectif O1\nP-LANG-01\nErreur fréquente EF1\n",
                    encoding="utf-8",
                )
                for kind, content in [
                    ("trace", "Objectif O1\nP-LANG-01\n"),
                    ("td", "### Exercice 1\nP-LANG-01\n"),
                    ("tp", "Objectif O1\nP-LANG-01\n"),
                    ("corrige", "### Corrigé exercice 1\n"),
                    ("evaluation", "### Question 1\nP-LANG-01\n"),
                    ("bareme", "### Barème question 1\n"),
                    ("remediation", "Activité corrective EF1\n"),
                ]:
                    (directory / f"P00_{kind}_test.md").write_text(content, encoding="utf-8")

                result = mod.analyze_alignment(root, prefixes=["P00"], program_ids={"P-LANG-01", "P-FAKE-99"})
                known = mod._load_known_failures()
                hard = [e for e in result.errors if not any(
                    e.startswith(f"{p}:") and cid in e for p, cid in known)]
                self.assertTrue(len(hard) >= 1, "Expected hard errors for P-FAKE-99, got none")
        finally:
            mod.KNOWN_FAILURES_PATH = original  # type: ignore[assignment]


    # --- D1b: structural adversarial tests for heading variants ---

    def _make_fixture(self, root: Path, corrige: str, bareme: str) -> Path:
        """Create a minimal sequence fixture and return the root."""
        d = root / "P00"
        d.mkdir(exist_ok=True)
        (d / "P00_cours_test.md").write_text(
            "Objectif O1\nP-LANG-01\nErreur fréquente EF1\n", encoding="utf-8")
        (d / "P00_trace_test.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
        (d / "P00_td_test.md").write_text(
            "### Exercice 1\nP-LANG-01\n### Exercice 2\nP-LANG-01\n", encoding="utf-8")
        (d / "P00_tp_test.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
        (d / "P00_corrige_test.md").write_text(corrige, encoding="utf-8")
        (d / "P00_evaluation_test.md").write_text(
            "### Question 1\nP-LANG-01\n### Question 2\nP-LANG-01\n", encoding="utf-8")
        (d / "P00_bareme_test.md").write_text(bareme, encoding="utf-8")
        (d / "P00_remediation_test.md").write_text("Activité corrective EF1\n", encoding="utf-8")
        return root

    def test_alt_corrige_missing_exercise_is_rouge(self) -> None:
        """Alt heading format: corrigé with ### Exercice 1 but missing ### Exercice 2 → ROUGE."""
        with tempfile.TemporaryDirectory() as raw:
            root = self._make_fixture(
                Path(raw),
                corrige="### Exercice 1\n- Réponse : 42\n",
                bareme="- Question 1 : 4 points\n- Question 2 : 4 points\n",
            )
            result = alignment.analyze_alignment(root, prefixes=["P00"], program_ids={"P-LANG-01"})
            self.assertTrue(
                any("Exercice 2" in e and "corrigé" in e for e in result.errors),
                f"Expected Exercice 2 sans corrigé, got: {result.errors}",
            )

    def test_alt_bareme_missing_question_is_rouge(self) -> None:
        """Alt heading format: barème with - Question 1 but missing - Question 2 → ROUGE."""
        with tempfile.TemporaryDirectory() as raw:
            root = self._make_fixture(
                Path(raw),
                corrige="### Exercice 1\n- Réponse\n### Exercice 2\n- Réponse\n",
                bareme="- Question 1 : 4 points\n",
            )
            result = alignment.analyze_alignment(root, prefixes=["P00"], program_ids={"P-LANG-01"})
            self.assertTrue(
                any("Question 2" in e and "barème" in e for e in result.errors),
                f"Expected Question 2 sans barème, got: {result.errors}",
            )

    def test_alt_format_complete_is_vert(self) -> None:
        """Both alt heading variants present and complete → VERT."""
        with tempfile.TemporaryDirectory() as raw:
            root = self._make_fixture(
                Path(raw),
                corrige="### Exercice 1\n- Réponse\n### Exercice 2\n- Réponse\n",
                bareme="- Question 1 : 4 points\n- Question 2 : 4 points\n",
            )
            result = alignment.analyze_alignment(root, prefixes=["P00"], program_ids={"P-LANG-01"})
            structural = [e for e in result.errors if "corrigé" in e or "barème" in e]
            self.assertEqual(structural, [], f"Expected no structural errors, got: {structural}")


    # --- E2: adversarial tests for variant file support ---

    def _make_variant_fixture(self, root: Path, variant_cours_fm: str, variant_td_body: str) -> Path:
        """Create a sequence with principal + variant files."""
        d = root / "P00"
        d.mkdir(exist_ok=True)
        # Principal files (P-LANG-01 only)
        (d / "P00_cours_main.md").write_text(
            "Objectif O1\nP-LANG-01\nErreur fréquente EF1\n", encoding="utf-8")
        (d / "P00_trace_main.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
        (d / "P00_td_main.md").write_text("### Exercice 1\nP-LANG-01\n", encoding="utf-8")
        (d / "P00_tp_main.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
        (d / "P00_corrige_main.md").write_text("### Corrigé exercice 1\n", encoding="utf-8")
        (d / "P00_evaluation_main.md").write_text("### Question 1\nP-LANG-01\n", encoding="utf-8")
        (d / "P00_bareme_main.md").write_text("### Barème question 1\n", encoding="utf-8")
        (d / "P00_remediation_main.md").write_text("Activité corrective EF1\n", encoding="utf-8")
        # Variant course file with extra capacity in frontmatter
        (d / "P00_cours_variant.md").write_text(
            variant_cours_fm, encoding="utf-8")
        # Variant TD file
        (d / "P00_td_variant.md").write_text(variant_td_body, encoding="utf-8")
        # Variant evaluation file
        (d / "P00_evaluation_variant.md").write_text(variant_td_body, encoding="utf-8")
        return root

    def test_variant_only_capacity_not_in_body_is_rouge(self) -> None:
        """(a) Capacity declared ONLY on variant file, not mentioned in any body → ROUGE."""
        with tempfile.TemporaryDirectory() as raw:
            root = self._make_variant_fixture(
                Path(raw),
                variant_cours_fm="---\ntitle: v\nofficial_program:\n  capacities:\n    - P-EXTRA-99\n---\nVariant content\n",
                variant_td_body="### Exercice 1\nSome work without the ID\n",
            )
            result = alignment.analyze_alignment(root, prefixes=["P00"], program_ids={"P-LANG-01", "P-EXTRA-99"})
            extra_errors = [e for e in result.errors if "P-EXTRA-99" in e]
            self.assertTrue(
                any("non travaillée" in e for e in extra_errors),
                f"Expected P-EXTRA-99 non travaillée, got: {result.errors}",
            )

    def test_variant_capacity_in_variant_body_is_vert(self) -> None:
        """(b) Capacity declared on variant AND mentioned in variant body → VERT."""
        with tempfile.TemporaryDirectory() as raw:
            root = self._make_variant_fixture(
                Path(raw),
                variant_cours_fm="---\ntitle: v\nofficial_program:\n  capacities:\n    - P-EXTRA-99\n---\nP-EXTRA-99 in course\n",
                variant_td_body="### Exercice 1\nExercice sur P-EXTRA-99\n",
            )
            result = alignment.analyze_alignment(root, prefixes=["P00"], program_ids={"P-LANG-01", "P-EXTRA-99"})
            extra_errors = [e for e in result.errors if "P-EXTRA-99" in e]
            self.assertEqual(extra_errors, [], f"Expected no errors for P-EXTRA-99, got: {extra_errors}")

    def test_principal_capacity_in_variant_body_is_vert(self) -> None:
        """(c) Capacity declared on principal, mentioned in variant body → VERT."""
        with tempfile.TemporaryDirectory() as raw:
            d = Path(raw) / "P00"
            d.mkdir()
            # Principal course declares P-EXTRA-99 in frontmatter
            (d / "P00_cours_main.md").write_text(
                "---\ntitle: t\nofficial_program:\n  capacities:\n    - P-EXTRA-99\n---\n"
                "Objectif O1\nP-LANG-01\nErreur fréquente EF1\n", encoding="utf-8")
            (d / "P00_trace_main.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
            (d / "P00_td_main.md").write_text("### Exercice 1\nP-LANG-01\n", encoding="utf-8")
            # Variant TD mentions P-EXTRA-99
            (d / "P00_td_variant.md").write_text("### Exercice 1\nP-EXTRA-99 exercé ici\n", encoding="utf-8")
            (d / "P00_tp_main.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
            (d / "P00_corrige_main.md").write_text("### Corrigé exercice 1\n", encoding="utf-8")
            (d / "P00_evaluation_main.md").write_text("### Question 1\nP-LANG-01\n", encoding="utf-8")
            # Variant eval mentions P-EXTRA-99
            (d / "P00_evaluation_variant.md").write_text("### Question 1\nP-EXTRA-99 évalué ici\n", encoding="utf-8")
            (d / "P00_bareme_main.md").write_text("### Barème question 1\n", encoding="utf-8")
            (d / "P00_remediation_main.md").write_text("Activité corrective EF1\n", encoding="utf-8")

            result = alignment.analyze_alignment(Path(raw), prefixes=["P00"], program_ids={"P-LANG-01", "P-EXTRA-99"})
            extra_errors = [e for e in result.errors if "P-EXTRA-99" in e]
            self.assertEqual(extra_errors, [], f"Expected no errors for P-EXTRA-99, got: {extra_errors}")


    # --- A4-2: permanent symmetry guard on real corpus ---

    def test_gate_coverage_declaration_symmetry(self) -> None:
        """Gate and coverage must see the same set of declared capacity IDs.

        Both sides use the REAL production functions — no reimplementation.
        The gate uses iter_sequence_md_files (shared helper) for collection;
        coverage uses iter_support_evidence. Any asymmetry = ROUGE.
        """
        from scripts.check_first_batch_alignment import (
            CAPACITY_RE as _CAP_RE,
            discover_all_prefixes as _discover,
        )
        from scripts._qa_common import ROOT as _ROOT, iter_sequence_md_files, read_frontmatter as _read_fm
        from scripts._supports_evidence import iter_support_evidence

        # Set A: declarations collected by the gate (shared helper, no kind whitelist)
        gate_caps: set[str] = set()
        for prefix in _discover():
            for fp in iter_sequence_md_files(prefix, _ROOT):
                fm = _read_fm(fp)
                official = fm.get("official_program")
                raw = official.get("capacities", []) if isinstance(official, dict) else []
                if isinstance(raw, list):
                    gate_caps |= {str(c) for c in raw if _CAP_RE.fullmatch(str(c))}

        # Set B: declarations seen by coverage (real production iterator)
        cov_caps: set[str] = set()
        for evidence in iter_support_evidence():
            if _CAP_RE.fullmatch(evidence.capacity_id):
                cov_caps.add(evidence.capacity_id)

        only_coverage = sorted(cov_caps - gate_caps)
        only_gate = sorted(gate_caps - cov_caps)
        self.assertEqual(only_coverage, [],
            f"Capacities seen by coverage but NOT by gate (inflation vector): {only_coverage}")
        self.assertEqual(only_gate, [],
            f"Capacities seen by gate but NOT by coverage: {only_gate}")

    # --- A4-3: adversarial tests for TP-only declaration ---

    def test_tp_only_capacity_not_in_body_is_rouge(self) -> None:
        """(a) Capacity declared ONLY on TP frontmatter, absent from all bodies → ROUGE."""
        with tempfile.TemporaryDirectory() as raw:
            d = Path(raw) / "P00"
            d.mkdir()
            (d / "P00_cours_main.md").write_text(
                "Objectif O1\nP-LANG-01\nErreur fréquente EF1\n", encoding="utf-8")
            (d / "P00_trace_main.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
            (d / "P00_td_main.md").write_text("### Exercice 1\nP-LANG-01\n", encoding="utf-8")
            # TP declares P-TP-ONLY-99 in frontmatter only
            (d / "P00_tp_main.md").write_text(
                "---\ntitle: t\nofficial_program:\n  capacities:\n    - P-TP-ONLY-99\n---\n"
                "Objectif O1\nP-LANG-01\n", encoding="utf-8")
            (d / "P00_corrige_main.md").write_text("### Corrigé exercice 1\n", encoding="utf-8")
            (d / "P00_evaluation_main.md").write_text("### Question 1\nP-LANG-01\n", encoding="utf-8")
            (d / "P00_bareme_main.md").write_text("### Barème question 1\n", encoding="utf-8")
            (d / "P00_remediation_main.md").write_text("Activité corrective EF1\n", encoding="utf-8")

            result = alignment.analyze_alignment(Path(raw), prefixes=["P00"],
                program_ids={"P-LANG-01", "P-TP-ONLY-99"})
            tp_errors = [e for e in result.errors if "P-TP-ONLY-99" in e]
            self.assertTrue(
                any("non travaillée" in e for e in tp_errors),
                f"Expected P-TP-ONLY-99 non travaillée, got: {result.errors}")

    def test_tp_only_capacity_in_bodies_is_vert(self) -> None:
        """(b) Capacity declared on TP, mentioned in TP body AND eval body → VERT."""
        with tempfile.TemporaryDirectory() as raw:
            d = Path(raw) / "P00"
            d.mkdir()
            (d / "P00_cours_main.md").write_text(
                "Objectif O1\nP-LANG-01\nErreur fréquente EF1\n", encoding="utf-8")
            (d / "P00_trace_main.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
            (d / "P00_td_main.md").write_text("### Exercice 1\nP-LANG-01\nP-TP-ONLY-99\n", encoding="utf-8")
            (d / "P00_tp_main.md").write_text(
                "---\ntitle: t\nofficial_program:\n  capacities:\n    - P-TP-ONLY-99\n---\n"
                "Objectif O1\nP-LANG-01\nP-TP-ONLY-99 exercé ici\n", encoding="utf-8")
            (d / "P00_corrige_main.md").write_text("### Corrigé exercice 1\n", encoding="utf-8")
            (d / "P00_evaluation_main.md").write_text("### Question 1\nP-LANG-01\nP-TP-ONLY-99\n", encoding="utf-8")
            (d / "P00_bareme_main.md").write_text("### Barème question 1\n", encoding="utf-8")
            (d / "P00_remediation_main.md").write_text("Activité corrective EF1\n", encoding="utf-8")

            result = alignment.analyze_alignment(Path(raw), prefixes=["P00"],
                program_ids={"P-LANG-01", "P-TP-ONLY-99"})
            tp_errors = [e for e in result.errors if "P-TP-ONLY-99" in e]
            self.assertEqual(tp_errors, [], f"Expected no errors for P-TP-ONLY-99, got: {tp_errors}")


    # --- F3: bareme-only adversarial test ---

    def test_bareme_only_capacity_is_collected_and_flagged(self) -> None:
        """Capacity declared ONLY on bareme frontmatter, absent from all bodies → ROUGE.

        This proves the old kind-whitelist (which excluded bareme) would have
        missed it, while the new rglob-based collection catches it.
        """
        with tempfile.TemporaryDirectory() as raw:
            d = Path(raw) / "03_progressions" / "supports" / "premiere" / "P00"
            d.mkdir(parents=True)
            (d / "P00_cours_main.md").write_text(
                "Objectif O1\nP-LANG-01\nErreur fréquente EF1\n", encoding="utf-8")
            (d / "P00_trace_main.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
            (d / "P00_td_main.md").write_text("### Exercice 1\nP-LANG-01\n", encoding="utf-8")
            (d / "P00_tp_main.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
            (d / "P00_corrige_main.md").write_text("### Corrigé exercice 1\n", encoding="utf-8")
            (d / "P00_evaluation_main.md").write_text("### Question 1\nP-LANG-01\n", encoding="utf-8")
            # Bareme declares P-BAR-ONLY-99 — NOT in any other file
            (d / "P00_bareme_main.md").write_text(
                "---\ntitle: b\nofficial_program:\n  capacities:\n    - P-BAR-ONLY-99\n---\n"
                "### Barème question 1\n", encoding="utf-8")
            (d / "P00_remediation_main.md").write_text("Activité corrective EF1\n", encoding="utf-8")

            result = alignment.analyze_alignment(Path(raw), prefixes=["P00"],
                program_ids={"P-LANG-01", "P-BAR-ONLY-99"})
            bar_errors = [e for e in result.errors if "P-BAR-ONLY-99" in e]
            self.assertTrue(
                any("non travaillée" in e for e in bar_errors),
                f"Expected P-BAR-ONLY-99 non travaillée (bareme-only), got: {result.errors}")

    # --- Commit 1 PR C: exact-match known-failures guard ---

    def test_known_failure_prefix_does_not_shadow_suffixed_id(self) -> None:
        """Known-failure for P-FAKE-01 must NOT downgrade error on P-FAKE-01A (prefix collision)."""
        import scripts.check_first_batch_alignment as mod
        original = mod.KNOWN_FAILURES_PATH
        try:
            with tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                kf = root / "known.yml"
                # Allowlist only P-FAKE-01 (NOT P-FAKE-01A)
                kf.write_text(
                    "known_failures:\n  - id: P-FAKE-01\n    prefix: P00\n    reason: test\n    resolution: PR Z\n",
                    encoding="utf-8",
                )
                mod.KNOWN_FAILURES_PATH = kf
                d = root / "P00"
                d.mkdir()
                # Declare BOTH P-FAKE-01 and P-FAKE-01A in frontmatter
                (d / "P00_cours_test.md").write_text(
                    "---\ntitle: t\nofficial_program:\n  capacities:\n    - P-FAKE-01\n    - P-FAKE-01A\n---\n"
                    "Objectif O1\nP-LANG-01\nErreur fréquente EF1\n", encoding="utf-8")
                for kind, content in [
                    ("trace", "Objectif O1\nP-LANG-01\n"),
                    ("td", "### Exercice 1\nP-LANG-01\n"),
                    ("tp", "Objectif O1\nP-LANG-01\n"),
                    ("corrige", "### Corrigé exercice 1\n"),
                    ("evaluation", "### Question 1\nP-LANG-01\n"),
                    ("bareme", "### Barème question 1\n"),
                    ("remediation", "Activité corrective EF1\n"),
                ]:
                    (d / f"P00_{kind}_test.md").write_text(content, encoding="utf-8")

                result = mod.analyze_alignment(root, prefixes=["P00"],
                    program_ids={"P-LANG-01", "P-FAKE-01", "P-FAKE-01A"})
                known = mod._load_known_failures()
                # P-FAKE-01 errors should be WARNING (known)
                # P-FAKE-01A errors should remain HARD (not in known list)
                hard = []
                for e in result.errors:
                    matched_key = None
                    for (prefix, cap_id) in known:
                        import re as _re
                        if e.startswith(f"{prefix}:") and _re.search(r"\b" + _re.escape(cap_id) + r"\b", e):
                            matched_key = (prefix, cap_id)
                            break
                    if matched_key is None:
                        hard.append(e)
                hard_01a = [e for e in hard if "P-FAKE-01A" in e]
                self.assertTrue(len(hard_01a) >= 1,
                    f"P-FAKE-01A must remain hard error (not shadowed by P-FAKE-01), got hard: {hard}")
                # Also verify P-FAKE-01 IS matched (warning, not hard)
                hard_01_exact = [e for e in hard if "P-FAKE-01" in e and "P-FAKE-01A" not in e]
                self.assertEqual(hard_01_exact, [],
                    f"P-FAKE-01 should be warning (known), but found hard: {hard_01_exact}")
        finally:
            mod.KNOWN_FAILURES_PATH = original


    # --- PR A6: rglob collects .md in sub-directories ---

    def test_rglob_collects_subdirectory_md(self) -> None:
        """A .md file in a sub-directory of a sequence should be collected
        by iter_sequence_md_files (rglob), ensuring symmetry with coverage."""
        from scripts._qa_common import iter_sequence_md_files
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            d = root / "P00"
            d.mkdir()
            (d / "P00_cours_test.md").write_text(
                "---\ntitle: t\n---\nBody\n", encoding="utf-8")
            # Sub-directory with a .md
            sub = d / "code"
            sub.mkdir()
            (sub / "P00_extra.md").write_text(
                "---\ntitle: extra\n---\nSub body\n", encoding="utf-8")
            # contracts/ should still be excluded
            contracts = d / "contracts"
            contracts.mkdir()
            (contracts / "contract.md").write_text(
                "---\ntitle: contract\n---\nExcluded\n", encoding="utf-8")

            files = iter_sequence_md_files("P00", root)
            names = [p.name for p in files]
            self.assertIn("P00_cours_test.md", names,
                "Top-level .md must be collected")
            self.assertIn("P00_extra.md", names,
                "Sub-directory .md must be collected by rglob")
            self.assertNotIn("contract.md", names,
                "contracts/ .md must remain excluded")


    def test_exercise_3bis_without_corrige_3bis_is_rouge(self) -> None:
        """Adverse: TD has 'Exercice 3bis' but corrigé lacks it → ROUGE."""
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            directory = root / "P00"
            directory.mkdir()
            (directory / "P00_cours_test.md").write_text(
                "Objectif O1\nCapacité : P-LANG-01\nErreur fréquente EF1\n", encoding="utf-8")
            (directory / "P00_trace_test.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
            (directory / "P00_td_test.md").write_text(
                "### Exercice 3\n### Exercice 3bis\n### Exercice 4\nP-LANG-01\n", encoding="utf-8")
            (directory / "P00_tp_test.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
            (directory / "P00_corrige_test.md").write_text(
                "### Exercice 3\n### Exercice 4\n", encoding="utf-8")
            (directory / "P00_evaluation_test.md").write_text("### Question 1\nP-LANG-01\n", encoding="utf-8")
            (directory / "P00_bareme_test.md").write_text("### Barème question 1\n", encoding="utf-8")
            (directory / "P00_remediation_test.md").write_text("Activité corrective EF1\n", encoding="utf-8")

            result = alignment.analyze_alignment(root, prefixes=["P00"], program_ids={"P-LANG-01"})

            self.assertTrue(
                any("3bis" in error and "corrigé" in error for error in result.errors),
                f"Expected '3bis sans corrigé' error, got: {result.errors}",
            )

    def test_exercise_3bis_with_corrige_3bis_is_vert(self) -> None:
        """T07 case: TD has 'Exercice 3bis' and corrigé has it too → VERT."""
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            directory = root / "P00"
            directory.mkdir()
            (directory / "P00_cours_test.md").write_text(
                "Objectif O1\nCapacité : P-LANG-01\nErreur fréquente EF1\n", encoding="utf-8")
            (directory / "P00_trace_test.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
            (directory / "P00_td_test.md").write_text(
                "### Exercice 3\n### Exercice 3bis\n### Exercice 4\nP-LANG-01\n", encoding="utf-8")
            (directory / "P00_tp_test.md").write_text("Objectif O1\nP-LANG-01\n", encoding="utf-8")
            (directory / "P00_corrige_test.md").write_text(
                "### Exercice 3\n### Exercice 3bis\n### Exercice 4\n", encoding="utf-8")
            (directory / "P00_evaluation_test.md").write_text("### Question 1\nP-LANG-01\n", encoding="utf-8")
            (directory / "P00_bareme_test.md").write_text("### Barème question 1\n", encoding="utf-8")
            (directory / "P00_remediation_test.md").write_text("Activité corrective EF1\n", encoding="utf-8")

            result = alignment.analyze_alignment(root, prefixes=["P00"], program_ids={"P-LANG-01"})

            exercise_errors = [e for e in result.errors if "corrigé" in e and "Exercice" in e]
            self.assertEqual(exercise_errors, [])


if __name__ == "__main__":
    unittest.main()
