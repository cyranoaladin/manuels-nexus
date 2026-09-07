"""Les trois requalifications ADGK sont liées à leurs preuves, ou refusées.

La décision humaine est explicite : « si le digest pédagogique de l'un de ces
trois objets diffère de celui soumis aux tests, ne pas requalifier cet objet ».
Ces tests vérifient que le lien est mécanique et qu'il se casse quand il doit.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_adgk_requalification_receipts as adgk  # noqa: E402

ARTIFACT = ROOT / "audit/ADGK_REQUALIFICATION_RECEIPTS.json"
DISPOSITIONS = ROOT / "audit/ANOMALY_DISPOSITIONS.yaml"


@pytest.fixture(scope="module")
def payload():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_one_receipt_per_object_never_a_batch(payload) -> None:
    """Ces trois changements sont pédagogiques : les batcher les effacerait."""
    ids = [r["OBJECT_ID"] for r in payload["receipts"]]
    assert sorted(ids) == [
        "1NSI-ADGK-ME-001", "1NSI-ADGK-ME-002", "1NSI-ADGK-ME-003",
    ]
    assert len(set(ids)) == 3


def test_every_receipt_carries_the_named_fields(payload) -> None:
    exiges = {
        "OBJECT_ID", "CURRENT_PEDAGOGICAL_CONTENT_DIGEST",
        "PREVIOUS_QUALIFICATION_DIGEST", "SCIENTIFIC_EVIDENCE_DIGEST",
        "REGRESSION_TEST_DIGEST", "REVIEWER_IDENTITY",
    }
    for receipt in payload["receipts"]:
        assert exiges <= set(receipt), receipt["OBJECT_ID"]
        assert receipt["REVIEWER_IDENTITY"] == "abenrhouma"
        for champ in exiges - {"OBJECT_ID", "REVIEWER_IDENTITY"}:
            assert receipt[champ], (receipt["OBJECT_ID"], champ)


def test_the_content_digest_matches_the_file_on_disk(payload) -> None:
    """La réserve de la décision, appliquée : contenu != testé -> pas de receipt."""
    for receipt in payload["receipts"]:
        courant = "sha256:" + hashlib.sha256(
            (ROOT / receipt["source"]).read_bytes()
        ).hexdigest()
        assert receipt["CURRENT_PEDAGOGICAL_CONTENT_DIGEST"] == courant


def test_the_regression_digest_matches_the_test_file(payload) -> None:
    attendu = "sha256:" + hashlib.sha256(
        (ROOT / payload["regression_tests"]).read_bytes()
    ).hexdigest()
    for receipt in payload["receipts"]:
        assert receipt["REGRESSION_TEST_DIGEST"] == attendu


def test_the_regression_suite_actually_passed(payload) -> None:
    assert payload["regression_passed"] is True
    assert payload["summary"]["REFUSED"] == 0


def test_a_changed_file_would_be_refused(monkeypatch, tmp_path) -> None:
    """Preuves en échec -> aucun receipt éligible."""
    monkeypatch.setattr(adgk, "_run_regression", lambda: (False, "1 failed"))
    verdict = adgk.build("abenrhouma")
    assert verdict["summary"]["ELIGIBLE"] == 0
    assert verdict["summary"]["REFUSED"] == 3
    for receipt in verdict["receipts"]:
        assert any("régression" in r for r in receipt["refus"])


def test_the_greedy_scope_limit_is_recorded(payload) -> None:
    """Le contre-exemple ne doit jamais être élargi : la limite est écrite."""
    glouton = next(
        r for r in payload["receipts"] if r["OBJECT_ID"] == "1NSI-ADGK-ME-002"
    )
    assert glouton["scope_limit"]
    assert "optimalité générale" in glouton["scope_limit"]
    assert "{1,3,4}" in glouton["scope_limit"]


def test_no_status_was_promoted(payload) -> None:
    """Requalifier ne promeut rien : les trois restent `needs_review`."""
    assert payload["promotes_no_status"] is True
    for receipt in payload["receipts"]:
        meta_line = (ROOT / receipt["source"]).read_text(
            encoding="utf-8"
        ).split("\n", 1)[0]
        meta = json.loads(meta_line.split("% META:", 1)[1])
        assert meta["status"] == "needs_review", receipt["OBJECT_ID"]


def test_each_disposition_keeps_its_previous_digest(payload) -> None:
    records = yaml.safe_load(DISPOSITIONS.read_text(encoding="utf-8"))["dispositions"]
    for receipt in payload["receipts"]:
        record = records[receipt["fingerprint"]]
        requal = record["requalification"]
        assert requal["change_class"] == "SUBSTANTIVE_CHANGE"
        assert requal["reviewer_identity"] == "abenrhouma"
        assert requal["regression_test_digest"] == receipt["REGRESSION_TEST_DIGEST"]
        assert record["method_source_sha"] == \
            receipt["CURRENT_PEDAGOGICAL_CONTENT_DIGEST"].removeprefix("sha256:")


def test_no_stale_qualification_remains_beyond_the_governance_conflict() -> None:
    """Il ne doit rester que les trois TRIGO, qui relèvent d'une autre décision."""
    import inventory_collection as ic

    restantes = ic.invalid_qualifications(ROOT)
    assert {e["fingerprint"] for e in restantes} == {
        "70dfcb9ea3d7e1ec", "baf25a2d0a53d6dc", "dc0025fc58dc2e34",
    }
