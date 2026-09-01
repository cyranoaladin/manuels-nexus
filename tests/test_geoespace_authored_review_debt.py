"""Un registre de dette declare ; il n'approuve rien.

La reconstruction de TSPE-GEOMETRIE-ESPACE a produit quarante-cinq objets que
la machine a verifies et que personne n'a relus. Le modele residuel refusait de
tourner tant qu'ils n'etaient ni qualifies ni declares -- et il avait raison.

Le risque, en levant ce blocage, est d'ecrire un registre qui ressemble a une
declaration mais fonctionne comme une approbation. Ces tests interdisent
exactement cela : le registre doit rester bloquant, hors baseline, et sans
acceptation de release. Un jour ou quelqu'un basculerait un de ces drapeaux
pour rendre un gate vert, la suite doit devenir rouge.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "audit/TSPE_GEOESPACE_AUTHORED_REVIEW_DEBT_45.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "geoespace_debt", ROOT / "scripts/build_geoespace_authored_review_debt.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def test_the_committed_ledger_matches_the_producer(producer) -> None:
    assert producer.main(["--check"]) == 0


def test_the_ledger_approves_nothing(ledger: dict) -> None:
    """Le seul garde qui compte vraiment."""

    assert ledger["in_approved_baseline"] is False
    assert ledger["release_blocking"] is True
    assert ledger["release_acceptance"] is False
    assert ledger["is_baseline_qualification"] is False
    assert ledger["is_gate_exception"] is False
    assert ledger["human_review_required"] is True

    for entry in ledger["entries"]:
        assert entry["policy_disposition"] == "open_debt"
        assert entry["in_approved_baseline"] is False
        assert entry["release_blocking"] is True
        assert entry["release_acceptance"] is False
        assert entry["human_review_required"] is True

    # Les paquets humains restent non assignes : aucun relecteur n'a ete
    # invente pour rendre le chapitre publiable.
    assert set(ledger["human_review_packets"].values()) == {"PENDING_UNASSIGNED"}


def test_the_lost_human_approvals_stay_visible(ledger: dict) -> None:
    """Perdre une approbation acquise n'est pas ne jamais en avoir eu.

    Cinq objets portaient `status: approved` avant d'etre reecrits. Fondre ces
    cinq lignes dans les quarante autres masquerait une regression assumee :
    une approbation humaine reelle a ete invalidee parce que le contenu qu'elle
    couvrait n'existe plus.
    """

    rewritten = [
        e
        for e in ledger["entries"]
        if e["origin"] == "REWRITTEN_PREVIOUSLY_APPROVED"
    ]
    created = [
        e for e in ledger["entries"] if e["origin"] == "NEW_AUTHORED_UNREVIEWED"
    ]

    assert len(rewritten) == 5
    assert len(created) == 40
    assert len(rewritten) + len(created) == ledger["count"] == 45
    assert ledger["counts_by_origin"] == {
        "NEW_AUTHORED_UNREVIEWED": 40,
        "REWRITTEN_PREVIOUSLY_APPROVED": 5,
    }
    assert ledger["new_fingerprint_set_digest"].startswith("sha256:")
    assert ledger["rewritten_stale_fingerprint_set_digest"].startswith("sha256:")
    assert ledger["rewritten_approval_evidence_chain_complete"] is True

    for entry in rewritten:
        assert entry["status_before_rewrite"] == "approved"
        assert entry["human_approval_invalidated_by_rewrite"] is True
        assert entry["approval_state"] == "STALE"
        assert entry["previous_semantic_digest"].startswith("sha256:")
        assert entry["current_semantic_digest"].startswith("sha256:")
        assert entry["previous_semantic_digest"] != entry["current_semantic_digest"]
        assert entry["semantic_digest_changed"] is True
        assert entry["evidence_chain_complete"] is True
    for entry in created:
        assert entry["status_before_rewrite"] is None
        assert entry["human_approval_invalidated_by_rewrite"] is False
        assert entry["approval_state"] == "NEVER_EXISTED"
        assert entry["historical_source_absent_at_approval_freeze"] is True

    assert sorted(ledger["human_approvals_invalidated"]) == sorted(
        entry["path"] for entry in rewritten
    )


def test_no_entry_is_already_approved(ledger: dict) -> None:
    """Un objet approuve n'a rien a faire dans une dette de revue."""

    for entry in ledger["entries"]:
        assert entry["status"] != "approved", (
            f"{entry['object_id']} est approuve : il ne doit pas figurer ici"
        )


def test_the_debt_is_disjoint_from_the_residual_thirteen(ledger: dict) -> None:
    """Sinon le residuel gele serait dilue par du contenu neuf."""

    residual = json.loads(
        (ROOT / "audit/RESIDUAL_TRUE_NEW_FORENSICS.json").read_text(encoding="utf-8")
    )
    thirteen = {str(entry["fingerprint"]) for entry in residual["entries"]}
    declared = {str(entry["fingerprint"]) for entry in ledger["entries"]}

    assert len(thirteen) == 13
    assert not thirteen & declared
    assert len(declared) == ledger["count"]
