from __future__ import annotations

import copy
import contextlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_1spe_suites_wrong_year_p0_forensics.py"
JSON_OUTPUT = ROOT / "audit" / "1SPE_SUITES_WRONG_YEAR_P0_FORENSICS.json"
MD_OUTPUT = ROOT / "audit" / "1SPE_SUITES_WRONG_YEAR_P0_FORENSICS.md"

EXPECTED_LOG_OR_THRESHOLD = {
    "1SPE-SUITES-EX-026",
    "1SPE-SUITES-CO-026",
    "1SPE-SUITES-EX-031",
    "1SPE-SUITES-CO-031",
    "1SPE-SUITES-EX-038",
    "1SPE-SUITES-CO-038",
    "1SPE-SUITES-CO-044",
    "1SPE-SUITES-CO-046",
    "1SPE-SUITES-EX-048",
    "1SPE-SUITES-CO-048",
    "1SPE-SUITES-CO-049",
}
EXPECTED_FORMAL_LIMIT = {
    "1SPE-SUITES-CO-027",
    "1SPE-SUITES-CO-037",
    "1SPE-SUITES-EX-040",
    "1SPE-SUITES-CO-040",
    "1SPE-SUITES-EX-042",
    "1SPE-SUITES-CO-042",
    "1SPE-SUITES-EX-043",
    "1SPE-SUITES-CO-043",
    "1SPE-SUITES-EX-048",
    "1SPE-SUITES-CO-048",
    "1SPE-SUITES-CO-046",
    "1SPE-SUITES-CO-049",
}
EXPECTED_INTERSECTION = {
    "1SPE-SUITES-CO-046",
    "1SPE-SUITES-EX-048",
    "1SPE-SUITES-CO-048",
    "1SPE-SUITES-CO-049",
}
EXPECTED_RENDERED_CLAIM_COUNTS = {
    "1SPE-SUITES-EX-026": 1,
    "1SPE-SUITES-CO-026": 5,
    "1SPE-SUITES-EX-031": 1,
    "1SPE-SUITES-CO-031": 2,
    "1SPE-SUITES-EX-038": 5,
    "1SPE-SUITES-CO-038": 5,
    "1SPE-SUITES-CO-044": 3,
    "1SPE-SUITES-CO-046": 8,
    "1SPE-SUITES-EX-048": 5,
    "1SPE-SUITES-CO-048": 11,
    "1SPE-SUITES-CO-049": 8,
    "1SPE-SUITES-CO-027": 1,
    "1SPE-SUITES-CO-037": 2,
    "1SPE-SUITES-EX-040": 3,
    "1SPE-SUITES-CO-040": 5,
    "1SPE-SUITES-EX-042": 3,
    "1SPE-SUITES-CO-042": 2,
    "1SPE-SUITES-EX-043": 3,
    "1SPE-SUITES-CO-043": 4,
}
EXPECTED_RENDERED_CLAIM_IDS = {
    f"{object_id}-C{index:02d}"
    for object_id, count in EXPECTED_RENDERED_CLAIM_COUNTS.items()
    for index in range(1, count + 1)
}
EXPECTED_OFFICIAL_ATOMS = {
    object_id: [] for object_id in EXPECTED_LOG_OR_THRESHOLD | EXPECTED_FORMAL_LIMIT
}
for _threshold_id in {
    "1SPE-SUITES-EX-026",
    "1SPE-SUITES-CO-026",
    "1SPE-SUITES-EX-038",
    "1SPE-SUITES-CO-038",
    "1SPE-SUITES-CO-046",
    "1SPE-SUITES-EX-048",
    "1SPE-SUITES-CO-048",
}:
    EXPECTED_OFFICIAL_ATOMS[_threshold_id] = ["1SPE-OFFICIAL-063"]
