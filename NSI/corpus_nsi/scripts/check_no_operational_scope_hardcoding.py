#!/usr/bin/env python3
"""Reject fixed prefix scopes in operational-support QA checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import ast
import re

from scripts._qa_common import ROOT

ALLOWED_PILOT_SCOPE_FILES = {"_qa_common.py"}


@dataclass
class ScopeHardcodingResult:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0


def default_script_paths(root: Path) -> list[Path]:
    scripts = root / "scripts"
    if not scripts.exists():
        return []
    return sorted(
        {
            *scripts.glob("check_*.py"),
            *scripts.glob("_*.py"),
        }
    )


def contains_fixed_prefix_set(path: Path, tree: ast.AST) -> list[str]:
    errors: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = [target.id for target in node.targets if isinstance(target, ast.Name)]
            forbidden_targets = [name for name in targets if name in {"TARGET_PREFIXES", "TARGET_SEQUENCES"}]
            if forbidden_targets and path.name not in ALLOWED_PILOT_SCOPE_FILES:
                errors.append("périmètre opérationnel codé en dur via TARGET_PREFIXES/TARGET_SEQUENCES")
            if path.name not in ALLOWED_PILOT_SCOPE_FILES and contains_sequence_literal_collection(node.value):
                errors.append("liste fixe de séquences P/T codée en dur")
    return errors


def contains_sequence_literal_collection(node: ast.AST) -> bool:
    if not isinstance(node, (ast.Set, ast.List, ast.Tuple)):
        return False
    values = [item.value for item in node.elts if isinstance(item, ast.Constant) and isinstance(item.value, str)]
    sequence_values = [value for value in values if re.fullmatch(r"[PT]\d{2}", value)]
    return len(sequence_values) >= 2


def analyze_no_operational_scope_hardcoding(
    root: Path = ROOT,
    script_paths: list[Path] | None = None,
) -> ScopeHardcodingResult:
    result = ScopeHardcodingResult()
    paths = script_paths or default_script_paths(root)
    for path in paths:
        if not path.exists():
            continue
        result.checked_files += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            result.errors.append(f"{path}: syntaxe Python invalide -> {exc}")
            continue
        for error in contains_fixed_prefix_set(path, tree):
            result.errors.append(f"{path}: {error}")
        prefix_slice_pattern = r"path\.name\[\s*:\s*3\s*\]"
        if re.search(prefix_slice_pattern, text):
            result.errors.append(f"{path}: extraction du préfixe de nom par tranche interdite pour déterminer le périmètre opérationnel")
        if re.search(r"range\(\s*10\s*,\s*20\s*\)", text) and re.search(r"[PT]\{|\bP\b|\bT\b", text):
            result.errors.append(f"{path}: plage numérique fixe appliquée à un périmètre P/T")
    return result


def main() -> int:
    result = analyze_no_operational_scope_hardcoding()
    if result.errors:
        print("check_no_operational_scope_hardcoding: KO")
        for error in result.errors[:80]:
            print(f"- {error}")
        return 1
    print(f"check_no_operational_scope_hardcoding: PASS ({result.checked_files} scripts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
