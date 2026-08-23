from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_official_program_atoms.py"
REGISTRY = ROOT / "audit" / "OFFICIAL_PROGRAM_ATOMS_2026_2027.json"
MANUALS = {"1SPE", "TSPE", "TCOMPL", "TEXPERTES", "1NSI", "TNSI"}
ALLOWED_TYPES = {
    "MANDATORY_KNOWLEDGE",
    "MANDATORY_SKILL",
    "MANDATORY_CAPACITY",
    "MANDATORY_ALGORITHM",
    "IMPLEMENTATION_GUIDANCE",
    "OPTIONAL_EXTENSION",
    "HISTORY_CONTEXT",
    "EXPLICIT_LIMITATION",
    "OTHER_EXPLICIT",
}


def test_official_program_atoms_registry_is_current() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_official_program_atoms_have_required_traceability() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    atoms = payload["atoms"]

    assert set(payload["summary"]["by_manual"]) == MANUALS
    assert len({atom["atom_id"] for atom in atoms}) == len(atoms)
    assert {atom["manual"] for atom in atoms} == MANUALS
    for atom in atoms:
        assert atom["authority_NOR"]
        assert atom["official_section"]
        assert atom["official_page_or_anchor"]
        assert atom["short_official_wording_or_paraphrase"]
        assert atom["type"] in ALLOWED_TYPES
        assert atom["mandatory"] in {"YES", "NO"}
        assert atom["effective_year"] in {"2019-2020", "2020-2021", "2026-2027"}
        assert atom["applicable_school_year"] == "2026-2027"
        assert atom["mandatory_justification"]
        assert atom["source_definition_path"] == (
            f"audit/official_atom_definitions/{atom['manual']}.json"
        )
        assert atom["source_segment_ids"]
        assert atom["coverage_status"] == "UNMAPPED"


def test_registry_is_direct_source_and_has_no_wrong_year_or_duplicate_atoms() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 2
    assert payload["methodology"]["official_source_segments_are_authority"] is True
    assert payload["methodology"]["internal_capacities_are_authority"] is False
    assert payload["methodology"]["coverage_matrices_are_authority"] is False
    assert payload["methodology"]["fuzzy_matches_are_proof"] is False
    assert payload["summary"]["wrong_year_atoms"] == 0
    assert payload["summary"]["duplicate_atoms"] == 0


def test_explicit_limitations_are_preserved_without_becoming_mandatory_content() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    limitations = [
        atom for atom in payload["atoms"] if atom["type"] == "EXPLICIT_LIMITATION"
    ]
    assert limitations
    assert all(atom["explicit_limitation"] for atom in limitations)
    assert all(atom["mandatory"] == "NO" for atom in limitations)
