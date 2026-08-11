#!/usr/bin/env python3
"""Run audit-extracted-source from the source_clean archive in Git checkouts."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]

from scripts.archive_security import safe_extract_tar as safe_extract_tar_path


def safe_extract_tar(archive: tarfile.TarFile, destination: Path) -> None:
    """Extract a tar archive through the canonical Lot 3 guard."""
    name = archive.name
    if not isinstance(name, str):
        raise ValueError("archive tar sans chemin local exploitable")
    safe_extract_tar_path(Path(name), destination)


def extracted_root(temp_path: Path) -> Path:
    expected = temp_path / "nsi-enseignement"
    if expected.exists():
        return expected
    candidates = [path for path in temp_path.iterdir() if path.is_dir()]
    if len(candidates) == 1:
        return candidates[0]
    raise FileNotFoundError("racine nsi-enseignement absente de source_clean.tar.gz")


def run_audit_extracted_source(root: Path = ROOT) -> int:
    archive = root / "dist" / "source_clean.tar.gz"
    if not archive.exists():
        print("run_audit_extracted_source: KO - dist/source_clean.tar.gz absent")
        return 1
    with tempfile.TemporaryDirectory() as raw:
        temp_path = Path(raw)
        safe_extract_tar_path(archive, temp_path)
        audit_root = extracted_root(temp_path)
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env.pop("NSI_DOCUMENTS_DRIVE_ROOT", None)
        completed = subprocess.run(["make", "audit-extracted-source"], cwd=audit_root, env=env)
        return completed.returncode


def main() -> int:
    return run_audit_extracted_source()


if __name__ == "__main__":
    sys.exit(main())
