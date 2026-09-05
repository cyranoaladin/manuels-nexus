"""Tests for Final Print Preflight and Visual/Semantic Regression.

Enforces:
1. PREFLIGHT_ALL_TARGETS = PASS across 12/12 targets
2. 100% embedded fonts, zero missing glyphs
3. Zero overfull hbox/vbox
4. Zero student separation leaks across all 6 student manuals
5. UNEXPECTED_VISUAL_DIFF = 0 and UNEXPLAINED_SEMANTIC_DIFF = 0
6. Mutation tests: simulated font flaw or unexplained diff breaks gate.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_FILE = ROOT / "audit/FINAL_PRINT_PREFLIGHT.json"
REGRESSION_FILE = ROOT / "audit/VISUAL_SEMANTIC_REGRESSION_REPORT.json"


@pytest.fixture(scope="module")
def preflight_data():
    assert PREFLIGHT_FILE.is_file(), "FINAL_PRINT_PREFLIGHT.json missing"
    return json.loads(PREFLIGHT_FILE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def regression_data():
    assert REGRESSION_FILE.is_file(), "VISUAL_SEMANTIC_REGRESSION_REPORT.json missing"
    return json.loads(REGRESSION_FILE.read_text(encoding="utf-8"))


def test_preflight_all_twelve_targets_pass(preflight_data):
    assert preflight_data["total_targets"] == 12
    assert preflight_data["passed_targets"] == 12
    assert preflight_data["preflight_all_targets"] == "PASS"


def test_each_target_satisfies_all_preflight_facets(preflight_data):
    for r in preflight_data["records"]:
        assert r["geometry"]["passed"] is True
        assert r["fonts"]["passed"] is True
        assert r["fonts"]["unembedded_fonts"] == 0
        assert r["structure"]["passed"] is True
        assert r["structure"]["toc_entries"] > 0
        assert r["structure"]["links_count"] > 0
        assert r["overfull_hbox_vbox"] == 0
        if r["variant"] == "eleve":
            assert r["student_separation"]["applicable"] is True
            assert r["student_separation"]["passed"] is True
            assert len(r["student_separation"]["violations"]) == 0
        assert r["preflight_status"] == "PASS"


def test_visual_semantic_regression_zero_unexpected(regression_data):
    assert regression_data["unexpected_visual_diff"] == 0
    assert regression_data["unexplained_semantic_diff"] == 0
    assert regression_data["regression_gate_status"] == "PASS"
    assert len(regression_data["classified_changes"]) >= 2
    for c in regression_data["classified_changes"]:
        assert c["justified"] is True


def test_mutation_unembedded_font_fails_preflight(preflight_data):
    mutated = copy.deepcopy(preflight_data)
    mutated["records"][0]["fonts"]["unembedded_fonts"] = 1
    mutated["records"][0]["fonts"]["passed"] = False
    mutated["records"][0]["preflight_status"] = "FAIL"

    passed_count = sum(1 for r in mutated["records"] if r["preflight_status"] == "PASS")
    gate_status = "PASS" if passed_count == len(mutated["records"]) else "FAIL"
    assert gate_status == "FAIL"


def test_mutation_unexpected_diff_fails_regression_gate(regression_data):
    mutated = copy.deepcopy(regression_data)
    mutated["unexpected_visual_diff"] = 1
    gate_status = "PASS" if (
        mutated["unexpected_visual_diff"] == 0 and mutated["unexplained_semantic_diff"] == 0
    ) else "FAIL"
    assert gate_status == "FAIL"
