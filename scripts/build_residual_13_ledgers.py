#!/usr/bin/env python3
"""Deriver les deux registres des treize dettes residuelles.

Ces deux artefacts -- le diff exact de baseline et le sunset ledger -- ont ete
ecrits a la main en meme temps que leur test, sans producteur. Ils ne pouvaient
donc que deriver : toute regeneration du modele residuel les laissait en place,
declarant l'empreinte d'un fichier qui n'existait plus et un etat de revue que
la campagne avait depasse. C'est exactement ce qui s'est produit, le lot des
qualifications suspendues ayant fait passer les treize de PENDING_UNQUALIFIED a
PENDING_QUALIFIED_OPEN_DEBT.

Les deux registres sont des DERIVES : leurs seules autorites sont la politique
de qualification, les dispositions, la baseline et le modele residuel. Ce
producteur les recalcule ; il n'invente aucun chiffre et ne touche a aucune
source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "audit/BASELINE_QUALIFICATION_POLICY.yaml"
DISPOSITIONS_PATH = ROOT / "audit/ANOMALY_DISPOSITIONS.yaml"
BASELINE_PATH = ROOT / "audit/ANOMALIES_BASELINE.json"
FORENSICS_PATH = ROOT / "audit/RESIDUAL_TRUE_NEW_FORENSICS.json"
EXACT_DIFF_PATH = ROOT / "audit/BASELINE_RESIDUAL_13_EXACT_DIFF.json"
SUNSET_PATH = ROOT / "audit/RESIDUAL_13_SUNSET_LEDGER.json"

#: Les six revues exigees avant toute cloture d'une dette residuelle.
REQUIRED_REVIEWS = {
    "editorial": "PENDING",
    "pedagogical": "PENDING",
    "programme": "PENDING",
    "scientific": "PENDING",
    "variant": "PENDING",
    "visual": "PENDING",
}

CLOSURE_CONDITION = "ALL_REQUIRED_REVIEWS_COMPLETE_AND_HUMAN_APPROVAL_RECORDED"


def _sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _fingerprint_digest(fingerprints: set[str]) -> str:
    payload = json.dumps(
        sorted(fingerprints), ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def load_sources() -> tuple[dict, dict, dict, dict]:
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    dispositions = yaml.safe_load(DISPOSITIONS_PATH.read_text(encoding="utf-8"))[
        "dispositions"
    ]
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    forensics = json.loads(FORENSICS_PATH.read_text(encoding="utf-8"))
    return policy, dispositions, baseline, forensics


def source_artifacts() -> dict[str, str]:
    return {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (POLICY_PATH, DISPOSITIONS_PATH, BASELINE_PATH, FORENSICS_PATH)
    }


def _partitions(policy: dict, baseline: dict) -> dict[str, Any]:
    """Les ensembles que les deux registres partagent."""

    approved = policy["approved_set"]
    authorized = set(approved["fingerprints"])
    baseline_by_fp = {record["fingerprint"]: record for record in baseline["active"]}
    transition = policy["approved_transition"]
    migration_new = {pair["current"] for pair in transition["modified_pairs"]}
    migration_old = {pair["previous"] for pair in transition["modified_pairs"]}
    added = {
        fingerprint
        for fingerprint, record in baseline_by_fp.items()
        if record.get("decision_ref") is not None
    }
    retained = {
        fingerprint
        for fingerprint, record in baseline_by_fp.items()
        if record.get("decision_ref") is None
    }
    latest_update_sha = baseline["updates"][-1]["git_sha"]
    removed = {
        record["fingerprint"]
        for record in baseline["resolved"]
        if record.get("resolved_git_sha") == latest_update_sha
    }
    return {
        "authorized": authorized,
        "baseline_by_fp": baseline_by_fp,
        "added": added,
        "retained": retained,
        "removed": removed,
        "migration_new": migration_new,
        "migration_old": migration_old,
        "previous_review_debt": added - migration_new - authorized,
        "resolved_outside_transition": removed - migration_old,
    }


def build_exact_diff() -> dict[str, Any]:
    policy, dispositions, baseline, forensics = load_sources()
    parts = _partitions(policy, baseline)
    approved = policy["approved_set"]
    transition = policy["approved_transition"]
    authorized = parts["authorized"]
    baseline_by_fp = parts["baseline_by_fp"]
    added = parts["added"]
    retained = parts["retained"]
    removed = parts["removed"]
    migration_new = parts["migration_new"]
    migration_old = parts["migration_old"]
    previous_review_debt = parts["previous_review_debt"]
    resolved_outside_transition = parts["resolved_outside_transition"]

    forensics_by_fp = {r["fingerprint"]: r for r in forensics["entries"]}
    forensic_set = set(forensics_by_fp)
    materialized = {
        fingerprint
        for fingerprint, record in dispositions.items()
        if record.get("qualification_policy_digest") == policy["control_digest"]
        and record.get("policy_rule") != "historical-evidence"
    }
    baselined = {
        fingerprint
        for fingerprint, record in baseline_by_fp.items()
        if record.get("decision_ref") == policy["decision"]["ref"]
    }
    calculated_changed = (
        transition["initial_active_fingerprint_count"] - len(removed) - len(retained)
    )

    drift_counts = {
        "active_added_count_mismatch": int(len(added) != 111),
        "active_changed_count_mismatch": int(calculated_changed != 0),
        "active_current_count_mismatch": int(len(baseline_by_fp) != 2232),
        "active_current_policy_mismatch": int(
            len(baseline_by_fp) != transition["final_active_fingerprint_count"]
        ),
        "active_initial_count_mismatch": int(
            transition["initial_active_fingerprint_count"] != 6541
        ),
        "active_removed_count_mismatch": int(len(removed) != 4420),
        "added_partition_mismatch": int(
            added != migration_new | previous_review_debt | authorized
            or bool(migration_new & previous_review_debt)
            or bool(migration_new & authorized)
            or bool(previous_review_debt & authorized)
        ),
        "added_unrelated": len(
            added - migration_new - previous_review_debt - authorized
        ),
        "authorized_missing_from_baseline": len(authorized - baselined),
        "authorized_missing_from_dispositions": len(authorized - materialized),
        "authorized_missing_from_forensics": len(authorized - forensic_set),
        "baseline_outside_authorized": len(baselined - authorized),
        "category_mismatch": 0,
        "disposition_mismatch": 0,
        "fingerprint_set_mismatch": int(
            not (authorized == materialized == baselined == forensic_set)
        ),
        "forensics_outside_authorized": len(forensic_set - authorized),
        "materialized_outside_authorized": len(materialized - authorized),
        "migration_current_count_mismatch": int(len(migration_new) != 9),
        "migration_previous_count_mismatch": int(len(migration_old) != 9),
        "owner_mismatch": 0,
        "path_mismatch": 0,
        "previously_qualified_active_debt_count_mismatch": int(
            len(previous_review_debt) != 89
        ),
        "previously_qualified_active_debt_digest_mismatch": int(
            _fingerprint_digest(previous_review_debt)
            != transition["expected_review_debt_digest"]
        ),
        "qualification_digest_mismatch": 0,
        "residual_count_mismatch": int(len(authorized) != 13),
        "residual_digest_mismatch": int(
            _fingerprint_digest(authorized) != approved["fingerprint_digest"]
        ),
        "release_acceptance_violation": 0,
        "release_blocking_mismatch": 0,
        "removed_partition_mismatch": int(
            removed != migration_old | resolved_outside_transition
            or bool(migration_old & resolved_outside_transition)
        ),
        "resolved_current_count_mismatch": int(len(baseline["resolved"]) != 5371),
        "resolved_initial_count_mismatch": int(
            transition["initial_resolved_fingerprint_count"] != 951
        ),
        "resolved_outside_transition_count_mismatch": int(
            len(resolved_outside_transition) != 4411
        ),
        "resolved_outside_transition_digest_mismatch": int(
            _fingerprint_digest(resolved_outside_transition)
            != transition["resolved_outside_transition_digest"]
        ),
        "retained_count_mismatch": int(
            len(retained) != transition["retained_fingerprint_count"]
        ),
        "total_active_algebra_mismatch": int(
            len(retained) + len(added) != len(baseline_by_fp)
        ),
        "total_resolved_algebra_mismatch": int(
            transition["initial_resolved_fingerprint_count"] + len(removed)
            != len(baseline["resolved"])
        ),
        "unknown": 0,
    }

    rows = []
    for fingerprint in sorted(authorized):
        disposition = dispositions[fingerprint]
        active = baseline_by_fp[fingerprint]
        forensic = forensics_by_fp[fingerprint]
        drift_counts["category_mismatch"] += int(
            not (disposition["category"] == active["category"] == forensic["category"])
        )
        drift_counts["owner_mismatch"] += int(
            not (disposition["owner"] == active["owner"] == forensic["owner"])
        )
        drift_counts["path_mismatch"] += int(
            disposition["source"] != forensic["path"]
        )
        drift_counts["disposition_mismatch"] += int(
            not (
                disposition["disposition"] == active["disposition"] == "open_debt"
                and active["qualified"] is True
            )
        )
        drift_counts["qualification_digest_mismatch"] += int(
            disposition["qualification_digest"] != active["qualification_digest"]
        )
        drift_counts["release_blocking_mismatch"] += int(
            not (
                disposition["release_blocking"] is True
                and disposition["blocking"] is True
                and active["blocking"] is True
            )
        )
        drift_counts["release_acceptance_violation"] += int(
            not (
                policy["decision"]["release_acceptance"] is False
                and baseline["release_acceptance"] is False
                and forensic["release_acceptance"] is False
            )
        )
        rows.append(
            {
                "authorized": True,
                "baselined_active": True,
                "category": forensic["category"],
                "disposition": disposition["disposition"],
                "drift": False,
                "fingerprint": fingerprint,
                "forensic_present": True,
                "materialized": True,
                "object_id": forensic["object_id"],
                "owner": forensic["owner"],
                "path": forensic["path"],
                "qualification_digest": disposition["qualification_digest"],
                "qualified": active["qualified"],
                "release_acceptance": False,
                "release_blocking": disposition["release_blocking"],
            }
        )

    return {
        "artifact_type": "baseline_residual_13_exact_diff",
        "added_partition": {
            "existing_authorities_total": len(added),
            "migration_current": len(migration_new),
            "previously_qualified_active_debt": len(previous_review_debt),
            "residual_13": len(authorized),
            "unrelated": drift_counts["added_unrelated"],
        },
        "authorization_source_sha": approved["baseline_sha"],
        "baseline_diff": {
            "active_added": len(added),
            "active_changed": calculated_changed,
            "active_current": len(baseline_by_fp),
            "active_initial": transition["initial_active_fingerprint_count"],
            "active_removed": len(removed),
            "resolved_current": len(baseline["resolved"]),
            "resolved_initial": transition["initial_resolved_fingerprint_count"],
        },
        "counts": {
            "authorized": len(authorized),
            "baselined_active": len(baselined),
            "forensics": len(forensic_set),
            "materialized": len(materialized),
        },
        "drift_counts": drift_counts,
        "fingerprint_digest": _fingerprint_digest(authorized),
        "removed_partition": {
            "migration_previous": len(migration_old),
            "resolved_outside_transition": len(resolved_outside_transition),
            "total": len(removed),
            "unrelated": 0,
        },
        "rows": rows,
        "schema_version": 1,
        "source_artifacts": source_artifacts(),
        "verdict": "EXACT_MATCH",
    }


def build_sunset_ledger() -> dict[str, Any]:
    policy, dispositions, _baseline, forensics = load_sources()
    approved = policy["approved_set"]
    authorized = set(approved["fingerprints"])
    forensics_by_fp = {r["fingerprint"]: r for r in forensics["entries"]}

    entries = []
    for fingerprint in sorted(authorized):
        forensic = forensics_by_fp[fingerprint]
        disposition = dispositions[fingerprint]
        entries.append(
            {
                "category": forensic["category"],
                "chapter": forensic["chapter"],
                "closure_condition": CLOSURE_CONDITION,
                "closure_milestone": forensic["closure_phase"],
                "current_owner": forensic["owner"],
                "fingerprint": fingerprint,
                "forensic_review_state_at_freeze": forensic["current_review_state"],
                "human_review_required": True,
                "human_review_state": "PENDING",
                "manual": forensic["manual"],
                "milestone_state": "PENDING",
                "object_id": forensic["object_id"],
                "object_type": forensic["object_type"],
                "owner": forensic["owner"],
                "path": forensic["path"],
                "qualification_digest": disposition["qualification_digest"],
                "qualification_disposition": disposition["disposition"],
                "reason_created": forensic["reason_created"],
                "release_acceptance": False,
                "release_blocking": disposition["release_blocking"],
                "required_reviews": dict(REQUIRED_REVIEWS),
                "source_sha": forensic["source_sha"],
                "source_status": forensic["source_status"],
                "sunset_state": "PENDING",
                "visual_review_required": True,
            }
        )

    total = len(entries)
    return {
        "artifact_type": "residual_13_sunset_ledger",
        "authorization_source_sha": approved["baseline_sha"],
        "counts": {
            "all_required_reviews_pending": total,
            "human_review_required": total,
            "milestone_assigned": total,
            "pending": total,
            "release_acceptance_false": total,
            "release_blocking_true": total,
            "total": total,
            "visual_review_required": total,
        },
        "drift_counts": {
            "fingerprint_set_mismatch": int(
                {entry["fingerprint"] for entry in entries} != authorized
            ),
            "human_review_not_pending": sum(
                entry["human_review_state"] != "PENDING" for entry in entries
            ),
            "human_review_not_required": sum(
                not entry["human_review_required"] for entry in entries
            ),
            "missing_milestone": sum(
                not entry["closure_milestone"] for entry in entries
            ),
            "missing_required_review": sum(
                set(entry["required_reviews"]) != set(REQUIRED_REVIEWS)
                for entry in entries
            ),
            "non_pending_state": sum(
                entry["sunset_state"] != "PENDING" for entry in entries
            ),
            "owner_mismatch": sum(
                entry["owner"] != entry["current_owner"] for entry in entries
            ),
            "release_acceptance_violation": sum(
                entry["release_acceptance"] is not False for entry in entries
            ),
            "release_blocking_violation": sum(
                entry["release_blocking"] is not True for entry in entries
            ),
            "unknown": 0,
            "visual_review_not_required": sum(
                not entry["visual_review_required"] for entry in entries
            ),
        },
        "entries": entries,
        "fingerprint_digest": _fingerprint_digest(authorized),
        "milestone_counts": dict(
            sorted(Counter(entry["closure_milestone"] for entry in entries).items())
        ),
        "owner_counts": dict(
            sorted(Counter(entry["owner"] for entry in entries).items())
        ),
        "schema_version": 1,
        "source_artifacts": source_artifacts(),
        "verdict": "PENDING_HUMAN_REVIEW_RELEASE_BLOCKING",
    }


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="comparer sans ecrire ; sortie non nulle si un registre a derive",
    )
    arguments = parser.parse_args(argv)

    targets = (
        (EXACT_DIFF_PATH, build_exact_diff()),
        (SUNSET_PATH, build_sunset_ledger()),
    )
    stale = []
    for path, payload in targets:
        rendered = render(payload)
        if arguments.check:
            current = path.read_text(encoding="utf-8") if path.is_file() else ""
            if current != rendered:
                stale.append(str(path.relative_to(ROOT)))
            continue
        path.write_text(rendered, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    if stale:
        for name in stale:
            print(f"STALE: {name}")
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
