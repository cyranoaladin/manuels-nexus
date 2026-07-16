import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pdf_integrity import log_has_missing_asset_warning, fonts_are_embedded  # noqa: E402


def test_log_with_missing_nexus_asset_is_rejected():
    assert log_has_missing_asset_warning("ClassWarning: Nexus asset missing: icons")


def test_pdffonts_output_requires_every_font_to_be_embedded():
    output = """name                                 type              encoding         emb sub uni object ID
------------------------------------ ----------------- ---------------- --- --- --- ---------
NATGLQ+JetBrainsMono-Bold            CID Type 0C       Identity-H       yes yes yes     66  0
TMHVPV+MSAM10                        Type 1            Builtin          yes yes no      93  0
"""
    assert fonts_are_embedded(output)
    assert not fonts_are_embedded(output.replace("yes yes yes     66", "no yes yes     66"))


def test_verify_pdf_reports_missing_pdffonts_without_traceback(tmp_path, monkeypatch, capsys):
    import pdf_integrity

    pdf = tmp_path / "test.pdf"
    log = tmp_path / "test.log"
    pdf.touch()
    log.write_text("", encoding="utf-8")

    def missing_command(*_args, **_kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(pdf_integrity.subprocess, "run", missing_command)

    assert pdf_integrity.verify_pdf(pdf, log) == 1
    assert "pdffonts (poppler-utils) introuvable" in capsys.readouterr().out


def test_missing_asset_in_log_triggers_verify_failure(tmp_path):
    """Unit : un log contenant le warning Nexus asset missing => verify_pdf = 1."""
    import pdf_integrity

    pdf = tmp_path / "chapter.pdf"
    log = tmp_path / "chapter.log"
    pdf.touch()
    log.write_text(
        "Some preamble output\n"
        "ClassWarning: Nexus asset missing: nexus-icons.tex not found\n"
        "Output written on chapter.pdf\n",
        encoding="utf-8",
    )
    assert pdf_integrity.verify_pdf(pdf, log) == 1


import shutil
import pytest

_HAS_LUALATEX = shutil.which("lualatex") is not None


@pytest.mark.skipif(not _HAS_LUALATEX, reason="lualatex absent de cet environnement")
def test_missing_asset_produces_warning_in_real_compilation(tmp_path):
    """F.1 — bout-en-bout reel : retirer nexus-icons.tex, compiler, verifier
    que le log contient le warning ET que verify_pdf retourne 1."""
    import subprocess
    import pdf_integrity

    # Copier gabarits/ en retirant nexus-icons.tex
    gabarits_src = ROOT / "gabarits"
    gabarits_dst = tmp_path / "gabarits"
    shutil.copytree(gabarits_src, gabarits_dst)
    (gabarits_dst / "nexus-icons.tex").unlink()

    # Document minimal
    doc = tmp_path / "minimal.tex"
    doc.write_text(
        "\\documentclass{nexus-manuel}\n"
        "\\begin{document}\n"
        "Page de test sans icons.\n"
        "\\end{document}\n",
        encoding="utf-8",
    )

    # Compiler avec TEXINPUTS pointant vers la copie
    import os
    env = os.environ.copy()
    env["TEXINPUTS"] = f"{gabarits_dst}:{env.get('TEXINPUTS', '')}"
    subprocess.run(
        ["lualatex", "-interaction=nonstopmode",
         f"-output-directory={tmp_path}", str(doc)],
        capture_output=True, cwd=tmp_path, env=env,
    )

    log_path = tmp_path / "minimal.log"
    pdf_path = tmp_path / "minimal.pdf"
    assert log_path.exists(), "le log de compilation n'a pas ete produit"

    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    assert "Nexus asset missing" in log_text, (
        "le warning Nexus asset missing n'apparait pas dans le log"
    )

    assert pdf_integrity.verify_pdf(pdf_path, log_path) == 1, (
        "verify_pdf aurait du retourner 1 (asset manquant)"
    )


def test_specimen_compiles_with_exit_zero():
    """F.1 — contre-epreuve : make specimen = 0 quand le gabarit est complet."""
    import subprocess

    result = subprocess.run(
        ["make", "specimen"],
        capture_output=True, text=True, errors="replace",
        cwd=ROOT,
    )
    assert result.returncode == 0, f"make specimen failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"
