"""Verrouille la gouvernance des statuts 1NSI sans auto-approbation."""

import json
import re
from collections import Counter
from pathlib import Path

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
NSI_ROOT = REPOSITORY_ROOT / "NSI"
POLICY_PATH = REPOSITORY_ROOT / "audit" / "1NSI_STATUS_GOVERNANCE.yaml"
META = re.compile(r"% META: (\{.*\})")


def _objects() -> list[tuple[Path, dict]]:
    objects = []
    for path in sorted((NSI_ROOT / "chapitres").glob("1NSI-*/**/*.tex")):
        match = META.search(path.read_text(encoding="utf-8"))
        if match:
            objects.append((path, json.loads(match.group(1))))
    return objects


def _receipt_verdict(source: Path, object_id: str) -> str | None:
    receipt = source.parents[1] / "validations" / f"{object_id}.execution.json"
    if not receipt.is_file():
        return None
    return json.loads(receipt.read_text(encoding="utf-8"))["verdict"]


def test_1nsi_object_statuses_follow_execution_evidence() -> None:
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    objects = _objects()
    counts = Counter(meta["status"] for _, meta in objects)

    assert len(objects) == 339
    assert counts == policy["expected_final"]["objects"]
    assert not (set(counts) & set(policy["prohibited_transitions"]))
    assert "generated" not in counts

    for source, meta in objects:
        verdict = _receipt_verdict(source, meta["id"])
        if meta["status"] == "verified":
            assert verdict == "pass", source
        elif meta["status"] == "manual_review":
            assert verdict == "manual_review", source


def test_1nsi_contracts_remain_pending_human_approval() -> None:
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    statuses = Counter()
    for path in sorted((NSI_ROOT / "chapitres").glob("1NSI-*/contrat.yaml")):
        contract = yaml.safe_load(path.read_text(encoding="utf-8"))
        statuses[contract["statut"]] += 1

    assert statuses == policy["expected_final"]["contracts"]
    assert policy["decision"]["publication_approval"] is False
    assert policy["decision"]["release_acceptance"] is False
    assert policy["expected_final"]["blocking_statuses"] == 349
