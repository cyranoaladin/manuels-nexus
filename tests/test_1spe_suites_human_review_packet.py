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
SCRIPT = ROOT / "scripts" / "build_1spe_suites_human_review_packet.py"
JSON_OUTPUT = ROOT / "audit" / "1SPE_SUITES_HUMAN_REVIEW_PACKET.json"
MD_OUTPUT = ROOT / "audit" / "1SPE_SUITES_HUMAN_REVIEW_PACKET.md"
CHAPTER = ROOT / "Mathematiques" / "manuel-maths" / "chapitres" / "1SPE-SUITES"
QCM_JSON = CHAPTER / "qcm" / "1SPE-SUITES-QCM.json"
QCM_TEX = CHAPTER / "qcm" / "1SPE-SUITES-QCM.tex"
RESIDUAL = ROOT / "audit" / "RESIDUAL_TRUE_NEW_FORENSICS.json"

EXPECTED_RESIDUAL = {
    "1SPE-SUITES-CR-017": "4b9a00c4ef815951",
    "1SPE-SUITES-EX-051": "85454c002c0a1d6a",
    "1SPE-SUITES-RE-C8": "8ca4f3f2a9212e39",
    "1SPE-SUITES-ME-008": "d6985b17d7cab316",
    "1SPE-SUITES-CO-051": "e8ac154947fefcdb",
}
DIMENSIONS = {
    "structure",
    "programme",
    "scientific",
    "pedagogical",
    "editorial",
    "variant",
    "visual",
}


