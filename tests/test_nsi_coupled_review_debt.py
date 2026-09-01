"""La reconstruction 1NSI declare sa dette de revue ; elle n'approuve rien.

Trente-six objets ont ete ecrits ou reecrits dans les deux chapitres
d'algorithmique. Chacun est verifie par execution -- les blocs Python tournent,
les assertions passent -- et aucun n'a ete relu par un humain.

Ces tests interdisent ce qui rendrait ce registre dangereux : qu'il cesse
d'etre bloquant, entre en baseline, ou se voie attribuer un relecteur invente.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "audit/NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "nsi_coupled_debt", ROOT / "scripts/build_nsi_coupled_review_debt.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def test_the_committed_ledger_matches_the_producer(producer) -> None:
    assert producer.main(["--check"]) == 0


def test_the_ledger_approves_nothing(payload: dict) -> None:
    assert payload["in_approved_baseline"] is False
    assert payload["release_blocking"] is True
    assert payload["release_acceptance"] is False
    assert payload["is_baseline_qualification"] is False
    assert payload["is_gate_exception"] is False
    for entry in payload["entries"]:
        assert entry["policy_disposition"] == "open_debt"
        assert entry["in_approved_baseline"] is False
        assert entry["release_blocking"] is True
        assert entry["release_acceptance"] is False
        assert entry["status"] != "approved"

    assert set(payload["human_review_packets"].values()) == {"PENDING_UNASSIGNED"}
    assert payload["reviewers_must_be_distinct"] is True
    assert set(payload["human_review_packets"]) == {
        "EXPERT_NSI",
        "EXPERT_PROGRAMME_PEDAGOGIE",
    }


def test_machine_verification_is_never_relabelled_as_lost_human_approval(
    payload: dict,
) -> None:
    """`verified` est une preuve machine, jamais une approbation humaine."""

    rewritten_machine = [
        e
        for e in payload["entries"]
        if e["origin"] == "REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED"
    ]
    created = [e for e in payload["entries"] if e["origin"] == "CREATED"]
    assert len(rewritten_machine) == 4
    assert len(created) == 32
    assert len(rewritten_machine) + len(created) == payload["count"] == 36

    for entry in rewritten_machine:
        assert entry["status_before_rewrite"] == "verified"
        assert entry["human_approval_invalidated_by_rewrite"] is False
        assert entry["human_approval_evidence"] is False
        assert entry["semantic_digest_before"].startswith("sha256:")
        assert entry["semantic_digest_current"].startswith("sha256:")
        assert entry["semantic_digest_before"] != entry["semantic_digest_current"]
        assert entry["source_sha256"].startswith("sha256:")
    for entry in created:
        assert entry["status_before_rewrite"] is None
        assert entry["human_approval_invalidated_by_rewrite"] is False
        assert entry["semantic_digest_before"] is None


def test_only_explicit_approved_status_counts_as_human_approval(producer) -> None:
    assert producer.HUMAN_APPROVED_STATUSES == frozenset({"approved"})
    assert "verified" not in producer.HUMAN_APPROVED_STATUSES


def test_machine_verification_is_not_presented_as_human_review(
    payload: dict,
) -> None:
    """La distinction que le P0 de clonage a rendue couteuse."""

    verification = payload["machine_verification_performed"]
    assert verification["clone_capacity_integrity"] == {
        "invalid_credit_objects": 0,
        "indeterminate_credit_objects": 0,
        "status": "COMPLETE",
    }
    assert verification["cross_discipline"] == {
        "condemned": 0,
        "unknown": 0,
        "status": "COMPLETE",
    }
    assert verification["role_coverage"]["cells"] == 63
    assert verification["role_coverage"]["semantic_unknown"] == 63
    assert verification["role_coverage"]["status"] == "UNVALIDATED"
    assert verification["execution_evidence"]["status"] == "UNBOUND_RECEIPTS"
    assert verification["execution_evidence"]["source_bound_current"] == 0
    assert "ne remplace" in verification["note"]
    assert not any(entry["machine_verified_by_execution"] for entry in payload["entries"])
    assert all(entry["human_review_required"] for entry in payload["entries"])


def test_the_debt_is_disjoint_from_the_other_ledgers(payload: dict) -> None:
    mine = {e["fingerprint"] for e in payload["entries"]}
    assert len(mine) == payload["count"]
    for other in (
        "audit/TSPE_GEOESPACE_AUTHORED_REVIEW_DEBT_45.json",
        "audit/VARALEA_C6C7_REVIEW_DEBT_12.json",
        "audit/NSI_TC_EVAL_CORRIGES_REVIEW_DEBT_2.json",
        "audit/TNSI_PROJET_QCM_REVIEW_DEBT_1.json",
    ):
        theirs = {
            str(e["fingerprint"])
            for e in json.loads((ROOT / other).read_text(encoding="utf-8"))["entries"]
        }
        assert mine.isdisjoint(theirs), other
