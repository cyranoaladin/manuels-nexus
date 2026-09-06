"""Une absence de rubrique n'est excusée que si elle est motivée.

« 5 chapitres sur 7 » ne dit pas s'il manque quelque chose. Un livret de
méthodes n'a pas besoin d'une fiche artificielle dans un chapitre sans
procédure autonome, et une remédiation n'a pas de sens pour un chapitre qui ne
porte qu'un projet. Mais une absence sans verdict motivé reste une lacune :
c'est la règle par défaut, et elle est fail-closed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_auxiliary_rubric_applicability as applicability  # noqa: E402
import build_release_deliverable_readiness as readiness  # noqa: E402


@pytest.fixture(scope="module")
def payload():
    return applicability.build()


def test_an_absence_without_a_verdict_is_a_gap(payload) -> None:
    assert payload["summary"]["UNJUSTIFIED_ABSENCES_ARE_GAPS"] is True
    for record in payload["chapters"]:
        if (record["chapter"], record["rubric"]) not in applicability.VERDICTS:
            assert record["verdict"] == applicability.REAL_GAP, record["chapter"]


def test_every_excused_chapter_carries_its_evidence(payload) -> None:
    for record in payload["chapters"]:
        if record["verdict"] == applicability.REAL_GAP:
            continue
        assert len(record["evidence"]) > 80, record["chapter"]
        assert record["chapter_object_types"], record["chapter"]


def test_the_project_chapter_is_excused_on_its_actual_content(payload) -> None:
    """TNSI-PROJET ne porte ni cours ni exercice : il porte le projet annuel."""
    record = next(
        r for r in payload["chapters"]
        if r["chapter"] == "TNSI-PROJET" and r["rubric"] == "remediation"
    )
    assert record["verdict"] == applicability.NOT_REQUIRED
    assert set(record["chapter_object_types"]) <= {"projet", "qcm"}


def test_the_seven_method_gaps_are_real(payload) -> None:
    """Sept chapitres 1NSI enseignent des procédures sans fiche méthode."""
    gaps = sorted(
        r["chapter"] for r in payload["chapters"]
        if r["rubric"] == "methodes" and r["verdict"] == applicability.REAL_GAP
    )
    assert len(gaps) == 7
    for chapter in gaps:
        record = next(r for r in payload["chapters"] if r["chapter"] == chapter)
        # Un chapitre sans exercice ne réclamerait pas de fiche méthode.
        assert record["chapter_object_types"].get("exercice", 0) > 0, chapter


def test_applicable_chapters_removes_only_excused_ones() -> None:
    chapters = {"TNSI-PROJET", "TNSI-HISTOIRE-INFORMATIQUE", "TNSI-ALGORITHMIQUE"}
    applicable = applicability.applicable_chapters("TNSI", "remediation", chapters)
    assert applicable == {"TNSI-ALGORITHMIQUE"}


def test_an_unknown_rubric_excuses_nothing() -> None:
    chapters = {"TNSI-PROJET", "TNSI-ALGORITHMIQUE"}
    assert applicability.applicable_chapters("TNSI", "evaluations", chapters) == chapters


def test_readiness_uses_applicability_for_booklets_only() -> None:
    """Les manuels ne sont jamais excusés : ils couvrent tous leurs chapitres."""
    payload = readiness.build()
    for row in payload["deliverables"]:
        if row["kind"] != "MANUEL":
            continue
        coverage = row["content_coverage"]
        assert coverage["chapters_covered"] == coverage["chapters_total"], row["deliverable_id"]


def test_tnsi_remediation_is_complete_on_its_applicable_chapters() -> None:
    payload = readiness.build()
    row = next(r for r in payload["deliverables"] if r["deliverable_id"] == "TNSI::remediations")
    assert row["content_coverage"]["chapters_total"] == 5
    assert row["axes"]["content"] is True
