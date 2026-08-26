from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_1spe_suites_human_gate_contract.py"
JSON_OUTPUT = ROOT / "audit" / "HUMAN_REVIEW_GATE_CONTRACT_1SPE_SUITES.json"
MD_OUTPUT = ROOT / "audit" / "HUMAN_REVIEW_GATE_CONTRACT_1SPE_SUITES.md"
EXPECTED_FIVE = {
    "4b9a00c4ef815951": "1SPE-SUITES-CR-017",
    "85454c002c0a1d6a": "1SPE-SUITES-EX-051",
    "8ca4f3f2a9212e39": "1SPE-SUITES-RE-C8",
    "d6985b17d7cab316": "1SPE-SUITES-ME-008",
    "e8ac154947fefcdb": "1SPE-SUITES-CO-051",
}


def _producer():
    assert SCRIPT.is_file(), f"producteur absent: {SCRIPT}"
    spec = importlib.util.spec_from_file_location(
        "build_1spe_suites_human_gate_contract", SCRIPT
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_fails_closed_on_all_undefined_semantics() -> None:
    payload = _producer().build_contract()

    assert payload["verdict"] == "GOVERNANCE_CONTRACT_INCOMPLETE"
    assert payload["approval_materialization_allowed"] is False
    assert payload["status_transition_allowed"] is False
    assert payload["debt_closure_allowed"] is False
    assert payload["required_roles"] == [
        "expert mathématique",
        "expert programme/pédagogie",
    ]
    assert payload["required_role_reviews"] == 2
    assert payload["auto_approval_allowed"] is False
    assert payload["human_contract_semantics"] == {
        "distinct_human_reviewers": "UNKNOWN",
        "one_human_may_satisfy_two_roles": "UNKNOWN",
        "identity_authentication_requirements": "UNKNOWN",
        "canonical_receipt_schema": "UNKNOWN",
        "canonical_allowed_approval_verdicts": "UNKNOWN",
        "approval_scope_granularity": "UNKNOWN",
        "source_sha_binding": "UNKNOWN",
        "render_pdf_binding": "UNKNOWN",
        "shared_dependency_staleness_policy": "UNKNOWN",
        "bulk_status_transition_authority": "UNKNOWN",
    }
    assert payload["unknown_contract_semantics"] == 10


def test_qcm_gate_is_pending_and_has_no_invented_owner() -> None:
    qcm = _producer().build_contract()["qcm_human_gate"]
    assert qcm == {
        "owner": "UNKNOWN",
        "granularity": "UNKNOWN",
        "current_state": "HUMAN_APPROVAL_PENDING_NO_AUTO_APPROVAL",
        "covered_by_math_role": "UNPROVED",
        "covered_by_programme_pedagogy_role": "UNPROVED",
        "distinct_campaign_required": "UNPROVED",
        "closure_materialization_allowed": False,
    }


def test_debt_intersections_and_stale_bindings_are_exact() -> None:
    payload = _producer().build_contract()
    rows = payload["residual13_chapter_intersection"]
    assert {row["fingerprint"]: row["object_id"] for row in rows} == EXPECTED_FIVE
    assert len(rows) == 5
    assert sum(row["sunset_source_binding_stale"] for row in rows) == 4
    assert all(row["machine_review_state"] == "MACHINE_PASS" for row in rows)
    assert all(row["current_status"] == "generated" for row in rows)
    assert all(row["closure_allowed"] is False for row in rows)
    assert payload["previous89_chapter_intersection"] == []
    assert payload["counts"]["previous89_chapter_debts"] == 0


def test_authorities_do_not_treat_local_role_tokens_or_legacy_file_as_contract() -> None:
    payload = _producer().build_contract()
    authority_ids = {row["authority_id"] for row in payload["authorities"]}
    assert {
        "CAHIER_TRACEABILITY",
        "CAHIER_DOUBLE_REVIEW",
        "CAHIER_ARCHIVAL",
        "README_RELEASE_INDEPENDENCE",
        "README_REVIEW_CHAIN",
        "GENERIC_VALIDATION_SCHEMA",
        "GENERIC_VALIDATION_DATABASE",
        "LEGACY_OBJECT_RECEIPT_CONVENTION",
        "QCM_MACHINE_AUDIT",
    } <= authority_ids
    assert payload["local_packet_role_tokens_are_canonical_authority"] is False
    assert payload["legacy_receipt_filename_is_sufficient_approval_contract"] is False
    assert payload["content_review_is_final_visual_or_d7_approval"] is False


def test_validator_rejects_approval_owner_or_unknown_erasure() -> None:
    producer = _producer()
    payload = producer.build_contract()
    mutations = []
    approved = copy.deepcopy(payload)
    approved["approval_materialization_allowed"] = True
    mutations.append(approved)
    owner = copy.deepcopy(payload)
    owner["qcm_human_gate"]["owner"] = "EXPERT_MATHEMATIQUE"
    mutations.append(owner)
    no_unknown = copy.deepcopy(payload)
    no_unknown["human_contract_semantics"]["canonical_receipt_schema"] = "DEFINED"
    mutations.append(no_unknown)
    closed = copy.deepcopy(payload)
    closed["residual13_chapter_intersection"][0]["closure_allowed"] = True
    mutations.append(closed)
    for mutation in mutations:
        with pytest.raises(ValueError):
            producer.validate_contract(mutation)


def test_outputs_and_check_cli_are_deterministic_when_present() -> None:
    producer = _producer()
    payload = producer.build_contract()
    if JSON_OUTPUT.exists() and MD_OUTPUT.exists():
        assert JSON_OUTPUT.read_text(encoding="utf-8") == producer.render_json(payload)
        assert MD_OUTPUT.read_text(encoding="utf-8") == producer.render_markdown(payload)
        run = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
        assert run.returncode == 0, run.stderr
        assert "GOVERNANCE_CONTRACT_INCOMPLETE" in run.stdout