for _intuitive_id in {
    "1SPE-SUITES-CO-037",
    "1SPE-SUITES-EX-040",
    "1SPE-SUITES-CO-040",
    "1SPE-SUITES-EX-043",
    "1SPE-SUITES-CO-043",
}:
    EXPECTED_OFFICIAL_ATOMS[_intuitive_id] = [
        "1SPE-OFFICIAL-053",
        "1SPE-OFFICIAL-059",
    ]


def _producer():
    assert SCRIPT.is_file(), f"producteur absent: {SCRIPT}"
    spec = importlib.util.spec_from_file_location(
        "build_1spe_suites_wrong_year_p0_forensics", SCRIPT
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _codes(payload: dict) -> set[str]:
    return {finding["code"] for finding in payload["findings"]}


def test_canonical_sets_are_the_exact_checkpoint_sets() -> None:
    producer = _producer()
    payload = producer.build_forensics()

    assert set(payload["sets"]["LOG_OR_FORMAL_THRESHOLD_SET"]) == EXPECTED_LOG_OR_THRESHOLD
    assert set(payload["sets"]["FORMAL_LIMIT_CONVERGENCE_SET"]) == EXPECTED_FORMAL_LIMIT
    assert set(payload["sets"]["INTERSECTION"]) == EXPECTED_INTERSECTION
    assert set(payload["sets"]["UNION"]) == EXPECTED_LOG_OR_THRESHOLD | EXPECTED_FORMAL_LIMIT
    assert payload["summary"] == {
        "status": "PASS",
        "log_or_formal_threshold_count": 11,
        "formal_limit_convergence_count": 12,
        "intersection_count": 4,
        "union_count": 19,
        "rendered_claim_count": 77,
        "technical_oracle_count": 19,
        "keep_as_is_count": 43,
        "rewrite_to_1spe_count": 34,
        "optional_terminale_extension_count": 0,
        "delete_invalid_count": 0,
        "unknown": 0,
        "finding_count": 0,
    }


def test_rendered_claim_manifest_is_independently_hard_locked() -> None:
    producer = _producer()
    payload = producer.build_forensics()
    claims = [claim for row in payload["objects"] for claim in row["claims"]]

    assert len(claims) == 77
    assert {claim["claim_id"] for claim in claims} == EXPECTED_RENDERED_CLAIM_IDS
    assert producer.EXPECTED_RENDERED_CLAIM_IDS == EXPECTED_RENDERED_CLAIM_IDS
    assert payload["rendered_claim_manifest_digest"] == (
        "sha256:95bbdd64c260723b71fd97b7fcd14fac401f8cdd55f82bdb9c89f1499a1b1afb"
    )
    assert payload["summary"]["optional_terminale_extension_count"] == 0
    assert all(
        claim["classification"] != "OPTIONAL_TERMINALE_EXTENSION"
        for claim in claims
    )


def test_internal_verifiers_are_non_rendered_technical_oracles() -> None:
    payload = _producer().build_forensics()
    oracles = payload["technical_oracles"]

    assert len(oracles) == 19
    assert {row["object_id"] for row in oracles} == (
        EXPECTED_LOG_OR_THRESHOLD | EXPECTED_FORMAL_LIMIT
    )
    assert all(row["classification"] == "NON_RENDERED_ORACLE_KEEP" for row in oracles)
    assert all("BEGIN-VERIFY" in row["current_oracle"] for row in oracles)
    assert all("END-VERIFY" in row["current_oracle"] for row in oracles)
    co043 = next(row for row in oracles if row["object_id"] == "1SPE-SUITES-CO-043")
    assert "assert limit(u_n, n, oo) == 1000" in co043["current_oracle"]
    for row in payload["objects"]:
        oracle = next(item for item in oracles if item["object_id"] == row["object_id"])
        assert all(claim["line_start"] > oracle["line_end"] for claim in row["claims"])


def test_official_atoms_are_claim_aware_and_exact_per_object() -> None:
    payload = _producer().build_forensics()
    assert {row["object_id"]: row["official_atoms"] for row in payload["objects"]} == (
        EXPECTED_OFFICIAL_ATOMS
    )


def test_every_object_and_claim_is_source_locked_and_fully_classified() -> None:
    producer = _producer()
    payload = producer.build_forensics()
    allowed = {
        "KEEP_AS_IS",
        "REWRITE_TO_1SPE",
        "OPTIONAL_TERMINALE_EXTENSION",
        "DELETE_INVALID",
    }

    assert len(payload["objects"]) == 19
    assert {row["object_id"] for row in payload["objects"]} == (
        EXPECTED_LOG_OR_THRESHOLD | EXPECTED_FORMAL_LIMIT
    )
    for row in payload["objects"]:
        assert {
            "object_id",
            "path",
            "object_type",
            "student_teacher",
            "capacities",
            "official_atoms",
            "source_sha",
            "source_digest",
            "claims",
        } <= row.keys()
        assert row["source_sha"] == producer.PRE_P0_REWRITE_SHA
        assert row["source_digest"].startswith("sha256:")
        assert row["claims"], row["object_id"]
        for claim in row["claims"]:
            assert claim["claim_id"]
            assert 1 <= claim["line_start"] <= claim["line_end"]
            assert claim["line_range"] == f"{claim['line_start']}-{claim['line_end']}"
            assert claim["current_statement_or_reasoning"]
            assert claim["line_digest"].startswith("sha256:")
            assert claim["classification"] in allowed
            assert claim["reason"]
            assert claim["official_authority"]
            assert claim["replacement_strategy"]


@pytest.mark.parametrize("mutation", ("omitted", "extra"))
def test_object_set_mutations_fail_closed(mutation: str) -> None:
    producer = _producer()
    specs = copy.deepcopy(producer.OBJECT_SPECS)
    if mutation == "omitted":
        specs.pop()
    else:
        extra = copy.deepcopy(specs[-1])
        extra["object_id"] = "1SPE-SUITES-EX-999"
        specs.append(extra)

    payload = producer.build_forensics(specs=specs)

    assert payload["summary"]["status"] == "RED"
    assert "OBJECT_SET_MISMATCH" in _codes(payload)


@pytest.mark.parametrize("set_name", ("log", "formal"))
def test_set_overlap_or_union_mutation_fails_closed(set_name: str) -> None:
    producer = _producer()
    log_set = set(producer.LOG_OR_FORMAL_THRESHOLD_SET)
    formal_set = set(producer.FORMAL_LIMIT_CONVERGENCE_SET)
    if set_name == "log":
        log_set.remove("1SPE-SUITES-EX-026")
        log_set.add("1SPE-SUITES-CO-027")
    else:
        formal_set.remove("1SPE-SUITES-CO-027")
        formal_set.add("1SPE-SUITES-EX-026")

    payload = producer.build_forensics(
        log_set=log_set,
        formal_set=formal_set,
    )

    assert payload["summary"]["status"] == "RED"
    assert {"SET_IDENTITY_MISMATCH", "INTERSECTION_MISMATCH"} & _codes(payload)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    (
        ("line_start", 1, "CLAIM_LINE_MISMATCH"),
        ("line_digest", "sha256:" + "0" * 64, "CLAIM_DIGEST_MISMATCH"),
        ("classification", "DELETE_INVALID", "CLAIM_CLASSIFICATION_MISMATCH"),
        ("official_authority", "autorité arbitraire", "CLAIM_AUTHORITY_MISMATCH"),
    ),
)
def test_claim_mutations_fail_closed(field: str, value: object, code: str) -> None:
    producer = _producer()
    specs = copy.deepcopy(producer.OBJECT_SPECS)
    claim = specs[0]["claims"][0]
    claim[field] = value
    if field == "line_start":
        claim["line_end"] = max(int(value), claim["line_end"])

    payload = producer.build_forensics(specs=specs)

    assert payload["summary"]["status"] == "RED"
    assert code in _codes(payload)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    (
        ("reason", "Justification arbitraire.", "CLAIM_REASON_MISMATCH"),
        (
            "replacement_strategy",
            "Stratégie générique sans ancrage.",
            "CLAIM_REPLACEMENT_STRATEGY_MISMATCH",
        ),
        ("line_range", "999-999", "CLAIM_LINE_RANGE_MISMATCH"),
    ),
)
def test_every_mandatory_claim_field_is_digest_locked_and_fails_closed(
    field: str, value: str, code: str
) -> None:
    producer = _producer()
    specs = copy.deepcopy(producer.OBJECT_SPECS)
    specs[0]["claims"][0][field] = value

    payload = producer.build_forensics(specs=specs)

    assert payload["summary"]["status"] == "RED"
    assert code in _codes(payload)
    assert payload["rendered_claim_manifest_digest"] != (
        "sha256:95bbdd64c260723b71fd97b7fcd14fac401f8cdd55f82bdb9c89f1499a1b1afb"
    )


