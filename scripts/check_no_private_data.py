#!/usr/bin/env python3
"""Detect private data and write privacy_report.md.

The metadata field private_data: false is declarative only and never suppresses
alerts. Only privacy_allowlist.yml can justify exceptions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List
import re

import yaml

from scripts._qa_common import ROOT, print_result

ALLOWLIST = ROOT / "privacy_allowlist.yml"
REPORT = ROOT / "privacy_report.md"
TEXT_SUFFIXES = {".md", ".tex", ".py", ".json", ".yml", ".yaml", ".txt", ".csv"}
EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "01_build_reports",
    "scrapping_NSI",
    "Documents_DRIVE",
    "nsi-enseignement",
    # latex/ and drive_quarantine/ ARE scanned (contain authored content).
    # Faux positifs latex : allowlistés dans privacy_allowlist.yml.
    "dist",  # build artifacts, not authored content
}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
FR_PHONE_RE = re.compile(r"(?:(?:\+|00)33|0)\s*[1-9](?:[\s().-]?\d){8}\b")
TN_PHONE_RE = re.compile(r"(?<![A-Za-z0-9.])(?:(?:\+|00)216\s*)?(?:[24579]\d)(?:[\s().-]?\d){6}(?![A-Za-z0-9])")
ADDRESS_RE = re.compile(
    r"\b(?:adresse personnelle|domicile|rue|avenue|boulevard|code postal|gouvernorat|ville de résidence)\b",
    re.IGNORECASE,
)
PROPER_NAME_RE = re.compile(
    r"\b[A-ZÉÈÀÂÊÎÔÛÇ][a-zéèàâêîôûç]+(?:[- ][A-ZÉÈÀÂÊÎÔÛÇ][a-zéèàâêîôûç]+)+\b"
)
ISO_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
YEAR_RANGE_RE = re.compile(r"\b\d{4}-\d{4}\b")


def load_allowlist() -> Dict[str, List[str]]:
    if not ALLOWLIST.exists():
        return {}
    data = yaml.safe_load(ALLOWLIST.read_text(encoding="utf-8")) or {}
    return {key: value or [] for key, value in data.items() if isinstance(value, list)}


def allowed(value: str, allowlist: Dict[str, List[str]]) -> bool:
    candidates: List[str] = []
    for key in [
        "allowed_emails",
        "allowed_phone_patterns",
        "allowed_name_patterns",
        "institutional_patterns",
        "allowed_privacy_warning_patterns",
    ]:
        candidates.extend(allowlist.get(key, []))
    return any(pattern and re.search(pattern, value, flags=re.IGNORECASE) for pattern in candidates)


def student_names(allowlist: Dict[str, List[str]]) -> List[str]:
    names: List[str] = []
    for raw in allowlist.get("student_names_files", []):
        path = (ROOT / raw).resolve()
        if not path.exists() or ROOT not in path.parents:
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                names.append(line)
    return names


HEX_CONTEXT_RE = re.compile(r"[0-9a-fA-F]{32,}")


def is_hex_hash_context(text: str, start: int, end: int) -> bool:
    """Suppress only if the match's digits are CONTAINED within a contiguous hex token."""
    for m in HEX_CONTEXT_RE.finditer(text):
        if m.start() <= start and m.end() >= end:
            return True
    return False


def is_population_context(text: str, start: int, end: int) -> bool:
    """Ignore country population values that look like Tunisian phone numbers."""
    window = text[max(0, start - 120): min(len(text), end + 120)]
    if "POPULATION" in window or "pays_monde.csv" in window:
        return True
    if re.search(r"\b[A-ZÉÈÀÂÎÔÛÇA-Za-zéèàâîôûç-]+,[^,\n]+,[^,\n]+,\d{7,10}\b", window):
        return True
    return False


def iter_text_files() -> Iterable[Path]:
    """Enumerate tracked text files via git ls-files for CI reproducibility."""
    import subprocess
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    if result.returncode == 0 and result.stdout:
        for rel in result.stdout.split("\0"):
            if not rel:
                continue
            path = ROOT / rel
            if path == REPORT:
                continue
            if any(part in EXCLUDED_PARTS for part in path.parts):
                continue
            if path.suffix in TEXT_SUFFIXES or path.name in {"manifest.csv"}:
                yield path
    else:
        # Fallback for non-git environments
        for path in sorted(ROOT.rglob("*")):
            if path.is_dir():
                continue
            if path == REPORT:
                continue
            if any(part in EXCLUDED_PARTS for part in path.parts):
                continue
            if path.suffix in TEXT_SUFFIXES or path.name in {"manifest.csv"}:
                yield path


def add_report(lines: List[str], title: str, items: List[str]) -> None:
    lines.append(f"## {title}")
    lines.append("")
    if items:
        for item in items[:200]:
            lines.append(f"- {item}")
        if len(items) > 200:
            lines.append(f"- ... {len(items) - 200} alertes supplémentaires non affichées")
    else:
        lines.append("- Aucune alerte.")
    lines.append("")


def main() -> None:
    allowlist = load_allowlist()
    names = student_names(allowlist)
    hard_errors: List[str] = []
    warnings: List[str] = []
    allowlisted: List[str] = []

    for path in iter_text_files():
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8", errors="replace")

        for label, regex in {
            "email": EMAIL_RE,
            "telephone_fr": FR_PHONE_RE,
            "telephone_tn": TN_PHONE_RE,
            "adresse": ADDRESS_RE,
        }.items():
            for match in regex.finditer(text):
                value = match.group(0)
                if label.startswith("telephone") and (ISO_DATE_RE.fullmatch(value) or YEAR_RANGE_RE.fullmatch(value)):
                    continue
                if label.startswith("telephone") and is_population_context(text, match.start(), match.end()):
                    continue
                if label.startswith("telephone") and is_hex_hash_context(text, match.start(), match.end()):
                    continue
                item = f"{rel}: {label} possible -> {value}"
                if allowed(value, allowlist) or allowed(str(rel), allowlist):
                    allowlisted.append(item)
                else:
                    hard_errors.append(item)

        for name in names:
            pattern = r"\b" + re.escape(name) + r"\b"
            if re.search(pattern, text, flags=re.IGNORECASE):
                item = f"{rel}: nom d'élève possible -> {name}"
                if allowed(name, allowlist):
                    allowlisted.append(item)
                else:
                    hard_errors.append(item)

        for match in PROPER_NAME_RE.finditer(text):
            value = match.group(0)
            item = f"{rel}: nom propre suspect -> {value}"
            if allowed(value, allowlist) or allowed(str(rel), allowlist):
                allowlisted.append(item)
            else:
                warnings.append(item)

    lines = [
        "# Privacy Report",
        "",
        "Le champ `private_data: false` n'est pas utilisé comme preuve.",
        "Les alertes bloquantes concernent emails, téléphones, coordonnées ou noms d'élèves non allowlistés.",
        "Les noms propres suspects sont listés pour revue humaine.",
        "",
    ]
    add_report(lines, "Alertes bloquantes", hard_errors)
    add_report(lines, "Alertes de revue", warnings)
    add_report(lines, "Éléments couverts par allowlist explicite", allowlisted)
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print_result("check_no_private_data", hard_errors)


if __name__ == "__main__":
    main()
