from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATOMS_PATH = ROOT / "audit" / "OFFICIAL_PROGRAM_ATOMS_2026_2027.json"
MATRIX_ROOT = ROOT / "audit" / "official_program_coverage"
MANUALS = ("1SPE", "TSPE", "TCOMPL", "TEXPERTES", "1NSI", "TNSI")
STATES = {
    "UNMAPPED",
    "STRUCTURALLY_MAPPED",
    "CONTENT_REVIEW_PENDING",
    "SCIENTIFIC_PASS",
    "PEDAGOGICAL_PASS",
    "FULL",
}
SOURCE_FIELDS = (
    "course_sources",
    "method_sources",
    "exercise_sources",
    "correction_sources",
    "assessment_sources",
    "remediation_sources",
)


def _rows() -> list[dict]:
    return [
        row
        for manual in MANUALS
        for row in json.loads(
            (MATRIX_ROOT / f"{manual}.json").read_text(encoding="utf-8")
        )["rows"]
    ]


def test_six_current_official_programme_matrices_exist() -> None:
    assert {path.stem for path in MATRIX_ROOT.glob("*.json")} == set(MANUALS)


def test_every_mandatory_atom_has_exactly_one_coverage_row() -> None:
    atoms = json.loads(ATOMS_PATH.read_text(encoding="utf-8"))["atoms"]
    mandatory_ids = {
        atom["atom_id"] for atom in atoms if atom["mandatory"] == "YES"
    }
    rows = _rows()

    assert len(rows) == len(mandatory_ids)
    assert {row["atom_id"] for row in rows} == mandatory_ids
    assert len({row["atom_id"] for row in rows}) == len(rows)


def test_coverage_rows_are_traceable_and_do_not_fake_full() -> None:
    atoms = {
        atom["atom_id"]: atom
        for atom in json.loads(ATOMS_PATH.read_text(encoding="utf-8"))["atoms"]
    }
    for row in _rows():
        atom = atoms[row["atom_id"]]
        assert row["official_document_id"] == atom["atom_id"]
        assert row["NOR"] == atom["authority_NOR"]
        assert row["official_section"] == atom["official_section"]
        assert row["official_page_or_anchor"] == atom["official_page_or_anchor"]
        assert row["official_wording_or_short_paraphrase"] == atom[
            "short_official_wording_or_paraphrase"
        ]
        assert row["obligation_type"] == atom["type"]
        assert row["mandatory"] == "YES"
        assert row["manual"] == atom["manual"]
        assert row["coverage_status"] in STATES
        assert row["review_status"] in {
            "NOT_REVIEWED",
            "PROGRAM_REVIEWED",
            "SCIENTIFIC_REVIEWED",
            "PEDAGOGICAL_REVIEWED",
            "HUMAN_APPROVAL_PENDING",
        }
        assert row["programme_state"] in {"PASS", "PENDING"}
        assert row["scientific_state"] in {"PASS", "PENDING"}
        assert row["pedagogical_state"] in {"PASS", "PENDING"}
        assert row["assessment_alignment_state"] in {"PASS", "PENDING"}

        if row["coverage_status"] != "UNMAPPED":
            assert row["chapter"]
            assert row["contract_capacity"]
            for field in SOURCE_FIELDS:
                assert row[field], (row["atom_id"], field)
            assert row["evidence_paths"]
            for relative in row["evidence_paths"]:
                assert (ROOT / relative).exists(), (row["atom_id"], relative)

        if row["coverage_status"] == "FULL":
            assert row["programme_state"] == "PASS"
            assert row["scientific_state"] == "PASS"
            assert row["pedagogical_state"] == "PASS"
            assert row["assessment_alignment_state"] == "PASS"
