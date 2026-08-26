from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "chapter_readiness.py"
SPEC = importlib.util.spec_from_file_location("chapter_readiness", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
chapter_readiness = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = chapter_readiness
SPEC.loader.exec_module(chapter_readiness)

SUITES = (
    ROOT
    / "Mathematiques"
    / "manuel-maths"
    / "chapitres"
    / "1SPE-SUITES"
)
BUILD_MANIFEST = ROOT / "audit" / "BUILD_MANIFEST.json"


def test_qcm_meta_is_counted_without_promoting_generated_status(
    tmp_path: Path,
) -> None:
    chapter = tmp_path / "1SPE-TEST-QCM"
    qcm = chapter / "qcm"
    qcm.mkdir(parents=True)
    (qcm / "1SPE-TEST-QCM-QCM.tex").write_text(
        "% META: "
        + json.dumps(
            {
                "id": "1SPE-TEST-QCM-QCM",
                "chapitre": "1SPE-TEST-QCM",
                "type_objet": "qcm",
                "status": "generated",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (qcm / "1SPE-TEST-QCM-QCM.json").write_text(
        json.dumps({"questions": []}) + "\n",
        encoding="utf-8",
    )

    result = chapter_readiness.analyser(chapter, {}, {})

    assert result.objects_total == 1
    assert result.objects_generated == 1
    assert result.objects_reviewed == 0


def test_real_1spe_suites_keeps_all_objects_generated_and_release_blocking(
) -> None:
    result = chapter_readiness.analyser(
        SUITES,
        {"1SPE": "2026"},
        {},
    )

    assert result.objects_total == 161
    assert result.objects_generated == 161
    assert result.objects_reviewed == 0
    assert result.contract_status == "draft"
    assert "161/161 objets encore au statut generated" in result.blocking_findings
    assert result.release_ready is False


def test_present_pdfs_without_observed_manifest_builds_are_not_ready() -> None:
    manifest = json.loads(BUILD_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["builds"] == []
    assert (
        ROOT
        / "Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf"
    ).is_file()
    assert (
        ROOT
        / "Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf"
    ).is_file()

    result = next(
        chapter
        for chapter in chapter_readiness.collecter()
        if chapter.chapter_id == "1SPE-SUITES"
    )

    assert result.student_build is False
    assert result.teacher_build is False


def test_canonical_observed_build_variants_enable_only_exact_variant() -> None:
    student = chapter_readiness.analyser(
        SUITES,
        {"1SPE": "2026"},
        {"1SPE": {"eleve"}},
    )
    teacher = chapter_readiness.analyser(
        SUITES,
        {"1SPE": "2026"},
        {"1SPE": {"professeur"}},
    )

    assert student.student_build is True
    assert student.teacher_build is False
    assert teacher.student_build is False
    assert teacher.teacher_build is True
