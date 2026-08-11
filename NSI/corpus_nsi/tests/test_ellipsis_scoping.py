"""Prove AST-based ellipsis scoping in check_no_placeholders_code."""
from __future__ import annotations

import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_no_placeholders_code as checker


def _check(code: str) -> list[str]:
    with tempfile.NamedTemporaryFile(
        suffix=".py", dir=ROOT, mode="w", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        f.flush()
        path = Path(f.name)
    try:
        return checker.check_file(path)
    finally:
        path.unlink()


def test_type_annotation_ellipsis_allowed() -> None:
    """tuple[Any, ...] in annotation -> PASS."""
    errors = _check("from typing import Any\nx: tuple[Any, ...] = (1,)\n")
    assert not any("ellipsis" in e for e in errors), f"Should be allowed: {errors}"


def test_function_body_ellipsis_flagged() -> None:
    """def f(): ... -> FLAGGED."""
    errors = _check("def f() -> None: ...\n")
    assert any("ellipsis" in e for e in errors), f"Should be flagged: {errors}"


def test_assignment_ellipsis_flagged() -> None:
    """x = ... -> FLAGGED."""
    errors = _check("x = ...\n")
    assert any("ellipsis" in e for e in errors), f"Should be flagged: {errors}"


def test_annotation_with_body_ellipsis_flags_body_only() -> None:
    """def f() -> tuple[Any, ...]: ...  -> annotation OK, body FLAGGED."""
    errors = _check("from typing import Any\ndef f() -> tuple[Any, ...]: ...\n")
    ellipsis_errors = [e for e in errors if "ellipsis" in e]
    # The body ellipsis should be flagged, but NOT the annotation one
    assert len(ellipsis_errors) == 1, f"Expected exactly 1 ellipsis error (body), got: {ellipsis_errors}"
