"""Mutation contract for the exact residual-13 baseline qualification.

Each test exercises one clause (A--H) of the human decision without touching
the tracked baseline, policy, dispositions, or D7 oracle.  Repository controls
are copied into ``tmp_path`` and evaluated through the production validators.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
from copy import deepcopy
from pathlib import Path

import jsonschema
import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
POLICY_REL = Path("audit/BASELINE_QUALIFICATION_POLICY.yaml")
BASELINE_REL = Path("audit/ANOMALIES_BASELINE.json")
DISPOSITIONS_REL = Path("audit/ANOMALY_DISPOSITIONS.yaml")
POLICY_SCHEMA_REL = Path(
    "audit/schemas/v1/baseline-qualification-policy.schema.json"
)


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def inventory_module():
    return _load_module(
        ROOT / "scripts/inventory_collection.py",
        "inventory_collection_residual13_mutations",
    )


@pytest.fixture()
def qualification_module():
    return _load_module(
        ROOT / "scripts/baseline_qualification.py",
        "baseline_qualification_residual13_mutations",
    )


@pytest.fixture()
def residual13_bundle(tmp_path: Path, qualification_module):
    """Copy the minimal frozen evidence bundle and expose its exact 13 rows."""

    for relative in (
        POLICY_REL,
        BASELINE_REL,
        DISPOSITIONS_REL,
        POLICY_SCHEMA_REL,
    ):
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)

    policy = qualification_module.load_policy(tmp_path / POLICY_REL)
    baseline = json.loads((tmp_path / BASELINE_REL).read_text(encoding="utf-8"))
    dispositions = yaml.safe_load(
        (tmp_path / DISPOSITIONS_REL).read_text(encoding="utf-8")
    )["dispositions"]
    fingerprints = policy["approved_set"]["fingerprints"]
    active_by_fingerprint = {
        record["fingerprint"]: record for record in baseline["active"]
    }
    exact_active = [
        deepcopy(active_by_fingerprint[fingerprint])
        for fingerprint in fingerprints
    ]

    assert len(exact_active) == len(set(fingerprints)) == 13
    return {
        "active": exact_active,
        "dispositions": dispositions,
        "fingerprints": fingerprints,
        "policy": policy,
        "schema": json.loads(
            (tmp_path / POLICY_SCHEMA_REL).read_text(encoding="utf-8")
        ),
    }


def _fail_on_new(
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    baseline_active: list[dict[str, object]],
    current_active: list[dict[str, object]],
) -> dict[str, object]:
    monkeypatch.setattr(
        inventory_module,
        "_load_validated_baseline",
        lambda _root: {
            "active": deepcopy(baseline_active),
            "provisional": False,
            "resolved": [],
        },
    )
    monkeypatch.setattr(inventory_module, "build_inventory", lambda _root: {})
    monkeypatch.setattr(
        inventory_module,
        "_current_active_debt",
        lambda _inventory: deepcopy(current_active),
    )
    monkeypatch.setattr(
        inventory_module,
        "_load_anomaly_identity_migrations",
        lambda _root: {},
    )
    return inventory_module._fail_on_new_gate(tmp_path)


def test_residual13_mutation_a_exact_13_fail_on_new_passes(
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    residual13_bundle,
    tmp_path: Path,
) -> None:
    active = residual13_bundle["active"]

    gate = _fail_on_new(
        inventory_module,
        monkeypatch,
        tmp_path,
        baseline_active=active,
        current_active=active,
    )

    assert gate["success"] is True
    assert gate["exit_code"] == 0
    assert gate["reasons"] == []
    assert gate["comparison"]["unchanged"] == sorted(
        residual13_bundle["fingerprints"]
    )


def test_residual13_mutation_b_fourteenth_fingerprint_fails(
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    residual13_bundle,
    tmp_path: Path,
) -> None:
    active = residual13_bundle["active"]
    extra = deepcopy(active[0])
    extra.update(
        {
            "fingerprint": "f" * 16,
            "locator_key": json.dumps(
                {
                    "category": "blocking_statuses",
                    "chapter": "1SPE-TEST",
                    "field": "",
                    "manual": "1SPE",
                    "source": "mutation/fourteenth.tex",
                    "target_or_id": "RESIDUAL-14",
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
        }
    )

    gate = _fail_on_new(
        inventory_module,
        monkeypatch,
        tmp_path,
        baseline_active=active,
        current_active=[*active, extra],
    )

    assert gate["success"] is False
    assert gate["exit_code"] == inventory_module.GATE_BASELINE_CODE
    assert gate["reasons"] == [f"anomalie nouvelle fp={'f' * 16}"]


def test_residual13_mutation_c_removed_deterministic_qualification_fails(
    qualification_module,
    residual13_bundle,
) -> None:
    dispositions = deepcopy(residual13_bundle["dispositions"])
    removed = residual13_bundle["fingerprints"][0]
    del dispositions[removed]

    failures = qualification_module.validate_materialized_registry(
        residual13_bundle["policy"],
        dispositions,
    )

    assert "materialized fingerprint count mismatch:12!=13" in failures
    assert "materialized fingerprint digest mismatch" in failures


def test_residual13_mutation_d_source_change_creates_new_fingerprint_debt(
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    residual13_bundle,
    tmp_path: Path,
) -> None:
    baseline_active = residual13_bundle["active"]
    current_active = deepcopy(baseline_active)
    previous = current_active[0]
    identity = json.loads(previous["locator_key"])
    identity["source"] = f"{identity['source']}.mutated"
    anomaly = {
        "chapter": identity["chapter"],
        "id": identity["target_or_id"],
        "manual": identity["manual"],
        "source": identity["source"],
        "status": "generated",
    }
    current_fingerprint = inventory_module._anomaly_fingerprint(
        anomaly,
        category=str(previous["category"]),
    )
    previous_fingerprint = str(previous["fingerprint"])
    previous["fingerprint"] = current_fingerprint
    previous["locator_key"] = inventory_module._anomaly_locator_key(
        anomaly,
        category=str(previous["category"]),
    )

    gate = _fail_on_new(
        inventory_module,
        monkeypatch,
        tmp_path,
        baseline_active=baseline_active,
        current_active=current_active,
    )

    assert current_fingerprint != previous_fingerprint
    assert gate["success"] is False
    assert gate["comparison"]["new"] == [current_fingerprint]
    assert previous_fingerprint in gate["comparison"]["resolved"]
    assert f"anomalie nouvelle fp={current_fingerprint}" in gate["reasons"]


def test_residual13_mutation_e_release_acceptance_true_fails_schema(
    residual13_bundle,
) -> None:
    policy = deepcopy(residual13_bundle["policy"])
    policy["decision"]["release_acceptance"] = True

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(
            residual13_bundle["schema"]
        ).validate(policy)


def test_residual13_mutation_f_approved_without_decision_receipt_fails(
    qualification_module,
    residual13_bundle,
) -> None:
    dispositions = deepcopy(residual13_bundle["dispositions"])
    fingerprint = residual13_bundle["fingerprints"][0]
    record = dispositions[fingerprint]
    assert record["approved_by"]
    record.pop("decision_ref")
    record["qualification_digest"] = qualification_module.qualification_digest(
        record
    )

    failures = qualification_module.validate_materialized_registry(
        residual13_bundle["policy"],
        dispositions,
    )

    assert f"managed decision mismatch:{fingerprint}:decision_ref" in failures


def test_residual13_mutation_g_forbidden_structural_anomaly_fails(
    qualification_module,
    residual13_bundle,
) -> None:
    dispositions = deepcopy(residual13_bundle["dispositions"])
    fingerprint = residual13_bundle["fingerprints"][0]
    record = dispositions[fingerprint]
    record["category"] = "unassembled_objects"
    record["qualification_digest"] = qualification_module.qualification_digest(
        record
    )

    failures = qualification_module.validate_materialized_registry(
        residual13_bundle["policy"],
        dispositions,
    )

    assert "materialized category counts mismatch" in failures


def test_residual13_mutation_h_wildcard_fails_schema(
    residual13_bundle,
) -> None:
    policy = deepcopy(residual13_bundle["policy"])
    policy["approved_set"]["fingerprints"] = ["*"]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(
            residual13_bundle["schema"]
        ).validate(policy)
