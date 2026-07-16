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
    """E.3.1 — bout-en-bout : un asset du tronc absent produit warning => verify_pdf = 1."""
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


def test_specimen_compiles_with_exit_zero():
    """E.3.1 — contre-epreuve : make specimen = 0 quand le gabarit est complet."""
    import subprocess

    result = subprocess.run(
        ["make", "specimen"],
        capture_output=True, text=True, errors="replace",
        cwd=ROOT,
    )
    assert result.returncode == 0, f"make specimen failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"
