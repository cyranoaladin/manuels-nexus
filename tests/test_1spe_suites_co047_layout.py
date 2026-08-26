from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "Mathematiques" / "manuel-maths"
CORRECTION = (
    MANUAL
    / "chapitres"
    / "1SPE-SUITES"
    / "corriges"
    / "1SPE-SUITES-CO-047.tex"
)


def _compile_correction(tmp_path: Path, run: int) -> str:
    output = tmp_path / f"run-{run}"
    output.mkdir()
    fixture = tmp_path / f"co047-layout-{run}.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel-v5}
\usepackage{gabarits/nexus-charte-v6}
\nxVersionProfesseurtrue
\begin{document}
\rubrique{Corrigés}
\input{chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-047.tex}
\end{document}
""",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment["NEXUS_MARGIN_VARIANT"] = "professeur"
    completed = subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={output}",
            str(fixture),
        ],
        cwd=MANUAL,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stdout[-8000:] + completed.stderr
    return (output / f"co047-layout-{run}.log").read_text(
        encoding="utf-8", errors="replace"
    )


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_co047_teacher_layout_is_repeatably_free_of_overfull_boxes(
    tmp_path: Path,
) -> None:
    source = CORRECTION.read_text(encoding="utf-8")
    forbidden_workarounds = (
        r"\sloppy",
        r"\hfuzz",
        r"\hbadness",
        r"\resizebox",
        r"\scalebox",
        r"\tiny",
        r"\scriptsize",
        r"\footnotesize",
        r"\small",
    )

    assert all(workaround not in source for workaround in forbidden_workarounds)
    logs = [_compile_correction(tmp_path, run) for run in (1, 2)]
    assert all(r"Overfull \hbox" not in log for log in logs)
