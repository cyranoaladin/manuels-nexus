"""Le registre de la dette écrite par cette branche est dérivé, pas recopié."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_t3_authored_review_debt as producer  # noqa: E402

LEDGER = ROOT / "audit/T3_AUTHORED_REVIEW_DEBT.json"


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def test_the_ledger_grants_nothing(payload) -> None:
    """Un registre d'observation n'approuve rien."""
    assert payload["in_approved_baseline"] is False
    assert payload["is_baseline_qualification"] is False
    assert payload["is_gate_exception"] is False
    assert payload["release_acceptance"] is False
    assert payload["release_blocking"] is True
    assert payload["human_review_required"] is True
    for entry in payload["entries"]:
        assert entry["release_blocking"] is True
        assert entry["in_approved_baseline"] is False
        assert entry["policy_disposition"] == "open_debt"


def test_every_entry_names_a_file_added_by_this_branch(payload) -> None:
    """Le critère d'appartenance est vérifiable, et je le rejoue."""
    added = producer._added_paths(ROOT, payload["baseline_sha"])
    assert added, "la base de branche doit être atteignable"
    for entry in payload["entries"]:
        assert entry["path"] in added, entry
        assert (ROOT / entry["path"]).is_file(), entry


def test_the_count_matches_the_entries(payload) -> None:
    assert payload["count"] == len(payload["entries"])
    fingerprints = [e["fingerprint"] for e in payload["entries"]]
    assert len(set(fingerprints)) == len(fingerprints)
    assert sum(payload["counts_by_role"].values()) == payload["count"]
    assert sum(payload["counts_by_chapter"].values()) == payload["count"]


def test_the_ledger_is_disjoint_from_the_others(payload) -> None:
    """Une même empreinte déclarée deux fois se compterait deux fois."""
    elsewhere = producer._declared_elsewhere(ROOT)
    mine = {e["fingerprint"] for e in payload["entries"]}
    assert mine.isdisjoint(elsewhere)


def test_a_file_that_predates_the_branch_would_not_enter(payload) -> None:
    """Le critère exclut ce qui existait avant, même en dette.

    Sans cette borne, le registre absorberait la dette héritée et la ferait
    passer pour une nouveauté déclarée de cette branche.
    """
    anciens = subprocess.run(
        ["git", "diff", "--diff-filter=M", "--name-only",
         f"{payload['baseline_sha']}..HEAD"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()
    modifies = {p for p in anciens if p.endswith(".tex")}
    inscrits = {e["path"] for e in payload["entries"]}
    assert inscrits.isdisjoint(modifies), sorted(inscrits & modifies)


def test_the_producer_reproduces_the_deposited_ledger() -> None:
    """Un registre recopié à la main divergerait de son producteur."""
    rebuilt = producer.build()
    deposited = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert rebuilt["fingerprint_set_digest"] == deposited["fingerprint_set_digest"]
    assert rebuilt["paths_digest"] == deposited["paths_digest"]
    assert rebuilt["count"] == deposited["count"]
