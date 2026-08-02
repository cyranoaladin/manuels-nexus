#!/usr/bin/env python3
"""Pure policy evaluation for the Phase 0 anomaly-debt qualification.

This module deliberately does not import :mod:`inventory_collection`.  It
classifies an already-built anomaly view and plans deterministic output
payloads.  Repository locking, confinement and writes stay in the inventory
orchestrator.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml


FINGERPRINT_SCHEMA_VERSION = 1
SCHEMA_VERSION = 1
POLICY_ARTIFACT_TYPE = "baseline_qualification_policy"
DISPOSITIONS_SCHEMA_REF = "audit/schemas/v1/anomaly-dispositions.schema.json"
UNQUALIFIED_SCHEMA_REF = "audit/schemas/v1/unqualified-anomalies.schema.json"

APPROVED_OWNERS = frozenset(
    {
        "direction_editoriale_pedagogique",
        "direction_scientifique_programme",
        "ingenierie_build_qualite",
    }
)
ALLOWED_DISPOSITIONS = (
    "open_debt",
    "generated_dependency",
    "harvest_candidate",
    "intentional_reuse",
    "false_positive",
    "accepted_exception",
    "fixed",
)
DISPOSITION_BLOCKS = {
    "accepted_exception": False,
    "false_positive": False,
    "fixed": False,
    "generated_dependency": False,
    "harvest_candidate": False,
    "intentional_reuse": False,
    "open_debt": True,
}
QUALIFICATION_DIGEST_FIELDS = (
    "approved_by",
    "decision_ref",
    "evidence",
    "justification",
    "owner",
    "policy_rule",
    "proof",
    "qualification_policy_digest",
    "reason",
)


class QualificationError(RuntimeError):
    """The approved policy contract or the proposed materialization is invalid."""


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """YAML loader rejecting duplicate keys in policy controls."""


def _construct_unique_mapping(
    loader: _UniqueKeySafeLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise yaml.constructor.ConstructorError(
                "baseline qualification policy",
                node.start_mark,
                f"duplicate YAML key: {key}",
                key_node.start_mark,
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _canonical(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _canonical(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return str(value)


def control_digest(payload: Mapping[str, Any]) -> str:
    """Return the canonical digest of a control payload."""

    canonical = {
        str(key): value
        for key, value in payload.items()
        if str(key) != "control_digest"
    }
    serialized = json.dumps(
        _canonical(canonical),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(serialized).hexdigest()}"


def fingerprint_set_digest(fingerprints: Sequence[str]) -> str:
    serialized = json.dumps(
        sorted(fingerprints),
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(serialized).hexdigest()}"


def qualification_digest(record: Mapping[str, Any]) -> str:
    """Fingerprint every field that gives a qualification its meaning."""

    payload = {
        field: _canonical(record.get(field))
        for field in QUALIFICATION_DIGEST_FIELDS
    }
    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(serialized).hexdigest()}"


def validate_materialized_registry(
    policy: Mapping[str, Any],
    dispositions: Mapping[str, Mapping[str, Any]],
    *,
    active_records: Sequence[Mapping[str, Any]] = (),
) -> list[str]:
    """Validate the frozen policy-produced subset independently of raw debt.

    This intentionally does not compare against the live anomaly set: after a
    freeze, a disappeared anomaly is an improvement and its registry record is
    retained as audit history.
    """

    policy_digest = str(policy.get("control_digest", ""))
    approved = policy.get("approved_set")
    initial = policy.get("initial_policy")
    if not isinstance(approved, Mapping) or not isinstance(initial, Mapping):
        return ["policy contract missing approved_set or initial_policy"]
    prohibited = set(initial.get("prohibited_outputs", []))
    managed = {
        str(fingerprint): record
        for fingerprint, record in dispositions.items()
        if (
            isinstance(record, Mapping)
            and record.get("policy_rule") != "historical-evidence"
            and (
                "qualification_policy_digest" in record
                or record.get("policy_rule")
            )
        )
    }
    failures: list[str] = []
    category_counts: Counter[str] = Counter()
    owner_counts: Counter[str] = Counter()
    rules_by_id = {
        str(rule.get("id")): rule
        for rule in policy.get("rules", [])
        if isinstance(rule, Mapping) and rule.get("id")
    }
    for fingerprint, record in sorted(dispositions.items()):
        owner = str(record.get("owner", ""))
        if owner not in APPROVED_OWNERS:
            failures.append(f"unknown owner:{fingerprint}:{owner}")
    for fingerprint, record in sorted(managed.items()):
        if record.get("fingerprint") != fingerprint:
            failures.append(f"fingerprint key mismatch:{fingerprint}")
        if record.get("qualification_policy_digest") != policy_digest:
            failures.append(f"policy digest mismatch:{fingerprint}")
        owner = str(record.get("owner", ""))
        if owner in APPROVED_OWNERS:
            owner_counts[owner] += 1
        disposition = str(record.get("disposition", ""))
        if disposition not in ALLOWED_DISPOSITIONS:
            failures.append(
                f"unknown disposition:{fingerprint}:{disposition}"
            )
        elif disposition in prohibited:
            failures.append(
                f"prohibited initial disposition:{fingerprint}:{disposition}"
            )
        elif record.get("release_blocking") is not DISPOSITION_BLOCKS[
            disposition
        ]:
            failures.append(
                f"release_blocking mismatch:{fingerprint}:{disposition}"
            )
        expected_digest = qualification_digest(record)
        if record.get("qualification_digest") != expected_digest:
            failures.append(f"qualification_digest mismatch:{fingerprint}")
        policy_rule = str(record.get("policy_rule", ""))
        rule = rules_by_id.get(policy_rule)
        decision = rule.get("decision") if isinstance(rule, Mapping) else None
        if not isinstance(decision, Mapping):
            failures.append(
                f"managed policy_rule unresolved:{fingerprint}:{policy_rule}"
            )
        else:
            expected_decision_fields = {
                "approved_by": policy.get("decision", {}).get("approved_by"),
                "baseline_sha": approved.get("baseline_sha"),
                "decision_ref": policy.get("decision", {}).get("ref"),
                "disposition": decision.get("disposition"),
                "justification": decision.get("reason"),
                "owner": decision.get("owner"),
                "policy_rule": policy_rule,
                "qualification_policy_digest": policy_digest,
                "reason": decision.get("reason"),
                "release_blocking": decision.get("release_blocking"),
            }
            for field, expected_value in expected_decision_fields.items():
                if _canonical(record.get(field)) != _canonical(
                    expected_value
                ):
                    failures.append(
                        f"managed decision mismatch:{fingerprint}:{field}"
                    )
        category_counts[str(record.get("category", ""))] += 1

    fingerprints = sorted(managed)
    if len(fingerprints) != approved.get("fingerprint_count"):
        failures.append(
            "materialized fingerprint count mismatch:"
            f"{len(fingerprints)}!={approved.get('fingerprint_count')}"
        )
    if fingerprint_set_digest(fingerprints) != approved.get(
        "fingerprint_digest"
    ):
        failures.append("materialized fingerprint digest mismatch")
    if dict(sorted(category_counts.items())) != dict(
        sorted(approved.get("category_counts", {}).items())
    ):
        failures.append("materialized category counts mismatch")
    if dict(sorted(owner_counts.items())) != dict(
        sorted(approved.get("owner_counts", {}).items())
    ):
        failures.append("materialized owner counts mismatch")

    exact_fields = (
        "approved_by",
        "baseline_sha",
        "blocking",
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
        "qualification_policy_digest",
        "reason",
        "release_blocking",
        "severity",
        "source",
    )
    for active in active_records:
        fingerprint = str(active.get("fingerprint", ""))
        actual = dispositions.get(fingerprint)
        if not isinstance(actual, Mapping):
            failures.append(f"active disposition missing:{fingerprint}")
            continue
        if actual.get("policy_rule") == "historical-evidence":
            continue
        category = str(active.get("category", ""))
        anomaly = active.get("anomaly")
        if not isinstance(anomaly, Mapping):
            failures.append(f"active anomaly context missing:{fingerprint}")
            continue
        decision = classify_anomaly(policy, category, anomaly)
        if decision is None:
            failures.append(f"active policy decision not unique:{fingerprint}")
            continue
        expected = _materialized_record(
            policy=policy,
            record=active,
            decision=decision,
        )
        for field in exact_fields:
            if _canonical(actual.get(field)) != _canonical(
                expected.get(field)
            ):
                failures.append(
                    f"active decision mismatch:{fingerprint}:{field}"
                )
    return sorted(set(failures))


def load_policy(path: Path) -> dict[str, Any]:
    """Load and validate policy invariants independent of repository state."""

    try:
        payload = yaml.load(
            path.read_text(encoding="utf-8"),
            Loader=_UniqueKeySafeLoader,
        )
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise QualificationError(f"invalid qualification policy: {exc}") from exc
    if not isinstance(payload, Mapping):
        raise QualificationError("qualification policy must be a mapping")
    policy = _canonical(payload)
    if policy.get("artifact_type") != POLICY_ARTIFACT_TYPE:
        raise QualificationError("qualification policy artifact_type mismatch")
    if policy.get("control_digest") != control_digest(policy):
        raise QualificationError("qualification policy control_digest mismatch")
    allowed = policy.get("allowed_dispositions")
    if allowed != list(ALLOWED_DISPOSITIONS):
        raise QualificationError("qualification policy dispositions mismatch")
    owners = policy.get("owners")
    if not isinstance(owners, Mapping) or set(owners) != APPROVED_OWNERS:
        raise QualificationError("qualification policy owners mismatch")
    rules = policy.get("rules")
    if not isinstance(rules, list) or not rules:
        raise QualificationError("qualification policy rules missing")
    ids = [rule.get("id") for rule in rules if isinstance(rule, Mapping)]
    orders = [rule.get("order") for rule in rules if isinstance(rule, Mapping)]
    if (
        len(ids) != len(rules)
        or len(set(ids)) != len(ids)
        or orders != list(range(1, len(rules) + 1))
    ):
        raise QualificationError("qualification policy rules are not uniquely ordered")
    initial = policy.get("initial_policy")
    prohibited = (
        set(initial.get("prohibited_outputs", []))
        if isinstance(initial, Mapping)
        else set()
    )
    outputs = {
        rule.get("decision", {}).get("disposition")
        for rule in rules
        if isinstance(rule, Mapping)
        and isinstance(rule.get("decision"), Mapping)
    }
    if outputs & prohibited:
        raise QualificationError("qualification policy produces a prohibited output")
    return policy


def _rule_matches(
    rule: Mapping[str, Any],
    category: str,
    anomaly: Mapping[str, Any],
) -> bool:
    match = rule.get("match")
    if not isinstance(match, Mapping):
        return False
    categories = match.get("categories")
    if not isinstance(categories, list) or category not in categories:
        return False
    field_equals = match.get("field_equals", {})
    if not isinstance(field_equals, Mapping) or any(
        anomaly.get(str(field)) != expected
        for field, expected in field_equals.items()
    ):
        return False
    field_in = match.get("field_in", {})
    if not isinstance(field_in, Mapping) or any(
        not isinstance(allowed, list) or anomaly.get(str(field)) not in allowed
        for field, allowed in field_in.items()
    ):
        return False
    source_glob = match.get("source_glob")
    if source_glob is not None:
        source = anomaly.get("source", anomaly.get("path"))
        patterns = (
            [source_glob, source_glob.replace("/**/", "/")]
            if isinstance(source_glob, str)
            else []
        )
        if (
            not isinstance(source_glob, str)
            or not isinstance(source, str)
            or not any(
                fnmatch.fnmatchcase(source.replace("\\", "/"), pattern)
                for pattern in patterns
            )
        ):
            return False
    all_true = match.get("all_true")
    if all_true is not None and (
        not isinstance(all_true, list)
        or not all(anomaly.get(str(field)) is True for field in all_true)
    ):
        return False
    not_all_true = match.get("not_all_true")
    if not_all_true is not None and (
        not isinstance(not_all_true, list)
        or all(anomaly.get(str(field)) is True for field in not_all_true)
    ):
        return False
    return True


def _matching_rules(
    policy: Mapping[str, Any],
    category: str,
    anomaly: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    rules = policy.get("rules")
    if not isinstance(rules, list):
        return []
    return [
        rule
        for rule in rules
        if isinstance(rule, Mapping) and _rule_matches(rule, category, anomaly)
    ]


def classify_anomaly(
    policy: Mapping[str, Any],
    category: str,
    anomaly: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Classify only when exactly one explicit rule matches."""

    matches = _matching_rules(policy, category, anomaly)
    if len(matches) != 1:
        return None
    rule = matches[0]
    decision = rule.get("decision")
    if not isinstance(decision, Mapping):
        return None
    return {
        **_canonical(decision),
        "policy_rule": str(rule["id"]),
    }


