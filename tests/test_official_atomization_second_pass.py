from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_official_atomization_second_pass.py"
SOURCE_SEGMENTS = ROOT / "audit" / "OFFICIAL_SOURCE_SEGMENTS_2026_2027.json"
FIRST_PASS_ATOMS = ROOT / "audit" / "OFFICIAL_PROGRAM_ATOMS_2026_2027.json"
AUTHORITY = ROOT / "audit" / "OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml"
SEGMENT_LEDGER = ROOT / "audit" / "OFFICIAL_SOURCE_SEGMENT_LEDGER.json"
SECOND_PASS = ROOT / "audit" / "OFFICIAL_ATOMIZATION_SECOND_PASS.json"
FINDING_CODES = {
    "MANDATORY_SEGMENT_UNREPRESENTED",
    "PHANTOM_ATOM",
    "PHANTOM_NON_ATOM_DISPOSITION",
    "DUPLICATE_ATOM",
    "AMBIGUOUS_ATOM",
    "WRONG_YEAR_ATOM",
    "MANDATORY_CLASSIFICATION_DISAGREEMENT",
    "ATOM_MANUAL_DISAGREEMENT",
    "ATOM_TYPE_DISAGREEMENT",
    "ATOM_WORDING_DISAGREEMENT",
    "ATOM_JUSTIFICATION_DISAGREEMENT",
    "NON_ATOM_MANUAL_DISAGREEMENT",
    "NON_ATOM_CLASSIFICATION_DISAGREEMENT",
    "NON_ATOM_MANDATORY_DISAGREEMENT",
    "NON_ATOM_JUSTIFICATION_DISAGREEMENT",
}
EXPECTED_BY_MANUAL = {
    "1SPE": {"source_segments": 179, "atoms": 170, "non_atoms": 9, "mandatory_atoms": 133},
    "TSPE": {"source_segments": 223, "atoms": 212, "non_atoms": 11, "mandatory_atoms": 155},
    "TCOMPL": {"source_segments": 184, "atoms": 174, "non_atoms": 10, "mandatory_atoms": 69},
    "TEXPERTES": {"source_segments": 114, "atoms": 108, "non_atoms": 6, "mandatory_atoms": 74},
    "1NSI": {"source_segments": 153, "atoms": 138, "non_atoms": 15, "mandatory_atoms": 87},
    "TNSI": {"source_segments": 132, "atoms": 117, "non_atoms": 15, "mandatory_atoms": 78},
}


