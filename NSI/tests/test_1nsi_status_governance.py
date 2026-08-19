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
    """Gouvernance des statuts sous état PENDING déclaré (clôture A4 §15).

    Le gel de transition (339 objets) est antérieur à la complétion des META
    (A4.1) qui a rendu visibles ~603 objets hérités au statut 'approved'
    (interdit — leur requalification exige une décision humaine, aucune
    promotion/rétrogradation machine). L'état EXACT est figé dans
    audit/1NSI_STATUS_GOVERNANCE_PENDING.json : toute dérive supplémentaire
    (nouvel objet en statut interdit, nouvelle lacune de preuve, changement
    de distribution) échoue. Le NO-GO reste porté par release-strict.
    """
    import hashlib

    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    objects = _objects()
    counts = Counter(meta["status"] for _, meta in objects)

    pending_path = REPOSITORY_ROOT / "audit" / "1NSI_STATUS_GOVERNANCE_PENDING.json"
    pending = json.loads(pending_path.read_text(encoding="utf-8"))
    assert pending["status"] == "PENDING_HUMAN_REVIEW"

    assert len(objects) == pending["objects_total"]
    assert dict(counts) == pending["observed_counts"]
    assert "generated" not in counts

    prohibited = sorted(
        str(path)
        for path, meta in objects
        if meta["status"] in set(policy["prohibited_transitions"])
    )
    # Chemins relatifs au dépôt dans le registre, absolus ici : normaliser.
    prohibited = [
        str(Path(p).relative_to(REPOSITORY_ROOT)) if Path(p).is_absolute() else p
        for p in prohibited
    ]
    assert len(prohibited) == pending["prohibited_status_objects_count"]
    digest = "sha256:" + hashlib.sha256(
        json.dumps(prohibited, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    assert digest == pending["prohibited_status_objects_digest"]

    declared_gaps = {
        (gap["path"], gap["status"], gap["verdict"])
        for gap in pending["evidence_gaps"]
    }
    observed_gaps = set()
    for source, meta in objects:
        verdict = _receipt_verdict(source, meta["id"])
        relative = str(source.relative_to(REPOSITORY_ROOT))
        if meta["status"] == "verified" and verdict != "pass":
            observed_gaps.add((relative, "verified", verdict))
        elif meta["status"] == "manual_review" and verdict != "manual_review":
            observed_gaps.add((relative, "manual_review", verdict))
    assert observed_gaps == declared_gaps, (
        "lacunes de preuve hors de l'état déclaré : "
        f"{sorted(observed_gaps ^ declared_gaps)}"
    )


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
