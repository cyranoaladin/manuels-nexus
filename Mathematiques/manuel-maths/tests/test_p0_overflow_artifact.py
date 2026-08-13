"""Contrat Red des débordements produits par le master élève 1SPE réel."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


MANUAL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MANUAL_ROOT / "scripts"))

import assemble_manuel  # noqa: E402


def test_p0_real_1spe_student_master_produces_no_overfull(tmp_path) -> None:
    master = assemble_manuel.render_master("eleve", "0" * 32)
    tex_path = tmp_path / "MANUEL_1SPE_eleve.tex"
    tex_path.write_text(master, encoding="utf-8")
    environment = os.environ.copy()
    environment["TEXMFVAR"] = str(tmp_path / "texmf-var")
    command = [
        "lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={tmp_path}",
        str(tex_path),
    ]

    try:
        for pass_number in range(1, 4):
            completed = subprocess.run(
                command,
                cwd=MANUAL_ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
                errors="replace",
                timeout=300,
            )
            assert completed.returncode == 0, (
                f"LuaLaTeX passe {pass_number} en échec :\n"
                f"{completed.stdout[-3000:]}\n{completed.stderr[-3000:]}"
            )
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        pytest.fail(f"compilation contractuelle indisponible : {error}")

    log_path = tmp_path / "MANUEL_1SPE_eleve.log"
    assert log_path.is_file(), "journal contractuel absent"
    log = log_path.read_text(encoding="utf-8", errors="replace")
    counts = {
        "Overfull \\hbox": log.count("Overfull \\hbox"),
        "Overfull \\vbox": log.count("Overfull \\vbox"),
    }
    assert not any(counts.values()), f"débordements 1SPE élève : {counts}"
