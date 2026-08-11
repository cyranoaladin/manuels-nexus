#!/usr/bin/env python3
"""Reject unfinished code constructs without blanket exclusion of Python files."""

from __future__ import annotations

from pathlib import Path
from typing import List
import ast
import io
import re
import tokenize

from scripts._qa_common import ROOT, print_result

COMMENT_MARKERS = ("TO" + "DO", "FIX" + "ME", "X" + "XX", "TBD")
COMPLETION_CONTEXT = re.compile(r"\b(?:[àa]\s+compl[ée]ter|starter\s+[ée]l[èe]ve)\b", re.I)
STARTER_MARKERS = ("TODO", "FIXME", "TBD", "XXX", "PLACEHOLDER")


def _set_parents(tree: ast.AST) -> None:
    """Annotate every node with a _parent attribute."""
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child._parent = node  # type: ignore[attr-defined]


def _ellipsis_is_in_annotation(node: ast.Constant) -> bool:
    """Return True if the Ellipsis node sits inside a type annotation context.

    Allowed: tuple[Any, ...], Callable[..., int], slice Subscript, etc.
    Forbidden: def f(): ..., x = ..., standalone Expr(...).
    """
    current: ast.AST = node
    while hasattr(current, "_parent"):
        parent = current._parent
        # Ellipsis inside a Subscript slice (e.g. tuple[Any, ...]) -> annotation
        if isinstance(parent, ast.Subscript) and current is parent.slice:
            return True
        if isinstance(parent, ast.Tuple) and hasattr(parent, "_parent"):
            grandparent = parent._parent
            if isinstance(grandparent, ast.Subscript) and parent is grandparent.slice:
                return True
        # Ellipsis in a function annotation (return type or arg annotation)
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if current is parent.returns:
                return True
        if isinstance(parent, ast.arg) and current is parent.annotation:
            return True
        if isinstance(parent, ast.AnnAssign):
            if current is parent.annotation:
                return True
        current = parent
    return False


def _containing_function(node: ast.AST) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    """Return the function that owns ``node``, if it has one."""
    current: ast.AST = node
    while hasattr(current, "_parent"):
        current = current._parent
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return current
    return None


def _contains_forbidden_code(tree: ast.AST, text: str) -> bool:
    """Check that a teacher correction is a real implementation, not a scaffold."""
    _set_parents(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Pass):
            return True
        if isinstance(node, ast.Raise):
            raised = node.exc
            name = getattr(raised.func, "id", "") if isinstance(raised, ast.Call) else getattr(raised, "id", "")
            if name == "NotImplementedError":
                return True
        if isinstance(node, ast.Constant) and node.value is Ellipsis and not _ellipsis_is_in_annotation(node):
            return True
    upper = text.upper()
    return any(marker in upper for marker in STARTER_MARKERS)


def _public_functions(tree: ast.AST) -> set[str]:
    return {
        node.name
        for node in ast.iter_child_nodes(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_")
    }


def _is_complete_teacher_correction(path: Path, expected_functions: set[str]) -> bool:
    """Require a non-empty professor correction implementing the starter API."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        return False
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return False
    return not _contains_forbidden_code(tree, text) and expected_functions <= _public_functions(tree)


def _has_linked_tp(sequence_dir: Path, starter_name: str) -> bool:
    """Require an explicit TP reference to the exact starter filename."""
    for document in sequence_dir.glob("*.md"):
        name = document.name.lower()
        if "tp" not in name:
            continue
        text = document.read_text(encoding="utf-8", errors="replace")
        if starter_name in text:
            return True
    return False


def _is_contractualized_starter(path: Path, tree: ast.AST, node: ast.Raise, text: str) -> bool:
    """Accept only a student starter backed by its TP, tests and teacher correction.

    This is deliberately structural: a name containing ``starter`` alone never
    grants an exception to the placeholder policy.
    """
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return False
    parts = rel.parts
    if len(parts) < 6 or parts[:2] != ("03_progressions", "supports"):
        return False
    if parts[2] not in {"premiere", "terminale"} or parts[4] != "code":
        return False

    filename = path.name.lower()
    if "starter" not in filename or any(token in filename for token in ("corrige", "bareme", "test")):
        return False
    if any(marker in text.upper() for marker in STARTER_MARKERS):
        return False

    sequence_dir = ROOT.joinpath(*parts[:4])
    code_dir = sequence_dir / "code"
    expected_tests = list(code_dir.glob("*_tests_attendus_*.py"))
    corrections = list(code_dir.glob("*_corrige_professeur_*.py"))
    if not expected_tests or not corrections or not _has_linked_tp(sequence_dir, path.name):
        return False

    expected_functions = _public_functions(tree)
    if not expected_functions or not any(
        _is_complete_teacher_correction(correction, expected_functions) for correction in corrections
    ):
        return False

    function = _containing_function(node)
    docstrings: list[str] = []
    if isinstance(tree, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        ds = ast.get_docstring(tree)
        if ds:
            docstrings.append(ds)
    if function is not None:
        ds = ast.get_docstring(function)
        if ds:
            docstrings.append(ds)
    context = "\n".join(docstrings)
    return bool(COMPLETION_CONTEXT.search(context))


def check_file(path: Path) -> List[str]:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8", errors="replace")
    errors: List[str] = []

    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        return [f"{rel}: syntaxe Python invalide ({exc})"]

    _set_parents(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.Pass):
            errors.append(f"{rel}:{node.lineno}: instruction pass interdite")
        if isinstance(node, ast.Raise):
            raised = node.exc
            if isinstance(raised, ast.Call):
                name = getattr(raised.func, "id", "")
            else:
                name = getattr(raised, "id", "")
            if name == "NotImplementedError" and not _is_contractualized_starter(path, tree, node, text):
                errors.append(f"{rel}:{node.lineno}: NotImplementedError interdit")
        if isinstance(node, ast.Constant) and node.value is Ellipsis:
            if not _ellipsis_is_in_annotation(node):
                errors.append(f"{rel}:{node.lineno}: ellipsis interdit")

    reader = io.StringIO(text).readline
    for token in tokenize.generate_tokens(reader):
        if token.type == tokenize.COMMENT:
            upper = token.string.upper()
            for marker in COMMENT_MARKERS:
                if marker in upper:
                    errors.append(f"{rel}:{token.start[0]}: marqueur de placeholder dans un commentaire")

    return errors


def main() -> None:
    errors: List[str] = []
    for path in sorted(ROOT.rglob("*.py")):
        if {".git", ".venv", "__pycache__", "scrapping_NSI", "Documents_DRIVE", "nsi-enseignement"} & set(path.parts):
            continue
        errors.extend(check_file(path))

    print_result("check_no_placeholders_code", errors)


if __name__ == "__main__":
    main()
