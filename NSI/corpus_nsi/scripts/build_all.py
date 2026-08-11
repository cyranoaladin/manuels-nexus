#!/usr/bin/env python3
"""Build helper for the NSI repository with validation pipeline."""

from __future__ import annotations

import subprocess
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
PY = 'python'

CHECKS = [
    'scripts/rebuild_inventory.py',
    'scripts/check_metadata.py',
    'scripts/check_links.py',
    'scripts/check_no_private_data.py',
    'scripts/check_no_placeholders_docs.py',
    'scripts/check_no_placeholders_code.py',
    'scripts/generate_index.py',
    'scripts/check_no_build_artifacts_in_index.py',
    'scripts/check_required_sections.py',
    'scripts/check_document_depth.py',
    'scripts/check_qcm_schema.py',
    'scripts/check_sequence_completeness.py',
    'scripts/check_program_coverage.py',
    'scripts/check_coverage_evidence.py',
    'scripts/run_python_tests.py',
    'scripts/check_quality_gates.py',
]


def run(cmd: list[str]) -> None:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run([PY] + cmd, cwd=ROOT, env=env)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    for cmd in CHECKS:
        run(cmd.split())
    print('build_all: PASS')


if __name__ == '__main__':
    main()
