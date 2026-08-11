"""Gate: package-audit must invoke build_source_archive UNCONDITIONALLY.

Fail-closed: fails if the target is missing (not silent pass).
Positive: proves the invocation LOGICAL line (after joining shell
continuations) has NO conditional guard tokens.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Tokens that, if present on the logical line containing
# build_source_archive, indicate a conditional guard.
GUARD_TOKENS = ("test -f", "[ -f", "[ -e", "if ", "||", "&&")


def _package_audit_body() -> str:
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    match = re.search(
        r"^package-audit:.*?\n(.*?)(?=\n[A-Za-z0-9_-]+:|\Z)", text, re.S | re.M
    )
    return match.group(1) if match else ""


def _join_continuations(body: str) -> list[str]:
    """Join shell continuation lines (ending with backslash) into logical lines."""
    logical: list[str] = []
    current = ""
    for line in body.splitlines():
        stripped = line.rstrip()
        if stripped.endswith("\\"):
            current += stripped[:-1] + " "
        else:
            current += stripped
            logical.append(current)
            current = ""
    if current:
        logical.append(current)
    return logical


def test_package_audit_target_exists() -> None:
    """Fail-closed: the test must fail if the target is missing entirely."""
    body = _package_audit_body()
    assert body.strip(), (
        "package-audit target is MISSING or EMPTY in the Makefile. "
        "This gate must fail-closed on missing evidence."
    )


def test_build_source_archive_invoked_unconditionally() -> None:
    """Positive: build_source_archive is present and has NO guard tokens
    on its logical line (after joining continuations)."""
    body = _package_audit_body()
    assert body.strip(), "package-audit target missing (fail-closed)"

    logical_lines = _join_continuations(body)
    build_lines = [
        line for line in logical_lines
        if "build_source_archive" in line
    ]
    assert build_lines, (
        "build_source_archive is NOT invoked in package-audit. "
        "The archive must be built fresh every time."
    )

    for line in build_lines:
        for token in GUARD_TOKENS:
            assert token not in line, (
                f"Conditional guard '{token}' found on build_source_archive "
                f"logical line: {line.strip()!r}. "
                "The archive must be built unconditionally."
            )
