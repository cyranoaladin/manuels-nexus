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
        assert atom["official_page_or_anchor"].startswith("section:")
        assert atom["short_official_wording_or_paraphrase"]
        assert atom["type"] in ALLOWED_TYPES
        assert atom["mandatory"] in {"YES", "NO"}
        assert atom["effective_year"] in {"2019-2020", "2020-2021", "2026-2027"}
        assert atom["applicable_school_year"] == "2026-2027"
        assert atom["source_matrix_path"].startswith("audit/PROGRAM_COVERAGE_MATRIX_")
        assert atom["source_matrix_row_id"]


def test_internal_findings_are_not_rehabilitated_as_official_atoms() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    atoms = payload["atoms"]

    assert not [
        atom
        for atom in atoms
        if atom["source_coverage_status"]
        in {"AUDIT_METADATA_ONLY", "WRONG_YEAR", "UNSUPPORTED_CLAIM"}
    ]
    assert payload["summary"]["excluded_internal_findings"] == 11


def test_embedded_explicit_limitation_is_preserved_on_mandatory_atom() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    atom = next(item for item in payload["atoms"] if item["atom_id"] == "1SPE-ATOM-008")

    assert atom["source_coverage_status"] == "CONTENT_REVIEW_PENDING"
    assert atom["explicit_limitation"] == "Toute formalisation de la notion de limite est exclue."
