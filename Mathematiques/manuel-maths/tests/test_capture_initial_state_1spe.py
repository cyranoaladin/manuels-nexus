import copy
import hashlib
import importlib.util
import json
import os
import subprocess
from pathlib import Path
from types import ModuleType

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "capture_initial_state_1spe.py"
SCHEMA = ROOT / "schemas" / "baseline_1spe.schema.json"


def test_capture_components_exist() -> None:
    assert SCRIPT.is_file()
    assert SCHEMA.is_file()


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("capture_initial_state_1spe", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def baseline_repository(tmp_path: Path) -> tuple[Path, str, str]:
    root = tmp_path / "collection" / "Mathematiques" / "manuel-maths"
    root.mkdir(parents=True)
    _git(tmp_path / "collection", "init", "-q")
    _git(tmp_path / "collection", "config", "user.name", "Baseline Test")
    _git(tmp_path / "collection", "config", "user.email", "baseline@example.invalid")

    _write(root, "chapitres/1SPE-TEST/cours/01.tex", "origine\n")
    _write(root, "chapitres/1SPE-TEST/contrat.yaml", "chapitre: 1SPE-TEST\n")
    _write(root, "referentiel/capacites_1SPE_TEST.json", '{"items": []}\n')
    _write(root, "DIRECTIVES_EN_COURS.md", "# Directive\n")
    _write(root, "RAPPORT_FINAL_1SPE.md", "# Rapport\n")
    source_sha = hashlib.sha256(b"origine\n").hexdigest()
    _write(
        root,
        "chapitres/1SPE-TEST/validations/current.json",
        json.dumps(
            {
                "object_path": "chapitres/1SPE-TEST/cours/01.tex",
                "object_sha256": source_sha,
            }
        ),
    )
    _write(
        root,
        "chapitres/1SPE-TEST/validations/unbound.json",
        '{"verdict": "pass"}\n',
    )
    _write(
        root,
        "chapitres/TSPE-HORS-PERIMETRE/validations/tspe.json",
        '{"verdict": "pass"}\n',
    )
    _git(tmp_path / "collection", "add", ".")
    _git(
        tmp_path / "collection",
        "commit",
        "-q",
        "-m",
        "[BASELINE] origine",
    )
    origin = _git(tmp_path / "collection", "rev-parse", "HEAD")
    _git(tmp_path / "collection", "tag", "manuel/1SPE-fixture-v1")

    _write(root, "chapitres/1SPE-TEST/cours/01.tex", "courant\n")
    _write(root, "chapitres/1SPE-TEST/exercices/1SPE-TEST-EX-001.tex", "exercice\n")
    _git(tmp_path / "collection", "add", ".")
    _git(
        tmp_path / "collection",
        "commit",
        "-q",
        "-m",
        "[CHARTE][V5.B-it2] corrige la baseline",
    )
    _write(root, "release/1SPE-toolchain.txt", "toolchain\n")
    _git(tmp_path / "collection", "add", ".")
    _git(
        tmp_path / "collection",
        "commit",
        "-q",
        "-m",
        "[1SPE][BAT] epingle le preflight",
    )
    current = _git(tmp_path / "collection", "rev-parse", "HEAD")
    return root, origin, current


def _test_evidence() -> dict[str, dict[str, object]]:
    return {
        "origin": {
            "kind": "historical_observation",
            "command": ".venv/bin/python -m pytest -q",
            "exit_code": 1,
            "passed": 1873,
            "failed": 7,
            "skipped": 5,
            "summary": "7 failed, 1873 passed, 5 skipped",
            "provenance": "Historique fourni par l'orchestrateur; non rejoué.",
        },
        "current": {
            "kind": "direct_execution",
            "command": ".venv/bin/python -m pytest -q",
            "exit_code": 0,
            "passed": 1946,
            "failed": 0,
            "skipped": 5,
            "summary": "1946 passed, 5 skipped",
            "provenance": "Exécution directe sur le commit courant propre.",
        },
    }


def test_capture_builds_two_traceable_snapshots(
    baseline_repository: tuple[Path, str, str],
) -> None:
    module = _load_module()
    root, origin, current = baseline_repository

    report = module.capture_repository(
        root=root,
        origin_ref=origin,
        current_ref=current,
        test_evidence=_test_evidence(),
    )

    assert report["status"] == "initial_snapshot"
    assert report["origin"]["label"] == "origin_immutable"
    assert report["origin"]["commit_sha"] == origin
    assert report["current"]["label"] == "current_preflight"
    assert report["current"]["commit_sha"] == current
    assert report["origin"]["test_execution"]["state"] == "historical_red"
    assert report["origin"]["test_execution"]["failed"] == 7
    assert report["current"]["test_execution"]["state"] == "green"
    assert report["current"]["test_execution"]["passed"] == 1946
    assert [item["kind"] for item in report["remediation_history"]] == [
        "baseline_remediation",
        "release_preflight",
    ]
    assert report["origin"]["tags"][0]["name"] == "manuel/1SPE-fixture-v1"
    assert len(report["origin"]["tags"][0]["object_sha256"]) == 64


def test_inventory_is_exhaustive_hashed_and_uniquely_classified(
    baseline_repository: tuple[Path, str, str],
) -> None:
    module = _load_module()
    root, origin, current = baseline_repository

    report = module.capture_repository(
        root=root,
        origin_ref=origin,
        current_ref=current,
        test_evidence=_test_evidence(),
    )

    current_inventory = report["current"]["inventory"]
    entries = current_inventory["entries"]
    paths = [entry["path"] for entry in entries]
    assert paths == sorted(paths)
    assert len(paths) == len(set(paths))
    assert not any("TSPE-HORS-PERIMETRE" in path for path in paths)
    assert report["completeness"] == {
        "duplicate_classifications": [],
        "unclassified_paths": [],
    }
    assert {
        "source_1spe",
        "referential",
        "contract",
        "directive",
        "report",
        "attestation",
    } <= {entry["category"] for entry in entries}
    assert all(len(entry["sha256"]) == 64 for entry in entries)
    assert current_inventory["sha256"] == hashlib.sha256(
        json.dumps(
            entries,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()


def test_attestations_have_one_conservative_verdict_and_fingerprints(
    baseline_repository: tuple[Path, str, str],
) -> None:
    module = _load_module()
    root, origin, current = baseline_repository

    report = module.capture_repository(
        root=root,
        origin_ref=origin,
        current_ref=current,
        test_evidence=_test_evidence(),
    )

    attestations = report["origin"]["attestations"]
    assert attestations
    by_name = {Path(item["path"]).name: item for item in attestations}
    assert by_name["current.json"]["classification"] == "stale"
    assert by_name["unbound.json"]["classification"] == "review_required"
    for attestation in attestations:
        assert attestation["classification"] in {
            "reusable",
            "stale",
            "review_required",
        }
        assert attestation["justification"]
        assert len(attestation["fingerprints"]["attestation_sha256"]) == 64


def test_report_validates_against_closed_schema(
    baseline_repository: tuple[Path, str, str],
) -> None:
    module = _load_module()
    root, origin, current = baseline_repository
    report = module.capture_repository(
        root=root,
        origin_ref=origin,
        current_ref=current,
        test_evidence=_test_evidence(),
    )

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(report)
    assert schema["additionalProperties"] is False


def test_schema_closes_nested_release_objects() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    assert schema["$defs"]["snapshot"]["additionalProperties"] is False
    assert schema["$defs"]["inventoryEntry"]["additionalProperties"] is False
    assert schema["$defs"]["attestation"]["properties"]["classification"][
        "enum"
    ] == ["reusable", "stale", "review_required"]
    assert schema["properties"]["status"]["const"] == "initial_snapshot"


def test_schema_rejects_invalid_nested_mutations(
    baseline_repository: tuple[Path, str, str],
) -> None:
    module = _load_module()
    root, origin, current = baseline_repository
    report = module.capture_repository(
        root=root,
        origin_ref=origin,
        current_ref=current,
        test_evidence=_test_evidence(),
    )
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    invalid_reports: list[dict[str, object]] = []
    with_extra = copy.deepcopy(report)
    with_extra["current"]["inventory"]["entries"][0]["unexpected"] = True
    invalid_reports.append(with_extra)
    with_bad_category = copy.deepcopy(report)
    with_bad_category["origin"]["inventory"]["entries"][0]["category"] = "other"
    invalid_reports.append(with_bad_category)
    with_bad_attestation = copy.deepcopy(report)
    with_bad_attestation["origin"]["attestations"][0]["classification"] = "pass"
    invalid_reports.append(with_bad_attestation)
    with_bad_sha = copy.deepcopy(report)
    with_bad_sha["current"]["inventory"]["sha256"] = "not-a-sha"
    invalid_reports.append(with_bad_sha)
    without_test_provenance = copy.deepcopy(report)
    del without_test_provenance["origin"]["test_execution"]["provenance"]
    invalid_reports.append(without_test_provenance)
    with_origin_relabelled_as_direct = copy.deepcopy(report)
    with_origin_relabelled_as_direct["origin"]["test_execution"][
        "kind"
    ] = "direct_execution"
    invalid_reports.append(with_origin_relabelled_as_direct)
    with_current_failure_hidden = copy.deepcopy(report)
    with_current_failure_hidden["current"]["test_execution"]["failed"] = 1
    invalid_reports.append(with_current_failure_hidden)

    assert all(not validator.is_valid(candidate) for candidate in invalid_reports)


def test_dirty_worktree_is_recorded_or_rejected_explicitly(
    baseline_repository: tuple[Path, str, str],
) -> None:
    module = _load_module()
    root, origin, current = baseline_repository
    _write(root, "notes-locales.tmp", "sale\n")

    report = module.capture_repository(
        root=root,
        origin_ref=origin,
        current_ref=current,
        test_evidence=_test_evidence(),
        dirty_policy="record",
    )

    assert report["capture_context"]["working_tree"] == {
        "status": "dirty",
        "paths": [{"path": "notes-locales.tmp", "status": "??"}],
    }
    with pytest.raises(module.CaptureError, match="dépôt sale"):
        module.capture_repository(
            root=root,
            origin_ref=origin,
            current_ref=current,
            test_evidence=_test_evidence(),
            dirty_policy="fail",
        )


def test_missing_origin_commit_fails_loudly(
    baseline_repository: tuple[Path, str, str],
) -> None:
    module = _load_module()
    root, _, current = baseline_repository

    with pytest.raises(module.CaptureError, match="commit origine absent"):
        module.capture_repository(
            root=root,
            origin_ref="0" * 40,
            current_ref=current,
            test_evidence=_test_evidence(),
        )


def test_unsafe_symlink_is_rejected_without_following_it(
    baseline_repository: tuple[Path, str, str],
) -> None:
    module = _load_module()
    root, origin, _ = baseline_repository
    link = root / "chapitres" / "1SPE-TEST" / "unsafe-link"
    os.symlink("../../../../outside", link)
    _git(root, "add", "chapitres/1SPE-TEST/unsafe-link")
    _git(root, "commit", "-q", "-m", "[1SPE][BAT] ajoute un lien test")
    current = _git(root, "rev-parse", "HEAD")

    with pytest.raises(module.CaptureError, match="lien symbolique sortant"):
        module.capture_repository(
            root=root,
            origin_ref=origin,
            current_ref=current,
            test_evidence=_test_evidence(),
        )


def test_cli_is_cwd_independent_schema_valid_and_deterministic(
    baseline_repository: tuple[Path, str, str],
    tmp_path: Path,
) -> None:
    root, origin, current = baseline_repository
    evidence = tmp_path / "evidence.json"
    evidence.write_text(json.dumps(_test_evidence()), encoding="utf-8")
    json_output = root / "out" / "baseline.json"
    markdown_output = root / "out" / "baseline.md"
    command = [
        str(SCRIPT),
        "--root",
        str(root),
        "--origin-ref",
        origin,
        "--current-ref",
        current,
        "--evidence-json",
        str(evidence),
        "--json",
        "out/baseline.json",
        "--markdown",
        "out/baseline.md",
    ]

    first = subprocess.run(
        command,
        cwd=tmp_path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert first.returncode == 0, first.stderr
    first_json = json_output.read_bytes()
    first_markdown = markdown_output.read_bytes()

    second = subprocess.run(
        command,
        cwd=tmp_path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert second.returncode == 0, second.stderr
    assert json_output.read_bytes() == first_json
    assert markdown_output.read_bytes() == first_markdown
    assert (json_output.stat().st_mode & 0o777) == 0o644
    assert (markdown_output.stat().st_mode & 0o777) == 0o644
    report = json.loads(first_json)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(report)
    assert origin in first_markdown.decode()
    assert current in first_markdown.decode()
    assert "historique" in first_markdown.decode().casefold()


def test_real_baseline_evidence_is_exact_and_never_calls_head_initial() -> None:
    module = _load_module()

    assert module.DEFAULT_ORIGIN_REF == "41eaa74"
    assert module.DEFAULT_CURRENT_REF == "ca16edb"
    assert module.DEFAULT_TEST_EVIDENCE["origin"] == {
        "kind": "historical_observation",
        "command": ".venv/bin/python -m pytest -q",
        "exit_code": 1,
        "passed": 1873,
        "failed": 7,
        "skipped": 5,
        "summary": "7 failed, 1873 passed, 5 skipped",
        "provenance": (
            "Première exécution historique consignée par l'orchestrateur sur "
            "41eaa74; résultat non rejoué et non présenté comme une mesure de HEAD."
        ),
    }
    assert module.DEFAULT_TEST_EVIDENCE["current"]["summary"] == (
        "1946 passed, 5 skipped"
    )
    assert module.DEFAULT_TEST_EVIDENCE["current"]["kind"] == "direct_execution"
    assert module.DEFAULT_REMEDIATION_COMMITS == (
        ("11dd437", "baseline_remediation"),
        ("44904f4", "baseline_remediation"),
        ("91dd5c9", "baseline_remediation"),
        ("16f6840", "baseline_remediation"),
        ("b834789", "baseline_remediation"),
        ("2386d4d", "release_preflight"),
        ("b4ed701", "release_preflight"),
        ("02a130e", "release_preflight"),
        ("d9ebe04", "release_preflight"),
        ("c698dfa", "release_preflight"),
        ("ca16edb", "release_preflight"),
    )


def test_large_blob_inventory_does_not_pipe_deadlock(tmp_path: Path) -> None:
    repository = tmp_path / "large-repository"
    repository.mkdir()
    _git(repository, "init", "-q")
    _git(repository, "config", "user.name", "Large Baseline Test")
    _git(repository, "config", "user.email", "large@example.invalid")
    for index in range(2500):
        _write(
            repository,
            f"chapitres/1SPE-MASS/cours/{index:04d}.tex",
            f"objet {index}\n" + ("x" * 2048),
        )
    _git(repository, "add", ".")
    _git(repository, "commit", "-q", "-m", "[BASELINE] masse")
    code = f"""
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("capture", {str(SCRIPT)!r})
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
root = Path({str(repository)!r})
commit = module._resolve_commit(root, "HEAD", label="test")
records = module._tree_records(root, "", commit)
blobs = module._read_blobs(root, {{item["oid"] for item in records}})
print(len(blobs))
"""

    completed = subprocess.run(
        [str(ROOT / ".venv" / "bin" / "python"), "-c", code],
        cwd=tmp_path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=10,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "2500"
