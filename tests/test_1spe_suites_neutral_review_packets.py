from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_1spe_suites_neutral_review_packets.py"
FREEZE = ROOT / "audit" / "1SPE_SUITES_REVIEW_SOURCE_FREEZE.json"
OUTPUTS = {
    "EXPERT_MATHEMATIQUE": (
        ROOT / "audit" / "1SPE_SUITES_EXPERT_MATHEMATIQUE_NEUTRAL_REVIEW_PACKET.json",
        ROOT / "audit" / "1SPE_SUITES_EXPERT_MATHEMATIQUE_NEUTRAL_REVIEW_PACKET.md",
    ),
    "EXPERT_PROGRAMME_PEDAGOGIE": (
        ROOT
        / "audit"
        / "1SPE_SUITES_EXPERT_PROGRAMME_PEDAGOGIE_NEUTRAL_REVIEW_PACKET.json",
        ROOT
        / "audit"
        / "1SPE_SUITES_EXPERT_PROGRAMME_PEDAGOGIE_NEUTRAL_REVIEW_PACKET.md",
    ),
}
EXPECTED_SOURCE_SHA = "2b00c28fa0e4a96737d787db9c9110071af36968"
EXPECTED_OBJECT_SET_DIGEST = (
    "sha256:e10cfdd9d6f500d7693cbec9f714a34e51fb43b75defc6e205642c74a23c6b9d"
)
EXPECTED_ATOMS = {f"1SPE-OFFICIAL-{number:03d}" for number in range(48, 63)}
EXPECTED_CORRECTION_CLASSES = {
    "Q_ZERO_IS_ALLOWED",
    "ZERO_POWER_ZERO_AVOIDED",
    "QUOTIENT_IS_CONDITIONAL_CHARACTERIZATION",
    "ZERO_SEQUENCE_AND_ZERO_TERMS_ALLOWED",
    "MINUS_ONE_POWER_N_IS_GEOMETRIC",
    "FINITE_PREFIX_DOES_NOT_PROVE_UNIVERSAL_PROPERTY",
    "U_OF_N_IS_VALID_FUNCTION_NOTATION",
}
FORBIDDEN_EXECUTABLE_KEYS = {
    "approval",
    "approved",
    "assigned_reviewer",
    "receipt",
    "receipt_path",
    "reviewer_identity",
    "status_transition",
    "new_status",
    "full_promotion",
}


def _producer():
    assert SCRIPT.is_file(), f"producteur absent: {SCRIPT}"
    spec = importlib.util.spec_from_file_location(
        "build_1spe_suites_neutral_review_packets", SCRIPT
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def test_two_independent_packets_are_bound_to_the_exact_freeze() -> None:
    packets = _producer().build_packets()
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))

    assert set(packets) == set(OUTPUTS)
    assert packets["EXPERT_MATHEMATIQUE"] is not packets[
        "EXPERT_PROGRAMME_PEDAGOGIE"
    ]
    for role, packet in packets.items():
        assert packet["review_role"] == role
        assert packet["chapter"] == "1SPE-SUITES"
        assert packet["source_freeze"]["source_sha"] == EXPECTED_SOURCE_SHA
        assert (
            packet["source_freeze"]["chapter_object_set_digest"]
            == EXPECTED_OBJECT_SET_DIGEST
        )
        assert packet["current_content_to_review"]["objects"] == freeze["objects"]
        assert packet["counts"]["objects"] == 161
        assert len(packet["current_content_to_review"]["objects"]) == 161


def test_packets_are_neutral_and_expose_no_executable_decision_surface() -> None:
    packets = _producer().build_packets()
    for packet in packets.values():
        assert packet["governance"]["contract_state"] == (
            "GOVERNANCE_CONTRACT_INCOMPLETE"
        )
        assert packet["governance"]["decision_capture"] == "DISABLED"
        assert packet["governance"]["human_review_state"] == "PENDING_UNASSIGNED"
        assert packet["governance"]["qcm_gate_owner"] == "UNKNOWN"
        assert packet["governance"]["qcm_gate_granularity"] == "UNKNOWN"
        assert packet["neutrality_invariants"] == {
            "executable_receipt_zone": False,
            "prechecked_decision": False,
            "status_or_full_transition": False,
            "debt_closure": False,
            "d7_or_visual_final_decision": False,
        }
        assert not (set(_walk_keys(packet)) & FORBIDDEN_EXECUTABLE_KEYS)
        serialized = json.dumps(packet, ensure_ascii=False)
        assert '"APPROVE"' not in serialized
        assert '"REQUEST_CHANGES"' not in serialized
        assert '"REJECT"' not in serialized