def test_unknown_classification_is_forbidden() -> None:
    producer = _producer()
    specs = copy.deepcopy(producer.OBJECT_SPECS)
    specs[0]["claims"][0]["classification"] = "UNKNOWN"

    payload = producer.build_forensics(specs=specs)

    assert payload["summary"]["status"] == "RED"
    assert payload["summary"]["unknown"] == 1
    assert "UNKNOWN_CLASSIFICATION" in _codes(payload)


def test_historical_source_line_mutation_breaks_both_source_and_claim_locks() -> None:
    producer = _producer()
    canonical = {
        row["path"]: producer._git_source(row["path"])
        for row in producer.OBJECT_SPECS
    }
    first = producer.OBJECT_SPECS[0]
    lines = canonical[first["path"]].splitlines(keepends=True)
    claim = first["claims"][0]
    lines[claim["line_start"] - 1] = lines[claim["line_start"] - 1].replace(
        "100", "101", 1
    )
    canonical[first["path"]] = "".join(lines)

    payload = producer.build_forensics(source_loader=canonical.__getitem__)

    assert payload["summary"]["status"] == "RED"
    assert {"SOURCE_DIGEST_MISMATCH", "CLAIM_DIGEST_MISMATCH"} <= _codes(payload)


def test_whole_object_overclassification_cannot_erase_a_keep_decision() -> None:
    producer = _producer()
    specs = copy.deepcopy(producer.OBJECT_SPECS)
    row = next(item for item in specs if item["object_id"] == "1SPE-SUITES-EX-040")
    assert any(claim["classification"] == "KEEP_AS_IS" for claim in row["claims"])
    for claim in row["claims"]:
        claim["classification"] = "REWRITE_TO_1SPE"

    payload = producer.build_forensics(specs=specs)

    assert payload["summary"]["status"] == "RED"
    assert "WHOLE_OBJECT_OVERCLASSIFICATION" in _codes(payload)


