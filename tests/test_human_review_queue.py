from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_human_review_queue.py"
ARTIFACT = ROOT / "audit/HUMAN_REVIEW_QUEUE.json"


def _module():
    spec = importlib.util.spec_from_file_location("build_human_review_queue", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_queue_is_exact_disjoint_and_current() -> None:
    payload = _module().build_queue()

    assert payload["status"] == "HUMAN_REVIEW_ACTION_REQUIRED"
    assert payload["approves_nothing"] is True
    assert payload["counts"] == {
        "OBJECT_REVIEW": 2325,
        "QCM_ANSWER_SEMANTICS": 168,
        "QCM_DIAGNOSTIC_RENVOI_SEMANTICS": 41,
        "EDITORIAL_DECISION": 1,
        "TOTAL": 2535,
    }
    assert payload["pairwise_intersections"] == []
    assert payload["unknown_count"] == 0

    all_units: list[str] = []
    for item in payload["items"]:
        assert item["count"] == len(item["unit_ids"]), item["item_id"]
        assert item["set_digest"].startswith("sha256:")
        all_units.extend(item["unit_ids"])
    assert len(all_units) == len(set(all_units)) == payload["counts"]["TOTAL"]

    nsi = {
        item["item_id"]: item
        for item in payload["items"]
        if item["item_id"].startswith("NSI_COUPLED_")
    }
    assert nsi["NSI_COUPLED_NEW_32"]["count"] == 32
    assert nsi["NSI_COUPLED_REWRITTEN_STALE_APPROVAL_4"]["count"] == 4
    assert all(
        item["required_reviewers"] == [
            "EXPERT_NSI",
            "EXPERT_PROGRAMME_PEDAGOGIE",
        ]
        for item in nsi.values()
    )
    allowed_roles = {
        "EXPERT_MATHEMATIQUE",
        "EXPERT_NSI",
        "EXPERT_PROGRAMME_PEDAGOGIE",
    }
    for item in payload["items"]:
        for chapter, roles in item["required_reviewers_by_chapter"].items():
            assert set(roles) <= allowed_roles
            assert len(roles) == 2
            expected = (
                "EXPERT_NSI"
                if chapter.startswith(("1NSI-", "TNSI-"))
                else "EXPERT_MATHEMATIQUE"
            )
            assert roles == [expected, "EXPERT_PROGRAMME_PEDAGOGIE"]


def test_committed_queue_matches_producer() -> None:
    assert json.loads(ARTIFACT.read_text(encoding="utf-8")) == _module().build_queue()


def test_queue_rejects_count_list_divergence_and_duplicate_qcm_identity() -> None:
    module = _module()
    partition = json.loads(
        (ROOT / "audit/CURRENT_REVIEW_DEBT_PARTITION.json").read_text(
            encoding="utf-8"
        )
    )
    evidence = json.loads(
        (ROOT / "audit/QCM_INDEPENDENT_EVIDENCE_V2.json").read_text(
            encoding="utf-8"
        )
    )
    reconciliation = json.loads(
        (ROOT / "audit/QCM_REVIEW_PROOF_RECONCILIATION.json").read_text(
            encoding="utf-8"
        )
    )
    decision = json.loads(
        (ROOT / "audit/TNSI_PROJET_ASSESSMENT_MODE.json").read_text(
            encoding="utf-8"
        )
    )

    broken_partition = copy.deepcopy(partition)
    broken_partition["current_review_debt_count"] += 1
    with pytest.raises(ValueError, match="partition.*count"):
        module.build_queue(
            partition=broken_partition,
            evidence=evidence,
            reconciliation=reconciliation,
            decision=decision,
        )

    broken_evidence = copy.deepcopy(evidence)
    question = next(
        row
        for row in broken_evidence["questions"]
        if row["evidence_status"] == "HUMAN_REVIEW_REQUIRED"
    )
    broken_evidence["questions"].append(copy.deepcopy(question))
    with pytest.raises(ValueError, match="QCM.*dupliquée"):
        module.build_queue(
            partition=partition,
            evidence=broken_evidence,
            reconciliation=reconciliation,
            decision=decision,
        )


def test_queue_fails_closed_on_unknown_or_empty_input_identity() -> None:
    module = _module()
    partition = json.loads(
        (ROOT / "audit/CURRENT_REVIEW_DEBT_PARTITION.json").read_text(
            encoding="utf-8"
        )
    )
    evidence = json.loads(
        (ROOT / "audit/QCM_INDEPENDENT_EVIDENCE_V2.json").read_text(
            encoding="utf-8"
        )
    )
    reconciliation = json.loads(
        (ROOT / "audit/QCM_REVIEW_PROOF_RECONCILIATION.json").read_text(
            encoding="utf-8"
        )
    )
    decision = json.loads(
        (ROOT / "audit/TNSI_PROJET_ASSESSMENT_MODE.json").read_text(
            encoding="utf-8"
        )
    )

    unknown_partition = copy.deepcopy(partition)
    unknown_partition["unknown_count"] = 1
    with pytest.raises(ValueError, match="partition.*unknown"):
        module.build_queue(
            partition=unknown_partition,
            evidence=evidence,
            reconciliation=reconciliation,
            decision=decision,
        )

    unknown_evidence = copy.deepcopy(evidence)
    unknown_evidence["questions"][0]["evidence_status"] = "UNKNOWN"
    with pytest.raises(ValueError, match="statut QCM inconnu"):
        module.build_queue(
            partition=partition,
            evidence=unknown_evidence,
            reconciliation=reconciliation,
            decision=decision,
        )

    empty_identity = copy.deepcopy(evidence)
    empty_identity["questions"][0]["chapter"] = ""
    with pytest.raises(ValueError, match="identité QCM vide"):
        module.build_queue(
            partition=partition,
            evidence=empty_identity,
            reconciliation=reconciliation,
            decision=decision,
        )
