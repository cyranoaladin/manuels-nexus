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
SCOPE_MANIFEST = ROOT / "release" / "baseline-scope-1spe.json"


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
    contract_content = "chapitre: 1SPE-TEST\n"
    _write(root, "chapitres/1SPE-TEST/contrat.yaml", contract_content)
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
    contract_sha = hashlib.sha256(contract_content.encode()).hexdigest()
    _write(
        root,
        "chapitres/1SPE-TEST/validations/partially-bound.json",
        json.dumps(
            {
                "object": {
                    "path": "chapitres/1SPE-TEST/contrat.yaml",
                    "sha256": contract_sha,
                },
                "gate_sha256": "f" * 64,
            }
        ),
    )
    _write(
        root,
        "chapitres/TSPE-HORS-PERIMETRE/validations/tspe.json",
        '{"verdict": "pass"}\n',
    )
    _write(root, "validations/E2/nsi.png", "preuve NSI hors 1SPE\n")
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
        "out_of_scope_pollution": [],
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


def test_unbound_declared_fingerprint_prevents_reuse(
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

    attestation = next(
        item
        for item in report["current"]["attestations"]
        if item["path"].endswith("partially-bound.json")
    )
    assert attestation["classification"] == "review_required"
    assert attestation["fingerprints"]["verified_bindings"]
    assert attestation["fingerprints"]["unbound_declared"] == [
        {
            "json_pointer": "/gate_sha256",
            "sha256": "f" * 64,
        }
    ]


def test_scope_manifest_is_explicit_versioned_and_has_required_sentinels() -> None:
    assert SCOPE_MANIFEST.is_file()
    manifest = json.loads(SCOPE_MANIFEST.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == 1
    includes = set(manifest["universe"]["include"])
    excludes = set(manifest["universe"]["exclude"])
    assert {
        "docs/01_conception_manuel.md",
        "docs/02_workflow_production.md",
        "docs/05_conventions_latex.md",
        "docs/06_charte_graphique.md",
        "docs/07_ligne_editoriale.md",
        "referentiel/CONFORMITE_BO2026.md",
        "sources/registry.yaml",
    } <= includes
    assert {"chapitres/TSPE-*/**", "validations/E2/**"} <= excludes
    assert {rule["category"] for rule in manifest["categories"]} == {
        "source_1spe",
        "referential",
        "contract",
        "directive",
        "report",
        "attestation",
    }


def test_scope_excludes_tspe_and_nsi_e2_pollution(
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

    paths = {
        item["path"] for item in report["current"]["inventory"]["entries"]
    }
    assert "chapitres/TSPE-HORS-PERIMETRE/validations/tspe.json" not in paths
    assert "validations/E2/nsi.png" not in paths


def test_scope_reports_candidate_without_category() -> None:
    module = _load_module()
    manifest = copy.deepcopy(module.load_scope_manifest(SCOPE_MANIFEST))
    manifest["universe"]["include"].append("inconnu/**")
    analysis = module._scope_analysis(
        [
            {
                "path": "inconnu/objet.dat",
                "mode": "100644",
                "oid": "0" * 40,
            }
        ],
        manifest,
    )

    assert analysis["unclassified_paths"] == ["inconnu/objet.dat"]
    assert analysis["classification"] == {}


def test_scope_reports_every_overlapping_category() -> None:
    module = _load_module()
    manifest = copy.deepcopy(module.load_scope_manifest(SCOPE_MANIFEST))
    directive = next(
        rule
        for rule in manifest["categories"]
        if rule["category"] == "directive"
    )
    directive["include"].append("chapitres/1SPE-*/cours/**")
    analysis = module._scope_analysis(
        [
            {
                "path": "chapitres/1SPE-TEST/cours/01.tex",
                "mode": "100644",
                "oid": "0" * 40,
            }
        ],
        manifest,
    )

    assert analysis["duplicate_classifications"] == [
        {
            "path": "chapitres/1SPE-TEST/cours/01.tex",
            "categories": ["directive", "source_1spe"],
        }
    ]
    assert analysis["classification"] == {}


def test_scope_reports_category_pollution_outside_universe() -> None:
    module = _load_module()
    manifest = copy.deepcopy(module.load_scope_manifest(SCOPE_MANIFEST))
    directive = next(
        rule
        for rule in manifest["categories"]
        if rule["category"] == "directive"
    )
    directive["include"].append("pollution/**")
    analysis = module._scope_analysis(
        [
            {
                "path": "pollution/objet.md",
                "mode": "100644",
                "oid": "0" * 40,
            }
        ],
        manifest,
    )

    assert analysis["out_of_scope_pollution"] == ["pollution/objet.md"]


def test_capture_reads_only_classified_candidate_blobs(
    baseline_repository: tuple[Path, str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    root, origin, current = baseline_repository
    git_root, prefix = module._git_context(root)
    records = module._tree_records(git_root, prefix, current)
    origin_records = module._tree_records(git_root, prefix, origin)
    excluded_oid = next(
        item["oid"]
        for item in records
        if item["path"] == "validations/E2/nsi.png"
    )
    all_tree_oids = {
        item["oid"] for item in [*origin_records, *records]
    }
    captured_oids: set[str] = set()
    real_reader = module._read_blobs

    def spy_reader(git_root: Path, oids: set[str]) -> dict[str, bytes]:
        captured_oids.update(oids)
        return real_reader(git_root, oids)

    monkeypatch.setattr(module, "_read_blobs", spy_reader)
    module.capture_repository(
        root=root,
        origin_ref=origin,
        current_ref=current,
        test_evidence=_test_evidence(),
    )

    assert excluded_oid not in captured_oids
    assert captured_oids < all_tree_oids


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


def test_markdown_never_claims_zero_when_completeness_has_findings(
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
    report["completeness"]["unclassified_paths"] = ["inconnu/objet.dat"]

    markdown = module.render_markdown(report)

    assert "Zéro chemin du périmètre non classé" not in markdown
    assert "1 non classé" in markdown


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


@pytest.mark.parametrize(
    ("mutation", "diagnostic"),
    [
        ("date", "RFC 3339"),
        ("counter", "compteurs"),
        ("inventory_sha", "empreinte canonique"),
        ("test_commit", "preuve de test"),
        ("remediation_chain", "chaîne de remédiation"),
        ("duplicate_inventory_path", "chemins d'inventaire"),
        ("attestation_coverage", "couverture des attestations"),
        ("binding_hash", "liaison vérifiée"),
        ("unbound_partition", "partition des empreintes"),
    ],
)
def test_semantic_validator_rejects_cross_field_mutations(
    baseline_repository: tuple[Path, str, str],
    mutation: str,
    diagnostic: str,
) -> None:
    module = _load_module()
    root, origin, current = baseline_repository
    report = module.capture_repository(
        root=root,
        origin_ref=origin,
        current_ref=current,
        test_evidence=_test_evidence(),
    )
    candidate = copy.deepcopy(report)

    if mutation == "date":
        candidate["current"]["committed_at"] = "2026-07-26"
    elif mutation == "counter":
        candidate["current"]["inventory"]["counts_by_category"][
            "source_1spe"
        ] += 1
    elif mutation == "inventory_sha":
        candidate["origin"]["inventory"]["sha256"] = "0" * 64
    elif mutation == "test_commit":
        candidate["current"]["test_execution"]["commit_sha"] = origin
    elif mutation == "remediation_chain":
        candidate["remediation_history"][0]["parent_commit_sha"] = "0" * 40
    elif mutation == "duplicate_inventory_path":
        candidate["current"]["inventory"]["entries"].append(
            copy.deepcopy(candidate["current"]["inventory"]["entries"][0])
        )
    elif mutation == "attestation_coverage":
        candidate["current"]["attestations"].pop()
    elif mutation == "binding_hash":
        attestation = next(
            item
            for item in candidate["current"]["attestations"]
            if item["fingerprints"]["verified_bindings"]
        )
        attestation["fingerprints"]["verified_bindings"][0]["sha256"] = "0" * 64
    elif mutation == "unbound_partition":
        attestation = next(
            item
            for item in candidate["current"]["attestations"]
            if item["fingerprints"]["unbound_declared"]
        )
        attestation["fingerprints"]["unbound_declared"] = []
    else:  # pragma: no cover - protects the parameter table itself
        raise AssertionError(mutation)

    with pytest.raises(module.CaptureError, match=diagnostic):
        module.validate_report_semantics(candidate)


def test_schema_validation_uses_a_date_time_format_checker(
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
    report["origin"]["tags"][0]["created_at"] = "date-invalide"

    with pytest.raises(jsonschema.ValidationError) as caught:
        module._validate_report(report, SCHEMA)
    assert caught.value.validator == "format"


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
        "paths": [
            {
                "path": "notes-locales.tmp",
                "status": "??",
                "role": "changed",
            }
        ],
    }
    with pytest.raises(module.CaptureError, match="dépôt sale"):
        module.capture_repository(
            root=root,
            origin_ref=origin,
            current_ref=current,
            test_evidence=_test_evidence(),
            dirty_policy="fail",
        )


def test_capture_records_head_separately_from_the_pinned_current_snapshot(
    baseline_repository: tuple[Path, str, str],
) -> None:
    module = _load_module()
    root, origin, current = baseline_repository
    _write(root, "hors-snapshot.txt", "commit postérieur au snapshot\n")
    _git(root, "add", "hors-snapshot.txt")
    _git(root, "commit", "-q", "-m", "[LOCAL] commit de capture")
    capture_head = _git(root, "rev-parse", "HEAD")

    report = module.capture_repository(
        root=root,
        origin_ref=origin,
        current_ref=current,
        test_evidence=_test_evidence(),
    )

    assert report["current"]["commit_sha"] == current
    assert report["capture_context"]["capture_head_commit"] == capture_head
    assert capture_head != current


def test_dirty_rename_records_source_and_destination_without_arrow_syntax(
    baseline_repository: tuple[Path, str, str],
) -> None:
    module = _load_module()
    root, origin, current = baseline_repository
    source = "chapitres/1SPE-TEST/cours/01.tex"
    destination = "chapitres/1SPE-TEST/cours/01-renomme.tex"
    _git(root, "mv", source, destination)

    report = module.capture_repository(
        root=root,
        origin_ref=origin,
        current_ref=current,
        test_evidence=_test_evidence(),
        dirty_policy="record",
    )

    assert report["capture_context"]["working_tree"] == {
        "status": "dirty",
        "paths": [
            {
                "path": destination,
                "status": "R ",
                "role": "rename_destination",
            },
            {
                "path": source,
                "status": "R ",
                "role": "rename_source",
            },
        ],
    }
    assert all(
        " -> " not in item["path"]
        for item in report["capture_context"]["working_tree"]["paths"]
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


def test_git_calls_ignore_hostile_parent_environment_and_protect_refs(
    baseline_repository: tuple[Path, str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    root, origin, current = baseline_repository
    hostile = {
        "GIT_DIR": "/tmp/depot-detourne",
        "GIT_WORK_TREE": "/tmp/arbre-detourne",
        "GIT_OBJECT_DIRECTORY": "/tmp/objets-detournes",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES": "/tmp/objets-alternatifs",
        "GIT_CONFIG_GLOBAL": "/tmp/config-globale-hostile",
        "GIT_CONFIG_SYSTEM": "/tmp/config-systeme-hostile",
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "alias.rev-parse",
        "GIT_CONFIG_VALUE_0": "!false",
        "GIT_NO_REPLACE_OBJECTS": "0",
        "GIT_OPTIONAL_LOCKS": "1",
        "GIT_TERMINAL_PROMPT": "1",
    }
    for key, value in hostile.items():
        monkeypatch.setenv(key, value)
    real_run = module.subprocess.run
    environments: list[dict[str, str] | None] = []
    commands: list[list[str]] = []

    def spy_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess:
        command = args[0]
        assert isinstance(command, list)
        commands.append(command)
        environment = kwargs.get("env")
        assert environment is None or isinstance(environment, dict)
        environments.append(environment)
        return real_run(*args, **kwargs)

    monkeypatch.setattr(module.subprocess, "run", spy_run)
    report = module.capture_repository(
        root=root,
        origin_ref=origin,
        current_ref=current,
        test_evidence=_test_evidence(),
    )

    assert report["origin"]["commit_sha"] == origin
    assert environments and all(environment is not None for environment in environments)
    trusted_git_keys = {
        "GIT_CONFIG_GLOBAL",
        "GIT_CONFIG_NOSYSTEM",
        "GIT_NO_REPLACE_OBJECTS",
        "GIT_OPTIONAL_LOCKS",
        "GIT_TERMINAL_PROMPT",
        "GIT_ASKPASS",
    }
    for environment in environments:
        assert environment is not None
        assert {
            key for key in environment if key.startswith("GIT_")
        } == trusted_git_keys
        assert environment["GIT_NO_REPLACE_OBJECTS"] == "1"
        assert environment["GIT_OPTIONAL_LOCKS"] == "0"
        assert environment["GIT_TERMINAL_PROMPT"] == "0"
    assert any(
        command[1:4] == ["rev-parse", "--verify", "--end-of-options"]
        for command in commands
    )


def test_capture_ignores_real_git_replace_refs(
    baseline_repository: tuple[Path, str, str],
) -> None:
    module = _load_module()
    root, origin, current = baseline_repository
    replacement_tree = _git(root, "rev-parse", f"{current}^{{tree}}")
    replacement = _git(
        root,
        "commit-tree",
        replacement_tree,
        "-m",
        "objet de remplacement hostile",
    )
    _git(root, "replace", origin, replacement)

    report = module.capture_repository(
        root=root,
        origin_ref=origin,
        current_ref=current,
        test_evidence=_test_evidence(),
    )

    origin_source = next(
        item
        for item in report["origin"]["inventory"]["entries"]
        if item["path"] == "chapitres/1SPE-TEST/cours/01.tex"
    )
    assert origin_source["sha256"] == hashlib.sha256(b"origine\n").hexdigest()
    assert report["origin"]["subject"] == "[BASELINE] origine"


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
    json_output = root / "validations" / "release-1spe" / "baseline.json"
    markdown_output = root / "validations" / "release-1spe" / "baseline.md"
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
        "validations/release-1spe/baseline.json",
        "--markdown",
        "validations/release-1spe/baseline.md",
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


def test_output_pair_is_restricted_to_release_evidence_directory(
    tmp_path: Path,
) -> None:
    module = _load_module()
    root = tmp_path / "project"
    (root / "validations" / "release-1spe").mkdir(parents=True)

    valid = module._validate_output_pair(
        root,
        Path("validations/release-1spe/baseline.json"),
        Path("validations/release-1spe/baseline.md"),
    )
    assert valid[0] == root / "validations" / "release-1spe" / "baseline.json"
    with pytest.raises(module.CaptureError, match="validations/release-1spe"):
        module._validate_output_pair(
            root,
            Path("out/baseline.json"),
            Path("validations/release-1spe/baseline.md"),
        )


@pytest.mark.parametrize("link_kind", ["final-internal", "final-external", "parent"])
def test_output_pair_rejects_every_symlink_component(
    tmp_path: Path,
    link_kind: str,
) -> None:
    module = _load_module()
    root = tmp_path / "project"
    evidence = root / "validations" / "release-1spe"
    evidence.mkdir(parents=True)
    json_relative = Path("validations/release-1spe/baseline.json")
    if link_kind == "final-internal":
        (evidence / "real.json").write_text("ancien", encoding="utf-8")
        os.symlink("real.json", evidence / "baseline.json")
    elif link_kind == "final-external":
        external = tmp_path / "external.json"
        external.write_text("extérieur", encoding="utf-8")
        os.symlink(external, evidence / "baseline.json")
    else:
        (root / "validations" / "release-1spe").rmdir()
        target = root / "real-evidence"
        target.mkdir()
        os.symlink(target, root / "validations" / "release-1spe")

    with pytest.raises(module.CaptureError, match="symbolique"):
        module._validate_output_pair(
            root,
            json_relative,
            Path("validations/release-1spe/baseline.md"),
        )


def test_output_pair_rejects_non_regular_final_and_ancestor_collision(
    tmp_path: Path,
) -> None:
    module = _load_module()
    root = tmp_path / "project"
    evidence = root / "validations" / "release-1spe"
    evidence.mkdir(parents=True)
    (evidence / "directory.json").mkdir()

    with pytest.raises(module.CaptureError, match="fichier régulier"):
        module._validate_output_pair(
            root,
            Path("validations/release-1spe/directory.json"),
            Path("validations/release-1spe/baseline.md"),
        )
    with pytest.raises(module.CaptureError, match="ancêtre"):
        module._validate_output_pair(
            root,
            Path("validations/release-1spe/a"),
            Path("validations/release-1spe/a/b"),
        )


@pytest.mark.parametrize("old_pair_exists", [False, True])
def test_pair_publication_rolls_back_when_second_replace_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    old_pair_exists: bool,
) -> None:
    module = _load_module()
    root = tmp_path / "project"
    evidence = root / "validations" / "release-1spe"
    evidence.mkdir(parents=True)
    json_output = evidence / "baseline.json"
    markdown_output = evidence / "baseline.md"
    if old_pair_exists:
        json_output.write_bytes(b"old-json")
        markdown_output.write_bytes(b"old-markdown")
    real_replace = module.os.replace
    calls = 0

    def fail_second_replace(source: object, destination: object) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("publication simulée interrompue")
        real_replace(source, destination)

    monkeypatch.setattr(module.os, "replace", fail_second_replace)
    with pytest.raises(OSError, match="interrompue"):
        module._atomic_write_pair(
            json_output,
            b"new-json",
            markdown_output,
            b"new-markdown",
        )

    if old_pair_exists:
        assert json_output.read_bytes() == b"old-json"
        assert markdown_output.read_bytes() == b"old-markdown"
    else:
        assert not json_output.exists()
        assert not markdown_output.exists()


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