def test_mixed_lines_are_split_and_generic_optional_blanket_fails_closed() -> None:
    producer = _producer()
    payload = producer.build_forensics()
    ex038 = next(row for row in payload["objects"] if row["object_id"] == "1SPE-SUITES-EX-038")
    line34 = [claim for claim in ex038["claims"] if claim["line_range"] == "34-34"]
    assert [claim["classification"] for claim in line34] == [
        "KEEP_AS_IS",
        "REWRITE_TO_1SPE",
        "KEEP_AS_IS",
    ]
    co040 = next(row for row in payload["objects"] if row["object_id"] == "1SPE-SUITES-CO-040")
    line50 = [claim for claim in co040["claims"] if claim["line_range"] == "50-50"]
    assert [claim["classification"] for claim in line50] == [
        "KEEP_AS_IS",
        "REWRITE_TO_1SPE",
    ]

    specs = copy.deepcopy(producer.OBJECT_SPECS)
    for row in specs:
        for claim in row["claims"]:
            if claim["classification"] == "REWRITE_TO_1SPE":
                claim["classification"] = "OPTIONAL_TERMINALE_EXTENSION"
                claim["reason"] = "Contenu de Terminale à conserver en option."
    mutated = producer.build_forensics(specs=specs)
    assert mutated["summary"]["status"] == "RED"
    assert {"OPTIONAL_COUNT_MISMATCH", "CLAIM_CLASSIFICATION_MISMATCH"} & _codes(mutated)


