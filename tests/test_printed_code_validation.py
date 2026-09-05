"""Tests de validation du code imprime sur toute la collection canonique (LOT 1)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "audit/PRINTED_CODE_VALIDATION.json"
SCRIPT_PATH = ROOT / "scripts/build_printed_code_validation.py"


@pytest.fixture(scope="module")
def validation_report() -> dict:
    assert REPORT_PATH.is_file(), f"L'artefact {REPORT_PATH} doit exister"
    with REPORT_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_printed_code_zero_syntax_errors(validation_report: dict) -> None:
    summary = validation_report["summary"]
    assert summary["PRINTED_CODE_SYNTAX_ERRORS"] == 0, (
        f"Erreurs de syntaxe detectees: {validation_report.get("syntax_errors")}"
    )


def test_printed_code_fidelity_pass(validation_report: dict) -> None:
    summary = validation_report["summary"]
    assert summary["PRINTED_CODE_FIDELITY"] == "PASS"


def test_printed_code_zero_output_mismatch(validation_report: dict) -> None:
    summary = validation_report["summary"]
    assert summary["PRINTED_CODE_EXPECTED_OUTPUT_MISMATCH"] == 0, (
        f"Divergences de sortie detectees: {validation_report.get("expected_output_mismatches")}"
    )


def test_zero_curved_quotes_and_ligatures(validation_report: dict) -> None:
    summary = validation_report["summary"]
    assert summary["CURVED_QUOTES_IN_CODE"] == 0
    assert summary["DESTRUCTIVE_LIGATURES_IN_CODE"] == 0


def test_expected_code_block_counts(validation_report: dict) -> None:
    summary = validation_report["summary"]
    assert summary["TOTAL_PYTHON_BLOCKS"] >= 1000
    assert summary["TOTAL_SQL_BLOCKS"] >= 150
    assert summary["TOTAL_CONSOLE_BLOCKS"] >= 120
    assert summary["TOTAL_VERIFIED_EXECUTIONS"] >= 120


def test_mutation_syntax_error_detected(monkeypatch) -> None:
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_printed_code_validation as mod

    # Mutation: simulate an invalid python block by monkeypatching ast.parse
    real_parse = mod.ast.parse
    def mutated_parse(code, *args, **kwargs):
        if "subprocess.run" in code:
            raise SyntaxError("simulated syntax error in python code")
        return real_parse(code, *args, **kwargs)

    monkeypatch.setattr(mod.ast, "parse", mutated_parse)
    report = mod.build_validation()
    assert report["summary"]["PRINTED_CODE_SYNTAX_ERRORS"] > 0
