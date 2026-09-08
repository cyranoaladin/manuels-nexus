"""A classified control is not a PASS; mutations must invalidate the evidence."""

import copy
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def producer():
    path = ROOT / "scripts/build_astra_delta_matrix.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("astra_delta_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def payload(producer):
    evidence = {"kind": "fixture_observation", "result": {"count": 3}}
    evidence["digest"] = producer.digest_json(evidence)
    return {
        "CURRENT_HEAD": "a" * 40,
        "approves_nothing": True,
        "evidence": {"E1": evidence},
        "rows": [
            {
                "ASTRA_CONTROL_ID": "SCI-01",
                "CURRENT_HEAD": "a" * 40,
                "CURRENT_EVIDENCE": ["E1"],
                "CURRENT_EVIDENCE_DIGEST": producer.digest_json(
                    {"E1": evidence["digest"]}
                ),
                "STATUS": "PARTIAL",
                "NOTES": "Only one bounded assertion checked",
            },
            {
                "ASTRA_CONTROL_ID": "PDF-01",
                "CURRENT_HEAD": "a" * 40,
                "CURRENT_EVIDENCE": [],
                "CURRENT_EVIDENCE_DIGEST": None,
                "STATUS": "DEFERRED_TO_RELEASE_PHASE",
                "NOTES": "Final PDF required",
            },
        ],
    }


def test_every_control_is_classified_once_without_becoming_approved(producer):
    assert producer is not None, "A reproducible Astra delta producer is required"
    value = payload(producer)
    producer.validate_control_partition(value, {"SCI-01", "PDF-01"})
    assert all(row["STATUS"] != "COVERED_CURRENT_HEAD" for row in value["rows"])


@pytest.mark.parametrize("mutation", ["remove", "duplicate", "invent"])
def test_partition_mutations_are_rejected(producer, mutation):
    assert producer is not None, "A reproducible Astra delta producer is required"
    value = payload(producer)
    if mutation == "remove":
        value["rows"].pop()
    elif mutation == "duplicate":
        value["rows"].append(copy.deepcopy(value["rows"][0]))
    else:
        value["rows"][0]["ASTRA_CONTROL_ID"] = "UNKNOWN-1"
    with pytest.raises(ValueError, match="partition"):
        producer.validate_control_partition(value, {"SCI-01", "PDF-01"})


def test_evidence_tampering_cannot_keep_a_valid_receipt(producer):
    assert producer is not None, "A reproducible Astra delta producer is required"
    value = payload(producer)
    value["evidence"]["E1"]["result"]["count"] = 0
    with pytest.raises(ValueError, match="digest"):
        producer.validate_control_partition(value, {"SCI-01", "PDF-01"})


@pytest.mark.parametrize("field", ["dependency_inputs", "history_refs"])
def test_tampering_with_refresh_dependency_manifest_is_detected(producer, field):
    value = payload(producer)
    value[field] = {"fixture": "original"}
    value[field + "_digest"] = producer.digest_json(value[field])
    producer.validate_control_partition(value, {"SCI-01", "PDF-01"})
    value[field]["fixture"] = "changed"
    with pytest.raises(ValueError, match="digest"):
        producer.validate_control_partition(value, {"SCI-01", "PDF-01"})


def test_covered_requires_actual_evidence(producer):
    assert producer is not None, "A reproducible Astra delta producer is required"
    value = payload(producer)
    value["rows"][1]["STATUS"] = "COVERED_CURRENT_HEAD"
    with pytest.raises(ValueError, match="evidence"):
        producer.validate_control_partition(value, {"SCI-01", "PDF-01"})


def test_no_human_approval_can_be_invented(producer):
    assert producer is not None, "A reproducible Astra delta producer is required"
    value = payload(producer)
    value["rows"][0]["STATUS"] = "HUMAN_APPROVED"
    with pytest.raises(ValueError, match="status"):
        producer.validate_control_partition(value, {"SCI-01", "PDF-01"})


def test_head_mismatch_is_rejected(producer):
    assert producer is not None, "A reproducible Astra delta producer is required"
    value = payload(producer)
    value["rows"][0]["CURRENT_HEAD"] = "b" * 40
    with pytest.raises(ValueError, match="HEAD"):
        producer.validate_control_partition(value, {"SCI-01", "PDF-01"})


def test_parser_rejects_duplicate_external_control_ids(producer):
    assert producer is not None, "A reproducible Astra delta producer is required"
    with pytest.raises(ValueError, match="duplicate"):
        producer.parse_controls("### SCI-01 — one\n### SCI-01 — two\n")


def test_parser_preserves_external_locations_without_copying_observations(producer):
    assert producer is not None, "A reproducible Astra delta producer is required"
    assert producer.parse_controls("# Title\n\n### SCI-01 — confidential text\n") == [
        ("SCI-01", 3)
    ]


def test_retired_source_reappearing_cannot_keep_obsolete_disposition(producer):
    assert producer.retirement_disposition([], {"old.tex": False}) == "OBSOLETE_BY_CURRENT_HEAD"
    assert producer.retirement_disposition([{"matched_body": "old"}], {"old.tex": False}) == "PARTIAL"
    assert producer.retirement_disposition([], {"old.tex": True}) == "PARTIAL"


def test_unexplained_chapter_delta_is_not_reported_reconciled(producer):
    delta = producer.chapter_delta(["NSI/chapitres/OLD"], ["NSI/chapitres/NEW"])
    assert delta["ONLY_IN_ASTRA"] == ["NSI/chapitres/OLD"]
    assert delta["ONLY_IN_CURRENT"] == ["NSI/chapitres/NEW"]
    assert delta["CANONICAL_CHAPTER_SET_UNRECONCILED"] == 2
    known = producer.chapter_delta([], ["NSI/chapitres/TNSI-PROJET"], reviewed_project_contract=True)
    assert known["CANONICAL_CHAPTER_SET_UNRECONCILED"] == 0
    changed = producer.chapter_delta([], ["NSI/chapitres/TNSI-PROJET"])
    assert changed["CANONICAL_CHAPTER_SET_UNRECONCILED"] == 1


@pytest.mark.parametrize("kind", ["untracked", "modified"])
def test_uncommitted_source_cannot_be_bound_to_HEAD(producer, tmp_path, kind):
    import subprocess

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    chapter = tmp_path / "chapitres"
    chapter.mkdir()
    source = chapter / "one.tex"
    source.write_text("original")
    subprocess.run(["git", "-C", str(tmp_path), "add", "chapitres"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
    )
    assert hasattr(
        producer, "require_head_inputs"
    ), "Source identity must guard untracked content"
    producer.require_head_inputs(tmp_path, ["chapitres"])
    if kind == "untracked":
        (chapter / "two.tex").write_text("new object")
    else:
        source.write_text("changed mathematics")
    with pytest.raises(ValueError, match="HEAD"):
        producer.require_head_inputs(tmp_path, ["chapitres"])


@pytest.mark.parametrize(
    "relative",
    ["NSI/manifests/books/TNSI.json", "scripts/build_p0_content_clone_ledger.py"],
)
def test_build_refuses_dirty_dependency_outside_chapters_before_reading_external_audit(
    producer, tmp_path, relative
):
    import subprocess

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    dependency = tmp_path / relative
    dependency.parent.mkdir(parents=True)
    dependency.write_text("original input")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
    )
    dependency.write_text("mutated input")
    # The external folder deliberately does not exist. Dirty HEAD inputs must
    # be rejected before their output can be attributed to a clean HEAD.
    with pytest.raises(ValueError, match="HEAD"):
        producer.build(tmp_path, tmp_path.parent / "external-not-read")
