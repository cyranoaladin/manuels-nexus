from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
from collections import Counter
from copy import deepcopy
from pathlib import Path

import jsonschema
import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "baseline_qualification.py"
INVENTORY_PATH = ROOT / "scripts" / "inventory_collection.py"
POLICY_PATH = ROOT / "audit" / "BASELINE_QUALIFICATION_POLICY.yaml"


def _load_module(path: Path, name: str):
    assert path.is_file(), f"{path.relative_to(ROOT)} doit être créé"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def qualification_module():
    return _load_module(MODULE_PATH, "baseline_qualification")


@pytest.fixture()
def inventory_module():
    return _load_module(INVENTORY_PATH, "inventory_collection_for_policy")


@pytest.fixture()
def policy(qualification_module):
    return qualification_module.load_policy(POLICY_PATH)


def _digest_fingerprints(fingerprints: list[str]) -> str:
    payload = json.dumps(
        sorted(fingerprints),
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def test_qualification_policy_schema_and_approved_contract(
    qualification_module,
    policy,
) -> None:
    schema_path = (
        ROOT
        / "audit"
        / "schemas"
        / "v1"
        / "baseline-qualification-policy.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    payload = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["control_digest"] == qualification_module.control_digest(payload)
    assert payload["decision"] == {
        "approved_by": "Alaeddine Ben Rhouma",
        "approver_role": "Direction scientifique et éditoriale Nexus Réussite",
        "baseline_purpose": "debt_regression_control",
        "id": "baseline-debt-extension-origin-main-2026-08-02",
        "provisional_after_freeze": False,
        "ref": (
            "audit/BASELINE_QUALIFICATION_DECISION.md"
            "#decision-baseline-debt-extension-origin-main-2026-08-02"
        ),
        "release_acceptance": False,
    }
    assert payload["approved_set"] == {
        "baseline_sha": "fb90e5c7cabb16c29c61bf4bdc1d5abae3f0121a",
        "category_counts": {
            "blocking_statuses": 134,
            "unassembled_objects": 52,
        },
        "fingerprint_count": 186,
        "fingerprint_digest": (
            "sha256:"
            "ac046f9784e3a492dbcb83dca74292ff0b503a19b52d09ebef51e5e94a299fe8"
        ),
        "observed_model_digest_before_materialization": (
            "sha256:"
            "606142c55324affad412521536f294a913c4ba45d0d0e10e7fb785238cba58aa"
        ),
        "observed_source_digest_before_materialization": (
            "sha256:"
            "f2b46f25776ce98e2a52a422581532911045d861613ab652625a08b838d07545"
        ),
        "owner_counts": {
            "direction_editoriale_pedagogique": 25,
            "direction_scientifique_programme": 109,
            "ingenierie_build_qualite": 52,
        },
    }
    assert set(payload["owners"]) == {
        "direction_scientifique_programme",
        "direction_editoriale_pedagogique",
        "ingenierie_build_qualite",
    }
    assert payload["allowed_dispositions"] == [
        "open_debt",
        "generated_dependency",
        "harvest_candidate",
        "intentional_reuse",
        "false_positive",
        "accepted_exception",
        "fixed",
    ]
    assert payload["initial_policy"]["prohibited_outputs"] == [
        "accepted_exception",
        "false_positive",
        "fixed",
    ]
    rule_ids = [rule["id"] for rule in payload["rules"]]
    assert len(rule_ids) == len(set(rule_ids))
    assert [rule["order"] for rule in payload["rules"]] == list(
        range(1, len(rule_ids) + 1)
    )
    assert not {
        rule["decision"]["disposition"] for rule in payload["rules"]
    } & set(payload["initial_policy"]["prohibited_outputs"])


@pytest.mark.parametrize(
    ("category", "anomaly", "expected"),
    [
        (
            "blocking_statuses",
            {"scope": "contract", "status": "complete"},
            ("blocking-contract-not-approved", "open_debt", "ingenierie_build_qualite", True),
        ),
        (
            "blocking_statuses",
            {"scope": "object", "object_type": "cours", "status": "generated"},
            (
                "blocking-scientific-object",
                "open_debt",
                "direction_scientifique_programme",
                True,
            ),
        ),
        (
            "blocking_statuses",
            {"scope": "object", "object_type": "qcm", "status": "needs_review"},
            (
                "blocking-scientific-object",
                "open_debt",
                "direction_scientifique_programme",
                True,
            ),
        ),
        (
            "blocking_statuses",
            {"scope": "object", "object_type": "remediation", "status": "draft"},
            (
                "blocking-pedagogical-object",
                "open_debt",
                "direction_editoriale_pedagogique",
                True,
            ),
        ),
        (
            "unassembled_objects",
            {"source": "Mathematiques/manuel-maths/chapitres/C/cours/a.tex"},
            ("unassembled-object", "open_debt", "ingenierie_build_qualite", True),
        ),
        (
            "broken_meta_references",
            {"source": "a.tex"},
            ("broken-meta-reference", "open_debt", "ingenierie_build_qualite", True),
        ),
        (
            "chapters_not_in_manual",
            {"source": "chapitres/C/contrat.yaml"},
            (
                "missing-chapter-deliverable",
                "open_debt",
                "direction_editoriale_pedagogique",
                True,
            ),
        ),
        (
            "missing_assemblers",
            {"source": "scripts/assemble_manuel.py"},
            ("missing-assembler", "open_debt", "ingenierie_build_qualite", True),
        ),
        (
            "missing_corrections",
            {"source": "chapitres/C/exercices/e.tex"},
            (
                "missing-correction",
                "open_debt",
                "direction_scientifique_programme",
                True,
            ),
        ),
        (
            "harvest_candidate",
            {"source": "NSI/_harvest/P04/example.candidate.tex"},
            (
                "harvest-candidate",
                "harvest_candidate",
                "direction_editoriale_pedagogique",
                False,
            ),
        ),
        (
            "generated_dependency",
            {"producer_identified": True, "producer_tested": True},
            (
                "generated-dependency-proved",
                "generated_dependency",
                "ingenierie_build_qualite",
                False,
            ),
        ),
        (
            "generated_dependency",
            {"producer_identified": True, "producer_tested": False},
            (
                "generated-dependency-unproved",
                "open_debt",
                "ingenierie_build_qualite",
                True,
            ),
        ),
        (
            "duplicate_assembly_objects",
            {
                "editorial_decision": True,
                "no_pdf_duplicate": True,
                "variant_identified": True,
            },
            (
                "intentional-reuse-proved",
                "intentional_reuse",
                "direction_editoriale_pedagogique",
                False,
            ),
        ),
        (
            "duplicate_assembly_objects",
            {
                "editorial_decision": True,
                "no_pdf_duplicate": False,
                "variant_identified": True,
            },
            (
                "intentional-reuse-unproved",
                "open_debt",
                "direction_editoriale_pedagogique",
                True,
            ),
        ),
    ],
)
def test_classifier_routes_contractual_samples(
    qualification_module,
    policy,
    category: str,
    anomaly: dict[str, object],
    expected: tuple[str, str, str, bool],
) -> None:
    decision = qualification_module.classify_anomaly(policy, category, anomaly)

    assert decision is not None
    assert (
        decision["policy_rule"],
        decision["disposition"],
        decision["owner"],
        decision["release_blocking"],
    ) == expected


def test_classifier_leaves_unknown_or_ambiguous_anomaly_unqualified(
    qualification_module,
    policy,
) -> None:
    assert qualification_module.classify_anomaly(
        policy,
        "category_not_in_policy",
        {"source": "unknown"},
    ) is None
    ambiguous = deepcopy(policy)
    duplicate = deepcopy(ambiguous["rules"][0])
    duplicate["id"] = "duplicate-contract-rule"
    duplicate["order"] = len(ambiguous["rules"]) + 1
    ambiguous["rules"].append(duplicate)

    assert qualification_module.classify_anomaly(
        ambiguous,
        "blocking_statuses",
        {"scope": "contract", "status": "complete"},
    ) is None


def test_harvest_candidate_matches_directly_under_harvest(
    qualification_module,
    policy,
) -> None:
    decision = qualification_module.classify_anomaly(
        policy,
        "harvest_candidate",
        {"source": "NSI/_harvest/a.candidate.tex"},
    )

    assert decision is not None
    assert decision["disposition"] == "harvest_candidate"


def test_policy_schema_freezes_each_owner_scope_exactly(policy) -> None:
    schema = json.loads(
        (
            ROOT
            / "audit/schemas/v1/baseline-qualification-policy.schema.json"
        ).read_text(encoding="utf-8")
    )
    expected = {
        "direction_scientifique_programme": [
            "mathematics",
            "official_programme",
            "demonstrations",
            "qcm",
            "corrections",
            "numerical_results",
        ],
        "direction_editoriale_pedagogique": [
            "pedagogy",
            "nexus_mastery_loop",
            "student_teacher_variants",
            "remediation",
            "editorial_content",
            "terminology",
        ],
        "ingenierie_build_qualite": [
            "metadata",
            "inventory",
            "assemblies",
            "latex",
            "python",
            "ci",
            "pdf",
            "visual_baselines",
        ],
    }
    assert {
        owner: value["scope"] for owner, value in policy["owners"].items()
    } == expected
    for owner in expected:
        mutated = deepcopy(policy)
        mutated["owners"][owner]["scope"] = expected[owner][:-1]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(schema).validate(mutated)


def test_repository_approved_set_has_exact_category_and_owner_counts(
    qualification_module,
    inventory_module,
    policy,
) -> None:
    inventory = inventory_module.build_inventory(ROOT)
    records = inventory_module._baseline_qualification_records(inventory)
    dispositions = inventory_module._load_dispositions(ROOT)
    managed = {
        fingerprint
        for fingerprint, disposition in dispositions.items()
        if (
            disposition.get("qualification_policy_digest")
            == policy["control_digest"]
            and disposition.get("policy_rule") != "historical-evidence"
        )
    }
    approved_records = [
        record
        for record in records
        if not record["qualified"] or record["fingerprint"] in managed
    ]
    fingerprints = [record["fingerprint"] for record in approved_records]

    assert len(approved_records) == 186
    assert len(fingerprints) == len(set(fingerprints))
    assert _digest_fingerprints(fingerprints) == policy["approved_set"][
        "fingerprint_digest"
    ]
    assert Counter(record["category"] for record in approved_records) == Counter(
        policy["approved_set"]["category_counts"]
    )
    decisions = [
        qualification_module.classify_anomaly(
            policy,
            record["category"],
            record["anomaly"],
        )
        for record in approved_records
    ]
    assert all(decision is not None for decision in decisions)
    assert Counter(decision["owner"] for decision in decisions if decision) == Counter(
        policy["approved_set"]["owner_counts"]
    )


def _refresh_empty_build_manifest(
    repository: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
):
    with monkeypatch.context() as isolated:
        isolated.setattr(
            inventory_module,
            "_load_observed_build_manifest",
            lambda *_args, **_kwargs: [],
        )
        candidate = inventory_module.build_inventory(repository)
    manifest_path = repository / "audit/BUILD_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["builds"] == []
    manifest["source_digest"] = candidate["source_digest"]
    manifest["model_digest"] = inventory_module._model_digest(candidate)
    manifest["provenance"] = {
        "branch": subprocess.run(
            ["git", "-C", str(repository), "branch", "--show-current"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip(),
        "dirty": False,
        "head_sha": subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip(),
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "-C", str(repository), "add", "-A"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "-c",
            "user.name=Nexus Fixture",
            "-c",
            "user.email=nexus-fixture@example.invalid",
            "commit",
            "-qm",
            "refresh empty build manifest fixture",
        ],
        check=True,
    )
    return inventory_module.build_inventory(repository)


def test_materialization_plan_preserves_history_and_emits_all_required_fields(
    qualification_module,
    inventory_module,
    policy,
) -> None:
    inventory = inventory_module.build_inventory(ROOT)
    records = inventory_module._baseline_qualification_records(inventory)
    historical = inventory_module._load_dispositions(ROOT)
    plan = qualification_module.plan_materialization(
        policy,
        records,
        historical,
        observed_source_digest=inventory["source_digest"],
        observed_model_digest=inventory_module._model_digest(inventory),
    )

    assert plan["approved_fingerprint_count"] == 186
    assert plan["approved_fingerprint_digest"] == policy["approved_set"][
        "fingerprint_digest"
    ]
    assert plan["unqualified"] == []
    payload = plan["dispositions_payload"]
    assert len(payload["dispositions"]) == 2647
    required = {
        "approved_by",
        "baseline_sha",
        "category",
        "chapter",
        "decision_ref",
        "disposition",
        "fingerprint",
        "fingerprint_schema_version",
        "justification",
        "manual",
        "owner",
        "policy_rule",
        "qualification_digest",
        "reason",
        "release_blocking",
        "severity",
        "source",
    }
    assert all(
        required <= set(record)
        for record in payload["dispositions"].values()
    )
    assert Counter(
        record["owner"]
        for record in payload["dispositions"].values()
        if record.get("qualification_policy_digest") == policy["control_digest"]
    ) == Counter(policy["approved_set"]["owner_counts"])
    assert all(
        record["disposition"] == "open_debt"
        and record["release_blocking"] is True
        for record in payload["dispositions"].values()
        if record.get("qualification_policy_digest") == policy["control_digest"]
    )
    assert all(
        record["disposition"] not in {"accepted_exception", "false_positive", "fixed"}
        for record in payload["dispositions"].values()
        if record.get("qualification_policy_digest") == policy["control_digest"]
    )
    assert payload["control_digest"] == qualification_module.control_digest(payload)
    assert plan["unqualified_json"]["summary"]["unqualified"] == 0
    assert plan["unqualified_markdown"].endswith("\n")


def test_materialization_preserves_prior_policy_records_verbatim(
    qualification_module,
    policy,
) -> None:
    historical = {
        "approved_by": "Décision antérieure",
        "baseline_sha": "1" * 40,
        "blocking": True,
        "category": "blocking_statuses",
        "chapter": "1SPE-SUITES",
        "decision_ref": "audit/DECISION_ANTERIEURE.md#decision",
        "disposition": "open_debt",
        "fingerprint": "a" * 16,
        "fingerprint_schema_version": 1,
        "justification": "Dette ouverte par une décision antérieure.",
        "manual": "1SPE",
        "owner": "direction_scientifique_programme",
        "policy_rule": "blocking-scientific-object",
        "qualification_policy_digest": "sha256:" + "1" * 64,
        "reason": "Dette ouverte par une décision antérieure.",
        "release_blocking": True,
        "severity": "blocking",
        "source": "chapitres/1SPE-SUITES/cours/cours.tex",
    }
    historical["qualification_digest"] = (
        qualification_module.qualification_digest(historical)
    )
    active = {
        "category": historical["category"],
        "chapter": historical["chapter"],
        "fingerprint": historical["fingerprint"],
        "fingerprint_schema_version": 1,
        "manual": historical["manual"],
        "severity": historical["severity"],
        "source": historical["source"],
    }

    preserved = qualification_module._normalize_historical_record(
        policy=policy,
        record=active,
        historical=historical,
    )

    assert preserved == historical


def test_repository_registry_excludes_prior_policy_from_current_policy(
    qualification_module,
    inventory_module,
    policy,
) -> None:
    inventory = inventory_module.build_inventory(ROOT)
    records = inventory_module._baseline_qualification_records(inventory)
    dispositions = inventory_module._load_dispositions(ROOT)

    assert any(
        record.get("qualification_policy_digest")
        not in {None, policy["control_digest"]}
        and record.get("policy_rule") != "historical-evidence"
        for record in dispositions.values()
    )
    assert qualification_module.validate_materialized_registry(
        policy,
        dispositions,
        active_records=records,
    ) == []


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("owner", "direction_editoriale_pedagogique"),
        ("justification", "Justification modifiée."),
        ("reason", "Cause modifiée."),
        ("approved_by", "Autre approbateur"),
        ("decision_ref", "audit/DECISION.md#autre"),
        ("evidence", {"test": "tests/test_other.py"}),
        ("proof", {"source": "audit/preuve-autre.md"}),
        ("policy_rule", "autre-regle"),
        ("qualification_policy_digest", "sha256:" + "f" * 64),
    ],
)
def test_qualification_digest_covers_every_contractual_decision_field(
    qualification_module,
    field: str,
    replacement: object,
) -> None:
    record = {
        "approved_by": "Alaeddine Ben Rhouma",
        "decision_ref": "audit/BASELINE_QUALIFICATION_DECISION.md#decision",
        "evidence": {"test": "tests/test_baseline_qualification.py"},
        "justification": "Dette qualifiée.",
        "owner": "direction_scientifique_programme",
        "policy_rule": "blocking-scientific-object",
        "proof": {"source": "audit/preuve.md"},
        "qualification_policy_digest": "sha256:" + "a" * 64,
        "reason": "Contenu non approuvé.",
    }
    baseline = qualification_module.qualification_digest(record)
    mutated = deepcopy(record)
    mutated[field] = replacement

    assert qualification_module.qualification_digest(mutated) != baseline


@pytest.mark.parametrize(
    ("field", "replacement", "expected_fragment"),
    [
        ("owner", "proprietaire_inconnu", "owner"),
        ("disposition", "accepted_exception", "prohibited"),
        (
            "qualification_policy_digest",
            "sha256:" + "f" * 64,
            "policy digest",
        ),
        ("qualification_digest", "sha256:" + "e" * 64, "qualification_digest"),
    ],
)
def test_policy_gate_rejects_tampered_materialized_registry(
    qualification_module,
    policy,
    field: str,
    replacement: object,
    expected_fragment: str,
) -> None:
    fingerprint = "a" * 16
    record = {
        "approved_by": policy["decision"]["approved_by"],
        "baseline_sha": policy["approved_set"]["baseline_sha"],
        "blocking": True,
        "category": "blocking_statuses",
        "chapter": "1SPE-SUITES",
        "decision_ref": policy["decision"]["ref"],
        "disposition": "open_debt",
        "fingerprint": fingerprint,
        "fingerprint_schema_version": 1,
        "justification": "Dette qualifiée.",
        "manual": "1SPE",
        "owner": "direction_scientifique_programme",
        "policy_rule": "blocking-scientific-object",
        "qualification_policy_digest": policy["control_digest"],
        "reason": "Contenu non approuvé.",
        "release_blocking": True,
        "severity": "blocking",
        "source": "chapitres/1SPE-SUITES/cours/cours.tex",
    }
    record["qualification_digest"] = qualification_module.qualification_digest(
        record
    )
    synthetic_policy = deepcopy(policy)
    synthetic_policy["approved_set"] = {
        **synthetic_policy["approved_set"],
        "category_counts": {"blocking_statuses": 1},
        "fingerprint_count": 1,
        "fingerprint_digest": qualification_module.fingerprint_set_digest(
            [fingerprint]
        ),
        "owner_counts": {"direction_scientifique_programme": 1},
    }
    mutated = deepcopy(record)
    mutated[field] = replacement

    failures = qualification_module.validate_materialized_registry(
        synthetic_policy,
        {fingerprint: mutated},
    )

    assert any(expected_fragment in failure for failure in failures)


def _synthetic_policy_record(
    qualification_module,
    policy,
    *,
    fingerprint: str,
    owner: str,
    policy_rule: str,
    reason: str,
    category: str = "blocking_statuses",
    chapter: str | None = "1SPE-SUITES",
    manual: str | None = "1SPE",
    severity: str = "blocking",
    source: str | None = "chapitres/1SPE-SUITES/cours/cours.tex",
) -> dict[str, object]:
    record: dict[str, object] = {
        "approved_by": policy["decision"]["approved_by"],
        "baseline_sha": policy["approved_set"]["baseline_sha"],
        "blocking": True,
        "category": category,
        "chapter": chapter,
        "decision_ref": policy["decision"]["ref"],
        "disposition": "open_debt",
        "fingerprint": fingerprint,
        "fingerprint_schema_version": 1,
        "justification": reason,
        "manual": manual,
        "owner": owner,
        "policy_rule": policy_rule,
        "qualification_policy_digest": policy["control_digest"],
        "reason": reason,
        "release_blocking": True,
        "severity": severity,
        "source": source,
    }
    record["qualification_digest"] = qualification_module.qualification_digest(
        record
    )
    return record


def _synthetic_policy_contract(
    qualification_module,
    policy,
    records: list[dict[str, object]],
):
    mutated = deepcopy(policy)
    mutated["approved_set"] = {
        **mutated["approved_set"],
        "category_counts": dict(
            Counter(str(record["category"]) for record in records)
        ),
        "fingerprint_count": len(records),
        "fingerprint_digest": qualification_module.fingerprint_set_digest(
            [str(record["fingerprint"]) for record in records]
        ),
        "owner_counts": dict(
            Counter(str(record["owner"]) for record in records)
        ),
    }
    return mutated


def test_policy_gate_rejects_complete_removal_of_policy_entries(
    qualification_module,
    policy,
) -> None:
    failures = qualification_module.validate_materialized_registry(
        policy,
        {},
        active_records=[],
    )

    assert any("fingerprint count" in failure for failure in failures)
    assert any("fingerprint digest" in failure for failure in failures)


def test_policy_gate_rejects_owner_swap_even_with_constant_owner_counts(
    qualification_module,
    policy,
) -> None:
    first = _synthetic_policy_record(
        qualification_module,
        policy,
        fingerprint="a" * 16,
        owner="direction_scientifique_programme",
        policy_rule="blocking-scientific-object",
        reason=(
            "Contenu disciplinaire ou corrigé sans statut de publication "
            "approuvé."
        ),
    )
    second = _synthetic_policy_record(
        qualification_module,
        policy,
        fingerprint="b" * 16,
        owner="direction_editoriale_pedagogique",
        policy_rule="blocking-pedagogical-object",
        reason=(
            "Objet pédagogique, de remédiation ou de variante non approuvé."
        ),
        source="chapitres/1SPE-SUITES/remediation/remediation.tex",
    )
    synthetic_policy = _synthetic_policy_contract(
        qualification_module,
        policy,
        [first, second],
    )
    active_records = [
        {
            "anomaly": {
                "object_type": "cours",
                "scope": "object",
                "status": "generated",
            },
            "category": "blocking_statuses",
            **{
                field: first[field]
                for field in (
                    "chapter",
                    "fingerprint",
                    "fingerprint_schema_version",
                    "manual",
                    "severity",
                    "source",
                )
            },
        },
        {
            "anomaly": {
                "object_type": "remediation",
                "scope": "object",
                "status": "draft",
            },
            "category": "blocking_statuses",
            **{
                field: second[field]
                for field in (
                    "chapter",
                    "fingerprint",
                    "fingerprint_schema_version",
                    "manual",
                    "severity",
                    "source",
                )
            },
        },
    ]
    swapped = deepcopy({str(first["fingerprint"]): first, str(second["fingerprint"]): second})
    swapped[str(first["fingerprint"])]["owner"] = second["owner"]
    swapped[str(second["fingerprint"])]["owner"] = first["owner"]
    for record in swapped.values():
        record["qualification_digest"] = qualification_module.qualification_digest(
            record
        )

    failures = qualification_module.validate_materialized_registry(
        synthetic_policy,
        swapped,
        active_records=active_records,
    )

    assert any("active decision mismatch" in failure for failure in failures)


def test_policy_gate_rejects_tampered_disappeared_entry_at_constant_counts(
    qualification_module,
    policy,
) -> None:
    first = _synthetic_policy_record(
        qualification_module,
        policy,
        fingerprint="a" * 16,
        owner="direction_scientifique_programme",
        policy_rule="blocking-scientific-object",
        reason=(
            "Contenu disciplinaire ou corrigé sans statut de publication "
            "approuvé."
        ),
    )
    second = _synthetic_policy_record(
        qualification_module,
        policy,
        fingerprint="b" * 16,
        owner="direction_editoriale_pedagogique",
        policy_rule="blocking-pedagogical-object",
        reason=(
            "Objet pédagogique, de remédiation ou de variante non approuvé."
        ),
        source="chapitres/1SPE-SUITES/remediation/remediation.tex",
    )
    synthetic_policy = _synthetic_policy_contract(
        qualification_module,
        policy,
        [first, second],
    )
    intact = {
        str(first["fingerprint"]): first,
        str(second["fingerprint"]): second,
    }
    assert qualification_module.validate_materialized_registry(
        synthetic_policy,
        intact,
        active_records=[],
    ) == []

    tampered = deepcopy(intact)
    tampered[str(first["fingerprint"])]["owner"] = second["owner"]
    tampered[str(second["fingerprint"])]["owner"] = first["owner"]
    for record in tampered.values():
        record["qualification_digest"] = qualification_module.qualification_digest(
            record
        )

    failures = qualification_module.validate_materialized_registry(
        synthetic_policy,
        tampered,
        active_records=[],
    )

    assert any(
        "managed decision mismatch" in failure
        for failure in failures
    )


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("reason", "Cause falsifiée."),
        ("policy_rule", "missing-assembler"),
        ("category", "missing_assemblers"),
        ("severity", "warning"),
        ("manual", "1NSI"),
        ("chapter", "1NSI-P01"),
        ("source", "NSI/chapitres/1NSI-P01/cours.tex"),
    ],
)
def test_policy_gate_rejects_altered_decision_or_context(
    qualification_module,
    policy,
    field: str,
    replacement: object,
) -> None:
    record = _synthetic_policy_record(
        qualification_module,
        policy,
        fingerprint="a" * 16,
        owner="direction_scientifique_programme",
        policy_rule="blocking-scientific-object",
        reason=(
            "Contenu disciplinaire ou corrigé sans statut de publication "
            "approuvé."
        ),
    )
    synthetic_policy = _synthetic_policy_contract(
        qualification_module,
        policy,
        [record],
    )
    active = {
        "anomaly": {
            "object_type": "cours",
            "scope": "object",
            "status": "generated",
        },
        "category": "blocking_statuses",
        **{
            key: record[key]
            for key in (
                "chapter",
                "fingerprint",
                "fingerprint_schema_version",
                "manual",
                "severity",
                "source",
            )
        },
    }
    mutated = deepcopy(record)
    mutated[field] = replacement
    mutated["qualification_digest"] = qualification_module.qualification_digest(
        mutated
    )

    failures = qualification_module.validate_materialized_registry(
        synthetic_policy,
        {str(record["fingerprint"]): mutated},
        active_records=[active],
    )

    assert any("active decision mismatch" in failure for failure in failures)