def _producer():
    assert SCRIPT.is_file(), f"producteur second-pass absent: {SCRIPT}"
    spec = importlib.util.spec_from_file_location(
        "build_official_atomization_second_pass", SCRIPT
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def source_payload() -> dict:
    return json.loads(SOURCE_SEGMENTS.read_text(encoding="utf-8"))


@pytest.fixture
def atom_payload() -> dict:
    return json.loads(FIRST_PASS_ATOMS.read_text(encoding="utf-8"))


@pytest.fixture
def authority_payload() -> dict:
    return yaml.safe_load(AUTHORITY.read_text(encoding="utf-8"))


def _build(source_payload: dict, atom_payload: dict, authority_payload: dict):
    return _producer().build_payloads(source_payload, atom_payload, authority_payload)


def _finding_ids(second_pass: dict, code: str) -> set[str]:
    return {
        item.get("atom_id") or item.get("segment_id") or item.get("identity", "")
        for item in second_pass["findings"][code]
    }


def test_second_pass_producer_imports_no_first_pass_code() -> None:
    producer_source = SCRIPT.read_text(encoding="utf-8") if SCRIPT.exists() else ""
    assert producer_source, "le producteur second-pass doit exister"
    tree = ast.parse(producer_source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert not any(
        name.startswith("scripts.build_official_")
        or name.startswith("build_official_")
        for name in imported
    ), imported


def test_independent_policy_reconstructs_the_current_source_denominator(
    source_payload: dict,
) -> None:
    requirements = _producer().build_independent_requirements(source_payload)
    summary = requirements["summary"]

    assert len(requirements["requirements"]) == 985
    assert summary == {
        "source_segments": 985,
        "atoms": 919,
        "non_atoms": 66,
        "mandatory_atoms": 596,
        "unknown": 0,
        "policy_counts": {
            "cross_cutting_non_atoms": 54,
            "structural_non_atoms": 6,
            "framework_non_atoms": 6,
        },
        "by_manual": EXPECTED_BY_MANUAL,
    }
    assert all(
        row["disposition"] in {"ATOM", "NON_ATOM"}
        for row in requirements["requirements"]
    )
    assert all(
        row["decision_basis"]
        for row in requirements["requirements"]
        if row["disposition"] == "NON_ATOM"
    )
    atom_requirements = [
        row for row in requirements["requirements"] if row["disposition"] == "ATOM"
    ]
    assert all(row["expected_atom_type"] for row in atom_requirements)
    assert all(row["canonical_justification"] for row in atom_requirements)
    assert sum(bool(row["allowed_paraphrase_digest"]) for row in atom_requirements) == 11
    non_atom_requirements = [
        row
        for row in requirements["requirements"]
        if row["disposition"] == "NON_ATOM"
    ]
    assert len(non_atom_requirements) == 66
    assert all(
        row["expected_non_atom_classification"] for row in non_atom_requirements
    )
    assert all(
        row["canonical_non_atom_justification"] for row in non_atom_requirements
    )


def test_first_pass_atom_mutation_cannot_change_independent_requirements(
    source_payload: dict,
    atom_payload: dict,
) -> None:
    producer = _producer()
    before = producer.build_independent_requirements(source_payload)
    mutated = copy.deepcopy(atom_payload)
    mutated["atoms"][0]["mandatory"] = "NO"
    after = producer.build_independent_requirements(source_payload)

    assert before == after
    assert hashlib.sha256(producer.render_json(before).encode()).hexdigest() == hashlib.sha256(
        producer.render_json(after).encode()
    ).hexdigest()


@pytest.mark.parametrize(
    ("record_kind", "mutation", "error_fragment"),
    (
        ("segment", "empty", "source segment_id must be non-empty and unique"),
        ("segment", "duplicate", "source segment_id must be non-empty and unique"),
        ("atom", "empty", "first-pass atom_id must be non-empty and unique"),
        ("atom", "duplicate", "first-pass atom_id must be non-empty and unique"),
    ),
)
def test_identifiers_fail_closed_before_indexation(
    source_payload: dict,
    atom_payload: dict,
    authority_payload: dict,
    record_kind: str,
    mutation: str,
    error_fragment: str,
) -> None:
    mutated_source = copy.deepcopy(source_payload)
    mutated_atoms = copy.deepcopy(atom_payload)
    records = (
        mutated_source["segments"]
        if record_kind == "segment"
        else mutated_atoms["atoms"]
    )
    identifier = "segment_id" if record_kind == "segment" else "atom_id"
    if mutation == "empty":
        records[0][identifier] = ""
    else:
        records[1][identifier] = records[0][identifier]

    with pytest.raises(ValueError, match=error_fragment):
        _build(mutated_source, mutated_atoms, authority_payload)


def test_segment_ledger_is_an_exact_total_partition_with_explicit_reasons(
    source_payload: dict,
    atom_payload: dict,
    authority_payload: dict,
) -> None:
    ledger, second_pass = _build(source_payload, atom_payload, authority_payload)
    source_ids = {row["segment_id"] for row in source_payload["segments"]}
    atom_ids = {atom["atom_id"] for atom in atom_payload["atoms"]}
    ledger_atom_ids = [
        atom_id for row in ledger["rows"] for atom_id in row["first_pass_atom_ids"]
    ]

    assert ledger["summary"]["status"] == "PASS"
    assert ledger["summary"]["source_segments"] == 985
    assert ledger["summary"]["atomized_source_segments"] == 919
    assert ledger["summary"]["classified_non_atoms"] == 66
    assert ledger["summary"]["official_atoms"] == 919
    assert ledger["summary"]["mandatory_atoms"] == 596
    assert ledger["summary"]["unknown"] == 0
    assert {row["segment_id"] for row in ledger["rows"]} == source_ids
    assert len(ledger["rows"]) == len(source_ids)
    assert set(ledger_atom_ids) == atom_ids
    assert len(ledger_atom_ids) == len(set(ledger_atom_ids)) == 919
    for row in ledger["rows"]:
        assert bool(row["first_pass_atom_ids"]) ^ bool(row["no_atom_reason"])
        assert row["source_wording_digest"].startswith("sha256:")
        assert row["traceability_status"] == "PASS"
    assert second_pass["summary"]["unknown"] == 0


def test_current_second_pass_has_all_six_findings_at_zero_and_uses_real_denominator(
    source_payload: dict,
    atom_payload: dict,
    authority_payload: dict,
) -> None:
    _, second_pass = _build(source_payload, atom_payload, authority_payload)
    summary = second_pass["summary"]

    assert second_pass["methodology"]["imports_first_pass_code"] is False
    assert second_pass["methodology"]["first_pass_atoms_shape_second_pass"] is False
    assert set(second_pass["findings"]) == FINDING_CODES
    assert all(second_pass["findings"][code] == [] for code in FINDING_CODES)
    assert summary["status"] == "PASS"
    assert summary["source_segments"] == 985
    assert summary["second_pass_atoms"] == 919
    assert summary["second_pass_non_atoms"] == 66
    assert summary["first_pass_atoms"] == 919
    assert summary["mandatory_denominator"] == sum(
        row["mandatory_for_coverage"] == "YES"
        and row["disposition"] == "ATOM"
        for row in second_pass["requirements"]
    )
    assert summary["mandatory_denominator"] == 596
    assert summary["first_pass_mandatory_atoms"] == 596
    assert summary["denominator_delta"] == 0
    assert summary["unknown"] == 0


def test_dropping_a_mandatory_atom_is_detected_by_the_unchanged_second_pass(
    source_payload: dict,
    atom_payload: dict,
    authority_payload: dict,
) -> None:
    mutated = copy.deepcopy(atom_payload)
    mutated["atoms"] = [
        atom for atom in mutated["atoms"] if atom["atom_id"] != "1SPE-OFFICIAL-010"
    ]

    _, second_pass = _build(source_payload, mutated, authority_payload)

    assert second_pass["summary"]["status"] == "RED"
    assert "1SPE-SOURCE-SEG-010" in _finding_ids(
        second_pass, "MANDATORY_SEGMENT_UNREPRESENTED"
    )


def test_duplicating_an_atom_is_detected_by_the_unchanged_second_pass(
    source_payload: dict,
    atom_payload: dict,
    authority_payload: dict,
) -> None:
    mutated = copy.deepcopy(atom_payload)
    duplicate = copy.deepcopy(
        next(atom for atom in mutated["atoms"] if atom["atom_id"] == "1SPE-OFFICIAL-010")
    )
    duplicate["atom_id"] = "1SPE-OFFICIAL-010-DUPLICATE"
    mutated["atoms"].append(duplicate)

    _, second_pass = _build(source_payload, mutated, authority_payload)

    assert second_pass["summary"]["status"] == "RED"
    assert "1SPE-SOURCE-SEG-010" in _finding_ids(second_pass, "DUPLICATE_ATOM")


def test_atom_pointing_to_an_unknown_segment_is_phantom(
    source_payload: dict,
    atom_payload: dict,
    authority_payload: dict,
) -> None:
    mutated = copy.deepcopy(atom_payload)
    atom = next(atom for atom in mutated["atoms"] if atom["atom_id"] == "1SPE-OFFICIAL-010")
    atom["source_segment_ids"] = ["1SPE-SOURCE-SEG-999"]

    _, second_pass = _build(source_payload, mutated, authority_payload)

    assert "1SPE-OFFICIAL-010" in _finding_ids(second_pass, "PHANTOM_ATOM")


def test_atom_without_one_exact_source_is_ambiguous(
    source_payload: dict,
    atom_payload: dict,
    authority_payload: dict,
) -> None:
    mutated = copy.deepcopy(atom_payload)
    atom = next(atom for atom in mutated["atoms"] if atom["atom_id"] == "1SPE-OFFICIAL-010")
    atom["source_segment_ids"] = []

    _, second_pass = _build(source_payload, mutated, authority_payload)

    assert "1SPE-OFFICIAL-010" in _finding_ids(second_pass, "AMBIGUOUS_ATOM")


def test_future_tspe_authority_is_a_wrong_year_atom(
    source_payload: dict,
    atom_payload: dict,
    authority_payload: dict,
) -> None:
    mutated = copy.deepcopy(atom_payload)
    atom = next(atom for atom in mutated["atoms"] if atom["atom_id"] == "TSPE-OFFICIAL-008")
    atom["authority_NOR"] = "MENE2602919A"
    atom["applicable_school_year"] = "2027-2028"
    atom["effective_year"] = "2027-2028"

    _, second_pass = _build(source_payload, mutated, authority_payload)

    assert "TSPE-OFFICIAL-008" in _finding_ids(second_pass, "WRONG_YEAR_ATOM")


def test_mandatory_flip_is_a_classification_disagreement(
    source_payload: dict,
    atom_payload: dict,
    authority_payload: dict,
) -> None:
    mutated = copy.deepcopy(atom_payload)
    atom = next(atom for atom in mutated["atoms"] if atom["atom_id"] == "1SPE-OFFICIAL-010")
    atom["mandatory"] = "NO"

    _, second_pass = _build(source_payload, mutated, authority_payload)

    assert "1SPE-OFFICIAL-010" in _finding_ids(
        second_pass, "MANDATORY_CLASSIFICATION_DISAGREEMENT"
    )


def test_changed_source_anchor_is_detected_as_ambiguous(
    source_payload: dict,
    atom_payload: dict,
    authority_payload: dict,
) -> None:
    mutated = copy.deepcopy(atom_payload)
    atom = next(atom for atom in mutated["atoms"] if atom["atom_id"] == "1SPE-OFFICIAL-010")
    atom["official_page_or_anchor"] = "lines:999"

    _, second_pass = _build(source_payload, mutated, authority_payload)

    assert "1SPE-OFFICIAL-010" in _finding_ids(second_pass, "AMBIGUOUS_ATOM")


@pytest.mark.parametrize(
    ("field", "mutated_value", "finding_code"),
    (
        ("type", "OPTIONAL_EXTENSION", "ATOM_TYPE_DISAGREEMENT"),
        (
            "short_official_wording_or_paraphrase",
            "Un texte sans rapport avec le segment officiel.",
            "ATOM_WORDING_DISAGREEMENT",
        ),
        (
            "mandatory_justification",
            "Justification arbitraire non issue de la taxonomie canonique.",
            "ATOM_JUSTIFICATION_DISAGREEMENT",
        ),
        ("manual", "BROKEN", "ATOM_MANUAL_DISAGREEMENT"),
    ),
)
def test_atom_semantic_mutations_fail_closed(
    source_payload: dict,
    atom_payload: dict,
    authority_payload: dict,
    field: str,
    mutated_value: str,
    finding_code: str,
) -> None:
    mutated = copy.deepcopy(atom_payload)
    atom = next(
        atom for atom in mutated["atoms"] if atom["atom_id"] == "1SPE-OFFICIAL-010"
    )
    atom[field] = mutated_value

    _, second_pass = _build(source_payload, mutated, authority_payload)

    assert second_pass["summary"]["status"] == "RED"
    assert "1SPE-OFFICIAL-010" in _finding_ids(second_pass, finding_code)


def test_the_eleven_locked_paraphrases_are_exact_and_fail_closed(
    source_payload: dict,
    atom_payload: dict,
    authority_payload: dict,
) -> None:
    source_by_id = {
        segment["segment_id"]: segment for segment in source_payload["segments"]
    }
    paraphrases = [
        atom
        for atom in atom_payload["atoms"]
        if atom["short_official_wording_or_paraphrase"]
        != source_by_id[atom["source_segment_ids"][0]]["source_wording_short"]
    ]
    assert len(paraphrases) == 11

    _, current = _build(source_payload, atom_payload, authority_payload)
    assert current["findings"]["ATOM_WORDING_DISAGREEMENT"] == []

    mutated = copy.deepcopy(atom_payload)
    atom = next(
        atom
        for atom in mutated["atoms"]
        if atom["atom_id"] == "TEXPERTES-OFFICIAL-008"
    )
    atom["short_official_wording_or_paraphrase"] = "Paraphrase non autorisée."

    _, second_pass = _build(source_payload, mutated, authority_payload)
    assert "TEXPERTES-OFFICIAL-008" in _finding_ids(
        second_pass, "ATOM_WORDING_DISAGREEMENT"
    )


def test_unknown_non_atom_disposition_is_a_phantom(
    source_payload: dict,
    atom_payload: dict,
    authority_payload: dict,
) -> None:
    mutated = copy.deepcopy(atom_payload)
    mutated["classified_non_atoms"][0]["source_segment_id"] = "UNKNOWN-SEG"

    _, second_pass = _build(source_payload, mutated, authority_payload)

    assert second_pass["summary"]["status"] == "RED"
    assert "UNKNOWN-SEG" in _finding_ids(
        second_pass, "PHANTOM_NON_ATOM_DISPOSITION"
    )


@pytest.mark.parametrize(
    ("field", "mutated_value", "finding_code"),
    (
        ("manual", "BROKEN", "NON_ATOM_MANUAL_DISAGREEMENT"),
        (
            "classification",
            "OPTIONAL_EXTENSION",
            "NON_ATOM_CLASSIFICATION_DISAGREEMENT",
        ),
        ("mandatory_for_coverage", "YES", "NON_ATOM_MANDATORY_DISAGREEMENT"),
        (
            "justification",
            "Justification arbitraire non issue de la taxonomie canonique.",
            "NON_ATOM_JUSTIFICATION_DISAGREEMENT",
        ),
    ),
)
def test_non_atom_semantic_mutations_fail_closed(
    source_payload: dict,
    atom_payload: dict,
    authority_payload: dict,
    field: str,
    mutated_value: str,
    finding_code: str,
) -> None:
    mutated = copy.deepcopy(atom_payload)
    disposition = mutated["classified_non_atoms"][0]
    assert disposition["source_segment_id"] == "1SPE-SOURCE-SEG-001"
    disposition[field] = mutated_value

    _, second_pass = _build(source_payload, mutated, authority_payload)

    assert second_pass["summary"]["status"] == "RED"
    assert "1SPE-SOURCE-SEG-001" in _finding_ids(second_pass, finding_code)


def test_missing_non_atom_reason_makes_the_ledger_unknown(
    source_payload: dict,
    atom_payload: dict,
    authority_payload: dict,
) -> None:
    mutated = copy.deepcopy(atom_payload)
    item = next(
        row
        for row in mutated["classified_non_atoms"]
        if row["source_segment_id"] == "1SPE-SOURCE-SEG-001"
    )
    item["justification"] = ""

    ledger, second_pass = _build(source_payload, mutated, authority_payload)

    assert ledger["summary"]["status"] == "RED"
    assert ledger["summary"]["unknown"] >= 1
    assert second_pass["summary"]["status"] == "RED"


def test_independent_unknown_and_trace_mismatch_make_both_artifacts_red(
    source_payload: dict,
    atom_payload: dict,
    authority_payload: dict,
) -> None:
    mutated = copy.deepcopy(source_payload)
    segment = next(
        row
        for row in mutated["segments"]
        if row["segment_id"] == "1SPE-SOURCE-SEG-001"
    )
    segment["source_wording_short"] += " — mutation de digest"

    ledger, second_pass = _build(mutated, atom_payload, authority_payload)

    assert second_pass["summary"]["unknown"] > 0
    assert second_pass["summary"]["status"] == "RED"
    assert ledger["summary"]["status"] == "RED"
    assert ledger["summary"]["independent_unknown"] > 0
    assert ledger["summary"]["trace_red_rows"] > 0


def test_second_pass_artifacts_are_current_and_deterministic() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert SEGMENT_LEDGER.is_file()
    assert SECOND_PASS.is_file()


def test_bundle_commit_rolls_back_all_four_outputs_after_one_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    producer = _producer()
    targets = [tmp_path / f"artifact-{index}" for index in range(4)]
    old_contents = {path: f"old-{index}\n" for index, path in enumerate(targets)}
    for path, content in old_contents.items():
        path.write_text(content, encoding="utf-8")
    new_contents = {path: f"new-{index}\n" for index, path in enumerate(targets)}
    real_replace = producer.os.replace
    replaced_targets = 0

    def replace_then_fail_once(source, destination) -> None:
        nonlocal replaced_targets
        real_replace(source, destination)
        if Path(destination) in targets:
            replaced_targets += 1
            if replaced_targets == 1:
                raise RuntimeError("injected failure after first replacement")

    monkeypatch.setattr(producer.os, "replace", replace_then_fail_once)

    with pytest.raises(RuntimeError, match="after first replacement"):
        producer.commit_output_bundle(new_contents)

    assert replaced_targets >= 1
    assert {path: path.read_text(encoding="utf-8") for path in targets} == old_contents
    assert set(tmp_path.iterdir()) == set(targets)


def test_bundle_double_failure_preserves_recovery_backups(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    producer = _producer()
    targets = [tmp_path / f"artifact-{index}" for index in range(4)]
    old_contents = {path: f"old-{index}\n" for index, path in enumerate(targets)}
    for path, content in old_contents.items():
        path.write_text(content, encoding="utf-8")
    new_contents = {path: f"new-{index}\n" for index, path in enumerate(targets)}
    real_replace = producer.os.replace
    target_replace_calls = 0

    def fail_install_then_rollback(source, destination) -> None:
        nonlocal target_replace_calls
        if Path(destination) in targets:
            target_replace_calls += 1
            if target_replace_calls == 1:
                real_replace(source, destination)
                raise RuntimeError("injected installation failure")
            if target_replace_calls == 2:
                raise RuntimeError("injected rollback failure")
        real_replace(source, destination)

    monkeypatch.setattr(producer.os, "replace", fail_install_then_rollback)

    with pytest.raises(RuntimeError) as captured:
        producer.commit_output_bundle(new_contents)

    recovery_directory = getattr(captured.value, "recovery_directory", None)
    assert recovery_directory is not None
    recovery_directory = Path(recovery_directory)
    assert str(recovery_directory) in str(captured.value)
    assert recovery_directory.is_dir()
    recovered = {
        path.read_text(encoding="utf-8")
        for path in recovery_directory.glob("*.old")
    }
    assert recovered == set(old_contents.values())


def test_cli_output_paths_are_not_overridable(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--output-dir", str(tmp_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert list(tmp_path.iterdir()) == []


def test_mandatory_denominator_is_not_hardcoded() -> None:
    source = SCRIPT.read_text(encoding="utf-8") if SCRIPT.exists() else ""
    assert "MANDATORY_CONTRACT_TOTAL" not in source
    assert "== 596" not in source
