"""Contrats Red des fuites réellement présentes dans les PDF élèves suivis."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


MANUAL_ROOT = Path(__file__).resolve().parents[1]


def _student_pdf_text(relative_path: str) -> str:
    pdf = MANUAL_ROOT / relative_path
    assert pdf.is_file(), f"PDF élève suivi absent : {pdf}"
    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        check=False,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip(), "extraction PDF élève vide"
    return completed.stdout


def test_p0_1spe_student_pdf_contains_no_teacher_pages_or_provisional_refs() -> None:
    text = _student_pdf_text("build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf")
    forbidden = [
        marker
        for marker in (
            "Correction et diagnostics",
            "Réponses correctes",
            "(renvois exercices M",
        )
        if marker in text
    ]
    assert not forbidden, f"fuites 1SPE élève détectées : {forbidden}"


def test_p0_tspe_student_pdf_contains_no_teacher_key_bareme_or_internal_id() -> None:
    text = _student_pdf_text(
        "build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf"
    )
    patterns = {
        "clé de correction": r"\bcl[eé]\s+de\s+correction\b",
        "barème enseignant": r"\bbar[èe]me\b",
        "identifiant interne": r"\bTSPE-[A-Z0-9]+(?:-[A-Z0-9]+)*\b",
    }
    found = [
        reason
        for reason, pattern in patterns.items()
        if re.search(pattern, text, re.IGNORECASE)
    ]
    assert not found, f"fuites TSPE élève détectées : {found}"
