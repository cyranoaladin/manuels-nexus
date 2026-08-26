from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "audit" / "T3_WAVE_A_INITIAL_FREEZE.json"
ALGEBRA = ROOT / "audit" / "CURRENT_ANOMALY_SET_ALGEBRA.json"
SUNSET = ROOT / "audit" / "RESIDUAL_13_SUNSET_LEDGER.json"
PRODUCER = ROOT / "scripts" / "build_t3_wave_a_initial_freeze.py"

EXPECTED_SOURCE_SHA = "7b6140920c1e09d359bc7bf0d837192f3fe455da"
EXPECTED_RESIDUAL_DIGEST = (
    "sha256:1abe51ad406752b1e09996020c1afb2db3982ac2741cf98ed7b2118f302ace98"
)
EXPECTED_PREVIOUS_89_DIGEST = (
    "sha256:8daf2b85cecb556daa788056c66060ee6e0c20d00a09c976b9bac9f1bd9d8303"
)
EXPECTED_PARTITION = {
    "1SPE-EXPONENTIELLE": 2,
    "1SPE-SUITES": 5,
    "1SPE-VARIABLES-ALEATOIRES": 4,
    "TNSI-PROJET": 2,
}
EXPECTED_POST_FREEZE_CONTENT_PATHS = [
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/10_C1_generalites_suites.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/12_C3_suites_geometriques.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/13_C4_sommes.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/dossier_curation.json",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/evaluations/1SPE-SUITES-EV-A-corrige.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/evaluations/1SPE-SUITES-EV-B-corrige.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/methodes/1SPE-SUITES-ME-003.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/remediation/1SPE-SUITES-RE-C3.tex",
]


