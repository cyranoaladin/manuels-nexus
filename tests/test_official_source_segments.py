from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_official_source_segments.py"
REGISTRY = ROOT / "audit" / "OFFICIAL_SOURCE_SEGMENTS_2026_2027.json"
ATOMS = ROOT / "audit" / "OFFICIAL_PROGRAM_ATOMS_2026_2027.json"
MANUALS = {"1SPE", "TSPE", "TCOMPL", "TEXPERTES", "1NSI", "TNSI"}
CLASSIFICATIONS = {
    "CONTENTS",
    "EXPECTED_CAPACITIES",
    "MANDATORY_PROOFS",
    "ALGORITHMS",
    "EXPLICIT_LIMITATIONS",
    "AUTOMATISMS",
    "CROSS_CUTTING_COMPETENCIES",
    "IMPLEMENTATION_GUIDANCE",
    "OPTIONAL_EXTENSIONS",
    "HISTORY_CONTEXT",
    "OTHER_OFFICIAL",
}


def test_official_source_segments_registry_is_current() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_official_source_segments_are_directly_anchored_in_six_authorities() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))

    assert payload["namespace"] == "PROGRAMME_D_ENSEIGNEMENT"
    assert set(payload["source_documents"]) == MANUALS
    assert payload["methodology"]["official_files_are_source"] is True
    assert payload["methodology"]["internal_capacities_are_source"] is False
    assert payload["methodology"]["coverage_matrices_are_source"] is False
    assert payload["methodology"]["mapping_policy"].startswith("fail-closed")
    assert payload["methodology"]["nsi_row_propagation"] is False

    for manual, source in payload["source_documents"].items():
        path = ROOT / source["source_path"]
        assert path.is_file(), (manual, path)
        assert source["authority_NOR"]
        assert source["applicable_school_year"] == "2026-2027"
        assert source["digest"] == f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"
        assert source["digest_matches_authority_registry"] is True

    for segment in payload["segments"]:
        assert segment["manual"] in MANUALS
        assert (ROOT / segment["source_path"]).is_file()
        assert segment["source_anchor"]
        assert segment["source_wording_short"]
        assert segment["classification"] in CLASSIFICATIONS
        if segment["atom_ids"]:
            assert segment["non_atomic_justification"] is None
        elif segment["mandatory"] == "NO":
            assert segment["non_atomic_justification"]
        else:
            assert segment["mapping_review_status"] == "UNMAPPED"
        assert set(segment["atom_ids"]).isdisjoint(segment["candidate_atom_ids"])


def test_official_source_segments_fail_closed_on_current_regulatory_findings() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    atoms_payload = json.loads(ATOMS.read_text(encoding="utf-8"))
    mandatory_atoms = {
        atom["atom_id"]
        for atom in atoms_payload["atoms"]
        if atom["mandatory"] == "YES"
    }
    assert payload["summary"]["mandatory_atoms"] == len(mandatory_atoms)
    assert payload["summary"]["regulatory_status"] == "RED"
    assert payload["summary"]["mapped_mandatory_atoms"] < len(mandatory_atoms)
    assert payload["summary"]["unparsed_mandatory_segments"] > 0
    assert payload["summary"]["duplicate_atoms"] == 3
    assert {
        tuple(group["atom_ids"])
        for group in payload["findings"]["duplicate_atom_groups"]
    } == {
        ("TCOMPL-ATOM-003", "TCOMPL-ATOM-022"),
        ("TCOMPL-ATOM-007", "TCOMPL-ATOM-043"),
        ("TCOMPL-ATOM-021", "TCOMPL-ATOM-042"),
    }
    assert {item["atom_id"] for item in payload["findings"]["false_mandatory_atoms"]} == {
        "TCOMPL-ATOM-017", "TCOMPL-ATOM-018", "TCOMPL-ATOM-019",
        "TCOMPL-ATOM-020", "TCOMPL-ATOM-026", "TCOMPL-ATOM-027",
        "TNSI-ATOM-025",
    }
    assert {item["atom_id"] for item in payload["findings"]["wrong_obligation_types"]} == {
        "1NSI-ATOM-025", "1NSI-ATOM-052",
    }
    assert payload["summary"]["ambiguous_obligations"] == 1
    assert payload["summary"]["compound_atoms"] == 3
    assert payload["summary"]["wrong_year_atoms"] == 0


def test_confirmed_missing_source_units_cannot_be_hidden_by_fuzzy_candidates() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    by_key = {
        (segment["manual"], segment["source_anchor"]): segment
        for segment in payload["segments"]
    }
    required_missing = {
        ("1SPE", "lines:486"),
        ("1SPE", "lines:488"),
        ("1SPE", "lines:643-644"),
        ("1SPE", "lines:646"),
        ("1SPE", "lines:657-659"),
        ("1SPE", "lines:660"),
        ("1SPE", "lines:661"),
        ("1SPE", "lines:662-663"),
        ("1SPE", "lines:664-667"),
        ("TSPE", "lines:355"),
        ("TCOMPL", "lines:167-186"),
        ("TEXPERTES", "lines:343"),
        ("TEXPERTES", "lines:651-655"),
    }
    for key in required_missing:
        assert key in by_key
        assert by_key[key]["mandatory"] == "YES"
        assert by_key[key]["atom_ids"] == []
        assert by_key[key]["mapping_review_status"] == "UNMAPPED"

    sql_capacity = by_key[("TNSI", "pdf-page:6;table:1;row:1;column:capacites;item:2")]
    assert "TNSI-ATOM-025" not in sql_capacity["atom_ids"]


def test_sql_comment_is_split_into_guidance_and_explicit_limitation() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    relevant = {
        segment["source_anchor"]: segment
        for segment in payload["segments"]
        if segment["manual"] == "TNSI" and "part:" in segment["source_anchor"]
    }
    guidance = relevant["pdf-page:6;table:1;row:1;column:commentaires;item:1;part:guidance"]
    limitation = relevant["pdf-page:6;table:1;row:1;column:commentaires;item:1;part:limitation"]
    assert guidance["classification"] == "IMPLEMENTATION_GUIDANCE"
    assert limitation["classification"] == "EXPLICIT_LIMITATIONS"
    assert guidance["mandatory"] == limitation["mandatory"] == "NO"


def test_source_first_population_exposes_a_deleted_mandatory_atom() -> None:
    spec = importlib.util.spec_from_file_location("official_source_segments", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    atoms = json.loads(ATOMS.read_text(encoding="utf-8"))["atoms"]
    baseline = module.build_registry()
    without_project_atom = [
        atom for atom in atoms if atom["atom_id"] != "TNSI-ATOM-060"
    ]

    mutated = module.build_registry(atoms_override=without_project_atom)
    assert [
        (item["segment_id"], item["source_anchor"], item["source_wording_short"])
        for item in baseline["segments"]
    ] == [
        (item["segment_id"], item["source_anchor"], item["source_wording_short"])
        for item in mutated["segments"]
    ]
    unparsed = {
        segment["segment_id"]: segment
        for segment in mutated["segments"]
        if segment["mandatory"] == "YES" and not segment["atom_ids"]
    }

    assert mutated["summary"]["unparsed_mandatory_segments"] >= 1
    assert any(
        segment["manual"] == "TNSI"
        and "quart" in segment["source_wording_short"].casefold()
        for segment in unparsed.values()
    )
