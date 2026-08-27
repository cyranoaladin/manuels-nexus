"""Tests de la reconciliation trois voies et du gel canonique 1SPE-SUITES.

Deux invariants sont verrouilles ici :

* aucun delta du WIP ne peut disparaitre sans disposition enregistree ;
* le gel canonique de 1SPE-SUITES porte 161 objets uniques et se reproduit.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import reconcile_wip_upstream as rec  # noqa: E402

RECONCILIATION = ROOT / "audit" / "WIP_UPSTREAM_RECONCILIATION.json"
LEDGER = ROOT / "audit" / "WIP_DROPPED_DELTA_LEDGER.json"
FREEZE = ROOT / "audit" / "1SPE_SUITES_REVIEW_SOURCE_FREEZE.json"
C8_PROOF = ROOT / "audit" / "1SPE_SUITES_C8_UNIQUENESS_PROOF.json"
DECISION = ROOT / "audit" / "1SPE_SUITES_REVIEW_FREEZE_CORRECTION_DECISION.json"

FREEZE_SHA = "c667f12b1792f31981b6b5894c8c604df1bce634"
CANONICAL_DIGEST = (
    "sha256:67d8006298299b44029de8ba8f85b500d9b3619997a0c596e63c20e1cffeee2d"
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Gel canonique 161
# --------------------------------------------------------------------------


def test_the_canonical_freeze_carries_161_unique_objects() -> None:
    freeze = _json(FREEZE)
    assert freeze["source_sha"] == FREEZE_SHA
    assert freeze["counts"]["chapter_objects"] == 161
    assert freeze["counts"]["unknown"] == 0
    identifiers = [row["object_id"] for row in freeze["objects"]]
    assert len(identifiers) == 161
    assert len(set(identifiers)) == 161, "un object_id canonique = une seule entree"


def test_the_original_161_digest_reproduces() -> None:
    freeze = _json(FREEZE)
    assert freeze["chapter_object_set_digest"] == CANONICAL_DIGEST
    decision = _json(DECISION)
    assert decision["canonical_freeze"]["ORIGINAL_161_FREEZE_REPRODUCED"] == "YES"
    assert decision["canonical_freeze"]["object_count"] == 161


def test_the_156_decision_is_invalidated_not_merely_superseded() -> None:
    decision = _json(DECISION)
    entry = decision["human_decision_received"]["superseded_by_decision"]
    assert entry["old_156_decision_state"] == "INVALIDATED_PREMISE_DISPROVEN"
    assert entry["canonical_human_review_object_count"] == 161
    assert entry["canonical_source_sha"] == FREEZE_SHA
    assert decision["root_cause"]["double_counting"] is False


@pytest.mark.parametrize(
    "object_id",
    [
        "1SPE-SUITES-CR-017",
        "1SPE-SUITES-ME-008",
        "1SPE-SUITES-EX-051",
        "1SPE-SUITES-CO-051",
        "1SPE-SUITES-RE-C8",
    ],
)
def test_each_c8_object_occurs_exactly_once(object_id: str) -> None:
    proof = _json(C8_PROOF)
    entry = next(row for row in proof["c8_objects"] if row["object_id"] == object_id)
    assert entry["occurrence_count"] == 1
    assert entry["meta_matches_object_id"] is True
    assert entry["programme_atoms"] == ["1SPE-SUITES-C8"]
    assert entry["source_blob_sha1"]


def test_the_fr_r_sheets_add_no_extra_occurrence() -> None:
    proof = _json(C8_PROOF)
    assert proof["fr_r_add_no_extra_occurrence"] is True
    assert all(row["occurrence_count"] == 1 for row in proof["fr_r_objects"])
    assert proof["duplicate_object_ids"] == []
    assert proof["unique_object_ids"] == proof["canonical_object_count"] == 161


def test_the_156_packets_are_invalidated_and_preserved() -> None:
    directory = ROOT / "audit/reviews/human/1SPE-SUITES/superseded/freeze-156-761508d9"
    stored = sorted(directory.glob("packet-*.json"))
    assert len(stored) == 2, "les packets invalides doivent etre conserves"
    for path in stored:
        payload = _json(path)
        assert payload["freeze_state"] == "INVALIDATED_WRONG_SOURCE_SCOPE"
        assert payload["receipt_may_attach"] is False


def test_the_current_packets_bind_the_161_freeze() -> None:
    directory = ROOT / "audit/reviews/human/1SPE-SUITES/freeze-161-c667f12b"
    packets = sorted(directory.glob("packet-*.json"))
    assert len(packets) == 2
    for path in packets:
        payload = _json(path)
        assert payload["object_count"] == 161
        assert len(payload["objects"]) == 161
        assert payload["reviewer_assignment"] == "PENDING_UNASSIGNED"
        assert payload["verdict"] is None
        freeze = payload["canonical_source_freeze"]
        assert freeze["source_sha"] == FREEZE_SHA
        assert freeze["chapter_object_set_digest"] == CANONICAL_DIGEST
        assert freeze["chapter_objects"] == 161
        assert freeze["chapter_object_set_digest"] != payload["object_set_digest"], (
            "les deux digests sont distincts et ne doivent jamais etre confondus"
        )
    state = _json(directory / "REVIEW_STATE.json")
    assert state["review_a"]["state"] == "PENDING_UNASSIGNED"
    assert state["review_b"]["state"] == "PENDING_UNASSIGNED"
    assert state["qcm_human_approval"] == "PENDING"


# --------------------------------------------------------------------------
# Reconciliation WIP
# --------------------------------------------------------------------------


def test_every_classification_is_declared() -> None:
    report = _json(RECONCILIATION)
    for entry in report["files"]:
        assert entry["classification"] in rec.CLASSIFICATIONS, entry["path"]
    assert report["unknown"] == 0


def test_generated_files_are_never_treated_as_conflicts() -> None:
    """Un .tex de QCM se regenere, il ne se reconcilie pas."""

    report = _json(RECONCILIATION)
    generated = [
        entry
        for entry in report["files"]
        if entry["classification"] == "GENERATED_DERIVATIVE"
    ]
    assert generated
    for entry in generated:
        assert entry["derived_from"], entry["path"]
        assert entry["producer"], entry["path"]
        assert entry["needs_human_editorial_decision"] is False


def test_no_wip_delta_is_dropped_silently() -> None:
    ledger = _json(LEDGER)
    assert ledger["silent_drops"] == 0
    assert ledger["accounting"]["dispositioned"] == "59/59"
    assert ledger["accounting"]["lost_valid_deltas"] == 0
    assert ledger["accounting"]["unknown"] == 0
    assert ledger["accounting"]["every_wip_delta_has_a_recorded_disposition"] is True
    allowed = {
        "SUPERSEDED_BY_CORRECT_UPSTREAM",
        "SUPERSEDED_BY_CLEARER_UNAMBIGUOUS_UPSTREAM",
        "SCIENTIFICALLY_WRONG",
        "WRONG_PROGRAMME_YEAR",
        "DUPLICATE",
        "NO_LONGER_REQUIRED",
        "OTHER_EXPLICIT",
        "PARTIELLEMENT_PORTABLE",
    }
    for entry in ledger["dropped_deltas"]:
        assert entry["reason_dropped"] in allowed, entry
        assert entry["proof"], entry


def test_the_wip_touched_no_question_the_upstream_left_alone() -> None:
    ledger = _json(LEDGER)
    assert ledger["wip_only_question_changes"] == 0
    totals = ledger["qcm_three_way_totals"]
    assert "WIP_ONLY_CHANGE" not in totals


def test_neither_side_is_a_superset_on_remediation_pointers() -> None:
    """Le plus recent n'est pas automatiquement le meilleur."""

    coverage = _json(LEDGER)["renvoi_coverage"]
    assert coverage["upstream"]["without"] == 108
    assert coverage["wip"]["without"] == 99
    assert coverage["wip"]["without"] < coverage["upstream"]["without"]


