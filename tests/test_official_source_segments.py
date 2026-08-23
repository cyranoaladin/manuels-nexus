from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_official_source_segments.py"
REGISTRY = ROOT / "audit" / "OFFICIAL_SOURCE_SEGMENTS_2026_2027.json"
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
    assert payload["methodology"]["atom_registry_dependency"] is False
    assert payload["methodology"]["fuzzy_mapping"] is False

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
        assert segment["mandatory"] in {"YES", "NO"}
        assert "atom_ids" not in segment
        assert "candidate_atom_ids" not in segment


def test_official_source_segments_are_a_pure_reviewed_population() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    segments = payload["segments"]

    assert payload["schema_version"] == 3
    assert payload["summary"]["source_extraction_status"] == "REVIEWED"
    assert payload["summary"]["source_segments"] == len(segments)
    assert payload["summary"]["mandatory_source_segments"] == sum(
        segment["mandatory"] == "YES" for segment in segments
    )
    assert "findings" not in payload


def test_confirmed_regulatory_units_are_present_without_fuzzy_mapping() -> None:
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


def test_reviewed_1spe_mandatory_blocks_are_extracted_source_first() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    by_key = {
        (segment["manual"], segment["source_anchor"]): segment
        for segment in payload["segments"]
    }
    expected = {
        # Vocabulaire ensembliste et logique.
        "lines:195-201": "CONTENTS",
        "lines:203": "EXPECTED_CAPACITIES",
        "lines:204": "EXPECTED_CAPACITIES",
        "lines:205": "EXPECTED_CAPACITIES",
        "lines:206": "EXPECTED_CAPACITIES",
        "lines:207": "EXPECTED_CAPACITIES",
        "lines:208": "EXPECTED_CAPACITIES",
        "lines:209-210": "EXPECTED_CAPACITIES",
        "lines:211": "EXPECTED_CAPACITIES",
        "lines:212-213": "EXPECTED_CAPACITIES",
        # Automatismes au-delà du seul bloc « Évolutions et variations ».
        "lines:268": "AUTOMATISMS",
        "lines:269": "AUTOMATISMS",
        "lines:270": "AUTOMATISMS",
        "lines:273": "AUTOMATISMS",
        "lines:274": "AUTOMATISMS",
        "lines:275": "AUTOMATISMS",
        "lines:276": "AUTOMATISMS",
        "lines:277": "AUTOMATISMS",
        "lines:280-281": "AUTOMATISMS",
        "lines:282": "AUTOMATISMS",
        "lines:283": "AUTOMATISMS",
        "lines:286-287": "AUTOMATISMS",
        "lines:288": "AUTOMATISMS",
        # Dérivation — contenus, et pas seulement capacités/démonstrations.
        "lines:435": "CONTENTS",
        "lines:436": "CONTENTS",
        "lines:437-438": "CONTENTS",
        "lines:439": "CONTENTS",
        "lines:441": "CONTENTS",
        "lines:442": "CONTENTS",
        "lines:443": "CONTENTS",
        "lines:444": "CONTENTS",
        "lines:445": "CONTENTS",
    }
    for anchor, classification in expected.items():
        segment = by_key[("1SPE", anchor)]
        assert segment["classification"] == classification
        assert segment["mandatory"] == "YES"

    framework = by_key[("1SPE", "lines:192-194")]
    assert framework["classification"] == "IMPLEMENTATION_GUIDANCE"
    assert framework["mandatory"] == "NO"


def test_reviewed_tspe_combinatorics_and_logic_blocks_are_extracted_source_first() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    by_key = {
        (segment["manual"], segment["source_anchor"]): segment
        for segment in payload["segments"]
    }
    expected_mandatory = {
        "lines:204-205": "EXPECTED_CAPACITIES",
        "lines:206-208": "EXPECTED_CAPACITIES",
        "lines:259-262": "CONTENTS",
        "lines:989-995": "CONTENTS",
        "lines:1009-1010": "EXPECTED_CAPACITIES",
        "lines:1011": "EXPECTED_CAPACITIES",
        "lines:1012-1013": "EXPECTED_CAPACITIES",
        "lines:1014": "EXPECTED_CAPACITIES",
        "lines:1015-1016": "EXPECTED_CAPACITIES",
        "lines:1017": "EXPECTED_CAPACITIES",
        "lines:1018-1019": "EXPECTED_CAPACITIES",
        "lines:1020": "EXPECTED_CAPACITIES",
        "lines:1021": "EXPECTED_CAPACITIES",
        "lines:1022": "EXPECTED_CAPACITIES",
        "lines:1023": "EXPECTED_CAPACITIES",
    }
    for anchor, classification in expected_mandatory.items():
        segment = by_key[("TSPE", anchor)]
        assert segment["classification"] == classification
        assert segment["mandatory"] == "YES"

    for anchor, classification in {
        "lines:985-988": "IMPLEMENTATION_GUIDANCE",
        "lines:996-1004": "IMPLEMENTATION_GUIDANCE",
        "lines:1005-1007": "EXPLICIT_LIMITATIONS",
    }.items():
        segment = by_key[("TSPE", anchor)]
        assert segment["classification"] == classification
        assert segment["mandatory"] == "NO"


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