def _producer():
    assert SCRIPT.is_file(), f"producteur absent: {SCRIPT}"
    spec = importlib.util.spec_from_file_location(
        "build_1spe_suites_human_review_packet", SCRIPT
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expected_tex_meta() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for path in sorted(CHAPTER.rglob("*.tex")):
        if path == QCM_TEX:
            continue
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
        assert first_line.startswith("% META: "), path
        meta = json.loads(first_line.removeprefix("% META: "))
        assert meta["id"] not in rows
        rows[meta["id"]] = {
            "path": path.relative_to(ROOT).as_posix(),
            "type": meta["type_objet"],
            "status": meta["status"],
            "source_sha256": _sha256(path),
        }
    assert len(rows) == 160
    return rows


def _walk(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)
    else:
        yield value


def test_exact_161_object_inventory_and_current_source_digests() -> None:
    payload = _producer().build_packet()
    objects = payload["objects"]
    regular = {row["object_id"]: row for row in objects if row["source_kind"] == "TEX_META"}
    synthetic = [row for row in objects if row["source_kind"] == "SYNTHETIC_QCM_CANONICAL"]

    assert payload["counts"]["objects"] == 161
    assert payload["counts"]["tex_meta_objects"] == 160
    assert payload["counts"]["synthetic_qcm_objects"] == 1
    assert len(objects) == len({row["object_id"] for row in objects}) == 161
    expected = _expected_tex_meta()
    assert set(regular) == set(expected)
    for object_id, expected_row in expected.items():
        assert {
            key: regular[object_id][key]
            for key in ("path", "type", "status", "source_sha256")
        } == expected_row

    assert len(synthetic) == 1
    qcm = synthetic[0]
    assert qcm["object_id"] == "1SPE-SUITES-QCM"
    assert qcm["path"] == QCM_JSON.relative_to(ROOT).as_posix()
    assert qcm["type"] == "qcm"
    assert qcm["status"] == "generated"
    assert qcm["source_sha256"] == _sha256(QCM_JSON)
    assert qcm["generated_tex_path"] == QCM_TEX.relative_to(ROOT).as_posix()
    assert qcm["generated_tex_sha256"] == _sha256(QCM_TEX)


def test_residual13_intersection_is_exact_five() -> None:
    payload = _producer().build_packet()
    assert payload["counts"]["residual13_intersection"] == 5
    assert {
        row["object_id"]: row["fingerprint"]
        for row in payload["residual13_intersection"]
    } == EXPECTED_RESIDUAL
    assert {
        row["object_id"] for row in payload["objects"] if row["residual13_member"]
    } == set(EXPECTED_RESIDUAL)


def test_machine_evidence_and_human_states_are_conservative() -> None:
    payload = _producer().build_packet()
    assert payload["chapter_state"] == "PENDING_HUMAN"
    assert payload["publication_approval"] is False
    assert payload["release_acceptance"] is False
    assert payload["contract"] == "draft"
    assert payload["human_review"]["independence_required"] is True
    roles = payload["human_review"]["roles"]
    assert [row["role"] for row in roles] == [
        "EXPERT_MATHEMATIQUE",
        "EXPERT_PROGRAMME_PEDAGOGIE",
    ]
    assert all(row["assigned_reviewer"] is None for row in roles)
    assert all(row["state"] == "PENDING" and row["approval"] is False for row in roles)

    expected_source_sha = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", str(CHAPTER.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    assert payload["review_source_sha"] == expected_source_sha
    assert payload["machine_review_campaign"]["reviewed_objects"] == 161
    assert payload["machine_review_campaign"]["targeted_tests"]["passed"] == 4339
    assert payload["machine_review_campaign"]["render_qa"]["pages_inspected"] == 209
    assert payload["machine_review_campaign"]["render_qa"]["visible_defects"] == 0

    pass_count = 0
    pending_count = 0
    for row in payload["objects"]:
        assert row["human_review_state"] == "PENDING_HUMAN"
        assert set(row["machine_review_dimensions"]) == DIMENSIONS
        states = {
            dimension: review["state"]
            for dimension, review in row["machine_review_dimensions"].items()
        }
        assert set(states.values()) == {"MACHINE_PASS"}
        for review in row["machine_review_dimensions"].values():
            assert review["explanation"]
            pass_count += 1
            assert review["evidence_refs"]

    assert pending_count == 0
    assert payload["counts"]["machine_pass_dimensions"] == pass_count == 1127
    assert payload["counts"]["machine_evidence_pending_dimensions"] == 0
    assert payload["counts"]["human_roles_required"] == 2
    assert payload["counts"]["human_roles_completed"] == 0
    assert payload["counts"]["unknown"] == 0
    assert "UNKNOWN" not in set(_walk(payload))
    assert "receipt" not in json.dumps(payload, sort_keys=True).lower()


def test_validator_fails_closed_on_approval_unknown_or_unsupported_pass() -> None:
    producer = _producer()
    payload = producer.build_packet()

    mutations = []
    approved = copy.deepcopy(payload)
    approved["publication_approval"] = True
    mutations.append(approved)
    forged_reviewer = copy.deepcopy(payload)
    forged_reviewer["human_review"]["roles"][0]["assigned_reviewer"] = "Agent"
    mutations.append(forged_reviewer)
    unknown = copy.deepcopy(payload)
    unknown["objects"][0]["machine_review_dimensions"]["programme"]["state"] = "UNKNOWN"
    mutations.append(unknown)
    unsupported_pass = copy.deepcopy(payload)
    regular = next(row for row in unsupported_pass["objects"] if row["source_kind"] == "TEX_META")
    regular["machine_review_dimensions"]["scientific"]["state"] = "MACHINE_PASS"
    regular["machine_review_dimensions"]["scientific"]["evidence_refs"] = []
    mutations.append(unsupported_pass)

    for mutation in mutations:
        with pytest.raises(ValueError):
            producer.validate_packet(mutation)


def test_rendered_outputs_and_check_cli_are_deterministic() -> None:
    producer = _producer()
    payload = producer.build_packet()
    assert JSON_OUTPUT.read_text(encoding="utf-8") == producer.render_json(payload)
    assert MD_OUTPUT.read_text(encoding="utf-8") == producer.render_markdown(payload)
    assert MD_OUTPUT.read_text(encoding="utf-8").count("| `1SPE-SUITES-") == 161

    commands = []
    for _ in range(2):
        commands.append(
            subprocess.run(
                [sys.executable, str(SCRIPT), "--check"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )
        )
    assert [run.returncode for run in commands] == [0, 0]
    assert commands[0].stdout == commands[1].stdout
    assert "161 objects" in commands[0].stdout
    assert "UNKNOWN=0" in commands[0].stdout
    assert commands[0].stderr == commands[1].stderr == ""


def test_cli_exposes_only_fixed_repository_outputs() -> None:
    help_run = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
        timeout=30,
    )
    assert "--check" in help_run.stdout
    assert "--json" not in help_run.stdout
    assert "--output" not in help_run.stdout