def test_no_editorial_decision_remains_pending() -> None:
    ledger = _json(LEDGER)
    assert ledger["deltas_requiring_human_editorial_decision"] == []
    resolved = ledger["resolved_editorial_decisions"]
    assert resolved, "les arbitrages rendus doivent rester traces"
    for entry in resolved:
        assert entry["resolution"] == "APPLIED"


def test_q9_is_not_recorded_as_a_scientific_error() -> None:
    """Sous u_{n+1}=q u_n, un terme nul est possible : le WIP n'etait pas faux."""

    ledger = _json(LEDGER)
    entry = next(
        item
        for item in ledger["dropped_deltas"]
        if item["path"].endswith("1SPE-SUITES-QCM.json") and item["scope"].startswith("Q9")
    )
    assert entry["reason_dropped"] == "SUPERSEDED_BY_CLEARER_UNAMBIGUOUS_UPSTREAM"
    assert entry["previous_classification"] == "SCIENTIFICALLY_WRONG"
    assert entry["severity"] == "NOT_A_DEFECT"


def test_the_euler_delta_is_superseded_not_wrong() -> None:
    ledger = _json(LEDGER)
    entry = next(
        item
        for item in ledger["dropped_deltas"]
        if "TEXP-GRAPHES" in item["path"] and item["scope"].startswith("Q3")
    )
    assert entry["reason_dropped"] == "SUPERSEDED_BY_CORRECT_UPSTREAM"
    assert entry["severity"] == "NOT_A_DEFECT"
    assert entry["future_option"]


