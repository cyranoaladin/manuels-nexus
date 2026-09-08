"""Une source, son fragment et ses alias doivent désigner le bon objet."""

import json
from copy import deepcopy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_official_program_coverage as coverage
import build_1spe_referential_capacity_closure as closure


def test_existing_source_with_question_fragment_is_not_missing(tmp_path, monkeypatch):
    (tmp_path / "qcm.json").write_text('{"questions": [{"id": "Q3"}]}')
    monkeypatch.setattr(coverage, "ROOT", tmp_path)
    rows = [{"atom_id": "ATOM", "assessment_sources": ["qcm.json#Q3"]}]
    assert coverage._dead_evidence(rows) == []


def test_removed_source_stays_missing_with_its_fragment(tmp_path, monkeypatch):
    monkeypatch.setattr(coverage, "ROOT", tmp_path)
    rows = [{"atom_id": "ATOM", "assessment_sources": ["retired.json#Q3"]}]
    assert coverage._dead_evidence(rows)[0]["path"] == "retired.json#Q3"


def test_local_and_official_alias_join_the_same_second_degree_capacity():
    atoms = closure.official_atoms()
    reference = "1SPE-SECOND-DEGRE-2026-C4"
    assert [a["atom_id"] for a in atoms.get(reference, [])] == ["1SPE-OFFICIAL-074"]


def test_referential_closure_no_longer_loses_existing_second_degree_credits():
    result = closure.build(write=False)
    lost = {r["capacity"] for r in result["capacities_without_direct_atom_credit"]}
    assert "1SPE-SECOND-DEGRE-2026-C4" not in lost
    assert "1SPE-SECOND-DEGRE-2026-D1" not in lost
    assert "1SPE-SECOND-DEGRE-2026-C3" not in lost


def _current_authoritative_rows():
    return [
        row
        for manual in ("TSPE", "TCOMPL", "TEXPERTES")
        for row in json.loads(
            (ROOT / "audit/official_program_coverage" / f"{manual}.json").read_text()
        )["rows"]
    ]


def test_retired_programme_evidence_is_rebound_without_inheriting_its_review():
    rows = _current_authoritative_rows()
    assert coverage._dead_evidence(rows) == []
    reconciled = [r for r in rows if r.get("evidence_reconciliation")]
    assert len(reconciled) == 20
    assert sum(len(r["evidence_reconciliation"]["bindings"]) for r in reconciled) == 23
    for row in reconciled:
        reconciliation = row["evidence_reconciliation"]
        assert reconciliation["review_inheritance"] == "NONE"
        assert reconciliation["human_approval"] is False
        assert row["scientific_state"] == "PENDING"
        assert row["pedagogical_state"] == "PENDING"
        for binding in reconciliation["bindings"]:
            assert binding["semantically_identical"] is False
            assert binding["old_source_disposition"] == "SUPERSEDED_HISTORICAL"
            assert binding["old_source"] not in row["evidence_paths"]


def test_restoring_a_retired_reference_is_detected_by_the_current_gate():
    rows = deepcopy(_current_authoritative_rows())
    assert coverage._dead_evidence(rows) == []
    row = next(r for r in rows if r["atom_id"] == "TCOMPL-OFFICIAL-160")
    retired = (
        "Mathematiques/manuel-maths/chapitres/TCOMPL-TEMPS-ATTENTE/"
        "exercices/TCOMPL-ATT-EX-010.tex"
    )
    row["exercise_sources"] = [retired]
    dead = coverage._dead_evidence(rows)
    assert [(r["atom_id"], r["field"], r["path"]) for r in dead] == [
        ("TCOMPL-OFFICIAL-160", "exercise_sources", retired)
    ]


def test_composed_derivative_gap_is_not_closed_by_a_quotient_remediation():
    row = next(r for r in _current_authoritative_rows()
               if r["atom_id"] == "TCOMPL-OFFICIAL-098")
    assert row["gap_type"] == "PARTIAL_OFFICIAL_CONTENT_COVERAGE"
    assert row["programme_state"] == "PENDING"
    assert row["coverage_status"] != "FULL"
    assert not any("MODELES-FONCTION-RE-C1" in p for p in row["remediation_sources"])
    assert row["exercise_sources"] == []
    assert row["correction_sources"] == []
