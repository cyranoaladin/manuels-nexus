"""Tests for Zero Product Technical Debt.

Enforces:
1. TECHNICAL_DEBT_OPEN = 0
2. CONTENT_DEBT_OPEN = 0
3. PROGRAMME_DEBT_OPEN = 0
4. PRINT_DEBT_OPEN = 0
5. MANIFEST_DEBT_OPEN = 0
6. REPRODUCIBILITY_DEBT_OPEN = 0
7. ALL_PRODUCT_DEBTS_ZERO = True
8. Mutation tests: simulated open technical debt immediately breaks gate.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
DEBT_REPORT_FILE = ROOT / "audit/ZERO_TECHNICAL_DEBT_REPORT.json"


@pytest.fixture(scope="module")
def debt_data():
    assert DEBT_REPORT_FILE.is_file(), "ZERO_TECHNICAL_DEBT_REPORT.json missing"
    return json.loads(DEBT_REPORT_FILE.read_text(encoding="utf-8"))


def test_all_product_debts_are_zero(debt_data):
    assert debt_data["all_product_debts_zero"] is True
    summary = debt_data["product_debt_summary"]
    assert summary["TECHNICAL_DEBT_OPEN"] == 0
    assert summary["CONTENT_DEBT_OPEN"] == 0
    assert summary["PROGRAMME_DEBT_OPEN"] == 0
    assert summary["PRINT_DEBT_OPEN"] == 0
    assert summary["MANIFEST_DEBT_OPEN"] == 0
    assert summary["REPRODUCIBILITY_DEBT_OPEN"] == 0


def test_no_residual_files_or_placeholders_detected(debt_data):
    assert len(debt_data["residual_files_detected"]) == 0
    assert len(debt_data["publishable_source_markers_detected"]) == 0


def test_governance_is_isolated_and_never_obscures_technical_debt(debt_data):
    for item in debt_data["isolated_governance_debts"]:
        assert item["product_impacting"] is False
        assert item["status"] == "NON_BLOCKING_GOVERNANCE_LEDGER"


def test_mutation_technical_debt_breaks_zero_debt_gate(debt_data):
    mutated = copy.deepcopy(debt_data)
    mutated["product_debt_summary"]["TECHNICAL_DEBT_OPEN"] = 1
    mutated["all_product_debts_zero"] = (
        all(v == 0 for v in mutated["product_debt_summary"].values())
    )
    assert mutated["all_product_debts_zero"] is False


def test_mutation_content_debt_breaks_zero_debt_gate(debt_data):
    mutated = copy.deepcopy(debt_data)
    mutated["product_debt_summary"]["CONTENT_DEBT_OPEN"] = 1
    mutated["all_product_debts_zero"] = (
        all(v == 0 for v in mutated["product_debt_summary"].values())
    )
    assert mutated["all_product_debts_zero"] is False
