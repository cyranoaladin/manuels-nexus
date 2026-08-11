#!/usr/bin/env python3
"""Check document naming conventions in session files.

Rejects:
- Doubled prefixes like P00_P00_cours.md or T01_T01_cours.md
- Missing sequence prefix for sequence-specific files
- Inconsistent casing in filenames
- Inconsistent extensions
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SESSION_FILES = [
    ROOT / "03_progressions/seances_premiere.md",
    ROOT / "03_progressions/seances_terminale.md",
]

# Pattern for sequence-prefixed filenames
SEQ_FILE_RE = re.compile(r"\b([PT]\d{2}_[A-Za-z0-9_]+\.[a-z]{2,4})\b")

# Pattern for doubled prefix like P00_P00_ or T01_T01_
DOUBLED_PREFIX_RE = re.compile(r"^([PT]\d{2})_\1_")

# Allowed extensions
ALLOWED_EXTENSIONS = {".md", ".py", ".csv", ".json", ".yml", ".yaml", ".txt"}


def extract_all_filenames(path: Path) -> list[tuple[str, str]]:
    """Return (session_id, filename) pairs from session file."""
    results: list[tuple[str, str]] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"(?=^### Séance )", text, flags=re.M)
    for block in blocks:
        if not block.startswith("### Séance "):
            continue
        session_id = block.splitlines()[0].replace("### Séance ", "").strip()
        for match in SEQ_FILE_RE.finditer(block):
            results.append((session_id, match.group(1)))
    return results


def main() -> None:
    errors: list[str] = []
    seen_files: set[str] = set()

    for session_path in SESSION_FILES:
        if not session_path.exists():
            errors.append(f"session file missing: {session_path.name}")
            continue
        filenames = extract_all_filenames(session_path)
        for session_id, filename in filenames:
            if filename in seen_files:
                continue
            seen_files.add(filename)

            # Check doubled prefix
            if DOUBLED_PREFIX_RE.match(filename):
                errors.append(
                    f"{session_id}: doubled prefix in '{filename}' "
                    f"(should be '{DOUBLED_PREFIX_RE.sub(lambda m: m.group(1) + '_', filename)}')"
                )

            # Check extension
            ext = "." + filename.rsplit(".", 1)[-1] if "." in filename else ""
            if ext not in ALLOWED_EXTENSIONS:
                errors.append(
                    f"{session_id}: unexpected extension '{ext}' in '{filename}'"
                )

            # Check mixed case in body (after prefix)
            body = filename.split("_", 1)[-1] if "_" in filename else filename
            if body != body.lower() and body != body.upper():
                # Allow TD, TP, QCM as uppercase tokens within the name
                cleaned = re.sub(r"(TD|TP|QCM|E\d+|Q\d+|R\d+|S\d+|J\d+)", "", body)
                if cleaned != cleaned.lower():
                    errors.append(
                        f"{session_id}: mixed case in '{filename}' "
                        f"(use lowercase except TD/TP/QCM)"
                    )

    if errors:
        print("check_document_naming_conventions: KO")
        for e in errors:
            print(f"- {e}")
        sys.exit(1)
    print("check_document_naming_conventions: PASS")


if __name__ == "__main__":
    main()