def test_materialization_plan_is_idempotent_after_policy_entries_exist(
    qualification_module,
    inventory_module,
    policy,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    approved_sha = policy["approved_set"]["baseline_sha"]
    subprocess.run(
        [
            "git",
            "clone",
            "-q",
            "--no-hardlinks",
            str(ROOT),
            str(repository),
        ],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "switch",
            "--create",
            "baseline-materialization-fixture",
            approved_sha,
        ],
        check=True,
        capture_output=True,
    )
    assert subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() == approved_sha
    shutil.copyfile(
        ROOT / "audit/schemas/v1/anomaly-dispositions.schema.json",
        repository / "audit/schemas/v1/anomaly-dispositions.schema.json",
    )
    historical_control = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "show",
            f"{approved_sha}:audit/ANOMALY_DISPOSITIONS.yaml",
        ],
        check=True,
        capture_output=True,
    ).stdout
    (repository / "audit/ANOMALY_DISPOSITIONS.yaml").write_bytes(
        historical_control
    )
    pre_inventory = _refresh_empty_build_manifest(
        repository,
        inventory_module,
        monkeypatch,
    )
    pre_model_digest = inventory_module._model_digest(pre_inventory)
    assert pre_inventory["source_digest"] == policy["approved_set"][
        "observed_source_digest_before_materialization"
    ]
    assert pre_model_digest == policy["approved_set"][
        "observed_model_digest_before_materialization"
    ]
    first = qualification_module.plan_materialization(
        policy,
        inventory_module._baseline_qualification_records(pre_inventory),
        inventory_module._load_dispositions(repository),
        observed_source_digest=pre_inventory["source_digest"],
        observed_model_digest=pre_model_digest,
    )
    (repository / "audit/ANOMALY_DISPOSITIONS.yaml").write_text(
        yaml.safe_dump(
            first["dispositions_payload"],
            allow_unicode=True,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    post_inventory = _refresh_empty_build_manifest(
        repository,
        inventory_module,
        monkeypatch,
    )
    post_model_digest = inventory_module._model_digest(post_inventory)

    second = qualification_module.plan_materialization(
        policy,
        inventory_module._baseline_qualification_records(post_inventory),
        inventory_module._load_dispositions(repository),
        observed_source_digest=post_inventory["source_digest"],
        observed_model_digest=post_model_digest,
    )

    assert post_model_digest != pre_model_digest
    assert all(
        qualification["qualified"] is True
        for qualification in post_inventory["anomaly_qualifications"].values()
    )
    assert second["approved_fingerprint_count"] == 186
    assert second["approved_fingerprint_digest"] == first[
        "approved_fingerprint_digest"
    ]
    assert second["dispositions_payload"] == first["dispositions_payload"]
    assert second["unqualified"] == []


def test_materialization_plan_corrects_policy_entry_drift_after_materialization(
    qualification_module,
    inventory_module,
    policy,
) -> None:
    inventory = inventory_module.build_inventory(ROOT)
    records = inventory_module._baseline_qualification_records(inventory)
    first = qualification_module.plan_materialization(
        policy,
        records,
        inventory_module._load_dispositions(ROOT),
        observed_source_digest=inventory["source_digest"],
        observed_model_digest=inventory_module._model_digest(inventory),
    )
    materialized_records = deepcopy(records)
    for record in materialized_records:
        record["qualified"] = True
    drifted = deepcopy(first["dispositions_payload"]["dispositions"])
    fingerprint = next(
        fingerprint
        for fingerprint, record in drifted.items()
        if record.get("qualification_policy_digest") == policy["control_digest"]
    )
    drifted[fingerprint]["owner"] = "ingenierie_build_qualite"

    repaired = qualification_module.plan_materialization(
        policy,
        materialized_records,
        drifted,
        observed_source_digest=inventory["source_digest"],
        observed_model_digest=inventory_module._model_digest(inventory),
    )

    assert repaired["dispositions_payload"]["dispositions"][fingerprint][
        "owner"
    ] != "ingenierie_build_qualite"


def test_materialization_refuses_approved_set_drift_without_partial_payload(
    qualification_module,
    inventory_module,
    policy,
) -> None:
    inventory = inventory_module.build_inventory(ROOT)
    records = inventory_module._baseline_qualification_records(inventory)
    historical = inventory_module._load_dispositions(ROOT)
    managed = {
        fingerprint
        for fingerprint, disposition in historical.items()
        if disposition.get("qualification_policy_digest")
        == policy["control_digest"]
    }
    changed = deepcopy(records)
    changed.pop(
        next(
            index
            for index, record in enumerate(changed)
            if not record["qualified"] or record["fingerprint"] in managed
        )
    )

    with pytest.raises(
        qualification_module.QualificationError,
        match="jeu approuvé",
    ):
        qualification_module.plan_materialization(
            policy,
            changed,
            historical,
            observed_source_digest=inventory["source_digest"],
            observed_model_digest=inventory_module._model_digest(inventory),
        )


def test_unqualified_reports_are_deterministic_for_an_unknown_anomaly(
    qualification_module,
    policy,
) -> None:
    changed = deepcopy(policy)
    records = [
        {
            "anomaly": {"source": "unknown.tex"},
            "category": "unknown",
            "chapter": None,
            "fingerprint": "a" * 16,
            "fingerprint_schema_version": 1,
            "manual": None,
            "qualified": False,
            "severity": "blocking",
            "source": "unknown.tex",
        }
    ]
    changed["approved_set"]["fingerprint_count"] = 1
    changed["approved_set"]["fingerprint_digest"] = _digest_fingerprints(
        ["a" * 16]
    )
    changed["approved_set"]["category_counts"] = {"unknown": 1}
    changed["approved_set"]["owner_counts"] = {}
    changed["approved_set"]["observed_source_digest_before_materialization"] = (
        "sha256:" + "1" * 64
    )
    changed["approved_set"]["observed_model_digest_before_materialization"] = (
        "sha256:" + "2" * 64
    )

    first = qualification_module.plan_materialization(
        changed,
        records,
        {},
        observed_source_digest="sha256:" + "1" * 64,
        observed_model_digest="sha256:" + "2" * 64,
        allow_unqualified=True,
    )
    second = qualification_module.plan_materialization(
        changed,
        records,
        {},
        observed_source_digest="sha256:" + "1" * 64,
        observed_model_digest="sha256:" + "2" * 64,
        allow_unqualified=True,
    )

    assert first["unqualified"] == second["unqualified"]
    assert first["unqualified_json"] == second["unqualified_json"]
    assert first["unqualified_markdown"] == second["unqualified_markdown"]
    assert first["unqualified"][0]["reason"] == "no_policy_rule"
