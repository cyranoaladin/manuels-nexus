"""Ensure documentation uses python -m scripts.<module>, not python scripts/*.py."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TRACKED_DOCS = ["README.md", "AGENTS.md", "SKILLS.md"]
OLD_PATTERN = re.compile(r"python\s+scripts/\w+\.py")


def test_no_old_style_script_invocations_in_docs() -> None:
    violations: list[str] = []
    for name in TRACKED_DOCS:
        path = ROOT / name
        if not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if OLD_PATTERN.search(line):
                violations.append(f"{name}:{lineno}: {line.strip()}")
    assert not violations, (
        "Old-style `python scripts/X.py` invocations found in docs. "
        "Use `python -m scripts.X` instead:\n" + "\n".join(violations)
    )
