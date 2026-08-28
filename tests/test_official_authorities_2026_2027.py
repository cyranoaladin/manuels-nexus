from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_PATH = ROOT / "audit" / "OFFICIAL_AUTHORITIES_2026_2027.json"


def test_authorities_separate_programme_exam_and_subject_namespaces() -> None:
    data = json.loads(AUTHORITY_PATH.read_text(encoding="utf-8"))
    assert set(data["namespaces"]) == {
        "PROGRAMME_D_ENSEIGNEMENT",
        "DEFINITION_D_EPREUVE",
        "SUJETS_D_EXAMEN",
    }
    assert set(data["manuals"]) == {
        "1SPE",
        "TSPE",
        "TCOMPL",
        "TEXPERTES",
        "1NSI",
        "TNSI",
    }
    for manual in data["manuals"].values():
        assert set(data["namespaces"]).issubset(manual)
        assert manual["PROGRAMME_D_ENSEIGNEMENT"]["program_authority"] is True
        assert manual["SUJETS_D_EXAMEN"]["program_authority"] is False


def test_sensitive_exam_alignment_values_are_regulatory_not_shorthand() -> None:
    data = json.loads(AUTHORITY_PATH.read_text(encoding="utf-8"))["manuals"]
    first = data["1SPE"]["EXAM_ALIGNMENT"]
    assert first == {
        "duration_minutes": 120,
        "coefficient": 2,
        "calculator": "forbidden",
        "part_1": {"kind": "automatismes_qcm", "points": 6},
        "part_2": {"kind": "2_to_3_independent_exercises", "points": 14},
    }

    tnsi = data["TNSI"]["DEFINITION_D_EPREUVE"]
    assert tnsi["written_raw_scale"] == 20
    assert tnsi["practical_raw_scale"] == 20
    assert tnsi["written_weight"] == 0.75
    assert tnsi["practical_weight"] == 0.25
    assert "written_points" not in tnsi
    assert "practical_points" not in tnsi

    assert data["TCOMPL"]["ASSESSMENT_REGIME"] == "optional_subject_regime"
    assert data["TEXPERTES"]["ASSESSMENT_REGIME"] == "optional_subject_regime"
    assert data["TSPE"]["ASSESSMENT_REGIME"] == "terminal_exam"
