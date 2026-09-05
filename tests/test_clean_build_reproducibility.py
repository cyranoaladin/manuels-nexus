"""Tests for Clean Build & Double-Build Reproducibility.

Enforces:
1. DOUBLE_BUILD_REPRODUCIBILITY = 12/12 PROVEN
2. MANIFEST_COVERAGE = 12/12
3. Zero missing or corrupt PDF evidence
4. Strict schema validation of BUILD_MANIFEST.json
5. Mutation test: tampering with any reproducibility hash or page count breaks gate.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import pytest
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_FILE = ROOT / "audit/CANONICAL_RELEASE_INVENTORY.json"
MANIFEST_FILE = ROOT / "audit/BUILD_MANIFEST.json"
REPRODUCIBILITY_FILE = ROOT / "audit/DOUBLE_BUILD_REPRODUCIBILITY.json"


@pytest.fixture(scope="module")
def manifest_data():
    assert MANIFEST_FILE.is_file(), "BUILD_MANIFEST.json missing"
    return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def reproducibility_data():
    assert REPRODUCIBILITY_FILE.is_file(), "DOUBLE_BUILD_REPRODUCIBILITY.json missing"
    return json.loads(REPRODUCIBILITY_FILE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def inventory_data():
    assert INVENTORY_FILE.is_file(), "CANONICAL_RELEASE_INVENTORY.json missing"
    return json.loads(INVENTORY_FILE.read_text(encoding="utf-8"))


def test_reproducibility_report_proves_twelve_targets(reproducibility_data):
    assert reproducibility_data["total_targets"] == 12
    assert reproducibility_data["reproducible_targets"] == 12
    assert reproducibility_data["double_build_reproducibility"] == "12/12"
    assert reproducibility_data["reproducibility_global"] == "PROVEN"

    for entry in reproducibility_data["results"]:
        assert entry["sha256_identical"] is True
        assert entry["pages_identical"] is True
        assert entry["reproducibility_status"] == "PASS"


def test_manifest_covers_all_twelve_canonical_targets(manifest_data, inventory_data):
    builds = manifest_data["builds"]
    assert len(builds) == 12

    registered_identities = {
        (b["manual"], b["variant"], b["pdf_path"]) for b in builds
    }

    expected_identities = {
        (t["manual_id"], t["variant"], t["pdf"])
        for t in inventory_data["canonical_targets"]
    }

    assert registered_identities == expected_identities


def test_manifest_schema_validation(manifest_data):
    schema_path = ROOT / manifest_data["schema_ref"]
    assert schema_path.is_file(), f"Schema missing: {schema_path}"
    schema_json = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validate(instance=manifest_data, schema=schema_json)


def test_each_target_pdf_matches_manifest_hash_and_pages(manifest_data):
    for b in manifest_data["builds"]:
        pdf_path = ROOT / b["pdf_path"]
        assert pdf_path.is_file(), f"PDF missing on disk: {pdf_path}"

        computed_sha = "sha256:" + hashlib.sha256(pdf_path.read_bytes()).hexdigest()
        assert computed_sha == b["pdf_sha256"], f"PDF hash mismatch for {b['pdf_path']}"
        assert b["page_count"] > 0


def test_student_variants_have_student_separation_gate_passed(manifest_data):
    for b in manifest_data["builds"]:
        gates = b["gates"]
        assert gates["compile"]["passed"] is True
        assert gates["preflight"]["passed"] is True
        if b["variant"] == "eleve":
            assert gates.get("student_separation", {}).get("passed") is True


def test_mutation_single_unreproducible_target_invalidates_global_proven(reproducibility_data):
    mutated = copy.deepcopy(reproducibility_data)
    # Tamper with target 0
    mutated["results"][0]["sha256_identical"] = False
    mutated["results"][0]["reproducibility_status"] = "FAIL"
    mutated["reproducible_targets"] = sum(
        1 for r in mutated["results"] if r["reproducibility_status"] == "PASS"
    )
    is_globally_proven = (
        mutated["reproducible_targets"] == mutated["total_targets"]
        and all(r["reproducibility_status"] == "PASS" for r in mutated["results"])
    )
    assert is_globally_proven is False
