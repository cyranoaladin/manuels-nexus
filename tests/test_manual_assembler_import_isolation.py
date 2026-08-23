"""Regression: Math and NSI assemblers must not share local dependencies."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("order", ("math_then_nsi", "nsi_then_math"))
def test_manual_assemblers_are_import_order_independent(order: str) -> None:
    script = r"""
import importlib
from pathlib import Path
import sys

repository_root = Path(sys.argv[1]).resolve()
math_root = repository_root / "Mathematiques" / "manuel-maths"
nsi_root = repository_root / "NSI"
math_scripts = str(math_root / "scripts")
nsi_scripts = str(nsi_root / "scripts")

if sys.argv[2] == "math_then_nsi":
    sys.path.insert(0, math_scripts)
    math_assemble = importlib.import_module("assemble")
    nsi_assemble = importlib.import_module("NSI.scripts.assemble")
    nsi_verify_python = importlib.import_module("NSI.scripts.verify_python")
else:
    sys.path.insert(0, nsi_scripts)
    nsi_assemble = importlib.import_module("NSI.scripts.assemble")
    nsi_verify_python = importlib.import_module("NSI.scripts.verify_python")
    sys.path.insert(0, math_scripts)
    math_assemble = importlib.import_module("assemble")

assert Path(math_assemble.ROOT).resolve() == math_root
assert Path(nsi_assemble.ROOT).resolve() == nsi_root
assert Path(nsi_verify_python.ROOT).resolve() == nsi_root
"""
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, "-c", script, str(REPOSITORY_ROOT), order],
        cwd=REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
