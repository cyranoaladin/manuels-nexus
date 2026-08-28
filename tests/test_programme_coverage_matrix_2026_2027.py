import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit" / "PROGRAMME_COVERAGE_MATRIX_2026_2027.json"
MANUALS = {"1SPE", "TSPE", "TCOMPL", "TEXPERTES", "1NSI", "TNSI"}


def test_candidate_crosswalk_never_claims_official_matrix_completion():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert set(payload["manuals"]) == MANUALS
    assert payload["summary"]["official_authorities"] == "6/6"
    assert payload["status"] == "REJECTED_AS_PROGRAMME_COVERAGE_MATRIX"
    assert payload["summary"]["programme_coverage_complete"] is False
    assert payload["summary"]["official_atoms_uninventoried"] is True
    assert payload["summary"]["candidate_internal_atoms"] == 312
    assert payload["summary"]["mandatory_missing"] is None
    assert payload["summary"]["unsupported_claim"] == 0
    assert payload["summary"]["out_of_scope_with_proof"] == 3
    assert payload["summary"]["wrong_year"] == 2

    required = {
        "official_document_id",
        "NOR",
        "official_section",
        "official_page_or_anchor",
        "official_wording_or_short_paraphrase",
        "obligation_type",
        "mandatory",
        "manual",
        "chapter",
        "contract_capacity",
        "course_sources",
        "method_sources",
        "exercise_sources",
        "assessment_sources",
        "remediation_sources",
        "coverage_status",
        "evidence_paths",
        "review_status",
    }
    assert all(required <= atom.keys() for atom in payload["atoms"])
    assert all(atom["official_page_or_anchor"].startswith("UNVERIFIED_CANDIDATE:") for atom in payload["atoms"])
    assert all(atom["coverage_status"] != "FULL" for atom in payload["atoms"])
    assert all(atom["review_status"] == "OFFICIAL_ATOM_REDERIVATION_REQUIRED" for atom in payload["atoms"])


def test_exam_or_assessment_alignment_is_present_for_every_manual():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    alignment = payload["exam_or_assessment_alignment"]
    assert set(alignment) == MANUALS
    assert alignment["1SPE"]["calculator"] == "forbidden"
    assert alignment["TNSI"]["written_raw_scale"] == 20
    assert alignment["TNSI"]["practical_raw_scale"] == 20
    assert alignment["TNSI"]["written_weight"] == 0.75
    assert alignment["TNSI"]["practical_weight"] == 0.25
    assert alignment["TCOMPL"]["ASSESSMENT_REGIME"] == "optional_subject_regime"
    assert alignment["TEXPERTES"]["ASSESSMENT_REGIME"] == "optional_subject_regime"


def test_programme_coverage_artifacts_match_generator():
    completed = subprocess.run(
        [sys.executable, "scripts/build_programme_coverage_matrix.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
