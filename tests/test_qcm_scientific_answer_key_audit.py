from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QCM_ROOT = ROOT / "Mathematiques/manuel-maths/chapitres"
AUDIT = ROOT / "audit/QCM_SCIENTIFIC_ANSWER_KEY_AUDIT.json"
BUILDER = ROOT / "scripts/build_qcm_scientific_answer_key_audit.py"
EVIDENCE = ROOT / "audit/qcm_review_evidence"
PARTITIONS = {
    "1SPE": (EVIDENCE / "1SPE_162.json", 162),
    "TSPE": (EVIDENCE / "TSPE_96.json", 96),
    "TCOMPL_TEXPERTES": (EVIDENCE / "TCOMPL_TEXPERTES_73.json", 73),
}


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
    assert payload["summary"]["total_questions"] == 331
    assert payload["summary"]["independently_recalculated"] == 331
    assert payload["summary"]["content_review_pending"] == 0
    assert payload["summary"]["by_manual"] == {
        "1SPE": 162,
        "TCOMPL": 48,
        "TEXPERTES": 25,
        "TSPE": 96,
    }
    assert payload["status"] == "HUMAN_APPROVAL_PENDING_NO_AUTO_APPROVAL"
    assert payload["summary"]["objective_zero_verified"] is True
    assert payload["summary"]["human_approval_complete"] is False
    assert all(value == 0 for value in payload["summary"]["objective_counters"].values())


def test_evidence_partitions_preserve_every_reviewed_row_and_are_current() -> None:
    observed: set[tuple[str, str]] = set()
    for _name, (path, expected_count) in PARTITIONS.items():
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload["questions"]
        assert len(rows) == expected_count
        for row in rows:
            source = ROOT / row["source_path"]
            expected_digest = row.get("source_sha256") or row.get("source_digest")
            assert expected_digest is not None
            assert expected_digest.removeprefix("sha256:") == hashlib.sha256(
                source.read_bytes()
            ).hexdigest()
            key = (row["chapter"], row["question_id"])
            assert key not in observed
            observed.add(key)
    assert observed == _source_keys()


def test_canonical_rows_are_objectively_green_but_not_human_approved() -> None:
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    for row in payload["questions"]:
        assert row["answer_key_status"] == "PASS"
        assert row["unique_correct_option"] == "PASS"
        assert row["diagnostic_consistency"] == "PASS"
        assert row["programme_alignment"] in {"PASS", "MANDATORY_PROGRAMME", "PREREQUISITE"}
        assert row["capacity_alignment"] == "PASS"
        assert row["wrong_programme_year"] is False
        assert row["review_status"] == "HUMAN_APPROVAL_PENDING_NO_AUTO_APPROVAL"


def test_qcm_scientific_audit_builder_is_deterministic() -> None:
    result = subprocess.run(
        [sys.executable, str(BUILDER), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


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
