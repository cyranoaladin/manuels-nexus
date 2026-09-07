"""Les deux banques d'épreuve doivent correspondre à leur plan, pas l'inverse.

Le plan a été déposé avant le moindre sujet. Ces tests vérifient que ce qui a
été écrit lui correspond, et qu'aucune des contraintes du texte officiel n'a
été relâchée en cours de route — en particulier l'indépendance des trois
exercices d'un sujet, qui est la seule que l'écriture pousse naturellement à
enfreindre.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_tnsi_exam_bank_audit as audit  # noqa: E402
import tnsi_exam_bank_blueprint as plan  # noqa: E402

ARTIFACT = ROOT / "audit/TNSI_EXAM_BANK_AUDIT.json"


@pytest.fixture(scope="module")
def payload():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_no_bank_defect(payload) -> None:
    assert payload["summary"]["BANK_DEFECTS"] == 0


def test_the_written_bank_matches_the_official_structure(payload) -> None:
    """Trois exercices indépendants, 3 h 30, selon MENE2516123N."""
    ecrit = plan.AUTHORITY["ecrit"]
    assert payload["authority"]["official_ref"] == "MENE2516123N"
    for subject in payload["subjects"]:
        assert len(subject["exercices"]) == ecrit["exercices"]
        assert subject["duree_totale_min"] == int(ecrit["duree_h"] * 60)
        assert subject["findings"] == []


def test_exercises_of_a_subject_share_no_defined_identifier(payload) -> None:
    """« Indépendants » se vérifie, il ne se déclare pas."""
    for subject in payload["subjects"]:
        assert subject["shared_identifiers"] == [], subject["subject_id"]


def test_a_shared_identifier_would_be_detected() -> None:
    """Le contrôle doit voir une dépendance qu'on lui fabrique."""
    left = "\\subsection*{Énoncé}\n\\begin{python}\ndef commune(x):\n    return x\n\\end{python}"
    right = "\\subsection*{Énoncé}\n\\begin{python}\ndef commune(y):\n    return y\n\\end{python}"
    assert audit.defined_names(left) == {"commune"}
    assert audit.defined_names(left) & audit.defined_names(right) == {"commune"}


def test_the_correction_is_not_read_for_independence() -> None:
    """Un corrigé redéfinit légitimement ce que l'énoncé a introduit."""
    text = (
        "\\subsection*{Énoncé}\n\\begin{python}\nx = 1\n\\end{python}\n"
        "\\subsection*{Corrigé}\n\\begin{python}\ndef seulement_au_corrige():\n    pass\n\\end{python}"
    )
    noms = audit.defined_names(text)
    assert "x" in noms
    assert "seulement_au_corrige" not in noms


def test_every_subject_covers_three_distinct_domains(payload) -> None:
    for subject in payload["subjects"]:
        assert len(set(subject["domains"])) == 3, subject["subject_id"]


def test_every_written_oracle_ran_and_passed(payload) -> None:
    rows = [r for r in payload["written"] if r.get("oracle")]
    assert len(rows) == plan_exercise_count()
    for row in rows:
        assert row["oracle"]["ran"] is True, row["exercise_id"]
        assert row["oracle"]["passed"] is True, row["exercise_id"]


def plan_exercise_count() -> int:
    return sum(len(s["exercices"]) for s in plan.WRITTEN_SUBJECTS)


def test_every_practical_test_passes_from_any_directory(payload) -> None:
    """Une banque qui ne tourne que dans le dépôt ne sert pas en salle."""
    import subprocess

    rows = payload["practical"]
    assert len(rows) == len(plan.PRACTICAL_SITUATIONS)
    for row in rows:
        assert row["oracle"]["passed"] is True, row["situation_id"]
        source = audit.oracle_source(
            (ROOT / row["path"]).read_text(encoding="utf-8")
        )
        ailleurs = subprocess.run(
            [sys.executable, "-c", source], capture_output=True, text=True, cwd="/tmp",
        )
        assert ailleurs.returncode == 0, row["situation_id"]


def test_every_file_carries_the_originality_notice(payload) -> None:
    """Rien ne doit pouvoir passer pour un sujet officiel."""
    for row in payload["written"] + payload["practical"]:
        text = (ROOT / row["path"]).read_text(encoding="utf-8")
        assert "ORIGINAL_NEXUS_TRAINING_MATERIAL_NOT_OFFICIAL_EXAM_CONTENT" in text
        assert "MENE2516123N" in text


def test_the_five_authoring_steps_are_present_everywhere(payload) -> None:
    for row in payload["written"]:
        assert not any(
            f.startswith("MISSING_AUTHORING_STEP") for f in row["findings"]
        ), row["exercise_id"]


def test_the_two_excused_chapters_name_their_reason() -> None:
    assert set(plan.PRACTICAL_NOT_APPLICABLE) == {
        "TNSI-PROJET", "TNSI-HISTOIRE-INFORMATIQUE",
    }
    for reason in plan.PRACTICAL_NOT_APPLICABLE.values():
        assert len(reason) > 80


def test_the_audit_declares_its_freshness(payload) -> None:
    import evidence_freshness as freshness

    assert freshness.assess(payload["freshness"])["FRESHNESS_STATUS"] == \
        freshness.CURRENT
