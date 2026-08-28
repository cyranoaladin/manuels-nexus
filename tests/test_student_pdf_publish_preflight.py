import json
import subprocess
import sys
from pathlib import Path

from scripts import audit_student_pdf_publish_preflight as preflight


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit" / "STUDENT_PDF_PUBLISH_PREFLIGHT.json"


def test_preflight_covers_six_student_variants_and_exposes_current_p0():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert len(payload["variants"]) == 6
    assert payload["summary"]["teacher_only_content_leak_documents"] == 4
    assert payload["summary"]["pdf_metadata_incomplete"] == 4
    assert payload["summary"]["pdf_navigation_missing"] == 4
    assert payload["summary"]["release_candidate_eligible"] is False

    nsi = [row for row in payload["variants"] if row["manual"] in {"1NSI", "TNSI"}]
    assert all(row["teacher_only_content_leak"] == 0 for row in nsi)
    assert all(row["title"] and row["author"] and row["bookmark_count"] > 0 for row in nsi)


def test_preflight_artifacts_match_read_only_scan():
    completed = subprocess.run(
        [sys.executable, "scripts/audit_student_pdf_publish_preflight.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_release_gate_is_red_while_current_math_pdfs_are_stale_and_leaking():
    completed = subprocess.run(
        [sys.executable, "scripts/audit_student_pdf_publish_preflight.py", "--gate"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 1
    assert "TEACHER_ONLY_CONTENT_LEAK" in completed.stdout


def test_clean_pdfs_from_a_stale_source_sha_are_never_release_eligible():
    assert not preflight.release_eligible(
        leaks=0,
        metadata=0,
        navigation=0,
        missing=0,
        final_source_sha_match=False,
    )
