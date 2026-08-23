"""Regression: Math and NSI assemblers must not share local dependencies."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("probe_cwd", ("repository", "external"))
@pytest.mark.parametrize("order", ("math_then_nsi", "nsi_then_math"))
def test_manual_assemblers_are_import_order_independent(
    order: str,
    probe_cwd: str,
    tmp_path: Path,
) -> None:
    script = r"""
import importlib
from pathlib import Path
import sys

repository_root = Path(sys.argv[1]).resolve()
math_root = repository_root / "Mathematiques" / "manuel-maths"
nsi_root = repository_root / "NSI"
math_scripts = str(math_root / "scripts")
nsi_scripts = str(nsi_root / "scripts")
sys.path.insert(0, str(repository_root))

if sys.argv[2] == "math_then_nsi":
    sys.path.insert(0, math_scripts)
    math_assemble = importlib.import_module("assemble")
    math_assemble_manuel = importlib.import_module("assemble_manuel")
    nsi_assemble = importlib.import_module("NSI.scripts.assemble")
    nsi_assemble_manuel = importlib.import_module("NSI.scripts.assemble_manuel")
    nsi_verify_python = importlib.import_module("NSI.scripts.verify_python")
else:
    nsi_assemble = importlib.import_module("NSI.scripts.assemble")
    nsi_assemble_manuel = importlib.import_module("NSI.scripts.assemble_manuel")
    nsi_verify_python = importlib.import_module("NSI.scripts.verify_python")
    sys.path.insert(0, math_scripts)
    math_assemble = importlib.import_module("assemble")
    math_assemble_manuel = importlib.import_module("assemble_manuel")

assert Path(math_assemble.ROOT).resolve() == math_root
assert Path(math_assemble_manuel.ROOT).resolve() == math_root
assert Path(nsi_assemble.ROOT).resolve() == nsi_root
assert Path(nsi_assemble_manuel.ROOT).resolve() == nsi_root
assert Path(nsi_verify_python.ROOT).resolve() == nsi_root

math_common = importlib.import_module("common")
math_pdf_integrity = importlib.import_module("pdf_integrity")
nsi_common = importlib.import_module("NSI.scripts.common")
nsi_pdf_integrity = importlib.import_module("NSI.scripts.pdf_integrity")
assert math_common is not nsi_common
assert math_pdf_integrity is not nsi_pdf_integrity
assert Path(math_common.__file__).resolve().is_relative_to(math_scripts)
assert Path(math_pdf_integrity.__file__).resolve().is_relative_to(math_scripts)
assert Path(nsi_common.__file__).resolve().is_relative_to(nsi_scripts)
assert Path(nsi_pdf_integrity.__file__).resolve().is_relative_to(nsi_scripts)
assert math_assemble_manuel.verify_pdf is math_pdf_integrity.verify_pdf
assert nsi_assemble_manuel.legacy is nsi_assemble
assert nsi_assemble.verify_pdf is nsi_pdf_integrity.verify_pdf
"""
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    cwd = REPOSITORY_ROOT if probe_cwd == "repository" else tmp_path
    completed = subprocess.run(
        [sys.executable, "-c", script, str(REPOSITORY_ROOT), order],
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
