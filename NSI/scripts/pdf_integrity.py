"""Gates d'intégrité des sorties LuaLaTeX."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

import fitz


MISSING_ASSET = "Nexus asset missing:"
MISSING_CHARACTER = "Missing character:"
BOOK_LOG_DIAGNOSTICS = (
    "! LaTeX Error",
    "Fatal error",
    "Emergency stop",
    "Overfull \\hbox",
    "Overfull \\vbox",
    "Underfull \\hbox",
    "Underfull \\vbox",
    "Undefined control sequence",
    MISSING_ASSET,
    MISSING_CHARACTER,
)
BOOK_METADATA_FIELDS = ("title", "author", "subject", "keywords")
BOOK_STUDENT_LEAK = re.compile(
    r"\bcorrigé\b|barème indicatif|réponse attendue|1NSI-",
    re.IGNORECASE,
)


def log_has_missing_asset_warning(log: str) -> bool:
    return MISSING_ASSET in log


def log_has_missing_character_warning(log: str) -> bool:
    return MISSING_CHARACTER in log


def fonts_are_embedded(output: str) -> bool:
    lines = [line.split() for line in output.splitlines()[2:] if line.strip()]
    for fields in lines:
        if len(fields) < 5 or fields[-5] != "yes":
            return False
        if fields[-4] != "yes":
            print(f"Avertissement : police non sous-ensemblée ({' '.join(fields[:-5])}).")
    return bool(lines)


def book_preflight_issues(
    pdf: Path,
    log: Path,
    *,
    check_student_leaks: bool = True,
) -> list[str]:
    issues = []
    try:
        log_text = log.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        issues.append(f"Journal LaTeX introuvable : {log}")
        log_text = ""
    for diagnostic in BOOK_LOG_DIAGNOSTICS:
        if diagnostic.lower() in log_text.lower():
            issues.append(f"Diagnostic LaTeX interdit : {diagnostic}")

    try:
        with fitz.open(pdf) as document:
            metadata = document.metadata or {}
            for field in BOOK_METADATA_FIELDS:
                if not str(metadata.get(field, "")).strip():
                    issues.append(f"Métadonnée PDF vide : {field}")
            if not document.get_toc(simple=True):
                issues.append("Outline PDF vide.")
            if not any(page.get_links() for page in document):
                issues.append("Aucun lien PDF.")
            try:
                text = "\n".join(page.get_text() for page in document)
            except (RuntimeError, ValueError) as error:
                issues.append(f"Extraction texte PDF impossible : {error}")
            else:
                if check_student_leaks:
                    leak = BOOK_STUDENT_LEAK.search(text)
                    if leak:
                        issues.append(f"Fuite version élève : {leak.group(0)}")
    except (FileNotFoundError, fitz.FileDataError) as error:
        issues.append(f"PDF illisible : {error}")
    return issues


def preflight_book_pdf(
    pdf: Path,
    log: Path,
    *,
    check_student_leaks: bool = True,
) -> int:
    issues = book_preflight_issues(
        pdf,
        log,
        check_student_leaks=check_student_leaks,
    )
    for issue in issues:
        print(issue)
    return int(bool(issues))


def verify_pdf(
    pdf: Path,
    log: Path,
    *,
    runner: Callable[..., Any] | None = None,
    environment: Mapping[str, str] | None = None,
) -> int:
    log_text = log.read_text(encoding="utf-8", errors="replace")
    if log_has_missing_asset_warning(log_text):
        print(f"Gabarit Nexus absent : {log}")
        return 1
    if log_has_missing_character_warning(log_text):
        print(f"Glyphe manquant dans le PDF : {log}")
        return 1
    try:
        active_runner = subprocess.run if runner is None else runner
        options: dict[str, Any] = {
            "capture_output": True,
            "text": True,
            "check": True,
        }
        if environment is not None:
            options["env"] = dict(environment)
        result = active_runner(["pdffonts", str(pdf)], **options)
    except FileNotFoundError:
        print("Gate polices : pdffonts (poppler-utils) introuvable")
        return 1
    if not fonts_are_embedded(result.stdout):
        print(result.stdout)
        return 1
    return 0
