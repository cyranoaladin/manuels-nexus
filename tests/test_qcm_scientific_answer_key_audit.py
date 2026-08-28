from __future__ import annotations

import json
from copy import deepcopy
import subprocess
import sys
from pathlib import Path

from scripts import audit_qcm_scientific_answer_keys as qcm_audit


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_qcm_scientific_answer_keys.py"
AUDIT = ROOT / "audit" / "QCM_SCIENTIFIC_ANSWER_KEY_AUDIT.json"
QCM_ROOT = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"


def _source_question_keys() -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for path in sorted(QCM_ROOT.glob("*/qcm/*-QCM.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        chapter = data["chapitre"]
        keys.update((chapter, question["id"]) for question in data["questions"])
    return keys


def test_qcm_scientific_audit_is_complete_and_current() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    rows = audit["questions"]
    observed = {(row["chapter"], row["question_id"]) for row in rows}
    assert observed == _source_question_keys()
    assert audit["summary"]["total_questions"] == len(observed)
    assert audit["summary"]["scientific_zero_claim_authorized"] is False

    q16 = next(
        row
        for row in rows
        if row["chapter"] == "1SPE-SECOND-DEGRE" and row["question_id"] == "Q16"
    )
    assert q16["independent_recalculation"] == "4 * (30 - 2*4) * (20 - 2*4) = 1056"
    assert q16["correct_answer"] == "D"
    assert q16["declared_correct_answer"] == "D"
    assert q16["answer_key_status"] == "PASS"
    assert q16["diagnostic_consistency"] == "PASS"


def test_confirmed_ox_alpha_p0_cluster_is_closed() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    summary = audit["summary"]
    counters = summary["objective_counters"]

    assert summary["independently_recalculated"] == 38
    assert summary["content_review_pending"] == 292
    assert counters["WRONG_ANSWER_KEY"] == 0
    assert counters["MULTIPLE_CORRECT_OPTIONS"] == 0
    assert counters["NO_CORRECT_OPTION"] == 0
    assert counters["INVALID_DISTRACTOR_DIAGNOSTIC"] == 0
    assert summary["known_invalid_distractor_diagnostic_entries"] == 99
    assert summary["questions_with_known_invalid_distractor_diagnostics"] == 33
    assert not [
        (row["chapter"], row["question_id"], row["answer_key_failure"])
        for row in audit["questions"]
        if row["answer_key_status"] == "FAIL"
        or row["diagnostic_consistency"] == "FAIL"
    ]


def _question(chapter: str, question_id: str) -> dict:
    path = next((QCM_ROOT / chapter / "qcm").glob("*-QCM.json"))
    payload = json.loads(path.read_text(encoding="utf-8"))
    return next(item for item in payload["questions"] if item["id"] == question_id)


def test_mutation_primitive_q2_rejects_a_second_true_affine_option() -> None:
    question = deepcopy(_question("TSPE-PRIMITIVES-EQDIFF", "Q2"))
    question["options"]["B"] = "$F-G$ est une fonction affine."
    result = qcm_audit.CHECKERS[("TSPE-PRIMITIVES-EQDIFF", "Q2")](question)

    assert result["answer_key_status"] == "FAIL"
    assert result["answer_key_failure"] == "MULTIPLE_CORRECT_OPTIONS"


def test_mutation_suites_q11_rejects_distractor_diagnostic_mismatch() -> None:
    question = deepcopy(_question("1SPE-SUITES", "Q11"))
    question["options"]["D"] = "$15$"
    result = qcm_audit.CHECKERS[("1SPE-SUITES", "Q11")](question)

    assert result["diagnostic_consistency"] == "FAIL"
    assert "D:OPTION_FRAGMENT_MISSING:$10$" in result["diagnostic_details"]
