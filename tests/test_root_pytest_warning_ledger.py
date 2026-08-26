from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_root_pytest_warning_ledger.py"
LEDGER = ROOT / "audit" / "ROOT_PYTEST_WARNING_LEDGER.json"


def _producer():
    assert SCRIPT.is_file(), f"missing fixed producer: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("root_pytest_warning_ledger", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_root_warning_ledger_is_exact_and_source_bound() -> None:
    producer = _producer()
    payload = producer.build_ledger()

    assert payload["artifact_type"] == "root_pytest_warning_ledger"
    assert payload["observed_source_sha"] == (
        "c667f12b1792f31981b6b5894c8c604df1bce634"
    )
    assert payload["summary"] == {
        "pytest_summary_warning_count": 4,
        "post_summary_interpreter_warning_count": 1,
        "total_observed_warning_events": 5,
        "project_origin_count": 0,
        "external_origin_count": 5,
        "project_actionable_count": 5,
        "unknown_count": 0,
    }
    assert payload["observed_result"] == {
        "passed": 5,
        "failed": 0,
        "errors": 0,
        "pytest_summary_warnings": 4,
        "post_summary_interpreter_warnings": 1,
    }

    warnings = payload["warnings"]
    assert [row["warning_id"] for row in warnings] == [
        "ROOT-PYTEST-W001",
        "ROOT-PYTEST-W002",
        "ROOT-PYTEST-W003",
        "ROOT-PYTEST-W004",
        "ROOT-PYTEST-W005",
    ]
    assert [row["warning_type"] for row in warnings] == [
        "UserWarning",
        "UserWarning",
        "DeprecationWarning",
        "DeprecationWarning",
        "DeprecationWarning",
    ]
    assert [row["pytest_summary_member"] for row in warnings] == [
        True,
        True,
        True,
        True,
        False,
    ]
    assert {row["origin_ownership"] for row in warnings} == {"EXTERNAL"}
    assert {row["trigger_ownership"] for row in warnings} == {"PROJECT"}
    assert {row["actionable"] for row in warnings} == {True}
    assert {row["release_relevance"] for row in warnings} == {
        "TECHNICAL_REPRODUCIBILITY"
    }
    assert {row["disposition"] for row in warnings} == {"OPEN"}
    assert payload["warning_suppression"] == "NONE"

    trigger = payload["trigger"]
    for proof in trigger["project_sources"]:
        path = ROOT / proof["path"]
        assert path.is_file()
        assert proof["sha256"] == _sha256(path)
    assert trigger["test_path"] == (
        "Mathematiques/manuel-maths/tests/test_retrieval.py"
    )
    assert trigger["test_line"] == 16
    assert trigger["call_line"] == 22
    assert trigger["import_line"] == 22


def test_root_warning_ledger_validator_rejects_mutations() -> None:
    producer = _producer()
    payload = producer.build_ledger()
    mutations = []

    missing = copy.deepcopy(payload)
    missing["warnings"].pop()
    mutations.append(missing)

    added = copy.deepcopy(payload)
    added["warnings"].append(copy.deepcopy(added["warnings"][0]))
    mutations.append(added)

    wrong_count = copy.deepcopy(payload)
    wrong_count["summary"]["pytest_summary_warning_count"] = 5
    mutations.append(wrong_count)

    unknown = copy.deepcopy(payload)
    unknown["warnings"][0]["origin_ownership"] = "UNKNOWN"
    mutations.append(unknown)

    hidden = copy.deepcopy(payload)
    hidden["warnings"][0]["actionable"] = False
    mutations.append(hidden)

    no_release_relation = copy.deepcopy(payload)
    no_release_relation["warnings"][0]["release_relevance"] = ""
    mutations.append(no_release_relation)

    stale_source = copy.deepcopy(payload)
    stale_source["trigger"]["project_sources"][0]["sha256"] = "0" * 64
    mutations.append(stale_source)

    for mutation in mutations:
        with pytest.raises(ValueError):
            producer.validate_ledger(mutation)


def test_root_warning_ledger_fixed_output_and_check_are_deterministic() -> None:
    producer = _producer()
    payload = producer.build_ledger()
    assert LEDGER.is_file(), f"missing generated ledger: {LEDGER}"
    assert LEDGER.read_text(encoding="utf-8") == producer.render_json(payload)
    assert json.loads(LEDGER.read_text(encoding="utf-8")) == payload

    runs = [
        subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
        for _ in range(2)
    ]
    assert [run.returncode for run in runs] == [0, 0]
    assert runs[0].stdout == runs[1].stdout
    assert "4 pytest-summary + 1 post-summary" in runs[0].stdout
    assert "UNKNOWN=0" in runs[0].stdout
    assert runs[0].stderr == runs[1].stderr == ""

    help_run = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
        timeout=30,
    )
    assert "--check" in help_run.stdout
    assert "--output" not in help_run.stdout
