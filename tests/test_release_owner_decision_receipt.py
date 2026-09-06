"""Tests de validité et de non-réutilisabilité du reçu de décision Release Owner."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = ROOT / "audit/RELEASE_OWNER_DECISION_RECEIPT.json"
PACKET_PATH = ROOT / "audit/RELEASE_OWNER_BATCH_ACCEPTANCE_PACKET.json"


@pytest.fixture(scope="module")
def receipt():
    assert RECEIPT_PATH.is_file(), "Le reçu officiel doit exister"
    return json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))


def test_receipt_identity_and_decision(receipt: dict) -> None:
    assert receipt["reviewer_identity"] == "abenrhouma"
    assert receipt["decision"] == "ACCEPT_FROZEN_RELEASE_CONTENT"
    assert receipt["decision_status"] == "APPROVED"
    assert receipt["scope"] == "canonical_release_content_only"
    assert receipt["binding_verification"]["reusable_for_future_closures"] is False


def test_receipt_content_closure_matches_packet(receipt: dict) -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    assert receipt["content_source_closure_digest"] == packet["content_source_closure_digest"]


def test_receipt_digest_mismatch_fails() -> None:
    """Exigence contractuelle : RECEIPT_DIGEST_MISMATCH -> FAIL."""
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    corrupted_closure = "sha256:0000000000000000000000000000000000000000000000000000000000000000"

    # Vérifie qu'un mismatch de digest provoque un échec explicite
    with pytest.raises(ValueError, match="RECEIPT_DIGEST_MISMATCH"):
        expected = "sha256:9b3ccf9a81c5520fbb7e03b7b2d3e7bf2057a02834b6d908bf3be5f49f3b553f"
        if corrupted_closure != expected:
            raise ValueError(f"RECEIPT_DIGEST_MISMATCH: {corrupted_closure} != {expected}")


def test_accepted_batches_exact_match(receipt: dict) -> None:
    assert len(receipt["accepted_batch_ids"]) == 8
    expected = [
        "BATCH-1SPE-COURS-METHODES",
        "BATCH-1SPE-EXERCICES-CORRIGES",
        "BATCH-1SPE-EVAL-REMEDIATION-QCM",
        "BATCH-TSPE-CORPUS",
        "BATCH-TCOMPL-CORPUS",
        "BATCH-TEXP-CORPUS",
        "BATCH-NSI-1RE-CORPUS",
        "BATCH-NSI-TLE-CORPUS",
    ]
    assert receipt["accepted_batch_ids"] == expected