def test_student_teacher_and_pair_buckets_are_exact_and_mutation_safe() -> None:
    producer = _producer()
    payload = producer.build_forensics()

    assert payload["location_buckets"]["physical_source"] == {
        "STUDENT_STATEMENT": 7,
        "TEACHER_CORRECTION": 12,
    }
    assert payload["location_buckets"]["pair_scope"] == {
        "STUDENT_STATEMENT_ONLY": [],
        "CORRECTION_ONLY": [
            "1SPE-SUITES-027",
            "1SPE-SUITES-037",
            "1SPE-SUITES-044",
            "1SPE-SUITES-046",
            "1SPE-SUITES-049",
        ],
        "BOTH": [
            "1SPE-SUITES-026",
            "1SPE-SUITES-031",
            "1SPE-SUITES-038",
            "1SPE-SUITES-040",
            "1SPE-SUITES-042",
            "1SPE-SUITES-043",
            "1SPE-SUITES-048",
        ],
    }

    specs = copy.deepcopy(producer.OBJECT_SPECS)
    specs[0]["student_teacher"] = "TEACHER_CORRECTION"
    mutated = producer.build_forensics(specs=specs)
    assert mutated["summary"]["status"] == "RED"
    assert "STUDENT_TEACHER_BUCKET_MISMATCH" in _codes(mutated)


def test_current_integration_relationship_is_explicit() -> None:
    payload = _producer().build_forensics()
    assert payload["source_freeze"] == {
        "PRE_P0_REWRITE_SHA": "efd544522252c48f50f7e9ede1e1e4c88374bd1e",
        "CURRENT_INTEGRATION_SHA": "10cb5f07772842d6630d2a2f78531f6900371023",
        "relationship": "CURRENT_INTEGRATION_IS_ANCESTOR_OF_PRE_P0_REWRITE",
    }


def test_source_freeze_commits_and_ancestry_are_verified_fail_closed() -> None:
    producer = _producer()
    invalid = producer.build_forensics(pre_sha="f" * 40)
    assert invalid["summary"]["status"] == "RED"
    assert "SOURCE_FREEZE_SHA_INVALID" in _codes(invalid)

    canonical_sources = {
        row["path"]: producer._git_source(row["path"])
        for row in producer.OBJECT_SPECS
    }
    canonical_authorities = {
        path: producer._git_blob(producer.PRE_P0_REWRITE_SHA, path)
        for path in (producer.OFFICIAL_ATOMS_PATH, producer.OFFICIAL_AUTHORITY_PATH)
    }
    reversed_relation = producer.build_forensics(
        pre_sha=producer.CURRENT_INTEGRATION_SHA,
        integration_sha=producer.PRE_P0_REWRITE_SHA,
        source_loader=canonical_sources.__getitem__,
        authority_loader=lambda _sha, path: canonical_authorities[path],
    )
    assert reversed_relation["summary"]["status"] == "RED"
    assert "SOURCE_FREEZE_RELATION_INVALID" in _codes(reversed_relation)


