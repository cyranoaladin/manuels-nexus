#!/usr/bin/env python3
"""Run unit tests in repository test files."""

from __future__ import annotations

from pathlib import Path
import importlib.util
import unittest
import sys

ROOT = Path(__file__).resolve().parents[1]
MIN_TESTS = 60
EXCLUDED_TEST_PATH_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "01_build_reports",
    "build",
    "dist",
    "site-packages",
}


def is_repository_test_file(path: Path, root: Path) -> bool:
    if path.suffix != ".py" or not path.name.startswith("test"):
        return False
    relative = path.relative_to(root)
    if "tests" not in relative.parts:
        return False
    return not any(part in EXCLUDED_TEST_PATH_PARTS for part in relative.parts)


def load_tests_from_file(path: Path) -> unittest.TestSuite:
    name = 'nsitest_' + path.stem.replace('-', '_')
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossible de charger le fichier de test: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return unittest.defaultTestLoader.loadTestsFromModule(module)


def main(root: Path = ROOT, min_tests: int = MIN_TESTS) -> None:
    suite = unittest.TestSuite()
    for path in sorted(root.rglob('test*.py')):
        if not is_repository_test_file(path, root):
            continue
        suite.addTests(load_tests_from_file(path))

    if suite.countTestCases() == 0:
        print('NO TESTS')
        raise SystemExit(1)
    if suite.countTestCases() < min_tests:
        print(f"run_python_tests: KO - tests insuffisants ({suite.countTestCases()}/{min_tests})")
        raise SystemExit(1)

    result = unittest.TestResult()
    suite.run(result)
    print(f"run_python_tests: tests exécutés = {result.testsRun}")
    for test, traceback in result.failures:
        print(f"FAIL: {test}")
        print(traceback)
    for test, traceback in result.errors:
        print(f"ERROR: {test}")
        print(traceback)
    if not result.wasSuccessful():
        print('run_python_tests: KO')
        raise SystemExit(1)
    print('run_python_tests: PASS')


if __name__ == '__main__':
    main()
