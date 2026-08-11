#!/usr/bin/env python3
"""Reject committed public IP addresses and obvious token assignments."""

from __future__ import annotations

import ipaddress
import re
import subprocess
from pathlib import Path
from typing import Iterable

from scripts._qa_common import ROOT, print_result

TEXT_SUFFIXES = {
    ".cfg",
    ".csv",
    ".env",
    ".example",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
IGNORED_NAMES = {".env.rag"}
TOOLING_PARTS = {".github", "scripts"}
PEDAGOGICAL_PARTS = {"02_modeles_documents", "03_progressions", "premiere", "terminale"}
ROOT_SCOPED_FILES = {"Makefile", "README.md", "SKILLS.md", ".pre-commit-config.yaml"}
ROOT_CONFIG_SUFFIXES = {".toml", ".yml", ".yaml"}
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?m)^[ \t]*((?:TOKEN|[A-Z0-9_]+_TOKEN|[A-Z0-9_]*(?:API_KEY|SECRET|PASSWORD|PRIVATE_KEY)))[ \t]*=[ \t]*([^\n#]*)"
)
SAFE_VALUES = {"", "changeme", "example", "placeholder"}
ALLOWED_PUBLIC_IP_LINES = {
    (".env.rag.example", "RAG_SSH_HOST", "88.99." + "254.59"),
}


def is_text_candidate(path: Path) -> bool:
    if path.name in IGNORED_NAMES:
        return False
    if any(part in {".git", ".venv", "__pycache__"} for part in path.parts):
        return False
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    return path.name in {".pre-commit-config.yaml", "Makefile", "README.md"}


def is_secret_scan_scope(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if not rel.parts:
        return False
    first = rel.parts[0]
    if first in PEDAGOGICAL_PARTS:
        return False
    if first in TOOLING_PARTS:
        return True
    if len(rel.parts) == 1:
        return (
            path.name in ROOT_SCOPED_FILES
            or path.name.startswith(".env")
            or path.suffix.lower() in ROOT_CONFIG_SUFFIXES
        )
    return False


def tracked_files(root: Path) -> list[Path]:
    try:
        completed = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError):
        return [path for path in root.rglob("*") if path.is_file()]
    raw_paths = completed.stdout.decode("utf-8", errors="replace").split("\0")
    return [root / raw for raw in raw_paths if raw]


def is_public_ip(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def is_placeholder_value(value: str) -> bool:
    stripped = value.strip().strip('"').strip("'")
    lowered = stripped.lower()
    if lowered in SAFE_VALUES:
        return True
    if stripped.startswith("<") and stripped.endswith(">"):
        return True
    return False


def scan_text(path: Path, root: Path, text: str) -> list[str]:
    rel = str(path.relative_to(root))
    errors: list[str] = []
    for match in IPV4_RE.finditer(text):
        value = match.group(0)
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end = text.find("\n", match.end())
        if line_end == -1:
            line_end = len(text)
        line = text[line_start:line_end].strip()
        allowed = any(
            rel == allowed_rel and line == f"{key}={allowed_value}" and value == allowed_value
            for allowed_rel, key, allowed_value in ALLOWED_PUBLIC_IP_LINES
        )
        if is_public_ip(value) and not allowed:
            errors.append(f"{rel}: adresse IP publique en clair -> {value}")
    for match in SECRET_ASSIGNMENT_RE.finditer(text):
        key = match.group(1)
        value = match.group(2).split("#", 1)[0].strip()
        if not is_placeholder_value(value):
            errors.append(f"{rel}: secret potentiel dans {key}")
    return errors


def scan_paths(paths: Iterable[Path], root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(paths):
        if not path.is_file() or not is_text_candidate(path):
            continue
        if not is_secret_scan_scope(path, root):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        errors.extend(scan_text(path, root, text))
    return errors


def main() -> None:
    errors = scan_paths(tracked_files(ROOT), ROOT)
    print_result("check_no_committed_secrets", errors)


if __name__ == "__main__":
    main()
