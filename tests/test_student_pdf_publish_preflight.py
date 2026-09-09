import json
import subprocess
import sys
from pathlib import Path

from scripts import audit_student_pdf_publish_preflight as preflight


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit" / "STUDENT_PDF_PUBLISH_PREFLIGHT.json"


def test_preflight_covers_six_student_variants_and_exposes_current_p0():
    """Le resume doit compter ce que les variantes portent, sur les six manuels.

    Les compteurs de defauts ne sont pas figes : les trois P0 constates le
    23 aout -- quatre documents avec fuite de contenu professeur, quatre sans
    metadonnees, quatre sans navigation -- ont depuis ete corriges, et exiger
    encore la valeur 4 ferait echouer le test SUR LA CORRECTION. Ce qui doit
    tenir est l'accord entre le resume et les variantes, et le fait qu'aucun
    document ne devienne release candidate sans provenance exacte.
    """
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    variants = payload["variants"]
    summary = payload["summary"]
    assert len(variants) == 6
    assert {row["manual"] for row in variants} == {
        "1SPE", "TSPE", "TCOMPL", "TEXPERTES", "1NSI", "TNSI"}

    assert summary["variants_scanned"] == len(variants)
    assert summary["teacher_only_content_leak_documents"] == sum(
        row["teacher_only_content_leak"] > 0 for row in variants)
    assert summary["pdf_metadata_incomplete"] == sum(
        not (row["title"] and row["author"]) for row in variants)
    assert summary["pdf_navigation_missing"] == sum(
        row["bookmark_count"] == 0 for row in variants)

    # Aucune edition eleve ne doit divulguer de contenu professeur.
    assert summary["teacher_only_content_leak_documents"] == 0, [
        row["manual"] for row in variants if row["teacher_only_content_leak"] > 0]

    # Les PDF observes restent construits depuis un commit anterieur.
    assert payload["provenance"]["final_source_sha_match"] is False
    assert summary["release_candidate_eligible"] is False


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
    # Le motif dominant a change quand les fuites ont ete corrigees : ce qui
    # bloque desormais est la provenance. Exiger nommement l'ancien motif
    # rendrait le test rouge pour cause de progres. Le gate doit rester rouge
    # et dire pourquoi, avec un motif declare.
    reasons = {"TEACHER_ONLY_CONTENT_LEAK", "PDF_METADATA_INCOMPLETE",
               "PDF_NAVIGATION_MISSING", "PDF_MISSING", "PROVENANCE_MISMATCH"}
    announced = completed.stdout.strip().removeprefix("PUBLISH PREFLIGHT RED:").strip()
    assert announced, "un gate rouge doit nommer son motif"
    assert {part.strip() for part in announced.split(",")} <= reasons, announced


def test_clean_pdfs_from_a_stale_source_sha_are_never_release_eligible():
    assert not preflight.release_eligible(
        leaks=0,
        metadata=0,
        navigation=0,
        missing=0,
        final_source_sha_match=False,
    )
