from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "audit/BASELINE_QUALIFICATION_POLICY.yaml"
DISPOSITIONS_PATH = ROOT / "audit/ANOMALY_DISPOSITIONS.yaml"
BASELINE_PATH = ROOT / "audit/ANOMALIES_BASELINE.json"
FORENSICS_PATH = ROOT / "audit/RESIDUAL_TRUE_NEW_FORENSICS.json"
EXACT_DIFF_PATH = ROOT / "audit/BASELINE_RESIDUAL_13_EXACT_DIFF.json"
EXACT_DIFF_MD_PATH = ROOT / "audit/BASELINE_RESIDUAL_13_EXACT_DIFF.md"
SUNSET_PATH = ROOT / "audit/RESIDUAL_13_SUNSET_LEDGER.json"
SUNSET_MD_PATH = ROOT / "audit/RESIDUAL_13_SUNSET_LEDGER.md"

EXPECTED_DIGEST = (
    "sha256:1abe51ad406752b1e09996020c1afb2db3982ac2741cf98ed7b2118f302ace98"
)
REQUIRED_REVIEWS = {
    "editorial": "PENDING",
    "pedagogical": "PENDING",
    "programme": "PENDING",
    "scientific": "PENDING",
    "variant": "PENDING",
    "visual": "PENDING",
}


def _load_sources() -> tuple[dict, dict, dict, dict]:
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    dispositions = yaml.safe_load(
        DISPOSITIONS_PATH.read_text(encoding="utf-8")
    )["dispositions"]
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    forensics = json.loads(FORENSICS_PATH.read_text(encoding="utf-8"))
    return policy, dispositions, baseline, forensics


def _sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _source_artifacts() -> dict[str, str]:
    return {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (
            POLICY_PATH,
            DISPOSITIONS_PATH,
            BASELINE_PATH,
            FORENSICS_PATH,
        )
    }


