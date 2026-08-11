#!/usr/bin/env python3
"""Shared local Documents_DRIVE path resolution for QA scripts."""

from __future__ import annotations

from pathlib import Path
import os

from scripts._qa_common import ROOT

DRIVE_ENV_VAR = "NSI_DOCUMENTS_DRIVE_ROOT"
DRIVE_DIRNAME = "Documents_DRIVE"


def documents_drive_root(repo_root: Path = ROOT) -> Path:
    configured = os.environ.get(DRIVE_ENV_VAR, "").strip()
    if configured:
        return Path(configured).expanduser()
    return repo_root.resolve().parent / DRIVE_DIRNAME


def resolve_drive_reference(value: str, repo_root: Path = ROOT) -> Path | None:
    raw = value.strip()
    if not raw:
        return None
    path = Path(raw)
    if path.is_absolute():
        return path
    prefix = f"{DRIVE_DIRNAME}/"
    if raw.startswith(prefix):
        return documents_drive_root(repo_root) / raw[len(prefix):]
    return None
