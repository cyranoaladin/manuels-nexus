from __future__ import annotations

import configparser
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_root_pytest_ruff_and_coverage_exclude_nested_clone() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    pytest_options = pyproject["tool"]["pytest"]["ini_options"]
    ruff_options = pyproject["tool"]["ruff"]

    assert "nsi-enseignement" in pytest_options["norecursedirs"]
    assert "nsi-enseignement" in ruff_options["exclude"]

    coverage_path = ROOT / ".coveragerc"
    assert coverage_path.exists()
    parser = configparser.ConfigParser()
    parser.read(coverage_path, encoding="utf-8")
    omit_entries = "\n".join(parser["run"].get("omit", "").splitlines())
    assert "nsi-enseignement" in omit_entries


def test_root_pytest_collect_only_omits_nested_clone() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=120,
    )

    assert result.returncode == 0, result.stdout
    collected_tests = [
        line
        for line in result.stdout.splitlines()
        if line.endswith(".py") or "::" in line
    ]
    assert collected_tests
    assert all("nsi-enseignement/" not in line for line in collected_tests)
