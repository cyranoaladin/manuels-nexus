#!/usr/bin/env python3
"""Check Python resources used by the pilot sequences."""

from __future__ import annotations

from typing import List
import ast

from scripts._qa_common import ROOT, TARGET_SEQUENCES, print_result


def main() -> None:
    errors: List[str] = []
    for seq in TARGET_SEQUENCES.values():
        for path in sorted((seq / "python").glob("*.py")):
            rel = path.relative_to(ROOT)
            text = path.read_text(encoding="utf-8", errors="replace")
            try:
                tree = ast.parse(text, filename=str(path))
                compile(text, str(path), "exec")
            except Exception as exc:
                errors.append(f"{rel}: code non exécutable ({exc})")
                continue

            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            if not functions:
                errors.append(f"{rel}: aucune fonction testable")
            for func in functions:
                if not func.returns:
                    errors.append(f"{rel}:{func.lineno}: annotation de retour manquante pour {func.name}")
                args_without_types = [
                    arg.arg
                    for arg in func.args.args
                    if arg.annotation is None and arg.arg not in {"self", "cls"}
                ]
                if args_without_types:
                    errors.append(f"{rel}:{func.lineno}: paramètres sans annotation -> {', '.join(args_without_types)}")
                if not ast.get_docstring(func):
                    errors.append(f"{rel}:{func.lineno}: docstring manquante pour {func.name}")

        tests = list((seq / "tests").glob("test*.py"))
        if not tests:
            errors.append(f"{seq.relative_to(ROOT)}: aucun test Python")

    print_result("check_python_quality", errors)


if __name__ == "__main__":
    main()