def digest(fingerprints: list[str]) -> str:
    payload = json.dumps(
        sorted(fingerprints), ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def git_blob(relative_path: str) -> tuple[bytes, str]:
    data = subprocess.run(
        ["git", "show", f"{EXPECTED_SOURCE_SHA}:{relative_path}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    oid = subprocess.run(
        ["git", "rev-parse", f"{EXPECTED_SOURCE_SHA}:{relative_path}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    return data, oid


def test_wave_a_initial_freeze_matches_canonical_debt_sources() -> None:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    algebra_bytes, algebra_oid = git_blob(str(ALGEBRA.relative_to(ROOT)))
    sunset_bytes, sunset_oid = git_blob(str(SUNSET.relative_to(ROOT)))
    algebra = json.loads(algebra_bytes.decode("utf-8"))
    sunset = json.loads(sunset_bytes.decode("utf-8"))

    residual = sorted(entry["fingerprint"] for entry in sunset["entries"])
    previous_89 = sorted(
        algebra["set_algebra"]["sets"]["EXPECTED_REVIEW_DEBT"]
    )
    partition = dict(
        sorted(Counter(entry["chapter"] for entry in sunset["entries"]).items())
    )
    wave_chapters = set(EXPECTED_PARTITION)
    previous_by_fp = {
        entry["fingerprint"]: entry
        for entry in algebra["expected_review_debt_details"]
    }
    intersection = sorted(
        fingerprint
        for fingerprint in previous_89
        if previous_by_fp[fingerprint]["chapter"] in wave_chapters
    )

    assert digest(residual) == EXPECTED_RESIDUAL_DIGEST
    assert digest(previous_89) == EXPECTED_PREVIOUS_89_DIGEST
    assert set(residual).isdisjoint(previous_89)
    assert freeze == {
        "artifact_type": "t3_wave_a_initial_freeze",
        "schema_version": 1,
        "wave_a_source_sha": EXPECTED_SOURCE_SHA,
        "freeze_materialization": {
            "basis": "IMMUTABLE_GIT_TREE",
            "chronology": "RETROACTIVE_AFTER_FIRST_SUITES_TDD_EDIT",
            "post_freeze_content_paths": EXPECTED_POST_FREEZE_CONTENT_PATHS,
            "post_freeze_content_path_count": 8,
        },
        "residual_13": {
            "count": 13,
            "digest": EXPECTED_RESIDUAL_DIGEST,
            "fingerprints": residual,
            "partition_by_chapter": EXPECTED_PARTITION,
        },
        "previous_89": {
            "count": 89,
            "digest": EXPECTED_PREVIOUS_89_DIGEST,
            "fingerprints": previous_89,
            "wave_a_intersection": intersection,
            "wave_a_intersection_count": 0,
        },
        "set_relations": {
            "residual_13_intersection_previous_89": [],
            "unknown": 0,
        },
        "source_artifacts": {
            "audit/CURRENT_ANOMALY_SET_ALGEBRA.json": {
                "git_blob_oid": algebra_oid,
                "sha256": f"sha256:{hashlib.sha256(algebra_bytes).hexdigest()}",
            },
            "audit/RESIDUAL_13_SUNSET_LEDGER.json": {
                "git_blob_oid": sunset_oid,
                "sha256": f"sha256:{hashlib.sha256(sunset_bytes).hexdigest()}",
            },
        },
        "source_semantic_digests": {
            "audit/CURRENT_ANOMALY_SET_ALGEBRA.json": algebra["source_digest"],
            "audit/RESIDUAL_13_SUNSET_LEDGER.json": sunset["fingerprint_digest"],
        },
        "verdict": "FROZEN_NO_TOCTOU",
    }


def test_wave_a_initial_freeze_markdown_is_object_visible() -> None:
    markdown = (ROOT / "audit" / "T3_WAVE_A_INITIAL_FREEZE.md").read_text(
        encoding="utf-8"
    )
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))

    assert EXPECTED_SOURCE_SHA in markdown
    assert EXPECTED_RESIDUAL_DIGEST in markdown
    assert EXPECTED_PREVIOUS_89_DIGEST in markdown
    for fingerprint in freeze["residual_13"]["fingerprints"]:
        assert fingerprint in markdown


def test_producer_check_and_git_tree_independence(monkeypatch: pytest.MonkeyPatch) -> None:
    subprocess.run(
        [sys.executable, str(PRODUCER), "--check"], cwd=ROOT, check=True
    )

    spec = importlib.util.spec_from_file_location("t3_freeze_builder", PRODUCER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original_read_text = Path.read_text

    def reject_worktree_sources(path: Path, *args: object, **kwargs: object) -> str:
        if path in {ALGEBRA, SUNSET}:
            raise AssertionError("worktree source read is forbidden")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", reject_worktree_sources)
    artifact, _markdown = module.build()
    assert artifact["wave_a_source_sha"] == EXPECTED_SOURCE_SHA


def test_pair_write_rolls_back_failure_between_replacements(tmp_path: Path) -> None:
    json_output = tmp_path / "freeze.json"
    md_output = tmp_path / "freeze.md"
    lock_path = tmp_path / "freeze.lock"
    json_output.write_text("old-json\n", encoding="utf-8")
    md_output.write_text("old-md\n", encoding="utf-8")
    spec = importlib.util.spec_from_file_location("t3_freeze_atomic", PRODUCER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    previous = os.environ.get("NEXUS_T3_FREEZE_TEST_FAIL_AFTER_FIRST_REPLACE")
    os.environ["NEXUS_T3_FREEZE_TEST_FAIL_AFTER_FIRST_REPLACE"] = "1"
    try:
        with pytest.raises(RuntimeError, match="injected failure"):
            module.atomic_write_pair(
                [(json_output, b"new-json\n"), (md_output, b"new-md\n")],
                lock_path,
            )
    finally:
        if previous is None:
            os.environ.pop(
                "NEXUS_T3_FREEZE_TEST_FAIL_AFTER_FIRST_REPLACE", None
            )
        else:
            os.environ[
                "NEXUS_T3_FREEZE_TEST_FAIL_AFTER_FIRST_REPLACE"
            ] = previous

    assert json_output.read_text(encoding="utf-8") == "old-json\n"
    assert md_output.read_text(encoding="utf-8") == "old-md\n"
