from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_latex_layout_warning_ledger.py"
LEDGER = ROOT / "audit" / "LATEX_LAYOUT_WARNING_LEDGER.json"


def _producer():
    assert SCRIPT.is_file(), f"missing fixed producer: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("latex_layout_warning_ledger", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256_at_revision(revision: str, path: str) -> str:
    content = subprocess.run(
        ["git", "show", f"{revision}:{path}"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout
    return hashlib.sha256(content).hexdigest()


def test_layout_warning_ledger_is_exact_partition_with_visual_evidence() -> None:
    producer = _producer()
    payload = producer.build_ledger()
    summary = payload["summary"]
    warnings = payload["warnings"]

    assert payload["scope"] == "OVERFULL_UNDERFULL"
    assert payload["build_source_sha"] == (
        "5d935e720a82e207d7a8769f6bd2608ef1160322"
    )
    assert payload["applicable_source_freeze_sha"] == (
        "c667f12b1792f31981b6b5894c8c604df1bce634"
    )
    assert summary == {
        "total": 25,
        "overfull": 21,
        "underfull": 4,
        "visible_overfull": 0,
        "visible_underfull": 2,
        "unclassified": 0,
        "unknown": 0,
        "by_variant": {"eleve": 12, "professeur": 13},
    }
    assert len(warnings) == 25
    assert len({row["warning_id"] for row in warnings}) == 25
    assert Counter(row["warning_type"] for row in warnings) == {
        "OVERFULL_HBOX": 21,
        "UNDERFULL_HBOX": 4,
    }
    assert Counter(row["variant"] for row in warnings) == {
        "eleve": 12,
        "professeur": 13,
    }
    assert sum(row["visible"] for row in warnings) == 2
    assert {row["actionable"] for row in warnings} == {True}
    assert {row["resolution_state"] for row in warnings} == {"OPEN"}
    assert all(row["classification"] and "UNKNOWN" not in row["classification"] for row in warnings)
    assert all(row["visual_inspection"]["dpi"] >= 150 for row in warnings)
    assert all(row["visual_inspection"]["pdf_page"] == row["pdf_page"] for row in warnings)
    assert all(row["visual_inspection"]["human_approval"] is False for row in warnings)

    toc = [row for row in warnings if row["warning_type"] == "OVERFULL_HBOX"]
    assert {row["amount_pt"] for row in toc} == {0.95421}
    assert {row["source"] for row in toc} == {
        "gabarits/common/nexus-pages-froides.sty"
    }
    assert {row["source_line_range"] for row in toc} == {"116-130"}
    assert {row["visible"] for row in toc} == {False}

    expected_toc = {
        ("eleve", 7, 119), ("eleve", 7, 149), ("eleve", 7, 185),
        ("eleve", 8, 215), ("eleve", 8, 233), ("eleve", 8, 258),
        ("eleve", 8, 283), ("eleve", 8, 311), ("eleve", 9, 345),
        ("eleve", 9, 349),
        ("professeur", 7, 136), ("professeur", 7, 238),
        ("professeur", 7, 293), ("professeur", 7, 362),
        ("professeur", 8, 416), ("professeur", 8, 444),
        ("professeur", 8, 483), ("professeur", 8, 523),
        ("professeur", 8, 564), ("professeur", 9, 613),
        ("professeur", 9, 617),
    }
    assert {(row["variant"], row["pdf_page"], row["rendered_page_number"]) for row in toc} == expected_toc

    underfull = [row for row in warnings if row["warning_type"] == "UNDERFULL_HBOX"]
    assert {
        (row["variant"], row["object_id"], row["pdf_page"], row["badness"], row["visible"])
        for row in underfull
    } == {
        ("eleve", "1SPE-GEOREP-CR-013", 265, 5217, False),
        ("professeur", "1SPE-GEOREP-CR-013", 491, 5217, False),
        ("eleve", "1SPE-VARALEA-FR-R2", 342, 2460, True),
        ("professeur", "1SPE-VARALEA-FR-R2", 600, 2460, True),
    }


def test_layout_warning_ledger_binds_causal_sources_and_names_out_of_scope_families() -> None:
    producer = _producer()
    payload = producer.build_ledger()

    for proof in payload["causal_source_proofs"]:
        assert proof["sha256"] == _sha256_at_revision(
            payload["applicable_source_freeze_sha"], proof["path"]
        )
        assert proof["unchanged_from_build_to_freeze"] is True

    assert payload["evidence"]["visual_inspection"]["dpi"] == 200
    assert payload["evidence"]["visual_inspection"]["pages_inspected"] == {
        "eleve": [7, 8, 9, 265, 342],
        "professeur": [7, 8, 9, 491, 599, 600],
    }
    assert payload["out_of_scope_warning_families"] == [
        {
            "family": "TYPEAREA_WARNING",
            "eleve_count": 1,
            "professeur_count": 1,
            "status": "REQUIRES_SEPARATE_TRIAGE",
        },
        {
            "family": "SCRLAYER_FOOTHEIGHT_TOO_LOW",
            "eleve_count": 3,
            "professeur_count": 3,
            "status": "REQUIRES_SEPARATE_TRIAGE",
        },
        {
            "family": "PDF_BACKEND_POP_EMPTY_COLOR_PAGE_STACK",
            "eleve_count": 943,
            "professeur_count": 3008,
            "status": "REQUIRES_SEPARATE_TRIAGE",
        },
        {
            "family": "MICROTYPE_MISSING_CHARACTER_INFO",
            "eleve_count": 1888,
            "professeur_count": 1913,
            "status": "INFORMATION_NOT_WARNING_REQUIRES_SEPARATE_REVIEW",
        },
    ]
    assert "does not prove all LaTeX warning families classified" in payload["scope_warning"]


def test_layout_warning_ledger_validator_rejects_mutations() -> None:
    producer = _producer()
    payload = producer.build_ledger()
    mutations = []

    missing = copy.deepcopy(payload)
    missing["warnings"].pop()
    mutations.append(missing)

    duplicate = copy.deepcopy(payload)
    duplicate["warnings"].append(copy.deepcopy(duplicate["warnings"][0]))
    mutations.append(duplicate)

    wrong_partition = copy.deepcopy(payload)
    wrong_partition["summary"]["overfull"] = 20
    mutations.append(wrong_partition)

    unknown = copy.deepcopy(payload)
    unknown["warnings"][0]["classification"] = "UNKNOWN"
    mutations.append(unknown)

    no_inspection = copy.deepcopy(payload)
    no_inspection["warnings"][0]["visual_inspection"] = {}
    mutations.append(no_inspection)

    auto_benign = copy.deepcopy(payload)
    auto_benign["warnings"][0]["classification"] = "BENIGN_SMALL_AMOUNT"
    mutations.append(auto_benign)

    stale_source = copy.deepcopy(payload)
    stale_source["causal_source_proofs"][0]["sha256"] = "0" * 64
    mutations.append(stale_source)

    for mutation in mutations:
        with pytest.raises(ValueError):
            producer.validate_ledger(mutation)


def test_layout_warning_ledger_fixed_output_and_check_are_deterministic() -> None:
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
    assert "21 Overfull + 4 Underfull" in runs[0].stdout
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
