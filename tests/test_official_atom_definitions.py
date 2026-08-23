from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEGMENTS_PATH = ROOT / "audit" / "OFFICIAL_SOURCE_SEGMENTS_2026_2027.json"
DEFINITIONS_ROOT = ROOT / "audit" / "official_atom_definitions"
MANUALS = ("1SPE", "TSPE", "TCOMPL", "TEXPERTES", "1NSI", "TNSI")
OBLIGATION_TYPES = {
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


def _payload(manual: str) -> dict:
    return json.loads(
        (DEFINITIONS_ROOT / f"{manual}.json").read_text(encoding="utf-8")
    )


def test_six_direct_source_atom_definition_files_exist() -> None:
    assert {path.stem for path in DEFINITIONS_ROOT.glob("*.json")} == set(MANUALS)


def test_every_official_source_segment_has_exactly_one_reviewed_disposition() -> None:
    source = json.loads(SEGMENTS_PATH.read_text(encoding="utf-8"))
    source_by_manual = {
        manual: {
            segment["segment_id"]: segment
            for segment in source["segments"]
            if segment["manual"] == manual
        }
        for manual in MANUALS
    }

    atom_ids: set[str] = set()
    for manual in MANUALS:
        payload = _payload(manual)
        assert payload["schema_version"] == 1
        assert payload["manual"] == manual
        assert payload["authority_NOR"]
        assert payload["review_method"] == "DIRECT_OFFICIAL_SOURCE_REVIEW"

        dispositions: list[str] = []
        for atom in payload["atoms"]:
            assert atom["atom_id"].startswith(f"{manual}-OFFICIAL-")
            assert atom["atom_id"] not in atom_ids
            atom_ids.add(atom["atom_id"])
            assert atom["obligation_type"] in OBLIGATION_TYPES
            assert atom["mandatory_for_coverage"] in {"YES", "NO"}
            assert atom["mandatory_justification"]
            assert atom["official_section"]
            assert atom["official_anchor"]
            assert atom["short_official_wording_or_paraphrase"]
            assert atom["source_segment_ids"]
            dispositions.extend(atom["source_segment_ids"])

        for item in payload["classified_non_atoms"]:
            assert item["classification"] in OBLIGATION_TYPES
            assert item["mandatory_for_coverage"] == "NO"
            assert item["justification"]
            dispositions.append(item["source_segment_id"])

        assert len(dispositions) == len(set(dispositions)), manual
        assert set(dispositions) == set(source_by_manual[manual]), manual


def test_mandatory_source_segments_cannot_be_discarded_as_non_atoms() -> None:
    source = json.loads(SEGMENTS_PATH.read_text(encoding="utf-8"))
    mandatory = {
        segment["segment_id"]
        for segment in source["segments"]
        if segment["mandatory"] == "YES"
    }
    atomised: set[str] = set()
    non_atoms: set[str] = set()
    for manual in MANUALS:
        payload = _payload(manual)
        for atom in payload["atoms"]:
            if atom["mandatory_for_coverage"] == "YES":
                atomised.update(atom["source_segment_ids"])
        non_atoms.update(
            item["source_segment_id"] for item in payload["classified_non_atoms"]
        )

    assert mandatory <= atomised
    assert not mandatory & non_atoms


def test_no_contractual_atom_denominator_is_hardcoded() -> None:
    builders = (
        ROOT / "scripts" / "build_official_program_atoms.py",
        ROOT / "scripts" / "build_official_source_segments.py",
    )
    for builder in builders:
        source = builder.read_text(encoding="utf-8")
        assert "MANDATORY_CONTRACT_TOTAL" not in source, builder
        assert "== 333" not in source, builder
