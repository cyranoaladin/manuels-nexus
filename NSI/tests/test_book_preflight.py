"""Tests du preflight réservé aux PDF de livres élèves."""
from pathlib import Path
import sys

import pytest

fitz = pytest.importorskip("fitz")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import pdf_integrity  # noqa: E402


def _write_pdf(
    path: Path,
    *,
    text: str = "Contenu élève public.",
    metadata: dict[str, str] | None = None,
    outline: bool = True,
    link: bool = True,
) -> None:
    values = {
        "title": "Manuel test",
        "author": "Nexus Réussite",
        "subject": "NSI",
        "keywords": "NSI, test",
    }
    if metadata is not None:
        values.update(metadata)
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    document.set_metadata(values)
    if outline:
        document.set_toc([[1, "Chapitre test", 1]])
    if link:
        page.insert_link(
            {
                "kind": fitz.LINK_GOTO,
                "from": fitz.Rect(70, 60, 180, 82),
                "page": 0,
                "to": fitz.Point(72, 72),
            }
        )
    document.save(path)
    document.close()


def _preflight(tmp_path: Path, **pdf_options) -> int:
    pdf = tmp_path / "book.pdf"
    log = tmp_path / "book.log"
    _write_pdf(pdf, **pdf_options)
    log.write_text("Compilation propre.\n", encoding="utf-8")
    return pdf_integrity.preflight_book_pdf(pdf, log)


def test_preflight_book_pdf_accepts_complete_student_book(tmp_path):
    assert _preflight(tmp_path) == 0


def test_preflight_book_pdf_rejects_missing_log(tmp_path):
    pdf = tmp_path / "book.pdf"
    _write_pdf(pdf)

    assert pdf_integrity.preflight_book_pdf(pdf, tmp_path / "missing.log") == 1


@pytest.mark.parametrize(
    "diagnostic",
    [
        "! LaTeX Error: échec",
        "Fatal error occurred",
        "Overfull \\hbox (2.0pt too wide)",
        "Overfull \\vbox (2.0pt too high)",
        "Underfull \\hbox (badness 10000)",
        "Underfull \\vbox (badness 10000)",
        "! Undefined control sequence.",
        "Missing character: There is no x",
        "Nexus asset missing: logo.pdf",
    ],
)
def test_preflight_book_pdf_rejects_latex_diagnostics(tmp_path, diagnostic):
    pdf = tmp_path / "book.pdf"
    log = tmp_path / "book.log"
    _write_pdf(pdf)
    log.write_text(diagnostic, encoding="utf-8")

    assert pdf_integrity.preflight_book_pdf(pdf, log) == 1


@pytest.mark.parametrize("field", ["title", "author", "subject", "keywords"])
def test_preflight_book_pdf_rejects_empty_metadata(tmp_path, field):
    assert _preflight(tmp_path, metadata={field: ""}) == 1


def test_preflight_book_pdf_rejects_empty_outline(tmp_path):
    assert _preflight(tmp_path, outline=False) == 1


def test_preflight_book_pdf_rejects_pdf_without_links(tmp_path):
    assert _preflight(tmp_path, link=False) == 1


@pytest.mark.parametrize(
    "leak",
    [
        "Corrigé",
        "Corrigés",
        "Barème indicatif",
        "Réponse attendue",
        "1NSI-INTERNE",
    ],
)
def test_preflight_book_pdf_rejects_student_leaks(tmp_path, leak):
    assert _preflight(tmp_path, text=f"Contenu public. {leak}") == 1


def test_preflight_book_pdf_rejects_unaccented_corriges_heading(tmp_path):
    assert _preflight(tmp_path, text="corriges") == 1


def test_preflight_book_pdf_allows_instruction_to_correct(tmp_path):
    assert (
        _preflight(
            tmp_path,
            text=(
                "Corrige puis corriger le programme. Tu corriges aussi un autre "
                "programme et étudies la version corrigée."
            ),
        )
        == 0
    )


@pytest.mark.parametrize("text", ["Tu corriges", "Tu corriges."])
def test_preflight_book_pdf_allows_corriges_as_a_verb(tmp_path, text):
    assert _preflight(tmp_path, text=text) == 0
