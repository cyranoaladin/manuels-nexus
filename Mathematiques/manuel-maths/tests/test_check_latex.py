import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_latex import compile_tex_files  # noqa: E402


def test_compile_tex_files_returns_nonzero_when_pdflatex_fails(tmp_path):
    source = tmp_path / "objet.tex"
    source.write_text(r"\section{Objet invalide}", encoding="utf-8")
    calls = []

    def failing_runner(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=1, stdout="! Undefined control sequence.", stderr="")

    code = compile_tex_files([source], tmp_path, runner=failing_runner)

    assert code == 1
    assert calls
    assert "-interaction=nonstopmode" in calls[0][0]
    assert "-halt-on-error" in calls[0][0]
