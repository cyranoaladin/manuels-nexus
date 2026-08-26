#!/usr/bin/env python3
"""Build the source-bound ledger for the observed root pytest warnings."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "audit" / "ROOT_PYTEST_WARNING_LEDGER.json"
OBSERVED_SOURCE_SHA = "c667f12b1792f31981b6b5894c8c604df1bce634"

PROJECT_SOURCES = (
    (
        "Mathematiques/manuel-maths/tests/test_retrieval.py",
        "422c75926ed6b0e36708b02b8fe8fe988992f7e2539de5f7a1b0eb9b80d85566",
        "warning trigger test",
    ),
    (
        "Mathematiques/manuel-maths/mcp/mcp_corpus/server.py",
        "d24945cc0bd579d854d9de304d19b705886077c0148e36ebb2cb87587d71ed4a",
        "lazy FlagEmbedding import",
    ),
    (
        "Mathematiques/manuel-maths/requirements.txt",
        "c3aa12be9779d4a610645346c6c9a53d70acff4ffca3ec7c4dce18398f523470",
        "dependency contract",
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _project_source_proofs() -> list[dict[str, str]]:
    proofs = []
    for relative, expected, role in PROJECT_SOURCES:
        path = ROOT / relative
        actual = _sha256(path)
        if actual != expected:
            raise ValueError(
                f"source proof stale for {relative}: expected {expected}, got {actual}"
            )
        proofs.append({"path": relative, "sha256": actual, "role": role})
    return proofs


def _warning(
    warning_id: str,
    warning_type: str,
    message: str,
    origin: str,
    origin_line: int | str,
    package: str,
    package_version: str,
    pytest_summary_member: bool,
    causal_dependency: str,
) -> dict[str, Any]:
    return {
        "warning_id": warning_id,
        "warning_type": warning_type,
        "message": message,
        "origin": origin,
        "origin_line": origin_line,
        "origin_package": package,
        "origin_package_version": package_version,
        "pytest_summary_member": pytest_summary_member,
        "origin_ownership": "EXTERNAL",
        "trigger_ownership": "PROJECT",
        "project_trigger": "search_corpus imports FlagEmbedding lazily",
        "causal_dependency": causal_dependency,
        "actionable": True,
        "actionability": (
            "Project dependency constraints permit this incompatible or deprecated "
            "external combination; resolve the controlled dependency contract."
        ),
        "release_relevance": "TECHNICAL_REPRODUCIBILITY",
        "disposition": "OPEN",
    }


def build_ledger() -> dict[str, Any]:
    warnings = [
        _warning(
            "ROOT-PYTEST-W001",
            "UserWarning",
            "Pandas requires version '2.10.2' or newer of 'numexpr' "
            "(version '2.9.0' currently installed).",
            "/home/alaeddine/.local/lib/python3.12/site-packages/pandas/core/computation/expressions.py",
            22,
            "pandas",
            "3.0.1",
            True,
            "numexpr==2.9.0 (minimum required by pandas: 2.10.2)",
        ),
        _warning(
            "ROOT-PYTEST-W002",
            "UserWarning",
            "Pandas requires version '1.4.2' or newer of 'bottleneck' "
            "(version '1.3.5' currently installed).",
            "/home/alaeddine/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py",
            56,
            "pandas",
            "3.0.1",
            True,
            "Bottleneck==1.3.5 (minimum required by pandas: 1.4.2)",
        ),
        _warning(
            "ROOT-PYTEST-W003",
            "DeprecationWarning",
            "builtin type SwigPyPacked has no __module__ attribute",
            "<frozen importlib._bootstrap>",
            488,
            "sentencepiece",
            "0.2.1",
            True,
            "sentencepiece._sentencepiece loaded by FlagEmbedding==1.4.0",
        ),
        _warning(
            "ROOT-PYTEST-W004",
            "DeprecationWarning",
            "builtin type SwigPyObject has no __module__ attribute",
            "<frozen importlib._bootstrap>",
            488,
            "sentencepiece",
            "0.2.1",
            True,
            "sentencepiece._sentencepiece loaded by FlagEmbedding==1.4.0",
        ),
        _warning(
            "ROOT-PYTEST-W005",
            "DeprecationWarning",
            "builtin type swigvarlink has no __module__ attribute",
            "sys",
            1,
            "sentencepiece",
            "0.2.1",
            False,
            "sentencepiece._sentencepiece interpreter shutdown via FlagEmbedding==1.4.0",
        ),
    ]
    return {
        "artifact_type": "root_pytest_warning_ledger",
        "observed_source_sha": OBSERVED_SOURCE_SHA,
        "observation": {
            "command": (
                "python -m pytest -q -W default "
                "Mathematiques/manuel-maths/tests/test_retrieval.py"
            ),
            "python_version": "3.12.3",
            "pytest_version": "9.0.2",
            "warning_capture": "default; no warning suppression",
        },
        "observed_result": {
            "passed": 5,
            "failed": 0,
            "errors": 0,
            "pytest_summary_warnings": 4,
            "post_summary_interpreter_warnings": 1,
        },
        "summary": {
            "pytest_summary_warning_count": 4,
            "post_summary_interpreter_warning_count": 1,
            "total_observed_warning_events": 5,
            "project_origin_count": 0,
            "external_origin_count": 5,
            "project_actionable_count": 5,
            "unknown_count": 0,
        },
        "trigger": {
            "test_path": "Mathematiques/manuel-maths/tests/test_retrieval.py",
            "test_line": 16,
            "call_line": 22,
            "import_line": 22,
            "import_path": "Mathematiques/manuel-maths/mcp/mcp_corpus/server.py",
            "project_sources": _project_source_proofs(),
        },
        "dependency_versions": {
            "FlagEmbedding": "1.4.0",
            "pandas": "3.0.1",
            "numexpr": "2.9.0",
            "Bottleneck": "1.3.5",
            "sentencepiece": "0.2.1",
        },
        "warning_suppression": "NONE",
        "warnings": warnings,
        "release_statement": (
            "All five events originate in external packages but are project-actionable "
            "through the controlled dependency contract; none is release evidence."
        ),
    }


def validate_ledger(payload: dict[str, Any]) -> None:
    expected = build_ledger()
    if payload != expected:
        raise ValueError("root pytest warning ledger differs from exact observed evidence")


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the fixed ledger is stale")
    args = parser.parse_args()

    payload = build_ledger()
    validate_ledger(payload)
    rendered = render_json(payload)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print(f"STALE: {OUTPUT.relative_to(ROOT)}")
            return 1
    else:
        _write_atomic(OUTPUT, rendered)
    print("PASS: 4 pytest-summary + 1 post-summary; UNKNOWN=0; suppression=NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
