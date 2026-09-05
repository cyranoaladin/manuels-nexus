"""Tests de conformite officielle de programme et d'exactitude des reponses (LOT 3)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "audit/PROGRAMME_CONTENT_VALIDATION.json"
SCRIPT_PATH = ROOT / "scripts/build_programme_content_validation.py"


@pytest.fixture(scope="module")
def prog_report() -> dict:
    assert REPORT_PATH.is_file(), f"L'artefact {REPORT_PATH} doit exister"
    with REPORT_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_zero_uncovered_atoms_and_zero_false_coverage(prog_report: dict) -> None:
    summary = prog_report["summary"]
    assert summary["OFFICIAL_ATOMS_UNCOVERED"] == 0
    assert summary["FALSE_COVERAGE"] == 0
    assert summary["MANDATORY_ATOMS_COUNT"] == summary["MAPPED_ATOMS_COUNT"]


def test_zero_unlabelled_out_of_programme(prog_report: dict) -> None:
    summary = prog_report["summary"]
    assert summary["UNLABELLED_OUT_OF_PROGRAMME_CONTENT"] == 0


def test_zero_independent_answer_mismatch(prog_report: dict) -> None:
    summary = prog_report["summary"]
    assert summary["INDEPENDENT_ANSWER_MISMATCH"] == 0
    assert summary["PASSED_INDEPENDENT_VALIDATIONS"] >= 400


def test_mutation_uncovered_atom_fails(tmp_path, monkeypatch) -> None:
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_programme_content_validation as mod

    # Create mutated coverage file with an unmapped atom
    real_cov = json.loads(mod.COVERAGE_PATH.read_text(encoding="utf-8"))
    real_cov["rows"].append({
        "atom_id": "FAKE-ATOM-999",
        "coverage_status": "UNMAPPED"
    })
    mutated_file = tmp_path / "mutated_coverage.json"
    mutated_file.write_text(json.dumps(real_cov), encoding="utf-8")

    monkeypatch.setattr(mod, "COVERAGE_PATH", mutated_file)
    report = mod.validate_programme_and_content()
    assert report["summary"]["OFFICIAL_ATOMS_UNCOVERED"] > 0
