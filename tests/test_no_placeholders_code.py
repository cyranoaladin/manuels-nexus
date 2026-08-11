from __future__ import annotations

import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

import scripts.check_no_placeholders_code as checker


class ContractualizedStarterTests(unittest.TestCase):
    @contextmanager
    def checker_root(self, root: Path):
        previous = checker.ROOT
        checker.ROOT = root
        try:
            yield
        finally:
            checker.ROOT = previous

    def write_contractualized_starter(
        self,
        root: Path,
        *,
        linked: bool = True,
        expected_tests: bool = True,
        correction: bool = True,
    ) -> Path:
        sequence = root / "03_progressions" / "supports" / "premiere" / "P99"
        code = sequence / "code"
        code.mkdir(parents=True)
        starter = code / "P99_starter_demo.py"
        starter.write_text(
            '"""Starter eleve du TP P99."""\n\n'
            "def resoudre() -> int:\n"
            '    """A completer par l\'eleve."""\n'
            '    raise NotImplementedError("a completer")\n',
            encoding="utf-8",
        )
        if linked:
            (sequence / "P99_tp_demo.md").write_text(
                "---\ndocument_type: tp\n---\n"
                "# TP\nFichier fourni : `code/P99_starter_demo.py`.\n",
                encoding="utf-8",
            )
        if expected_tests:
            (code / "P99_tests_attendus_demo.py").write_text(
                "def test_reference() -> None:\n    assert 1 == 1\n",
                encoding="utf-8",
            )
        if correction:
            (code / "P99_corrige_professeur_demo.py").write_text(
                "def resoudre() -> int:\n    return 1\n",
                encoding="utf-8",
            )
        return starter

    def errors_for(self, root: Path, path: Path) -> list[str]:
        with self.checker_root(root):
            return checker.check_file(path)

    def test_contractualized_starter_with_not_implemented_error_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            starter = self.write_contractualized_starter(root)

            self.assertEqual(self.errors_for(root, starter), [])

    def test_unreferenced_starter_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            starter = self.write_contractualized_starter(root, linked=False)

            self.assertTrue(any("NotImplementedError" in error for error in self.errors_for(root, starter)))

    def test_starter_without_expected_tests_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            starter = self.write_contractualized_starter(root, expected_tests=False)

            self.assertTrue(any("NotImplementedError" in error for error in self.errors_for(root, starter)))

    def test_starter_without_teacher_correction_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            starter = self.write_contractualized_starter(root, correction=False)

            self.assertTrue(any("NotImplementedError" in error for error in self.errors_for(root, starter)))

    def test_not_implemented_error_in_teacher_correction_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            correction = (
                root
                / "03_progressions"
                / "supports"
                / "terminale"
                / "T99"
                / "code"
                / "T99_corrige_professeur_demo.py"
            )
            correction.parent.mkdir(parents=True)
            correction.write_text("def corriger() -> None:\n    raise NotImplementedError\n", encoding="utf-8")

            self.assertTrue(any("NotImplementedError" in error for error in self.errors_for(root, correction)))

    def test_not_implemented_error_in_production_script_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "scripts" / "demo.py"
            script.parent.mkdir(parents=True)
            script.write_text("def controler() -> None:\n    raise NotImplementedError\n", encoding="utf-8")

            self.assertTrue(any("NotImplementedError" in error for error in self.errors_for(root, script)))

    def test_pass_in_production_script_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "scripts" / "demo.py"
            script.parent.mkdir(parents=True)
            script.write_text("def controler() -> None:\n    pass\n", encoding="utf-8")

            self.assertTrue(any("instruction pass" in error for error in self.errors_for(root, script)))

    def test_pass_in_expected_tests_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            expected = root / "03_progressions" / "supports" / "premiere" / "P99" / "code" / "P99_tests_attendus_demo.py"
            expected.parent.mkdir(parents=True)
            expected.write_text("def test_demo() -> None:\n    pass\n", encoding="utf-8")

            self.assertTrue(any("instruction pass" in error for error in self.errors_for(root, expected)))

    def test_real_t10_and_t17_starters_are_accepted(self) -> None:
        root = Path(__file__).resolve().parents[1]
        t10 = root / "03_progressions" / "supports" / "terminale" / "T10" / "code" / "T10_starter_sql_select_where_join.py"
        t17 = root / "03_progressions" / "supports" / "terminale" / "T17" / "code" / "T17_starter_programmation_dynamique.py"

        self.assertEqual(checker.check_file(t10), [])
        self.assertEqual(checker.check_file(t17), [])

    def test_real_t10_expected_tests_and_td_quality_script_have_no_placeholder(self) -> None:
        root = Path(__file__).resolve().parents[1]
        expected = root / "03_progressions" / "supports" / "terminale" / "T10" / "code" / "T10_tests_attendus_sql_select_where_join.py"
        quality = root / "scripts" / "check_linked_td_quality.py"

        self.assertEqual(checker.check_file(expected), [])
        self.assertEqual(checker.check_file(quality), [])


if __name__ == "__main__":
    unittest.main()