def test_official_authority_sources_and_cited_atom_evidence_are_canonical() -> None:
    producer = _producer()
    payload = producer.build_forensics()

    assert payload["official_authority_sources"] == {
        "source_sha": producer.PRE_P0_REWRITE_SHA,
        "atoms": {
            "path": producer.OFFICIAL_ATOMS_PATH,
            "digest": "sha256:9afb4acfe12a96772496a75aaa09603b48da389897922f5a5e4f9d8ffcac3fcc",
        },
        "authority": {
            "path": producer.OFFICIAL_AUTHORITY_PATH,
            "digest": "sha256:c0dbd04a69c58eca13b9a70c8b1703468aae1da6d9f98b51d20fff5308f3dda7",
        },
    }
    evidence = payload["official_atom_evidence"]
    assert set(evidence) == {
        "1SPE-OFFICIAL-053",
        "1SPE-OFFICIAL-057",
        "1SPE-OFFICIAL-059",
        "1SPE-OFFICIAL-060",
        "1SPE-OFFICIAL-063",
        "TSPE-OFFICIAL-120",
        "TSPE-OFFICIAL-121",
    }
    assert producer._cited_atom_ids(producer.OBJECT_SPECS) <= set(evidence)
    assert all(
        row["manual"] == atom_id.split("-OFFICIAL-")[0]
        for atom_id, row in evidence.items()
    )
    assert all(row["applicable_school_year"] == "2026-2027" for row in evidence.values())
    assert all(row["short_official_wording_or_paraphrase"] for row in evidence.values())

    markdown = producer.render_markdown(payload)
    assert producer.OFFICIAL_ATOMS_PATH in markdown
    assert producer.OFFICIAL_AUTHORITY_PATH in markdown
    assert payload["official_authority_sources"]["atoms"]["digest"] in markdown
    assert payload["official_authority_sources"]["authority"]["digest"] in markdown


def test_bogus_atom_mapping_and_authority_source_mutation_fail_closed() -> None:
    producer = _producer()
    mapping = copy.deepcopy(producer.CLAIM_AWARE_OFFICIAL_ATOMS)
    mapping["1SPE-SUITES-EX-026"].append("1SPE-OFFICIAL-999")
    bogus = producer.build_forensics(atom_map=mapping)
    assert bogus["summary"]["status"] == "RED"
    assert "OFFICIAL_ATOM_NOT_FOUND" in _codes(bogus)

    specs = copy.deepcopy(producer.OBJECT_SPECS)
    specs[0]["claims"][0]["official_authority"] = (
        "MENE2602917A — 1SPE-OFFICIAL-999 : citation introuvable."
    )
    bogus_claim = producer.build_forensics(specs=specs)
    assert bogus_claim["summary"]["status"] == "RED"
    assert "OFFICIAL_ATOM_NOT_FOUND" in _codes(bogus_claim)

    def mutated_source(sha: str, path: str) -> str:
        raw = producer._git_blob(sha, path)
        if path == producer.OFFICIAL_ATOMS_PATH:
            payload = json.loads(raw)
            payload["artifact_name"] = "MUTATED"
            return json.dumps(payload, ensure_ascii=False)
        return raw

    mutated = producer.build_forensics(authority_loader=mutated_source)
    assert mutated["summary"]["status"] == "RED"
    assert "OFFICIAL_AUTHORITY_SOURCE_DIGEST_MISMATCH" in _codes(mutated)

    def mutated_registry(sha: str, path: str) -> str:
        raw = producer._git_blob(sha, path)
        if path == producer.OFFICIAL_AUTHORITY_PATH:
            return raw.replace(
                'official_ref: "MENE2602917A"',
                'official_ref: "BROKEN"',
                1,
            )
        return raw

    bogus_authority = producer.build_forensics(authority_loader=mutated_registry)
    assert bogus_authority["summary"]["status"] == "RED"
    assert "OFFICIAL_AUTHORITY_NOR_MISMATCH" in _codes(bogus_authority)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    (
        ("manual", "BROKEN", "OFFICIAL_ATOM_MANUAL_MISMATCH"),
        ("authority_NOR", "BROKEN", "OFFICIAL_ATOM_NOR_MISMATCH"),
        ("effective_year", "1900-1901", "OFFICIAL_ATOM_YEAR_MISMATCH"),
        ("applicable_school_year", "1900-1901", "OFFICIAL_ATOM_YEAR_MISMATCH"),
        ("short_official_wording_or_paraphrase", "", "OFFICIAL_ATOM_WORDING_INVALID"),
    ),
)
def test_cited_atom_authority_fields_are_validated_without_test_side_copies(
    field: str, value: str, code: str
) -> None:
    producer = _producer()

    def mutated_authority(sha: str, path: str) -> str:
        raw = producer._git_blob(sha, path)
        if path == producer.OFFICIAL_ATOMS_PATH:
            payload = json.loads(raw)
            atom = next(
                row for row in payload["atoms"]
                if row["atom_id"] == "1SPE-OFFICIAL-063"
            )
            atom[field] = value
            return json.dumps(payload, ensure_ascii=False)
        return raw

    payload = producer.build_forensics(authority_loader=mutated_authority)
    assert payload["summary"]["status"] == "RED"
    assert code in _codes(payload)


