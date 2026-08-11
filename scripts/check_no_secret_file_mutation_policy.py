#!/usr/bin/env python3
"""Reject documented or scripted direct mutation of local secret files."""

from __future__ import annotations

from pathlib import Path
import re

from scripts._qa_common import ROOT, print_result


SECRET_TARGETS = (".env.rag", ".env.local", ".env", "*.pem", "id_rsa")
DIRECT_MUTATION_PATTERNS = [
    re.compile(r"\bperl\b[^\n]*-(?:0?pi|i)[^\n]*(?:\.env(?:\.rag|\.local)?|id_rsa|\.pem)\b"),
    re.compile(r"\bsed\b[^\n]*\s-i[^\n]*(?:\.env(?:\.rag|\.local)?|id_rsa|\.pem)\b"),
    re.compile(r"\bcat\s+(?:\.env(?:\.rag|\.local)?|id_rsa|[^\s]*\.pem)\b"),
    re.compile(r"\bgit\s+add\s+(?:\.env(?:\.rag|\.local)?|id_rsa|[^\s]*\.pem)\b"),
    re.compile(r">\s*(?:\.env(?:\.rag|\.local)?|id_rsa|[^\s]*\.pem)\b"),
    re.compile(r"\btee\s+(?:\.env(?:\.rag|\.local)?|id_rsa|[^\s]*\.pem)\b"),
]


def is_scanned_path(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    if not path.is_file():
        return False
    if rel.as_posix() == "scripts/check_no_secret_file_mutation_policy.py":
        return False
    if rel.parts and rel.parts[0] in {"tests", ".git", "dist", ".venv"}:
        return False
    return path.suffix in {".py", ".md", ".sh", ".yml", ".yaml", ".toml"} or path.name in {
        "Makefile",
        ".gitignore",
    }


def scan_paths(paths: list[Path], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(root).as_posix()
        for pattern in DIRECT_MUTATION_PATTERNS:
            match = pattern.search(text)
            if match:
                target = next((name for name in SECRET_TARGETS if name.replace("*", "") in match.group(0)), "secret")
                errors.append(f"{rel}: mutation directe interdite de {target}")
                break
    return errors


def iter_candidate_paths(root: Path = ROOT) -> list[Path]:
    return [path for path in root.rglob("*") if is_scanned_path(path, root)]


def main() -> None:
    print_result("check_no_secret_file_mutation_policy", scan_paths(iter_candidate_paths()))


if __name__ == "__main__":
    main()