def _unqualified_entry(
    record: Mapping[str, Any],
    reason: str,
) -> dict[str, Any]:
    return {
        "category": str(record["category"]),
        "chapter": record.get("chapter"),
        "fingerprint": str(record["fingerprint"]),
        "manual": record.get("manual"),
        "reason": reason,
        "source": record.get("source"),
    }


def _historical_owner(disposition: str) -> str:
    if disposition == "intentional_reuse":
        return "direction_editoriale_pedagogique"
    return "ingenierie_build_qualite"


def _materialized_record(
    *,
    policy: Mapping[str, Any],
    record: Mapping[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    policy_decision = policy["decision"]
    approved_set = policy["approved_set"]
    reason = str(decision["reason"])
    disposition = str(decision["disposition"])
    release_blocking = bool(decision["release_blocking"])
    if release_blocking != DISPOSITION_BLOCKS[disposition]:
        raise QualificationError(
            f"release_blocking mismatch for {record['fingerprint']}"
        )
    materialized = {
        "approved_by": str(policy_decision["approved_by"]),
        "baseline_sha": str(approved_set["baseline_sha"]),
        "blocking": release_blocking,
        "category": str(record["category"]),
        "chapter": record.get("chapter"),
        "decision_ref": str(policy_decision["ref"]),
        "disposition": disposition,
        "fingerprint": str(record["fingerprint"]),
        "fingerprint_schema_version": int(
            record.get("fingerprint_schema_version", FINGERPRINT_SCHEMA_VERSION)
        ),
        "justification": reason,
        "manual": record.get("manual"),
        "owner": str(decision["owner"]),
        "policy_rule": str(decision["policy_rule"]),
        "qualification_policy_digest": str(policy["control_digest"]),
        "reason": reason,
        "release_blocking": release_blocking,
        "severity": str(record["severity"]),
        "source": record.get("source"),
    }
    materialized["qualification_digest"] = qualification_digest(materialized)
    return materialized


def _normalize_historical_record(
    *,
    policy: Mapping[str, Any],
    record: Mapping[str, Any],
    historical: Mapping[str, Any],
) -> dict[str, Any]:
    disposition = str(historical.get("disposition", ""))
    if disposition not in ALLOWED_DISPOSITIONS:
        raise QualificationError(
            f"historical disposition invalid for {record['fingerprint']}"
        )
    if disposition in {"generated_dependency", "intentional_reuse"} and not (
        historical.get("proof") or historical.get("evidence")
    ):
        raise QualificationError(
            f"historical proof missing for {record['fingerprint']}"
        )
    normalized = _canonical(historical)
    normalized.update(
        {
            "baseline_sha": str(policy["approved_set"]["baseline_sha"]),
            "blocking": DISPOSITION_BLOCKS[disposition],
            "category": str(record["category"]),
            "chapter": record.get("chapter"),
            "fingerprint_schema_version": int(
                record.get(
                    "fingerprint_schema_version",
                    FINGERPRINT_SCHEMA_VERSION,
                )
            ),
            "manual": record.get("manual"),
            "owner": _historical_owner(disposition),
            "policy_rule": "historical-evidence",
            "reason": str(historical["justification"]),
            "release_blocking": DISPOSITION_BLOCKS[disposition],
            "severity": str(record["severity"]),
            "source": record.get("source"),
        }
    )
    normalized["qualification_digest"] = qualification_digest(normalized)
    return normalized


def _unqualified_payload(
    policy: Mapping[str, Any],
    values: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "anomalies": [_canonical(value) for value in values],
        "artifact_type": "unqualified_anomalies",
        "fingerprint_schema_version": FINGERPRINT_SCHEMA_VERSION,
        "generated_by": "baseline_qualification.py",
        "policy_digest": str(policy["control_digest"]),
        "schema_ref": UNQUALIFIED_SCHEMA_REF,
        "schema_version": SCHEMA_VERSION,
        "summary": {"unqualified": len(values)},
    }


def render_unqualified_markdown(
    values: Sequence[Mapping[str, Any]],
    *,
    policy_digest: str,
) -> str:
    lines = [
        "# Anomalies non qualifiées",
        "",
        f"- Politique : `{policy_digest}`",
        f"- Nombre : **{len(values)}**",
        "",
    ]
    if values:
        lines.extend(
            [
                "| Fingerprint | Catégorie | Manuel | Chapitre | Source | Cause |",
                "|---|---|---|---|---|---|",
            ]
        )
        for value in values:
            cells = [
                str(value.get("fingerprint", "")),
                str(value.get("category", "")),
                str(value.get("manual") or "—"),
                str(value.get("chapter") or "—"),
                str(value.get("source") or "—"),
                str(value.get("reason", "")),
            ]
            lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |")
    else:
        lines.append("Aucune anomalie active non qualifiée.")
    return "\n".join(lines) + "\n"


def plan_materialization(
    policy: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
    historical_dispositions: Mapping[str, Mapping[str, Any]],
    *,
    observed_source_digest: str,
    observed_model_digest: str,
    allow_unqualified: bool = False,
) -> dict[str, Any]:
    """Plan the one-shot approved materialization without writing files."""

    approved = policy.get("approved_set")
    if not isinstance(approved, Mapping):
        raise QualificationError("approved_set missing from policy")
    by_fingerprint: dict[str, Mapping[str, Any]] = {}
    for record in records:
        fingerprint = str(record.get("fingerprint", ""))
        if not fingerprint or fingerprint in by_fingerprint:
            raise QualificationError(
                f"jeu approuvé: fingerprint dupliqué ou vide: {fingerprint}"
            )
        by_fingerprint[fingerprint] = record

    policy_digest = str(policy.get("control_digest", ""))
    policy_generated_fingerprints = {
        str(fingerprint)
        for fingerprint, disposition in historical_dispositions.items()
        if (
            disposition.get("qualification_policy_digest") == policy_digest
            and disposition.get("policy_rule") != "historical-evidence"
        )
    }
    if not policy_generated_fingerprints and (
        observed_source_digest
        != approved.get("observed_source_digest_before_materialization")
        or observed_model_digest
        != approved.get("observed_model_digest_before_materialization")
    ):
        raise QualificationError(
            "jeu approuvé pré-matérialisation: source/model digest drift"
        )
    unknown_policy_fingerprints = (
        policy_generated_fingerprints - set(by_fingerprint)
    )
    if unknown_policy_fingerprints:
        raise QualificationError(
            "jeu approuvé: policy disposition without active raw anomaly"
        )
    approved_records = [
        record
        for record in records
        if record.get("qualified") is not True
        or str(record["fingerprint"]) in policy_generated_fingerprints
    ]
    fingerprints = [str(record["fingerprint"]) for record in approved_records]
    approved_count = len(fingerprints)
    approved_digest = fingerprint_set_digest(fingerprints)
    category_counts = Counter(
        str(record["category"]) for record in approved_records
    )
    if (
        approved_count != approved.get("fingerprint_count")
        or approved_digest != approved.get("fingerprint_digest")
        or dict(sorted(category_counts.items()))
        != dict(sorted(approved.get("category_counts", {}).items()))
    ):
        raise QualificationError(
            "jeu approuvé: count, fingerprint digest or category counts drift"
        )

    qualified_fingerprints = {
        str(record["fingerprint"])
        for record in records
        if record.get("qualified") is True
    }
    registered_fingerprints = set(historical_dispositions)
    historical_fingerprints = (
        registered_fingerprints - policy_generated_fingerprints
    )
    if qualified_fingerprints != registered_fingerprints:
        raise QualificationError(
            "jeu approuvé: historical disposition set does not match active records"
        )

    entries: dict[str, dict[str, Any]] = {}
    unqualified: list[dict[str, Any]] = []
    generated_decisions: list[dict[str, Any]] = []
    for record in sorted(
        approved_records,
        key=lambda value: str(value["fingerprint"]),
    ):
        matches = _matching_rules(
            policy,
            str(record["category"]),
            record["anomaly"],
        )
        if len(matches) != 1:
            unqualified.append(
                _unqualified_entry(
                    record,
                    "no_policy_rule"
                    if not matches
                    else "ambiguous_policy_rules",
                )
            )
            continue
        decision = classify_anomaly(
            policy,
            str(record["category"]),
            record["anomaly"],
        )
        if decision is None:
            raise QualificationError("internal classification inconsistency")
        if decision["owner"] not in APPROVED_OWNERS:
            raise QualificationError(
                f"unknown owner for {record['fingerprint']}: {decision['owner']}"
            )
        if decision["disposition"] in set(
            policy["initial_policy"]["prohibited_outputs"]
        ):
            raise QualificationError(
                f"prohibited initial disposition for {record['fingerprint']}"
            )
        generated_decisions.append(decision)
        entries[str(record["fingerprint"])] = _materialized_record(
            policy=policy,
            record=record,
            decision=decision,
        )

    owner_counts = Counter(
        str(decision["owner"]) for decision in generated_decisions
    )
    if not unqualified and dict(sorted(owner_counts.items())) != dict(
        sorted(approved.get("owner_counts", {}).items())
    ):
        raise QualificationError("jeu approuvé: owner counts drift")
    if unqualified and not allow_unqualified:
        raise QualificationError(
            f"{len(unqualified)} anomalies remain unqualified"
        )

    for fingerprint in sorted(historical_fingerprints):
        entries[fingerprint] = _normalize_historical_record(
            policy=policy,
            record=by_fingerprint[fingerprint],
            historical=historical_dispositions[fingerprint],
        )

    dispositions_payload: dict[str, Any] = {
        "artifact_type": "anomaly_dispositions",
        "control_digest": "sha256:" + "0" * 64,
        "dispositions": dict(sorted(entries.items())),
        "fingerprint_schema_version": FINGERPRINT_SCHEMA_VERSION,
        "schema_ref": DISPOSITIONS_SCHEMA_REF,
        "schema_version": SCHEMA_VERSION,
    }
    dispositions_payload["control_digest"] = control_digest(dispositions_payload)
    unqualified.sort(
        key=lambda value: (str(value["fingerprint"]), str(value["category"]))
    )
    unqualified_json = _unqualified_payload(policy, unqualified)
    return {
        "approved_fingerprint_count": approved_count,
        "approved_fingerprint_digest": approved_digest,
        "dispositions_payload": dispositions_payload,
        "observed_model_digest": observed_model_digest,
        "observed_source_digest": observed_source_digest,
        "owner_counts": dict(sorted(owner_counts.items())),
        "unqualified": unqualified,
        "unqualified_json": unqualified_json,
        "unqualified_markdown": render_unqualified_markdown(
            unqualified,
            policy_digest=str(policy["control_digest"]),
        ),
    }
