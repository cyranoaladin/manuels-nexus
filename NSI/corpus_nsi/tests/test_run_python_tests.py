from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.run_python_tests as run_python_tests


class RunPythonTestsTest(unittest.TestCase):
    def test_empty_test_directory_is_failure(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "tests").mkdir()

            with self.assertRaises(SystemExit) as context:
                run_python_tests.main(root=root, min_tests=1)

            self.assertEqual(context.exception.code, 1)

    def test_present_tests_pass_when_minimum_is_met(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            tests = root / "tests"
            tests.mkdir()
            (tests / "test_demo.py").write_text(
                "import unittest\n\n"
                "class DemoTest(unittest.TestCase):\n"
                "    def test_true(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )

            run_python_tests.main(root=root, min_tests=1)

    def test_venv_vendor_tests_are_not_collected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            tests = root / "tests"
            tests.mkdir()
            (tests / "test_demo.py").write_text(
                "import unittest\n\n"
                "class DemoTest(unittest.TestCase):\n"
                "    def test_true(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            vendor_tests = root / ".venv" / "lib" / "python3.12" / "site-packages" / "vendor" / "tests"
            vendor_tests.mkdir(parents=True)
            (vendor_tests / "test_vendor.py").write_text(
                "raise RuntimeError('vendor tests must not be imported')\n",
                encoding="utf-8",
            )

            run_python_tests.main(root=root, min_tests=1)


if __name__ == "__main__":
    unittest.main()