def _fingerprint_digest(fingerprints: set[str]) -> str:
    payload = json.dumps(
        sorted(fingerprints),
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def test_residual_13_exact_diff_matches_all_canonical_sources() -> None:
    policy, dispositions, baseline, forensics = _load_sources()
    report = json.loads(EXACT_DIFF_PATH.read_text(encoding="utf-8"))

    approved = policy["approved_set"]
    authorized = set(approved["fingerprints"])
    materialized = {
        fingerprint
        for fingerprint, record in dispositions.items()
        if record.get("qualification_policy_digest") == policy["control_digest"]
        and record.get("policy_rule") != "historical-evidence"
    }
    baseline_by_fp = {
        record["fingerprint"]: record for record in baseline["active"]
    }
    baselined = {
        fingerprint
        for fingerprint, record in baseline_by_fp.items()
        if record.get("decision_ref") == policy["decision"]["ref"]
    }
    forensics_by_fp = {
        record["fingerprint"]: record for record in forensics["entries"]
    }
    forensic_set = set(forensics_by_fp)
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
    migration_new = {
        pair["current"]
        for pair in policy["approved_transition"]["modified_pairs"]
    }
    migration_old = {
        pair["previous"]
        for pair in policy["approved_transition"]["modified_pairs"]
    }
    previous_review_debt = added - migration_new - authorized
    latest_update_sha = baseline["updates"][-1]["git_sha"]
    removed = {
        record["fingerprint"]
        for record in baseline["resolved"]
        if record.get("resolved_git_sha") == latest_update_sha
    }
    resolved_outside_transition = removed - migration_old
    calculated_changed = (
        policy["approved_transition"]["initial_active_fingerprint_count"]
        - len(removed)
        - len(retained)
    )

    assert len(authorized) == 13
    assert approved["fingerprint_count"] == 13
    assert approved["fingerprint_digest"] == EXPECTED_DIGEST
    assert _fingerprint_digest(authorized) == EXPECTED_DIGEST

    expected_counts = {
        "authorized": 13,
        "baselined_active": 13,
        "forensics": 13,
        "materialized": 13,
    }
    expected_baseline_diff = {
        "active_added": 111,
        "active_changed": 0,
        "active_current": 2232,
        "active_initial": 6541,
        "active_removed": 4420,
        "resolved_current": 5371,
        "resolved_initial": 951,
    }
    expected_added_partition = {
        "existing_authorities_total": 111,
        "migration_current": 9,
        "previously_qualified_active_debt": 89,
        "residual_13": 13,
        "unrelated": 0,
    }
    expected_removed_partition = {
        "migration_previous": 9,
        "resolved_outside_transition": 4411,
        "total": 4420,
        "unrelated": 0,
    }
    expected_drifts = {
        "active_added_count_mismatch": int(len(added) != 111),
        "active_changed_count_mismatch": int(calculated_changed != 0),
        "active_current_count_mismatch": int(len(baseline_by_fp) != 2232),
        "active_current_policy_mismatch": int(
            len(baseline_by_fp)
            != policy["approved_transition"]["final_active_fingerprint_count"]
        ),
        "active_initial_count_mismatch": int(
            policy["approved_transition"]["initial_active_fingerprint_count"]
            != 6541
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
            != policy["approved_transition"]["expected_review_debt_digest"]
        ),
        "qualification_digest_mismatch": 0,
        "residual_count_mismatch": int(len(authorized) != 13),
        "residual_digest_mismatch": int(
            _fingerprint_digest(authorized) != EXPECTED_DIGEST
        ),
        "release_acceptance_violation": 0,
        "release_blocking_mismatch": 0,
        "removed_partition_mismatch": int(
            removed != migration_old | resolved_outside_transition
            or bool(migration_old & resolved_outside_transition)
        ),
        "resolved_current_count_mismatch": int(
            len(baseline["resolved"]) != 5371
        ),
        "resolved_initial_count_mismatch": int(
            policy["approved_transition"]["initial_resolved_fingerprint_count"]
            != 951
        ),
        "resolved_outside_transition_count_mismatch": int(
            len(resolved_outside_transition) != 4411
        ),
        "resolved_outside_transition_digest_mismatch": int(
            _fingerprint_digest(resolved_outside_transition)
            != policy["approved_transition"][
                "resolved_outside_transition_digest"
            ]
        ),
        "retained_count_mismatch": int(
            len(retained)
            != policy["approved_transition"]["retained_fingerprint_count"]
        ),
        "total_active_algebra_mismatch": int(
            len(retained) + len(added) != len(baseline_by_fp)
        ),
        "total_resolved_algebra_mismatch": int(
            policy["approved_transition"]["initial_resolved_fingerprint_count"]
            + len(removed)
            != len(baseline["resolved"])
        ),
        "unknown": 0,
    }
    expected_rows = []
    for fingerprint in sorted(authorized):
        disposition = dispositions[fingerprint]
        active = baseline_by_fp[fingerprint]
        forensic = forensics_by_fp[fingerprint]
        category_matches = (
            disposition["category"] == active["category"] == forensic["category"]
        )
        owner_matches = (
            disposition["owner"] == active["owner"] == forensic["owner"]
        )
        path_matches = disposition["source"] == forensic["path"]
        disposition_matches = (
            disposition["disposition"] == active["disposition"] == "open_debt"
            and active["qualified"] is True
        )
        digest_matches = (
            disposition["qualification_digest"]
            == active["qualification_digest"]
        )
        blocking_matches = (
            disposition["release_blocking"] is True
            and disposition["blocking"] is True
            and active["blocking"] is True
        )
        release_acceptance_matches = (
            policy["decision"]["release_acceptance"] is False
            and baseline["release_acceptance"] is False
            and forensic["release_acceptance"] is False
        )
        expected_drifts["category_mismatch"] += int(not category_matches)
        expected_drifts["owner_mismatch"] += int(not owner_matches)
        expected_drifts["path_mismatch"] += int(not path_matches)
        expected_drifts["disposition_mismatch"] += int(not disposition_matches)
        expected_drifts["qualification_digest_mismatch"] += int(
            not digest_matches
        )
        expected_drifts["release_blocking_mismatch"] += int(
            not blocking_matches
        )
        expected_drifts["release_acceptance_violation"] += int(
            not release_acceptance_matches
        )
        expected_rows.append(
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

    assert report == {
        "artifact_type": "baseline_residual_13_exact_diff",
        "added_partition": expected_added_partition,
        "authorization_source_sha": approved["baseline_sha"],
        "baseline_diff": expected_baseline_diff,
        "counts": expected_counts,
        "drift_counts": expected_drifts,
        "fingerprint_digest": EXPECTED_DIGEST,
        "removed_partition": expected_removed_partition,
        "rows": expected_rows,
        "schema_version": 1,
        "source_artifacts": _source_artifacts(),
        "verdict": "EXACT_MATCH",
    }
    assert set(report["drift_counts"].values()) == {0}


def test_residual_13_sunset_ledger_is_pending_and_release_blocking() -> None:
    policy, dispositions, _baseline, forensics = _load_sources()
    ledger = json.loads(SUNSET_PATH.read_text(encoding="utf-8"))
    approved = policy["approved_set"]
    authorized = set(approved["fingerprints"])
    forensics_by_fp = {
        record["fingerprint"]: record for record in forensics["entries"]
    }

    expected_entries = []
    for fingerprint in sorted(authorized):
        forensic = forensics_by_fp[fingerprint]
        disposition = dispositions[fingerprint]
        expected_entries.append(
            {
                "category": forensic["category"],
                "chapter": forensic["chapter"],
                "closure_condition": (
                    "ALL_REQUIRED_REVIEWS_COMPLETE_AND_HUMAN_APPROVAL_RECORDED"
                ),
                "closure_milestone": forensic["closure_phase"],
                "current_owner": forensic["owner"],
                "fingerprint": fingerprint,
                "forensic_review_state_at_freeze": forensic[
                    "current_review_state"
                ],
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
                "required_reviews": REQUIRED_REVIEWS,
                "source_sha": forensic["source_sha"],
                "source_status": forensic["source_status"],
                "sunset_state": "PENDING",
                "visual_review_required": True,
            }
        )

    expected_owner_counts = dict(
        sorted(Counter(entry["owner"] for entry in expected_entries).items())
    )
    expected_milestones = dict(
        sorted(
            Counter(
                entry["closure_milestone"] for entry in expected_entries
            ).items()
        )
    )
    assert expected_owner_counts == approved["owner_counts"]
    assert ledger == {
        "artifact_type": "residual_13_sunset_ledger",
        "authorization_source_sha": approved["baseline_sha"],
        "counts": {
            "all_required_reviews_pending": 13,
            "human_review_required": 13,
            "milestone_assigned": 13,
            "pending": 13,
            "release_acceptance_false": 13,
            "release_blocking_true": 13,
            "total": 13,
            "visual_review_required": 13,
        },
        "drift_counts": {
            "fingerprint_set_mismatch": 0,
            "human_review_not_pending": 0,
            "human_review_not_required": 0,
            "missing_milestone": 0,
            "missing_required_review": 0,
            "non_pending_state": 0,
            "owner_mismatch": 0,
            "release_acceptance_violation": 0,
            "release_blocking_violation": 0,
            "unknown": 0,
            "visual_review_not_required": 0,
        },
        "entries": expected_entries,
        "fingerprint_digest": EXPECTED_DIGEST,
        "milestone_counts": expected_milestones,
        "owner_counts": expected_owner_counts,
        "schema_version": 1,
        "source_artifacts": _source_artifacts(),
        "verdict": "PENDING_HUMAN_REVIEW_RELEASE_BLOCKING",
    }
    assert set(ledger["drift_counts"].values()) == {0}


def test_residual_13_markdown_reports_are_exact_and_object_visible() -> None:
    policy, _dispositions, _baseline, _forensics = _load_sources()
    fingerprints = policy["approved_set"]["fingerprints"]
    exact_diff = EXACT_DIFF_MD_PATH.read_text(encoding="utf-8")
    sunset = SUNSET_MD_PATH.read_text(encoding="utf-8")

    assert "AUTHORIZED = `13`" in exact_diff
    assert "MATERIALIZED = `13`" in exact_diff
    assert "BASELINED_ACTIVE = `13`" in exact_diff
    assert "FORENSICS = `13`" in exact_diff
    assert "ACTIVE = `6541 → 2232`" in exact_diff
    assert "RESOLVED = `951 → 5371`" in exact_diff
    assert "ADDED = `111 = 9 + 89 + 13`" in exact_diff
    assert "REMOVED = `4420 = 9 + 4411`" in exact_diff
    assert "CHANGED = `0`" in exact_diff
    assert "ADDED_UNRELATED = `0`" in exact_diff
    assert "Tous les compteurs de dérive sont à `0`" in exact_diff
    assert EXPECTED_DIGEST in exact_diff
    assert "PENDING = `13`" in sunset
    assert "release_acceptance = `false` pour 13/13" in sunset
    assert "revue humaine requise = `13/13`" in sunset
    assert "revue visuelle requise = `13/13`" in sunset
    assert "Tous les compteurs de dérive sont à `0`" in sunset
    for fingerprint in fingerprints:
        assert exact_diff.count(f"`{fingerprint}`") == 1
        assert sunset.count(f"`{fingerprint}`") == 1
