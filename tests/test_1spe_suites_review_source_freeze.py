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
SCRIPT = ROOT / "scripts" / "build_1spe_suites_review_source_freeze.py"
OUTPUT = ROOT / "audit" / "1SPE_SUITES_REVIEW_SOURCE_FREEZE.json"
SOURCE_SHA = "1057951c1a7e8be8731982b5918effb60f2471cc"


def _producer():
    assert SCRIPT.is_file(), f"producteur absent: {SCRIPT}"
    spec = importlib.util.spec_from_file_location(
        "build_1spe_suites_review_source_freeze", SCRIPT
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git_bytes(path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{SOURCE_SHA}:{path}"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout


def _git_blob(path: str) -> str:
    return subprocess.run(
        ["git", "rev-parse", f"{SOURCE_SHA}:{path}"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def test_exact_candidate_and_161_source_bindings() -> None:
    payload = _producer().build_freeze()

    assert payload["source_sha"] == SOURCE_SHA
    assert payload["counts"] == {
        "chapter_objects": 161,
        "tex_meta_objects": 160,
        "synthetic_qcm_objects": 1,
        "remediation_sources": 13,
        "unknown": 0,
    }
    rows = payload["objects"]
    assert len(rows) == len({row["object_id"] for row in rows}) == 161
    assert {row["source_kind"] for row in rows} == {
        "TEX_META",
        "SYNTHETIC_QCM_CANONICAL",
    }
    for row in rows:
        source = _git_bytes(row["path"])
        assert row["source_sha256"] == hashlib.sha256(source).hexdigest()
        assert row["git_blob_sha1"] == _git_blob(row["path"])


def test_contract_qcm_remediation_manifest_and_programme_authority_are_bound() -> None:
    payload = _producer().build_freeze()

    for key in ("contract", "relevant_manifest"):
        binding = payload[key]
        assert binding["sha256"] == hashlib.sha256(_git_bytes(binding["path"])).hexdigest()
        assert binding["git_blob_sha1"] == _git_blob(binding["path"])

    qcm = payload["qcm"]
    for key in ("canonical", "generated_tex"):
        binding = qcm[key]
        assert binding["sha256"] == hashlib.sha256(_git_bytes(binding["path"])).hexdigest()
        assert binding["git_blob_sha1"] == _git_blob(binding["path"])

    remediation = payload["remediation"]
    assert len(remediation["sources"]) == 13
    assert remediation["aggregate_digest"] == _producer().canonical_digest(
        remediation["sources"]
    )
    authority = payload["programme_authority"]
    assert authority["sources"]
    assert authority["aggregate_digest"] == _producer().canonical_digest(
        authority["sources"]
    )
    assert payload["chapter_object_set_digest"] == _producer().canonical_digest(
        payload["objects"]
    )


def test_validator_fails_closed_on_any_source_or_set_mutation() -> None:
    producer = _producer()
    payload = producer.build_freeze()

    mutations = []
    wrong_sha = copy.deepcopy(payload)
    wrong_sha["source_sha"] = "0" * 40
    mutations.append(wrong_sha)
    missing = copy.deepcopy(payload)
    missing["objects"].pop()
    mutations.append(missing)
    changed_blob = copy.deepcopy(payload)
    changed_blob["objects"][0]["git_blob_sha1"] = "0" * 40
    mutations.append(changed_blob)
    unknown = copy.deepcopy(payload)
    unknown["counts"]["unknown"] = 1
    mutations.append(unknown)

    for mutation in mutations:
        with pytest.raises(ValueError):
            producer.validate_freeze(mutation)


def test_fixed_output_and_check_cli_are_deterministic_when_present() -> None:
    producer = _producer()
    payload = producer.build_freeze()
    if OUTPUT.exists():
        assert OUTPUT.read_text(encoding="utf-8") == producer.render_json(payload)
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
        assert runs[0].stderr == runs[1].stderr == ""
        assert "161 objects" in runs[0].stdout


def test_derived_manifest_envelope_drift_does_not_rebind_content_freeze(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    producer = _producer()
    payload = producer.build_freeze()
    original = producer._current_blob

    def current_blob(path: str) -> str:
        if path == "audit/BUILD_MANIFEST.json":
            raise AssertionError("derived manifest must not be a live content binding")
        return original(path)

    monkeypatch.setattr(producer, "_current_blob", current_blob)
    producer.validate_current_bindings(payload)


def test_cli_has_no_arbitrary_output_or_source_override() -> None:
    run = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
        timeout=30,
    )
    assert "--check" in run.stdout
    assert "--output" not in run.stdout
    assert "--source-sha" not in run.stdout