def test_each_packet_contains_complete_current_review_material() -> None:
    packets = _producer().build_packets()
    for packet in packets.values():
        current = packet["current_content_to_review"]
        assert len(current["chapter_pdfs"]) == 4
        assert sum(row["pages"] for row in current["chapter_pdfs"]) == 209
        assert all(row["sha256"].startswith("sha256:") for row in current["chapter_pdfs"])
        assert all(row["use"] == "CONTENT_REVIEW_AID_ONLY" for row in current["chapter_pdfs"])
        assert current["pdf_limitations"]["release_proof"] is False
        assert current["pdf_limitations"]["d7_or_final_visual_proof"] is False
        assert current["pdf_limitations"]["global_manual_layout_proof"] is False

        programme = packet["programme_mapping"]
        assert programme["nor"] == "MENE2602917A"
        assert programme["mandatory_atoms_count"] == 15
        assert programme["full_atoms_count"] == 0
        assert {row["atom_id"] for row in programme["mandatory_atoms"]} == (
            EXPECTED_ATOMS
        )

        qcm = packet["qcm_review_material"]
        assert qcm["questions_count"] == 21
        assert len(qcm["questions"]) == 21
        assert qcm["human_state"] == "HUMAN_APPROVAL_PENDING_NO_AUTO_APPROVAL"
        assert qcm["human_gate_owner"] == "UNKNOWN"
        assert qcm["human_gate_granularity"] == "UNKNOWN"

        remediation = packet["remediation_review_material"]
        assert remediation["source_count"] == 13
        assert len(remediation["sources"]) == 13
        assert remediation["required_capacity_loops"] == 8
        assert remediation["machine_validated_capacity_loops"] == 8
        assert remediation["exercise_correction_pairs"] == 44


def test_fix_history_is_separate_and_exact() -> None:
    packets = _producer().build_packets()
    for packet in packets.values():
        history = packet["change_history_fix_evidence"]
        p0 = history["wrong_year_p0"]
        assert p0["object_count"] == 19
        assert len(p0["objects"]) == 19
        assert p0["claim_count"] == 77
        assert p0["rewritten_claim_count"] == 34
        assert p0["technical_oracle_count"] == 19
        assert all(row["current_frozen_source_sha256"] for row in p0["objects"])
        classes = history["other_scientific_corrections"]
        assert {row["class_id"] for row in classes} == EXPECTED_CORRECTION_CLASSES
        assert all(row["evidence_paths"] for row in classes)
        assert history["scope"] == "CHANGE_HISTORY_FIX_EVIDENCE_NOT_CURRENT_CONTENT"


def test_role_checklists_are_distinct_and_have_source_navigation() -> None:
    packets = _producer().build_packets()
    math = packets["EXPERT_MATHEMATIQUE"]
    pedagogy = packets["EXPERT_PROGRAMME_PEDAGOGIE"]
    assert math["role_checklist"] != pedagogy["role_checklist"]
    assert len(math["role_checklist"]) >= 15
    assert len(pedagogy["role_checklist"]) >= 15
    assert all(item["evidence_refs"] for item in math["role_checklist"])
    assert all(item["evidence_refs"] for item in pedagogy["role_checklist"])
    assert all("recording" not in item for item in math["role_checklist"])
    assert all("recording" not in item for item in pedagogy["role_checklist"])


def test_validator_rejects_any_governance_or_freeze_promotion() -> None:
    producer = _producer()
    packet = producer.build_packets()["EXPERT_MATHEMATIQUE"]
    mutations = []
    decision = copy.deepcopy(packet)
    decision["governance"]["decision_capture"] = "ENABLED"
    mutations.append(decision)
    owner = copy.deepcopy(packet)
    owner["governance"]["qcm_gate_owner"] = "EXPERT_MATHEMATIQUE"
    mutations.append(owner)
    full = copy.deepcopy(packet)
    full["programme_mapping"]["full_atoms_count"] = 15
    mutations.append(full)
    changed_set = copy.deepcopy(packet)
    changed_set["current_content_to_review"]["objects"].pop()
    mutations.append(changed_set)
    executable = copy.deepcopy(packet)
    executable["receipt"] = {"verdict": "APPROVE"}
    mutations.append(executable)
    for mutation in mutations:
        with pytest.raises(ValueError):
            producer.validate_packet(mutation)


def test_outputs_and_check_cli_are_deterministic_when_present() -> None:
    producer = _producer()
    packets = producer.build_packets()
    if all(path.exists() for pair in OUTPUTS.values() for path in pair):
        for role, (json_path, md_path) in OUTPUTS.items():
            assert json_path.read_text(encoding="utf-8") == producer.render_json(
                packets[role]
            )
            assert md_path.read_text(encoding="utf-8") == producer.render_markdown(
                packets[role]
            )
        run = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
        assert run.returncode == 0, run.stderr
        assert "two neutral packets current" in run.stdout
