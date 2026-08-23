from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QCM_ROOT = ROOT / "Mathematiques/manuel-maths/chapitres"
AUDIT = ROOT / "audit/QCM_SCIENTIFIC_ANSWER_KEY_AUDIT.json"


def _sources() -> list[Path]:
    return sorted(QCM_ROOT.glob("*/qcm/*-QCM.json"))


def _source_keys() -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for path in _sources():
        payload = json.loads(path.read_text(encoding="utf-8"))
        keys.update((payload["chapitre"], question["id"]) for question in payload["questions"])
    return keys


def _source_digest() -> str:
    digest = hashlib.sha256()
    for path in _sources():
        relative = path.relative_to(ROOT)
        digest.update(str(relative).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def test_qcm_scientific_audit_inventory_and_digest_are_current() -> None:
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    rows = payload["questions"]

    assert {(row["chapter"], row["question_id"]) for row in rows} == _source_keys()
    assert payload["qcm_source_digest"] == _source_digest()
    assert payload["summary"]["total_questions"] == 330
    assert payload["summary"]["independently_recalculated"] == 109
    assert payload["summary"]["content_review_pending"] == 221
    assert payload["summary"]["scientific_zero_claim_authorized"] is False


def test_three_requested_false_greens_are_closed_in_current_audit() -> None:
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    rows = {
        (row["chapter"], row["question_id"]): row for row in payload["questions"]
    }
    for key in (
        ("1SPE-SECOND-DEGRE", "Q16"),
        ("TSPE-PRIMITIVES-EQDIFF", "Q2"),
        ("1SPE-SUITES", "Q11"),
    ):
        assert rows[key]["answer_key_status"] == "PASS"
        assert rows[key]["unique_correct_option"] == "PASS"
        assert rows[key]["diagnostic_consistency"] == "PASS"
