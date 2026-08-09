"""Role-aware regression tests for the shared book PDF preflight."""

from __future__ import annotations

from pathlib import Path
import sys

import fitz
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import pdf_integrity  # noqa: E402


def _write_pdf(
    path: Path,
    *,
    text: str = "Public content.",
    missing_metadata: str | None = None,
    outline: bool = True,
    link: bool = True,
) -> None:
    metadata = {
        "title": "Test manual",
        "author": "Nexus Reussite",
        "subject": "NSI",
        "keywords": "NSI, test",
    }
    if missing_metadata:
        metadata[missing_metadata] = ""
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    document.set_metadata(metadata)
    if outline:
        document.set_toc([[1, "Test chapter", 1]])
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


def _paths(tmp_path: Path, **pdf_options) -> tuple[Path, Path]:
    pdf = tmp_path / "manual.pdf"
    log = tmp_path / "manual.log"
    _write_pdf(pdf, **pdf_options)
    log.write_text("Clean compilation.\n", encoding="utf-8")
    return pdf, log


def test_student_leak_check_defaults_to_enabled(tmp_path):
    pdf, log = _paths(tmp_path, text="Corrigé complet.")

    assert any(
        issue.startswith("Fuite version")
        for issue in pdf_integrity.book_preflight_issues(pdf, log)
    )
    assert pdf_integrity.preflight_book_pdf(pdf, log) == 1


def test_teacher_role_disables_only_student_leak_check(tmp_path):
    pdf, log = _paths(tmp_path, text="Corrigé complet. Barème indicatif.")

    assert pdf_integrity.book_preflight_issues(
        pdf, log, check_student_leaks=False
    ) == []
    assert pdf_integrity.preflight_book_pdf(
        pdf, log, check_student_leaks=False
    ) == 0


@pytest.mark.parametrize(
    ("case", "options"),
    [
        ("metadata", {"missing_metadata": "author"}),
        ("outline", {"outline": False}),
        ("links", {"link": False}),
    ],
)
def test_teacher_role_keeps_common_pdf_checks(tmp_path, case, options):
    pdf, log = _paths(tmp_path, **options)

    issues = pdf_integrity.book_preflight_issues(
        pdf, log, check_student_leaks=False
    )

    assert issues, case


def test_teacher_role_keeps_log_checks(tmp_path):
    pdf, log = _paths(tmp_path)
    log.write_text("! LaTeX Error: broken\n", encoding="utf-8")

    assert pdf_integrity.preflight_book_pdf(
        pdf, log, check_student_leaks=False
    ) == 1


def test_teacher_role_keeps_readability_check(tmp_path):
    pdf = tmp_path / "manual.pdf"
    log = tmp_path / "manual.log"
    pdf.write_bytes(b"not a PDF")
    log.write_text("Clean compilation.\n", encoding="utf-8")

    assert pdf_integrity.preflight_book_pdf(
        pdf, log, check_student_leaks=False
    ) == 1