def test_no_remediation_target_was_fabricated() -> None:
    result = _json(LEDGER)["renvoi_port_result"]
    assert result["no_target_fabricated"] is True
    assert result["ported"] + result["rejected"] == result["candidates"] == 45
    assert result["ported"] == 0
    assert result["blocking_constraint_discovered"]["escalated"] is True
    assert result["open_findings"]


def test_the_p0_correction_is_preserved_upstream() -> None:
    """La correction CO-048 ne doit pas pouvoir se perdre dans l'arbitrage."""

    ledger = _json(LEDGER)
    entry = next(
        item
        for item in ledger["deltas_to_port"]
        if item["path"].endswith("1SPE-VARALEA-CO-048.tex")
    )
    assert entry["p0_preserved_upstream"] is True
    upstream = subprocess.run(
        ["git", "show", "dc6735d1:Mathematiques/manuel-maths/chapitres/"
         "1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-048.tex"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    assert "15\\,552\\,000" in upstream
    assert "assert V5 == 15552000" in upstream
    assert "assert round(float(sqrt(V5))) == 3944" in upstream


def test_no_reconciliation_output_mutates_the_repository() -> None:
    assert _json(RECONCILIATION)["modifies_nothing"] is True


def test_a_freeze_is_never_bound_to_another_chapter() -> None:
    """Le garde-fou doit refuser de lier un packet au gel d'un autre chapitre."""

    import human_review_governance as g

    policy = g.load_policy(ROOT)
    scope = g.build_scope("1SPE-VARIABLES-ALEATOIRES", ROOT)
    foreign = g.load_source_freeze("1SPE-SUITES", ROOT)
    assert foreign is not None and foreign["chapter_objects"] == 161
    with pytest.raises(g.HumanReviewViolation, match="meme nombre d'objets"):
        g.build_packet(scope, "EXPERT_MATHEMATIQUE", policy, [], ROOT, source_freeze=foreign)


def test_each_chapter_resolves_its_own_freeze() -> None:
    import human_review_governance as g

    assert g.source_freeze_path("1SPE-SUITES", ROOT).name == (
        "1SPE_SUITES_REVIEW_SOURCE_FREEZE.json"
    )
    assert g.load_source_freeze("1SPE-VARIABLES-ALEATOIRES", ROOT) is None
