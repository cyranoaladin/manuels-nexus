"""Les agregats de severite sont la longueur de listes nommees, pas des sommes."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FINDINGS_JSON = ROOT / "audit/OPEN_FINDINGS.json"
RELEASE_JSON = ROOT / "audit/RELEASE_ALL_CHECK.json"


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def findings():
    assert FINDINGS_JSON.is_file()
    return json.loads(FINDINGS_JSON.read_text(encoding="utf-8"))


def test_every_finding_has_a_unique_identifier(findings):
    ids = [f["id"] for f in findings["findings"]]
    assert len(ids) == len(set(ids))
    assert findings["summary"]["DUPLICATE_FINDING_IDS"] == 0


def test_true_product_clones_equals_its_identifier_list(findings):
    """L'assertion demandee : le compteur est la longueur de la liste."""

    assert findings["summary"]["TRUE_PRODUCT_CLONES_OPEN"] == len(
        findings["clone_finding_ids"]
    )


def test_each_severity_total_equals_its_identifier_list(findings):
    by_severity = findings["finding_ids_by_severity"]
    for severity, key in (("P0", "TOTAL_P0_OPEN"), ("P1", "TOTAL_P1_OPEN"), ("P2", "TOTAL_P2_OPEN")):
        assert findings["summary"][key] == len(by_severity.get(severity, []))


def test_every_finding_names_its_evidence(findings):
    for finding in findings["findings"]:
        if finding["kind"] == "MISSING_EVIDENCE":
            continue
        assert finding["evidence"], finding["id"]
        assert (ROOT / finding["evidence"]).is_file(), finding["evidence"]


def test_release_summary_reads_the_same_register(findings):
    """Le resume de release ne doit pas recomposer ses propres severites."""

    assert RELEASE_JSON.is_file()
    summary = json.loads(RELEASE_JSON.read_text(encoding="utf-8"))["summary"]
    assert summary["TOTAL_P0_OPEN"] == findings["summary"]["TOTAL_P0_OPEN"]
    assert summary["TOTAL_P1_OPEN"] == findings["summary"]["TOTAL_P1_OPEN"]
    assert summary["TOTAL_P2_OPEN"] == findings["summary"]["TOTAL_P2_OPEN"]
    assert summary["TRUE_PRODUCT_CLONES_OPEN"] == len(findings["clone_finding_ids"])


def test_a_clone_finding_points_at_a_real_file(findings):
    for finding in findings["findings"]:
        if finding["kind"] != "TRUE_PRODUCT_CLONE":
            continue
        assert (ROOT / finding["path"]).is_file(), finding["path"]


def test_committed_register_matches_the_producer(findings):
    module = _load("open_findings", "scripts/build_open_findings.py")
    recomputed = module.build(ROOT)
    assert recomputed["summary"] == findings["summary"]


def test_no_author_decision_is_pending(findings):
    assert findings["summary"]["UNRESOLVED_AUTHOR_DECISION"] == 0


def test_no_statement_drift_remains(findings):
    assert findings["summary"]["STUDENT_TEACHER_STATEMENT_DRIFT"] == 0


def test_all_product_clones_are_closed(findings):
    """Gate produit : rouge tant que des clones restent, sans xfail."""

    assert findings["summary"]["TRUE_PRODUCT_CLONES_OPEN"] == 0
