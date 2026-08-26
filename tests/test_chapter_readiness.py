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

    result = chapter_readiness.analyser(chapter, {}, set())

    assert result.objects_total == 1
    assert result.objects_generated == 1
    assert result.objects_reviewed == 0


def test_real_1spe_suites_keeps_all_objects_generated_and_release_blocking(
) -> None:
    result = chapter_readiness.analyser(
        SUITES,
        {"1SPE": "2026"},
        set(),
    )

    assert result.objects_total == 161
    assert result.objects_generated == 161
    assert result.objects_reviewed == 0
    assert result.contract_status == "draft"
    assert "161/161 objets encore au statut generated" in result.blocking_findings
    assert result.release_ready is False