def test_two_output_commit_rolls_back_after_partial_installation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    producer = _producer()
    json_target = tmp_path / "forensics.json"
    md_target = tmp_path / "forensics.md"
    monkeypatch.setattr(producer, "JSON_OUTPUT", json_target)
    monkeypatch.setattr(producer, "MD_OUTPUT", md_target)
    json_target.write_text("old-json", encoding="utf-8")
    md_target.write_text("old-md", encoding="utf-8")
    calls = 0

    def fail_second_install(source: str | os.PathLike[str], target: str | os.PathLike[str]):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected second-install failure")
        os.replace(source, target)

    with pytest.raises(OSError, match="injected second-install failure"):
        producer.commit_output_bundle(
            {json_target: "new-json", md_target: "new-md"},
            replace_func=fail_second_install,
        )

    assert json_target.read_text(encoding="utf-8") == "old-json"
    assert md_target.read_text(encoding="utf-8") == "old-md"


def test_double_install_and_rollback_failure_preserves_recovery_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    producer = _producer()
    json_target = tmp_path / "forensics.json"
    md_target = tmp_path / "forensics.md"
    monkeypatch.setattr(producer, "JSON_OUTPUT", json_target)
    monkeypatch.setattr(producer, "MD_OUTPUT", md_target)
    old = {json_target: "old-json", md_target: "old-md"}
    for path, content in old.items():
        path.write_text(content, encoding="utf-8")
    real_replace = os.replace
    target_calls = 0

    def fail_install_then_rollback(source, destination):
        nonlocal target_calls
        if Path(destination) in old:
            target_calls += 1
            if target_calls == 1:
                real_replace(source, destination)
                raise RuntimeError("injected install failure")
            if target_calls == 2:
                raise RuntimeError("injected rollback failure")
        real_replace(source, destination)

    with pytest.raises(producer.OutputBundleRecoveryError) as captured:
        producer.commit_output_bundle(
            {json_target: "new-json", md_target: "new-md"},
            replace_func=fail_install_then_rollback,
        )

    error = captured.value
    assert error.recovery_directory.is_dir()
    assert error.rollback_errors
    assert str(error.recovery_directory) in str(error)
    assert {path.read_text(encoding="utf-8") for path in error.recovery_directory.glob("old-*")} == set(old.values())


@pytest.mark.parametrize("interruption", (KeyboardInterrupt, SystemExit))
def test_baseexception_during_installation_rolls_back_cleanly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    interruption: type[BaseException],
) -> None:
    producer = _producer()
    json_target = tmp_path / "forensics.json"
    md_target = tmp_path / "forensics.md"
    monkeypatch.setattr(producer, "JSON_OUTPUT", json_target)
    monkeypatch.setattr(producer, "MD_OUTPUT", md_target)
    old = {json_target: "old-json", md_target: "old-md"}
    for path, content in old.items():
        path.write_text(content, encoding="utf-8")
    real_replace = os.replace
    calls = 0

    def interrupt_second_install(source, destination):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise interruption("injected interruption")
        real_replace(source, destination)

    with pytest.raises(interruption, match="injected interruption"):
        producer.commit_output_bundle(
            {json_target: "new-json", md_target: "new-md"},
            replace_func=interrupt_second_install,
        )

    assert {path: path.read_text(encoding="utf-8") for path in old} == old
    assert set(tmp_path.iterdir()) == set(old)


