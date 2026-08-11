#!/usr/bin/env python3
"""Reject obsolete generated build reports."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "01_build_reports"
OBSOLETE = ["s01_structures_graphiques", "graph_tools", "notes_tools"]
CHECKED = ["build_index.md", "build_index.json", "build_report.md"]


def main() -> int:
    errors: list[str] = []
    if REPORT_DIR.exists():
        for path in REPORT_DIR.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".json", ".txt"}:
                text = path.read_text(encoding="utf-8", errors="replace")
                for token in OBSOLETE:
                    if token in text:
                        errors.append(f"{path.relative_to(ROOT)} contains obsolete token {token}")
        for name in CHECKED:
            path = REPORT_DIR / name
            if path.exists():
                text = path.read_text(encoding="utf-8", errors="replace")
                if any(token in text for token in OBSOLETE):
                    errors.append(f"{path.relative_to(ROOT)} is obsolete")
    if errors:
        print("check_build_reports_freshness: KO")
        for error in errors:
            print(f"- {error}")
        return 1
    print("check_build_reports_freshness: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
