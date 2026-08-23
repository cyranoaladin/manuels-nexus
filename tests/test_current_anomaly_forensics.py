from __future__ import annotations

import hashlib

from scripts.current_anomaly_forensics import build_exact_set_algebra


def test_exact_set_algebra_projects_transitions_without_double_counting() -> None:
    baseline = {"stable", "old", "resolved"}
    current = {"stable", "new", "expected", "fresh"}

    report = build_exact_set_algebra(
        baseline=baseline,
        current=current,
        unchanged={"stable"},
        resolved={"resolved"},
        approved_transition_old={"old"},
        approved_transition_new={"new"},
        expected_review_debt={"expected"},
        true_new={"fresh"},
    )

    assert report["cardinalities"]["BASELINE"] == 3
    assert report["cardinalities"]["SURVIVING_BASELINE"] == 2
    assert report["cardinalities"]["CURRENT_ACTIVE"] == 4
    assert report["equalities"]["baseline_partition"] is True
    assert report["equalities"]["current_partition"] is True
    assert report["sets"]["SURVIVING_BASELINE"] == ["old", "stable"]
    assert report["sets"]["PREVIOUSLY_QUALIFIED_ACTIVE_DEBT"] == [
        "expected"
    ]
    assert report["aliases"] == {
        "PREVIOUSLY_QUALIFIED_ACTIVE_DEBT": "EXPECTED_REVIEW_DEBT"
    }
    assert report["sets"]["SURVIVING_BASELINE_CURRENT_PROJECTION"] == [
        "new",
        "stable",
    ]
    assert report["nonempty_intersections"]


def test_true_new_digest_is_canonical_and_order_independent() -> None:
    first = build_exact_set_algebra(
        baseline=set(),
        current={"b", "a"},
        unchanged=set(),
        resolved=set(),
        approved_transition_old=set(),
        approved_transition_new=set(),
        expected_review_debt=set(),
        true_new={"b", "a"},
    )
    second = build_exact_set_algebra(
        baseline=set(),
        current={"a", "b"},
        unchanged=set(),
        resolved=set(),
        approved_transition_old=set(),
        approved_transition_new=set(),
        expected_review_debt=set(),
        true_new={"a", "b"},
    )

    expected = "sha256:" + hashlib.sha256(b"a\nb\n").hexdigest()
    assert first["true_new_set_digest"] == expected
    assert second["true_new_set_digest"] == expected