@pytest.mark.parametrize("extra_count", (0, 2))
def test_commit_rejects_noncanonical_output_cardinality(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, extra_count: int
) -> None:
    producer = _producer()
    json_target = tmp_path / "forensics.json"
    md_target = tmp_path / "forensics.md"
    monkeypatch.setattr(producer, "JSON_OUTPUT", json_target)
    monkeypatch.setattr(producer, "MD_OUTPUT", md_target)
    outputs = {json_target: "json"}
    if extra_count:
        outputs[md_target] = "md"
        outputs[tmp_path / "third.txt"] = "third"

    with pytest.raises(ValueError, match="exactly the canonical JSON and MD"):
        producer.commit_output_bundle(outputs)


def test_check_reads_both_outputs_under_one_shared_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    producer = _producer()
    json_target = tmp_path / "forensics.json"
    md_target = tmp_path / "forensics.md"
    monkeypatch.setattr(producer, "JSON_OUTPUT", json_target)
    monkeypatch.setattr(producer, "MD_OUTPUT", md_target)
    json_target.write_text("json", encoding="utf-8")
    md_target.write_text("md", encoding="utf-8")
    entered: list[Path] = []

    @contextlib.contextmanager
    def observed_lock(path: Path):
        entered.append(path)
        yield

    monkeypatch.setattr(producer, "_shared_lock", observed_lock)
    assert producer.check_output_bundle({json_target: "json", md_target: "md"}) == []
    assert entered == [producer.LOCK_PATH]


def test_shared_check_waits_for_concurrent_exclusive_writer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    producer = _producer()
    json_target = tmp_path / "forensics.json"
    md_target = tmp_path / "forensics.md"
    monkeypatch.setattr(producer, "JSON_OUTPUT", json_target)
    monkeypatch.setattr(producer, "MD_OUTPUT", md_target)
    json_target.write_text("json", encoding="utf-8")
    md_target.write_text("md", encoding="utf-8")
    ready = tmp_path / "ready"
    child = subprocess.Popen(
        [
            sys.executable,
            "-c",
            (
                "import fcntl,pathlib,sys,time; "
                "f=pathlib.Path(sys.argv[1]).open('a+'); "
                "fcntl.flock(f.fileno(),fcntl.LOCK_EX); "
                "pathlib.Path(sys.argv[2]).write_text('ready'); "
                "time.sleep(0.35); f.close()"
            ),
            str(producer.LOCK_PATH),
            str(ready),
        ]
    )
    try:
        for _ in range(100):
            if ready.is_file():
                break
            time.sleep(0.01)
        assert ready.is_file()
        started = time.monotonic()
        assert producer.check_output_bundle({json_target: "json", md_target: "md"}) == []
        assert time.monotonic() - started >= 0.20
    finally:
        child.wait(timeout=3)


def test_cli_has_fixed_repository_outputs_and_check_is_deterministic() -> None:
    assert JSON_OUTPUT.is_file()
    assert MD_OUTPUT.is_file()
    run = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr

    rejected = subprocess.run(
        [sys.executable, str(SCRIPT), "--json-output", str(ROOT / "elsewhere.json")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert rejected.returncode != 0

    payload = json.loads(JSON_OUTPUT.read_text(encoding="utf-8"))
    assert _producer().render_json(payload) == JSON_OUTPUT.read_text(encoding="utf-8")


def test_rendered_and_generated_markdown_have_no_trailing_whitespace() -> None:
    producer = _producer()
    rendered = producer.render_markdown(producer.build_forensics())

    assert all(line == line.rstrip() for line in rendered.splitlines())
    assert "- Atomes officiels : aucun" in rendered
    generated = MD_OUTPUT.read_text(encoding="utf-8")
    assert all(line == line.rstrip() for line in generated.splitlines())
