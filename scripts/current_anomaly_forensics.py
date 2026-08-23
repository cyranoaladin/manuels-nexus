#!/usr/bin/env python3
"""Build exact, non-mutating anomaly-set forensics.

This module deliberately does not update the anomaly baseline or its policy.
It only projects the canonical comparison into explicit set partitions.
"""

from __future__ import annotations

import hashlib
from itertools import combinations
from typing import Iterable


def _sorted(values: Iterable[str]) -> list[str]:
    return sorted(set(values))


def build_exact_set_algebra(
    *,
    baseline: set[str],
    current: set[str],
    unchanged: set[str],
    resolved: set[str],
    approved_transition_old: set[str],
    approved_transition_new: set[str],
    expected_review_debt: set[str],
    true_new: set[str],
) -> dict[str, object]:
    """Return the exact baseline/current partitions and their intersections."""

    surviving_baseline = unchanged | approved_transition_old
    surviving_current_projection = unchanged | approved_transition_new
    previously_qualified = set(expected_review_debt)
    named_sets = {
        "BASELINE": baseline,
        "SURVIVING_BASELINE": surviving_baseline,
        "RESOLVED_BASELINE": resolved,
        "PREVIOUSLY_QUALIFIED_ACTIVE_DEBT": previously_qualified,
        "EXPECTED_REVIEW_DEBT": expected_review_debt,
        "APPROVED_TRANSITION_OLD": approved_transition_old,
        "APPROVED_TRANSITION_NEW": approved_transition_new,
        "TRUE_NEW": true_new,
        "CURRENT_ACTIVE": current,
        "UNCHANGED": unchanged,
        "SURVIVING_BASELINE_CURRENT_PROJECTION": surviving_current_projection,
    }
    nonempty_intersections = []
    for left, right in combinations(named_sets, 2):
        intersection = named_sets[left] & named_sets[right]
        if intersection:
            nonempty_intersections.append(
                {
                    "left": left,
                    "right": right,
                    "cardinality": len(intersection),
                    "fingerprints": _sorted(intersection),
                }
            )

    baseline_partition = resolved | surviving_baseline
    current_partition = (
        surviving_current_projection | expected_review_debt | true_new
    )
    partition_components = (
        unchanged,
        approved_transition_new,
        expected_review_debt,
        true_new,
    )
    pairwise_disjoint_current = all(
        not left & right for left, right in combinations(partition_components, 2)
    )
    true_new_bytes = "".join(f"{value}\n" for value in _sorted(true_new)).encode(
        "ascii"
    )

    return {
        "aliases": {
            "PREVIOUSLY_QUALIFIED_ACTIVE_DEBT": "EXPECTED_REVIEW_DEBT"
        },
        "cardinalities": {
            name: len(values) for name, values in named_sets.items()
        },
        "equalities": {
            "baseline_partition": baseline_partition == baseline,
            "current_partition": current_partition == current,
            "current_partition_pairwise_disjoint": pairwise_disjoint_current,
        },
        "nonempty_intersections": nonempty_intersections,
        "sets": {name: _sorted(values) for name, values in named_sets.items()},
        "true_new_set_digest": "sha256:"
        + hashlib.sha256(true_new_bytes).hexdigest(),
    }
