from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_residual_true_new_forensics.py"
INITIAL_JSON = ROOT / "audit" / "TRUE_NEW_18_FORENSICS.json"
INITIAL_MD = ROOT / "audit" / "TRUE_NEW_18_FORENSICS.md"
INVENTORY = ROOT / "audit" / "INVENTAIRE_COLLECTION.json"
X3_FINGERPRINT = "65b5b9f56ca8900a"


def _load_module():
    assert SCRIPT.is_file(), "le générateur résiduel doit exister"
    spec = importlib.util.spec_from_file_location(
        "build_residual_true_new_forensics",
        SCRIPT,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _inventory_copy(tmp_path: Path) -> Path:
    target = tmp_path / "INVENTAIRE_COLLECTION.json"
    target.write_bytes(INVENTORY.read_bytes())
    return target


def test_builds_exact_residual_without_mutating_frozen_inputs(tmp_path: Path) -> None:
    module = _load_module()
    frozen_before = {
        INITIAL_JSON: INITIAL_JSON.read_bytes(),
        INITIAL_MD: INITIAL_MD.read_bytes(),
    }

    reports = module.build_reports(ROOT)
    module.write_reports(reports, tmp_path)
    first_bytes = {
        path.name: path.read_bytes() for path in sorted(tmp_path.iterdir())
    }
    module.write_reports(reports, tmp_path)

    assert {path.name: path.read_bytes() for path in sorted(tmp_path.iterdir())} == (
        first_bytes
    )
    assert {path: path.read_bytes() for path in frozen_before} == frozen_before
    assert set(first_bytes) == {
        "CURRENT_ANOMALY_SET_ALGEBRA_RESIDUAL.json",
        "CURRENT_ANOMALY_SET_ALGEBRA_RESIDUAL.md",
        "RESIDUAL_TRUE_NEW_FORENSICS.json",
        "RESIDUAL_TRUE_NEW_FORENSICS.md",
    }

    residual = reports["residual_forensics"]
    algebra = reports["residual_algebra"]
    forensic_source_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert residual["forensic_source_sha"] == forensic_source_sha
    assert algebra["forensic_source_sha"] == forensic_source_sha
    expected_counts = {
        "TRUE_NEW_INITIAL": 18,
        "ACTIVE_FINGERPRINTS_CLOSED": 0,
        "REMOVED": 0,
        "REVIEW_CLOSED": 0,
        "CONTENT_FINDINGS_FIXED": 8,
        "NEW_AFTER_TRIAGE": 1,
        "RESIDUAL_TRUE_NEW": 19,
    }
    assert residual["counts"] == expected_counts
    assert algebra["counts"] == expected_counts
    assert len(residual["entries"]) == 19
    assert algebra["equalities"] == {
        "initial_still_active_unqualified": True,
        "new_after_triage_is_exactly_x3": True,
        "residual_equation": True,
    }

    required = {
        "fingerprint",
        "object_id",
        "path",
        "category",
        "why_legitimate",
        "why_cannot_close",
        "current_review_state",
        "owner",
        "closure_phase",
        "release_acceptance",
        "source_sha",
        "triage_class",
        "reason_created",
    }
    assert all(required <= set(entry) for entry in residual["entries"])
    assert all(
        entry["triage_class"] == "LEGITIMATE_REVIEW_DEBT"
        and entry["release_acceptance"] is False
        and entry["source_sha"].startswith("sha256:")
        for entry in residual["entries"]
    )
    x3 = next(
        entry
        for entry in residual["entries"]
        if entry["fingerprint"] == X3_FINGERPRINT
    )
    assert x3["object_id"] == "1SPE-VARALEA-CR-X3"
    assert x3["reason_created"] == "OTHER_PROVED_EDITORIAL_NEED"
    assert x3["source_sha"] == "sha256:" + hashlib.sha256(
        (ROOT / x3["path"]).read_bytes()
    ).hexdigest()


def test_rejects_any_unexpected_active_unqualified_fingerprint(
    tmp_path: Path,
) -> None:
    module = _load_module()
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    inventory["anomaly_qualifications"]["ffffffffffffffff"] = {
        "blocking": True,
        "categories": ["blocking_statuses"],
        "category": "blocking_statuses",
        "disposition": "open_debt",
        "fingerprint": "ffffffffffffffff",
        "occurrence_count": 1,
        "qualified": False,
        "raw_identities": ["f" * 64],
    }
    mutated = tmp_path / "inventory-extra.json"
    mutated.write_text(json.dumps(inventory), encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="ensemble actif non qualifié inattendu",
    ):
        module.build_reports(ROOT, inventory_path=mutated)


@pytest.mark.parametrize("field,value", [("qualified", True), ("disposition", "fixed")])
def test_rejects_an_initial_fingerprint_that_is_no_longer_open_unqualified(
    tmp_path: Path,
    field: str,
    value: object,
) -> None:
    module = _load_module()
    inventory = copy.deepcopy(
        json.loads(INVENTORY.read_text(encoding="utf-8"))
    )
    initial = json.loads(INITIAL_JSON.read_text(encoding="utf-8"))
    fingerprint = initial["entries"][0]["fingerprint"]
    inventory["anomaly_qualifications"][fingerprint][field] = value
    mutated = tmp_path / f"inventory-{field}.json"
    mutated.write_text(json.dumps(inventory), encoding="utf-8")

    with pytest.raises(ValueError, match="18 fingerprints initiaux"):
        module.build_reports(ROOT, inventory_path=mutated)
