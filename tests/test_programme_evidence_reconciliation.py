"""Une source, son fragment et ses alias doivent désigner le bon objet."""

import json
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
