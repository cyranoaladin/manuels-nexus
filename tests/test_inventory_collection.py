from __future__ import annotations

import ast
import datetime
import importlib.util
import hashlib
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import warnings
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path, PurePosixPath

import jsonschema
import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inventory_collection.py"
GENERATOR_COMPONENTS = (
    "baseline_qualification.py",
    "build_manifest.py",
    "inventory_collection.py",
    "inventory_reports.py",
    "inventory_graph.py",
    "inventory_assembly.py",
    "inventory_pdf.py",
)


def _load_inventory_module():
    assert SCRIPT.is_file(), "scripts/inventory_collection.py doit etre cree"
    spec = importlib.util.spec_from_file_location("inventory_collection", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def inventory_module():
    return _load_inventory_module()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _init_repository(root: Path) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)


def _track(root: Path, *relative_paths: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), "add", "--", *relative_paths],
        check=True,
    )


def _contract(chapter: str, level: str, capacities: int = 2) -> str:
    rows = "\n".join(
        f'  - {{ code: C{index}, ref_capacite: {chapter}-C{index}, libelle_eleve: "Capacite {index}" }}'
        for index in range(1, capacities + 1)
    )
    return (
        f"chapitre: {chapter}\n"
        f"niveau: {level}\n"
        f"titre: Chapitre de test\n"
        "statut: approved\n"
        "capacites:\n"
        f"{rows}\n"
    )


def _meta(**overrides: object) -> str:
    data: dict[str, object] = {
        "id": "1SPE-TEST-COURS-C1",
        "chapitre": "1SPE-TEST",
        "type_objet": "cours",
        "status": "generated",
    }
    data.update(overrides)
    return (
        "% META: "
        + json.dumps(data, ensure_ascii=False, sort_keys=True)
        + "\nContenu\n"
    )


def _chapter_path(manual: str, chapter: str) -> str:
    if manual in {"1SPE", "TSPE"}:
        return f"Mathematiques/manuel-maths/chapitres/{chapter}"
    return f"NSI/chapitres/{chapter}"


def _install_audit_schemas(repository: Path) -> None:
    shutil.copytree(ROOT / "audit/schemas", repository / "audit/schemas")


def _commit_repository(repository: Path, message: str = "fixture") -> str:
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "-c",
            "user.name=Phase 0.1 Tests",
            "-c",
            "user.email=phase01-tests@example.invalid",
            "commit",
            "--allow-empty",
            "-qm",
            message,
        ],
        check=True,
    )
    return subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _local_cli_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("CI", None)
    return environment


def _run_inventory_cli(repository: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repository), *arguments],
        capture_output=True,
        text=True,
        check=False,
        env=_local_cli_environment(),
    )


def _run_repository_inventory_cli(
    repository: Path, *arguments: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(repository / "scripts/inventory_collection.py"),
            "--root",
            str(repository),
            *arguments,
        ],
        capture_output=True,
        text=True,
        check=False,
        env=_local_cli_environment(),
    )


def _install_generator_components(repository: Path) -> tuple[str, ...]:
    relative_paths = tuple(
        f"scripts/{component}" for component in GENERATOR_COMPONENTS
    )
    for relative_path in relative_paths:
        source = ROOT / relative_path
        destination = repository / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    _track(repository, *relative_paths)
    return relative_paths


def _seed_cli_repository(repository: Path) -> tuple[str, ...]:
    _init_repository(repository)
    _install_audit_schemas(repository)
    base = _chapter_path("1SPE", "1SPE-TEST")
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        f"{base}/cours/c1.tex": _meta(status="approved"),
    }
    for path, content in sources.items():
        _write(repository / path, content)
    schema_paths = tuple(
        path.relative_to(repository).as_posix()
        for path in sorted((repository / "audit/schemas").rglob("*.json"))
    )
    tracked = (*sources, *schema_paths)
    _track(repository, *tracked)
    return tracked


def _managed_output_paths(
    repository: Path, result: dict[str, object]
) -> tuple[Path, ...]:
    artifacts = result["artifacts"]
    assert isinstance(artifacts, dict)
    return tuple(
        sorted(repository / str(relative) for relative in artifacts.values())
    )


def _git_status_bytes(repository: Path) -> bytes:
    return subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "-z",
        ],
        check=True,
        capture_output=True,
    ).stdout


def _minimal_inventory(repository: Path, inventory_module):
    _init_repository(repository)
    base = _chapter_path("1SPE", "1SPE-TEST")
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        f"{base}/cours/c1.tex": _meta(status="approved"),
    }
    for path, content in sources.items():
        _write(repository / path, content)
    _track(repository, *sources)
    return inventory_module.build_inventory(repository)


def test_git_tracked_files_excludes_untracked_sources(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    tracked = f"{base}/cours/section.tex"
    untracked = f"{base}/cours/brouillon.tex"
    _write(tmp_path / tracked, _meta())
    _write(tmp_path / untracked, _meta(id="1SPE-TEST-BROUILLON"))
    _track(tmp_path, tracked)

    assert inventory_module.git_tracked_files(tmp_path) == (tracked,)


@pytest.mark.parametrize(
    "source_roles_payload",
    [
        pytest.param(None, id="absent"),
        pytest.param("", id="empty-file"),
        pytest.param("null\n", id="yaml-null"),
        pytest.param("roles: {}\n", id="empty-roles-mapping"),
        pytest.param(
            "roles:\n  production_object: []\n",
            id="role-without-usable-pattern",
        ),
        pytest.param(
            "roles:\n  fixture:\n    - '**/fixtures/**'\n",
            id="roles-without-production",
        ),
        pytest.param(
            "roles:\n"
            "  production_object:\n"
            "    - 'Mathematiques/manuel-maths/chapitres/**'\n"
            "    - 'NSI/chapitres/**'\n"
            "  fixture:\n"
            "    - '**/fixtures/**'\n"
            "role_order:\n"
            "  - fixture\n",
            id="production-omitted-from-role-order",
        ),
    ],
)
def test_source_roles_fall_back_when_configuration_is_absent(
    tmp_path: Path,
    inventory_module,
    source_roles_payload: str | None,
) -> None:
    _init_repository(tmp_path)
    if source_roles_payload is not None:
        _write(tmp_path / "audit/SOURCE_ROLES.yaml", source_roles_payload)
    base = _chapter_path("1SPE", "1SPE-TEST")
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        f"{base}/cours/c1.tex": _meta(status="approved"),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    fallback = inventory_module._default_role_patterns()
    assert inventory_module._collect_role_patterns(tmp_path) == fallback

    inventory = inventory_module.build_inventory(tmp_path)
    assert list(inventory["manuals"]["1SPE"]["chapters"]) == ["1SPE-TEST"]


@pytest.mark.parametrize(
    ("path", "expected_role"),
    [
        pytest.param(
            "NSI/chapitres/1NSI-TEST/_harvest/direct.candidate.tex",
            "harvest_candidate",
            id="harvest-direct-before-production",
        ),
        pytest.param(
            "NSI/chapitres/1NSI-TEST/_harvest/P04/cours.candidate.tex",
            "harvest_candidate",
            id="harvest-one-level-before-production",
        ),
        pytest.param(
            "NSI/chapitres/1NSI-TEST/_harvest/P04/nested/cours.candidate.tex",
            "harvest_candidate",
            id="harvest-deep-before-production",
        ),
        pytest.param(
            "Mathematiques/manuel-maths/build/maquette-v5/renvois.tex",
            "generated_dependency",
            id="generated-renvois",
        ),
        pytest.param(
            "NSI/build/direct.tex",
            "generated_dependency",
            id="generated-build-direct",
        ),
        pytest.param(
            "NSI/build/one/dependency.cls",
            "generated_dependency",
            id="generated-build-one-level",
        ),
        pytest.param(
            "NSI/build/one/deep/dependency.pdf",
            "generated_dependency",
            id="generated-build-deep",
        ),
        pytest.param(
            "Mathematiques/manuel-maths/chapitres/1SPE-TEST/tests/fixtures/cas.tex",
            "fixture",
            id="fixture-before-production",
        ),
        pytest.param(
            "Mathematiques/manuel-maths/validations/charte.visual.json",
            "visual_reference",
            id="visual-before-validation",
        ),
        pytest.param(
            "Mathematiques/manuel-maths/validations/v5-it1/page-13.png",
            "visual_reference",
            id="visual-v5-it1-png",
        ),
        pytest.param(
            "Mathematiques/manuel-maths/validations/v5-it2/page-13.png",
            "visual_reference",
            id="visual-v5-it2-png",
        ),
        pytest.param(
            "Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/main.tex",
            "visual_reference",
            id="visual-reference-kit",
        ),
        pytest.param(
            "audit/historique/ETAT_COLLECTION_AVANT_P0.md",
            "archive",
            id="archive-before-validation",
        ),
        pytest.param(
            "Mathematiques/manuel-maths/chapitres/1SPE-TEST/validations/c1.json",
            "validation_reference",
            id="validation-before-production",
        ),
        pytest.param(
            "Mathematiques/manuel-maths/chapitres/1SPE-TEST/cours/c1.tex",
            "production_object",
            id="production",
        ),
        pytest.param(
            ".github/actions/cache/entry.json",
            "excluded",
            id="excluded-first",
        ),
        pytest.param(
            "scripts/inventory_collection.py",
            "transversal",
            id="transversal-fallback",
        ),
    ],
)
def test_default_source_role_precedence_is_most_specific_first(
    inventory_module,
    path: str,
    expected_role: str,
) -> None:
    patterns, default, order = inventory_module._default_role_patterns()

    assert inventory_module._classify_source_path(
        path,
        {},
        default=default,
        role_patterns=patterns,
        role_order=order,
    ) == expected_role


def test_direct_harvest_candidate_never_enters_production_inventory(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    contract = f"{base}/contrat.yaml"
    course = f"{base}/cours/c1.tex"
    candidate = f"{base}/_harvest/direct.candidate.tex"
    _write(tmp_path / contract, _contract("1SPE-TEST", "1SPE", capacities=1))
    _write(tmp_path / course, _meta(status="approved"))
    _write(tmp_path / candidate, "Candidate de collecte sans META\n")
    _track(tmp_path, contract, course, candidate)

    inventory = inventory_module.build_inventory(tmp_path)
    object_paths = {
        item["path"]
        for item in inventory["manuals"]["1SPE"]["chapters"]["1SPE-TEST"]["objects"]
    }

    assert object_paths == {course}
    assert candidate not in object_paths
    assert candidate not in {
        anomaly["path"]
        for anomaly in inventory["anomalies"]["metadata_missing"]
    }
    assert candidate not in {
        anomaly["cible"]
        for anomaly in inventory["anomalies"]["orphan_files"]
    }


def test_real_harvest_candidates_never_produce_blocking_production_anomalies(
    inventory_module,
) -> None:
    tracked = inventory_module.git_tracked_files(ROOT)
    harvest = {
        path
        for path in tracked
        if inventory_module._is_intrinsic_harvest_candidate(path)
    }
    inventory = inventory_module.build_inventory(ROOT)
    object_paths = {
        item["path"]
        for manual in inventory["manuals"].values()
        for chapter in manual["chapters"].values()
        for item in chapter["objects"]
    }

    assert len(harvest) == 19
    assert harvest.isdisjoint(object_paths)
    for category in inventory_module.BLOCKING_ANOMALY_CATEGORIES:
        assert not any(
            any(
                path in json.dumps(anomaly, ensure_ascii=False, sort_keys=True)
                for path in harvest
            )
            for anomaly in inventory["anomalies"][category]
        ), category


def test_source_roles_control_file_is_schema_valid_and_digest_verified(
    inventory_module,
) -> None:
    path = ROOT / "audit/SOURCE_ROLES.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    schema = json.loads(
        (ROOT / "audit/schemas/v1/source-roles.schema.json").read_text(
            encoding="utf-8"
        )
    )

    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["control_digest"] == inventory_module._control_digest(payload)
    patterns, default, order = inventory_module._collect_role_patterns(ROOT)
    assert (patterns, default, order) == inventory_module._default_role_patterns()
    assert default == "transversal"
    assert order == [
        "excluded",
        "fixture",
        "harvest_candidate",
        "visual_reference",
        "archive",
        "generated_dependency",
        "validation_reference",
        "production_object",
        "transversal",
    ]
    assert patterns["generated_dependency"][0].endswith(
        "build/maquette-v5/renvois.tex"
    )
    tracked = inventory_module.git_tracked_files(ROOT)
    assignments = inventory_module._load_source_roles(ROOT, tracked)
    harvest = [
        path
        for path in tracked
        if "/_harvest/" in path and path.endswith(".candidate.tex")
    ]
    assert len(harvest) == 19
    assert {assignments[path] for path in harvest} == {"harvest_candidate"}
    assert inventory_module._classify_source_path(
        "Mathematiques/manuel-maths/build/maquette-v5/renvois.tex",
        assignments,
        default=default,
        role_patterns=patterns,
        role_order=order,
    ) == "generated_dependency"


def test_source_roles_control_rejects_digest_drift(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    payload = yaml.safe_load(
        (ROOT / "audit/SOURCE_ROLES.yaml").read_text(encoding="utf-8")
    )
    payload["default"] = "production_object"
    _write(
        tmp_path / "audit/SOURCE_ROLES.yaml",
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True),
    )

    with pytest.raises(inventory_module.InventoryError, match="control_digest"):
        inventory_module._collect_role_patterns(tmp_path)


def test_source_roles_control_rejects_schema_valid_precedence_weakening(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    payload = yaml.safe_load(
        (ROOT / "audit/SOURCE_ROLES.yaml").read_text(encoding="utf-8")
    )
    payload["role_order"] = [
        "production_object",
        *[
            role
            for role in payload["role_order"]
            if role != "production_object"
        ],
    ]
    payload["control_digest"] = inventory_module._control_digest(payload)
    _write(
        tmp_path / "audit/SOURCE_ROLES.yaml",
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True),
    )

    with pytest.raises(inventory_module.InventoryError, match="role_order"):
        inventory_module._collect_role_patterns(tmp_path)


@pytest.mark.parametrize(
    "mutation",
    [
        pytest.param("default", id="default-not-transversal"),
        pytest.param("missing-role", id="missing-canonical-role"),
        pytest.param("empty-role", id="empty-canonical-role"),
        pytest.param("broken-sentinel", id="harvest-sentinel-not-protected"),
    ],
)
def test_source_roles_control_rejects_digest_valid_invariant_weakening(
    tmp_path: Path,
    inventory_module,
    mutation: str,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    payload = yaml.safe_load(
        (ROOT / "audit/SOURCE_ROLES.yaml").read_text(encoding="utf-8")
    )
    if mutation == "default":
        payload["default"] = "production_object"
    elif mutation == "missing-role":
        payload["roles"].pop("fixture")
    elif mutation == "empty-role":
        payload["roles"]["fixture"] = []
    else:
        payload["roles"]["harvest_candidate"] = [
            "**/_harvest/reviewed-only/*.candidate.tex"
        ]
    payload["control_digest"] = inventory_module._control_digest(payload)
    _write(
        tmp_path / "audit/SOURCE_ROLES.yaml",
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True),
    )

    with pytest.raises(inventory_module.InventoryError, match="invariant"):
        inventory_module._collect_role_patterns(tmp_path)


@pytest.mark.parametrize(
    "mutation",
    [
        pytest.param("literal-sentinels", id="harvest-pattern-limited-to-sentinels"),
        pytest.param("targeted-fixture", id="real-harvest-hidden-as-fixture"),
    ],
)
def test_source_roles_rejects_digest_valid_harvest_bypass_on_all_tracked_candidates(
    tmp_path: Path,
    inventory_module,
    mutation: str,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    payload = yaml.safe_load(
        (ROOT / "audit/SOURCE_ROLES.yaml").read_text(encoding="utf-8")
    )
    tracked_harvest = [
        path
        for path in inventory_module.git_tracked_files(ROOT)
        if "/_harvest/" in path and path.endswith(".candidate.tex")
    ]
    assert len(tracked_harvest) == 19
    for path in tracked_harvest:
        _write(tmp_path / path, "% candidate de collecte\n")
    if mutation == "literal-sentinels":
        payload["roles"]["harvest_candidate"] = [
            "NSI/chapitres/1NSI-X/_harvest/direct.candidate.tex",
            "NSI/chapitres/1NSI-X/_harvest/P04/one.candidate.tex",
            "NSI/chapitres/1NSI-X/_harvest/P04/deep/n.candidate.tex",
        ]
    else:
        payload["roles"]["fixture"].append(tracked_harvest[0])
    payload["control_digest"] = inventory_module._control_digest(payload)
    _write(
        tmp_path / "audit/SOURCE_ROLES.yaml",
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True),
    )
    tracked = [*tracked_harvest, "audit/SOURCE_ROLES.yaml"]
    _track(tmp_path, *tracked)

    with pytest.raises(inventory_module.InventoryError, match="harvest"):
        inventory_module._load_source_roles(tmp_path)
    with pytest.raises(inventory_module.InventoryError, match="harvest"):
        inventory_module._load_source_roles(tmp_path, tracked)
    with pytest.raises(inventory_module.InventoryError, match="harvest"):
        inventory_module.build_inventory(tmp_path)
    gate = inventory_module._validate_model_gate(tmp_path)
    assert gate["success"] is False
    assert any("harvest" in reason for reason in gate["reasons"])


def test_source_roles_preserves_fixture_precedence_for_canonical_harvest_fixture(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    fixture = "tests/fixtures/_harvest/P04/example.candidate.tex"
    _write(tmp_path / fixture, "% fixture candidate\n")
    _track(tmp_path, fixture)

    assignments = inventory_module._load_source_roles(tmp_path, [fixture])

    assert assignments[fixture] == "fixture"


def test_source_roles_preserve_literal_backslash_git_path(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    literal = r"NSI\scripts\assemble.py"
    _write(
        tmp_path / literal,
        'ORDER = [("cours", "*")]\nVARIANTS = ["complet"]\n',
    )
    _track(tmp_path, literal)

    tracked = inventory_module.git_tracked_files(tmp_path)
    assignments = inventory_module._load_source_roles(tmp_path, tracked)

    assert tracked == (literal,)
    assert assignments == {literal: "transversal"}
    assert inventory_module._classify_source_path(literal, assignments) == "transversal"
    assert (
        inventory_module._classify_source_path(
            literal,
            {"NSI/scripts/assemble.py": "fixture"},
        )
        == "fixture"
    )
    inventory = inventory_module.build_inventory(tmp_path)
    assert not any(
        assembly["assembler"] == literal for assembly in inventory["assemblies"]
    )


def test_source_roles_reject_normalized_git_path_collision_deterministically(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    canonical = "NSI/scripts/assemble.py"
    literal = r"NSI\scripts\assemble.py"
    source = 'ORDER = [("cours", "*")]\nVARIANTS = ["complet"]\n'
    _write(tmp_path / canonical, source)
    _write(tmp_path / literal, source)
    _track(tmp_path, canonical, literal)
    tracked = inventory_module.git_tracked_files(tmp_path)

    errors: list[str] = []
    for paths in (tracked, tuple(reversed(tracked))):
        with pytest.raises(
            inventory_module.InventoryError,
            match="collision.*NSI/scripts/assemble.py",
        ) as exc_info:
            inventory_module._load_source_roles(tmp_path, paths)
        errors.append(str(exc_info.value))

    assert errors[0] == errors[1]
    assert canonical in errors[0]
    assert literal in errors[0]
    with pytest.raises(
        inventory_module.InventoryError,
        match="collision.*NSI/scripts/assemble.py",
    ):
        inventory_module.build_inventory(tmp_path)


def test_source_roles_rejects_digest_valid_reclassification_of_tracked_object(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    payload = yaml.safe_load(
        (ROOT / "audit/SOURCE_ROLES.yaml").read_text(encoding="utf-8")
    )
    base = _chapter_path("1SPE", "1SPE-TEST")
    contract = f"{base}/contrat.yaml"
    course = f"{base}/cours/c1.tex"
    _write(tmp_path / contract, _contract("1SPE-TEST", "1SPE", capacities=1))
    _write(tmp_path / course, _meta(status="approved"))
    payload["roles"]["fixture"].append(course)
    payload["control_digest"] = inventory_module._control_digest(payload)
    _write(
        tmp_path / "audit/SOURCE_ROLES.yaml",
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True),
    )
    _track(tmp_path, contract, course, "audit/SOURCE_ROLES.yaml")

    with pytest.raises(inventory_module.InventoryError, match="classification canonique"):
        inventory_module._load_source_roles(tmp_path)
    with pytest.raises(inventory_module.InventoryError, match="classification canonique"):
        inventory_module.build_inventory(tmp_path)
    gate = inventory_module._validate_model_gate(tmp_path)
    assert gate["success"] is False
    assert any("classification canonique" in reason for reason in gate["reasons"])


def test_require_clean_uses_canonical_union_for_untracked_source_roles(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    payload = yaml.safe_load(
        (ROOT / "audit/SOURCE_ROLES.yaml").read_text(encoding="utf-8")
    )
    hidden = (
        "Mathematiques/manuel-maths/chapitres/"
        "1SPE-TEST/cours/untracked.tex"
    )
    payload["roles"]["fixture"].append(hidden)
    payload["control_digest"] = inventory_module._control_digest(payload)
    _write(
        tmp_path / "audit/SOURCE_ROLES.yaml",
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True),
    )
    schema_paths = [
        path.relative_to(tmp_path).as_posix()
        for path in (tmp_path / "audit/schemas").rglob("*.json")
    ]
    _track(tmp_path, "audit/SOURCE_ROLES.yaml", *schema_paths)
    _commit_repository(tmp_path, "contrôle versionné")
    _write(tmp_path / hidden, _meta(status="approved"))

    gate = inventory_module._require_clean_gate(tmp_path)

    assert gate["exit_code"] == 4
    assert gate["reasons"] == [f"untracked_relevant:{hidden}"]


def test_source_roles_control_cannot_downgrade_to_legacy_when_schema_is_installed(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    _write(
        tmp_path / "audit/SOURCE_ROLES.yaml",
        "roles:\n  production_object:\n    - 'NSI/chapitres/**'\n",
    )

    with pytest.raises(inventory_module.InventoryError, match="contrôle versionné"):
        inventory_module._collect_role_patterns(tmp_path)


def test_visual_reference_is_relevant_to_provenance_and_require_clean(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    _commit_repository(tmp_path, "clean")
    visual = "Mathematiques/manuel-maths/validations/v5-it2/page-13.png"
    _write(tmp_path / visual, "visual fixture\n")
    patterns, _, order = inventory_module._default_role_patterns()

    relevant = inventory_module._git_relevant_untracked(
        tmp_path,
        tracked={},
        role_patterns=patterns,
        role_order=order,
    )
    gate = inventory_module._require_clean_gate(tmp_path)

    assert relevant == [visual]
    assert gate["exit_code"] == 4
    assert gate["reasons"] == [f"untracked_relevant:{visual}"]


def test_load_contract_reads_yaml_without_losing_capacity_order(
    tmp_path: Path, inventory_module
) -> None:
    contract_path = tmp_path / "contrat.yaml"
    _write(contract_path, _contract("1SPE-TEST", "1SPE", capacities=2))

    contract = inventory_module.load_contract(contract_path)

    assert contract["chapitre"] == "1SPE-TEST"
    assert [capacity["code"] for capacity in contract["capacites"]] == ["C1", "C2"]


def test_read_meta_validates_required_fields(tmp_path: Path, inventory_module) -> None:
    valid_path = tmp_path / "valid.tex"
    missing_id_path = tmp_path / "missing-id.tex"
    invalid_json_path = tmp_path / "invalid-json.tex"
    _write(valid_path, _meta())
    _write(
        missing_id_path,
        '% META: {"chapitre": "1SPE-TEST", "type_objet": "cours", "status": "generated"}\n',
    )
    _write(invalid_json_path, "% META: pas-du-json\n")

    assert inventory_module.read_meta(valid_path)["id"] == "1SPE-TEST-COURS-C1"
    with pytest.raises(inventory_module.MetadataError, match="id"):
        inventory_module.read_meta(missing_id_path)
    with pytest.raises(inventory_module.MetadataError, match="JSON"):
        inventory_module.read_meta(invalid_json_path)


def test_non_string_subtype_is_reported_as_invalid_metadata_without_crashing(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    contract = f"{base}/contrat.yaml"
    invalid = f"{base}/cours/invalid-subtype.tex"
    _write(tmp_path / contract, _contract("1SPE-TEST", "1SPE", capacities=1))
    _write(tmp_path / invalid, _meta(sous_type=["diagnostic"]))
    _track(tmp_path, contract, invalid)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["metadata_invalid"] == [
        {"path": invalid, "reason": "champ META sous_type invalide: texte attendu"}
    ]
    assert inventory["manuals"]["1SPE"]["chapters"]["1SPE-TEST"]["objects"] == []


@pytest.mark.parametrize(
    ("source_type", "source_subtype", "expected"),
    [
        ("cours", None, "sections_cours"),
        ("cours", "diagnostic", "diagnostics"),
        ("cours", "td_contextualise", "td"),
        ("cours", "td_fil_rouge", "td"),
        ("cours", "ouverture", None),
        ("methode", None, "methodes"),
        ("exercice", None, "exercices_principaux"),
        ("corrige", None, "corriges"),
        ("corrige_evaluation", None, "corriges"),
        ("evaluation_corrige", None, "corriges"),
        ("coup_de_pouce", None, "coups_de_pouce"),
        ("qcm", None, "qcm"),
        ("qcm_diagnostics", None, "diagnostics"),
        ("remediation", None, "remediations"),
        ("td", None, "td"),
        ("evaluation", None, "evaluations"),
        ("projet", None, "projets"),
        ("amenagee", None, None),
    ],
)
def test_canonical_category_preserves_required_taxonomy(
    source_type: str,
    source_subtype: str | None,
    expected: str | None,
    inventory_module,
) -> None:
    assert inventory_module.canonical_category(source_type, source_subtype) == expected


def test_subtype_priority_changes_counts_but_preserves_source_taxonomy(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        f"{base}/cours/diagnostic.tex": _meta(
            id="1SPE-TEST-DIAG", sous_type="diagnostic"
        ),
        f"{base}/cours/ouverture.tex": _meta(
            id="1SPE-TEST-OPEN", sous_type="ouverture"
        ),
        f"{base}/cours/td-context.tex": _meta(
            id="1SPE-TEST-TD-CONTEXT", sous_type="td_contextualise"
        ),
        f"{base}/cours/td-fil.tex": _meta(
            id="1SPE-TEST-TD-FIL", sous_type="td_fil_rouge"
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    chapter = inventory_module.build_inventory(tmp_path)["manuals"]["1SPE"]["chapters"][
        "1SPE-TEST"
    ]

    assert chapter["counts"]["sections_cours"] == 0
    assert chapter["counts"]["diagnostics"] == 1
    assert chapter["counts"]["td"] == 2
    assert chapter["source_taxonomy"] == {"cours": 4}
    assert chapter["source_subtypes"] == {
        "diagnostic": 1,
        "ouverture": 1,
        "td_contextualise": 1,
        "td_fil_rouge": 1,
    }


def test_build_inventory_aggregates_objects_and_keeps_six_manuals(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    math_base = _chapter_path("1SPE", "1SPE-TEST")
    nsi_base = _chapter_path("1NSI", "1NSI-TEST")
    sources = {
        f"{math_base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=2),
        f"{math_base}/cours/c1.tex": _meta(),
        f"{math_base}/methodes/m1.tex": _meta(id="1SPE-TEST-M1", type_objet="methode"),
        f"{math_base}/exercices/e1.tex": _meta(
            id="1SPE-TEST-EX-001", type_objet="exercice"
        ),
        f"{math_base}/corriges/co1.tex": _meta(
            id="1SPE-TEST-CO-001", type_objet="corrige"
        ),
        f"{math_base}/exercices/e1-cdp.tex": _meta(
            id="1SPE-TEST-EX-001-CDP", type_objet="coup_de_pouce"
        ),
        f"{math_base}/qcm/qcm.tex": _meta(id="1SPE-TEST-QCM", type_objet="qcm"),
        f"{math_base}/qcm/diag.tex": _meta(
            id="1SPE-TEST-QCM-DIAG", type_objet="qcm_diagnostics"
        ),
        f"{math_base}/remediation/r1.tex": _meta(
            id="1SPE-TEST-REM-001", type_objet="remediation"
        ),
        f"{math_base}/td/td.tex": _meta(id="1SPE-TEST-TD", type_objet="td"),
        f"{math_base}/evaluations/eval.tex": _meta(
            id="1SPE-TEST-EVAL", type_objet="evaluation"
        ),
        f"{math_base}/projets/projet.tex": _meta(
            id="1SPE-TEST-PROJET", type_objet="projet"
        ),
        f"{math_base}/evaluations/corrige.tex": _meta(
            id="1SPE-TEST-EVAL-CO", type_objet="corrige_evaluation"
        ),
        f"{nsi_base}/contrat.yaml": _contract("1NSI-TEST", "1NSI", capacities=1),
        f"{nsi_base}/cours/c1.tex": _meta(
            id="1NSI-TEST-COURS-C1",
            chapitre="1NSI-TEST",
            type_objet="cours",
            status="approved",
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)

    assert list(inventory["manuals"]) == [
        "1NSI",
        "1SPE",
        "TCOMPL",
        "TEXPERTES",
        "TNSI",
        "TSPE_2026_2027",
    ]
    chapter = inventory["manuals"]["1SPE"]["chapters"]["1SPE-TEST"]
    assert chapter["counts"] == {
        "capacites": 2,
        "sections_cours": 1,
        "methodes": 1,
        "exercices_principaux": 1,
        "corriges": 2,
        "coups_de_pouce": 1,
        "qcm": 1,
        "diagnostics": 1,
        "remediations": 1,
        "td": 1,
        "evaluations": 1,
        "projets": 1,
    }
    assert chapter["source_taxonomy"] == {
        "corrige": 1,
        "corrige_evaluation": 1,
        "coup_de_pouce": 1,
        "cours": 1,
        "evaluation": 1,
        "exercice": 1,
        "methode": 1,
        "projet": 1,
        "qcm": 1,
        "qcm_diagnostics": 1,
        "remediation": 1,
        "td": 1,
    }
    assert chapter["statuses"] == {"generated": 12}
    assert inventory["manuals"]["1SPE"]["totals"] == chapter["counts"]
    assert inventory["manuals"]["1NSI"]["totals"]["capacites"] == 1
    assert inventory["manuals"]["TNSI"]["chapters"] == {}
    assert inventory["manuals"]["TSPE_2026_2027"]["chapters"] == {}


def test_build_inventory_reports_metadata_ids_and_blocking_statuses(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1NSI", "1NSI-TEST")
    sources = {
        f"{base}/contrat.yaml": _contract("1NSI-TEST", "1NSI", capacities=1).replace(
            "statut: approved", "statut: draft"
        ),
        f"{base}/cours/valid.tex": _meta(
            id="DUPLICATE-ID", chapitre="1NSI-TEST", status="needs_review"
        ),
        f"{base}/methodes/duplicate.tex": _meta(
            id="DUPLICATE-ID",
            chapitre="1NSI-TEST",
            type_objet="methode",
            status="generated",
        ),
        f"{base}/cours/no-meta.tex": "Contenu sans en-tete META\n",
        f"{base}/cours/invalid.tex": "% META: {json invalide}\n",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    anomalies = inventory["anomalies"]

    assert anomalies["metadata_missing"] == [
        {"path": f"{base}/cours/no-meta.tex", "reason": "en-tete % META absent"}
    ]
    assert anomalies["metadata_invalid"][0]["path"] == f"{base}/cours/invalid.tex"
    assert anomalies["duplicate_ids"] == [
        {
            "id": "DUPLICATE-ID",
            "paths": [
                f"{base}/cours/valid.tex",
                f"{base}/methodes/duplicate.tex",
            ],
        }
    ]
    assert anomalies["blocking_statuses"] == [
        {
            "chapter": "1NSI-TEST",
            "id": None,
            "manual": "1NSI",
            "path": f"{base}/contrat.yaml",
            "scope": "contract",
            "status": "draft",
        },
        {
            "chapter": "1NSI-TEST",
            "id": "DUPLICATE-ID",
            "manual": "1NSI",
            "path": f"{base}/cours/valid.tex",
            "scope": "object",
            "status": "needs_review",
        },
        {
            "chapter": "1NSI-TEST",
            "id": "DUPLICATE-ID",
            "manual": "1NSI",
            "path": f"{base}/methodes/duplicate.tex",
            "scope": "object",
            "status": "generated",
        },
    ]


def test_build_inventory_keeps_raw_anomalies_unqualified(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    contract = f"{base}/contrat.yaml"
    missing_meta = f"{base}/cours/no-meta.tex"
    dispositions = "audit/ANOMALY_DISPOSITIONS.yaml"
    _write(tmp_path / contract, _contract("1SPE-TEST", "1SPE", capacities=1))
    _write(tmp_path / missing_meta, "Contenu sans en-tete META\n")
    _write(tmp_path / dispositions, "{}\n")
    _track(tmp_path, contract, missing_meta, dispositions)

    inventory = inventory_module.build_inventory(tmp_path)
    anomaly = inventory["anomalies"]["metadata_missing"][0]

    assert anomaly == {"path": missing_meta, "reason": "en-tete % META absent"}
    assert {"source", "fingerprint", "disposition", "blocking"}.isdisjoint(anomaly)


def test_build_inventory_artifacts_renders_markdown_without_parsing_it_as_yaml(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        f"{base}/cours/c1.tex": _meta(status="approved"),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)
    _commit_repository(tmp_path, "sources")

    result = inventory_module.build_inventory_artifacts(tmp_path)

    assert set(result["artifacts"]) == {
        "audit",
        "ecarts",
        "etat",
        "json",
        "markdown",
        "matrice",
    }
    for relative_path in result["artifacts"].values():
        artifact = tmp_path / relative_path
        assert artifact.is_file()
        content = artifact.read_text(encoding="utf-8")
        assert content.strip()
        if artifact.suffix == ".json":
            assert isinstance(json.loads(content), dict)
        elif artifact.suffix in {".yaml", ".yml"}:
            assert isinstance(yaml.safe_load(content), dict)


@pytest.mark.parametrize(
    ("basename", "artifact_type", "loader"),
    [
        pytest.param(
            "INVENTAIRE_COLLECTION.json",
            "inventory_collection",
            json.loads,
            id="inventory-json",
        ),
        pytest.param(
            "ECARTS_ET_CONTRADICTIONS.yaml",
            "ecarts_et_contradictions",
            yaml.safe_load,
            id="ecarts-yaml",
        ),
        pytest.param(
            "MATRICE_LIVRABLES.yaml",
            "matrice_livrables",
            yaml.safe_load,
            id="matrice-yaml",
        ),
    ],
)
def test_machine_artifacts_parse_and_validate_against_their_versioned_schema(
    tmp_path: Path,
    inventory_module,
    basename: str,
    artifact_type: str,
    loader,
) -> None:
    inventory = _minimal_inventory(tmp_path, inventory_module)
    rendered = inventory_module._render_inventory_artifacts(
        inventory,
        repo_root=ROOT,
        audit_root=tmp_path / "rendered",
    )

    content = next(value for path, value in rendered.items() if path.name == basename)
    payload = loader(content)

    assert payload["schema_version"] == 1
    assert payload["artifact_type"] == artifact_type
    assert payload["schema_ref"] == inventory_module._schema_ref_for(
        artifact_type, 1
    )
    assert payload["source_digest"] == inventory["source_digest"]
    assert payload["model_digest"].startswith("sha256:")
    assert payload["provenance"] == inventory["provenance"]
    schema = inventory_module._load_artifact_schema(
        ROOT,
        artifact_type=artifact_type,
        schema_version=payload["schema_version"],
        schema_ref=payload["schema_ref"],
    )
    jsonschema.Draft202012Validator(schema).validate(payload)


@pytest.mark.parametrize(
    "schema_name",
    [
        "inventory-collection.schema.json",
        "ecarts-et-contradictions.schema.json",
        "matrice-livrables.schema.json",
        "source-roles.schema.json",
        "anomaly-dispositions.schema.json",
        "anomalies-baseline.schema.json",
        "build-manifest.schema.json",
        "build-producers.schema.json",
    ],
)
def test_v1_json_schemas_are_valid_draft_2020_12(schema_name: str) -> None:
    schema_path = ROOT / "audit/schemas/v1" / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    jsonschema.Draft202012Validator.check_schema(schema)


def test_v1_schema_directory_contains_exactly_the_registered_contracts(
    inventory_module,
) -> None:
    registered = {
        Path(schema_ref).name
        for versions in inventory_module.SCHEMA_REGISTRY.values()
        for schema_ref in versions.values()
    }
    present = {
        path.name for path in (ROOT / "audit/schemas/v1").glob("*.schema.json")
    }

    assert present == registered


def test_qualification_schemas_are_registered(inventory_module) -> None:
    assert inventory_module._schema_ref_for(
        "baseline_qualification_policy",
        1,
    ) == "audit/schemas/v1/baseline-qualification-policy.schema.json"
    assert inventory_module._schema_ref_for(
        "unqualified_anomalies",
        1,
    ) == "audit/schemas/v1/unqualified-anomalies.schema.json"


def test_build_producers_schema_is_registered(inventory_module) -> None:
    assert inventory_module._schema_ref_for("build_producers", 1) == (
        "audit/schemas/v1/build-producers.schema.json"
    )


def _build_producers_payload(inventory_module, producers=None):
    payload = {
        "artifact_type": "build_producers",
        "control_digest": "sha256:" + "0" * 64,
        "producers": producers
        or [
            {
                "producer_id": "math-1spe-manual",
                "assembler": (
                    "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
                ),
                "recorder": "scripts/build_manifest.py",
                "assembly_ids": [
                    "math:manual:1SPE:eleve",
                    "math:manual:1SPE:professeur",
                ],
            }
        ],
        "schema_ref": "audit/schemas/v1/build-producers.schema.json",
        "schema_version": 1,
    }
    payload["control_digest"] = inventory_module._control_digest(payload)
    return payload


def _write_build_producers_fixture(repository, inventory_module, producers=None):
    _init_repository(repository)
    _install_audit_schemas(repository)
    paths = {
        "Mathematiques/manuel-maths/scripts/assemble_manuel.py": "# assembler\n",
        "scripts/build_manifest.py": "# recorder\n",
    }
    for relative, content in paths.items():
        _write(repository / relative, content)
    payload = _build_producers_payload(inventory_module, producers)
    _write(
        repository / "audit/BUILD_PRODUCERS.yaml",
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
    )
    _track(
        repository,
        *paths,
        "audit/BUILD_PRODUCERS.yaml",
        "audit/schemas/v1/build-producers.schema.json",
    )
    return payload


def test_build_producers_control_loads_canonical_tracked_producer(
    tmp_path: Path,
    inventory_module,
) -> None:
    payload = _write_build_producers_fixture(tmp_path, inventory_module)

    assert inventory_module._load_build_producers(tmp_path) == payload["producers"]


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        pytest.param("digest", "control_digest", id="digest-drift"),
        pytest.param("duplicate-id", "producer_id", id="duplicate-producer-id"),
        pytest.param(
            "duplicate-assembly",
            "assembly_id",
            id="duplicate-assembly-coverage",
        ),
        pytest.param("absolute", "assembler", id="absolute-assembler"),
        pytest.param("traversal", "assembler", id="traversing-assembler"),
        pytest.param("missing", "assembleur", id="missing-assembler"),
        pytest.param("untracked", "suivi", id="untracked-assembler"),
        pytest.param("symlink", "symbolique", id="symlink-assembler"),
        pytest.param("recorder", "recorder", id="non-canonical-recorder"),
        pytest.param("producer-order", "ordre", id="producer-order"),
        pytest.param("assembly-order", "ordre", id="assembly-order"),
    ],
)
def test_build_producers_control_rejects_invalid_or_unproved_producer(
    tmp_path: Path,
    inventory_module,
    mutation: str,
    expected: str,
) -> None:
    second = {
        "producer_id": "math-1spe-secondary",
        "assembler": "scripts/secondary_assembler.py",
        "recorder": "scripts/build_manifest.py",
        "assembly_ids": ["math:manual:1SPE:secondary"],
    }
    producers = _build_producers_payload(inventory_module)["producers"]
    if mutation in {"duplicate-id", "duplicate-assembly", "producer-order"}:
        producers.append(second)
    payload = _write_build_producers_fixture(
        tmp_path,
        inventory_module,
        producers,
    )
    if mutation in {"duplicate-id", "producer-order"}:
        _write(tmp_path / "scripts/secondary_assembler.py", "# secondary\n")
        _track(tmp_path, "scripts/secondary_assembler.py")
    if mutation == "digest":
        payload["control_digest"] = "sha256:" + "f" * 64
    elif mutation == "duplicate-id":
        payload["producers"][1]["producer_id"] = "math-1spe-manual"
    elif mutation == "duplicate-assembly":
        payload["producers"][1]["assembly_ids"] = [
            "math:manual:1SPE:eleve"
        ]
    elif mutation == "absolute":
        payload["producers"][0]["assembler"] = "/tmp/assembler.py"
    elif mutation == "traversal":
        payload["producers"][0]["assembler"] = "../assembler.py"
    elif mutation == "missing":
        payload["producers"][0]["assembler"] = "scripts/missing.py"
    elif mutation == "untracked":
        _write(tmp_path / "scripts/untracked.py", "# untracked\n")
        payload["producers"][0]["assembler"] = "scripts/untracked.py"
    elif mutation == "symlink":
        symlink = tmp_path / "scripts/symlink.py"
        symlink.symlink_to("build_manifest.py")
        _track(tmp_path, "scripts/symlink.py")
        payload["producers"][0]["assembler"] = "scripts/symlink.py"
    elif mutation == "recorder":
        payload["producers"][0]["recorder"] = "scripts/other_recorder.py"
    elif mutation == "producer-order":
        payload["producers"].reverse()
    elif mutation == "assembly-order":
        payload["producers"][0]["assembly_ids"].reverse()
    if mutation != "digest":
        payload["control_digest"] = inventory_module._control_digest(payload)
    _write(
        tmp_path / "audit/BUILD_PRODUCERS.yaml",
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
    )

    with pytest.raises(inventory_module.InventoryError, match=expected):
        inventory_module._load_build_producers(tmp_path)


def test_harvest_candidate_is_a_non_blocking_disposition(
    inventory_module,
) -> None:
    assert "harvest_candidate" in inventory_module.ANOMALY_DISPOSITIONS
    assert (
        inventory_module.ANOMALY_DISPOSITION_BLOCKS["harvest_candidate"]
        is False
    )


def test_materialize_baseline_qualifications_check_is_read_only(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    subprocess.run(
        [
            "git",
            "clone",
            "-q",
            "--no-hardlinks",
            str(ROOT),
            str(repository),
        ],
        check=True,
    )
    for relative in (
        "audit/BASELINE_QUALIFICATION_POLICY.yaml",
        "audit/schemas/v1/anomaly-dispositions.schema.json",
        "audit/schemas/v1/baseline-qualification-policy.schema.json",
        "audit/schemas/v1/unqualified-anomalies.schema.json",
    ):
        destination = repository / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)
    # Le manifeste observé est hors du contrat one-shot de cette fixture. Le
    # retirer du clone évite qu'un digest historique du worktree réel rende le
    # test CLI dépendant de l'ordre des lots locaux.
    (repository / "audit/BUILD_MANIFEST.json").unlink(missing_ok=True)
    destinations = (
        repository / "audit/ANOMALY_DISPOSITIONS.yaml",
        repository / "audit/UNQUALIFIED_ANOMALIES.json",
        repository / "audit/UNQUALIFIED_ANOMALIES.md",
    )
    before_destinations = {
        path: path.read_bytes() if path.exists() else None
        for path in destinations
    }
    before = _git_status_bytes(repository)

    result = _run_inventory_cli(
        repository,
        "--materialize-baseline-qualifications",
        "--check",
    )

    payload = json.loads(result.stdout)
    assert payload["gate"] == "materialize-baseline-qualifications"
    assert payload["approved_fingerprint_count"] == 189
    assert payload["unqualified"] == 0
    assert result.returncode in {0, 3}
    assert (result.returncode == 0) is (payload["diffs"] == [])
    assert set(payload["diffs"]) <= {
        "audit/ANOMALY_DISPOSITIONS.yaml",
        "audit/UNQUALIFIED_ANOMALIES.json",
        "audit/UNQUALIFIED_ANOMALIES.md",
    }
    assert {
        path: path.read_bytes() if path.exists() else None
        for path in destinations
    } == before_destinations
    assert _git_status_bytes(repository) == before


def test_materialization_revalidations_use_only_the_owned_lock_identity(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    subprocess.run(
        [
            "git",
            "clone",
            "-q",
            "--no-hardlinks",
            str(ROOT),
            str(repository),
        ],
        check=True,
    )
    original_lock = inventory_module._lock_generation
    original_plan = inventory_module._baseline_materialization_plan
    original_manifest_loader = inventory_module._load_observed_build_manifest
    lock_identities: list[dict[str, tuple[int, int]]] = []
    plan_lock_arguments: list[dict[str, tuple[int, int]] | None] = []
    manifest_lock_arguments: list[dict[str, tuple[int, int]] | None] = []

    @contextmanager
    def observed_lock(root: Path):
        with original_lock(root) as lock_identity:
            lock_identities.append(lock_identity)
            arbitrary = root / "notes-utilisateur.txt"
            _write(arbitrary, "WIP utilisateur\n")
            assert inventory_module._observed_git_state(
                root,
                allowed_generation_paths=lock_identity,
            )[2] is True
            arbitrary.unlink()
            yield lock_identity

    def observed_plan(
        root: Path,
        *,
        owned_generation_lock: dict[str, tuple[int, int]] | None = None,
    ) -> dict[str, object]:
        plan_lock_arguments.append(
            dict(owned_generation_lock)
            if owned_generation_lock is not None
            else None
        )
        if owned_generation_lock is None:
            return original_plan(root)
        arbitrary = root / "notes-utilisateur.txt"
        _write(arbitrary, "WIP utilisateur\n")
        assert inventory_module._observed_git_state(
            root,
            allowed_generation_paths=owned_generation_lock,
        )[2] is True
        arbitrary.unlink()
        return original_plan(
            root,
            owned_generation_lock=owned_generation_lock,
        )

    def observed_manifest_loader(
        root: Path,
        *,
        owned_generation_lock: dict[str, tuple[int, int]] | None = None,
        **kwargs: object,
    ) -> list[dict[str, object]]:
        manifest_lock_arguments.append(
            dict(owned_generation_lock)
            if owned_generation_lock is not None
            else None
        )
        return original_manifest_loader(
            root,
            owned_generation_lock=owned_generation_lock,
            **kwargs,
        )

    monkeypatch.setattr(inventory_module, "_lock_generation", observed_lock)
    monkeypatch.setattr(
        inventory_module,
        "_baseline_materialization_plan",
        observed_plan,
    )
    monkeypatch.setattr(
        inventory_module,
        "_load_observed_build_manifest",
        observed_manifest_loader,
    )
    result = inventory_module._safe_materialize_baseline_qualifications(
        repository,
        check_only=False,
    )

    assert result["reasons"] == []
    assert result["success"] is True
    assert len(lock_identities) == 1
    owned_identity = lock_identities[0]
    assert set(owned_identity) == {inventory_module.GENERIC_LOCK_FILE}
    assert plan_lock_arguments[:2] == [None, owned_identity]
    assert len(plan_lock_arguments) == 3
    staged_identity = plan_lock_arguments[2]
    assert staged_identity is not None
    assert staged_identity[inventory_module.GENERIC_LOCK_FILE] == (
        owned_identity[inventory_module.GENERIC_LOCK_FILE]
    )
    transaction_paths = set(staged_identity) - {
        inventory_module.GENERIC_LOCK_FILE
    }
    assert transaction_paths
    assert all(
        re.fullmatch(
            r"\.inventory-collection-apply-[0-9a-f]{24}/"
            r"(?:transaction-owner|preparing\.json|journal\.json|"
            r"journal-ready|(?:stage|backup)-[0-9]{8})",
            path,
        )
        for path in transaction_paths
    )
    assert manifest_lock_arguments == plan_lock_arguments
    assert "owned_generation_lock" not in inspect.signature(
        inventory_module.build_inventory
    ).parameters
    assert _git_status_bytes(repository) == b""
    assert not list(repository.glob(".inventory-collection-apply-*"))
    assert not (repository / inventory_module.GENERIC_LOCK_FILE).exists()


def _synthetic_materialization_plan(
    *,
    marker: str = "stable",
    unqualified: int = 0,
) -> dict[str, object]:
    anomalies = [
        {
            "category": "unknown",
            "chapter": None,
            "fingerprint": f"{index:016x}",
            "manual": None,
            "reason": "no_policy_rule",
            "source": "unknown.tex",
        }
        for index in range(unqualified)
    ]
    rendered = {
        Path("audit/UNQUALIFIED_ANOMALIES.json"): (
            json.dumps({"marker": marker, "anomalies": anomalies}) + "\n"
        ),
        Path("audit/UNQUALIFIED_ANOMALIES.md"): (
            f"# Non qualifiées\n\n{marker}: {unqualified}\n"
        ),
    }
    if not anomalies:
        rendered[Path("audit/ANOMALY_DISPOSITIONS.yaml")] = (
            f"marker: {marker}\n"
        )
    return {
        "approved_fingerprint_count": 2457,
        "approved_fingerprint_digest": "sha256:" + "a" * 64,
        "observed_model_digest": "sha256:" + "b" * 64,
        "observed_source_digest": "sha256:" + "c" * 64,
        "owner_counts": {
            "direction_editoriale_pedagogique": 328,
            "direction_scientifique_programme": 1473,
            "ingenierie_build_qualite": 656,
        },
        "rendered": rendered,
        "unqualified": anomalies,
    }


@pytest.mark.parametrize("unqualified", [1, 2])
def test_materialization_writes_only_unqualified_reports_when_policy_cannot_decide(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    unqualified: int,
) -> None:
    plan = _synthetic_materialization_plan(
        marker="ambiguous" if unqualified == 2 else "absent",
        unqualified=unqualified,
    )
    monkeypatch.setattr(
        inventory_module,
        "_baseline_materialization_plan",
        lambda _root, **_kwargs: deepcopy(plan),
    )
    monkeypatch.setattr(
        inventory_module,
        "_repo_head_sha",
        lambda _root, *, required: "a" * 40,
    )

    result = inventory_module._safe_materialize_baseline_qualifications(
        tmp_path,
        check_only=False,
    )

    assert result["success"] is False
    assert result["exit_code"] == 3
    assert not (tmp_path / "audit/ANOMALY_DISPOSITIONS.yaml").exists()
    assert (tmp_path / "audit/UNQUALIFIED_ANOMALIES.json").is_file()
    assert (tmp_path / "audit/UNQUALIFIED_ANOMALIES.md").is_file()


def test_materialization_check_revalidates_changed_head(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = _synthetic_materialization_plan()
    for relative, content in plan["rendered"].items():  # type: ignore[union-attr]
        _write(tmp_path / relative, content)
    heads = iter(["a" * 40, "b" * 40])
    monkeypatch.setattr(
        inventory_module,
        "_repo_head_sha",
        lambda _root, *, required: next(heads),
    )
    monkeypatch.setattr(
        inventory_module,
        "_baseline_materialization_plan",
        lambda _root, **_kwargs: deepcopy(plan),
    )

    result = inventory_module._safe_materialize_baseline_qualifications(
        tmp_path,
        check_only=True,
    )

    assert result["success"] is False
    assert any("HEAD" in reason for reason in result["reasons"])


@pytest.mark.parametrize(
    ("field", "changed"),
    [
        ("observed_source_digest", "sha256:" + "d" * 64),
        ("observed_model_digest", "sha256:" + "e" * 64),
        ("approved_fingerprint_digest", "sha256:" + "f" * 64),
    ],
)
def test_materialization_check_revalidates_all_approved_digests(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    changed: str,
) -> None:
    first = _synthetic_materialization_plan()
    second = deepcopy(first)
    second[field] = changed
    for relative, content in first["rendered"].items():  # type: ignore[union-attr]
        _write(tmp_path / relative, content)
    plans = iter([first, second])
    monkeypatch.setattr(
        inventory_module,
        "_repo_head_sha",
        lambda _root, *, required: "a" * 40,
    )
    monkeypatch.setattr(
        inventory_module,
        "_baseline_materialization_plan",
        lambda _root, **_kwargs: deepcopy(next(plans)),
    )

    result = inventory_module._safe_materialize_baseline_qualifications(
        tmp_path,
        check_only=True,
    )

    assert result["success"] is False
    assert any("modifié" in reason for reason in result["reasons"])


@pytest.mark.parametrize("attack", ["symlink", "hardlink", "directory"])
def test_materialization_cli_transaction_rejects_path_substitution(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    attack: str,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    repository.mkdir()
    outside.mkdir()
    sentinel = outside / "sentinel.txt"
    sentinel.write_text("historique\n", encoding="utf-8")
    target = repository / "audit/ANOMALY_DISPOSITIONS.yaml"
    if attack == "directory":
        (repository / "audit").symlink_to(outside, target_is_directory=True)
    else:
        target.parent.mkdir()
        if attack == "symlink":
            target.symlink_to(sentinel)
        else:
            os.link(sentinel, target)
    plan = _synthetic_materialization_plan()
    monkeypatch.setattr(
        inventory_module,
        "_repo_head_sha",
        lambda _root, *, required: "a" * 40,
    )
    monkeypatch.setattr(
        inventory_module,
        "_baseline_materialization_plan",
        lambda _root, **_kwargs: deepcopy(plan),
    )

    result = inventory_module._safe_materialize_baseline_qualifications(
        repository,
        check_only=False,
    )

    assert result["success"] is False
    assert sentinel.read_text(encoding="utf-8") == "historique\n"
    assert not (outside / "UNQUALIFIED_ANOMALIES.json").exists()
    assert not (outside / "UNQUALIFIED_ANOMALIES.md").exists()


def test_materialization_cli_rolls_back_all_outputs_on_apply_failure(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in (
        "ANOMALY_DISPOSITIONS.yaml",
        "UNQUALIFIED_ANOMALIES.json",
        "UNQUALIFIED_ANOMALIES.md",
    ):
        _write(tmp_path / "audit" / name, f"historique {name}\n")
    before = {
        path: path.read_bytes() for path in sorted((tmp_path / "audit").iterdir())
    }
    plan = _synthetic_materialization_plan(marker="nouveau")
    monkeypatch.setattr(
        inventory_module,
        "_repo_head_sha",
        lambda _root, *, required: "a" * 40,
    )
    monkeypatch.setattr(
        inventory_module,
        "_baseline_materialization_plan",
        lambda _root, **_kwargs: deepcopy(plan),
    )
    original_replace = inventory_module.os.replace
    forward_replacements = 0

    def fail_second_forward_replace(
        source: str,
        destination: str,
        **kwargs: object,
    ) -> None:
        nonlocal forward_replacements
        if str(source).startswith("stage-"):
            forward_replacements += 1
            if forward_replacements == 2:
                raise OSError("injection crash matérialisation")
        original_replace(source, destination, **kwargs)

    monkeypatch.setattr(
        inventory_module.os,
        "replace",
        fail_second_forward_replace,
    )

    result = inventory_module._safe_materialize_baseline_qualifications(
        tmp_path,
        check_only=False,
    )

    assert result["success"] is False
    assert {path: path.read_bytes() for path in before} == before
    preserved = list(
        (tmp_path / "audit").glob(
            ".inventory-collection-rollback-*.tmp"
        )
    )
    assert len(preserved) == 1
    assert b"nouveau" in preserved[0].read_bytes()
    assert "preserved rollback entry" in " ".join(result["reasons"])
    assert list(tmp_path.glob(".inventory-collection-apply-*")) == []


def test_materialization_transaction_revalidates_digests_after_staging(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in (
        "ANOMALY_DISPOSITIONS.yaml",
        "UNQUALIFIED_ANOMALIES.json",
        "UNQUALIFIED_ANOMALIES.md",
    ):
        _write(tmp_path / "audit" / name, f"historique {name}\n")
    before = {
        path: path.read_bytes()
        for path in sorted((tmp_path / "audit").iterdir())
    }
    stable = _synthetic_materialization_plan(marker="stable")
    changed = deepcopy(stable)
    changed["observed_source_digest"] = "sha256:" + "f" * 64
    drifted = False

    monkeypatch.setattr(
        inventory_module,
        "_repo_head_sha",
        lambda _root, *, required: "a" * 40,
    )
    monkeypatch.setattr(
        inventory_module,
        "_baseline_materialization_plan",
        lambda _root, **_kwargs: deepcopy(changed if drifted else stable),
    )
    real_write_entry = inventory_module._write_transaction_entry

    def mutate_after_staging(
        directory_fd: int,
        name: str,
        payload: bytes,
    ):
        nonlocal drifted
        result = real_write_entry(directory_fd, name, payload)
        if name == "journal-ready":
            drifted = True
        return result

    monkeypatch.setattr(
        inventory_module,
        "_write_transaction_entry",
        mutate_after_staging,
    )

    result = inventory_module._safe_materialize_baseline_qualifications(
        tmp_path,
        check_only=False,
    )

    assert result["success"] is False
    assert any("digests" in reason or "modifiés" in reason for reason in result["reasons"])
    assert {
        path: path.read_bytes()
        for path in sorted((tmp_path / "audit").iterdir())
    } == before
    assert list(tmp_path.glob(".inventory-collection-apply-*")) == []


def test_materialization_cli_recovers_previous_process_crash_before_writing(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    historical = {
        "ANOMALY_DISPOSITIONS.yaml": "dispositions historiques\n",
        "UNQUALIFIED_ANOMALIES.json": "json historique\n",
        "UNQUALIFIED_ANOMALIES.md": "markdown historique\n",
    }
    for name, content in historical.items():
        _write(tmp_path / "audit" / name, content)
    child_code = f"""
import importlib.util
import os
from pathlib import Path

spec = importlib.util.spec_from_file_location("inventory_collection", {str(SCRIPT)!r})
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original_replace = module.os.replace

def crash_after_first_replace(source, target, **kwargs):
    original_replace(source, target, **kwargs)
    if str(source).startswith("stage-"):
        os._exit(98)

module.os.replace = crash_after_first_replace
module._apply_atomic_payloads(
    Path({str(tmp_path)!r}),
    {{
        Path("audit/ANOMALY_DISPOSITIONS.yaml"): "dispositions crash\\n",
        Path("audit/UNQUALIFIED_ANOMALIES.json"): "json crash\\n",
        Path("audit/UNQUALIFIED_ANOMALIES.md"): "markdown crash\\n",
    }},
)
"""
    crashed = subprocess.run([sys.executable, "-c", child_code], check=False)
    assert crashed.returncode == 98
    assert list(tmp_path.glob(".inventory-collection-apply-*"))

    plan = _synthetic_materialization_plan(marker="après récupération")
    monkeypatch.setattr(
        inventory_module,
        "_repo_head_sha",
        lambda _root, *, required: "a" * 40,
    )
    monkeypatch.setattr(
        inventory_module,
        "_baseline_materialization_plan",
        lambda _root, **_kwargs: deepcopy(plan),
    )

    def stop_before_new_write(*_args: object, **_kwargs: object) -> None:
        raise OSError("arrêt après récupération CLI")

    monkeypatch.setattr(
        inventory_module,
        "_apply_atomic_payloads",
        stop_before_new_write,
    )

    result = inventory_module._safe_materialize_baseline_qualifications(
        tmp_path,
        check_only=False,
    )

    assert result["success"] is False
    assert all(
        (tmp_path / "audit" / name).read_text(encoding="utf-8") == content
        for name, content in historical.items()
    )
    assert list(tmp_path.glob(".inventory-collection-apply-*")) == []


@pytest.mark.parametrize(
    "schema_name",
    ["source-roles.schema.json", "anomaly-dispositions.schema.json"],
)
def test_control_schemas_require_a_content_digest(schema_name: str) -> None:
    schema = json.loads(
        (ROOT / "audit/schemas/v1" / schema_name).read_text(encoding="utf-8")
    )

    assert "control_digest" in schema["required"]
    assert schema["properties"]["control_digest"] == {
        "type": "string",
        "pattern": "^sha256:[0-9a-f]{64}$",
    }


def _qualified_disposition_record(
    disposition: str, fingerprint: str
) -> dict[str, object]:
    return {
        "approved_by": "Responsable éditorial",
        "decision_ref": "DEC-2026-07-22-01",
        "disposition": disposition,
        "fingerprint": fingerprint,
        "justification": "Qualification humaine documentée.",
        "owner": "équipe éditoriale",
    }


def _dispositions_payload(record: dict[str, object]) -> dict[str, object]:
    fingerprint = str(record["fingerprint"])
    return {
        "artifact_type": "anomaly_dispositions",
        "control_digest": "sha256:" + "b" * 64,
        "dispositions": {fingerprint: record},
        "fingerprint_schema_version": 1,
        "schema_ref": "audit/schemas/v1/anomaly-dispositions.schema.json",
        "schema_version": 1,
    }


def _accepted_exception_dispositions_payload() -> dict[str, object]:
    fingerprint = "a" * 16
    record = {
        **_qualified_disposition_record("accepted_exception", fingerprint),
        "author": "Autrice de la décision",
        "blocking": False,
        "evidence": ["audit/decisions/DEC-2026-07-22-01.md"],
        "expiry": "2026-12-31",
        "scope": {"manual": "1SPE", "variant": "maquette"},
    }
    return _dispositions_payload(record)


def test_anomaly_dispositions_schema_accepts_contractual_accepted_exception() -> None:
    schema = json.loads(
        (
            ROOT / "audit/schemas/v1/anomaly-dispositions.schema.json"
        ).read_text(encoding="utf-8")
    )

    jsonschema.Draft202012Validator(schema).validate(
        _accepted_exception_dispositions_payload()
    )


def test_anomaly_dispositions_schema_accepts_qualified_open_debt() -> None:
    schema = json.loads(
        (
            ROOT / "audit/schemas/v1/anomaly-dispositions.schema.json"
        ).read_text(encoding="utf-8")
    )
    fingerprint = "c" * 16
    payload = _dispositions_payload(
        _qualified_disposition_record("open_debt", fingerprint)
    )

    jsonschema.Draft202012Validator(schema).validate(payload)


@pytest.mark.parametrize(
    "missing_field",
    [
        "baseline_sha",
        "category",
        "chapter",
        "fingerprint_schema_version",
        "manual",
        "policy_rule",
        "qualification_digest",
        "qualification_policy_digest",
        "reason",
        "release_blocking",
        "severity",
        "source",
    ],
)
def test_policy_generated_disposition_requires_materialization_contract(
    missing_field: str,
) -> None:
    schema = json.loads(
        (
            ROOT / "audit/schemas/v1/anomaly-dispositions.schema.json"
        ).read_text(encoding="utf-8")
    )
    fingerprint = "c" * 16
    record = {
        **_qualified_disposition_record("open_debt", fingerprint),
        "baseline_sha": "a" * 40,
        "category": "blocking_statuses",
        "chapter": None,
        "fingerprint_schema_version": 1,
        "manual": "1SPE",
        "policy_rule": "blocking-scientific-object",
        "qualification_digest": "sha256:" + "e" * 64,
        "qualification_policy_digest": "sha256:" + "d" * 64,
        "reason": "Dette active qualifiée par politique.",
        "release_blocking": True,
        "severity": "blocking",
        "source": "chapitres/C/cours/c.tex",
    }
    record.pop(missing_field)

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(
            _dispositions_payload(record)
        )


@pytest.mark.parametrize(
    "missing_field",
    [
        "approved_by",
        "decision_ref",
        "disposition",
        "fingerprint",
        "justification",
        "owner",
    ],
)
def test_anomaly_dispositions_schema_rejects_record_missing_common_field(
    missing_field: str,
) -> None:
    schema = json.loads(
        (
            ROOT / "audit/schemas/v1/anomaly-dispositions.schema.json"
        ).read_text(encoding="utf-8")
    )
    fingerprint = "c" * 16
    record = _qualified_disposition_record("open_debt", fingerprint)
    record.pop(missing_field)
    if missing_field == "fingerprint":
        record["fingerprint"] = fingerprint
        payload = _dispositions_payload(record)
        record.pop("fingerprint")
    else:
        payload = _dispositions_payload(record)

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


@pytest.mark.parametrize(
    "missing_field",
    [
        "approved_by",
        "author",
        "blocking",
        "decision_ref",
        "evidence",
        "expiry",
        "fingerprint",
        "justification",
        "owner",
        "scope",
    ],
)
def test_anomaly_dispositions_schema_rejects_incomplete_accepted_exception(
    missing_field: str,
) -> None:
    schema = json.loads(
        (
            ROOT / "audit/schemas/v1/anomaly-dispositions.schema.json"
        ).read_text(encoding="utf-8")
    )
    payload = _accepted_exception_dispositions_payload()
    fingerprint = "a" * 16
    disposition = dict(payload["dispositions"][fingerprint])  # type: ignore[index]
    disposition.pop(missing_field)
    payload["dispositions"] = {fingerprint: disposition}

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


@pytest.mark.parametrize(
    "disposition",
    ["false_positive", "generated_dependency", "intentional_reuse", "fixed"],
)
def test_anomaly_dispositions_schema_rejects_evidentiary_record_without_proof(
    disposition: str,
) -> None:
    schema = json.loads(
        (
            ROOT / "audit/schemas/v1/anomaly-dispositions.schema.json"
        ).read_text(encoding="utf-8")
    )
    fingerprint = "e" * 16
    payload = _dispositions_payload(
        _qualified_disposition_record(disposition, fingerprint)
    )

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


@pytest.mark.parametrize(
    "disposition",
    ["false_positive", "generated_dependency", "intentional_reuse", "fixed"],
)
def test_anomaly_dispositions_schema_documents_proof_alias(
    disposition: str,
) -> None:
    schema = json.loads(
        (
            ROOT / "audit/schemas/v1/anomaly-dispositions.schema.json"
        ).read_text(encoding="utf-8")
    )
    fingerprint = "f" * 16
    record = _qualified_disposition_record(disposition, fingerprint)
    record["proof"] = "audit/preuves/qualification.md"

    jsonschema.Draft202012Validator(schema).validate(_dispositions_payload(record))


def test_dispositions_control_file_is_schema_valid_and_digest_verified(
    inventory_module,
) -> None:
    path = ROOT / "audit/ANOMALY_DISPOSITIONS.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    schema = json.loads(
        (ROOT / "audit/schemas/v1/anomaly-dispositions.schema.json").read_text(
            encoding="utf-8"
        )
    )

    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["control_digest"] == inventory_module._control_digest(payload)
    dispositions = inventory_module._load_dispositions(ROOT)
    intentional = {
        fingerprint: record
        for fingerprint, record in dispositions.items()
        if record["disposition"] == "intentional_reuse"
    }
    generated = {
        fingerprint: record
        for fingerprint, record in dispositions.items()
        if record["disposition"] == "generated_dependency"
    }
    assert set(intentional) == {
        "19669084dffa5d5b",
        "2695d63b022fe9f0",
        "b912c1041392a181",
    }
    assert set(generated) == {"62c72a29cc4eedb7"}
    assert all(
        "Mathematiques/manuel-maths/build/maquette-v5/manifest.json"
        in str(record["proof"])
        for record in intentional.values()
    )


def test_repository_build_applies_qualification_view_without_mutating_raw_anomalies(
    inventory_module,
) -> None:
    inventory = inventory_module.build_inventory(ROOT)
    raw_duplicates = inventory["anomalies"]["duplicate_assembly_objects"]
    qualifications = inventory["anomaly_qualifications"]
    intentional_fingerprints = {
        "19669084dffa5d5b",
        "2695d63b022fe9f0",
        "b912c1041392a181",
    }

    assert len(raw_duplicates) == 3
    assert all(
        {"fingerprint", "disposition", "blocking"}.isdisjoint(anomaly)
        for anomaly in raw_duplicates
    )
    assert {
        fingerprint
        for fingerprint in intentional_fingerprints
        if qualifications[fingerprint]["disposition"] == "intentional_reuse"
        and qualifications[fingerprint]["blocking"] is False
    } == intentional_fingerprints
    blockers = inventory["deliverable_matrix"]["manuals"]["1SPE"]["blockers"]
    assert not any(
        blocker["code"] == "anomalie:duplicate_assembly_objects"
        for blocker in blockers
    )


def test_load_dispositions_rejects_envelope_digest_drift(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    payload = yaml.safe_load(
        (ROOT / "audit/ANOMALY_DISPOSITIONS.yaml").read_text(encoding="utf-8")
    )
    payload["fingerprint_schema_version"] = 2
    _write(
        tmp_path / "audit/ANOMALY_DISPOSITIONS.yaml",
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True),
    )

    with pytest.raises(inventory_module.InventoryError, match="control_digest"):
        inventory_module._load_dispositions(tmp_path)


def test_load_dispositions_rejects_unsupported_fingerprint_schema_version(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    payload = yaml.safe_load(
        (ROOT / "audit/ANOMALY_DISPOSITIONS.yaml").read_text(encoding="utf-8")
    )
    payload["fingerprint_schema_version"] = 2
    payload["control_digest"] = inventory_module._control_digest(payload)
    _write(
        tmp_path / "audit/ANOMALY_DISPOSITIONS.yaml",
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True),
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="fingerprint_schema_version",
    ):
        inventory_module._load_dispositions(tmp_path)


@pytest.mark.parametrize("expiry_field", ["expires_at", "expiry"])
def test_load_dispositions_rejects_invalid_expiry_at_load_time(
    tmp_path: Path,
    inventory_module,
    expiry_field: str,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    fingerprint = "a" * 16
    record = {
        **_qualified_disposition_record("accepted_exception", fingerprint),
        "author": "Responsable éditorial",
        "blocking": False,
        "proof": "audit/proofs/accepted-exception.md",
        "scope": {"manual": "1SPE"},
        expiry_field: "jamais",
    }
    payload = _dispositions_payload(record)
    payload["control_digest"] = inventory_module._control_digest(payload)
    _write(
        tmp_path / "audit/ANOMALY_DISPOSITIONS.yaml",
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True),
    )

    with pytest.raises(inventory_module.InventoryError, match="expiration"):
        inventory_module._load_dispositions(tmp_path)


def test_accepted_exception_rejects_both_expiry_aliases_in_loader_and_gates(
    tmp_path: Path,
    inventory_module,
) -> None:
    _seed_cli_repository(tmp_path)
    fingerprint = "a" * 16
    record = {
        **_qualified_disposition_record("accepted_exception", fingerprint),
        "author": "Responsable éditorial",
        "blocking": False,
        "proof": "audit/proofs/accepted-exception.md",
        "scope": {"manual": "1SPE"},
        "expires_at": "2026-12-31",
        "expiry": "2026-12-31",
    }
    payload = _dispositions_payload(record)
    payload["control_digest"] = inventory_module._control_digest(payload)
    _write(
        tmp_path / "audit/ANOMALY_DISPOSITIONS.yaml",
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True),
    )

    with pytest.raises(inventory_module.InventoryError, match="alias d.expiration"):
        inventory_module._load_dispositions(tmp_path)
    validate = inventory_module._validate_model_gate(tmp_path)
    release = inventory_module._release_strict_gate_for_root(tmp_path)
    assert validate["success"] is False
    assert any("alias d'expiration" in reason for reason in validate["reasons"])
    assert release["success"] is False
    assert any("alias d'expiration" in reason for reason in release["reasons"])


def test_invalid_expiry_blocks_inventory_generation_and_validate_model(
    tmp_path: Path,
    inventory_module,
) -> None:
    _seed_cli_repository(tmp_path)
    fingerprint = "a" * 16
    record = {
        **_qualified_disposition_record("accepted_exception", fingerprint),
        "author": "Responsable éditorial",
        "blocking": False,
        "proof": "audit/proofs/accepted-exception.md",
        "scope": {"manual": "1SPE"},
        "expires_at": "date-invalide",
    }
    payload = _dispositions_payload(record)
    payload["control_digest"] = inventory_module._control_digest(payload)
    _write(
        tmp_path / "audit/ANOMALY_DISPOSITIONS.yaml",
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True),
    )

    with pytest.raises(inventory_module.InventoryError, match="expiration"):
        inventory_module.build_inventory(tmp_path)
    gate = inventory_module._validate_model_gate(tmp_path)
    assert gate["success"] is False
    assert any("expiration" in reason for reason in gate["reasons"])


def test_dispositions_control_cannot_downgrade_to_legacy_when_schema_is_installed(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    _write(
        tmp_path / "audit/ANOMALY_DISPOSITIONS.yaml",
        "dispositions: {}\n",
    )

    with pytest.raises(inventory_module.InventoryError, match="contrôle versionné"):
        inventory_module._load_dispositions(tmp_path)


def test_load_dispositions_rejects_key_fingerprint_mismatch(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    record = {
        **_qualified_disposition_record("open_debt", "b" * 16),
    }
    payload = _dispositions_payload(record)
    payload["dispositions"] = {"a" * 16: record}
    payload["control_digest"] = inventory_module._control_digest(payload)
    _write(
        tmp_path / "audit/ANOMALY_DISPOSITIONS.yaml",
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True),
    )

    with pytest.raises(inventory_module.InventoryError, match="fingerprint"):
        inventory_module._load_dispositions(tmp_path)


@pytest.mark.parametrize(
    ("relative_path", "content", "loader_name"),
    [
        pytest.param(
            "audit/SOURCE_ROLES.yaml",
            "default: transversal\ndefault: transversal\n",
            "_collect_role_patterns",
            id="source-roles-top-level",
        ),
        pytest.param(
            "audit/SOURCE_ROLES.yaml",
            "roles:\n  fixture:\n    - tests/**\n  fixture:\n    - '**/fixtures/**'\n",
            "_collect_role_patterns",
            id="source-roles-nested",
        ),
        pytest.param(
            "audit/ANOMALY_DISPOSITIONS.yaml",
            "schema_version: 1\nschema_version: 1\n",
            "_load_dispositions",
            id="dispositions-top-level",
        ),
        pytest.param(
            "audit/ANOMALY_DISPOSITIONS.yaml",
            "dispositions:\n  aaaaaaaaaaaaaaaa:\n    disposition: open_debt\n    disposition: fixed\n",
            "_load_dispositions",
            id="dispositions-nested",
        ),
    ],
)
def test_versioned_control_yaml_rejects_duplicate_keys_at_every_level(
    tmp_path: Path,
    inventory_module,
    relative_path: str,
    content: str,
    loader_name: str,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    _write(tmp_path / relative_path, content)

    with pytest.raises(inventory_module.InventoryError, match="clé YAML dupliquée"):
        getattr(inventory_module, loader_name)(tmp_path)


def test_qualification_view_is_separate_from_raw_anomalies_and_covers_all_dispositions(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    anomalies = {
        "sample": [
            {"path": f"cas-{index}.tex", "reason": disposition}
            for index, disposition in enumerate(
                inventory_module.ANOMALY_DISPOSITIONS,
                start=1,
            )
        ],
        "unqualified": [{"path": "dette-sans-decision.tex", "reason": "active"}],
    }
    raw_before = deepcopy(anomalies)
    records: dict[str, dict[str, object]] = {}
    for anomaly, disposition in zip(
        anomalies["sample"],
        inventory_module.ANOMALY_DISPOSITIONS,
        strict=True,
    ):
        fingerprint = inventory_module._anomaly_fingerprint(
            anomaly,
            category="sample",
        )
        record = _qualified_disposition_record(disposition, fingerprint)
        if disposition in {
            "false_positive",
            "generated_dependency",
            "intentional_reuse",
            "fixed",
        }:
            record["proof"] = f"audit/proofs/{disposition}.md"
        elif disposition == "accepted_exception":
            record.update(
                {
                    "author": "Responsable éditorial",
                    "blocking": False,
                    "proof": "audit/proofs/accepted-exception.md",
                    "scope": {"manual": "1SPE"},
                    "expires_at": "2000-01-01",
                }
            )
        records[fingerprint] = record
    payload = {
        "artifact_type": "anomaly_dispositions",
        "control_digest": "sha256:" + "0" * 64,
        "dispositions": records,
        "fingerprint_schema_version": 1,
        "schema_ref": "audit/schemas/v1/anomaly-dispositions.schema.json",
        "schema_version": 1,
    }
    payload["control_digest"] = inventory_module._control_digest(payload)
    _write(
        tmp_path / "audit/ANOMALY_DISPOSITIONS.yaml",
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True),
    )

    dispositions = inventory_module._load_dispositions(tmp_path)
    qualifications = inventory_module._build_anomaly_qualification_view(
        anomalies,
        dispositions,
        today=datetime.date(2026, 7, 30),
    )

    assert anomalies == raw_before
    assert {
        record["disposition"] for record in qualifications.values()
    } == set(inventory_module.ANOMALY_DISPOSITIONS)
    expired = next(
        record
        for record in qualifications.values()
        if record["disposition"] == "accepted_exception"
    )
    assert expired["expired"] is True
    assert expired["blocking"] is True
    unqualified_fingerprint = inventory_module._anomaly_fingerprint(
        anomalies["unqualified"][0],
        category="unqualified",
    )
    assert qualifications[unqualified_fingerprint] == {
        "blocking": True,
        "categories": ["unqualified"],
        "category": "unqualified",
        "disposition": "open_debt",
        "fingerprint": unqualified_fingerprint,
        "occurrence_count": 1,
        "qualified": False,
        "raw_identities": [
            inventory_module._raw_anomaly_identity(
                "unqualified",
                anomalies["unqualified"][0],
            )
        ],
    }
    fixed = next(
        record
        for record in qualifications.values()
        if record["disposition"] == "fixed"
    )
    assert fixed["blocking"] is True
    assert fixed["regression"] is True


def test_live_gates_recheck_expiry_after_deterministic_artifact_date(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_cli_repository(tmp_path)
    initial = inventory_module.build_inventory(tmp_path)
    anomaly = initial["anomalies"]["unassembled_objects"][0]
    fingerprint = inventory_module._anomaly_fingerprint(
        anomaly,
        category="unassembled_objects",
    )
    record = {
        **_qualified_disposition_record("accepted_exception", fingerprint),
        "author": "Responsable éditorial",
        "blocking": False,
        "proof": "audit/proofs/accepted-exception.md",
        "scope": {"manual": "1SPE"},
        "expires_at": "2026-07-15",
    }
    payload = _dispositions_payload(record)
    payload["control_digest"] = inventory_module._control_digest(payload)
    _write(
        tmp_path / "audit/ANOMALY_DISPOSITIONS.yaml",
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True),
    )
    _track(tmp_path, "audit/ANOMALY_DISPOSITIONS.yaml")
    _commit_repository(tmp_path, "exception temporaire")
    artifact_date = datetime.datetime(2026, 7, 1, tzinfo=datetime.UTC)
    monkeypatch.setenv("SOURCE_DATE_EPOCH", str(int(artifact_date.timestamp())))

    result = inventory_module.build_inventory_artifacts(tmp_path)
    artifact = result["inventory"]
    artifact_qualification = artifact["anomaly_qualifications"][fingerprint]

    assert artifact["provenance"]["generated_at_utc"].startswith("2026-07-01")
    assert artifact_qualification["expired"] is False
    assert artifact_qualification["blocking"] is False

    live_date = datetime.date(2026, 7, 30)
    validate = inventory_module._validate_model_gate(tmp_path, today=live_date)
    release = inventory_module._release_strict_gate_for_root(
        tmp_path,
        today=live_date,
    )

    assert validate["success"] is False
    assert any(
        f"accepted_exception_expirée:{fingerprint}" in reason
        for reason in validate["reasons"]
    )
    assert any(
        "1SPE:anomalie:unassembled_objects" in reason
        for reason in release["reasons"]
    )


def test_configured_fingerprint_collision_across_four_raw_anomalies_is_rejected(
    inventory_module,
) -> None:
    anomalies = {
        "broken_latex_references": [
            {
                "champ": "input",
                "cible": "build/generated.tex",
                "line": index + 1,
                "raison": "cible absente",
                "source": "manual.tex",
            }
            for index in range(4)
        ]
    }
    fingerprint = inventory_module._anomaly_fingerprint(
        anomalies["broken_latex_references"][0],
        category="broken_latex_references",
    )
    disposition = _qualified_disposition_record(
        "generated_dependency",
        fingerprint,
    )
    disposition["proof"] = "scripts/generate.py"

    with pytest.raises(inventory_module.InventoryError, match="ambigu"):
        inventory_module._build_anomaly_qualification_view(
            anomalies,
            {fingerprint: disposition},
        )


def test_unqualified_fingerprint_collision_preserves_four_raw_identities(
    inventory_module,
) -> None:
    anomalies = {
        "broken_latex_references": [
            {
                "champ": "input",
                "cible": "build/generated.tex",
                "line": index + 1,
                "raison": "cible absente",
                "source": "manual.tex",
            }
            for index in range(4)
        ]
    }
    fingerprint = inventory_module._anomaly_fingerprint(
        anomalies["broken_latex_references"][0],
        category="broken_latex_references",
    )

    qualifications = inventory_module._build_anomaly_qualification_view(
        anomalies,
        {},
    )

    assert qualifications[fingerprint]["occurrence_count"] == 4
    assert len(qualifications[fingerprint]["raw_identities"]) == 4
    assert qualifications[fingerprint]["qualified"] is False
    assert qualifications[fingerprint]["blocking"] is True


def _baseline_contract_payload() -> dict[str, object]:
    git_sha = "a" * 40
    return {
        "active": [
            {
                "blocking": True,
                "category": "missing_corrections",
                "disposition": "open_debt",
                "fingerprint": "b" * 16,
                "justification": "Dette historique qualifiée avant publication.",
                "locator_key": "missing_corrections|1SPE|chapitre|source|champ|id",
                "occurrence_count": 2,
                "owner": "direction_scientifique_programme",
                "qualification_digest": "sha256:" + "1" * 64,
                "qualified": True,
                "severity": "blocking",
            }
        ],
        "artifact_type": "anomalies_baseline",
        "baseline_purpose": "debt_regression_control",
        "fingerprint_schema_version": 1,
        "generated_at_utc": "2026-07-22T10:00:00Z",
        "generated_by": "inventory_collection.py",
        "git_sha": git_sha,
        "model_digest": "sha256:" + "c" * 64,
        "previous_baseline_digest": None,
        "provenance": {"head_sha": git_sha},
        "provisional": True,
        "release_acceptance": False,
        "resolved": [
            {
                "blocking": False,
                "category": "metadata_missing",
                "disposition": "fixed",
                "fingerprint": "d" * 16,
                "resolved_at": "2026-07-22T09:00:00Z",
                "resolved_git_sha": git_sha,
            }
        ],
        "schema_ref": "audit/schemas/v1/anomalies-baseline.schema.json",
        "schema_version": 1,
        "source_digest": "sha256:" + "e" * 64,
        "summary": {"active": 1, "resolved": 1},
        "updates": [
            {
                "approved_by": "Responsable éditorial",
                "git_sha": git_sha,
                "new_baseline_digest": "sha256:" + "f" * 64,
                "previous_baseline_digest": None,
                "reason": "Création de la baseline provisoire après qualification.",
                "timestamp": "2026-07-22T10:00:00Z",
            }
        ],
    }


def _append_baseline_update(
    payload: dict[str, object],
    inventory_module,
    *,
    reason: str,
    timestamp: str,
) -> str:
    previous_digest = inventory_module._baseline_payload_digest(payload)
    payload["previous_baseline_digest"] = previous_digest
    payload["provisional"] = False
    updates = payload["updates"]
    assert isinstance(updates, list)
    update = {
        "approved_by": "Responsable éditorial",
        "git_sha": payload["git_sha"],
        "new_baseline_digest": "sha256:" + "0" * 64,
        "previous_baseline_digest": previous_digest,
        "reason": reason,
        "timestamp": timestamp,
    }
    updates.append(update)
    new_digest = inventory_module._baseline_payload_digest(payload)
    update["new_baseline_digest"] = new_digest
    return new_digest


def test_anomalies_baseline_schema_accepts_provisional_active_resolved_history() -> None:
    schema = json.loads(
        (ROOT / "audit/schemas/v1/anomalies-baseline.schema.json").read_text(
            encoding="utf-8"
        )
    )

    jsonschema.Draft202012Validator(schema).validate(_baseline_contract_payload())


@pytest.mark.parametrize(
    "missing_field",
    [
        "active",
        "baseline_purpose",
        "git_sha",
        "previous_baseline_digest",
        "provisional",
        "release_acceptance",
        "resolved",
        "updates",
    ],
)
def test_anomalies_baseline_schema_rejects_missing_debt_history_field(
    missing_field: str,
) -> None:
    schema = json.loads(
        (ROOT / "audit/schemas/v1/anomalies-baseline.schema.json").read_text(
            encoding="utf-8"
        )
    )
    payload = _baseline_contract_payload()
    payload.pop(missing_field)

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


def test_anomalies_baseline_schema_rejects_non_fixed_resolved_entry() -> None:
    schema = json.loads(
        (ROOT / "audit/schemas/v1/anomalies-baseline.schema.json").read_text(
            encoding="utf-8"
        )
    )
    payload = _baseline_contract_payload()
    resolved = dict(payload["resolved"][0])  # type: ignore[index]
    resolved["disposition"] = "open_debt"
    payload["resolved"] = [resolved]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


def test_anomalies_baseline_schema_rejects_release_acceptance_true() -> None:
    schema = json.loads(
        (ROOT / "audit/schemas/v1/anomalies-baseline.schema.json").read_text(
            encoding="utf-8"
        )
    )
    payload = _baseline_contract_payload()
    payload["release_acceptance"] = True

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("baseline_purpose", "release_acceptance"),
        ("release_acceptance", True),
    ],
)
def test_validated_baseline_rejects_non_regression_contract_mutation(
    tmp_path: Path,
    inventory_module,
    field: str,
    value: object,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    payload = _baseline_contract_payload()
    payload[field] = value
    _write(
        tmp_path / "audit/ANOMALIES_BASELINE.json",
        json.dumps(payload, ensure_ascii=False),
    )

    with pytest.raises(inventory_module.InventoryError, match=field):
        inventory_module._load_validated_baseline(tmp_path)


def test_validate_model_rejects_release_acceptance_before_debt_comparison(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    payload = _baseline_contract_payload()
    payload["release_acceptance"] = True
    _write(
        tmp_path / "audit/ANOMALIES_BASELINE.json",
        json.dumps(payload, ensure_ascii=False),
    )
    monkeypatch.setattr(
        inventory_module,
        "_qualification_policy_control_failures",
        lambda _root, inventory: [],
    )
    monkeypatch.setattr(
        inventory_module,
        "_load_source_roles",
        lambda _root, _tracked: {},
    )
    monkeypatch.setattr(
        inventory_module,
        "_load_dispositions",
        lambda _root: {},
    )
    monkeypatch.setattr(inventory_module, "MODEL_ARTIFACTS", {})

    result = inventory_module._validate_model_gate(tmp_path)

    assert result["success"] is False
    assert any(
        "release_acceptance" in reason for reason in result["reasons"]
    )


def test_validated_baseline_rejects_tampered_historical_update_digest(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    payload = _baseline_contract_payload()
    payload["updates"] = []
    payload["provisional"] = True
    _append_baseline_update(
        payload,
        inventory_module,
        reason="Premier gel audité",
        timestamp="2026-07-22T10:00:00Z",
    )
    _append_baseline_update(
        payload,
        inventory_module,
        reason="Second gel audité",
        timestamp="2026-07-23T10:00:00Z",
    )
    _write(
        tmp_path / "audit/ANOMALIES_BASELINE.json",
        json.dumps(payload, ensure_ascii=False),
    )

    assert inventory_module._load_validated_baseline(tmp_path)

    updates = payload["updates"]
    assert isinstance(updates, list)
    assert isinstance(updates[0], dict)
    updates[0]["new_baseline_digest"] = "sha256:" + "9" * 64
    _write(
        tmp_path / "audit/ANOMALIES_BASELINE.json",
        json.dumps(payload, ensure_ascii=False),
    )

    with pytest.raises(inventory_module.InventoryError, match="empreinte|chaîne"):
        inventory_module._load_validated_baseline(tmp_path)


def test_validated_baseline_rejects_final_state_without_audited_update(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    payload = _baseline_contract_payload()
    payload["provisional"] = False
    payload["updates"] = []
    _write(
        tmp_path / "audit/ANOMALIES_BASELINE.json",
        json.dumps(payload, ensure_ascii=False),
    )

    with pytest.raises(inventory_module.InventoryError, match="audit"):
        inventory_module._load_validated_baseline(tmp_path)


def test_baseline_gate_refuses_tracked_symlink_to_external_payload(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    outside = tmp_path.parent / f"{tmp_path.name}-external-baseline.json"
    payload = _baseline_contract_payload()
    payload["updates"] = []
    payload["provisional"] = True
    _write(outside, json.dumps(payload, ensure_ascii=False))
    baseline_path = tmp_path / "audit/ANOMALIES_BASELINE.json"
    baseline_path.symlink_to(outside)
    schema_paths = tuple(
        path.relative_to(tmp_path).as_posix()
        for path in (tmp_path / "audit/schemas").rglob("*.json")
    )
    _track(
        tmp_path,
        "audit/ANOMALIES_BASELINE.json",
        *schema_paths,
    )
    _commit_repository(tmp_path, "tracked external baseline symlink")

    assert inventory_module._require_clean_gate(tmp_path)["success"] is True

    with pytest.raises(
        inventory_module.InventoryError,
        match="symlink|regular",
    ):
        inventory_module._load_validated_baseline(tmp_path)

    gate = inventory_module._fail_on_new_gate(tmp_path)

    assert gate["success"] is False
    assert any(
        "symlink" in reason or "regular" in reason
        for reason in gate["reasons"]
    )


@pytest.mark.parametrize("missing_field", ["locator_key", "qualified"])
def test_anomalies_baseline_schema_requires_active_qualification_identity(
    missing_field: str,
) -> None:
    schema = json.loads(
        (ROOT / "audit/schemas/v1/anomalies-baseline.schema.json").read_text(
            encoding="utf-8"
        )
    )
    payload = _baseline_contract_payload()
    active = dict(payload["active"][0])  # type: ignore[index]
    active.pop(missing_field)
    payload["active"] = [active]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


def test_repository_baseline_is_frozen_schema_valid_and_gate_green(
    inventory_module,
) -> None:
    path = ROOT / "audit/ANOMALIES_BASELINE.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    inventory_module._validate_artifact_schema(
        payload,
        root=ROOT,
        path=Path("audit/ANOMALIES_BASELINE.json"),
    )
    gate = inventory_module._fail_on_new_gate(ROOT)

    assert payload["provisional"] is False
    assert payload["baseline_purpose"] == "debt_regression_control"
    assert payload["release_acceptance"] is False
    assert payload["fingerprint_schema_version"] == 1
    assert gate["success"] is True
    assert gate["exit_code"] == 0
    assert gate["reasons"] == []


def _fingerprint_case(**overrides: object) -> dict[str, object]:
    anomaly: dict[str, object] = {
        "chapter": "1SPE-SUITES",
        "field": "corrige_tex",
        "manual": "1SPE",
        "reason_code": "missing_correction",
        "source": "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/e1.tex",
        "target": "1SPE-SUITES-EX-001",
    }
    anomaly.update(overrides)
    return anomaly


def test_fingerprint_v1_is_stable_across_non_semantic_noise(
    tmp_path: Path,
    inventory_module,
) -> None:
    root_a = tmp_path / "clone-a"
    root_b = tmp_path / "clone-b"
    relative = (
        "Mathematiques/manuel-maths/chapitres/"
        "1SPE-SUITES/exercices/e1.tex"
    )
    first = _fingerprint_case(
        source=str(root_a / relative),
        line=14,
        generated_at="2026-07-29T08:00:00Z",
        tool_message="latexmk: ligne 14",
        details={"labels": ["b", "a"], "counts": {"z": 2, "a": 1}},
    )
    second = _fingerprint_case(
        source=str(root_b / relative),
        line=912,
        generated_at="2032-01-01T00:00:00Z",
        tool_message="outil différent et chemin absolu différent",
        details={"counts": {"a": 1, "z": 2}, "labels": ["a", "b"]},
    )

    assert inventory_module.FINGERPRINT_SCHEMA_VERSION == 1
    assert inventory_module._anomaly_fingerprint(
        first,
        category="missing_corrections",
        repository_root=root_a,
    ) == inventory_module._anomaly_fingerprint(
        second,
        category="missing_corrections",
        repository_root=root_b,
    )


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("category", "broken_latex_references"),
        ("manual", "1NSI"),
        ("chapter", "1SPE-SECOND-DEGRE"),
        (
            "source",
            "Mathematiques/manuel-maths/chapitres/"
            "1SPE-SUITES/exercices/e2.tex",
        ),
        ("field", "enonce_tex"),
        ("target", "1SPE-SUITES-EX-002"),
        ("reason_code", "invalid_correction"),
    ],
)
def test_fingerprint_v1_changes_for_each_contractual_identity_field(
    inventory_module,
    field: str,
    replacement: str,
) -> None:
    anomaly = _fingerprint_case()
    category = "missing_corrections"
    changed = dict(anomaly)
    if field == "category":
        changed_category = replacement
    else:
        changed[field] = replacement
        changed_category = category

    assert inventory_module._anomaly_fingerprint(
        anomaly,
        category=category,
    ) != inventory_module._anomaly_fingerprint(
        changed,
        category=changed_category,
    )


def test_fingerprint_v1_treats_target_id_as_the_same_explicit_slot(
    inventory_module,
) -> None:
    with_target = _fingerprint_case(target="1SPE-SUITES-EX-001")
    with_id = _fingerprint_case()
    with_id.pop("target")
    with_id["id"] = "1SPE-SUITES-EX-001"

    assert inventory_module._anomaly_fingerprint(
        with_target,
        category="missing_corrections",
    ) == inventory_module._anomaly_fingerprint(
        with_id,
        category="missing_corrections",
    )


def test_fingerprint_v1_sorts_non_semantic_mapping_and_list_identity_values(
    inventory_module,
) -> None:
    first = _fingerprint_case(
        target={"ids": ["EX-002", "EX-001"], "scope": {"z": 2, "a": 1}}
    )
    second = _fingerprint_case(
        target={"scope": {"a": 1, "z": 2}, "ids": ["EX-001", "EX-002"]}
    )

    assert inventory_module._anomaly_fingerprint(
        first,
        category="missing_corrections",
    ) == inventory_module._anomaly_fingerprint(
        second,
        category="missing_corrections",
    )


def test_fingerprint_v1_uses_semantic_reason_when_reason_code_is_absent(
    inventory_module,
) -> None:
    previous = {
        "path": "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/objet.tex",
        "reason": "en-tete % META absent",
        "scope": "source",
        "status": "generated",
    }
    current = {
        **previous,
        "reason": "JSON META doit etre un objet",
        "status": "draft",
    }
    category = "metadata_invalid"
    previous_fingerprint = inventory_module._anomaly_fingerprint(
        previous,
        category=category,
    )
    current_fingerprint = inventory_module._anomaly_fingerprint(
        current,
        category=category,
    )

    assert previous_fingerprint != current_fingerprint
    assert inventory_module._anomaly_locator_key(
        previous,
        category=category,
    ) == inventory_module._anomaly_locator_key(
        current,
        category=category,
    )

    disposition = _qualified_disposition_record(
        "open_debt",
        previous_fingerprint,
    )
    qualifications = inventory_module._build_anomaly_qualification_view(
        {category: [current]},
        {previous_fingerprint: disposition},
    )

    assert current_fingerprint in qualifications
    assert qualifications[current_fingerprint]["qualified"] is False
    assert previous_fingerprint not in qualifications


def test_fingerprint_v1_normalizes_volatile_noise_inside_fallback_reason(
    tmp_path: Path,
    inventory_module,
) -> None:
    root_a = tmp_path / "clone-a"
    root_b = tmp_path / "clone-b"
    first = {
        "path": "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/objet.tex",
        "reason": (
            f"JSON META invalide dans {root_a}/objet.tex: "
            "ligne 14, colonne 3, caractère 221 à 2026-07-29T08:00:00Z"
        ),
        "scope": "source",
        "status": "generated",
    }
    second = {
        **first,
        "reason": (
            f"JSON META invalide dans {root_b}/objet.tex: "
            "ligne 912, colonne 17, caractère 9921 à 2032-01-01T00:00:00Z"
        ),
    }

    assert inventory_module._anomaly_fingerprint(
        first,
        category="metadata_invalid",
        repository_root=root_a,
    ) == inventory_module._anomaly_fingerprint(
        second,
        category="metadata_invalid",
        repository_root=root_b,
    )


def test_fingerprint_v1_does_not_inherit_non_metadata_reason_change(
    inventory_module,
) -> None:
    previous = {
        "champ": "methodes[0]",
        "cible": "M1",
        "raison": "alias absent",
        "source": "chapitre.tex",
    }
    current = {**previous, "raison": "alias ambigu"}
    category = "broken_meta_references"

    assert inventory_module._anomaly_fingerprint(
        previous,
        category=category,
    ) != inventory_module._anomaly_fingerprint(
        current,
        category=category,
    )
    assert inventory_module._anomaly_locator_key(
        previous,
        category=category,
    ) == inventory_module._anomaly_locator_key(
        current,
        category=category,
    )


def _active_debt(
    fingerprint: str,
    *,
    locator_key: str = "missing_corrections|1SPE|1SPE-SUITES|e1.tex|corrige_tex|EX-001",
    occurrence_count: int = 1,
    severity: str = "blocking",
    disposition: str = "open_debt",
    owner: str = "direction_scientifique_programme",
    justification: str = "Dette qualifiée et suivie avant publication.",
    qualified: bool = True,
    qualification_digest: str = "sha256:" + "1" * 64,
) -> dict[str, object]:
    return {
        "blocking": severity in {"blocking", "regression"},
        "category": "missing_corrections",
        "disposition": disposition,
        "fingerprint": fingerprint,
        "justification": justification,
        "locator_key": locator_key,
        "occurrence_count": occurrence_count,
        "owner": owner,
        "qualification_digest": qualification_digest,
        "qualified": qualified,
        "severity": severity,
    }


def test_debt_comparison_is_multiset_aware_and_disappearance_is_improvement(
    inventory_module,
) -> None:
    unchanged = _active_debt("a" * 16, occurrence_count=2)
    disappeared = _active_debt(
        "b" * 16,
        locator_key="missing_corrections|1SPE|1SPE-SUITES|e2.tex|corrige_tex|EX-002",
    )

    comparison = inventory_module._compare_anomaly_debt(
        [unchanged],
        [unchanged, disappeared],
        [],
    )

    assert comparison["success"] is True
    assert comparison["unchanged"] == ["a" * 16]
    assert comparison["resolved"] == ["b" * 16]
    assert comparison["new"] == []
    assert comparison["modified"] == []
    assert comparison["regressions"] == []
    assert any("disparition" in value for value in comparison["improvements"])


def test_debt_comparison_detects_new_growth_and_stable_total_replacement(
    inventory_module,
) -> None:
    retained = _active_debt("a" * 16)
    grown = _active_debt(
        "b" * 16,
        locator_key="missing_corrections|1SPE|1SPE-SUITES|e2.tex|corrige_tex|EX-002",
        occurrence_count=2,
    )
    replacement = _active_debt(
        "c" * 16,
        locator_key="missing_corrections|1SPE|1SPE-SUITES|e3.tex|corrige_tex|EX-003",
    )
    baseline = [
        retained,
        _active_debt(
            "b" * 16,
            locator_key=grown["locator_key"],  # type: ignore[arg-type]
        ),
        _active_debt(
            "d" * 16,
            locator_key="missing_corrections|1SPE|1SPE-SUITES|old.tex|corrige_tex|EX-004",
        ),
    ]

    comparison = inventory_module._compare_anomaly_debt(
        [retained, grown, replacement],
        baseline,
        [],
    )

    assert comparison["success"] is False
    assert comparison["new"] == ["c" * 16]
    assert "d" * 16 in comparison["resolved"]
    assert any("croissance" in value for value in comparison["failures"])
    assert any("nouvelle" in value for value in comparison["failures"])


def test_debt_comparison_detects_modified_severity_and_lost_disposition(
    inventory_module,
) -> None:
    old_modified = _active_debt("a" * 16)
    new_modified = _active_debt(
        "b" * 16,
        locator_key=old_modified["locator_key"],  # type: ignore[arg-type]
    )
    severity_old = _active_debt(
        "c" * 16,
        locator_key="metadata_invalid|1SPE|1SPE-SUITES|m.tex|status|OBJ-1",
        severity="warning",
    )
    severity_new = dict(severity_old, severity="blocking", blocking=True)
    disposition_old = _active_debt(
        "d" * 16,
        locator_key="duplicate|1SPE|1SPE-SUITES|manifest.json|object|OBJ-2",
        disposition="intentional_reuse",
    )
    disposition_new = dict(
        disposition_old,
        disposition="open_debt",
    )

    comparison = inventory_module._compare_anomaly_debt(
        [new_modified, severity_new, disposition_new],
        [old_modified, severity_old, disposition_old],
        [],
    )

    assert comparison["success"] is False
    assert comparison["modified"] == [
        {"current": "b" * 16, "previous": "a" * 16}
    ]
    assert any("sévérité" in value for value in comparison["failures"])
    assert any("disposition" in value for value in comparison["failures"])


def test_fail_on_new_rejects_a_changed_qualification_digest(
    inventory_module,
) -> None:
    previous = _active_debt(
        "a" * 16,
        qualification_digest="sha256:" + "1" * 64,
    )
    current = _active_debt(
        "a" * 16,
        qualification_digest="sha256:" + "2" * 64,
    )

    comparison = inventory_module._compare_anomaly_debt(
        [current],
        [previous],
        [],
    )

    assert comparison["success"] is False
    assert any(
        "qualification modifiée" in reason
        for reason in comparison["failures"]
    )


def test_qualification_digest_bootstrap_diagnosis_allows_pure_digest_drift(
    inventory_module,
) -> None:
    previous = _active_debt("a" * 16, qualification_digest="sha256:" + "1" * 64)
    current = _active_debt("a" * 16, qualification_digest="sha256:" + "2" * 64)

    comparison = inventory_module._compare_anomaly_debt(
        [current],
        [previous],
        [],
    )
    pure, offending = inventory_module._qualification_digest_bootstrap_diagnosis(
        [current],
        [previous],
        comparison,
    )

    assert pure is True
    assert offending == []


def test_qualification_digest_bootstrap_diagnosis_rejects_new_fingerprint(
    inventory_module,
) -> None:
    previous = _active_debt("a" * 16, qualification_digest="sha256:" + "1" * 64)
    current = _active_debt("a" * 16, qualification_digest="sha256:" + "2" * 64)
    added = _active_debt(
        "b" * 16,
        locator_key="missing_corrections|1SPE|1SPE-SUITES|e2.tex|corrige_tex|EX-002",
    )

    comparison = inventory_module._compare_anomaly_debt(
        [current, added],
        [previous],
        [],
    )
    pure, offending = inventory_module._qualification_digest_bootstrap_diagnosis(
        [current, added],
        [previous],
        comparison,
    )

    assert pure is False
    assert any("new" in value for value in offending)


def test_qualification_digest_bootstrap_diagnosis_rejects_removed_fingerprint(
    inventory_module,
) -> None:
    previous = _active_debt("a" * 16, qualification_digest="sha256:" + "1" * 64)
    current = _active_debt("a" * 16, qualification_digest="sha256:" + "2" * 64)
    removed = _active_debt(
        "b" * 16,
        locator_key="missing_corrections|1SPE|1SPE-SUITES|e2.tex|corrige_tex|EX-002",
    )

    comparison = inventory_module._compare_anomaly_debt(
        [current],
        [previous, removed],
        [],
    )
    pure, offending = inventory_module._qualification_digest_bootstrap_diagnosis(
        [current],
        [previous, removed],
        comparison,
    )

    assert pure is False
    assert any("resolved" in value for value in offending)


def test_qualification_digest_bootstrap_diagnosis_rejects_disposition_change(
    inventory_module,
) -> None:
    previous = _active_debt(
        "a" * 16,
        qualification_digest="sha256:" + "1" * 64,
        disposition="open_debt",
    )
    current = _active_debt(
        "a" * 16,
        qualification_digest="sha256:" + "2" * 64,
        disposition="intentional_reuse",
    )

    comparison = inventory_module._compare_anomaly_debt(
        [current],
        [previous],
        [],
    )
    pure, offending = inventory_module._qualification_digest_bootstrap_diagnosis(
        [current],
        [previous],
        comparison,
    )

    assert pure is False
    assert any("modification de disposition" in value for value in offending)


def test_qualification_digest_bootstrap_diagnosis_rejects_owner_change(
    inventory_module,
) -> None:
    previous = _active_debt(
        "a" * 16,
        qualification_digest="sha256:" + "1" * 64,
        owner="direction_scientifique_programme",
    )
    current = _active_debt(
        "a" * 16,
        qualification_digest="sha256:" + "2" * 64,
        owner="ingenierie_build_qualite",
    )

    comparison = inventory_module._compare_anomaly_debt(
        [current],
        [previous],
        [],
    )
    pure, offending = inventory_module._qualification_digest_bootstrap_diagnosis(
        [current],
        [previous],
        comparison,
    )

    assert pure is False
    assert any("owner" in value for value in offending)


def _canonical_test_digest(value: object) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"sha256:{hashlib.sha256(serialized.encode('utf-8')).hexdigest()}"


def _approved_transition_case(inventory_module) -> dict[str, object]:
    retained = _active_debt(
        "a" * 16,
        locator_key="missing_corrections|1SPE|C1|retained.tex|corrige_tex|RET-1",
    )
    resolved = _active_debt(
        "b" * 16,
        locator_key="missing_corrections|1SPE|C1|resolved.tex|corrige_tex|RES-1",
    )
    previous_modified = _active_debt(
        "c" * 16,
        locator_key="missing_corrections|1SPE|C1|modified.tex|corrige_tex|MOD-1",
    )
    added = _active_debt(
        "d" * 16,
        locator_key="missing_corrections|1SPE|C1|added.tex|corrige_tex|ADD-1",
    )
    current_modified = _active_debt(
        "e" * 16,
        locator_key=str(previous_modified["locator_key"]),
    )
    baseline_payload = {
        "active": [retained, resolved, previous_modified],
        "resolved": [],
        "schema_version": 1,
    }
    current_active = [deepcopy(retained), added, current_modified]
    comparison = inventory_module._compare_anomaly_debt(
        current_active,
        baseline_payload["active"],
        baseline_payload["resolved"],
    )
    modified_pairs = [
        {"current": "e" * 16, "previous": "c" * 16},
    ]
    policy_digest = "sha256:" + "f" * 64
    policy = {
        "control_digest": policy_digest,
        "decision": {
            "approved_by": "Alaeddine Ben Rhouma",
            "baseline_purpose": "debt_regression_control",
            "release_acceptance": False,
        },
        "approved_set": {
            "category_counts": {"missing_corrections": 2},
            "fingerprint_count": 2,
            "fingerprint_digest": (
                inventory_module._baseline_qualification.fingerprint_set_digest(
                    ["d" * 16, "e" * 16]
                )
            ),
            "owner_counts": {"direction_scientifique_programme": 2},
        },
        "approved_transition": {
            "final_active_fingerprint_count": 3,
            "initial_active_fingerprint_count": 3,
            "initial_baseline_digest": inventory_module._baseline_payload_digest(
                baseline_payload
            ),
            "initial_resolved_fingerprint_count": 0,
            "modified_pairs": modified_pairs,
            "modified_pairs_digest": _canonical_test_digest(modified_pairs),
            "resolved_category_counts": {"missing_corrections": 2},
            "resolved_fingerprint_count": 2,
            "resolved_fingerprint_digest": (
                inventory_module._baseline_qualification.fingerprint_set_digest(
                    ["b" * 16, "c" * 16]
                )
            ),
            "retained_fingerprint_count": 1,
        },
    }
    dispositions = {
        fingerprint: {
            "disposition": "open_debt",
            "fingerprint": fingerprint,
            "owner": "direction_scientifique_programme",
            "qualification_policy_digest": policy_digest,
            "release_blocking": True,
        }
        for fingerprint in ("d" * 16, "e" * 16)
    }
    return {
        "baseline_payload": baseline_payload,
        "comparison": comparison,
        "current_active": current_active,
        "dispositions": dispositions,
        "policy": policy,
    }


def _diagnose_approved_transition(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    case: dict[str, object],
) -> tuple[bool, list[str]]:
    monkeypatch.setattr(
        inventory_module._baseline_qualification,
        "load_policy",
        lambda _path: case["policy"],
    )
    monkeypatch.setattr(
        inventory_module,
        "_load_dispositions",
        lambda _root: case["dispositions"],
    )
    return inventory_module._approved_baseline_extension_diagnosis(
        tmp_path,
        case["current_active"],
        case["baseline_payload"],
        case["comparison"],
        approved_by="Alaeddine Ben Rhouma",
    )


def _refresh_transition_comparison(case: dict[str, object], inventory_module) -> None:
    baseline_payload = case["baseline_payload"]
    case["comparison"] = inventory_module._compare_anomaly_debt(
        case["current_active"],
        baseline_payload["active"],
        baseline_payload["resolved"],
    )


def _refresh_transition_baseline_digest(
    case: dict[str, object], inventory_module
) -> None:
    case["policy"]["approved_transition"]["initial_baseline_digest"] = (
        inventory_module._baseline_payload_digest(case["baseline_payload"])
    )


def test_approved_baseline_extension_diagnosis_preserves_pure_extension_mode(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    previous = _active_debt("a" * 16)
    added = _active_debt(
        "b" * 16,
        locator_key="blocking_statuses|1SPE|1SPE-SUITES|cours.tex|status|OBJ-1",
    )
    added["category"] = "blocking_statuses"
    current = [previous, added]
    comparison = inventory_module._compare_anomaly_debt(
        current,
        [previous],
        [],
    )
    policy_digest = "sha256:" + "f" * 64
    policy = {
        "control_digest": policy_digest,
        "decision": {
            "approved_by": "Alaeddine Ben Rhouma",
            "baseline_purpose": "debt_regression_control",
            "release_acceptance": False,
        },
        "approved_set": {
            "category_counts": {"blocking_statuses": 1},
            "fingerprint_count": 1,
            "fingerprint_digest": (
                inventory_module._baseline_qualification.fingerprint_set_digest(
                    [str(added["fingerprint"])]
                )
            ),
            "owner_counts": {"direction_scientifique_programme": 1},
        },
    }
    monkeypatch.setattr(
        inventory_module._baseline_qualification,
        "load_policy",
        lambda _path: policy,
    )
    monkeypatch.setattr(
        inventory_module,
        "_load_dispositions",
        lambda _root: {
            str(added["fingerprint"]): {
                "disposition": "open_debt",
                "fingerprint": added["fingerprint"],
                "owner": added["owner"],
                "qualification_policy_digest": policy_digest,
                "release_blocking": True,
            }
        },
    )

    approved, offending = (
        inventory_module._approved_baseline_extension_diagnosis(
            tmp_path,
            current,
            {"active": [previous], "resolved": [], "schema_version": 1},
            comparison,
            approved_by="Alaeddine Ben Rhouma",
        )
    )

    assert approved is True
    assert offending == []


def test_approved_baseline_extension_diagnosis_rejects_forged_pure_extension(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    previous = _active_debt("a" * 16)
    altered = deepcopy(previous)
    altered["occurrence_count"] = 2
    altered["owner"] = "ingenierie_build_qualite"
    added = _active_debt(
        "b" * 16,
        locator_key="blocking_statuses|1SPE|1SPE-SUITES|cours.tex|status|OBJ-1",
    )
    added["category"] = "blocking_statuses"
    current = [altered, added]
    forged_comparison = inventory_module._compare_anomaly_debt(
        [previous, added],
        [previous],
        [],
    )
    policy_digest = "sha256:" + "f" * 64
    policy = {
        "control_digest": policy_digest,
        "decision": {
            "approved_by": "Alaeddine Ben Rhouma",
            "baseline_purpose": "debt_regression_control",
            "release_acceptance": False,
        },
        "approved_set": {
            "category_counts": {"blocking_statuses": 1},
            "fingerprint_count": 1,
            "fingerprint_digest": (
                inventory_module._baseline_qualification.fingerprint_set_digest(
                    [str(added["fingerprint"])]
                )
            ),
            "owner_counts": {"direction_scientifique_programme": 1},
        },
    }
    monkeypatch.setattr(
        inventory_module._baseline_qualification,
        "load_policy",
        lambda _path: policy,
    )
    monkeypatch.setattr(
        inventory_module,
        "_load_dispositions",
        lambda _root: {
            str(added["fingerprint"]): {
                "disposition": "open_debt",
                "fingerprint": added["fingerprint"],
                "owner": added["owner"],
                "qualification_policy_digest": policy_digest,
                "release_blocking": True,
            }
        },
    )

    approved, offending = (
        inventory_module._approved_baseline_extension_diagnosis(
            tmp_path,
            current,
            {"active": [previous], "resolved": [], "schema_version": 1},
            forged_comparison,
            approved_by="Alaeddine Ben Rhouma",
        )
    )

    assert approved is False
    assert any(
        "comparaison" in value or "conservé" in value
        for value in offending
    )


def test_approved_baseline_extension_diagnosis_rejects_non_open_debt(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    previous = _active_debt("a" * 16)
    added = _active_debt(
        "b" * 16,
        locator_key="blocking_statuses|1SPE|1SPE-SUITES|cours.tex|status|OBJ-1",
        disposition="intentional_reuse",
    )
    added["category"] = "blocking_statuses"
    current = [previous, added]
    comparison = inventory_module._compare_anomaly_debt(
        current,
        [previous],
        [],
    )
    policy_digest = "sha256:" + "f" * 64
    policy = {
        "control_digest": policy_digest,
        "decision": {
            "approved_by": "Alaeddine Ben Rhouma",
            "baseline_purpose": "debt_regression_control",
            "release_acceptance": False,
        },
        "approved_set": {
            "category_counts": {"blocking_statuses": 1},
            "fingerprint_count": 1,
            "fingerprint_digest": (
                inventory_module._baseline_qualification.fingerprint_set_digest(
                    [str(added["fingerprint"])]
                )
            ),
            "owner_counts": {"direction_scientifique_programme": 1},
        },
    }
    monkeypatch.setattr(
        inventory_module._baseline_qualification,
        "load_policy",
        lambda _path: policy,
    )
    monkeypatch.setattr(
        inventory_module,
        "_load_dispositions",
        lambda _root: {
            str(added["fingerprint"]): {
                "disposition": "intentional_reuse",
                "fingerprint": added["fingerprint"],
                "owner": added["owner"],
                "qualification_policy_digest": policy_digest,
                "release_blocking": False,
            }
        },
    )

    approved, offending = (
        inventory_module._approved_baseline_extension_diagnosis(
            tmp_path,
            current,
            {"active": [previous], "resolved": [], "schema_version": 1},
            comparison,
            approved_by="Alaeddine Ben Rhouma",
        )
    )

    assert approved is False
    assert any("open_debt" in value for value in offending)


def test_approved_baseline_extension_diagnosis_accepts_exact_reconciliation(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _approved_transition_case(inventory_module)

    approved, offending = _diagnose_approved_transition(
        tmp_path, inventory_module, monkeypatch, case
    )

    assert approved is True
    assert offending == []


def test_approved_baseline_extension_diagnosis_rejects_addition_outside_lot(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _approved_transition_case(inventory_module)
    case["current_active"].append(
        _active_debt(
            "f" * 16,
            locator_key="missing_corrections|1SPE|C1|extra.tex|corrige_tex|EXTRA-1",
        )
    )
    _refresh_transition_comparison(case, inventory_module)

    approved, offending = _diagnose_approved_transition(
        tmp_path, inventory_module, monkeypatch, case
    )

    assert approved is False
    assert offending


def test_approved_baseline_extension_diagnosis_rejects_resolution_outside_lot(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _approved_transition_case(inventory_module)
    case["current_active"] = [
        entry
        for entry in case["current_active"]
        if entry["fingerprint"] != "a" * 16
    ]
    _refresh_transition_comparison(case, inventory_module)

    approved, offending = _diagnose_approved_transition(
        tmp_path, inventory_module, monkeypatch, case
    )

    assert approved is False
    assert offending


def test_approved_baseline_extension_diagnosis_rejects_different_pair(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _approved_transition_case(inventory_module)
    replacement = next(
        entry
        for entry in case["current_active"]
        if entry["fingerprint"] == "e" * 16
    )
    replacement["locator_key"] = (
        "missing_corrections|1SPE|C1|other.tex|corrige_tex|OTHER-1"
    )
    _refresh_transition_comparison(case, inventory_module)

    approved, offending = _diagnose_approved_transition(
        tmp_path, inventory_module, monkeypatch, case
    )

    assert approved is False
    assert any("paire" in value for value in offending)


def test_approved_baseline_extension_diagnosis_rejects_resolved_reappearance(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _approved_transition_case(inventory_module)
    reappeared = _active_debt(
        "9" * 16,
        locator_key="missing_corrections|1SPE|C1|history.tex|corrige_tex|HIST-1",
    )
    case["baseline_payload"]["resolved"] = [
        {"fingerprint": "9" * 16, "resolved_at": "2026-08-01T00:00:00Z"}
    ]
    case["current_active"].append(reappeared)
    _refresh_transition_baseline_digest(case, inventory_module)
    _refresh_transition_comparison(case, inventory_module)

    approved, offending = _diagnose_approved_transition(
        tmp_path, inventory_module, monkeypatch, case
    )

    assert approved is False
    assert any("réappar" in value for value in offending)


def test_approved_baseline_extension_diagnosis_rejects_retained_record_change(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _approved_transition_case(inventory_module)
    retained = next(
        entry
        for entry in case["current_active"]
        if entry["fingerprint"] == "a" * 16
    )
    retained["justification"] = "Justification altérée."
    _refresh_transition_comparison(case, inventory_module)

    approved, offending = _diagnose_approved_transition(
        tmp_path, inventory_module, monkeypatch, case
    )

    assert approved is False
    assert any("conserv" in value for value in offending)


def test_approved_baseline_extension_diagnosis_rejects_occurrence_decrease(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _approved_transition_case(inventory_module)
    case["baseline_payload"]["active"][0]["occurrence_count"] = 2
    _refresh_transition_baseline_digest(case, inventory_module)
    _refresh_transition_comparison(case, inventory_module)

    approved, offending = _diagnose_approved_transition(
        tmp_path, inventory_module, monkeypatch, case
    )

    assert approved is False
    assert any("conserv" in value for value in offending)


def test_approved_baseline_extension_diagnosis_rejects_severity_decrease(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _approved_transition_case(inventory_module)
    retained = next(
        entry
        for entry in case["current_active"]
        if entry["fingerprint"] == "a" * 16
    )
    retained["severity"] = "warning"
    _refresh_transition_comparison(case, inventory_module)

    approved, offending = _diagnose_approved_transition(
        tmp_path, inventory_module, monkeypatch, case
    )

    assert approved is False
    assert any("conserv" in value for value in offending)


def test_approved_baseline_extension_diagnosis_rejects_blocking_decrease(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _approved_transition_case(inventory_module)
    retained = next(
        entry
        for entry in case["current_active"]
        if entry["fingerprint"] == "a" * 16
    )
    retained["blocking"] = False
    _refresh_transition_comparison(case, inventory_module)

    approved, offending = _diagnose_approved_transition(
        tmp_path, inventory_module, monkeypatch, case
    )

    assert approved is False
    assert any("conserv" in value for value in offending)


def test_approved_baseline_extension_diagnosis_rejects_initial_digest_drift(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _approved_transition_case(inventory_module)
    case["policy"]["approved_transition"]["initial_baseline_digest"] = (
        "sha256:" + "0" * 64
    )

    approved, offending = _diagnose_approved_transition(
        tmp_path, inventory_module, monkeypatch, case
    )

    assert approved is False
    assert any("baseline initiale" in value for value in offending)


def test_approved_baseline_extension_diagnosis_rejects_nonempty_initial_resolved(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _approved_transition_case(inventory_module)
    case["baseline_payload"]["resolved"] = [
        {"fingerprint": "9" * 16, "resolved_at": "2026-08-01T00:00:00Z"}
    ]
    _refresh_transition_baseline_digest(case, inventory_module)
    _refresh_transition_comparison(case, inventory_module)

    approved, offending = _diagnose_approved_transition(
        tmp_path, inventory_module, monkeypatch, case
    )

    assert approved is False
    assert any("resolved initial" in value for value in offending)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("disposition", "intentional_reuse"),
        ("blocking", False),
        ("owner", "ingenierie_build_qualite"),
    ],
)
def test_approved_baseline_extension_diagnosis_rejects_invalid_added_record(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: object,
) -> None:
    case = _approved_transition_case(inventory_module)
    added = next(
        entry
        for entry in case["current_active"]
        if entry["fingerprint"] == "d" * 16
    )
    added[field] = value
    _refresh_transition_comparison(case, inventory_module)

    approved, offending = _diagnose_approved_transition(
        tmp_path, inventory_module, monkeypatch, case
    )

    assert approved is False
    assert offending


def test_approved_baseline_extension_diagnosis_rejects_policy_digest_mismatch(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _approved_transition_case(inventory_module)
    case["dispositions"]["d" * 16]["qualification_policy_digest"] = (
        "sha256:" + "0" * 64
    )

    approved, offending = _diagnose_approved_transition(
        tmp_path, inventory_module, monkeypatch, case
    )

    assert approved is False
    assert any("disposition ajoutée" in value for value in offending)


def test_qualification_digest_bootstrap_diagnosis_rejects_severity_change(
    inventory_module,
) -> None:
    previous = _active_debt(
        "a" * 16,
        qualification_digest="sha256:" + "1" * 64,
        severity="warning",
    )
    current = dict(
        _active_debt(
            "a" * 16,
            qualification_digest="sha256:" + "2" * 64,
        ),
        severity="blocking",
    )

    comparison = inventory_module._compare_anomaly_debt(
        [current],
        [previous],
        [],
    )
    pure, offending = inventory_module._qualification_digest_bootstrap_diagnosis(
        [current],
        [previous],
        comparison,
    )

    assert pure is False
    assert any("aggravation" in value for value in offending) or any(
        "severity" in value for value in offending
    )


def test_qualification_digest_bootstrap_diagnosis_rejects_when_no_drift_at_all(
    inventory_module,
) -> None:
    unchanged = _active_debt("a" * 16, qualification_digest="sha256:" + "1" * 64)

    comparison = inventory_module._compare_anomaly_debt(
        [unchanged],
        [unchanged],
        [],
    )
    pure, offending = inventory_module._qualification_digest_bootstrap_diagnosis(
        [unchanged],
        [unchanged],
        comparison,
    )

    assert comparison["success"] is True
    assert pure is False
    assert offending == []


def test_disposition_coverage_policy_gate_requires_zero_unqualified_reports(
    tmp_path: Path,
    inventory_module,
) -> None:
    policy = {"control_digest": "sha256:" + "a" * 64}

    missing = inventory_module._qualification_unqualified_report_failures(
        tmp_path,
        policy,
    )

    assert any("UNQUALIFIED_ANOMALIES.json absent" in reason for reason in missing)
    assert any("UNQUALIFIED_ANOMALIES.md absent" in reason for reason in missing)

    payload = {
        "anomalies": [
            {
                "category": "blocking_statuses",
                "chapter": "1SPE-SUITES",
                "fingerprint": "b" * 16,
                "manual": "1SPE",
                "reason": "no_policy_rule",
                "source": "chapitres/1SPE-SUITES/cours/cours.tex",
            }
        ],
        "artifact_type": "unqualified_anomalies",
        "fingerprint_schema_version": 1,
        "generated_by": "baseline_qualification.py",
        "policy_digest": policy["control_digest"],
        "schema_ref": "audit/schemas/v1/unqualified-anomalies.schema.json",
        "schema_version": 1,
        "summary": {"unqualified": 1},
    }
    _write(
        tmp_path / "audit/UNQUALIFIED_ANOMALIES.json",
        json.dumps(payload, ensure_ascii=False),
    )
    _write(
        tmp_path / "audit/UNQUALIFIED_ANOMALIES.md",
        inventory_module._baseline_qualification.render_unqualified_markdown(
            payload["anomalies"],
            policy_digest=str(policy["control_digest"]),
        ),
    )

    nonempty = inventory_module._qualification_unqualified_report_failures(
        tmp_path,
        policy,
    )

    assert any("anomalies_non_qualifiées:1" in reason for reason in nonempty)


def test_validate_model_includes_policy_gate_failures(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        inventory_module,
        "_qualification_policy_control_failures",
        lambda _root, *, inventory=None: ["policy_gate:altération injectée"],
    )

    result = inventory_module._validate_model_gate(tmp_path)

    assert result["success"] is False
    assert "policy_gate:altération injectée" in result["reasons"]


def test_policy_gate_rejects_missing_policy_after_contract_activation(
    tmp_path: Path,
    inventory_module,
) -> None:
    _write(
        tmp_path / "audit/UNQUALIFIED_ANOMALIES.json",
        "{}\n",
    )

    failures = inventory_module._qualification_policy_control_failures(
        tmp_path,
    )

    assert any("politique absente" in reason for reason in failures)


def test_disposition_coverage_rejects_arbitrary_historical_active_owner(
    inventory_module,
) -> None:
    active = _active_debt(
        "a" * 16,
        owner="équipe historique arbitraire",
    )

    failures = inventory_module._active_debt_qualification_failures(
        {"a" * 16: active}
    )

    assert any("owner logique inconnu" in reason for reason in failures)


def test_debt_comparison_treats_error_false_to_blocking_true_as_escalation(
    inventory_module,
) -> None:
    previous = _active_debt(
        "a" * 16,
        severity="error",
    )
    previous["blocking"] = False
    current = dict(
        previous,
        severity="blocking",
        blocking=True,
    )

    comparison = inventory_module._compare_anomaly_debt(
        [current],
        [previous],
        [],
    )

    assert inventory_module._ANOMALY_SEVERITY_RANK["blocking"] > (
        inventory_module._ANOMALY_SEVERITY_RANK["error"]
    )
    assert comparison["success"] is False
    assert any("sévérité" in reason for reason in comparison["failures"])
    assert any(
        "caractère bloquant" in reason
        and "False→True" in reason
        for reason in comparison["failures"]
    )


def test_debt_comparison_detects_resolved_recurrence_and_preserves_history(
    inventory_module,
) -> None:
    recurring = _active_debt("a" * 16)
    resolved = [
        {
            "blocking": False,
            "category": "missing_corrections",
            "disposition": "fixed",
            "fingerprint": "a" * 16,
            "resolved_at": "2026-07-22T09:00:00Z",
            "resolved_git_sha": "b" * 40,
        },
        {
            "blocking": False,
            "category": "metadata_missing",
            "disposition": "fixed",
            "fingerprint": "c" * 16,
            "resolved_at": "2026-07-21T09:00:00Z",
            "resolved_git_sha": "d" * 40,
        },
    ]

    comparison = inventory_module._compare_anomaly_debt(
        [recurring],
        [recurring],
        resolved,
    )

    assert comparison["success"] is False
    assert comparison["regressions"] == ["a" * 16]
    assert comparison["resolved_history"] == resolved
    assert any("réapparition" in value for value in comparison["failures"])


def test_fixed_disposition_reappearance_flows_to_active_regression_and_gate(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    category = "missing_corrections"
    anomaly = _fingerprint_case()
    fingerprint = inventory_module._anomaly_fingerprint(
        anomaly,
        category=category,
    )
    fixed = _qualified_disposition_record("fixed", fingerprint)
    fixed["proof"] = "audit/proofs/correction.md"
    fixed["qualification_digest"] = (
        inventory_module._baseline_qualification.qualification_digest(fixed)
    )
    anomalies = {category: [anomaly]}
    qualifications = inventory_module._build_anomaly_qualification_view(
        anomalies,
        {fingerprint: fixed},
    )
    inventory = {
        "anomalies": anomalies,
        "anomaly_qualifications": qualifications,
    }

    active = inventory_module._current_active_debt(inventory)

    assert qualifications[fingerprint]["regression"] is True
    assert qualifications[fingerprint]["blocking"] is True
    assert active == [
        {
            "blocking": True,
            "category": category,
            "disposition": "fixed",
            "fingerprint": fingerprint,
            "justification": fixed["justification"],
            "locator_key": inventory_module._anomaly_locator_key(
                anomaly,
                category=category,
            ),
                "occurrence_count": 1,
                "owner": fixed["owner"],
                "qualification_digest": (
                    inventory_module._baseline_qualification
                    .qualification_digest(fixed)
                ),
                "qualified": True,
            "severity": "regression",
        }
    ]

    resolved = {
        "blocking": False,
        "category": category,
        "disposition": "fixed",
        "fingerprint": fingerprint,
        "resolved_at": "2026-07-22T09:00:00Z",
        "resolved_git_sha": "a" * 40,
    }
    comparison = inventory_module._compare_anomaly_debt(
        active,
        [],
        [resolved],
    )
    assert comparison["success"] is False
    assert comparison["regressions"] == [fingerprint]

    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    baseline = _baseline_contract_payload()
    baseline["active"] = []
    baseline["provisional"] = True
    baseline["resolved"] = [resolved]
    baseline["updates"] = []
    _append_baseline_update(
        baseline,
        inventory_module,
        reason="Correction auditée avant test de réapparition",
        timestamp="2026-07-23T10:00:00Z",
    )
    _write(
        tmp_path / "audit/ANOMALIES_BASELINE.json",
        json.dumps(baseline, ensure_ascii=False),
    )
    monkeypatch.setattr(
        inventory_module,
        "build_inventory",
        lambda _root: inventory,
    )

    gate = inventory_module._fail_on_new_gate(tmp_path)

    assert gate["success"] is False
    assert gate["exit_code"] == 5
    assert any("réapparition" in reason for reason in gate["reasons"])


@pytest.mark.parametrize(
    ("missing", "replacement"),
    [
        ("owner", ""),
        ("justification", ""),
        ("qualified", False),
    ],
)
def test_debt_comparison_rejects_active_anomaly_without_qualification(
    inventory_module,
    missing: str,
    replacement: object,
) -> None:
    active = _active_debt("a" * 16)
    active[missing] = replacement

    comparison = inventory_module._compare_anomaly_debt([active], [], [])

    assert comparison["success"] is False
    assert any("qualification" in value for value in comparison["failures"])


def _ready_check(name: str, success: bool = True) -> dict[str, object]:
    return {
        "name": name,
        "reasons": [] if success else [f"{name}: échec injecté"],
        "success": success,
    }


def test_baseline_ready_reports_all_ten_stabilization_checks(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected_names = [
        "phase0_tests",
        "artifact_schemas",
        "renderers",
        "object_counts",
        "harvest_candidates",
        "generated_renvois",
        "intentional_reuse_decisions",
        "disposition_coverage",
        "fingerprint_determinism",
        "validate_model",
    ]
    monkeypatch.setattr(
        inventory_module,
        "_run_baseline_readiness_check",
        lambda _root, name: _ready_check(
            name,
            success=name != "object_counts",
        ),
    )

    result = inventory_module._baseline_ready_gate(tmp_path)

    assert [check["name"] for check in result["checks"]] == expected_names
    assert result["success"] is False
    assert result["exit_code"] == 8
    assert result["reasons"] == ["object_counts: échec injecté"]


@pytest.mark.parametrize(
    ("arguments", "expected_reason"),
    [
        (
            ("--update-baseline", "--reason", "", "--approved-by", "Responsable"),
            "justification",
        ),
        (
            (
                "--update-baseline",
                "--reason",
                "Gel contrôlé",
                "--approved-by",
                "",
            ),
            "approbateur",
        ),
    ],
)
def test_update_baseline_cli_rejects_empty_audit_fields(
    tmp_path: Path,
    arguments: tuple[str, ...],
    expected_reason: str,
) -> None:
    _seed_cli_repository(tmp_path)

    completed = _run_inventory_cli(tmp_path, *arguments)
    result = json.loads(completed.stdout)

    assert completed.returncode == 8
    assert result["gate"] == "update-baseline"
    assert any(expected_reason in reason for reason in result["reasons"])
    assert not (tmp_path / "audit/BASELINE_UPDATE_REPORT.md").exists()


def test_update_baseline_cli_rejects_ci_dirty_repo_and_invalid_model(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ci_repository = tmp_path / "ci"
    _seed_cli_repository(ci_repository)
    ci_environment = dict(os.environ, CI="true")
    ci = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--root",
            str(ci_repository),
            "--update-baseline",
            "--reason",
            "Gel contrôlé",
            "--approved-by",
            "Responsable",
        ],
        capture_output=True,
        text=True,
        check=False,
        env=ci_environment,
    )

    dirty_repository = tmp_path / "dirty"
    tracked = _seed_cli_repository(dirty_repository)
    _commit_repository(dirty_repository)
    _write(dirty_repository / tracked[0], "modification locale\n")
    dirty = _run_inventory_cli(
        dirty_repository,
        "--update-baseline",
        "--reason",
        "Gel contrôlé",
        "--approved-by",
        "Responsable",
    )

    invalid_repository = tmp_path / "invalid"
    _seed_cli_repository(invalid_repository)
    _commit_repository(invalid_repository)
    invalid = _run_inventory_cli(
        invalid_repository,
        "--update-baseline",
        "--reason",
        "Gel contrôlé",
        "--approved-by",
        "Responsable",
    )

    assert ci.returncode == 8
    assert any("CI" in reason for reason in json.loads(ci.stdout)["reasons"])
    assert dirty.returncode == 8
    assert any("propre" in reason for reason in json.loads(dirty.stdout)["reasons"])
    assert invalid.returncode == 8
    assert any(
        "modèle" in reason for reason in json.loads(invalid.stdout)["reasons"]
    )


def test_update_baseline_writes_audited_transition_and_preserves_resolved_history(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CI", raising=False)
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    _write(tmp_path / "tracked.txt", "source\n")
    schema_paths = tuple(
        path.relative_to(tmp_path).as_posix()
        for path in (tmp_path / "audit/schemas").rglob("*.json")
    )
    _track(tmp_path, "tracked.txt", *schema_paths)
    head_sha = _commit_repository(tmp_path)
    old_baseline = _baseline_contract_payload()
    old_baseline["git_sha"] = head_sha
    old_baseline["active"] = [
        _active_debt(
            "a" * 16,
            locator_key="missing|1SPE|old",
        )
    ]
    old_baseline["resolved"] = [
        {
            "blocking": False,
            "category": "metadata_missing",
            "disposition": "fixed",
            "fingerprint": "d" * 16,
            "resolved_at": "2026-07-22T09:00:00Z",
            "resolved_git_sha": head_sha,
        }
    ]
    old_baseline["updates"] = []
    _write(
        tmp_path / "audit/ANOMALIES_BASELINE.json",
        json.dumps(old_baseline, ensure_ascii=False),
    )
    _track(tmp_path, "audit/ANOMALIES_BASELINE.json")
    head_sha = _commit_repository(tmp_path, "baseline")

    current = _active_debt(
        "b" * 16,
        locator_key="missing|1SPE|new",
    )
    inventory = {
        "anomalies": {},
        "anomaly_qualifications": {},
        "provenance": {
            "generated_at_utc": inventory_module._generation_timestamp(
                tmp_path,
                required=True,
            ),
            "head_sha": head_sha,
        },
        "source_digest": "sha256:" + "e" * 64,
    }
    monkeypatch.setattr(
        inventory_module,
        "_model_digest",
        lambda _inventory: "sha256:" + "c" * 64,
    )
    monkeypatch.setattr(
        inventory_module,
        "_validate_model_gate",
        lambda _root: inventory_module._gate_result(
            "validate-model",
            success=True,
            failure_code=6,
            dimensions={"structure": "passed"},
            reasons=[],
        ),
    )
    monkeypatch.setattr(
        inventory_module,
        "_baseline_ready_gate",
        lambda _root: {
            **inventory_module._gate_result(
                "baseline-ready",
                success=True,
                failure_code=8,
                dimensions={"structure": "passed"},
                reasons=[],
            ),
            "checks": [
                _ready_check(name)
                for name in inventory_module.BASELINE_READY_CHECK_NAMES
            ],
        },
    )
    received_lock_identities: list[dict[str, tuple[int, int]]] = []

    def build_inventory_under_owned_lock(
        _root: Path,
        *,
        require_git_provenance: bool = False,
        owned_generation_lock: dict[str, tuple[int, int]] | None = None,
    ) -> dict[str, object]:
        assert require_git_provenance is True
        assert owned_generation_lock is not None
        received_lock_identities.append(dict(owned_generation_lock))
        return inventory

    monkeypatch.setattr(
        inventory_module,
        "_build_inventory",
        build_inventory_under_owned_lock,
    )
    monkeypatch.setattr(
        inventory_module,
        "_current_active_debt",
        lambda _inventory: [current],
    )
    monkeypatch.setattr(
        inventory_module,
        "_load_dispositions",
        lambda _root: {
            str(current["fingerprint"]): {
                "qualification_policy_digest": "sha256:" + "f" * 64,
            }
        },
    )

    result = inventory_module._update_baseline_gate(
        tmp_path,
        reason="Gel contrôlé après stabilisation",
        approved_by="Responsable éditorial",
    )

    payload = json.loads(
        (tmp_path / "audit/ANOMALIES_BASELINE.json").read_text(encoding="utf-8")
    )
    report = (tmp_path / "audit/BASELINE_UPDATE_REPORT.md").read_text(
        encoding="utf-8"
    )
    freeze_report = (
        tmp_path / "audit/BASELINE_FREEZE_REPORT.md"
    ).read_text(encoding="utf-8")
    assert result["success"] is True
    assert len(received_lock_identities) == 1
    assert inventory_module.GENERIC_LOCK_FILE in received_lock_identities[0]
    assert payload["provisional"] is False
    assert payload["baseline_purpose"] == "debt_regression_control"
    assert payload["release_acceptance"] is False
    assert payload["git_sha"] == head_sha
    assert payload["active"] == [current]
    assert {entry["fingerprint"] for entry in payload["resolved"]} == {
        "a" * 16,
        "d" * 16,
    }
    assert payload["previous_baseline_digest"].startswith("sha256:")
    update = payload["updates"][-1]
    assert update["approved_by"] == "Responsable éditorial"
    assert update["reason"] == "Gel contrôlé après stabilisation"
    assert update["previous_baseline_digest"].startswith("sha256:")
    assert update["new_baseline_digest"].startswith("sha256:")
    assert update["git_sha"] == head_sha
    assert "Empreinte précédente" in report
    assert "Nouvelle empreinte" in report
    assert head_sha in report
    assert "aaaaaaaaaaaaaaaa" in report
    assert "bbbbbbbbbbbbbbbb" in report
    assert "# Rapport de gel de la baseline de non-régression" in freeze_report
    assert "baseline_purpose: `debt_regression_control`" in freeze_report
    assert "release_acceptance: `false`" in freeze_report
    assert "Fingerprints actifs : `1`" in freeze_report
    assert "Anomalies non qualifiées : `0`" in freeze_report
    assert "Responsable éditorial" in freeze_report
    assert "Gel contrôlé après stabilisation" in freeze_report
    assert head_sha in freeze_report
    assert payload["previous_baseline_digest"] in freeze_report
    assert update["new_baseline_digest"] in freeze_report


def _prepare_bootstrap_repository(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    *,
    old_active: list[dict[str, object]],
    current_active: list[dict[str, object]],
) -> str:
    monkeypatch.delenv("CI", raising=False)
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    _write(tmp_path / "tracked.txt", "source\n")
    schema_paths = tuple(
        path.relative_to(tmp_path).as_posix()
        for path in (tmp_path / "audit/schemas").rglob("*.json")
    )
    _track(tmp_path, "tracked.txt", *schema_paths)
    head_sha = _commit_repository(tmp_path)
    old_baseline = _baseline_contract_payload()
    old_baseline["git_sha"] = head_sha
    old_baseline["active"] = old_active
    old_baseline["resolved"] = []
    old_baseline["provisional"] = False
    old_baseline["previous_baseline_digest"] = None
    placeholder_update = {
        "approved_by": "Alaeddine Ben Rhouma",
        "git_sha": head_sha,
        "new_baseline_digest": "sha256:" + "0" * 64,
        "previous_baseline_digest": None,
        "reason": "Gel initial",
        "timestamp": "2026-07-30T08:00:00Z",
    }
    old_baseline["updates"] = [placeholder_update]
    placeholder_update["new_baseline_digest"] = (
        inventory_module._baseline_payload_digest(old_baseline)
    )
    _write(
        tmp_path / "audit/ANOMALIES_BASELINE.json",
        json.dumps(old_baseline, ensure_ascii=False),
    )
    _track(tmp_path, "audit/ANOMALIES_BASELINE.json")
    head_sha = _commit_repository(tmp_path, "baseline")

    inventory = {
        "anomalies": {},
        "anomaly_qualifications": {},
        "provenance": {
            "generated_at_utc": inventory_module._generation_timestamp(
                tmp_path,
                required=True,
            ),
            "head_sha": head_sha,
        },
        "source_digest": "sha256:" + "e" * 64,
    }
    monkeypatch.setattr(
        inventory_module,
        "_model_digest",
        lambda _inventory: "sha256:" + "c" * 64,
    )
    monkeypatch.setattr(
        inventory_module,
        "_validate_model_gate",
        lambda _root: inventory_module._gate_result(
            "validate-model",
            success=True,
            failure_code=6,
            dimensions={"structure": "passed"},
            reasons=[],
        ),
    )
    monkeypatch.setattr(
        inventory_module,
        "_run_baseline_readiness_check",
        lambda _root, name: _ready_check(
            name, success=(name != "phase0_tests")
        ),
    )
    monkeypatch.setattr(
        inventory_module,
        "build_inventory",
        lambda _root, **_kwargs: inventory,
    )
    monkeypatch.setattr(
        inventory_module,
        "_current_active_debt",
        lambda _inventory: current_active,
    )
    monkeypatch.setattr(
        inventory_module,
        "_load_dispositions",
        lambda _root: {
            str(entry["fingerprint"]): {
                "qualification_policy_digest": "sha256:" + "f" * 64,
            }
            for entry in current_active
        },
    )
    return head_sha


def test_update_baseline_bootstrap_allows_pure_qualification_digest_realignment(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old_entry = _active_debt("a" * 16, qualification_digest="sha256:" + "1" * 64)
    current = _active_debt("a" * 16, qualification_digest="sha256:" + "2" * 64)
    _prepare_bootstrap_repository(
        tmp_path,
        inventory_module,
        monkeypatch,
        old_active=[old_entry],
        current_active=[current],
    )

    result = inventory_module._update_baseline_gate(
        tmp_path,
        reason="Réalignement mécanique de qualification_digest",
        approved_by="Responsable éditorial",
        allow_qualification_digest_bootstrap=True,
    )

    assert result["success"] is True
    phase0 = next(
        check for check in result["checks"] if check["name"] == "phase0_tests"
    )
    assert phase0["success"] is True
    assert "bootstrap_bypass" in phase0
    payload = json.loads(
        (tmp_path / "audit/ANOMALIES_BASELINE.json").read_text(encoding="utf-8")
    )
    assert payload["active"] == [current]


def test_update_baseline_allows_verified_approved_extension(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old_entry = _active_debt("a" * 16)
    added = _active_debt(
        "b" * 16,
        locator_key="blocking_statuses|1SPE|1SPE-SUITES|cours.tex|status|OBJ-1",
    )
    current = [old_entry, added]
    _prepare_bootstrap_repository(
        tmp_path,
        inventory_module,
        monkeypatch,
        old_active=[old_entry],
        current_active=current,
    )
    monkeypatch.setattr(
        inventory_module,
        "_approved_baseline_extension_diagnosis",
        lambda *_args, **_kwargs: (True, []),
    )

    result = inventory_module._update_baseline_gate(
        tmp_path,
        reason="Extension approuvée de la dette de non-régression",
        approved_by="Alaeddine Ben Rhouma",
        allow_approved_baseline_extension=True,
    )

    assert result["success"] is True
    phase0 = next(
        check for check in result["checks"] if check["name"] == "phase0_tests"
    )
    assert phase0["success"] is True
    assert "approved_extension_bypass" in phase0
    payload = json.loads(
        (tmp_path / "audit/ANOMALIES_BASELINE.json").read_text(encoding="utf-8")
    )
    assert payload["active"] == current


def test_update_baseline_without_bootstrap_flag_still_requires_phase0_tests(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old_entry = _active_debt("a" * 16, qualification_digest="sha256:" + "1" * 64)
    current = _active_debt("a" * 16, qualification_digest="sha256:" + "2" * 64)
    _prepare_bootstrap_repository(
        tmp_path,
        inventory_module,
        monkeypatch,
        old_active=[old_entry],
        current_active=[current],
    )
    original_payload = (
        tmp_path / "audit/ANOMALIES_BASELINE.json"
    ).read_text(encoding="utf-8")

    result = inventory_module._update_baseline_gate(
        tmp_path,
        reason="Réalignement mécanique de qualification_digest",
        approved_by="Responsable éditorial",
        allow_qualification_digest_bootstrap=False,
    )

    assert result["success"] is False
    assert any("phase0_tests" in reason for reason in result["reasons"])
    assert (
        tmp_path / "audit/ANOMALIES_BASELINE.json"
    ).read_text(encoding="utf-8") == original_payload


@pytest.mark.parametrize(
    ("old_entry", "current"),
    [
        pytest.param(
            [_active_debt("a" * 16, qualification_digest="sha256:" + "1" * 64)],
            [
                _active_debt("a" * 16, qualification_digest="sha256:" + "2" * 64),
                _active_debt(
                    "b" * 16,
                    locator_key=(
                        "missing_corrections|1SPE|1SPE-SUITES|e2.tex|"
                        "corrige_tex|EX-002"
                    ),
                ),
            ],
            id="added_anomaly",
        ),
        pytest.param(
            [
                _active_debt("a" * 16, qualification_digest="sha256:" + "1" * 64),
                _active_debt(
                    "b" * 16,
                    locator_key=(
                        "missing_corrections|1SPE|1SPE-SUITES|e2.tex|"
                        "corrige_tex|EX-002"
                    ),
                ),
            ],
            [_active_debt("a" * 16, qualification_digest="sha256:" + "2" * 64)],
            id="removed_anomaly",
        ),
        pytest.param(
            [
                _active_debt(
                    "a" * 16,
                    qualification_digest="sha256:" + "1" * 64,
                    disposition="open_debt",
                )
            ],
            [
                _active_debt(
                    "a" * 16,
                    qualification_digest="sha256:" + "2" * 64,
                    disposition="intentional_reuse",
                )
            ],
            id="disposition_change",
        ),
        pytest.param(
            [
                _active_debt(
                    "a" * 16,
                    qualification_digest="sha256:" + "1" * 64,
                    owner="direction_scientifique_programme",
                )
            ],
            [
                _active_debt(
                    "a" * 16,
                    qualification_digest="sha256:" + "2" * 64,
                    owner="ingenierie_build_qualite",
                )
            ],
            id="owner_change",
        ),
    ],
)
def test_update_baseline_bootstrap_refuses_any_non_digest_drift(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    old_entry: list[dict[str, object]],
    current: list[dict[str, object]],
) -> None:
    _prepare_bootstrap_repository(
        tmp_path,
        inventory_module,
        monkeypatch,
        old_active=old_entry,
        current_active=current,
    )
    original_payload = (
        tmp_path / "audit/ANOMALIES_BASELINE.json"
    ).read_text(encoding="utf-8")

    result = inventory_module._update_baseline_gate(
        tmp_path,
        reason="Réalignement mécanique de qualification_digest",
        approved_by="Responsable éditorial",
        allow_qualification_digest_bootstrap=True,
    )

    assert result["success"] is False
    assert any(
        "bootstrap_digest_realignment" in reason for reason in result["reasons"]
    )
    assert (
        tmp_path / "audit/ANOMALIES_BASELINE.json"
    ).read_text(encoding="utf-8") == original_payload


@pytest.mark.parametrize(
    ("reason", "approved_by"),
    [
        pytest.param("", "Responsable éditorial", id="missing_reason"),
        pytest.param("Réalignement mécanique", "", id="missing_approved_by"),
    ],
)
def test_update_baseline_bootstrap_still_requires_reason_and_approver(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    reason: str,
    approved_by: str,
) -> None:
    monkeypatch.delenv("CI", raising=False)

    result = inventory_module._update_baseline_gate(
        tmp_path,
        reason=reason,
        approved_by=approved_by,
        allow_qualification_digest_bootstrap=True,
    )

    assert result["success"] is False
    assert any(
        "justification" in reason_value or "approbateur" in reason_value
        for reason_value in result["reasons"]
    )


def test_baseline_freeze_report_is_deterministic_and_counts_payload_debt(
    inventory_module,
) -> None:
    active = [
        _active_debt("1" * 16),
        {
            **_active_debt(
                "2" * 16,
                owner="direction_editoriale_pedagogique",
            ),
            "category": "chapters_not_in_manual",
        },
        {
            **_active_debt(
                "3" * 16,
                disposition="generated_dependency",
                owner="ingenierie_build_qualite",
                severity="warning",
            ),
            "category": "broken_latex_references",
        },
        {
            **_active_debt(
                "4" * 16,
                disposition="intentional_reuse",
                owner="direction_editoriale_pedagogique",
                severity="warning",
            ),
            "category": "duplicate_assembly_objects",
        },
    ]
    dispositions = {
        "1" * 16: {
            "qualification_policy_digest": "sha256:" + "d" * 64,
        },
        "2" * 16: {
            "qualification_policy_digest": "sha256:" + "d" * 64,
        },
        "3" * 16: {"policy_rule": "historical-evidence"},
        "4" * 16: {"policy_rule": "historical-evidence"},
    }
    payload = {
        "active": active,
        "baseline_purpose": "debt_regression_control",
        "release_acceptance": False,
    }
    keyword_arguments = {
        "approved_by": "Alaeddine Ben Rhouma",
        "dispositions": dispositions,
        "git_sha": "a" * 40,
        "new_digest": "sha256:" + "b" * 64,
        "payload": payload,
        "previous_digest": "sha256:" + "c" * 64,
        "reason": (
            "État initial qualifié de la dette existante après stabilisation "
            "de la Phase 0, utilisé exclusivement pour détecter les "
            "régressions et les nouvelles anomalies."
        ),
        "timestamp": "2026-07-30T10:00:00Z",
    }

    first = inventory_module._render_baseline_freeze_report(
        **keyword_arguments
    )
    second = inventory_module._render_baseline_freeze_report(
        **keyword_arguments
    )

    assert first == second
    assert "Fingerprints actifs : `4`" in first
    assert "Anomalies qualifiées par la politique : `2`" in first
    assert "Anomalies non qualifiées : `0`" in first
    assert "| `open_debt` | 2 |" in first
    assert "| `intentional_reuse` | 1 |" in first
    assert "| `generated_dependency` | 1 |" in first
    assert first.count("| `direction_scientifique_programme` | 1 |") == 2
    assert "| `direction_editoriale_pedagogique` | 2 |" in first
    assert "| `direction_editoriale_pedagogique` | 1 |" in first
    assert "| `ingenierie_build_qualite` | 1 |" in first
    assert "| `Bloquantes` | 2 |" in first
    assert "| `Non bloquantes` | 2 |" in first


def test_update_baseline_rejects_head_change_immediately_before_replace(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CI", raising=False)
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    _write(tmp_path / "tracked.txt", "source\n")
    schema_paths = tuple(
        path.relative_to(tmp_path).as_posix()
        for path in (tmp_path / "audit/schemas").rglob("*.json")
    )
    _track(tmp_path, "tracked.txt", *schema_paths)
    _commit_repository(tmp_path)
    baseline = _baseline_contract_payload()
    baseline["updates"] = []
    baseline["provisional"] = True
    _write(
        tmp_path / "audit/ANOMALIES_BASELINE.json",
        json.dumps(baseline, ensure_ascii=False),
    )
    _track(tmp_path, "audit/ANOMALIES_BASELINE.json")
    head_sha = _commit_repository(tmp_path, "baseline")
    generated_at = inventory_module._generation_timestamp(
        tmp_path,
        required=True,
    )
    inventory = {
        "anomalies": {},
        "anomaly_qualifications": {},
        "provenance": {
            "generated_at_utc": generated_at,
            "head_sha": head_sha,
        },
        "source_digest": "sha256:" + "e" * 64,
    }
    monkeypatch.setattr(
        inventory_module,
        "_model_digest",
        lambda _inventory: "sha256:" + "c" * 64,
    )
    monkeypatch.setattr(
        inventory_module,
        "_validate_model_gate",
        lambda _root: inventory_module._gate_result(
            "validate-model",
            success=True,
            failure_code=6,
            dimensions={"structure": "passed"},
            reasons=[],
        ),
    )
    monkeypatch.setattr(
        inventory_module,
        "_baseline_ready_gate",
        lambda _root: {
            **inventory_module._gate_result(
                "baseline-ready",
                success=True,
                failure_code=8,
                dimensions={"structure": "passed"},
                reasons=[],
            ),
            "checks": [
                _ready_check(name)
                for name in inventory_module.BASELINE_READY_CHECK_NAMES
            ],
        },
    )
    monkeypatch.setattr(
        inventory_module,
        "build_inventory",
        lambda _root, **_kwargs: inventory,
    )
    monkeypatch.setattr(
        inventory_module,
        "_current_active_debt",
        lambda _inventory: [],
    )
    real_ensure_clean = inventory_module._ensure_clean_tree
    ensure_calls = 0

    def change_head_after_second_clean_check(
        *args: object,
        **kwargs: object,
    ) -> None:
        nonlocal ensure_calls
        real_ensure_clean(*args, **kwargs)
        ensure_calls += 1
        if ensure_calls == 2:
            _commit_repository(tmp_path, "concurrent HEAD change")

    apply_calls = 0

    def record_apply(*_args: object, **_kwargs: object) -> None:
        nonlocal apply_calls
        apply_calls += 1

    monkeypatch.setattr(
        inventory_module,
        "_ensure_clean_tree",
        change_head_after_second_clean_check,
    )
    monkeypatch.setattr(
        inventory_module,
        "_apply_atomic_payloads",
        record_apply,
    )

    result = inventory_module._safe_update_baseline_gate(
        tmp_path,
        reason="Gel contrôlé",
        approved_by="Responsable éditorial",
    )

    assert result["success"] is False
    assert result["exit_code"] == 8
    assert any("HEAD modifié" in reason for reason in result["reasons"])
    assert apply_calls == 0


def test_update_baseline_recovers_interrupted_write_before_clean_preflight(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CI", raising=False)
    baseline = tmp_path / "audit/ANOMALIES_BASELINE.json"
    report = tmp_path / "audit/BASELINE_UPDATE_REPORT.md"
    freeze_report = tmp_path / "audit/BASELINE_FREEZE_REPORT.md"
    _write(baseline, "baseline historique\n")
    _write(report, "rapport historique\n")
    _write(freeze_report, "rapport de gel historique\n")
    child_code = f"""
import importlib.util
import os
from pathlib import Path

spec = importlib.util.spec_from_file_location("inventory_collection", {str(SCRIPT)!r})
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original_replace = module.os.replace

def crash_after_replace(source, destination, **kwargs):
    original_replace(source, destination, **kwargs)
    if str(source).startswith("stage-"):
        os._exit(95)

module.os.replace = crash_after_replace
module._apply_atomic_payloads(
    Path({str(tmp_path)!r}),
    {{
        Path("audit/ANOMALIES_BASELINE.json"): "baseline nouvelle\\n",
        Path("audit/BASELINE_UPDATE_REPORT.md"): "rapport nouveau\\n",
        Path("audit/BASELINE_FREEZE_REPORT.md"): "rapport gel nouveau\\n",
    }},
)
"""
    crashed = subprocess.run(
        [sys.executable, "-c", child_code],
        check=False,
    )
    assert crashed.returncode == 95

    restored_before_clean: list[bool] = []

    def observe_clean(_root: Path) -> dict[str, object]:
        restored_before_clean.append(
            baseline.read_text(encoding="utf-8") == "baseline historique\n"
            and report.read_text(encoding="utf-8") == "rapport historique\n"
            and freeze_report.read_text(encoding="utf-8")
            == "rapport de gel historique\n"
        )
        return inventory_module._gate_result(
            "require-clean",
            success=False,
            failure_code=4,
            dimensions={"structure": "failed"},
            reasons=["arrêt contrôlé après observation"],
        )

    monkeypatch.setattr(
        inventory_module,
        "_require_clean_gate",
        observe_clean,
    )

    result = inventory_module._update_baseline_gate(
        tmp_path,
        reason="Gel contrôlé",
        approved_by="Responsable éditorial",
    )

    assert result["success"] is False
    assert restored_before_clean == [True]
    assert list(tmp_path.glob(".inventory-collection-apply-*")) == []


def test_update_baseline_cli_boundary_maps_transaction_error_to_code_8(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise inventory_module.InventoryError("transaction injectée")

    monkeypatch.setattr(inventory_module, "_update_baseline_gate", fail)

    result = inventory_module._safe_update_baseline_gate(
        tmp_path,
        reason="Gel contrôlé",
        approved_by="Responsable",
    )

    assert result["success"] is False
    assert result["exit_code"] == 8
    assert result["reasons"] == ["update_error:transaction injectée"]


def _build_manifest_contract_payload() -> dict[str, object]:
    return {
        "artifact_type": "build_manifest",
        "build_state_digest": "sha256:" + "1" * 64,
        "builds": [
            {
                "excluded_objects": ["OBJ-EXCLUDED"],
                "gates": {
                    "compile": {"passed": True},
                    "preflight": {"passed": True},
                    "release_strict": {"blocker_count": 42, "passed": False},
                    "validate_model": {"passed": True},
                },
                "generated_dependencies": ["build/generated-index.tex"],
                "generated_dependency_digests": {
                    "build/generated-index.tex": "sha256:" + "6" * 64
                },
                "git_sha": "2" * 40,
                "included_objects": ["OBJ-SECOND", "OBJ-FIRST"],
                "manual": "1SPE",
                "model_digest": "sha256:" + "3" * 64,
                "ordered_trace": ["OBJ-SECOND", "OBJ-FIRST"],
                "page_count": 128,
                "pdf_path": "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf",
                "pdf_sha256": "sha256:" + "4" * 64,
                "reproducibility": {
                    "config_path": (
                        "Mathematiques/manuel-maths/config/"
                        "reproducible-build.json"
                    ),
                    "force_source_date": "1",
                    "locale": "C.UTF-8",
                    "pythonhashseed": "0",
                    "source_commit": "2" * 40,
                    "source_date_epoch": 1,
                    "timezone": "UTC",
                },
                "source_digest": "sha256:" + "5" * 64,
                "tool_versions": {
                    "lualatex": "LuaHBTeX, Version 1.17.0",
                    "pdfinfo": "pdfinfo version 24.02.0",
                    "pdffonts": "pdffonts version 24.02.0",
                    "python": "Python 3.12.3",
                },
                "variant": "professeur",
            }
        ],
        "generated_by": "build_manifest.py",
        "model_digest": "sha256:" + "3" * 64,
        "provenance": {
            "branch": "finalisation/collection-v1",
            "dirty": False,
            "head_sha": "2" * 40,
        },
        "schema_ref": "audit/schemas/v1/build-manifest.schema.json",
        "schema_version": 1,
        "source_digest": "sha256:" + "5" * 64,
    }


def test_build_manifest_schema_accepts_envelope_with_ordered_build_objects() -> None:
    schema = json.loads(
        (ROOT / "audit/schemas/v1/build-manifest.schema.json").read_text(
            encoding="utf-8"
        )
    )
    payload = _build_manifest_contract_payload()

    jsonschema.Draft202012Validator(schema).validate(payload)

    assert payload["builds"][0]["included_objects"] == [  # type: ignore[index]
        "OBJ-SECOND",
        "OBJ-FIRST",
    ]


@pytest.mark.parametrize(
    "missing_field",
    ["build_state_digest", "builds"],
)
def test_build_manifest_schema_rejects_missing_envelope_field(
    missing_field: str,
) -> None:
    schema = json.loads(
        (ROOT / "audit/schemas/v1/build-manifest.schema.json").read_text(
            encoding="utf-8"
        )
    )
    payload = _build_manifest_contract_payload()
    payload.pop(missing_field)

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


@pytest.mark.parametrize(
    "missing_field",
    [
        "excluded_objects",
        "gates",
        "generated_dependencies",
        "git_sha",
        "included_objects",
        "manual",
        "model_digest",
        "ordered_trace",
        "page_count",
        "pdf_path",
        "pdf_sha256",
        "source_digest",
        "tool_versions",
        "variant",
    ],
)
def test_build_manifest_schema_rejects_incomplete_observed_build(
    missing_field: str,
) -> None:
    schema = json.loads(
        (ROOT / "audit/schemas/v1/build-manifest.schema.json").read_text(
            encoding="utf-8"
        )
    )
    payload = _build_manifest_contract_payload()
    build = dict(payload["builds"][0])  # type: ignore[index]
    build.pop(missing_field)
    payload["builds"] = [build]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


def test_build_manifest_schema_rejects_unknown_build_field() -> None:
    schema = json.loads(
        (ROOT / "audit/schemas/v1/build-manifest.schema.json").read_text(
            encoding="utf-8"
        )
    )
    payload = _build_manifest_contract_payload()
    build = dict(payload["builds"][0])  # type: ignore[index]
    build["proof_by_filename_only"] = True
    payload["builds"] = [build]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


def test_build_manifest_schema_rejects_empty_observed_trace() -> None:
    schema = json.loads(
        (ROOT / "audit/schemas/v1/build-manifest.schema.json").read_text(
            encoding="utf-8"
        )
    )
    payload = _build_manifest_contract_payload()
    build = dict(payload["builds"][0])  # type: ignore[index]
    build["included_objects"] = []
    build["ordered_trace"] = []
    payload["builds"] = [build]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


def test_artifact_schema_loading_fails_when_the_registered_schema_is_absent(
    tmp_path: Path, inventory_module
) -> None:
    schema_ref = inventory_module._schema_ref_for("inventory_collection", 1)

    with pytest.raises(inventory_module.InventoryError, match="schéma absent"):
        inventory_module._load_artifact_schema(
            tmp_path,
            artifact_type="inventory_collection",
            schema_version=1,
            schema_ref=schema_ref,
        )


def test_artifact_schema_loading_fails_for_an_unknown_version(
    inventory_module,
) -> None:
    with pytest.raises(inventory_module.InventoryError, match="version de schéma inconnue"):
        inventory_module._schema_ref_for("inventory_collection", 999)


def test_canonical_model_payload_is_compact_stable_and_excludes_envelope_fields(
    inventory_module,
) -> None:
    inventory = {
        "source_digest": "sha256:" + "a" * 64,
        "source_files": ["z.tex", "a.tex"],
        "manuals": {"1SPE": {"objects": ["second", "first"]}},
        "anomalies": {"missing_corrections": [{"id": "EX-1"}]},
        "anomaly_qualifications": {
            "abc": {"blocking": True, "disposition": "open_debt"}
        },
        "reference_graph": [{"source": "z.tex", "cible": "a.tex"}],
        "correction_links": [{"exercise_id": "EX-1"}],
        "assemblies": [{"assembly_id": "second"}, {"assembly_id": "first"}],
        "pdfs": [{"path": "manual.pdf"}],
        "report_reconciliation": {"claims": []},
        "coherence_checks": {"status_distribution": {"ok": True}},
        "deliverable_matrix": {"manuals": {}},
        "schema_version": 1,
        "schema_ref": "ignored",
        "artifact_type": "ignored",
        "model_digest": "sha256:" + "b" * 64,
        "provenance": {"generated_at_utc": "ignored"},
        "observed_builds": [{"pdf": "ignored.pdf"}],
    }

    payload = inventory_module.canonical_model_payload(inventory)
    serialized = inventory_module._serialize_canonical_model(payload)

    assert list(payload) == [
        "anomalies",
        "anomaly_qualifications",
        "coherence_checks",
        "correction_links",
        "declared_assemblies",
        "deliverable_matrix",
        "manuals",
        "pdfs",
        "reference_graph",
        "report_reconciliation",
        "source_digest",
        "source_files",
    ]
    assert payload["source_files"] == ["z.tex", "a.tex"]
    assert payload["declared_assemblies"] == [
        {"assembly_id": "second"},
        {"assembly_id": "first"},
    ]
    assert "assemblies" not in payload
    assert serialized == json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    assert inventory_module._model_digest(inventory) == (
        "sha256:" + hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    )


def test_canonical_model_payload_accepts_declared_assemblies_without_legacy_key(
    inventory_module,
) -> None:
    declared = [{"assembly_id": "manual-professeur"}]
    inventory = {
        "anomalies": {},
        "anomaly_qualifications": {},
        "coherence_checks": {},
        "correction_links": [],
        "declared_assemblies": declared,
        "deliverable_matrix": {},
        "manuals": {},
        "pdfs": [],
        "reference_graph": [],
        "report_reconciliation": {},
        "source_digest": "sha256:" + "a" * 64,
        "source_files": [],
    }

    payload = inventory_module.canonical_model_payload(inventory)

    assert payload["declared_assemblies"] == declared
    assert "assemblies" not in payload


def test_canonical_model_rejects_divergent_assembly_alias(
    inventory_module,
) -> None:
    inventory = {
        "anomalies": {},
        "anomaly_qualifications": {},
        "assemblies": [{"assembly_id": "legacy"}],
        "coherence_checks": {},
        "correction_links": [],
        "declared_assemblies": [{"assembly_id": "canonical"}],
        "deliverable_matrix": {},
        "manuals": {},
        "pdfs": [],
        "reference_graph": [],
        "report_reconciliation": {},
        "source_digest": "sha256:" + "a" * 64,
        "source_files": [],
    }

    with pytest.raises(
        inventory_module.InventoryError,
        match="alias assemblies",
    ):
        inventory_module.canonical_model_payload(inventory)


def test_observed_builds_do_not_change_the_static_model_digest(
    inventory_module,
) -> None:
    inventory = {
        "anomalies": {},
        "anomaly_qualifications": {},
        "assemblies": [{"assembly_id": "manual-professeur"}],
        "coherence_checks": {},
        "correction_links": [],
        "declared_assemblies": [{"assembly_id": "manual-professeur"}],
        "deliverable_matrix": {},
        "manuals": {},
        "pdfs": [],
        "reference_graph": [],
        "report_reconciliation": {},
        "source_digest": "sha256:" + "a" * 64,
        "source_files": [],
    }
    before = inventory_module._model_digest(inventory)
    inventory["observed_builds"] = [{"manual": "1SPE", "variant": "professeur"}]
    inventory["observed_build_coverage"] = {
        "1SPE": {"professeur": {"observed": True}}
    }

    assert inventory_module._model_digest(inventory) == before


def test_build_manifest_is_excluded_from_source_and_model_digests(
    tmp_path: Path,
    inventory_module,
) -> None:
    _seed_cli_repository(tmp_path)
    before = inventory_module.build_inventory(tmp_path)
    head_sha = _commit_repository(tmp_path, "before build manifest")
    branch = subprocess.run(
        ["git", "-C", str(tmp_path), "branch", "--show-current"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    manifest = {
        "artifact_type": "build_manifest",
        "build_state_digest": inventory_module._build_state_digest([]),
        "builds": [],
        "generated_by": "build_manifest.py",
        "model_digest": inventory_module._model_digest(before),
        "provenance": {
            "branch": branch,
            "dirty": False,
            "head_sha": head_sha,
        },
        "schema_ref": "audit/schemas/v1/build-manifest.schema.json",
        "schema_version": 1,
        "source_digest": before["source_digest"],
    }
    _write(
        tmp_path / inventory_module.BUILD_MANIFEST_FILE,
        json.dumps(manifest, ensure_ascii=False, sort_keys=True),
    )
    _track(tmp_path, inventory_module.BUILD_MANIFEST_FILE)
    _commit_repository(tmp_path, "empty build manifest")

    after = inventory_module.build_inventory(tmp_path)

    assert inventory_module.BUILD_MANIFEST_FILE not in after["source_files"]
    assert after["source_digest"] == before["source_digest"]
    assert inventory_module._model_digest(after) == inventory_module._model_digest(
        before
    )


def test_rendering_the_same_inventory_twice_is_byte_identical_by_basename(
    tmp_path: Path, inventory_module
) -> None:
    inventory = _minimal_inventory(tmp_path, inventory_module)

    first = inventory_module._render_inventory_artifacts(
        inventory,
        repo_root=ROOT,
        audit_root=tmp_path / "first",
    )
    second = inventory_module._render_inventory_artifacts(
        inventory,
        repo_root=ROOT,
        audit_root=tmp_path / "second",
    )
    first_by_name = {path.name: content for path, content in first.items()}
    second_by_name = {path.name: content for path, content in second.items()}

    assert first_by_name == second_by_name
    machine_names = {
        "INVENTAIRE_COLLECTION.json",
        "ECARTS_ET_CONTRADICTIONS.yaml",
        "MATRICE_LIVRABLES.yaml",
    }
    parsed = {
        name: (
            json.loads(first_by_name[name])
            if name.endswith(".json")
            else yaml.safe_load(first_by_name[name])
        )
        for name in machine_names
    }
    for common_field in (
        "generated_by",
        "model_digest",
        "provenance",
        "schema_version",
        "source_digest",
    ):
        serialized_values = {
            json.dumps(payload[common_field], ensure_ascii=False, sort_keys=True)
            for payload in parsed.values()
        }
        assert len(serialized_values) == 1


def test_metadata_errors_are_not_duplicated_as_orphan_files(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    contract = f"{base}/contrat.yaml"
    missing_meta = f"{base}/cours/missing-meta.tex"
    malformed_meta = f"{base}/cours/malformed-meta.tex"
    orphan = "NSI/extras/orphan.tex"
    sources = {
        contract: _contract("1SPE-TEST", "1SPE", capacities=1),
        missing_meta: "Contenu sans en-tete META\n",
        malformed_meta: "% META: {json invalide}\n",
        orphan: "Contenu LaTeX valide mais non reference\n",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    orphan_paths = {
        anomaly["cible"] for anomaly in inventory["anomalies"]["orphan_files"]
    }

    assert {anomaly["path"] for anomaly in inventory["anomalies"]["metadata_missing"]} == {
        missing_meta
    }
    assert {anomaly["path"] for anomaly in inventory["anomalies"]["metadata_invalid"]} == {
        malformed_meta
    }
    assert orphan_paths == {orphan}


def test_only_explicitly_approved_status_is_publishable(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1NSI", "1NSI-TEST")
    sources = {
        f"{base}/contrat.yaml": _contract("1NSI-TEST", "1NSI", capacities=1),
        f"{base}/cours/approved.tex": _meta(
            id="APPROVED", chapitre="1NSI-TEST", status="approved"
        ),
        f"{base}/cours/generated.tex": _meta(
            id="GENERATED", chapitre="1NSI-TEST", status="generated"
        ),
        f"{base}/cours/spaces.tex": _meta(
            id="SPACES", chapitre="1NSI-TEST", status=" approved "
        ),
        f"{base}/cours/arbitrary.tex": _meta(
            id="ARBITRARY", chapitre="1NSI-TEST", status="publie-peut-etre"
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    anomalies = inventory["anomalies"]

    assert [item["id"] for item in anomalies["blocking_statuses"]] == [
        "ARBITRARY",
        "GENERATED",
        "SPACES",
    ]
    assert anomalies["invalid_statuses"] == [
        {
            "normalized_status": "publie-peut-etre",
            "path": f"{base}/cours/arbitrary.tex",
            "reason": "statut inconnu",
            "scope": "object",
            "source_status": "publie-peut-etre",
        },
        {
            "normalized_status": "approved",
            "path": f"{base}/cours/spaces.tex",
            "reason": "statut non canonique",
            "scope": "object",
            "source_status": " approved ",
        },
    ]
    chapter = inventory["manuals"]["1NSI"]["chapters"]["1NSI-TEST"]
    assert chapter["statuses"] == {
        "approved": 2,
        "generated": 1,
        "publie-peut-etre": 1,
    }
    by_id = {item["id"]: item for item in chapter["objects"]}
    assert by_id["SPACES"]["status"] == "approved"
    assert by_id["SPACES"]["status_valid"] is False
    assert by_id["APPROVED"]["publishable"] is True
    assert by_id["SPACES"]["publishable"] is False


def test_all_math_and_nsi_object_schema_statuses_are_recognized_but_only_approved_publishes(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1NSI", "1NSI-TEST")
    statuses = (
        "approved",
        "draft",
        "generated",
        "manual_review",
        "needs_review",
        "ready",
        "rejected",
        "verified",
    )
    sources = {f"{base}/contrat.yaml": _contract("1NSI-TEST", "1NSI", capacities=1)}
    for status in statuses:
        sources[f"{base}/cours/{status}.tex"] = _meta(
            id=f"STATUS-{status}", chapitre="1NSI-TEST", status=status
        )
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    anomalies = inventory["anomalies"]
    chapter = inventory["manuals"]["1NSI"]["chapters"]["1NSI-TEST"]

    assert anomalies["invalid_statuses"] == []
    assert {item["id"] for item in anomalies["blocking_statuses"]} == {
        f"STATUS-{status}" for status in statuses if status != "approved"
    }
    assert {
        item["source_status"]: item["publishable"] for item in chapter["objects"]
    } == {status: status == "approved" for status in statuses}


def test_contract_status_vocabulary_is_separate_and_requires_explicit_approval(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    contract_statuses = ("approved", "complete", "draft", "valide")
    sources = {}
    for status in contract_statuses:
        chapter = f"1SPE-TEST-{status.upper()}"
        base = _chapter_path("1SPE", chapter)
        sources[f"{base}/contrat.yaml"] = _contract(
            chapter, "1SPE", capacities=1
        ).replace("statut: approved", f"statut: {status}")
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    anomalies = inventory["anomalies"]

    assert anomalies["invalid_statuses"] == []
    assert {
        (item["chapter"], item["status"]) for item in anomalies["blocking_statuses"]
    } == {
        ("1SPE-TEST-COMPLETE", "complete"),
        ("1SPE-TEST-DRAFT", "draft"),
        ("1SPE-TEST-VALIDE", "valide"),
    }


def test_only_well_formed_contract_capacities_are_counted_and_each_error_is_reported(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-CAPACITES")
    contract_path = f"{base}/contrat.yaml"
    _write(
        tmp_path / contract_path,
        """chapitre: 1SPE-CAPACITES
niveau: 1SPE
statut: approved
capacites:
  - {code: C1, ref_capacite: 1SPE-CAPACITES-C1}
  - entree-non-objet
  - {code: C3, ref_capacite: ""}
  - {code: C4, ref_capacite: 4}
""",
    )
    second_chapter = _chapter_path("1SPE", "1SPE-CAPACITES-NON-LISTE")
    second_contract = f"{second_chapter}/contrat.yaml"
    _write(
        tmp_path / second_contract,
        """chapitre: 1SPE-CAPACITES-NON-LISTE
niveau: 1SPE
statut: approved
capacites: pas-une-liste
""",
    )
    _track(tmp_path, contract_path, second_contract)

    inventory = inventory_module.build_inventory(tmp_path)
    first = inventory["manuals"]["1SPE"]["chapters"]["1SPE-CAPACITES"]
    second = inventory["manuals"]["1SPE"]["chapters"]["1SPE-CAPACITES-NON-LISTE"]

    assert first["counts"]["capacites"] == 1
    assert [capacity["ref_capacite"] for capacity in first["capacities"]] == [
        "1SPE-CAPACITES-C1"
    ]
    assert second["counts"]["capacites"] == 0
    assert inventory["anomalies"]["invalid_capacities"] == [
        {
            "index": None,
            "path": second_contract,
            "reason": "capacites doit etre une liste",
        },
        {
            "index": 1,
            "path": contract_path,
            "reason": "capacite doit etre un objet",
        },
        {
            "index": 2,
            "path": contract_path,
            "reason": "ref_capacite doit etre un texte non vide",
        },
        {
            "index": 3,
            "path": contract_path,
            "reason": "ref_capacite doit etre un texte non vide",
        },
    ]


def test_path_meta_and_contract_context_mismatches_are_explicit(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-CONTEXTE")
    contract_path = f"{base}/contrat.yaml"
    object_path = f"{base}/cours/c1.tex"
    _write(
        tmp_path / contract_path,
        _contract("1SPE-AUTRE", "TSPE", capacities=1),
    )
    _write(
        tmp_path / object_path,
        _meta(
            id="1SPE-CONTEXTE-COURS-C1",
            chapitre="1SPE-META-AUTRE",
            status="approved",
        ),
    )
    _track(tmp_path, contract_path, object_path)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["context_mismatches"] == [
        {
            "actual": "1SPE-AUTRE",
            "expected": "1SPE-CONTEXTE",
            "field": "chapitre",
            "path": contract_path,
            "scope": "contract",
        },
        {
            "actual": "TSPE",
            "expected": "1SPE",
            "field": "niveau",
            "path": contract_path,
            "scope": "contract",
        },
        {
            "actual": "1SPE-META-AUTRE",
            "expected": "1SPE-CONTEXTE",
            "field": "chapitre",
            "path": object_path,
            "scope": "object",
        },
    ]


def test_duplicate_capacity_references_are_detected_across_chapters(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    first_chapter = "1SPE-PREMIER"
    second_chapter = "1SPE-SECOND"
    first = f"{_chapter_path('1SPE', first_chapter)}/contrat.yaml"
    second = f"{_chapter_path('1SPE', second_chapter)}/contrat.yaml"
    shared_reference = "1SPE-CAPACITE-PARTAGEE"
    _write(
        tmp_path / first,
        _contract(first_chapter, "1SPE", capacities=1).replace(
            f"{first_chapter}-C1", shared_reference
        ),
    )
    _write(
        tmp_path / second,
        _contract(second_chapter, "1SPE", capacities=1).replace(
            f"{second_chapter}-C1", shared_reference
        ),
    )
    _track(tmp_path, first, second)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["duplicate_capacity_refs"] == [
        {
            "occurrences": [
                {
                    "chapter": first_chapter,
                    "index": 0,
                    "manual": "1SPE",
                    "path": first,
                },
                {
                    "chapter": second_chapter,
                    "index": 0,
                    "manual": "1SPE",
                    "path": second,
                },
            ],
            "ref_capacite": shared_reference,
        }
    ]


def test_unknown_chapter_prefix_is_never_silently_ignored(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = "NSI/chapitres/INCONNU-TEST"
    sources = {
        f"{base}/contrat.yaml": _contract("INCONNU-TEST", "INCONNU", capacities=1),
        f"{base}/cours/c1.tex": _meta(
            id="INCONNU-TEST-C1", chapitre="INCONNU-TEST", status="approved"
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["unknown_chapter_prefixes"] == [
        {
            "chapter": "INCONNU-TEST",
            "path": f"{base}/contrat.yaml",
            "reason": "prefixe de chapitre sans manuel canonique",
        },
        {
            "chapter": "INCONNU-TEST",
            "path": f"{base}/cours/c1.tex",
            "reason": "prefixe de chapitre sans manuel canonique",
        },
    ]
    assert all(not manual["chapters"] for manual in inventory["manuals"].values())


def test_source_digest_uses_only_tracked_relevant_sources(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    contract = f"{base}/contrat.yaml"
    course = f"{base}/cours/c1.tex"
    readme = "README.md"
    _write(tmp_path / contract, _contract("1SPE-TEST", "1SPE", capacities=1))
    _write(tmp_path / course, _meta())
    _write(tmp_path / readme, "Documentation sans effet sur le contenu\n")
    _track(tmp_path, contract, course, readme)

    first = inventory_module.build_inventory(tmp_path)["source_digest"]
    _write(tmp_path / f"{base}/cours/untracked.tex", _meta(id="UNTRACKED"))
    assert inventory_module.build_inventory(tmp_path)["source_digest"] == first

    _write(tmp_path / readme, "Documentation modifiee\n")
    assert inventory_module.build_inventory(tmp_path)["source_digest"] == first

    _write(tmp_path / course, _meta(status="approved"))
    assert inventory_module.build_inventory(tmp_path)["source_digest"] != first


def test_reference_graph_reports_missing_correction_and_broken_meta_and_latex_targets(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    contract = f"{base}/contrat.yaml"
    exercise = f"{base}/exercices/1SPE-TEST-EX-001.tex"
    course = f"{base}/cours/10_cours.tex"
    missing_correction = "chapitres/1SPE-TEST/corriges/1SPE-TEST-CO-001.tex"
    missing_source = "corpus/source-absente.md"
    missing_input = "chapitres/1SPE-TEST/cours/fragment-absent.tex"
    _write(tmp_path / contract, _contract("1SPE-TEST", "1SPE", capacities=1))
    _write(
        tmp_path / exercise,
        _meta(
            id="1SPE-TEST-EX-001",
            type_objet="exercice",
            fichier_tex="chapitres/1SPE-TEST/exercices/1SPE-TEST-EX-001.tex",
            corrige_tex=missing_correction,
            sources_inspiration=[missing_source],
        ),
    )
    _write(
        tmp_path / course,
        _meta(id="1SPE-TEST-COURS-C1", status="approved")
        + f"\\input{{{missing_input.removesuffix('.tex')}}}\n",
    )
    _track(tmp_path, contract, exercise, course)

    inventory = inventory_module.build_inventory(tmp_path)
    anomalies = inventory["anomalies"]

    assert {
        (item["source"], item["cible"], item["champ"], item["raison"])
        for item in anomalies["broken_meta_references"]
    } == {
        (
            exercise,
            f"Mathematiques/manuel-maths/{missing_correction}",
            "corrige_tex",
            "chemin META absent des sources suivies",
        ),
    }
    assert anomalies["unavailable_inspiration_sources"] == [
        {
            "source": exercise,
            "cible": f"Mathematiques/manuel-maths/{missing_source}",
            "champ": "sources_inspiration[0]",
            "raison": "source d'inspiration absente des sources suivies",
        }
    ]
    assert anomalies["broken_latex_references"] == [
        {
            "champ": "input",
            "cible": f"Mathematiques/manuel-maths/{missing_input}",
            "raison": "cible LaTeX absente des sources suivies",
            "source": course,
        }
    ]
    assert anomalies["missing_corrections"] == [
        {
            "champ": "corrige_tex",
            "cible": f"Mathematiques/manuel-maths/{missing_correction}",
            "raison": "aucun corrige suivi ne resout cet exercice",
            "source": exercise,
        }
    ]
    assert any(
        edge["source"] == exercise
        and edge["champ"] == "fichier_tex"
        and edge["resolved"] is True
        for edge in inventory["reference_graph"]
    )


def test_reverse_and_conventional_correction_links_prevent_false_missing_reports(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1NSI", "1NSI-TEST")
    sources = {
        f"{base}/contrat.yaml": _contract("1NSI-TEST", "1NSI", capacities=1),
        f"{base}/exercices/1NSI-TEST-EX-001.tex": _meta(
            id="1NSI-TEST-EX-001",
            chapitre="1NSI-TEST",
            type_objet="exercice",
            status="approved",
        ),
        f"{base}/corriges/1NSI-TEST-CO-001.tex": _meta(
            id="1NSI-TEST-CO-001",
            chapitre="1NSI-TEST",
            type_objet="corrige",
            status="approved",
        ),
        f"{base}/exercices/1NSI-TEST-EX-002.tex": _meta(
            id="1NSI-TEST-EX-002",
            chapitre="1NSI-TEST",
            type_objet="exercice",
            status="approved",
        ),
        f"{base}/corriges/correction-libre.tex": _meta(
            id="CORRECTION-LIBRE",
            chapitre="1NSI-TEST",
            type_objet="corrige",
            exercice_ref="1NSI-TEST-EX-002",
            status="approved",
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["missing_corrections"] == []
    assert {
        (link["exercise_id"], link["correction_id"], link["mode"])
        for link in inventory["correction_links"]
    } == {
        ("1NSI-TEST-EX-001", "1NSI-TEST-CO-001", "id_convention"),
        ("1NSI-TEST-EX-002", "CORRECTION-LIBRE", "reverse_meta"),
    }


def test_meta_capacity_references_resolve_local_codes_and_report_unknown_ids(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    contract = f"{base}/contrat.yaml"
    course = f"{base}/cours/10_cours.tex"
    _write(tmp_path / contract, _contract("1SPE-TEST", "1SPE", capacities=1))
    _write(
        tmp_path / course,
        _meta(
            id="1SPE-TEST-COURS-C1",
            status="approved",
            capacites=["C1", "1SPE-TEST-C9"],
        ),
    )
    _track(tmp_path, contract, course)

    inventory = inventory_module.build_inventory(tmp_path)

    edges = [
        item for item in inventory["reference_graph"] if item["kind"] == "capacity"
    ]
    assert edges == [
        {
            "champ": "capacites[0]",
            "cible": "1SPE-TEST-C1",
            "kind": "capacity",
            "resolved": True,
            "source": course,
        },
        {
            "champ": "capacites[1]",
            "cible": "1SPE-TEST-C9",
            "kind": "capacity",
            "resolved": False,
            "source": course,
        },
    ]
    assert inventory["anomalies"]["broken_meta_references"] == [
        {
            "champ": "capacites[1]",
            "cible": "1SPE-TEST-C9",
            "raison": "capacite META absente du contrat du chapitre",
            "source": course,
        }
    ]


def test_source_digest_includes_tracked_targets_reached_by_meta_graph(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1NSI", "1NSI-TEST")
    contract = f"{base}/contrat.yaml"
    course = f"{base}/cours/10_cours.tex"
    inspiration = "NSI/corpus/source.md"
    _write(tmp_path / contract, _contract("1NSI-TEST", "1NSI", capacities=1))
    _write(
        tmp_path / course,
        _meta(
            id="1NSI-TEST-COURS-C1",
            chapitre="1NSI-TEST",
            status="approved",
            sources_inspiration=["corpus/source.md"],
        ),
    )
    _write(tmp_path / inspiration, "version une\n")
    _track(tmp_path, contract, course, inspiration)

    first = inventory_module.build_inventory(tmp_path)
    _write(tmp_path / inspiration, "version deux\n")
    second = inventory_module.build_inventory(tmp_path)

    assert inspiration in first["source_files"]
    assert first["source_digest"] != second["source_digest"]


def test_analyze_assembler_reads_constants_and_variants_without_execution(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble.py"
    _write(
        assembler,
        """raise RuntimeError("ce module ne doit jamais etre execute")
ORDER = [("cours", "1*"), ("exercices", "*")]
CHAPITRES = ["1SPE-TEST", "1SPE-AUTRE"]
VARIANTES = ["complet", "methodes"]
ELEVE_EXCLUDES = {"corriges", "evaluations"}
ELEVE_ALLOWED_TYPES = {"cours", "evaluation", "exercice"}
parser.add_argument("--variant", choices=["eleve", "professeur"])
""",
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert analysis["constants"] == {
        "CHAPITRES": ["1SPE-TEST", "1SPE-AUTRE"],
        "ELEVE_ALLOWED_TYPES": ["cours", "evaluation", "exercice"],
        "ELEVE_EXCLUDES": ["corriges", "evaluations"],
        "ORDER": [["cours", "1*"], ["exercices", "*"]],
        "VARIANTES": ["complet", "methodes"],
    }
    assert analysis["variants"] == [
        "complet",
        "eleve",
        "methodes",
        "professeur",
    ]


def test_manual_variant_orders_are_literal_closed_and_validated(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        '''CHAPITRES = ["1NSI-TEST"]
ORDER = [("cours", "*")]
VARIANTS = ["eleve", "professeur", "evaluations", "projets"]
VARIANT_ORDERS = {
    "eleve": [("cours", "*")],
    "professeur": [("cours", "*"), ("corriges", "*")],
    "evaluations": [("evaluations", "*")],
    "projets": [("projet", "*")],
}
ELEVE_VARIANTS = {"eleve", "projets"}
ELEVE_ALLOWED_TYPES = {"cours", "projet"}
''',
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert analysis["constants"]["VARIANT_ORDERS"] == {
        "eleve": [["cours", "*"]],
        "evaluations": [["evaluations", "*"]],
        "professeur": [["cours", "*"], ["corriges", "*"]],
        "projets": [["projet", "*"]],
    }
    assert analysis["constants"]["ELEVE_VARIANTS"] == ["eleve", "projets"]
    assert inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    ) == []


@pytest.mark.parametrize(
    ("variant_orders", "student_variants", "expected_field"),
    [
        (
            '{"eleve": [("cours", "*")]}',
            '["eleve"]',
            "VARIANT_ORDERS",
        ),
        (
            '{"eleve": [], "professeur": [("cours", "*")]}',
            '["eleve"]',
            "VARIANT_ORDERS",
        ),
        (
            '{"eleve": [("", "*")], "professeur": [("cours", "*")]}',
            '["eleve"]',
            "VARIANT_ORDERS",
        ),
        (
            '{"eleve": [("cours", "*")], "professeur": [("cours", "*")]}',
            "[]",
            "ELEVE_VARIANTS",
        ),
        (
            '{"eleve": [("cours", "*")], "professeur": [("cours", "*")]}',
            '["professeur"]',
            "ELEVE_VARIANTS",
        ),
        (
            '{"eleve": [("cours", "*")], "professeur": [("cours", "*")]}',
            '["eleve", "inconnue"]',
            "ELEVE_VARIANTS",
        ),
    ],
    ids=(
        "partial-orders",
        "empty-rules",
        "empty-directory",
        "empty-student-variants",
        "missing-eleve",
        "foreign-student-variant",
    ),
)
def test_closed_manual_variant_contract_rejects_invalid_literals(
    tmp_path: Path,
    inventory_module,
    variant_orders: str,
    student_variants: str,
    expected_field: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        'CHAPITRES = ["1NSI-TEST"]\n'
        'ORDER = [("cours", "*")]\n'
        'VARIANTS = ["eleve", "professeur"]\n'
        f"VARIANT_ORDERS = {variant_orders}\n"
        f"ELEVE_VARIANTS = {student_variants}\n"
        'ELEVE_ALLOWED_TYPES = ["cours"]\n',
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert expected_field in {field for field, _reason in errors}


@pytest.mark.parametrize(
    ("contract_declaration", "missing_field"),
    [
        (
            'VARIANT_ORDERS = {"eleve": [("cours", "*")]}\n',
            "ELEVE_VARIANTS",
        ),
        ('ELEVE_VARIANTS = ["eleve"]\n', "VARIANT_ORDERS"),
        ('VARIANT_ORDERS = build_orders()\n', "VARIANT_ORDERS"),
        (
            'VARIANT_ORDERS = {"eleve": [("cours", "*")]}\n'
            "VARIANT_ORDERS = build_orders()\n",
            "VARIANT_ORDERS",
        ),
        (
            'ELEVE_VARIANTS = ["eleve"]\n'
            "ELEVE_VARIANTS = build_student_variants()\n",
            "ELEVE_VARIANTS",
        ),
    ],
    ids=(
        "orders-only",
        "student-variants-only",
        "dynamic-orders",
        "reassigned-dynamic-orders",
        "reassigned-dynamic-student-variants",
    ),
)
def test_closed_manual_variant_contract_cannot_be_declared_partially(
    tmp_path: Path,
    inventory_module,
    contract_declaration: str,
    missing_field: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        'CHAPITRES = ["1NSI-TEST"]\n'
        'ORDER = [("cours", "*")]\n'
        'VARIANTS = ["eleve"]\n'
        'ELEVE_ALLOWED_TYPES = ["cours"]\n'
        + contract_declaration,
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert missing_field in {field for field, _reason in errors}


def test_closed_contract_rejects_chained_dynamic_declarations(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        '''CHAPITRES = ["1NSI-TEST"]
ORDER = [("cours", "*")]
VARIANTS = ["eleve"]
ELEVE_ALLOWED_TYPES = ["cours"]
VARIANT_ORDERS = orders = build_orders()
ELEVE_VARIANTS = student_variants = build_student_variants()
''',
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert {field for field, _reason in errors} >= {
        "ELEVE_VARIANTS",
        "VARIANT_ORDERS",
    }


def test_closed_contract_rejects_conditional_reassignments(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        '''CHAPITRES = ["1NSI-TEST"]
ORDER = [("cours", "*")]
VARIANTS = ["eleve"]
VARIANT_ORDERS = {"eleve": [("cours", "*")]}
ELEVE_VARIANTS = ["eleve"]
ELEVE_ALLOWED_TYPES = ["cours"]
if contract_enabled:
    VARIANT_ORDERS = build_orders()
    ELEVE_VARIANTS = build_student_variants()
''',
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert {field for field, _reason in errors} >= {
        "ELEVE_VARIANTS",
        "VARIANT_ORDERS",
    }


def test_closed_contract_rejects_non_string_variant_order_keys(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        '''CHAPITRES = ["1NSI-TEST"]
ORDER = [("cours", "*")]
VARIANTS = ["1", "eleve"]
VARIANT_ORDERS = {1: [("cours", "*")], "eleve": [("cours", "*")]}
ELEVE_VARIANTS = ["eleve"]
ELEVE_ALLOWED_TYPES = ["cours"]
''',
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "VARIANT_ORDERS" in {field for field, _reason in errors}


def test_closed_contract_uses_last_supported_top_level_assignment(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        '''CHAPITRES = ["1NSI-TEST"]
ORDER = [("cours", "*")]
VARIANTS = ["eleve"]
VARIANT_ORDERS = build_orders()
VARIANT_ORDERS = {"eleve": [("cours", "*")]}
ELEVE_VARIANTS = build_student_variants()
ELEVE_VARIANTS = ["eleve"]
ELEVE_ALLOWED_TYPES = ["cours"]
''',
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    ) == []


def _closed_contract_source(extra: str = "") -> str:
    return (
        '''CHAPITRES = ["1NSI-TEST"]
ORDER = [("cours", "*")]
VARIANTS = ["eleve", "professeur"]
VARIANT_ORDERS = {
    "eleve": [("cours", "*")],
    "professeur": [("cours", "*"), ("corriges", "*")],
}
ELEVE_VARIANTS = ["eleve"]
ELEVE_ALLOWED_TYPES = ["cours"]
ELEVE_EXCLUDES = []
'''
        + extra
    )


@pytest.mark.parametrize(
    ("mutation", "expected_field"),
    [
        (
            'VARIANT_ORDERS["eleve"] = [("corriges", "*")]\n',
            "VARIANT_ORDERS",
        ),
        ('ELEVE_VARIANTS.append("professeur")\n', "ELEVE_VARIANTS"),
        ('ELEVE_ALLOWED_TYPES.append("corrige")\n', "ELEVE_ALLOWED_TYPES"),
        ('ELEVE_EXCLUDES += ["corriges"]\n', "ELEVE_EXCLUDES"),
        (
            'VARIANT_ORDERS.update({"eleve": [("corriges", "*")]})\n',
            "VARIANT_ORDERS",
        ),
    ],
    ids=(
        "subscript-assignment",
        "student-variant-append",
        "student-type-append",
        "excludes-iadd",
        "variant-order-update",
    ),
)
def test_closed_contract_rejects_module_scope_runtime_mutations(
    tmp_path: Path,
    inventory_module,
    mutation: str,
    expected_field: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(assembler, _closed_contract_source(mutation))

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert expected_field in {field for field, _reason in errors}


def test_closed_contract_ignores_function_local_names_and_mutations(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''def configure_local_contract(ELEVE_ALLOWED_TYPES):
    VARIANT_ORDERS = build_orders()
    ELEVE_VARIANTS = build_student_variants()
    ELEVE_ALLOWED_TYPES.append("corrige")
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    ) == []


def test_closed_contract_rejects_unshadowed_function_mutations(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''def mutate_unshadowed_contract():
    VARIANT_ORDERS["eleve"] = [("corriges", "*")]
    ELEVE_ALLOWED_TYPES.append("corrige")
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert {field for field, _reason in errors} >= {
        "ELEVE_ALLOWED_TYPES",
        "VARIANT_ORDERS",
    }


def test_closed_contract_rejects_function_global_mutations(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''def mutate_global_contract():
    global VARIANT_ORDERS, ELEVE_ALLOWED_TYPES
    VARIANT_ORDERS = build_orders()
    ELEVE_ALLOWED_TYPES.append("corrige")
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert {field for field, _reason in errors} >= {
        "ELEVE_ALLOWED_TYPES",
        "VARIANT_ORDERS",
    }


def test_closed_contract_rejects_module_conditional_mutation(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''if contract_enabled:
    ELEVE_ALLOWED_TYPES.append("corrige")
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "ELEVE_ALLOWED_TYPES" in {field for field, _reason in errors}


@pytest.mark.parametrize(
    ("binding", "expected_field"),
    [
        ("import runtime_order as ORDER\n", "ORDER"),
        (
            "from runtime_types import values as ELEVE_ALLOWED_TYPES\n",
            "ELEVE_ALLOWED_TYPES",
        ),
        ("def VARIANT_ORDERS():\n    pass\n", "VARIANT_ORDERS"),
        ("class ELEVE_VARIANTS:\n    pass\n", "ELEVE_VARIANTS"),
        (
            'match payload:\n    case {"order": ORDER}:\n        pass\n',
            "ORDER",
        ),
    ],
    ids=("import", "import-from", "function", "class", "match-capture"),
)
def test_closed_contract_rejects_module_scope_bindings(
    tmp_path: Path,
    inventory_module,
    binding: str,
    expected_field: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(assembler, _closed_contract_source(binding))

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert expected_field in {field for field, _reason in errors}


def test_closed_contract_rejects_function_global_import_binding(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''def replace_global_order():
    global ORDER
    import runtime_order as ORDER
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "ORDER" in {field for field, _reason in errors}


def test_closed_contract_rejects_module_star_import_used_by_function(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''from runtime_contract import *

def select_rules(variant):
    return VARIANT_ORDERS[variant]
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert {field for field, _reason in errors} >= {
        "ELEVE_ALLOWED_TYPES",
        "VARIANT_ORDERS",
    }


def test_module_star_import_does_not_opt_legacy_assembler_into_closed_contract(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        '''CHAPITRES = ["1NSI-TEST"]
ORDER = [("cours", "*")]
VARIANTS = ["eleve"]
ELEVE_ALLOWED_TYPES = ["cours"]
from runtime_contract import *
''',
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    ) == []


def test_closed_contract_allows_class_attributes_with_audited_names(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''class LocalContract:
    ORDER = [("corriges", "*")]
    ELEVE_ALLOWED_TYPES = ["corrige"]
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    ) == []


def test_closed_contract_allows_class_local_binding_before_mutation(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''class LocalContract:
    ELEVE_ALLOWED_TYPES = []
    ELEVE_ALLOWED_TYPES.append("corrige")
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    ) == []


def test_closed_contract_rejects_unshadowed_class_body_mutation(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''class ContractMutator:
    ELEVE_ALLOWED_TYPES.append("corrige")
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "ELEVE_ALLOWED_TYPES" in {field for field, _reason in errors}


def test_closed_contract_rejects_unshadowed_class_augmented_assignment(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''class ContractMutator:
    ELEVE_ALLOWED_TYPES += ["corrige"]
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "ELEVE_ALLOWED_TYPES" in {field for field, _reason in errors}


def test_closed_contract_class_delete_reexposes_global_binding(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''class ContractMutator:
    ELEVE_ALLOWED_TYPES = []
    del ELEVE_ALLOWED_TYPES
    ELEVE_ALLOWED_TYPES.append("corrige")
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "ELEVE_ALLOWED_TYPES" in {field for field, _reason in errors}


@pytest.mark.parametrize(
    "class_body",
    [
        '''    ELEVE_ALLOWED_TYPES.append("corrige")
    ELEVE_ALLOWED_TYPES = []
''',
        '''    if enabled:
        ELEVE_ALLOWED_TYPES = []
    ELEVE_ALLOWED_TYPES.append("corrige")
''',
    ],
    ids=("later-binding", "conditional-binding"),
)
def test_closed_contract_class_bindings_do_not_mask_global_retroactively(
    tmp_path: Path,
    inventory_module,
    class_body: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source("class ContractMutator:\n" + class_body),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "ELEVE_ALLOWED_TYPES" in {field for field, _reason in errors}


def test_closed_contract_rejects_method_mutating_unshadowed_global(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''class ContractMutator:
    def mutate(self):
        ELEVE_ALLOWED_TYPES.append("corrige")
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "ELEVE_ALLOWED_TYPES" in {field for field, _reason in errors}


@pytest.mark.parametrize(
    ("alias_binding", "expected_field"),
    [
        (
            "alias = VARIANT_ORDERS\n"
            'alias.update({"eleve": [("corriges", "*")]})\n',
            "VARIANT_ORDERS",
        ),
        (
            "alias = ELEVE_ALLOWED_TYPES\n"
            'alias.append("corrige")\n',
            "ELEVE_ALLOWED_TYPES",
        ),
        (
            "def mutate_alias():\n"
            "    alias = VARIANT_ORDERS\n"
            '    alias.update({"eleve": [("corriges", "*")]})\n',
            "VARIANT_ORDERS",
        ),
    ],
    ids=("module-dict", "module-list", "function-dict"),
)
def test_closed_contract_rejects_aliases_of_global_mutable_constants(
    tmp_path: Path,
    inventory_module,
    alias_binding: str,
    expected_field: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(assembler, _closed_contract_source(alias_binding))

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert expected_field in {field for field, _reason in errors}


@pytest.mark.parametrize(
    ("escape", "expected_field"),
    [
        ("mutate(VARIANT_ORDERS)\n", "VARIANT_ORDERS"),
        ("helper(values=ELEVE_ALLOWED_TYPES)\n", "ELEVE_ALLOWED_TYPES"),
        ("def helper(orders=VARIANT_ORDERS):\n    pass\n", "VARIANT_ORDERS"),
        ('box = {"orders": VARIANT_ORDERS}\n', "VARIANT_ORDERS"),
        ("box = [ELEVE_ALLOWED_TYPES]\n", "ELEVE_ALLOWED_TYPES"),
    ],
    ids=("call", "keyword", "default", "dict", "list"),
)
def test_closed_contract_rejects_mutable_constant_escapes(
    tmp_path: Path,
    inventory_module,
    escape: str,
    expected_field: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(assembler, _closed_contract_source(escape))

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert expected_field in {field for field, _reason in errors}


def test_closed_contract_rejects_mutation_through_indexed_rules_alias(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''def mutate_rules():
    rules = VARIANT_ORDERS["eleve"]
    rules[:] = [("corriges", "*")]
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "VARIANT_ORDERS" in {field for field, _reason in errors}


def test_closed_contract_rejects_global_alias_of_indexed_rules(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''def expose_rules():
    global rules
    rules = VARIANT_ORDERS["eleve"]
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "VARIANT_ORDERS" in {field for field, _reason in errors}


@pytest.mark.parametrize(
    ("mutation", "expected_field"),
    [
        (
            '''def mutate_rules():
    for rules in VARIANT_ORDERS.values():
        rules.append(("corriges", "*"))
''',
            "VARIANT_ORDERS",
        ),
        (
            '''def mutate_rules():
    for _variant, rules in VARIANT_ORDERS.items():
        rules.append(("corriges", "*"))
''',
            "VARIANT_ORDERS",
        ),
        (
            '''def mutate_rules():
    rules = VARIANT_ORDERS.get("eleve")
    rules.append(("corriges", "*"))
''',
            "VARIANT_ORDERS",
        ),
        (
            '''def mutate_rule():
    rule = ORDER[0]
    rule[0] = "corriges"
''',
            "ORDER",
        ),
        (
            '''def mutate_rules():
    for rules in [VARIANT_ORDERS["eleve"]]:
        rules.append(("corriges", "*"))
''',
            "VARIANT_ORDERS",
        ),
        (
            '''def mutate_rules():
    [
        rules.append(("corriges", "*"))
        for rules in [VARIANT_ORDERS["eleve"]]
    ]
''',
            "VARIANT_ORDERS",
        ),
    ],
    ids=("values", "items", "get", "order-subscript", "for-target", "comp-target"),
)
def test_closed_contract_rejects_nested_mutable_aliases(
    tmp_path: Path,
    inventory_module,
    mutation: str,
    expected_field: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(assembler, _closed_contract_source(mutation))

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert expected_field in {field for field, _reason in errors}


@pytest.mark.parametrize(
    "conditional_mutation",
    [
        '''def mutate_rules(enabled):
    rules = VARIANT_ORDERS["eleve"]
    if enabled:
        rules = []
    rules.append(("corriges", "*"))
''',
        '''def mutate_rules(enabled):
    rules = VARIANT_ORDERS["eleve"]
    if enabled:
        rules = []
    else:
        pass
    rules.append(("corriges", "*"))
''',
        '''def mutate_rules(enabled, finalize):
    rules = VARIANT_ORDERS["eleve"]
    try:
        if enabled:
            rules = []
    except RuntimeError:
        rules = []
    finally:
        if finalize:
            rules = []
    rules.append(("corriges", "*"))
''',
        '''def mutate_rules(values):
    rules = VARIANT_ORDERS["eleve"]
    for _value in values:
        rules = []
    rules.append(("corriges", "*"))
''',
        '''def mutate_rules(enabled):
    rules = VARIANT_ORDERS["eleve"]
    while enabled:
        rules = []
        enabled = False
    rules.append(("corriges", "*"))
''',
    ],
    ids=("if", "if-else", "try-except-finally", "for", "while"),
)
def test_closed_contract_keeps_aliases_possible_on_control_flow_paths(
    tmp_path: Path,
    inventory_module,
    conditional_mutation: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(assembler, _closed_contract_source(conditional_mutation))

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "VARIANT_ORDERS" in {field for field, _reason in errors}


@pytest.mark.parametrize(
    "safe_rebinding",
    [
        '''def rebind_rules(enabled):
    rules = VARIANT_ORDERS["eleve"]
    if enabled:
        rules = []
    else:
        rules = []
    rules.append(("local", "*"))
''',
        '''def rebind_rules():
    rules = VARIANT_ORDERS["eleve"]
    try:
        rules = []
    except RuntimeError:
        rules = []
    rules.append(("local", "*"))
''',
        '''def rebind_rules():
    rules = VARIANT_ORDERS["eleve"]
    try:
        action()
    finally:
        rules = []
    rules.append(("local", "*"))
''',
    ],
    ids=("if-else", "try-except", "finally"),
)
def test_closed_contract_allows_aliases_cleared_on_all_paths(
    tmp_path: Path,
    inventory_module,
    safe_rebinding: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(assembler, _closed_contract_source(safe_rebinding))

    analysis = inventory_module.analyze_assembler(assembler)

    assert inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    ) == []


def test_closed_contract_nonlocal_rebinding_clears_owner_alias(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''def outer():
    rules = VARIANT_ORDERS["eleve"]

    def rebind_rules():
        nonlocal rules
        rules = []
        rules.append(("local", "*"))
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    ) == []


def test_closed_contract_nonlocal_conditional_rebinding_keeps_owner_alias(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''def outer():
    rules = VARIANT_ORDERS["eleve"]

    def mutate_rules(enabled):
        nonlocal rules
        if enabled:
            rules = []
        rules.append(("corriges", "*"))
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "VARIANT_ORDERS" in {field for field, _reason in errors}


def test_closed_contract_nested_nonlocal_reset_does_not_clear_uncalled_owner_alias(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''def outer():
    rules = VARIANT_ORDERS["eleve"]

    def reset_rules():
        nonlocal rules
        rules = []

    rules.append(("corriges", "*"))
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "VARIANT_ORDERS" in {field for field, _reason in errors}


def test_closed_contract_exception_handler_sees_alias_from_try_prefix(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''def mutate_rules():
    rules = []
    try:
        rules = VARIANT_ORDERS["eleve"]
        raise RuntimeError
    except RuntimeError:
        rules.append(("corriges", "*"))
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "VARIANT_ORDERS" in {field for field, _reason in errors}


def test_closed_contract_allows_read_only_variant_order_accessor(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''def select_rules(variant):
    rules = VARIANT_ORDERS.get(variant, ())
    return [(directory, pattern) for directory, pattern in rules]
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    ) == []


@pytest.mark.parametrize(
    "mutation",
    [
        '''def mutate_rules():
    VARIANT_ORDERS.get("eleve", []).append(("corriges", "*"))
''',
        '''def mutate_rules():
    VARIANT_ORDERS.get("eleve", [])[0] = ("corriges", "*")
''',
    ],
    ids=("method", "subscript"),
)
def test_closed_contract_rejects_direct_accessor_result_mutation(
    tmp_path: Path,
    inventory_module,
    mutation: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(assembler, _closed_contract_source(mutation))

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "VARIANT_ORDERS" in {field for field, _reason in errors}


def test_closed_contract_rejects_nonlocal_alias_introduction(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''def outer():
    rules = []

    def select_rules():
        nonlocal rules
        rules = VARIANT_ORDERS["eleve"]

    select_rules()
    rules.append(("corriges", "*"))
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "VARIANT_ORDERS" in {field for field, _reason in errors}


@pytest.mark.parametrize(
    "escape",
    [
        "def expose(variant):\n    return VARIANT_ORDERS[variant]\n",
        "def mutate(variant):\n    consume(VARIANT_ORDERS[variant])\n",
    ],
    ids=("return", "argument"),
)
def test_closed_contract_rejects_indexed_mutable_value_escapes(
    tmp_path: Path,
    inventory_module,
    escape: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(assembler, _closed_contract_source(escape))

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert "VARIANT_ORDERS" in {field for field, _reason in errors}


@pytest.mark.parametrize(
    "function_source",
    [
        '''def annotated(
    value: mutate(ELEVE_ALLOWED_TYPES),
):
    pass
''',
        '''def annotated(value) -> mutate(VARIANT_ORDERS):
    pass
''',
    ],
    ids=("argument-annotation", "return-annotation"),
)
def test_closed_contract_rejects_mutations_in_function_annotations(
    tmp_path: Path,
    inventory_module,
    function_source: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(assembler, _closed_contract_source(function_source))

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert {field for field, _reason in errors} & {
        "ELEVE_ALLOWED_TYPES",
        "VARIANT_ORDERS",
    }


@pytest.mark.parametrize(
    "class_body",
    [
        '''    for ELEVE_ALLOWED_TYPES in local_lists:
        ELEVE_ALLOWED_TYPES.append("corrige")
''',
        '''    with local_context() as ELEVE_ALLOWED_TYPES:
        ELEVE_ALLOWED_TYPES.append("corrige")
''',
        '''    try:
        action()
    except RuntimeError as ELEVE_ALLOWED_TYPES:
        ELEVE_ALLOWED_TYPES.append("corrige")
''',
    ],
    ids=("for", "with", "except"),
)
def test_closed_contract_allows_active_class_block_bindings(
    tmp_path: Path,
    inventory_module,
    class_body: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source("class LocalContract:\n" + class_body),
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    ) == []


def test_closed_contract_allows_async_local_block_bindings(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''async def consume_locals(local_lists, local_context):
    async for ELEVE_ALLOWED_TYPES in local_lists:
        ELEVE_ALLOWED_TYPES.append("corrige")
    async with local_context() as VARIANT_ORDERS:
        VARIANT_ORDERS.update({"local": []})
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    ) == []


@pytest.mark.parametrize(
    "comprehension",
    [
        "[VARIANT_ORDERS for VARIANT_ORDERS in values]",
        "{ELEVE_ALLOWED_TYPES for ELEVE_ALLOWED_TYPES in values}",
        "{VARIANT_ORDERS: item for VARIANT_ORDERS, item in values}",
        "(ELEVE_ALLOWED_TYPES for ELEVE_ALLOWED_TYPES in values)",
    ],
    ids=("list", "set", "dict", "generator"),
)
def test_closed_contract_allows_local_comprehension_targets(
    tmp_path: Path,
    inventory_module,
    comprehension: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            "def collect(values):\n"
            f"    result = {comprehension}\n"
            "    return result\n"
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    ) == []


@pytest.mark.parametrize(
    ("comprehension", "expected_field"),
    [
        ("[VARIANT_ORDERS for item in values]", "VARIANT_ORDERS"),
        (
            "{helper(values=ELEVE_ALLOWED_TYPES) for item in values}",
            "ELEVE_ALLOWED_TYPES",
        ),
        (
            "{item: VARIANT_ORDERS for item in values}",
            "VARIANT_ORDERS",
        ),
        (
            "(mutate(ELEVE_ALLOWED_TYPES) for item in values)",
            "ELEVE_ALLOWED_TYPES",
        ),
    ],
    ids=("list", "set", "dict", "generator"),
)
def test_closed_contract_rejects_global_escapes_in_comprehensions(
    tmp_path: Path,
    inventory_module,
    comprehension: str,
    expected_field: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            "def collect(values):\n"
            f"    result = {comprehension}\n"
            "    return result\n"
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)
    errors = inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    )

    assert expected_field in {field for field, _reason in errors}


def test_closed_contract_allows_indexed_variant_order_reads(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''def select_directories(variant):
    rules = VARIANT_ORDERS[variant]
    selected = []
    for directory, pattern in rules:
        if pattern == "*":
            selected.append(directory)
    first_directory = rules[0][0]
    has_rules = rules != []
    return selected, first_directory, has_rules
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    ) == []


def test_closed_contract_allows_indexed_order_reads(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        _closed_contract_source(
            '''def select_rule():
    rule = ORDER[0]
    selected = []
    for part in rule:
        selected.append(part)
    directory = rule[0]
    return selected, directory
'''
        ),
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert inventory_module._assembly_core.validate_analysis(
        "NSI/scripts/assemble_manuel.py",
        analysis,
    ) == []


def test_legacy_manual_assembler_remains_valid_without_closed_variant_contract(
    inventory_module,
) -> None:
    path = ROOT / "Mathematiques/manuel-maths/scripts/assemble_manuel.py"

    analysis = inventory_module.analyze_assembler(path)

    assert "VARIANT_ORDERS" not in analysis["constants"]
    assert "ELEVE_VARIANTS" not in analysis["constants"]
    assert inventory_module._assembly_core.validate_analysis(
        "Mathematiques/manuel-maths/scripts/assemble_manuel.py",
        analysis,
    ) == []


def test_professor_only_manual_assembler_does_not_require_student_filter(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        '''CHAPITRES = ["1SPE-TEST"]
ORDER = [("cours", "1*")]
VARIANTS = ["professeur"]
''',
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert inventory_module._assembly_core.validate_analysis(
        "Mathematiques/manuel-maths/scripts/assemble_manuel.py",
        analysis,
    ) == []


@pytest.mark.parametrize(
    ("variant_declaration", "student_filter_declaration"),
    [
        ('VARIANTS = ["professeur", "eleve"]\n', ""),
        (
            'parser.add_argument("--variant", choices=["professeur", "eleve"])\n',
            "ELEVE_ALLOWED_TYPES = []\n",
        ),
        (
            'VARIANTS = ["eleve"]\n',
            "ELEVE_ALLOWED_TYPES = build_student_filter()\n",
        ),
        (
            'parser.add_argument("--variant", choices=["eleve"])\n',
            'ELEVE_ALLOWED_TYPES = ["cours", 3]\n',
        ),
    ],
    ids=("missing", "empty-via-argparse", "dynamic", "malformed-via-argparse"),
)
def test_student_manual_assembler_requires_a_literal_non_empty_filter(
    tmp_path: Path,
    inventory_module,
    variant_declaration: str,
    student_filter_declaration: str,
) -> None:
    assembler = tmp_path / "assemble_manuel.py"
    _write(
        assembler,
        'CHAPITRES = ["1SPE-TEST"]\n'
        'ORDER = [("cours", "1*")]\n'
        + variant_declaration
        + student_filter_declaration,
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert inventory_module._assembly_core.validate_analysis(
        "Mathematiques/manuel-maths/scripts/assemble_manuel.py",
        analysis,
    ) == [
        (
            "ELEVE_ALLOWED_TYPES",
            "filtre metadata eleve absent ou invalide",
        )
    ]


def test_manual_student_assembly_filters_teacher_objects_by_metadata(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    assembler = "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        f"{base}/cours/10_cours.tex": _meta(
            id="1SPE-TEST-COURS-C1", type_objet="cours", status="approved"
        ),
        f"{base}/exercices/1SPE-TEST-EX-001.tex": _meta(
            id="1SPE-TEST-EX-001", type_objet="exercice", status="approved"
        ),
        f"{base}/corriges/1SPE-TEST-CO-001.tex": _meta(
            id="1SPE-TEST-CO-001",
            type_objet="corrige",
            exercice_id="1SPE-TEST-EX-001",
            status="approved",
        ),
        f"{base}/evaluations/1SPE-TEST-EV-A.tex": _meta(
            id="1SPE-TEST-EV-A", type_objet="evaluation", status="approved"
        ),
        f"{base}/evaluations/1SPE-TEST-EV-A-corrige.tex": _meta(
            id="1SPE-TEST-EV-A-corrige",
            type_objet="corrige_evaluation",
            status="approved",
        ),
        assembler: """CHAPITRES = ["1SPE-TEST"]
ORDER = [("cours", "1*"), ("exercices", "*"), ("evaluations", "*"), ("corriges", "*")]
VARIANTS = ["professeur", "eleve"]
ELEVE_EXCLUDES = {"corriges"}
ELEVE_ALLOWED_TYPES = {"cours", "evaluation", "exercice"}
""",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    assemblies = {item["assembly_id"]: item for item in inventory["assemblies"]}
    professor = assemblies["math:manual:1SPE:professeur"]
    student = assemblies["math:manual:1SPE:eleve"]

    assert professor["included_objects"] == [
        f"{base}/cours/10_cours.tex",
        f"{base}/exercices/1SPE-TEST-EX-001.tex",
        f"{base}/evaluations/1SPE-TEST-EV-A-corrige.tex",
        f"{base}/evaluations/1SPE-TEST-EV-A.tex",
        f"{base}/corriges/1SPE-TEST-CO-001.tex",
    ]
    assert student["included_objects"] == [
        f"{base}/cours/10_cours.tex",
        f"{base}/exercices/1SPE-TEST-EX-001.tex",
        f"{base}/evaluations/1SPE-TEST-EV-A.tex",
    ]


def test_declared_variant_orders_drive_specialized_manual_selection(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    assembler = "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
    student_objects = {
        "eleve": f"{base}/cours/10_cours.tex",
        "methodes": f"{base}/methodes/10_methode.tex",
        "remediation": f"{base}/remediation/10_remediation.tex",
        "amenagee": f"{base}/amenagee/10_amenagee.tex",
        "projets": f"{base}/projet/10_projet.tex",
    }
    teacher_objects = {
        variant: str(PurePosixPath(path).with_name(f"99_{variant}_prof.tex"))
        for variant, path in student_objects.items()
    }
    evaluation = f"{base}/evaluations/10_evaluation.tex"
    evaluation_correction = f"{base}/evaluations/20_corrige.tex"
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        student_objects["eleve"]: _meta(
            id="1SPE-TEST-COURS-C1", type_objet="cours", status="approved"
        ),
        student_objects["methodes"]: _meta(
            id="1SPE-TEST-METHODE-C1", type_objet="methode", status="approved"
        ),
        student_objects["remediation"]: _meta(
            id="1SPE-TEST-REMEDIATION-C1",
            type_objet="remediation",
            status="approved",
        ),
        student_objects["amenagee"]: _meta(
            id="1SPE-TEST-AMENAGEE-C1", type_objet="exercice", status="approved"
        ),
        student_objects["projets"]: _meta(
            id="1SPE-TEST-PROJET-C1", type_objet="projet", status="approved"
        ),
        evaluation: _meta(
            id="1SPE-TEST-EVALUATION-C1",
            type_objet="evaluation",
            status="approved",
        ),
        evaluation_correction: _meta(
            id="1SPE-TEST-EVALUATION-CORRIGE-C1",
            type_objet="corrige_evaluation",
            status="approved",
        ),
        assembler: '''CHAPITRES = ["1SPE-TEST"]
ORDER = [("cours", "*")]
VARIANTS = ["eleve", "professeur", "methodes", "remediation", "amenagee", "evaluations", "projets"]
VARIANT_ORDERS = {
    "eleve": [("cours", "*")],
    "professeur": [("cours", "*"), ("methodes", "*"), ("remediation", "*"), ("amenagee", "*"), ("evaluations", "*"), ("projet", "*")],
    "methodes": [("methodes", "*")],
    "remediation": [("remediation", "*")],
    "amenagee": [("amenagee", "*")],
    "evaluations": [("evaluations", "*")],
    "projets": [("projet", "*")],
}
ELEVE_VARIANTS = ["eleve", "methodes", "remediation", "amenagee", "projets"]
ELEVE_ALLOWED_TYPES = ["cours", "methode", "remediation", "exercice", "projet"]
''',
    }
    for index, (variant, path) in enumerate(teacher_objects.items(), start=1):
        sources[path] = _meta(
            id=f"1SPE-TEST-{variant.upper()}-PROF-{index}",
            type_objet="corrige_evaluation",
            status="approved",
        )
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    assemblies = {item["assembly_id"]: item for item in inventory["assemblies"]}

    for variant, expected_path in student_objects.items():
        assembly = assemblies[f"math:manual:1SPE:{variant}"]
        assert assembly["included_objects"] == [expected_path]
        assert teacher_objects[variant] not in assembly["included_objects"]
    assert assemblies["math:manual:1SPE:evaluations"]["included_objects"] == [
        evaluation,
        evaluation_correction,
    ]
    assert set(assemblies["math:manual:1SPE:professeur"]["included_objects"]) == {
        *student_objects.values(),
        *teacher_objects.values(),
        evaluation,
        evaluation_correction,
    }


def test_assemblies_follow_ast_globs_and_expose_duplicates_exclusions_and_orphans(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    chapter_assembler = "Mathematiques/manuel-maths/scripts/assemble.py"
    manual_assembler = "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        f"{base}/cours/10_cours.tex": _meta(id="1SPE-TEST-COURS-C1", status="approved"),
        f"{base}/exercices/1SPE-TEST-EX-001.tex": _meta(
            id="1SPE-TEST-EX-001", type_objet="exercice", status="approved"
        ),
        f"{base}/corriges/1SPE-TEST-CO-001.tex": _meta(
            id="1SPE-TEST-CO-001",
            type_objet="corrige",
            exercice_id="1SPE-TEST-EX-001",
            status="approved",
        ),
        chapter_assembler: """ORDER = [("cours", "*"), ("cours", "1*"), ("exercices", "*")]
VARIANTS = ["complet"]
""",
        manual_assembler: """CHAPITRES = ["1SPE-TEST"]
ORDER = [("cours", "1*"), ("exercices", "*")]
VARIANTS = ["professeur", "eleve"]
ELEVE_EXCLUDES = {"evaluations", "corriges"}
ELEVE_ALLOWED_TYPES = {"cours", "exercice"}
""",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    assemblies = {item["assembly_id"]: item for item in inventory["assemblies"]}
    chapter = assemblies["math:chapter:1SPE-TEST:complet"]
    professor = assemblies["math:manual:1SPE:professeur"]

    assert chapter["included_objects"] == [
        f"{base}/cours/10_cours.tex",
        f"{base}/exercices/1SPE-TEST-EX-001.tex",
    ]
    assert chapter["excluded_source_types"] == ["corrige"]
    assert professor["chapters"] == ["1SPE-TEST"]
    assert inventory["anomalies"]["duplicate_assembly_objects"] == [
        {
            "champ": "math:chapter:1SPE-TEST:complet",
            "cible": f"{base}/cours/10_cours.tex",
            "raison": "2 regles de glob selectionnent le meme objet; l'assembleur le deduplique",
            "source": chapter_assembler,
        }
    ]
    assert inventory["anomalies"]["unassembled_objects"] == [
        {
            "champ": "assemblages_declares",
            "cible": f"{base}/corriges/1SPE-TEST-CO-001.tex",
            "raison": "objet META exclu de tous les assemblages declares",
            "source": f"{base}/corriges/1SPE-TEST-CO-001.tex",
        }
    ]
    manual_model = inventory["manuals"]["1SPE"]
    chapter_model = manual_model["chapters"]["1SPE-TEST"]
    assert manual_model["declared_variants"] == {
        "chapter": ["complet"],
        "manual": ["eleve", "professeur"],
        "static": [],
    }
    assert chapter_model["declared_variants"] == manual_model["declared_variants"]


def test_manual_assembler_gaps_and_chapters_outside_manual_are_explicit(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapters = (
        ("TSPE", "TSPE-TEST", "TSPE"),
        ("1NSI", "1NSI-TEST", "1NSI"),
        ("TNSI", "TNSI-TEST", "TNSI"),
    )
    sources: dict[str, str] = {}
    for manual, chapter, level in chapters:
        base = _chapter_path(manual, chapter)
        sources[f"{base}/contrat.yaml"] = _contract(chapter, level, capacities=1)
        sources[f"{base}/cours/10_cours.tex"] = _meta(
            id=f"{chapter}-COURS-C1",
            chapitre=chapter,
            status="approved",
        )
    sources["Mathematiques/manuel-maths/scripts/assemble.py"] = (
        'ORDER = [("cours", "1*")]\nVARIANTS = ["complet"]\n'
    )
    sources["NSI/scripts/assemble.py"] = (
        'ORDER = [("cours", "1*")]\nVARIANTS = ["complet"]\n'
    )
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    gaps = inventory["anomalies"]["missing_assemblers"]

    assert {
        (item["cible"], item["champ"], item["raison"])
        for item in gaps
        if item["champ"] == "manuel"
    } == {
        ("1NSI", "manuel", "aucun assembleur de manuel suivi"),
        ("1SPE", "manuel", "aucun assembleur de manuel suivi"),
        ("TCOMPL", "manuel", "aucun assembleur de manuel suivi"),
        ("TEXPERTES", "manuel", "aucun assembleur de manuel suivi"),
        ("TNSI", "manuel", "aucun assembleur de manuel suivi"),
        ("TSPE_2026_2027", "manuel", "aucun assembleur de manuel suivi"),
    }
    assert {
        item["cible"] for item in inventory["anomalies"]["chapters_not_in_manual"]
    } == {"1NSI-TEST", "TNSI-TEST", "TSPE-TEST"}


def test_nsi_manual_assembler_cannot_cover_tnsi_chapters(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    assembler = "NSI/scripts/assemble_manuel.py"
    sources = {
        "NSI/chapitres/1NSI-TEST/contrat.yaml": _contract(
            "1NSI-TEST", "1NSI", capacities=1
        ),
        "NSI/chapitres/1NSI-TEST/cours/10_cours.tex": _meta(
            id="1NSI-TEST-COURS-C1",
            chapitre="1NSI-TEST",
            status="approved",
        ),
        "NSI/chapitres/TNSI-TEST/contrat.yaml": _contract(
            "TNSI-TEST", "TNSI", capacities=1
        ),
        "NSI/chapitres/TNSI-TEST/cours/10_cours.tex": _meta(
            id="TNSI-TEST-COURS-C1",
            chapitre="TNSI-TEST",
            status="approved",
        ),
        assembler: '''CHAPITRES = ["1NSI-TEST", "TNSI-TEST"]
ORDER = [("cours", "*")]
VARIANTS = ["eleve"]
VARIANT_ORDERS = {"eleve": [("cours", "*")]}
ELEVE_VARIANTS = ["eleve"]
ELEVE_ALLOWED_TYPES = ["cours"]
''',
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    manual_assemblies = {
        assembly["assembly_id"]: assembly
        for assembly in inventory["assemblies"]
        if assembly["scope"] == "manual"
    }

    assert "nsi:manual:1NSI:eleve" in manual_assemblies
    assert "nsi:manual:TNSI:eleve" not in manual_assemblies
    assert any(
        anomaly["source"] == assembler
        and anomaly["cible"] == "TNSI-TEST"
        and anomaly["champ"] == "CHAPITRES[1]"
        and "perimetre" in anomaly["raison"]
        for anomaly in inventory["anomalies"]["broken_assembly_references"]
    )
    assert any(
        anomaly["cible"] == "TNSI-TEST"
        for anomaly in inventory["anomalies"]["chapters_not_in_manual"]
    )


def test_supported_manuals_distinguish_nsi_chapter_and_manual_assemblers(
    inventory_module,
) -> None:
    supported = inventory_module._supported_manuals_for_assembler

    assert supported("NSI/scripts/assemble_manuel.py") == ("1NSI",)
    assert supported("NSI/scripts/assemble.py") == ("1NSI", "TNSI")
    assert supported("Mathematiques/manuel-maths/scripts/assemble_manuel.py") == (
        "1SPE",
        "TSPE_2026_2027",
        "TCOMPL",
        "TEXPERTES",
    )


def test_live_1nsi_runtime_selection_matches_declared_manual_assemblies(
    inventory_module, monkeypatch: pytest.MonkeyPatch
) -> None:
    assembler_path = ROOT / "NSI/scripts/assemble_manuel.py"
    assert assembler_path.is_file(), "assemble_manuel.py doit etre cree"
    spec = importlib.util.spec_from_file_location("assemble_manuel_live", assembler_path)
    assert spec is not None and spec.loader is not None
    scripts_path = str(ROOT / "NSI/scripts")
    monkeypatch.syspath_prepend(scripts_path)
    runtime = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, runtime)
    spec.loader.exec_module(runtime)

    tracked = set(inventory_module.git_tracked_files(ROOT))
    tracked.add("NSI/scripts/assemble_manuel.py")
    monkeypatch.setattr(
        inventory_module,
        "git_tracked_files",
        lambda _repository: tuple(sorted(tracked)),
    )
    monkeypatch.setattr(
        inventory_module,
        "_load_observed_build_manifest",
        lambda *_args, **_kwargs: [],
    )
    inventory = inventory_module.build_inventory(ROOT)
    assemblies = {
        assembly["variant"]: assembly
        for assembly in inventory["assemblies"]
        if assembly["manual"] == "1NSI" and assembly["scope"] == "manual"
    }

    assert set(assemblies) == set(runtime.VARIANTS)
    for variant in runtime.VARIANTS:
        runtime_paths = [
            path.relative_to(ROOT).as_posix()
            for path in runtime.collect_variant_objects(variant)
        ]
        assert assemblies[variant]["included_objects"] == runtime_paths


def test_live_1nsi_manual_declaration_closes_assembly_debt_without_tnsi(
    inventory_module, monkeypatch: pytest.MonkeyPatch
) -> None:
    assembler = "NSI/scripts/assemble_manuel.py"
    assert (ROOT / assembler).is_file(), "assemble_manuel.py doit etre cree"
    tracked = set(inventory_module.git_tracked_files(ROOT))
    tracked.add(assembler)
    monkeypatch.setattr(
        inventory_module,
        "git_tracked_files",
        lambda _repository: tuple(sorted(tracked)),
    )
    monkeypatch.setattr(
        inventory_module,
        "_load_observed_build_manifest",
        lambda *_args, **_kwargs: [],
    )

    inventory = inventory_module.build_inventory(ROOT)
    nsi_manual_assemblies = [
        assembly
        for assembly in inventory["assemblies"]
        if assembly["scope"] == "manual" and assembly["manual"] == "1NSI"
    ]
    tnsi_manual_assemblies = [
        assembly
        for assembly in inventory["assemblies"]
        if assembly["scope"] == "manual" and assembly["manual"] == "TNSI"
    ]
    tnsi_chapter_variants = {
        assembly["variant"]
        for assembly in inventory["assemblies"]
        if assembly["scope"] == "chapter" and assembly["manual"] == "TNSI"
    }

    assert len(nsi_manual_assemblies) == 7
    assert {
        chapter
        for assembly in nsi_manual_assemblies
        for chapter in assembly["chapters"]
    } == set(inventory["manuals"]["1NSI"]["chapters"])
    assert not [
        anomaly
        for anomaly in inventory["anomalies"]["chapters_not_in_manual"]
        if anomaly["cible"].startswith("1NSI-")
    ]
    assert not [
        anomaly
        for anomaly in inventory["anomalies"]["unassembled_objects"]
        if anomaly["cible"].startswith("NSI/chapitres/1NSI-")
    ]
    assert tnsi_manual_assemblies == []
    assert tnsi_chapter_variants == {
        "amenagee",
        "complet",
        "methodes",
        "parcours1",
        "professeur",
        "remediation",
    }
    assert not (ROOT / "NSI/manifests/books/TNSI.json").exists()


def test_pdf_inventory_uses_only_tracked_files_and_reports_unavailable_page_count(
    tmp_path: Path, inventory_module, monkeypatch: pytest.MonkeyPatch
) -> None:
    _init_repository(tmp_path)
    tracked_pdf = "Mathematiques/manuel-maths/build/tracked.pdf"
    untracked_pdf = "NSI/build/untracked.pdf"
    _write(tmp_path / tracked_pdf, "pas un vrai pdf")
    _write(tmp_path / untracked_pdf, "pas un vrai pdf")
    _track(tmp_path, tracked_pdf)
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_pdfinfo",
        lambda _path: (None, "pdfinfo indisponible"),
    )
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_python",
        lambda _path: (None, "lecteur PDF Python indisponible"),
    )

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["pdfs"] == [
        {
            "chapter": None,
            "manual": None,
            "page_count": None,
            "page_count_method": None,
            "path": tracked_pdf,
            "reason": ("pdfinfo indisponible; lecteur PDF Python indisponible"),
            "scope": None,
            "source_role": "generated_dependency",
            "status": "page_count_unavailable",
            "variant": None,
        }
    ]
    assert inventory["anomalies"]["unattributed_pdfs"] == [
        {
            "champ": "attribution",
            "cible": tracked_pdf,
            "raison": "PDF suivi sans attribution fiable a un livrable",
            "source": tracked_pdf,
        }
    ]


def test_pdf_inventory_prefers_pdfinfo_page_count(
    tmp_path: Path, inventory_module, monkeypatch: pytest.MonkeyPatch
) -> None:
    _init_repository(tmp_path)
    tracked_pdf = "NSI/build/MANUEL_1NSI_eleve.pdf"
    _write(tmp_path / tracked_pdf, "contenu simule")
    _track(tmp_path, tracked_pdf)
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_pdfinfo",
        lambda _path: (27, None),
    )

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["pdfs"] == [
        {
            "chapter": None,
            "manual": "1NSI",
            "page_count": 27,
            "page_count_method": "pdfinfo",
            "path": tracked_pdf,
            "reason": None,
            "scope": "manual",
            "source_role": "generated_dependency",
            "status": "counted",
            "variant": "eleve",
        }
    ]
    assert inventory["manuals"]["1NSI"]["compiled_artifacts"] == inventory["pdfs"]
    assert inventory["manuals"]["1NSI"]["compiled_variants"]["manual"] == ["eleve"]
    assert inventory["observed_builds"] == []


@pytest.mark.parametrize(
    "page_count",
    [
        pytest.param(0, id="zero"),
        pytest.param(True, id="bool"),
    ],
)
def test_generated_pdf_with_invalid_count_is_not_compiled_evidence(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    page_count: int | bool,
) -> None:
    _init_repository(tmp_path)
    pdf = "NSI/build/MANUEL_1NSI_eleve.pdf"
    _write(tmp_path / pdf, "contenu simule")
    _track(tmp_path, pdf)
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_pdfinfo",
        lambda _path: (page_count, None),
    )

    inventory = inventory_module.build_inventory(tmp_path)
    artifact = inventory["pdfs"][0]
    manual = inventory["manuals"]["1NSI"]

    assert artifact["path"] == pdf
    assert artifact["status"] == "counted"
    assert artifact["page_count"] is page_count or artifact["page_count"] == page_count
    assert manual["compiled_artifacts"] == []
    assert manual["compiled_variants"]["manual"] == []
    assert inventory["coherence_checks"]["artifact_cardinality"] == {
        "ok": True,
        "violations": [],
    }


def test_unreadable_generated_pdf_is_not_compiled_evidence(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_repository(tmp_path)
    pdf = "NSI/build/MANUEL_1NSI_eleve.pdf"
    _write(tmp_path / pdf, "contenu invalide")
    _track(tmp_path, pdf)
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_pdfinfo",
        lambda _path: (None, "pdfinfo invalide"),
    )
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_python",
        lambda _path: (None, "lecteur Python invalide"),
    )

    inventory = inventory_module.build_inventory(tmp_path)
    artifact = inventory["pdfs"][0]
    manual = inventory["manuals"]["1NSI"]

    assert artifact["path"] == pdf
    assert artifact["status"] == "page_count_unavailable"
    assert artifact["page_count"] is None
    assert manual["compiled_artifacts"] == []
    assert manual["compiled_variants"]["manual"] == []
    assert inventory["coherence_checks"]["artifact_cardinality"] == {
        "ok": True,
        "violations": [],
    }


def test_missing_generated_pdf_is_not_compiled_evidence(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    pdf = "NSI/build/MANUEL_1NSI_eleve.pdf"
    _write(tmp_path / pdf, "contenu indexe puis supprime")
    _track(tmp_path, pdf)
    (tmp_path / pdf).unlink()

    inventory = inventory_module.build_inventory(tmp_path)
    artifact = inventory["pdfs"][0]
    manual = inventory["manuals"]["1NSI"]

    assert artifact["path"] == pdf
    assert artifact["status"] == "page_count_unavailable"
    assert artifact["page_count"] is None
    assert manual["compiled_artifacts"] == []
    assert manual["compiled_variants"]["manual"] == []
    assert inventory["coherence_checks"]["artifact_cardinality"] == {
        "ok": True,
        "violations": [],
    }


def test_missing_tracked_pdf_has_deterministic_checkout_status(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    tracked_pdf = "NSI/build/deleted.pdf"
    _write(tmp_path / tracked_pdf, "contenu indexe puis supprime")
    _track(tmp_path, tracked_pdf)
    (tmp_path / tracked_pdf).unlink()

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["pdfs"] == [
        {
            "chapter": None,
            "manual": None,
            "page_count": None,
            "page_count_method": None,
            "path": tracked_pdf,
            "reason": "fichier PDF suivi absent du checkout",
            "scope": None,
            "source_role": "generated_dependency",
            "status": "page_count_unavailable",
            "variant": None,
        }
    ]


@pytest.mark.parametrize(
    "link_kind",
    [
        pytest.param("absolute-external", id="absolute-external"),
        pytest.param("relative-external", id="relative-external"),
        pytest.param("relative-internal", id="relative-internal"),
        pytest.param("broken", id="broken"),
    ],
)
def test_tracked_pdf_symlink_is_not_read_or_counted(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    link_kind: str,
) -> None:
    _init_repository(tmp_path)
    pdf = "NSI/build/MANUEL_1NSI_eleve.pdf"
    link = tmp_path / pdf
    link.parent.mkdir(parents=True)
    if link_kind in {"absolute-external", "relative-external"}:
        target = tmp_path.parent / f"{tmp_path.name}-{link_kind}.pdf"
        _write(target, "contenu PDF externe simule")
        link_target = (
            str(target)
            if link_kind == "absolute-external"
            else os.path.relpath(target, link.parent)
        )
    elif link_kind == "relative-internal":
        target = tmp_path / "evidence/real.pdf"
        _write(target, "contenu PDF interne simule")
        link_target = os.path.relpath(target, link.parent)
    else:
        target = tmp_path / "missing.pdf"
        link_target = os.path.relpath(target, link.parent)
    link.symlink_to(link_target)
    _track(tmp_path, pdf)
    counter_calls: list[Path] = []

    def unexpected_counter(path: Path) -> tuple[int | None, str | None]:
        counter_calls.append(path)
        return 9, None

    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_pdfinfo",
        unexpected_counter,
    )
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_python",
        unexpected_counter,
    )

    inventory = inventory_module.build_inventory(tmp_path)
    artifact = inventory["pdfs"][0]

    assert link.is_symlink()
    assert counter_calls == []
    assert artifact == {
        "chapter": None,
        "manual": "1NSI",
        "page_count": None,
        "page_count_method": None,
        "path": pdf,
        "reason": "fichier PDF suivi non régulier: lien symbolique interdit",
        "scope": "manual",
        "source_role": "generated_dependency",
        "status": "page_count_unavailable",
        "variant": "eleve",
    }
    assert inventory["manuals"]["1NSI"]["compiled_artifacts"] == []
    assert inventory["manuals"]["1NSI"]["compiled_variants"]["manual"] == []
    assert inventory["coherence_checks"]["artifact_cardinality"] == {
        "ok": True,
        "violations": [],
    }
    assert inventory["observed_builds"] == []


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFO indisponible")
def test_nonregular_tracked_pdf_is_not_read_or_counted(
    tmp_path: Path,
    inventory_module,
) -> None:
    pdf = "NSI/build/MANUEL_1NSI_eleve.pdf"
    fifo = tmp_path / pdf
    fifo.parent.mkdir(parents=True)
    os.mkfifo(fifo)
    counter_calls: list[Path] = []

    def unexpected_counter(path: Path) -> tuple[int | None, str | None]:
        counter_calls.append(path)
        return 9, None

    inventory = {
        "anomalies": {"unattributed_pdfs": []},
        "manuals": {"1NSI": {"chapters": {}}},
    }
    artifacts = inventory_module._pdf_core.inventory_pdfs(
        tmp_path,
        (pdf,),
        inventory,
        source_roles={pdf: "generated_dependency"},
        pdfinfo_counter=unexpected_counter,
        python_counter=unexpected_counter,
    )

    assert counter_calls == []
    assert artifacts == [
        {
            "chapter": None,
            "manual": "1NSI",
            "page_count": None,
            "page_count_method": None,
            "path": pdf,
            "reason": "fichier PDF suivi non régulier: type de fichier interdit",
            "scope": "manual",
            "source_role": "generated_dependency",
            "status": "page_count_unavailable",
            "variant": "eleve",
        }
    ]


@pytest.mark.parametrize(
    "mutation",
    [
        pytest.param("leaf-new-inode", id="leaf-new-inode"),
        pytest.param("leaf-switch-back", id="leaf-switch-back"),
        pytest.param("parent-switch-back", id="parent-switch-back"),
        pytest.param("in-place", id="in-place"),
    ],
)
def test_pdf_mutation_during_counting_invalidates_private_snapshot_evidence(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    _init_repository(tmp_path)
    pdf = "NSI/build/MANUEL_1NSI_eleve.pdf"
    repository_pdf = tmp_path / pdf
    invalid_blob = b"invalid PDF bytes at secure open"
    _write(repository_pdf, invalid_blob.decode("ascii"))
    _track(tmp_path, pdf)
    initial_inode = repository_pdf.stat().st_ino
    external_pdf = tmp_path.parent / f"{tmp_path.name}-{mutation}-external.pdf"
    external_pdf.write_bytes(b"%PDF-1.7 external valid replacement")
    snapshot_paths: list[Path] = []
    snapshot_blobs: list[bytes] = []

    def mutating_counter(snapshot: Path) -> tuple[int | None, str | None]:
        snapshot_paths.append(snapshot)
        snapshot_blobs.append(snapshot.read_bytes())
        if mutation == "leaf-new-inode":
            parked = repository_pdf.with_suffix(".old")
            repository_pdf.rename(parked)
            repository_pdf.symlink_to(external_pdf)
            assert repository_pdf.read_bytes().startswith(b"%PDF")
            repository_pdf.unlink()
            repository_pdf.write_bytes(invalid_blob)
            assert repository_pdf.stat().st_ino != initial_inode
            parked.unlink()
        elif mutation == "leaf-switch-back":
            parked = repository_pdf.with_suffix(".parked")
            repository_pdf.rename(parked)
            repository_pdf.symlink_to(external_pdf)
            assert repository_pdf.read_bytes().startswith(b"%PDF")
            repository_pdf.unlink()
            parked.rename(repository_pdf)
            assert repository_pdf.stat().st_ino == initial_inode
        elif mutation == "parent-switch-back":
            build = repository_pdf.parent
            parked = build.with_name("build-parked")
            external_build = tmp_path.parent / f"{tmp_path.name}-external-build"
            _write(
                external_build / repository_pdf.name,
                "%PDF-1.7 external parent replacement",
            )
            build.rename(parked)
            build.symlink_to(external_build, target_is_directory=True)
            assert repository_pdf.read_bytes().startswith(b"%PDF")
            build.unlink()
            parked.rename(build)
            assert repository_pdf.stat().st_ino == initial_inode
        else:
            repository_pdf.write_bytes(b"X" * len(invalid_blob))
            assert repository_pdf.stat().st_ino == initial_inode
        return 9, None

    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_pdfinfo",
        mutating_counter,
    )

    inventory = inventory_module.build_inventory(tmp_path)
    artifact = inventory["pdfs"][0]

    assert len(snapshot_paths) == 1
    assert snapshot_paths[0] != repository_pdf
    assert snapshot_blobs == [invalid_blob]
    assert not snapshot_paths[0].exists()
    assert not snapshot_paths[0].parent.exists()
    assert artifact["status"] == "page_count_unavailable"
    assert artifact["page_count"] is None
    assert artifact["page_count_method"] is None
    assert artifact["reason"] == (
        "fichier PDF modifié pendant le comptage sécurisé"
    )
    assert inventory["manuals"]["1NSI"]["compiled_artifacts"] == []
    assert inventory["manuals"]["1NSI"]["compiled_variants"]["manual"] == []
    assert inventory["coherence_checks"]["artifact_cardinality"] == {
        "ok": True,
        "violations": [],
    }
    assert inventory["observed_builds"] == []


def test_regular_pdf_is_counted_from_private_snapshot_then_snapshot_is_removed(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_repository(tmp_path)
    pdf = "NSI/build/MANUEL_1NSI_eleve.pdf"
    repository_pdf = tmp_path / pdf
    blob = b"%PDF-1.7 stable canonical bytes"
    repository_pdf.parent.mkdir(parents=True)
    repository_pdf.write_bytes(blob)
    _track(tmp_path, pdf)
    snapshots: list[Path] = []

    def snapshot_counter(snapshot: Path) -> tuple[int | None, str | None]:
        snapshots.append(snapshot)
        assert snapshot != repository_pdf
        assert snapshot.read_bytes() == blob
        assert snapshot.stat().st_mode & 0o777 == 0o600
        assert snapshot.parent.stat().st_mode & 0o777 == 0o700
        return 11, None

    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_pdfinfo",
        snapshot_counter,
    )

    inventory = inventory_module.build_inventory(tmp_path)
    artifact = inventory["pdfs"][0]

    assert artifact["status"] == "counted"
    assert artifact["page_count"] == 11
    assert artifact["page_count_method"] == "pdfinfo"
    assert inventory["manuals"]["1NSI"]["compiled_artifacts"] == [artifact]
    assert len(snapshots) == 1
    assert not snapshots[0].exists()
    assert not snapshots[0].parent.exists()
    assert repository_pdf.read_bytes() == blob


@pytest.mark.parametrize(
    ("pdf", "expected_role"),
    [
        pytest.param(
            "NSI/tests/fixtures/MANUEL_1NSI_eleve.pdf",
            "fixture",
            id="fixture",
        ),
        pytest.param(
            "Mathematiques/manuel-maths/gabarits/"
            "reference-v4/MANUEL_1NSI_eleve.pdf",
            "visual_reference",
            id="visual-reference",
        ),
        pytest.param(
            "NSI/historique/MANUEL_1NSI_eleve.pdf",
            "archive",
            id="archive",
        ),
    ],
)
def test_non_publishable_pdf_is_inventoried_without_compiled_evidence(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    pdf: str,
    expected_role: str,
) -> None:
    _init_repository(tmp_path)
    _write(tmp_path / pdf, "contenu simule")
    _track(tmp_path, pdf)
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_pdfinfo",
        lambda _path: (12, None),
    )

    inventory = inventory_module.build_inventory(tmp_path)
    artifact = inventory["pdfs"][0]
    manual = inventory["manuals"]["1NSI"]

    assert artifact["path"] == pdf
    assert artifact["manual"] == "1NSI"
    assert artifact["variant"] == "eleve"
    assert artifact["source_role"] == expected_role
    assert manual["compiled_artifacts"] == []
    assert manual["compiled_variants"] == {
        "chapter": [],
        "manual": [],
        "static": [],
    }
    assert inventory["coherence_checks"]["artifact_cardinality"] == {
        "ok": True,
        "violations": [],
    }
    assert inventory["observed_builds"] == []


@pytest.mark.parametrize(
    ("pdf", "manual_id"),
    [
        pytest.param(
            r"NSI\build/MANUEL_1NSI_eleve.pdf",
            "1NSI",
            id="literal-backslash-root",
        ),
        pytest.param(
            "evil/build/MANUEL_1NSI_eleve.pdf",
            "1NSI",
            id="untrusted-generated-root",
        ),
        pytest.param(
            "NSІ/build/MANUEL_1NSI_eleve.pdf",
            "1NSI",
            id="unicode-confusable-root",
        ),
        pytest.param(
            "Mathematiques/manuel-maths/build/MANUEL_1NSI_eleve.pdf",
            "1NSI",
            id="nsi-manual-under-math-root",
        ),
        pytest.param(
            "NSI/build/MANUEL_1SPE_eleve.pdf",
            "1SPE",
            id="math-manual-under-nsi-root",
        ),
    ],
)
def test_generated_pdf_outside_manual_project_is_not_compiled_evidence(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    pdf: str,
    manual_id: str,
) -> None:
    _init_repository(tmp_path)
    _write(tmp_path / pdf, "contenu simule")
    _track(tmp_path, pdf)
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_pdfinfo",
        lambda _path: (9, None),
    )

    inventory = inventory_module.build_inventory(tmp_path)
    artifact = inventory["pdfs"][0]
    manual = inventory["manuals"][manual_id]

    assert artifact["path"] == pdf
    assert artifact["manual"] == manual_id
    assert artifact["source_role"] == "generated_dependency"
    assert artifact["status"] == "counted"
    assert artifact["page_count"] == 9
    assert manual["compiled_artifacts"] == []
    assert manual["compiled_variants"]["manual"] == []
    assert inventory["coherence_checks"]["artifact_cardinality"] == {
        "ok": True,
        "violations": [],
    }
    assert inventory["observed_builds"] == []


@pytest.mark.parametrize(
    ("pdf", "manual_id"),
    [
        pytest.param(
            "NSI/build/MANUEL_1NSI_eleve.pdf",
            "1NSI",
            id="1nsi",
        ),
        pytest.param(
            "NSI/build/MANUEL_TNSI_eleve.pdf",
            "TNSI",
            id="tnsi",
        ),
        pytest.param(
            "Mathematiques/manuel-maths/build/MANUEL_1SPE_eleve.pdf",
            "1SPE",
            id="1spe",
        ),
        pytest.param(
            "Mathematiques/manuel-maths/build/"
            "MANUEL_TSPE_2026-2027_eleve.pdf",
            "TSPE_2026_2027",
            id="tspe",
        ),
    ],
)
def test_valid_pdf_under_canonical_manual_project_is_compiled_evidence(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    pdf: str,
    manual_id: str,
) -> None:
    _init_repository(tmp_path)
    _write(tmp_path / pdf, "contenu simule")
    _track(tmp_path, pdf)
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_pdfinfo",
        lambda _path: (9, None),
    )

    inventory = inventory_module.build_inventory(tmp_path)
    artifact = inventory["pdfs"][0]
    manual = inventory["manuals"][manual_id]

    assert artifact["path"] == pdf
    assert artifact["manual"] == manual_id
    assert artifact["source_role"] == "generated_dependency"
    assert artifact["status"] == "counted"
    assert artifact["page_count"] == 9
    assert manual["compiled_artifacts"] == [artifact]
    assert manual["compiled_variants"]["manual"] == ["eleve"]
    assert inventory["coherence_checks"]["artifact_cardinality"] == {
        "ok": True,
        "violations": [],
    }
    assert inventory["observed_builds"] == []


def test_recursive_static_latex_assembly_counts_duplicates_and_assembles_correction(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    exercise = f"{base}/exercices/1SPE-TEST-EX-001.tex"
    correction = f"{base}/corriges/1SPE-TEST-CO-001.tex"
    root_tex = "Mathematiques/manuel-maths/build/maquette-v5/maquette.tex"
    section = "Mathematiques/manuel-maths/parts/section.tex"
    template = "Mathematiques/manuel-maths/gabarits/chapitre_master.tex"
    orphan = "Mathematiques/manuel-maths/extras/perdu.tex"
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        exercise: _meta(
            id="1SPE-TEST-EX-001", type_objet="exercice", status="approved"
        ),
        correction: _meta(
            id="1SPE-TEST-CO-001",
            type_objet="corrige",
            exercice_id="1SPE-TEST-EX-001",
            status="approved",
        ),
        root_tex: """\\documentclass{article}
\\begin{document}
\\input{parts/section}
\\input{parts/section}
\\end{document}
""",
        section: """\\input{chapitres/1SPE-TEST/exercices/1SPE-TEST-EX-001}
\\input{chapitres/1SPE-TEST/corriges/1SPE-TEST-CO-001}
""",
        template: "%%CONTENT%%\n",
        orphan: "Texte non reference sans META\n",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    first = inventory_module.build_inventory(tmp_path)
    first_digest = first["source_digest"]
    assemblies = {item["assembly_id"]: item for item in first["assemblies"]}
    static_id = f"math:static:{root_tex}"

    assert assemblies[static_id]["included_objects"] == [exercise, correction]
    assert first["manuals"]["1SPE"]["declared_variants"]["static"] == ["maquette-v5"]
    assert first["manuals"]["1SPE"]["chapters"]["1SPE-TEST"]["declared_variants"][
        "static"
    ] == ["maquette-v5"]
    assert first["anomalies"]["unassembled_objects"] == []
    assert {
        (item["champ"], item["cible"])
        for item in first["anomalies"]["duplicate_assembly_objects"]
    } == {(static_id, exercise), (static_id, correction)}
    assert first["anomalies"]["orphan_files"] == [
        {
            "champ": "reachability",
            "cible": orphan,
            "raison": "fichier LaTeX suivi sans META, non reference et hors assemblage",
            "role": "latex_source",
            "source": orphan,
        }
    ]
    assert template not in {
        item["cible"] for item in first["anomalies"]["orphan_files"]
    }
    assert root_tex in first["source_files"]
    assert section in first["source_files"]

    _write(tmp_path / section, sources[section] + "% modification suivie\n")
    assert inventory_module.build_inventory(tmp_path)["source_digest"] != first_digest


def test_graph_source_role_policies_are_explicit(
    inventory_module,
) -> None:
    assert inventory_module.BLOCKING_LATEX_REFERENCE_SOURCE_ROLES == frozenset(
        {"generated_dependency", "production_object", "transversal"}
    )
    assert inventory_module.ORPHAN_SOURCE_ROLES == frozenset(
        {"production_object", "transversal"}
    )
    assert inventory_module.STATIC_ASSEMBLY_ROOT_SOURCE_ROLES == frozenset(
        {"generated_dependency", "production_object", "transversal"}
    )
    assert inventory_module.STATIC_ASSEMBLY_TRAVERSAL_SOURCE_ROLES == frozenset(
        {"generated_dependency", "production_object", "transversal"}
    )
    assert inventory_module.ORPHAN_ROOT_SOURCE_ROLES == frozenset(
        {"generated_dependency", "production_object", "transversal"}
    )
    assert inventory_module.ORPHAN_TRAVERSAL_SOURCE_ROLES == frozenset(
        {"generated_dependency", "production_object", "transversal"}
    )
    assert inventory_module.DECLARED_ASSEMBLER_SOURCE_ROLES == frozenset(
        {"production_object", "transversal"}
    )
    assert inventory_module.DECLARED_ASSEMBLER_PATH_ALLOWLIST == frozenset(
        {
            "Mathematiques/manuel-maths/scripts/assemble.py",
            "Mathematiques/manuel-maths/scripts/assemble_manuel.py",
            "NSI/scripts/assemble.py",
            "NSI/scripts/assemble_manuel.py",
        }
    )
    assert inventory_module.COMPILED_PDF_SOURCE_ROLES == frozenset(
        {"generated_dependency"}
    )
    assert dict(inventory_module.COMPILED_PDF_BUILD_ROOTS) == {
        "1NSI": "NSI/build",
        "1SPE": "Mathematiques/manuel-maths/build",
        "TCOMPL": "Mathematiques/manuel-maths/build",
        "TEXPERTES": "Mathematiques/manuel-maths/build",
        "TNSI": "NSI/build",
        "TSPE_2026_2027": "Mathematiques/manuel-maths/build",
    }


@pytest.mark.parametrize(
    "source",
    [
        pytest.param(
            "NSI/chapitres/1NSI-TEST/_harvest/P04/bad.candidate.tex",
            id="harvest",
        ),
        pytest.param("NSI/tests/fixtures/bad.tex", id="fixture"),
        pytest.param(
            "Mathematiques/manuel-maths/gabarits/reference-v4/bad.tex",
            id="visual-reference",
        ),
        pytest.param("NSI/historique/bad.tex", id="archive"),
        pytest.param("NSI/validations/bad.tex", id="validation-reference"),
        pytest.param("NSI/__pycache__/bad.tex", id="excluded"),
    ],
)
def test_non_publishable_latex_source_keeps_edge_without_broken_blocker(
    tmp_path: Path,
    inventory_module,
    source: str,
) -> None:
    _init_repository(tmp_path)
    _write(tmp_path / source, "\\input{absent}\n")
    _track(tmp_path, source)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["broken_latex_references"] == []
    assert any(
        edge["source"] == source
        and edge["resolved"] is False
        and edge["cible"].endswith("/absent.tex")
        for edge in inventory["reference_graph"]
    )
    assert not any(
        source in json.dumps(anomaly, ensure_ascii=False, sort_keys=True)
        for category in inventory_module.BLOCKING_ANOMALY_CATEGORIES
        for anomaly in inventory["anomalies"][category]
    )


@pytest.mark.parametrize(
    "master",
    [
        pytest.param("NSI/extras/master.tex", id="transversal"),
        pytest.param("NSI/chapitres/UNKNOWN/master.tex", id="production"),
        pytest.param("NSI/build/master.tex", id="generated-dependency"),
    ],
)
def test_publishable_latex_sources_still_report_broken_inputs(
    tmp_path: Path,
    inventory_module,
    master: str,
) -> None:
    _init_repository(tmp_path)
    _write(tmp_path / master, "\\input{transversal/absent}\n")
    _track(tmp_path, master)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["broken_latex_references"] == [
        {
            "champ": "input",
            "cible": "NSI/transversal/absent.tex",
            "raison": "cible LaTeX absente des sources suivies",
            "source": master,
        }
    ]
    assert master in inventory["source_files"]


@pytest.mark.parametrize(
    "static_root",
    [
        pytest.param(
            "Mathematiques/manuel-maths/chapitres/"
            "1SPE-TEST/_harvest/root.candidate.tex",
            id="harvest-root",
        ),
        pytest.param("NSI/tests/fixtures/root.tex", id="fixture-root"),
    ],
)
def test_non_publishable_document_root_cannot_assemble_production_object(
    tmp_path: Path,
    inventory_module,
    static_root: str,
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    contract = f"{base}/contrat.yaml"
    course = f"{base}/cours/c1.tex"
    sources = {
        contract: _contract("1SPE-TEST", "1SPE", capacities=1),
        course: _meta(status="approved"),
        static_root: (
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            f"\\input{{{course.removesuffix('.tex')}}}\n"
            "\\end{document}\n"
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)

    assert not any(
        assembly.get("assembler") == static_root
        for assembly in inventory["assemblies"]
    )
    assert inventory["anomalies"]["unassembled_objects"] == [
        {
            "champ": "assemblages_declares",
            "cible": course,
            "raison": "objet META exclu de tous les assemblages declares",
            "source": course,
        }
    ]


@pytest.mark.parametrize(
    "non_publishable_root",
    [
        pytest.param(
            "NSI/chapitres/1NSI-TEST/_harvest/root.candidate.tex",
            id="harvest",
        ),
        pytest.param("NSI/tests/fixtures/root.tex", id="fixture"),
        pytest.param("NSI/historique/root.tex", id="archive"),
        pytest.param("NSI/validations/root.tex", id="validation"),
    ],
)
def test_non_publishable_document_root_cannot_hide_transversal_orphan(
    tmp_path: Path,
    inventory_module,
    non_publishable_root: str,
) -> None:
    _init_repository(tmp_path)
    orphan = "NSI/extras/hidden.tex"
    sources = {
        non_publishable_root: (
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            "\\input{extras/hidden}\n"
            "\\end{document}\n"
        ),
        orphan: "Contenu LaTeX non référencé par une racine publiable\n",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)

    assert {
        anomaly["cible"] for anomaly in inventory["anomalies"]["orphan_files"]
    } == {orphan}


@pytest.mark.parametrize(
    "non_publishable_bridge",
    [
        pytest.param(
            "NSI/chapitres/1NSI-TEST/_harvest/bridge.candidate.tex",
            id="harvest",
        ),
        pytest.param("NSI/tests/fixtures/bridge.tex", id="fixture"),
        pytest.param("NSI/historique/bridge.tex", id="archive"),
        pytest.param("NSI/validations/bridge.tex", id="validation"),
    ],
)
def test_non_publishable_source_cannot_extend_orphan_reachability(
    tmp_path: Path,
    inventory_module,
    non_publishable_bridge: str,
) -> None:
    _init_repository(tmp_path)
    production_root = "NSI/extras/master.tex"
    orphan = "NSI/extras/hidden.tex"
    sources = {
        production_root: (
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            f"\\input{{{non_publishable_bridge.removeprefix('NSI/')}}}\n"
            "\\end{document}\n"
        ),
        non_publishable_bridge: "\\input{extras/hidden}\n",
        orphan: "Contenu LaTeX derrière une source non publiable\n",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)

    assert {
        anomaly["cible"] for anomaly in inventory["anomalies"]["orphan_files"]
    } == {orphan}


@pytest.mark.parametrize(
    "non_publishable_bridge",
    [
        pytest.param(
            "Mathematiques/manuel-maths/chapitres/"
            "1SPE-TEST/_harvest/bridge.candidate.tex",
            id="harvest",
        ),
        pytest.param(
            "Mathematiques/manuel-maths/tests/fixtures/bridge.tex",
            id="fixture",
        ),
        pytest.param(
            "Mathematiques/manuel-maths/historique/bridge.tex",
            id="archive",
        ),
        pytest.param(
            "Mathematiques/manuel-maths/validations/bridge.tex",
            id="validation",
        ),
    ],
)
def test_non_publishable_source_cannot_extend_static_assembly(
    tmp_path: Path,
    inventory_module,
    non_publishable_bridge: str,
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    contract = f"{base}/contrat.yaml"
    course = f"{base}/cours/c1.tex"
    static_root = "Mathematiques/manuel-maths/build/root.tex"
    bridge_target = non_publishable_bridge.removeprefix(
        "Mathematiques/manuel-maths/"
    )
    sources = {
        contract: _contract("1SPE-TEST", "1SPE", capacities=1),
        course: _meta(status="approved"),
        static_root: (
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            f"\\input{{{bridge_target}}}\n"
            "\\end{document}\n"
        ),
        non_publishable_bridge: (
            "\\input{chapitres/1SPE-TEST/cours/c1}\n"
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    assembly = next(
        item
        for item in inventory["assemblies"]
        if item["assembler"] == static_root
    )

    assert non_publishable_bridge in assembly["included_files"]
    assert course not in assembly["included_files"]
    assert assembly["included_objects"] == []
    assert inventory["anomalies"]["unassembled_objects"] == [
        {
            "champ": "assemblages_declares",
            "cible": course,
            "raison": "objet META exclu de tous les assemblages declares",
            "source": course,
        }
    ]


def test_fixture_assembler_cannot_assemble_production_objects(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1NSI", "1NSI-TEST")
    contract = f"{base}/contrat.yaml"
    course = f"{base}/cours/10_cours.tex"
    assembler = "NSI/tests/fixtures/scripts/assemble.py"
    sources = {
        contract: _contract("1NSI-TEST", "1NSI", capacities=1),
        course: _meta(
            id="1NSI-TEST-COURS-C1",
            chapitre="1NSI-TEST",
            status="approved",
        ),
        assembler: 'ORDER = [("cours", "*")]\nVARIANTS = ["complet"]\n',
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)

    assert not any(
        assembly["assembler"] == assembler for assembly in inventory["assemblies"]
    )
    assert inventory["anomalies"]["unassembled_objects"] == [
        {
            "champ": "assemblages_declares",
            "cible": course,
            "raison": "objet META exclu de tous les assemblages declares",
            "source": course,
        }
    ]


@pytest.mark.parametrize(
    "assembler",
    [
        pytest.param(
            "NSI/chapitres/1NSI-TEST/scripts/assemble.py",
            id="production-role",
        ),
        pytest.param(
            "NSI/extras/scripts/assemble.py",
            id="transversal-role",
        ),
    ],
)
def test_noncanonical_assembler_cannot_prove_declared_assembly(
    tmp_path: Path,
    inventory_module,
    assembler: str,
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1NSI", "1NSI-TEST")
    contract = f"{base}/contrat.yaml"
    course = f"{base}/cours/10_cours.tex"
    sources = {
        contract: _contract("1NSI-TEST", "1NSI", capacities=1),
        course: _meta(
            id="1NSI-TEST-COURS-C1",
            chapitre="1NSI-TEST",
            status="approved",
        ),
        assembler: 'ORDER = [("cours", "*")]\nVARIANTS = ["complet"]\n',
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)

    assert not any(
        assembly["assembler"] == assembler for assembly in inventory["assemblies"]
    )
    assert inventory["anomalies"]["unassembled_objects"] == [
        {
            "champ": "assemblages_declares",
            "cible": course,
            "raison": "objet META exclu de tous les assemblages declares",
            "source": course,
        }
    ]
    assert {
        anomaly["cible"]
        for anomaly in inventory["anomalies"]["missing_assemblers"]
        if anomaly["champ"] == "chapitre"
    } >= {"1NSI", "TNSI"}


def test_declared_assembler_allowlist_preserves_real_and_planned_engines(
    inventory_module, monkeypatch
) -> None:
    tracked = inventory_module.git_tracked_files(ROOT)
    source_roles = inventory_module._load_source_roles(ROOT, tracked)
    expected = inventory_module.DECLARED_ASSEMBLER_PATH_ALLOWLIST
    planned = "NSI/scripts/assemble_manuel.py"
    existing = expected & set(tracked)

    assert planned in expected
    assert expected <= set(tracked) | {planned}
    assert {
        source_roles[path] for path in existing
    } <= inventory_module.DECLARED_ASSEMBLER_SOURCE_ROLES
    for path in existing:
        analysis = inventory_module.analyze_assembler(ROOT / path)
        assert inventory_module._assembly_core.validate_analysis(
            path,
            analysis,
        ) == []

    monkeypatch.setattr(
        inventory_module,
        "BUILD_MANIFEST_FILE",
        "audit/TEST_ABSENT_BUILD_MANIFEST.json",
    )
    inventory = inventory_module.build_inventory(ROOT)
    assert inventory["declared_assemblies"] == inventory["assemblies"]
    observed = {
        assembly["assembler"]
        for assembly in inventory["assemblies"]
        if assembly["scope"] in {"chapter", "manual"}
    }

    assert observed == existing


@pytest.mark.parametrize(
    "orphan",
    [
        pytest.param("NSI/extras/orphan.tex", id="default-transversal"),
        pytest.param("NSI/transversal/orphan.tex", id="explicit-transversal"),
    ],
)
def test_transversal_tex_without_root_remains_a_real_orphan(
    tmp_path: Path,
    inventory_module,
    orphan: str,
) -> None:
    _init_repository(tmp_path)
    _write(tmp_path / orphan, "Contenu LaTeX non référencé\n")
    _track(tmp_path, orphan)

    inventory = inventory_module.build_inventory(tmp_path)

    assert {
        anomaly["cible"] for anomaly in inventory["anomalies"]["orphan_files"]
    } == {orphan}


def test_orphan_reachability_ignores_edges_from_unreachable_sources_and_cycles(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    first = "NSI/extras/cycle-a.tex"
    second = "NSI/extras/cycle-b.tex"
    leaf = "NSI/extras/leaf.tex"
    sources = {
        first: "\\input{extras/cycle-b}\n",
        second: "\\input{extras/cycle-a}\n",
        leaf: "Contenu sans racine\n",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    orphans = {item["cible"] for item in inventory["anomalies"]["orphan_files"]}

    assert orphans == {first, second, leaf}


def test_latex_reference_uses_source_relative_target_when_it_is_tracked(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    master = "Mathematiques/manuel-maths/gabarits/reference/main.tex"
    part = "Mathematiques/manuel-maths/gabarits/reference/chapters/part.tex"
    _write(tmp_path / master, "\\documentclass{article}\n\\input{chapters/part}\n")
    _write(tmp_path / part, "Partie suivie\n")
    _track(tmp_path, master, part)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["broken_latex_references"] == []
    assert any(
        edge["source"] == master and edge["cible"] == part and edge["resolved"] is True
        for edge in inventory["reference_graph"]
    )


def test_missing_declared_manual_chapter_is_broken_and_never_covered(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    assembler = "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        f"{base}/cours/10_cours.tex": _meta(id="1SPE-TEST-COURS-C1", status="approved"),
        assembler: """CHAPITRES = ["1SPE-TEST", "1SPE-ABSENT", "INCONNU-CHAP"]
ORDER = [("cours", "1*")]
VARIANTS = ["professeur"]
""",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    manual = next(
        item
        for item in inventory["assemblies"]
        if item["assembly_id"] == "math:manual:1SPE:professeur"
    )

    assert manual["chapters"] == ["1SPE-TEST"]
    assert inventory["anomalies"]["broken_assembly_references"] == [
        {
            "champ": "CHAPITRES[1]",
            "cible": "1SPE-ABSENT",
            "raison": "chapitre declare par l'assembleur absent des sources suivies",
            "source": assembler,
        },
        {
            "champ": "CHAPITRES[2]",
            "cible": "INCONNU-CHAP",
            "raison": "prefixe de chapitre inconnu dans CHAPITRES",
            "source": assembler,
        },
    ]


def test_exercise_glob_order_places_all_hints_after_primary_exercises(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    assembler = "Mathematiques/manuel-maths/scripts/assemble.py"
    paths = [
        f"{base}/exercices/1SPE-TEST-EX-001.tex",
        f"{base}/exercices/1SPE-TEST-EX-001-CDP.tex",
        f"{base}/exercices/1SPE-TEST-EX-002.tex",
        f"{base}/exercices/1SPE-TEST-EX-002-CDP.tex",
    ]
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        paths[0]: _meta(id="EX-1", type_objet="exercice", status="approved"),
        paths[1]: _meta(id="CDP-1", type_objet="coup_de_pouce", status="approved"),
        paths[2]: _meta(id="EX-2", type_objet="exercice", status="approved"),
        paths[3]: _meta(id="CDP-2", type_objet="coup_de_pouce", status="approved"),
        assembler: 'ORDER = [("exercices", "*")]\nVARIANTS = ["complet"]\n',
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    assembly = next(
        item
        for item in inventory["assemblies"]
        if item["assembly_id"] == "math:chapter:1SPE-TEST:complet"
    )

    assert assembly["included_objects"] == [paths[0], paths[2], paths[1], paths[3]]


def test_pdf_page_count_falls_back_to_python_reader(
    tmp_path: Path, inventory_module, monkeypatch: pytest.MonkeyPatch
) -> None:
    _init_repository(tmp_path)
    pdf = "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
    _write(tmp_path / pdf, "contenu simule")
    _track(tmp_path, pdf)
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_pdfinfo",
        lambda _path: (None, "pdfinfo indisponible"),
    )
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_python",
        lambda _path: (19, None),
    )

    artifact = inventory_module.build_inventory(tmp_path)["pdfs"][0]

    assert artifact["page_count"] == 19
    assert artifact["page_count_method"] == "python"
    assert artifact["manual"] == "1SPE"
    assert artifact["scope"] == "manual"
    assert artifact["variant"] == "professeur"


def test_chapter_pdf_attribution_aggregates_pages_and_variants(
    tmp_path: Path, inventory_module, monkeypatch: pytest.MonkeyPatch
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    pdf = "Mathematiques/manuel-maths/build/1SPE-TEST/" "1SPE-TEST_methodes.pdf"
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        f"{base}/cours/10_cours.tex": _meta(id="1SPE-TEST-COURS-C1", status="approved"),
        pdf: "contenu simule",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_pdfinfo",
        lambda _path: (8, None),
    )

    inventory = inventory_module.build_inventory(tmp_path)
    artifact = inventory["pdfs"][0]
    manual = inventory["manuals"]["1SPE"]
    chapter_model = manual["chapters"][chapter]

    assert artifact["manual"] == "1SPE"
    assert artifact["chapter"] == chapter
    assert artifact["scope"] == "chapter"
    assert artifact["variant"] == "methodes"
    expected_compiled = {
        "chapter": ["methodes"],
        "manual": [],
        "static": [],
    }
    assert manual["compiled_variants"] == expected_compiled
    assert chapter_model["compiled_variants"] == expected_compiled
    assert manual["compiled_artifacts"] == [artifact]
    assert chapter_model["compiled_artifacts"] == [artifact]
    assert "compiled_pages" not in manual
    assert "compiled_pages" not in chapter_model
    assert "variants" not in manual
    assert "variants" not in chapter_model


def test_meta_graph_resolves_capacity_prerequisite_method_and_hint_families(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    contract = f"{base}/contrat.yaml"
    method_one = f"{base}/methodes/1SPE-TEST-ME-001.tex"
    method_two = f"{base}/methodes/1SPE-TEST-ME-002.tex"
    hint = f"{base}/exercices/1SPE-TEST-EX-001-CDP.tex"
    exercise = f"{base}/exercices/1SPE-TEST-EX-001.tex"
    _write(
        tmp_path / contract,
        _contract(chapter, "1SPE", capacities=1)
        + "prerequis:\n  - {code: R1, libelle: Prerequis}\n",
    )
    sources = {
        method_one: _meta(
            id="1SPE-TEST-ME-001", type_objet="methode", status="approved"
        ),
        method_two: _meta(
            id="1SPE-TEST-ME-002", type_objet="methode", status="approved"
        ),
        hint: _meta(
            id="1SPE-TEST-EX-001-CDP",
            type_objet="coup_de_pouce",
            status="approved",
        ),
        exercise: _meta(
            id="1SPE-TEST-EX-001",
            type_objet="exercice",
            status="approved",
            capacites_codes=["C1", "R1"],
            methodes=["M1", "1SPE-TEST-ME-002"],
            coups_de_pouce=[
                "1SPE-TEST-EX-001-CDP",
                "chapitres/1SPE-TEST/exercices/1SPE-TEST-EX-001-CDP.tex",
            ],
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, contract, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    edges = {
        (edge["champ"], edge["cible"], edge["kind"], edge["resolved"])
        for edge in inventory["reference_graph"]
        if edge["source"] == exercise
    }

    assert ("capacites_codes[0]", "1SPE-TEST-C1", "capacity", True) in edges
    assert (
        "capacites_codes[1]",
        "1SPE-TEST:prerequis:R1",
        "prerequisite",
        True,
    ) in edges
    assert ("methodes[0]", "1SPE-TEST-ME-001", "method", True) in edges
    assert ("methodes[1]", "1SPE-TEST-ME-002", "method", True) in edges
    assert ("coups_de_pouce[0]", "1SPE-TEST-EX-001-CDP", "hint_id", True) in edges
    assert ("coups_de_pouce[1]", hint, "hint_path", True) in edges


def test_meta_graph_reports_unknown_and_invalid_reference_forms_by_family(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    contract = f"{base}/contrat.yaml"
    exercise = f"{base}/exercices/1SPE-TEST-EX-001.tex"
    _write(tmp_path / contract, _contract(chapter, "1SPE", capacities=1))
    _write(
        tmp_path / exercise,
        _meta(
            id="1SPE-TEST-EX-001",
            type_objet="exercice",
            status="approved",
            capacites_codes=["C9", 9],
            methodes=["M9", {"invalide": True}],
            coups_de_pouce=["CDP-INCONNU", False],
        ),
    )
    _track(tmp_path, contract, exercise)

    inventory = inventory_module.build_inventory(tmp_path)

    broken_fields = {
        item["champ"] for item in inventory["anomalies"]["broken_meta_references"]
    }
    invalid_fields = {
        item["champ"] for item in inventory["anomalies"]["invalid_meta_references"]
    }
    assert {"capacites_codes[0]", "methodes[0]", "coups_de_pouce[0]"} <= broken_fields
    assert {"capacites_codes[1]", "methodes[1]", "coups_de_pouce[1]"} <= invalid_fields


def test_method_aliases_use_meta_then_verified_id_suffix_without_positional_fallback(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    contract = f"{base}/contrat.yaml"
    method_one = f"{base}/methodes/1SPE-TEST-ME-001.tex"
    method_three = f"{base}/methodes/1SPE-TEST-ME-003.tex"
    explicit = f"{base}/methodes/methode-explicite.tex"
    exercise = f"{base}/exercices/1SPE-TEST-EX-001.tex"
    sources = {
        contract: _contract(chapter, "1SPE", capacities=1),
        method_one: _meta(
            id="1SPE-TEST-ME-001", type_objet="methode", status="approved"
        ),
        method_three: _meta(
            id="1SPE-TEST-ME-003", type_objet="methode", status="approved"
        ),
        explicit: _meta(
            id="1SPE-TEST-METHODE-ALPHA",
            type_objet="methode",
            methodes=["M7"],
            status="approved",
        ),
        exercise: _meta(
            id="1SPE-TEST-EX-001",
            type_objet="exercice",
            methodes=["M2", "M3", "M7"],
            status="approved",
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    edges = {
        (edge["champ"], edge["cible"], edge["resolved"])
        for edge in inventory["reference_graph"]
        if edge["source"] == exercise
    }

    assert ("methodes[0]", "M2", False) in edges
    assert ("methodes[1]", "1SPE-TEST-ME-003", True) in edges
    assert ("methodes[2]", "1SPE-TEST-METHODE-ALPHA", True) in edges


def test_missing_and_duplicate_method_aliases_are_reported(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        f"{base}/methodes/sans-alias.tex": _meta(
            id="1SPE-TEST-METHODE-SANS-ALIAS",
            type_objet="methode",
            status="approved",
        ),
        f"{base}/methodes/doublon-a.tex": _meta(
            id="1SPE-TEST-METHODE-A",
            type_objet="methode",
            methodes=["M4"],
            status="approved",
        ),
        f"{base}/methodes/doublon-b.tex": _meta(
            id="1SPE-TEST-METHODE-B",
            type_objet="methode",
            methodes=["M4"],
            status="approved",
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    issues = inventory["anomalies"]["broken_meta_references"]

    assert any(
        item["source"].endswith("sans-alias.tex")
        and "alias de methode absent" in item["raison"]
        for item in issues
    )
    assert (
        sum("alias de methode ambigu ou duplique" in item["raison"] for item in issues)
        >= 2
    )


def test_physical_chapter_drives_assembly_even_when_meta_chapter_mismatches(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    physical = "1SPE-PHYSIQUE"
    base = _chapter_path("1SPE", physical)
    course = f"{base}/cours/10_cours.tex"
    assembler = "Mathematiques/manuel-maths/scripts/assemble.py"
    sources = {
        f"{base}/contrat.yaml": _contract(physical, "1SPE", capacities=1),
        course: _meta(
            id="OBJ-MISMATCH",
            chapitre="1SPE-META-AUTRE",
            status="approved",
        ),
        assembler: 'ORDER = [("cours", "1*")]\nVARIANTS = ["complet"]\n',
        "Mathematiques/manuel-maths/gabarits/chapitre_master.tex": "%%CONTENT%%\n",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    item = inventory["manuals"]["1SPE"]["chapters"][physical]["objects"][0]
    assembly = next(
        value
        for value in inventory["assemblies"]
        if value["assembly_id"] == f"math:chapter:{physical}:complet"
    )

    assert item["path_chapter"] == physical
    assert assembly["included_objects"] == [course]
    assert inventory["anomalies"]["context_mismatches"]


def test_assembler_choices_name_is_resolved_and_invalid_declarations_do_not_cover(
    tmp_path: Path, inventory_module
) -> None:
    valid = tmp_path / "valid.py"
    _write(
        valid,
        """ORDER = [("cours", "*")]
VARIANTS = ["complet", "methodes"]
parser.add_argument("--variant", choices=VARIANTS)
""",
    )
    assert inventory_module.analyze_assembler(valid)["variants"] == [
        "complet",
        "methodes",
    ]

    repository = tmp_path / "repo"
    _init_repository(repository)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    assembler = "Mathematiques/manuel-maths/scripts/assemble.py"
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        f"{base}/cours/10_cours.tex": _meta(status="approved"),
        assembler: 'ORDER = "invalide"\nVARIANTS = []\n',
    }
    for path, content in sources.items():
        _write(repository / path, content)
    _track(repository, *sources)

    inventory = inventory_module.build_inventory(repository)

    assert inventory["assemblies"] == []
    assert any(
        item["source"] == assembler
        for item in inventory["anomalies"]["assembler_invalid"]
    )
    assert any(
        item["cible"] == "1SPE" and item["champ"] == "chapitre"
        for item in inventory["anomalies"]["missing_assemblers"]
    )


def test_dynamic_assembler_dependencies_are_included_and_missing_ones_are_broken(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    chapter_assembler = "Mathematiques/manuel-maths/scripts/assemble.py"
    manual_assembler = "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
    master = "Mathematiques/manuel-maths/gabarits/chapitre_master.tex"
    transversal = "Mathematiques/manuel-maths/transversal/page_de_garde.tex"
    contract = f"{base}/contrat.yaml"
    sources = {
        contract: _contract(chapter, "1SPE", capacities=1),
        f"{base}/cours/10_cours.tex": _meta(status="approved"),
        master: "%%CONTENT%%\n",
        transversal: "Page de garde\n",
        chapter_assembler: 'ORDER = [("cours", "1*")]\nVARIANTS = ["complet"]\n',
        manual_assembler: """CHAPITRES = ["1SPE-TEST"]
ORDER = [("cours", "1*")]
VARIANTS = ["professeur"]
parts.append("\\\\input{transversal/page_de_garde}")
""",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    assemblies = {item["assembly_id"]: item for item in inventory["assemblies"]}

    assert {master, contract} <= set(
        assemblies[f"math:chapter:{chapter}:complet"]["included_files"]
    )
    assert {transversal, contract} <= set(
        assemblies["math:manual:1SPE:professeur"]["included_files"]
    )
    assert not inventory["anomalies"]["broken_assembly_references"]

    (tmp_path / master).unlink()
    inventory = inventory_module.build_inventory(tmp_path)
    assert any(
        item["cible"] == master
        for item in inventory["anomalies"]["broken_assembly_references"]
    )


def test_fstring_documentclass_is_a_dynamic_assembly_dependency(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    assembler = "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
    collection_class = "Mathematiques/manuel-maths/gabarits/nexus-manuel.cls"
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        f"{base}/cours/10_cours.tex": _meta(status="approved"),
        collection_class: "\\NeedsTeXFormat{LaTeX2e}\n",
        assembler: '''CHAPITRES = ["1SPE-TEST"]
ORDER = [("cours", "1*")]
VARIANTS = ["professeur"]
master = f"""\\\\documentclass{{gabarits/nexus-manuel}}
\\\\begin{{document}}
{content}
\\\\end{{document}}
"""
''',
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    assembly = next(
        item
        for item in inventory["assemblies"]
        if item["assembly_id"] == "math:manual:1SPE:professeur"
    )

    assert collection_class in assembly["included_files"]
    assert not inventory["anomalies"]["broken_assembly_references"]

    (tmp_path / collection_class).unlink()
    inventory = inventory_module.build_inventory(tmp_path)
    assert any(
        item["cible"] == collection_class
        for item in inventory["anomalies"]["broken_assembly_references"]
    )


def test_generic_chapter_engine_exists_without_claiming_manual_coverage(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    assembler = "NSI/scripts/assemble.py"
    master = "NSI/gabarits/chapitre_master.tex"
    sources = {
        assembler: 'ORDER = [("cours", "*")]\nVARIANTS = ["complet"]\n',
        master: "%%CONTENT%%\n",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    missing = inventory["anomalies"]["missing_assemblers"]

    assert not any(
        item["cible"] == "TNSI" and item["champ"] == "chapitre" for item in missing
    )
    assert any(
        item["cible"] == "TNSI" and item["champ"] == "manuel" for item in missing
    )
    assert not any(
        item["manual"] == "TNSI" and item["scope"] == "chapter"
        for item in inventory["assemblies"]
    )


def test_duplicate_chapter_declaration_preserves_multiple_inclusion_and_reports_it(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    course = f"{base}/cours/10_cours.tex"
    assembler = "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        course: _meta(status="approved"),
        assembler: """CHAPITRES = ["1SPE-TEST", "1SPE-TEST"]
ORDER = [("cours", "1*")]
VARIANTS = ["professeur"]
""",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    assembly = next(
        item
        for item in inventory["assemblies"]
        if item["assembly_id"] == "math:manual:1SPE:professeur"
    )

    assert assembly["chapters"] == [chapter, chapter]
    assert assembly["included_objects"] == [course, course]
    assert any(
        item["cible"] == course and "chapitre duplique" in item["raison"]
        for item in inventory["anomalies"]["duplicate_assembly_objects"]
    )


def test_latex_comment_parser_preserves_escaped_percent(inventory_module) -> None:
    source = r"Texte 50\% puis \input{visible} % \input{ignore}"

    assert inventory_module._latex_inputs(source) == [("input", "visible")]


def test_static_latex_cycle_is_reported_and_deep_chain_is_iterative(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    project = "NSI"
    root_tex = f"{project}/build/root.tex"
    sources = {
        root_tex: "\\documentclass{article}\n\\input{chain/0000}\n",
    }
    depth = 1050
    for index in range(depth):
        current = f"{project}/chain/{index:04d}.tex"
        following = f"chain/{index + 1:04d}" if index + 1 < depth else "chain/0000"
        sources[current] = f"\\input{{{following}}}\n"
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["latex_cycles"]
    assert any(
        item["champ"] == f"nsi:static:{root_tex}"
        for item in inventory["anomalies"]["latex_cycles"]
    )


def test_source_digest_distinguishes_empty_from_missing_tracked_file(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    source = "NSI/gabarits/empty.tex"
    _write(tmp_path / source, "")
    _track(tmp_path, source)

    present = inventory_module.build_inventory(tmp_path)["source_digest"]
    (tmp_path / source).unlink()
    missing = inventory_module.build_inventory(tmp_path)["source_digest"]

    assert present != missing


def test_pdfinfo_timeout_is_bounded_and_reported(
    tmp_path: Path, inventory_module, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf = tmp_path / "slow.pdf"
    _write(pdf, "contenu")

    def timeout_runner(*_args, **kwargs):
        assert kwargs["timeout"] == inventory_module.PDFINFO_TIMEOUT_SECONDS
        raise subprocess.TimeoutExpired("pdfinfo", kwargs["timeout"])

    monkeypatch.setattr(inventory_module.subprocess, "run", timeout_runner)

    assert inventory_module._page_count_with_pdfinfo(pdf) == (
        None,
        f"pdfinfo timeout ({inventory_module.PDFINFO_TIMEOUT_SECONDS}s)",
    )


def test_report_claims_reconcile_chapter_table_and_keep_unknown_pages_open(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    report = "Mathematiques/manuel-maths/RAPPORT_FINAL_1SPE.md"
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        f"{base}/exercices/ex-1.tex": _meta(
            id="1SPE-TEST-EX-001", type_objet="exercice", status="approved"
        ),
        f"{base}/exercices/ex-2.tex": _meta(
            id="1SPE-TEST-EX-002", type_objet="exercice", status="approved"
        ),
        report: """# RAPPORT FINAL — Manuel de Mathematiques Premiere Specialite

### Chapitres (1)

| # | Chapitre | Exercices | Pages (chap) |
|---|---|---:|---:|
| 1 | Chapitre de test | 2 | 12 |
| | **Total** | **2** | **12** |
""",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    reconciliation = inventory["report_reconciliation"]
    claims = reconciliation["claims"]

    chapter_exercises = next(
        claim
        for claim in claims
        if claim["scope"] == "chapter:1SPE-TEST"
        and claim["metric"] == "exercices_principaux"
    )
    assert chapter_exercises == {
        "calculated": 2,
        "declared": 2,
        "evidence": "manuals.1SPE.chapters.1SPE-TEST.counts.exercices_principaux",
        "etat": "confirme",
        "line": 7,
        "metric": "exercices_principaux",
        "path": report,
        "raw": "| 1 | Chapitre de test | 2 | 12 |",
        "scope": "chapter:1SPE-TEST",
    }
    chapter_pages = next(
        claim
        for claim in claims
        if claim["scope"] == "chapter:1SPE-TEST"
        and claim["metric"] == "pages_compilees"
    )
    assert chapter_pages["declared"] == 12
    assert chapter_pages["calculated"] is None
    assert chapter_pages["etat"] == "ouvert"
    assert chapter_pages in reconciliation["claims_non_resolues"]
    assert reconciliation["summary"] == {
        "confirme": 3,
        "contredit": 0,
        "ouvert": 2,
    }


def test_report_claims_flag_numeric_and_completeness_contradictions(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1NSI-TEST"
    base = _chapter_path("1NSI", chapter)
    report = "NSI/DIRECTIVES_EN_COURS.md"
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1NSI", capacities=1).replace(
            "statut: approved", "statut: draft"
        ),
        f"{base}/exercices/ex-1.tex": _meta(
            id="1NSI-TEST-EX-001",
            chapitre=chapter,
            type_objet="exercice",
            status="needs_review",
        ),
        report: """# DIRECTIVES EN COURS

- [x] PILOTE 1NSI-TEST : LOT 0→7 complet (3 ex, 1 corriges,
      2 CDP, 4 QCM, 5 rem, 6 eval, 7 TD, 8 projets).
      Gates strict VERT, 165 tests.
""",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    claims = inventory_module.build_inventory(tmp_path)["report_reconciliation"][
        "claims"
    ]

    exercises = next(
        claim for claim in claims if claim["metric"] == "exercices_principaux"
    )
    assert exercises["path"] == report
    assert exercises["line"] == 3
    assert exercises["scope"] == "chapter:1NSI-TEST"
    assert exercises["declared"] == 3
    assert exercises["calculated"] == 1
    assert exercises["etat"] == "contredit"
    completeness = next(claim for claim in claims if claim["metric"] == "completude")
    assert completeness["declared"] is True
    assert completeness["calculated"] is False
    assert completeness["etat"] == "contredit"
    tests = next(claim for claim in claims if claim["metric"] == "tests_passes")
    assert tests["line"] == 5
    assert tests["declared"] == 165
    assert tests["calculated"] is None
    assert tests["etat"] == "ouvert"


def test_report_source_routing_prefers_history_and_ignores_generated_outputs(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    root_report = "ETAT_COLLECTION.md"
    history = "audit/historique/ETAT_COLLECTION_AVANT_P0.md"
    generated = "audit/AUDIT_CONSOLIDE.md"
    generated_yaml = "audit/ECARTS_ET_CONTRADICTIONS.yaml"
    math_report = "Mathematiques/manuel-maths/ETAT_COLLECTION.md"
    sources = {
        root_report: "# Ancien etat\n",
        history: "# Archive de l'ancien etat\n",
        generated: "<!-- AUTO-GENERE PAR inventory_collection.py -->\n",
        generated_yaml: "# generated by inventory_collection.py\ncounts: {}\n",
        math_report: "# Etat mathematiques\n",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)
    tracked = inventory_module.git_tracked_files(tmp_path)

    assert inventory_module.report_source_paths(tmp_path, tracked) == (
        history,
        math_report,
    )


def test_report_claim_spanning_multiple_chapters_stays_open(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    first = "1SPE-PREMIER"
    second = "1SPE-SECOND"
    sources = {
        f"{_chapter_path('1SPE', first)}/contrat.yaml": _contract(
            first, "1SPE", capacities=1
        ),
        f"{_chapter_path('1SPE', second)}/contrat.yaml": _contract(
            second, "1SPE", capacities=1
        ),
        "ETAT_COLLECTION.md": (
            "| Manuel | Etat |\n"
            "|---|---|\n"
            "| Mathématiques Première | 1SPE-PREMIER et 1SPE-SECOND : "
            "30 exercices |\n"
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    claim = next(
        claim
        for claim in inventory_module.build_inventory(tmp_path)[
            "report_reconciliation"
        ]["claims"]
        if claim["metric"] == "exercices_principaux"
    )

    assert claim["scope"] == "unresolved:portee_chapitres_ambigue"
    assert claim["calculated"] is None
    assert claim["etat"] == "ouvert"


def test_deliverable_matrix_covers_all_mission_variants_and_blocks_publication(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        f"{base}/cours/c1.tex": _meta(status="approved"),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    matrix = inventory["deliverable_matrix"]

    assert list(matrix["manuals"]) == [
        "1NSI",
        "1SPE",
        "TCOMPL",
        "TEXPERTES",
        "TNSI",
        "TSPE_2026_2027",
    ]
    assert set(matrix["manuals"]["1SPE"]["variants"]) == {
        "banque_evaluations",
        "livret_methodes",
        "livret_remediation",
        "manuel_eleve",
        "manuel_professeur",
    }
    assert set(matrix["manuals"]["1NSI"]["variants"]) == {
        "evaluations",
        "livret_methodes",
        "manuel_eleve",
        "manuel_professeur",
        "projets",
        "remediations",
        "version_amenagee",
    }
    assert set(matrix["manuals"]["TNSI"]["variants"]) == {
        "banque_ecrite",
        "banque_pratique",
        "manuel_eleve",
        "manuel_professeur",
        "projets",
        "remediations",
        "version_amenagee",
    }
    assert matrix["manuals"]["1SPE"]["current"]["chapter_count"] == 1
    assert matrix["manuals"]["1SPE"]["objective"]["target_chapters"] == 10
    assert matrix["manuals"]["1SPE"]["publication_eligible"] is False
    assert any(
        blocker["code"] == "chapitres_manquants"
        for blocker in matrix["manuals"]["1SPE"]["blockers"]
    )
    assert all(
        variant["state"] == "absent"
        for variant in matrix["manuals"]["1SPE"]["variants"].values()
    )


def test_deliverable_matrix_blocks_needs_review_and_checks_model_coherence(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1NSI-TEST"
    base = _chapter_path("1NSI", chapter)
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1NSI", capacities=1),
        f"{base}/cours/c1.tex": _meta(
            id="1NSI-TEST-C1",
            chapitre=chapter,
            status="needs_review",
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    manual = inventory["deliverable_matrix"]["manuals"]["1NSI"]

    assert manual["publication_eligible"] is False
    assert any(
        blocker["code"] == "statuts_non_approuves" for blocker in manual["blockers"]
    )
    assert inventory["coherence_checks"] == {
        "artifact_cardinality": {"ok": True, "violations": []},
        "chapter_manual_sums": {"ok": True, "violations": []},
        "status_distribution": {"ok": True, "violations": []},
    }

    inventory["manuals"]["1NSI"]["totals"]["sections_cours"] += 1
    checks = inventory_module.validate_inventory_coherence(inventory)
    assert checks["chapter_manual_sums"]["ok"] is False
    assert checks["chapter_manual_sums"]["violations"] == [
        {
            "calculated": 1,
            "declared": 2,
            "manual": "1NSI",
            "metric": "sections_cours",
        }
    ]

    inventory["manuals"]["1NSI"]["totals"]["sections_cours"] -= 1
    inventory["manuals"]["1NSI"]["statuses"] = {"approved": 1}
    checks = inventory_module.validate_inventory_coherence(inventory)
    assert checks["status_distribution"]["ok"] is False

    inventory["pdfs"].append(
        {
            "chapter": None,
            "manual": "1NSI",
            "page_count": 10,
            "page_count_method": "pdfinfo",
            "path": "NSI/build/MANUEL_1NSI_v1.pdf",
            "reason": None,
            "scope": "manual",
            "source_role": "generated_dependency",
            "status": "counted",
            "variant": "eleve",
        }
    )
    checks = inventory_module.validate_inventory_coherence(inventory)
    assert checks["artifact_cardinality"]["ok"] is False
    assert checks["artifact_cardinality"]["violations"] == [
        {
            "actual": 0,
            "expected": 1,
            "manual": "1NSI",
            "scope": "manual",
        }
    ]


def test_chapter_and_manual_blockers_use_the_same_qualification_view(
    tmp_path: Path,
    inventory_module,
) -> None:
    inventory = _minimal_inventory(tmp_path, inventory_module)
    for values in inventory["anomalies"].values():
        values.clear()
    anomaly = {
        "chapter": "1SPE-TEST",
        "id": "1SPE-TEST-EX-001",
        "manual": "1SPE",
    }
    inventory["anomalies"]["missing_corrections"] = [anomaly]
    fingerprint = inventory_module._anomaly_fingerprint(
        anomaly,
        category="missing_corrections",
    )
    inventory["anomaly_qualifications"] = {
        fingerprint: {
            "blocking": False,
            "disposition": "accepted_exception",
            "fingerprint": fingerprint,
        }
    }
    specification = deepcopy(inventory_module.DELIVERABLE_SPECS["1SPE"])
    specification["target_chapters"] = 1

    assert inventory_module._chapter_publication_eligible(
        inventory,
        "1SPE",
        "1SPE-TEST",
    ) is True
    assert not any(
        blocker["code"] == "anomalie:missing_corrections"
        for blocker in inventory_module._manual_blockers(
            inventory,
            "1SPE",
            specification,
        )
    )

    inventory["anomaly_qualifications"][fingerprint]["blocking"] = True

    assert inventory_module._chapter_publication_eligible(
        inventory,
        "1SPE",
        "1SPE-TEST",
    ) is False
    assert any(
        blocker["code"] == "anomalie:missing_corrections"
        for blocker in inventory_module._manual_blockers(
            inventory,
            "1SPE",
            specification,
        )
    )


def test_real_object_count_is_not_the_sum_of_overlapping_metrics(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        f"{base}/cours/diagnostic.tex": _meta(
            id="1SPE-TEST-DIAG",
            sous_type="diagnostic",
            status="approved",
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    manual = inventory["manuals"]["1SPE"]
    report = inventory_module._render_inventory_markdown(inventory)

    assert manual["object_count"] == 1
    assert manual["content_file_count"] == 1
    assert sum(manual["totals"].values()) == 2
    row = next(line for line in report.splitlines() if "| 1SPE |" in line)
    assert "| 1 | — |" in row
    assert "| 2 | — |" not in row


def test_human_reports_use_real_anomaly_fields_and_keep_etat_bounded(
    tmp_path: Path, inventory_module
) -> None:
    inventory = _minimal_inventory(tmp_path, inventory_module)
    inventory["anomalies"]["broken_meta_references"] = [
        {
            "id": None,
            "detail": None,
            "code": None,
            "source": "chapitres/source.tex",
            "champ": "corrige_tex",
            "cible": "chapitres/correction.tex",
            "raison": "chemin absent",
        }
    ]
    inventory["deliverable_matrix"] = inventory_module.build_deliverable_matrix(
        inventory
    )

    reports = {
        "inventory": inventory_module._render_inventory_markdown(inventory),
        "audit": inventory_module._render_audit_consolide(inventory),
        "etat": inventory_module._render_etat_collection(inventory),
    }

    for report in reports.values():
        assert "id=—, detail=—, code=—" not in report
        assert "=—" not in report
    assert "source=chapitres/source.tex" in reports["inventory"]
    assert "champ=corrige_tex" in reports["audit"]
    assert len(reports["etat"].splitlines()) < 250
    for target in (
        "audit/INVENTAIRE_COLLECTION.json",
        "audit/ECARTS_ET_CONTRADICTIONS.yaml",
        "audit/MATRICE_LIVRABLES.yaml",
    ):
        assert target in reports["etat"]


def test_gate_result_contract_exposes_exact_dimensions_and_sorted_reasons(
    inventory_module,
) -> None:
    assert (
        inventory_module.GATE_USAGE_CODE,
        inventory_module.GATE_CHECK_CODE,
        inventory_module.GATE_CLEAN_CODE,
        inventory_module.GATE_BASELINE_CODE,
        inventory_module.GATE_VALIDATE_CODE,
        inventory_module.GATE_RELEASE_CODE,
        inventory_module.GATE_BASELINE_UPDATE_CODE,
    ) == (2, 3, 4, 5, 6, 7, 8)
    result = inventory_module._gate_result(
        "example",
        success=False,
        failure_code=7,
        dimensions={"structure": "failed"},
        reasons=["zeta", "alpha"],
    )

    assert result == {
        "blocker_count": 2,
        "dimensions": {
            "execution": "not_covered",
            "mathematics": "not_covered",
            "pedagogy": "not_covered",
            "print": "not_covered",
            "regulation": "not_covered",
            "structure": "failed",
            "visual": "not_covered",
        },
        "exit_code": 7,
        "gate": "example",
        "reasons": ["alpha", "zeta"],
        "success": False,
    }
    assert all(
        status != "passed"
        for dimension, status in result["dimensions"].items()
        if dimension != "structure"
    )


def test_missing_corrections_is_a_structural_publication_blocker(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        f"{base}/exercices/e1.tex": _meta(
            id="1SPE-TEST-EX-001",
            type_objet="exercice",
            status="approved",
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    matrix = inventory["deliverable_matrix"]["manuals"]["1SPE"]

    assert len(inventory["anomalies"]["missing_corrections"]) == 1
    assert "anomalie:missing_corrections" in matrix["structural_blockers"]
    assert matrix["phase0_structural_eligible"] is False
    assert matrix["publication_eligible"] is False


def test_structurally_eligible_manual_stays_unpublishable_without_gate_proofs(
    tmp_path: Path, inventory_module, monkeypatch: pytest.MonkeyPatch
) -> None:
    inventory = _minimal_inventory(tmp_path, inventory_module)
    for values in inventory["anomalies"].values():
        values.clear()
    specifications = deepcopy(inventory_module.DELIVERABLE_SPECS)
    for manual_id, specification in specifications.items():
        specification["target_chapters"] = len(
            inventory["manuals"][manual_id]["chapters"]
        )
    monkeypatch.setattr(inventory_module, "DELIVERABLE_SPECS", specifications)

    matrix = inventory_module.build_deliverable_matrix(inventory)["manuals"]["1SPE"]

    assert matrix["phase0_structural_eligible"] is True
    assert matrix["publication_eligible"] is False


def test_check_gate_reports_drift_without_writing_any_managed_output(
    tmp_path: Path, inventory_module
) -> None:
    _seed_cli_repository(tmp_path)
    _commit_repository(tmp_path, "sources")
    result = inventory_module.build_inventory_artifacts(tmp_path)
    managed = sorted(
        tmp_path / relative
        for relative in result["artifacts"].values()
    )
    drifted = tmp_path / result["artifacts"]["audit"]
    drifted.write_text(drifted.read_text(encoding="utf-8") + "\nDÉRIVE\n", encoding="utf-8")
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in managed}

    completed = _run_inventory_cli(tmp_path, "--check")
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in managed}
    payload = json.loads(completed.stdout)

    assert completed.returncode == 3
    assert payload["gate"] == "check"
    assert payload["exit_code"] == 3
    assert payload["success"] is False
    assert payload["reasons"] == sorted(payload["reasons"])
    assert before == after


@pytest.mark.parametrize("source_date_epoch", [None, "date-invalide"])
def test_two_normal_generations_are_stable_without_a_valid_source_date_epoch(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    source_date_epoch: str | None,
) -> None:
    _seed_cli_repository(tmp_path)
    _commit_repository(tmp_path, "sources")
    if source_date_epoch is None:
        monkeypatch.delenv("SOURCE_DATE_EPOCH", raising=False)
    else:
        monkeypatch.setenv("SOURCE_DATE_EPOCH", source_date_epoch)

    first = inventory_module.build_inventory_artifacts(tmp_path)
    paths = _managed_output_paths(tmp_path, first)
    first_bytes = {path: path.read_bytes() for path in paths}
    first_provenance = json.loads(
        (tmp_path / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8")
    )["provenance"]
    time.sleep(1.1)
    inventory_module.build_inventory_artifacts(tmp_path)
    second_bytes = {path: path.read_bytes() for path in paths}
    second_provenance = json.loads(
        (tmp_path / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8")
    )["provenance"]

    assert first_bytes == second_bytes
    assert first_provenance == second_provenance
    assert first_provenance["dirty"] is False
    assert first_provenance["modified_tracked"] == []
    assert first_provenance["untracked_relevant"] == []


def test_complete_generations_in_two_isolated_git_roots_are_byte_identical(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    roots = (tmp_path / "first", tmp_path / "second")
    commit_environment = os.environ.copy()
    commit_environment.update(
        {
            "GIT_AUTHOR_DATE": "2026-07-29T12:00:00+00:00",
            "GIT_COMMITTER_DATE": "2026-07-29T12:00:00+00:00",
        }
    )
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1785326400")
    heads: list[str] = []
    generated: list[dict[str, bytes]] = []
    for root in roots:
        _seed_cli_repository(root)
        subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "-c",
                "user.name=Phase 0.1 Tests",
                "-c",
                "user.email=phase01-tests@example.invalid",
                "commit",
                "-qm",
                "sources identiques",
            ],
            check=True,
            env=commit_environment,
        )
        heads.append(
            subprocess.run(
                ["git", "-C", str(root), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
        result = inventory_module.build_inventory_artifacts(root)
        generated.append(
            {
                relative: (root / relative).read_bytes()
                for relative in sorted(result["artifacts"].values())
            }
        )

    assert heads[0] == heads[1]
    assert generated[0] == generated[1]


def test_artifact_generation_rejects_a_non_git_root_explicitly(
    tmp_path: Path,
    inventory_module,
) -> None:
    with pytest.raises(
        inventory_module.InventoryError, match="Git provenance unavailable"
    ):
        inventory_module.build_inventory_artifacts(tmp_path)


@pytest.mark.parametrize("failed_git_command", ["status", "ls-files"])
def test_artifact_generation_rejects_git_command_failure(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    failed_git_command: str,
) -> None:
    _seed_cli_repository(tmp_path)
    _commit_repository(tmp_path, "sources")
    original_run = inventory_module.subprocess.run

    def fail_git_status(command: list[str], *args: object, **kwargs: object):
        if (
            command[:3] == ["git", "-C", str(tmp_path)]
            and failed_git_command in command
        ):
            raise subprocess.CalledProcessError(128, command)
        return original_run(command, *args, **kwargs)

    monkeypatch.setattr(inventory_module.subprocess, "run", fail_git_status)

    with pytest.raises(
        inventory_module.InventoryError, match="Git provenance unavailable"
    ):
        inventory_module.build_inventory_artifacts(tmp_path)


def test_unborn_in_memory_inventory_marks_git_provenance_unavailable(
    tmp_path: Path,
    inventory_module,
) -> None:
    inventory = _minimal_inventory(tmp_path, inventory_module)
    provenance = inventory["provenance"]

    assert provenance["git_available"] is False
    assert provenance["dirty"] is None
    assert provenance["head_sha"] is None
    assert provenance["branch"] is None
    assert provenance["generated_at_utc"] is None
    assert provenance["errors"]


def test_generation_uses_valid_source_date_epoch_for_provenance(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_cli_repository(tmp_path)
    _commit_repository(tmp_path, "sources")
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1700000000")

    inventory_module.build_inventory_artifacts(tmp_path)
    provenance = json.loads(
        (tmp_path / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8")
    )["provenance"]

    assert provenance["generated_at_utc"] == "2023-11-14T22:13:20Z"


def test_now_utc_is_timezone_aware_without_deprecation_warning(
    inventory_module,
) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        timestamp = inventory_module._now_utc()

    assert timestamp.endswith("Z")
    assert "+00:00" not in timestamp


def test_git_status_preserves_unicode_spaces_and_both_rename_paths(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)
    old_path = "NSI/chapitres/1NSI-TEST/cours/ancien fichier é.tex"
    new_path = "NSI/chapitres/1NSI-TEST/cours/nouveau → fichier.tex"
    untracked_path = "NSI/chapitres/1NSI-TEST/cours/brouillon été.tex"
    _write(tmp_path / old_path, _meta(id="1NSI-TEST-ANCIEN"))
    _track(tmp_path, old_path)
    _commit_repository(tmp_path, "source Unicode")
    subprocess.run(
        ["git", "-C", str(tmp_path), "mv", "--", old_path, new_path],
        check=True,
    )
    _write(tmp_path / untracked_path, _meta(id="1NSI-TEST-BROUILLON"))

    status = inventory_module._git_status(tmp_path)

    assert inventory_module._git_modified_tracked(
        tmp_path, status=status
    ) == sorted([old_path, new_path])
    assert inventory_module._git_untracked(
        tmp_path, status=status
    ) == [untracked_path]


def test_tool_versions_come_from_each_real_executable(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)

    versions = inventory_module._file_version_signature(tmp_path)

    expected_commands = {
        "git": ["git", "--version"],
        "latexmk": ["latexmk", "-version"],
        "pdfinfo": ["pdfinfo", "-v"],
        "python": [sys.executable, "--version"],
        "texlive": ["pdflatex", "--version"],
    }
    expected: dict[str, str] = {}
    for name, command in expected_commands.items():
        executable = (
            command[0]
            if Path(command[0]).is_absolute()
            else shutil.which(command[0])
        )
        if executable is None:
            expected[name] = "unavailable"
            continue
        completed = subprocess.run(
            [str(executable), *command[1:]],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        expected[name] = completed.stdout.splitlines()[0].strip()

    assert versions == expected
    assert not isinstance(versions["git"], bool)


def test_tool_version_routing_uses_each_expected_command(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    routed: list[list[str]] = []

    def resolve(executable: str) -> str:
        return f"/resolved/{executable}"

    def run(command: list[str], **_kwargs: object):
        routed.append(command)
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=f"version for {Path(command[0]).name}\n",
        )

    monkeypatch.setattr(inventory_module.shutil, "which", resolve)
    monkeypatch.setattr(inventory_module.subprocess, "run", run)

    versions = inventory_module._file_version_signature(tmp_path)

    assert routed == [
        ["/resolved/git", "--version"],
        ["/resolved/latexmk", "-version"],
        ["/resolved/pdfinfo", "-v"],
        [sys.executable, "--version"],
        ["/resolved/pdflatex", "--version"],
    ]
    assert set(versions) == {"git", "latexmk", "pdfinfo", "python", "texlive"}


def test_ensure_clean_tree_validates_mode_and_head_on_a_clean_tree(
    tmp_path: Path,
    inventory_module,
) -> None:
    _init_repository(tmp_path)

    with pytest.raises(inventory_module.InventoryError, match="unknown clean mode"):
        inventory_module._ensure_clean_tree(tmp_path, mode="inconnu")
    with pytest.raises(inventory_module.InventoryError, match="resolved HEAD"):
        inventory_module._ensure_clean_tree(tmp_path, mode="head")

    _commit_repository(tmp_path)
    head = _commit_repository(tmp_path, "second commit")
    (tmp_path / ".git/HEAD").write_text(f"{head}\n", encoding="utf-8")
    with pytest.raises(inventory_module.InventoryError, match="attached branch"):
        inventory_module._ensure_clean_tree(tmp_path, mode="head")


@pytest.mark.parametrize(
    ("audit_directory", "etat_path"),
    [
        ("/tmp/nexus-audit-absolu", "ETAT_COLLECTION.md"),
        ("../audit-hors-depot", "ETAT_COLLECTION.md"),
    ],
)
def test_generation_rejects_absolute_and_parent_output_paths(
    tmp_path: Path,
    inventory_module,
    audit_directory: str,
    etat_path: str,
) -> None:
    _seed_cli_repository(tmp_path)

    with pytest.raises(inventory_module.InventoryError, match="outside repository"):
        inventory_module.build_inventory_artifacts(
            tmp_path,
            audit_directory=audit_directory,
            etat_path=etat_path,
        )


def test_generation_rejects_symlink_escape_before_any_write(
    tmp_path: Path,
    inventory_module,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    outside.mkdir()
    _seed_cli_repository(repository)
    (repository / "evidence").symlink_to(outside, target_is_directory=True)

    with pytest.raises(inventory_module.InventoryError, match="symlink escape"):
        inventory_module.build_inventory_artifacts(
            repository,
            audit_directory="evidence/audit",
            etat_path="ETAT_COLLECTION.md",
        )

    assert list(outside.iterdir()) == []


def test_generation_lock_covers_render_compare_clean_and_apply(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_cli_repository(tmp_path)
    _commit_repository(tmp_path, "sources")
    active = False
    observed: list[tuple[str, bool]] = []

    @contextmanager
    def observed_lock(_root: Path):
        nonlocal active
        active = True
        try:
            yield
        finally:
            active = False

    original_render = inventory_module._render_managed_artifacts
    original_compare = inventory_module._compare_rendered_artifacts
    original_clean = inventory_module._ensure_clean_tree
    original_apply = inventory_module._apply_atomic_payloads

    def render(*args: object, **kwargs: object):
        observed.append(("render", active))
        return original_render(*args, **kwargs)

    def compare(*args: object, **kwargs: object):
        observed.append(("compare", active))
        return original_compare(*args, **kwargs)

    def clean(*args: object, **kwargs: object):
        observed.append(("clean", active))
        return original_clean(*args, **kwargs)

    def apply(*args: object, **kwargs: object):
        observed.append(("apply", active))
        return original_apply(*args, **kwargs)

    monkeypatch.setattr(inventory_module, "_lock_generation", observed_lock)
    monkeypatch.setattr(inventory_module, "_render_managed_artifacts", render)
    monkeypatch.setattr(inventory_module, "_compare_rendered_artifacts", compare)
    monkeypatch.setattr(inventory_module, "_ensure_clean_tree", clean)
    monkeypatch.setattr(inventory_module, "_apply_atomic_payloads", apply)

    inventory_module.build_inventory_artifacts(tmp_path)

    transactional = [
        state
        for operation, state in observed
        if operation in {"render", "compare", "apply"}
    ]
    assert transactional == [True, True, True]
    assert observed[-2:] == [("clean", True), ("apply", True)]


def test_generation_with_observed_manifest_accepts_only_its_owned_lock(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_cli_repository(tmp_path)
    observed_manifest = tmp_path / inventory_module.BUILD_MANIFEST_FILE
    _write(
        observed_manifest,
        json.dumps(
            {
                "builds": [
                    {"manual": "1SPE", "variant": "professeur"},
                ]
            }
        ),
    )
    _track(tmp_path, inventory_module.BUILD_MANIFEST_FILE)
    _commit_repository(tmp_path, "sources and observed manifest")
    observed_build = {"manual": "1SPE", "variant": "professeur"}
    received_lock_identities: list[dict[str, tuple[int, int]]] = []

    def load_observed(
        root: Path,
        *,
        owned_generation_lock: dict[str, tuple[int, int]] | None = None,
        **_kwargs: object,
    ) -> list[dict[str, str]]:
        assert json.loads(observed_manifest.read_text(encoding="utf-8"))["builds"]
        assert owned_generation_lock is not None
        received_lock_identities.append(owned_generation_lock)
        assert inventory_module._observed_git_state(root)[2] is True
        assert inventory_module._observed_git_state(
            root,
            allowed_generation_paths=owned_generation_lock,
        )[2] is False
        return [observed_build]

    monkeypatch.setattr(
        inventory_module,
        "_load_observed_build_manifest",
        load_observed,
    )
    monkeypatch.setattr(
        inventory_module,
        "_render_managed_artifacts",
        lambda *_args, **_kwargs: {},
    )
    monkeypatch.setattr(
        inventory_module,
        "_compare_rendered_artifacts",
        lambda *_args, **_kwargs: [],
    )
    monkeypatch.setattr(
        inventory_module,
        "_apply_atomic_payloads",
        lambda *_args, **_kwargs: None,
    )

    result = inventory_module.build_inventory_artifacts(tmp_path)

    assert result["inventory"]["observed_builds"] == [observed_build]
    assert len(received_lock_identities) == 1
    assert set(received_lock_identities[0]) == {
        inventory_module.GENERIC_LOCK_FILE,
    }
    assert all(
        value > 0
        for value in received_lock_identities[0][
            inventory_module.GENERIC_LOCK_FILE
        ]
    )
    assert "owned_generation_lock" not in inspect.signature(
        inventory_module.build_inventory
    ).parameters
    assert not (tmp_path / inventory_module.GENERIC_LOCK_FILE).exists()


@pytest.mark.parametrize(
    "mutation",
    ["arbitrary", "unowned", "substituted", "other-dirty"],
)
def test_observed_git_state_never_hides_unowned_generation_paths(
    tmp_path: Path,
    inventory_module,
    mutation: str,
) -> None:
    _init_repository(tmp_path)
    _commit_repository(tmp_path, "clean repository")
    lock_path = tmp_path / inventory_module.GENERIC_LOCK_FILE

    if mutation == "arbitrary":
        arbitrary = tmp_path / "notes-utilisateur.txt"
        _write(arbitrary, "WIP utilisateur\n")
        metadata = arbitrary.stat(follow_symlinks=False)
        assert inventory_module._observed_git_state(
            tmp_path,
            allowed_generation_paths={
                arbitrary.name: (metadata.st_dev, metadata.st_ino),
            },
        )[2] is True
        return

    if mutation == "unowned":
        _write(lock_path, "foreign lock\n")
        owned_generation_lock = {
            inventory_module.GENERIC_LOCK_FILE: (-1, -1),
        }
        assert inventory_module._observed_git_state(
            tmp_path,
            allowed_generation_paths=owned_generation_lock,
        )[2] is True
        return

    with inventory_module._lock_generation(tmp_path) as owned_generation_lock:
        if mutation == "substituted":
            lock_path.unlink()
            _write(lock_path, "replacement lock\n")
        else:
            _write(tmp_path / "notes-utilisateur.txt", "WIP utilisateur\n")

        assert inventory_module._observed_git_state(
            tmp_path,
            allowed_generation_paths=owned_generation_lock,
        )[2] is True


def test_live_generation_lock_times_out_without_removing_owner_record(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(inventory_module, "LOCK_TIMEOUT_SECONDS", 0.05)
    lock_path = tmp_path / inventory_module.GENERIC_LOCK_FILE
    process = subprocess.Popen(
        [
            sys.executable,
            "-c",
            (
                "import importlib.util,time;"
                f"spec=importlib.util.spec_from_file_location('inventory_collection',{str(SCRIPT)!r});"
                "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
                f"from pathlib import Path;"
                f"root=Path({str(tmp_path)!r});"
                "ctx=m._lock_generation(root);ctx.__enter__();"
                "print('LOCKED',flush=True);time.sleep(0.5);ctx.__exit__(None,None,None)"
            ),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        assert process.stdout is not None
        assert process.stdout.readline().strip() == "LOCKED"
        owner_record = lock_path.read_bytes()

        with pytest.raises(
            inventory_module.InventoryError, match="generation lock timeout"
        ):
            with inventory_module._lock_generation(tmp_path):
                pytest.fail("un verrou vivant ne doit jamais être repris")

        assert lock_path.read_bytes() == owner_record
        assert process.poll() is None
    finally:
        process.communicate(timeout=2)


def test_stale_dead_generation_lock_is_quarantined_once(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(inventory_module, "LOCK_TIMEOUT_SECONDS", 0.1)
    monkeypatch.setattr(
        inventory_module, "LOCK_STALE_SECONDS", 0.01, raising=False
    )
    lock_path = tmp_path / inventory_module.GENERIC_LOCK_FILE
    stale_record = {
        "created_at_utc": "2000-01-01T00:00:00Z",
        "pid": 999_999_999,
        "process_start_token": "dead-process",
    }
    lock_path.write_text(
        json.dumps(stale_record, sort_keys=True),
        encoding="utf-8",
    )

    with inventory_module._lock_generation(tmp_path):
        current = json.loads(lock_path.read_text(encoding="utf-8"))
        assert current["pid"] == os.getpid()
        assert current["process_start_token"]

    assert not lock_path.exists()
    quarantines = list(
        tmp_path.glob(f"{inventory_module.GENERIC_LOCK_FILE}.stale.*")
    )
    assert len(quarantines) == 1
    assert json.loads(quarantines[0].read_text(encoding="utf-8")) == stale_record


def test_stale_snapshot_never_unlinks_a_replacement_lock_owner(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(inventory_module, "LOCK_TIMEOUT_SECONDS", 0.03)
    lock_path = tmp_path / inventory_module.GENERIC_LOCK_FILE
    stale_record = {
        "created_at_utc": "2000-01-01T00:00:00Z",
        "pid": 999_999_999,
        "process_start_token": "dead-process",
    }
    lock_path.write_text(json.dumps(stale_record), encoding="utf-8")
    stale_read = threading.Event()
    resume_reclaimer = threading.Event()
    result: list[bool] = []
    failures: list[BaseException] = []
    original_owner_is_live = inventory_module._lock_owner_is_live

    def pause_after_stale_read(record: dict[str, object]) -> bool:
        if record.get("process_start_token") == "dead-process":
            stale_read.set()
            if not resume_reclaimer.wait(timeout=2):
                raise AssertionError("barrière de reprise stale expirée")
            return False
        return original_owner_is_live(record)

    def reclaim_snapshot() -> None:
        try:
            result.append(inventory_module._quarantine_stale_lock(lock_path))
        except BaseException as exc:
            failures.append(exc)

    monkeypatch.setattr(
        inventory_module,
        "_lock_owner_is_live",
        pause_after_stale_read,
    )
    reclaimer = threading.Thread(target=reclaim_snapshot)
    reclaimer.start()
    assert stale_read.wait(timeout=2)

    lock_path.unlink()
    with inventory_module._lock_generation(tmp_path):
        replacement_stat = lock_path.stat(follow_symlinks=False)
        resume_reclaimer.set()
        reclaimer.join(timeout=2)
        assert not reclaimer.is_alive()
        assert failures == []
        assert result == [False]
        current_stat = lock_path.stat(follow_symlinks=False)
        assert (current_stat.st_dev, current_stat.st_ino) == (
            replacement_stat.st_dev,
            replacement_stat.st_ino,
        )
        with pytest.raises(
            inventory_module.InventoryError, match="generation lock timeout"
        ):
            with inventory_module._lock_generation(tmp_path):
                pytest.fail("le verrou de remplacement doit rester exclusif")


@pytest.mark.parametrize("lock_kind", ["symlink", "directory"])
def test_stale_reclaimer_refuses_symlink_and_nonregular_lock(
    tmp_path: Path,
    inventory_module,
    lock_kind: str,
) -> None:
    lock_path = tmp_path / inventory_module.GENERIC_LOCK_FILE
    if lock_kind == "symlink":
        target = tmp_path / "stale-record.json"
        target.write_text(
            json.dumps(
                {
                    "created_at_utc": "2000-01-01T00:00:00Z",
                    "pid": 999_999_999,
                    "process_start_token": "dead-process",
                }
            ),
            encoding="utf-8",
        )
        lock_path.symlink_to(target)
    else:
        lock_path.mkdir()

    assert inventory_module._quarantine_stale_lock(lock_path) is False
    assert lock_path.exists()
    if lock_kind == "symlink":
        assert lock_path.is_symlink()


def test_stale_reclaimer_is_disabled_without_fcntl(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lock_path = tmp_path / inventory_module.GENERIC_LOCK_FILE
    lock_path.write_text(
        json.dumps(
            {
                "created_at_utc": "2000-01-01T00:00:00Z",
                "pid": 999_999_999,
                "process_start_token": "dead-process",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(inventory_module, "fcntl", None, raising=False)

    assert inventory_module._quarantine_stale_lock(lock_path) is False
    assert lock_path.exists()


@pytest.mark.parametrize(
    "record",
    [
        "{pas-json",
        json.dumps(
            {
                "created_at_utc": "2999-01-01T00:00:00Z",
                "pid": 999_999_999,
                "process_start_token": "dead-process",
            }
        ),
    ],
)
def test_malformed_or_young_generation_lock_times_out_unchanged(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
    record: str,
) -> None:
    monkeypatch.setattr(inventory_module, "LOCK_TIMEOUT_SECONDS", 0.03)
    monkeypatch.setattr(
        inventory_module, "LOCK_STALE_SECONDS", 20, raising=False
    )
    lock_path = tmp_path / inventory_module.GENERIC_LOCK_FILE
    lock_path.write_text(record, encoding="utf-8")

    with pytest.raises(
        inventory_module.InventoryError, match="generation lock timeout"
    ):
        with inventory_module._lock_generation(tmp_path):
            pytest.fail("un verrou non récupérable ne doit jamais être remplacé")

    assert lock_path.read_text(encoding="utf-8") == record


def test_atomic_batch_failure_restores_every_target_byte_for_byte(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = tmp_path / "audit/existing.txt"
    new_target = tmp_path / "audit/new.txt"
    _write(existing, "contenu historique\n")
    before = hashlib.sha256(existing.read_bytes()).hexdigest()
    original_replace = inventory_module.os.replace
    replacements = 0

    def fail_second_replace(
        source: Path | str,
        target: Path | str,
        **kwargs: object,
    ) -> None:
        nonlocal replacements
        replacements += 1
        if replacements == 2:
            raise OSError("injection échec remplacement 2")
        original_replace(source, target, **kwargs)

    monkeypatch.setattr(inventory_module.os, "replace", fail_second_replace)

    with pytest.raises(
        inventory_module.InventoryError, match="transaction rolled back"
    ):
        inventory_module._apply_atomic_payloads(
            tmp_path,
            {
                Path("audit/existing.txt"): "nouveau contenu\n",
                Path("audit/new.txt"): "nouveau fichier\n",
            },
        )

    assert hashlib.sha256(existing.read_bytes()).hexdigest() == before
    assert not new_target.exists()


def test_transaction_rejects_stage_substituted_before_identity_validation(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    first = repository / "audit/a-first.txt"
    second = repository / "audit/z-second.txt"
    sentinel = outside / "sentinel-wip.txt"
    _write(first, "premier historique\n")
    _write(second, "second historique\n")
    _write(sentinel, "WIP concurrent à préserver\n")
    before = {
        first: first.read_bytes(),
        second: second.read_bytes(),
    }
    sentinel_before = sentinel.read_bytes()
    original_write_entry = inventory_module._write_transaction_entry
    substituted = False
    callback_called = False

    def substitute_stage_after_staging(
        directory_fd: int,
        name: str,
        payload: bytes,
    ) -> os.stat_result:
        nonlocal substituted
        identity = original_write_entry(directory_fd, name, payload)
        if name == "journal-ready" and not substituted:
            os.unlink("stage-00000000", dir_fd=directory_fd)
            os.link(
                sentinel,
                "stage-00000000",
                dst_dir_fd=directory_fd,
                follow_symlinks=False,
            )
            substituted = True
        return identity

    def observe_validation(
        _owned_entries: dict[str, tuple[int, int]],
    ) -> None:
        nonlocal callback_called
        callback_called = True

    monkeypatch.setattr(
        inventory_module,
        "_write_transaction_entry",
        substitute_stage_after_staging,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match=(
            "transaction rolled back.*transaction validation entry identity "
            "changed: stage-00000000"
        ),
    ) as captured:
        inventory_module._apply_atomic_payloads(
            repository,
            {
                Path("audit/a-first.txt"): "premier nouveau\n",
                Path("audit/z-second.txt"): "second nouveau\n",
            },
            validate_before_apply=observe_validation,
        )

    assert substituted is True
    assert callback_called is False
    assert {path: path.read_bytes() for path in before} == before
    assert sentinel.read_bytes() == sentinel_before
    assert sentinel.stat().st_nlink == 2
    transaction_directories = list(
        repository.glob(".inventory-collection-apply-*")
    )
    assert len(transaction_directories) == 1
    retained_stage = transaction_directories[0] / "stage-00000000"
    assert retained_stage.read_bytes() == sentinel_before
    assert retained_stage.stat().st_ino == sentinel.stat().st_ino
    assert any(
        "preserved foreign transaction entry stage-00000000" in note
        for note in getattr(captured.value, "__notes__", ())
    )


def test_cleanup_preserves_unique_wip_substituted_for_stage(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    first = repository / "audit/a-first.txt"
    second = repository / "audit/z-second.txt"
    wip = outside / "unique-wip.txt"
    _write(first, "premier historique\n")
    _write(second, "second historique\n")
    _write(wip, "WIP unique à récupérer\n")
    before = {
        first: first.read_bytes(),
        second: second.read_bytes(),
    }
    wip_before = wip.read_bytes()
    original_write_entry = inventory_module._write_transaction_entry
    substituted = False
    callback_called = False

    def move_wip_over_stage(
        directory_fd: int,
        name: str,
        payload: bytes,
    ) -> os.stat_result:
        nonlocal substituted
        identity = original_write_entry(directory_fd, name, payload)
        if name == "journal-ready" and not substituted:
            os.unlink("stage-00000000", dir_fd=directory_fd)
            os.rename(
                wip,
                "stage-00000000",
                dst_dir_fd=directory_fd,
            )
            substituted = True
        return identity

    def observe_validation(
        _owned_entries: dict[str, tuple[int, int]],
    ) -> None:
        nonlocal callback_called
        callback_called = True

    monkeypatch.setattr(
        inventory_module,
        "_write_transaction_entry",
        move_wip_over_stage,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match=(
            "transaction rolled back.*transaction validation entry identity "
            "changed: stage-00000000"
        ),
    ) as captured:
        inventory_module._apply_atomic_payloads(
            repository,
            {
                Path("audit/a-first.txt"): "premier nouveau\n",
                Path("audit/z-second.txt"): "second nouveau\n",
            },
            validate_before_apply=observe_validation,
        )

    assert substituted is True
    assert callback_called is False
    assert {path: path.read_bytes() for path in before} == before
    assert not wip.exists()
    transaction_directories = list(
        repository.glob(".inventory-collection-apply-*")
    )
    assert len(transaction_directories) == 1
    retained_wip = transaction_directories[0] / "stage-00000000"
    assert retained_wip.read_bytes() == wip_before
    assert any(
        "preserved foreign transaction entry stage-00000000" in note
        for note in getattr(captured.value, "__notes__", ())
    )


def test_rollback_never_uses_substituted_backup(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    first = repository / "audit/a-first.txt"
    second = repository / "audit/z-second.txt"
    wip = outside / "foreign-backup.txt"
    _write(first, "premier historique\n")
    _write(second, "second historique\n")
    _write(wip, "WIP étranger au rollback\n")
    before = {
        first: first.read_bytes(),
        second: second.read_bytes(),
    }
    wip_before = wip.read_bytes()
    original_write_entry = inventory_module._write_transaction_entry
    original_replace = inventory_module.os.replace
    substituted = False

    def move_wip_over_backup(
        directory_fd: int,
        name: str,
        payload: bytes,
    ) -> os.stat_result:
        nonlocal substituted
        identity = original_write_entry(directory_fd, name, payload)
        if name == "journal-ready" and not substituted:
            os.unlink("backup-00000000", dir_fd=directory_fd)
            os.rename(
                wip,
                "backup-00000000",
                dst_dir_fd=directory_fd,
            )
            substituted = True
        return identity

    def fail_second_forward_replace(
        source: Path | str,
        target: Path | str,
        **kwargs: object,
    ) -> None:
        if str(source) == "stage-00000001":
            raise OSError("injection second forward replace")
        original_replace(source, target, **kwargs)

    monkeypatch.setattr(
        inventory_module,
        "_write_transaction_entry",
        move_wip_over_backup,
    )
    monkeypatch.setattr(
        inventory_module.os,
        "replace",
        fail_second_forward_replace,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="transaction rolled back.*injection second forward replace",
    ) as captured:
        inventory_module._apply_atomic_payloads(
            repository,
            {
                Path("audit/a-first.txt"): "premier nouveau\n",
                Path("audit/z-second.txt"): "second nouveau\n",
            },
        )

    assert substituted is True
    assert {path: path.read_bytes() for path in before} == before
    assert not wip.exists()
    transaction_directories = list(
        repository.glob(".inventory-collection-apply-*")
    )
    assert len(transaction_directories) == 1
    retained_wip = transaction_directories[0] / "backup-00000000"
    assert retained_wip.read_bytes() == wip_before
    assert any(
        "preserved foreign transaction entry backup-00000000" in note
        for note in getattr(captured.value, "__notes__", ())
    )
    assert list(repository.glob(".inventory-collection-recovery-*")) == []


def test_rollback_uses_authenticated_payload_after_backup_toctou_substitution(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    first = repository / "audit/a-first.txt"
    second = repository / "audit/z-second.txt"
    wip = outside / "foreign-backup.txt"
    _write(first, "premier historique\n")
    _write(second, "second historique\n")
    _write(wip, "WIP étranger au rollback\n")
    before = {
        first: first.read_bytes(),
        second: second.read_bytes(),
    }
    wip_before = wip.read_bytes()
    original_write_entry = inventory_module._write_transaction_entry
    original_replace = inventory_module.os.replace
    original_exchange = inventory_module._exchange_directory_entries
    transaction_fd: int | None = None
    substituted = False

    def capture_transaction_fd(
        directory_fd: int,
        name: str,
        payload: bytes,
    ) -> os.stat_result:
        nonlocal transaction_fd
        identity = original_write_entry(directory_fd, name, payload)
        if name == "journal-ready":
            transaction_fd = directory_fd
        return identity

    def substitute_backup_during_restore(
        source: Path | str,
        target: Path | str,
        **kwargs: object,
    ) -> None:
        nonlocal substituted
        if str(source) == "stage-00000001":
            raise OSError("injection second forward replace")
        original_replace(source, target, **kwargs)

    def substitute_backup_during_exchange(
        source_fd: int,
        source_name: str,
        destination_fd: int,
        destination_name: str,
    ) -> None:
        nonlocal substituted
        if (
            source_name.startswith(".inventory-collection-rollback-")
            and not substituted
        ):
            assert transaction_fd is not None
            os.unlink("backup-00000000", dir_fd=transaction_fd)
            os.rename(
                wip,
                "backup-00000000",
                dst_dir_fd=transaction_fd,
            )
            substituted = True
        original_exchange(
            source_fd,
            source_name,
            destination_fd,
            destination_name,
        )

    monkeypatch.setattr(
        inventory_module,
        "_write_transaction_entry",
        capture_transaction_fd,
    )
    monkeypatch.setattr(
        inventory_module.os,
        "replace",
        substitute_backup_during_restore,
    )
    monkeypatch.setattr(
        inventory_module,
        "_exchange_directory_entries",
        substitute_backup_during_exchange,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="transaction rolled back.*injection second forward replace",
    ) as captured:
        inventory_module._apply_atomic_payloads(
            repository,
            {
                Path("audit/a-first.txt"): "premier nouveau\n",
                Path("audit/z-second.txt"): "second nouveau\n",
            },
        )

    assert substituted is True
    assert {path: path.read_bytes() for path in before} == before
    assert not wip.exists()
    transaction_directories = list(
        repository.glob(".inventory-collection-apply-*")
    )
    assert len(transaction_directories) == 1
    retained_wip = transaction_directories[0] / "backup-00000000"
    assert retained_wip.read_bytes() == wip_before
    assert any(
        "preserved foreign transaction entry backup-00000000" in note
        for note in getattr(captured.value, "__notes__", ())
    )
    assert list(repository.glob(".inventory-collection-recovery-*")) == []


def test_rollback_quarantines_substituted_restore_entry_and_retries(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    first = repository / "audit/a-first.txt"
    second = repository / "audit/z-second.txt"
    wip = outside / "foreign-rollback.txt"
    _write(first, "premier historique\n")
    _write(second, "second historique\n")
    _write(wip, "WIP substitué au rollback\n")
    before = {
        first: first.read_bytes(),
        second: second.read_bytes(),
    }
    wip_before = wip.read_bytes()
    original_replace = inventory_module.os.replace
    original_exchange = inventory_module._exchange_directory_entries
    substituted = False

    def substitute_restore_entry(
        source: Path | str,
        target: Path | str,
        **kwargs: object,
    ) -> None:
        nonlocal substituted
        if str(source) == "stage-00000001":
            raise OSError("injection second forward replace")
        original_replace(source, target, **kwargs)

    def substitute_restore_exchange(
        source_fd: int,
        source_name: str,
        destination_fd: int,
        destination_name: str,
    ) -> None:
        nonlocal substituted
        if source_name.startswith(".inventory-collection-rollback-") and not substituted:
            os.unlink(source_name, dir_fd=source_fd)
            os.rename(wip, source_name, dst_dir_fd=source_fd)
            substituted = True
        original_exchange(
            source_fd,
            source_name,
            destination_fd,
            destination_name,
        )

    monkeypatch.setattr(
        inventory_module.os,
        "replace",
        substitute_restore_entry,
    )
    monkeypatch.setattr(
        inventory_module,
        "_exchange_directory_entries",
        substitute_restore_exchange,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="transaction rolled back.*injection second forward replace",
    ) as captured:
        inventory_module._apply_atomic_payloads(
            repository,
            {
                Path("audit/a-first.txt"): "premier nouveau\n",
                Path("audit/z-second.txt"): "second nouveau\n",
            },
        )

    assert substituted is True
    assert {path: path.read_bytes() for path in before} == before
    assert not wip.exists()
    quarantined = list(
        (repository / "audit").glob(
            ".inventory-collection-preserved-rollback-*.wip"
        )
    )
    assert len(quarantined) == 1
    assert quarantined[0].read_bytes() == wip_before
    assert "preserved rollback entry" in str(captured.value)
    assert list(repository.glob(".inventory-collection-recovery-*")) == []


def test_persistent_restore_substitution_fails_safe_with_recovery_payload(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    first = repository / "audit/a-first.txt"
    second = repository / "audit/z-second.txt"
    _write(first, "premier historique\n")
    _write(second, "second historique\n")
    historical = first.read_bytes()
    foreign_payloads = [
        f"WIP persistant {index}\n".encode()
        for index in range(3)
    ]
    foreign_paths = [
        outside / f"foreign-rollback-{index}.txt"
        for index in range(3)
    ]
    for path, payload in zip(foreign_paths, foreign_payloads, strict=True):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    original_replace = inventory_module.os.replace
    original_exchange = inventory_module._exchange_directory_entries
    substitutions = 0

    def substitute_every_restore_entry(
        source: Path | str,
        target: Path | str,
        **kwargs: object,
    ) -> None:
        nonlocal substitutions
        if str(source) == "stage-00000001":
            raise OSError("injection second forward replace")
        original_replace(source, target, **kwargs)

    def substitute_every_restore_exchange(
        source_fd: int,
        source_name: str,
        destination_fd: int,
        destination_name: str,
    ) -> None:
        nonlocal substitutions
        if source_name.startswith(".inventory-collection-rollback-"):
            os.unlink(source_name, dir_fd=source_fd)
            os.rename(
                foreign_paths[substitutions],
                source_name,
                dst_dir_fd=source_fd,
            )
            substitutions += 1
        original_exchange(
            source_fd,
            source_name,
            destination_fd,
            destination_name,
        )

    monkeypatch.setattr(
        inventory_module.os,
        "replace",
        substitute_every_restore_entry,
    )
    monkeypatch.setattr(
        inventory_module,
        "_exchange_directory_entries",
        substitute_every_restore_exchange,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="transaction rolled back incompletely",
    ) as captured:
        inventory_module._apply_atomic_payloads(
            repository,
            {
                Path("audit/a-first.txt"): "premier nouveau\n",
                Path("audit/z-second.txt"): "second nouveau\n",
            },
    )

    assert substitutions == 3
    assert first.read_bytes() == b""
    assert first.is_file()
    assert second.read_text(encoding="utf-8") == "second historique\n"
    quarantined = list(
        (repository / "audit").glob(
            ".inventory-collection-preserved-rollback-*.wip"
        )
    )
    assert sorted(path.read_bytes() for path in quarantined) == sorted(
        foreign_payloads
    )
    recovery = list(
        repository.glob(".inventory-collection-recovery-*.bak")
    )
    assert len(recovery) == 1
    assert recovery[0].read_bytes() == historical
    assert (
        str(captured.value).count(
            ".inventory-collection-preserved-rollback-"
        )
        == 3
    )


def test_rollback_cleanup_never_unlinks_a_substituted_wip(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    first = repository / "audit/a-first.txt"
    second = repository / "audit/z-second.txt"
    wip = outside / "cleanup-wip.txt"
    _write(first, "premier historique\n")
    _write(second, "second historique\n")
    _write(wip, "WIP substitué pendant cleanup\n")
    wip_before = wip.read_bytes()
    original_replace = inventory_module.os.replace
    original_stat = inventory_module.os.stat
    rollback_stats = 0
    substituted = False

    def fail_restore_replace(
        source: Path | str,
        target: Path | str,
        **kwargs: object,
    ) -> None:
        if str(source) == "stage-00000001":
            raise OSError("injection second forward replace")
        original_replace(source, target, **kwargs)

    def fail_restore_exchange(
        _source_fd: int,
        source_name: str,
        _destination_fd: int,
        _destination_name: str,
    ) -> None:
        if source_name.startswith(".inventory-collection-rollback-"):
            raise OSError("injection rollback exchange")
        raise AssertionError("unexpected non-rollback exchange")

    def substitute_after_cleanup_stat(
        path: Path | str,
        *args: object,
        **kwargs: object,
    ) -> os.stat_result:
        nonlocal rollback_stats, substituted
        result = original_stat(path, *args, **kwargs)
        if str(path).startswith(".inventory-collection-rollback-"):
            rollback_stats += 1
            if rollback_stats == 2:
                directory_fd = kwargs["dir_fd"]
                assert isinstance(directory_fd, int)
                os.unlink(path, dir_fd=directory_fd)
                os.rename(wip, path, dst_dir_fd=directory_fd)
                substituted = True
        return result

    monkeypatch.setattr(inventory_module.os, "replace", fail_restore_replace)
    monkeypatch.setattr(
        inventory_module,
        "_exchange_directory_entries",
        fail_restore_exchange,
    )
    monkeypatch.setattr(
        inventory_module.os,
        "stat",
        substitute_after_cleanup_stat,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="transaction rolled back incompletely",
    ):
        inventory_module._apply_atomic_payloads(
            repository,
            {
                Path("audit/a-first.txt"): "premier nouveau\n",
                Path("audit/z-second.txt"): "second nouveau\n",
            },
        )

    assert substituted is False
    assert wip.read_bytes() == wip_before


def test_recovery_payload_rejects_same_inode_content_corruption(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root_fd = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    payload = b"historical authenticated bytes\n"
    original_write_all = inventory_module._write_all

    def corrupt_after_write(fd: int, written_payload: bytes) -> None:
        original_write_all(fd, written_payload)
        os.lseek(fd, 0, os.SEEK_SET)
        os.write(fd, b"CORRUPTED")
        os.ftruncate(fd, len(b"CORRUPTED"))

    monkeypatch.setattr(
        inventory_module,
        "_write_all",
        corrupt_after_write,
    )
    try:
        with pytest.raises(
            inventory_module.InventoryError,
            match="recovery backup content changed",
        ):
            inventory_module._copy_recovery_payload(
                tmp_path,
                root_fd=root_fd,
                payload=payload,
            )
    finally:
        os.close(root_fd)


def test_recovery_payload_revalidates_name_after_directory_fsync(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root_fd = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    wip = tmp_path.parent / f"{tmp_path.name}-recovery-wip.txt"
    _write(wip, "WIP substitué après fsync répertoire\n")
    wip_before = wip.read_bytes()
    original_fsync = inventory_module.os.fsync
    substituted = False

    def substitute_after_directory_fsync(fd: int) -> None:
        nonlocal substituted
        original_fsync(fd)
        if fd == root_fd and not substituted:
            recovery = next(
                tmp_path.glob(".inventory-collection-recovery-*.bak")
            )
            recovery.unlink()
            wip.rename(recovery)
            substituted = True

    monkeypatch.setattr(
        inventory_module.os,
        "fsync",
        substitute_after_directory_fsync,
    )
    try:
        with pytest.raises(
            inventory_module.InventoryError,
            match="recovery backup identity changed",
        ):
            inventory_module._copy_recovery_payload(
                tmp_path,
                root_fd=root_fd,
                payload=b"historical authenticated bytes\n",
            )
    finally:
        os.close(root_fd)

    assert substituted is True
    recovery = list(tmp_path.glob(".inventory-collection-recovery-*.bak"))
    assert len(recovery) == 1
    assert recovery[0].read_bytes() == wip_before


def test_quarantine_never_overwrites_an_existing_entry(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    first = repository / "audit/a-first.txt"
    second = repository / "audit/z-second.txt"
    source_wip = outside / "source-wip.txt"
    _write(first, "premier historique\n")
    _write(second, "second historique\n")
    _write(source_wip, "WIP source substitué\n")
    collision_token = "2" * 32
    collision = (
        repository
        / "audit"
        / f".inventory-collection-preserved-rollback-{collision_token}.wip"
    )
    _write(collision, "WIP de quarantaine préexistant\n")
    collision_before = collision.read_bytes()
    original_replace = inventory_module.os.replace
    original_exchange = inventory_module._exchange_directory_entries
    tokens = iter(
        ["1" * 32, collision_token, "3" * 32, "4" * 32]
    )
    substituted = False

    def substitute_restore_entry(
        source: Path | str,
        target: Path | str,
        **kwargs: object,
    ) -> None:
        nonlocal substituted
        if str(source) == "stage-00000001":
            raise OSError("injection second forward replace")
        original_replace(source, target, **kwargs)

    def substitute_restore_exchange(
        source_fd: int,
        source_name: str,
        destination_fd: int,
        destination_name: str,
    ) -> None:
        nonlocal substituted
        if source_name.startswith(".inventory-collection-rollback-") and not substituted:
            os.unlink(source_name, dir_fd=source_fd)
            os.rename(source_wip, source_name, dst_dir_fd=source_fd)
            substituted = True
        original_exchange(
            source_fd,
            source_name,
            destination_fd,
            destination_name,
        )

    def deterministic_token_hex(nbytes: int) -> str:
        if nbytes == 12:
            return "a" * 24
        return next(tokens)

    monkeypatch.setattr(
        inventory_module.secrets,
        "token_hex",
        deterministic_token_hex,
    )
    monkeypatch.setattr(
        inventory_module.os,
        "replace",
        substitute_restore_entry,
    )
    monkeypatch.setattr(
        inventory_module,
        "_exchange_directory_entries",
        substitute_restore_exchange,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="transaction rolled back.*injection second forward replace",
    ):
        inventory_module._apply_atomic_payloads(
            repository,
            {
                Path("audit/a-first.txt"): "premier nouveau\n",
                Path("audit/z-second.txt"): "second nouveau\n",
            },
        )

    assert substituted is True
    assert first.read_text(encoding="utf-8") == "premier historique\n"
    assert collision.read_bytes() == collision_before
    quarantined = list(
        (repository / "audit").glob(
            ".inventory-collection-preserved-rollback-*.wip"
        )
    )
    assert len(quarantined) == 2


def test_transaction_entry_write_failure_never_unlinks_substituted_wip(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    directory = tmp_path / "transaction"
    directory.mkdir()
    directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    wip = tmp_path / "write-failure-wip.txt"
    _write(wip, "WIP substitué après échec écriture\n")
    wip_before = wip.read_bytes()
    original_stat = inventory_module.os.stat
    substituted = False

    def fail_fsync(_fd: int) -> None:
        raise OSError("injection fsync transaction entry")

    def substitute_after_validation(
        path: Path | str,
        *args: object,
        **kwargs: object,
    ) -> os.stat_result:
        nonlocal substituted
        result = original_stat(path, *args, **kwargs)
        if str(path) == "stage-00000000" and not substituted:
            os.unlink(path, dir_fd=directory_fd)
            os.rename(wip, path, dst_dir_fd=directory_fd)
            substituted = True
        return result

    monkeypatch.setattr(inventory_module.os, "fsync", fail_fsync)
    monkeypatch.setattr(
        inventory_module.os,
        "stat",
        substitute_after_validation,
    )
    try:
        with pytest.raises(OSError, match="injection fsync transaction entry"):
            inventory_module._write_transaction_entry(
                directory_fd,
                "stage-00000000",
                b"owned payload\n",
            )
    finally:
        os.close(directory_fd)

    assert substituted is False
    assert wip.read_bytes() == wip_before


def test_rollback_exchange_preserves_destination_substituted_before_install(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    first = repository / "audit/a-first.txt"
    second = repository / "audit/z-second.txt"
    wip = outside / "destination-wip.txt"
    displaced = outside / "displaced-applied.txt"
    _write(first, "premier historique\n")
    _write(second, "second historique\n")
    _write(wip, "WIP substitué en destination\n")
    wip_before = wip.read_bytes()
    original_replace = inventory_module.os.replace
    original_exchange = inventory_module._exchange_directory_entries
    substituted = False

    def inject_destination(source_fd: int) -> None:
        nonlocal substituted
        if substituted:
            return
        os.rename(
            "a-first.txt",
            displaced,
            src_dir_fd=source_fd,
        )
        os.rename(wip, "a-first.txt", dst_dir_fd=source_fd)
        substituted = True

    def replace_with_destination_substitution(
        source: Path | str,
        target: Path | str,
        **kwargs: object,
    ) -> None:
        if str(source) == "stage-00000001":
            raise OSError("injection second forward replace")
        if str(source).startswith(".inventory-collection-rollback-"):
            source_fd = kwargs["src_dir_fd"]
            assert isinstance(source_fd, int)
            inject_destination(source_fd)
        original_replace(source, target, **kwargs)

    def exchange_with_destination_substitution(
        source_fd: int,
        source_name: str,
        destination_fd: int,
        destination_name: str,
    ) -> None:
        if source_name.startswith(".inventory-collection-rollback-"):
            inject_destination(destination_fd)
        original_exchange(
            source_fd,
            source_name,
            destination_fd,
            destination_name,
        )

    monkeypatch.setattr(
        inventory_module.os,
        "replace",
        replace_with_destination_substitution,
    )
    monkeypatch.setattr(
        inventory_module,
        "_exchange_directory_entries",
        exchange_with_destination_substitution,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="transaction rolled back.*injection second forward replace",
    ) as captured:
        inventory_module._apply_atomic_payloads(
            repository,
            {
                Path("audit/a-first.txt"): "premier nouveau\n",
                Path("audit/z-second.txt"): "second nouveau\n",
            },
        )

    assert substituted is True
    assert first.read_text(encoding="utf-8") == "premier historique\n"
    assert displaced.read_text(encoding="utf-8") == "premier nouveau\n"
    assert not wip.exists()
    preserved = list(
        (repository / "audit").glob(
            ".inventory-collection-rollback-*.tmp"
        )
    )
    assert any(path.read_bytes() == wip_before for path in preserved)
    assert "preserved rollback entry" in str(captured.value)


def test_rollback_fsyncs_parent_immediately_after_each_exchange(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    first = repository / "audit/a-first.txt"
    second = repository / "audit/z-second.txt"
    wip = tmp_path / "exchange-sync-wip.txt"
    _write(first, "premier historique\n")
    _write(second, "second historique\n")
    _write(wip, "WIP pour échange durable\n")
    original_exchange = inventory_module._exchange_directory_entries
    original_fsync = inventory_module.os.fsync
    original_read_backup = inventory_module._read_destination_backup
    pending_sync_fd: int | None = None
    read_before_sync = False
    substituted = False

    def observe_exchange(
        source_fd: int,
        source_name: str,
        destination_fd: int,
        destination_name: str,
    ) -> None:
        nonlocal pending_sync_fd, substituted
        if (
            source_name.startswith(".inventory-collection-rollback-")
            and not substituted
        ):
            os.unlink(source_name, dir_fd=source_fd)
            os.rename(wip, source_name, dst_dir_fd=source_fd)
            substituted = True
        original_exchange(
            source_fd,
            source_name,
            destination_fd,
            destination_name,
        )
        pending_sync_fd = destination_fd

    def observe_fsync(fd: int) -> None:
        nonlocal pending_sync_fd
        original_fsync(fd)
        if fd == pending_sync_fd:
            pending_sync_fd = None

    def require_exchange_sync(
        parent_fd: int,
        basename: str,
    ) -> tuple[bytes, os.stat_result] | None:
        nonlocal read_before_sync
        if pending_sync_fd is not None:
            read_before_sync = True
        return original_read_backup(parent_fd, basename)

    original_replace = inventory_module.os.replace

    def fail_second_forward_replace(
        source: Path | str,
        target: Path | str,
        **kwargs: object,
    ) -> None:
        nonlocal substituted
        if str(source) == "stage-00000001":
            raise OSError("injection second forward replace")
        if (
            str(source).startswith(".inventory-collection-rollback-")
            and not substituted
        ):
            source_fd = kwargs["src_dir_fd"]
            assert isinstance(source_fd, int)
            os.unlink(source, dir_fd=source_fd)
            os.rename(wip, source, dst_dir_fd=source_fd)
            substituted = True
        original_replace(source, target, **kwargs)

    monkeypatch.setattr(
        inventory_module,
        "_exchange_directory_entries",
        observe_exchange,
    )
    monkeypatch.setattr(inventory_module.os, "fsync", observe_fsync)
    monkeypatch.setattr(
        inventory_module,
        "_read_destination_backup",
        require_exchange_sync,
    )
    monkeypatch.setattr(
        inventory_module.os,
        "replace",
        fail_second_forward_replace,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="transaction rolled back.*injection second forward replace",
    ):
        inventory_module._apply_atomic_payloads(
            repository,
            {
                Path("audit/a-first.txt"): "premier nouveau\n",
                Path("audit/z-second.txt"): "second nouveau\n",
            },
        )

    assert substituted is True
    assert pending_sync_fd is None
    assert read_before_sync is False


def test_next_transaction_recovers_batch_after_process_crash(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = tmp_path / "audit/a-first.txt"
    second = tmp_path / "audit/z-second.txt"
    _write(first, "premier historique\n")
    _write(second, "second historique\n")
    child_code = f"""
import importlib.util
import os
from pathlib import Path

spec = importlib.util.spec_from_file_location("inventory_collection", {str(SCRIPT)!r})
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original_replace = module.os.replace

def crash_after_first_replace(source, target, **kwargs):
    original_replace(source, target, **kwargs)
    if str(source).startswith("stage-"):
        os._exit(91)

module.os.replace = crash_after_first_replace
module._apply_atomic_payloads(
    Path({str(tmp_path)!r}),
    {{
        Path("audit/a-first.txt"): "premier nouveau\\n",
        Path("audit/z-second.txt"): "second nouveau\\n",
    }},
)
"""

    crashed = subprocess.run(
        [sys.executable, "-c", child_code],
        check=False,
    )

    assert crashed.returncode == 91
    assert first.read_text(encoding="utf-8") == "premier nouveau\n"
    assert second.read_text(encoding="utf-8") == "second historique\n"
    assert list(tmp_path.glob(".inventory-collection-apply-*"))

    def fail_new_transaction(_root_fd: int):
        raise OSError("arrêt après récupération")

    monkeypatch.setattr(
        inventory_module,
        "_create_transaction_directory",
        fail_new_transaction,
    )

    with pytest.raises(OSError, match="arrêt après récupération"):
        inventory_module._apply_atomic_payloads(
            tmp_path,
            {Path("audit/irrelevant.txt"): "non écrit\n"},
        )

    assert first.read_text(encoding="utf-8") == "premier historique\n"
    assert second.read_text(encoding="utf-8") == "second historique\n"
    assert list(tmp_path.glob(".inventory-collection-apply-*")) == []


def test_next_transaction_discards_partial_journal_before_any_replace(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "audit/existing.txt"
    _write(target, "historique\n")
    child_code = f"""
import importlib.util
import os
from pathlib import Path

spec = importlib.util.spec_from_file_location("inventory_collection", {str(SCRIPT)!r})
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original_write_entry = module._write_transaction_entry

def crash_during_journal(directory_fd, name, payload):
    if name == "journal.tmp":
        fd = os.open(
            name,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600,
            dir_fd=directory_fd,
        )
        os.write(fd, payload[:17])
        os.fsync(fd)
        os._exit(93)
    return original_write_entry(directory_fd, name, payload)

module._write_transaction_entry = crash_during_journal
module._apply_atomic_payloads(
    Path({str(tmp_path)!r}),
    {{Path("audit/existing.txt"): "nouveau\\n"}},
)
"""

    crashed = subprocess.run(
        [sys.executable, "-c", child_code],
        check=False,
    )

    assert crashed.returncode == 93
    assert target.read_text(encoding="utf-8") == "historique\n"

    def fail_new_transaction(_root_fd: int):
        raise OSError("arrêt après abandon pré-journal")

    monkeypatch.setattr(
        inventory_module,
        "_create_transaction_directory",
        fail_new_transaction,
    )

    with pytest.raises(OSError, match="abandon pré-journal"):
        inventory_module._apply_atomic_payloads(
            tmp_path,
            {Path("audit/irrelevant.txt"): "non écrit\n"},
        )

    assert target.read_text(encoding="utf-8") == "historique\n"
    assert list(tmp_path.glob(".inventory-collection-apply-*")) == []


def test_next_transaction_discards_partial_preparing_marker(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    child_code = f"""
import importlib.util
import os
from pathlib import Path

spec = importlib.util.spec_from_file_location("inventory_collection", {str(SCRIPT)!r})
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original_write_entry = module._write_transaction_entry

def crash_during_preparing(directory_fd, name, payload):
    if name == "preparing.tmp":
        fd = os.open(
            name,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600,
            dir_fd=directory_fd,
        )
        os.write(fd, payload[:11])
        os.fsync(fd)
        os._exit(96)
    return original_write_entry(directory_fd, name, payload)

module._write_transaction_entry = crash_during_preparing
module._apply_atomic_payloads(
    Path({str(tmp_path)!r}),
    {{Path("audit/output.txt"): "nouveau\\n"}},
)
"""

    crashed = subprocess.run(
        [sys.executable, "-c", child_code],
        check=False,
    )

    assert crashed.returncode == 96
    assert not (tmp_path / "audit/output.txt").exists()

    def fail_new_transaction(_root_fd: int):
        raise OSError("arrêt après abandon preparing")

    monkeypatch.setattr(
        inventory_module,
        "_create_transaction_directory",
        fail_new_transaction,
    )

    with pytest.raises(OSError, match="abandon preparing"):
        inventory_module._apply_atomic_payloads(
            tmp_path,
            {Path("audit/irrelevant.txt"): "non écrit\n"},
        )

    assert not (tmp_path / "audit/output.txt").exists()
    assert list(tmp_path.glob(".inventory-collection-apply-*")) == []


def test_next_transaction_discards_empty_directory_left_after_mkdir_crash(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    child_code = f"""
import importlib.util
import os
from pathlib import Path

spec = importlib.util.spec_from_file_location("inventory_collection", {str(SCRIPT)!r})
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original_mkdir = module.os.mkdir

def crash_after_mkdir(path, *args, **kwargs):
    original_mkdir(path, *args, **kwargs)
    if str(path).startswith(".inventory-collection-apply-"):
        os._exit(97)

module.os.mkdir = crash_after_mkdir
module._apply_atomic_payloads(
    Path({str(tmp_path)!r}),
    {{Path("audit/output.txt"): "nouveau\\n"}},
)
"""

    crashed = subprocess.run(
        [sys.executable, "-c", child_code],
        check=False,
    )

    assert crashed.returncode == 97
    assert not (tmp_path / "audit/output.txt").exists()

    def fail_new_transaction(_root_fd: int):
        raise OSError("arrêt après abandon mkdir")

    monkeypatch.setattr(
        inventory_module,
        "_create_transaction_directory",
        fail_new_transaction,
    )

    with pytest.raises(OSError, match="abandon mkdir"):
        inventory_module._apply_atomic_payloads(
            tmp_path,
            {Path("audit/irrelevant.txt"): "non écrit\n"},
        )

    assert list(tmp_path.glob(".inventory-collection-apply-*")) == []


def test_recovery_refuses_target_substituted_after_snapshot(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "audit/existing.txt"
    _write(target, "historique\n")
    child_code = f"""
import importlib.util
import os
from pathlib import Path

spec = importlib.util.spec_from_file_location("inventory_collection", {str(SCRIPT)!r})
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original_replace = module.os.replace

def crash_after_replace(source, destination, **kwargs):
    original_replace(source, destination, **kwargs)
    if str(source).startswith("stage-"):
        os._exit(94)

module.os.replace = crash_after_replace
module._apply_atomic_payloads(
    Path({str(tmp_path)!r}),
    {{Path("audit/existing.txt"): "nouveau\\n"}},
)
"""
    crashed = subprocess.run(
        [sys.executable, "-c", child_code],
        check=False,
    )
    assert crashed.returncode == 94

    original_read = inventory_module._read_destination_backup
    substituted = False

    def substitute_after_snapshot(
        parent_fd: int,
        basename: str,
    ):
        nonlocal substituted
        value = original_read(parent_fd, basename)
        if basename == "existing.txt" and not substituted:
            os.unlink(basename, dir_fd=parent_fd)
            foreign_fd = os.open(
                basename,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600,
                dir_fd=parent_fd,
            )
            try:
                os.write(foreign_fd, b"concurrent\n")
            finally:
                os.close(foreign_fd)
            substituted = True
        return value

    monkeypatch.setattr(
        inventory_module,
        "_read_destination_backup",
        substitute_after_snapshot,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="identity changed",
    ):
        inventory_module._apply_atomic_payloads(
            tmp_path,
            {Path("audit/irrelevant.txt"): "non écrit\n"},
        )

    assert substituted is True
    assert target.read_text(encoding="utf-8") == "concurrent\n"
    assert list(tmp_path.glob(".inventory-collection-apply-*"))


def test_next_transaction_finishes_cleanup_after_committed_process_crash(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = tmp_path / "audit/a-first.txt"
    second = tmp_path / "audit/z-second.txt"
    _write(first, "premier historique\n")
    _write(second, "second historique\n")
    child_code = f"""
import importlib.util
import os
from pathlib import Path

spec = importlib.util.spec_from_file_location("inventory_collection", {str(SCRIPT)!r})
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original_unlink = module.os.unlink

def crash_during_cleanup(path, *args, **kwargs):
    original_unlink(path, *args, **kwargs)
    if str(path).startswith("backup-"):
        os._exit(92)

module.os.unlink = crash_during_cleanup
module._apply_atomic_payloads(
    Path({str(tmp_path)!r}),
    {{
        Path("audit/a-first.txt"): "premier nouveau\\n",
        Path("audit/z-second.txt"): "second nouveau\\n",
    }},
)
"""

    crashed = subprocess.run(
        [sys.executable, "-c", child_code],
        check=False,
    )

    assert crashed.returncode == 92
    assert first.read_text(encoding="utf-8") == "premier nouveau\n"
    assert second.read_text(encoding="utf-8") == "second nouveau\n"
    assert list(tmp_path.glob(".inventory-collection-apply-*"))

    def fail_new_transaction(_root_fd: int):
        raise OSError("arrêt après finalisation")

    monkeypatch.setattr(
        inventory_module,
        "_create_transaction_directory",
        fail_new_transaction,
    )

    with pytest.raises(OSError, match="arrêt après finalisation"):
        inventory_module._apply_atomic_payloads(
            tmp_path,
            {Path("audit/irrelevant.txt"): "non écrit\n"},
        )

    assert first.read_text(encoding="utf-8") == "premier nouveau\n"
    assert second.read_text(encoding="utf-8") == "second nouveau\n"
    assert list(tmp_path.glob(".inventory-collection-apply-*")) == []


def test_failed_rollback_preserves_and_reports_recoverable_backup(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = tmp_path / "audit/a-existing.txt"
    _write(existing, "octets historiques\n")
    original_replace = inventory_module.os.replace
    replacements = 0

    def fail_apply_then_rollback(
        source: Path | str,
        target: Path | str,
        **kwargs: object,
    ) -> None:
        nonlocal replacements
        replacements += 1
        if replacements == 2:
            raise OSError(f"injection replace {replacements}")
        original_replace(source, target, **kwargs)

    def fail_rollback_exchange(
        _source_fd: int,
        source_name: str,
        _destination_fd: int,
        _destination_name: str,
    ) -> None:
        if source_name.startswith(".inventory-collection-rollback-"):
            raise OSError("injection rollback exchange")
        raise AssertionError("unexpected non-rollback exchange")

    monkeypatch.setattr(
        inventory_module.os,
        "replace",
        fail_apply_then_rollback,
    )
    monkeypatch.setattr(
        inventory_module,
        "_exchange_directory_entries",
        fail_rollback_exchange,
    )

    with pytest.raises(
        inventory_module.InventoryError, match="recoverable backup"
    ) as captured:
        inventory_module._apply_atomic_payloads(
            tmp_path,
            {
                Path("audit/a-existing.txt"): "nouveaux octets\n",
                Path("audit/z-new.txt"): "nouveau fichier\n",
            },
        )

    match = re.search(r"recoverable backup: ([^;]+)", str(captured.value))
    assert match is not None
    backup_path = Path(match.group(1))
    assert backup_path.parent == tmp_path
    assert backup_path.name.startswith(".inventory-collection-recovery-")
    assert backup_path.read_bytes() == b"octets historiques\n"
    assert existing.read_bytes() == b"nouveaux octets\n"


def test_lock_write_failure_never_unlinks_a_replacement_inode(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lock_path = tmp_path / inventory_module.GENERIC_LOCK_FILE
    foreign_record = b"foreign lock owner\n"

    def replace_lock_then_fail(_fd: int, _payload: bytes) -> int:
        lock_path.unlink()
        lock_path.write_bytes(foreign_record)
        raise OSError("injection écriture verrou")

    monkeypatch.setattr(inventory_module.os, "write", replace_lock_then_fail)

    with pytest.raises(OSError, match="injection écriture verrou"):
        with inventory_module._lock_generation(tmp_path):
            pytest.fail("l'acquisition doit échouer")

    assert lock_path.read_bytes() == foreign_record


def test_transaction_uses_pinned_temp_directory_after_path_substitution(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    existing = repository / "audit/existing.txt"
    _write(existing, "octets historiques\n")
    outside.mkdir()
    sentinel = outside / "sentinel.txt"
    sentinel.write_bytes(b"ne pas supprimer\n")
    original_fsync = inventory_module.os.fsync
    substitution: dict[str, Path] = {}

    def substitute_real_temp_root(fd: int) -> None:
        original_fsync(fd)
        if substitution:
            return
        try:
            open_path = Path(os.readlink(f"/proc/self/fd/{fd}"))
        except OSError:
            return
        temp_root = open_path.parent
        if (
            temp_root.parent != repository
            or not temp_root.name.startswith(".inventory-collection-apply-")
        ):
            return
        moved_root = repository / f"{temp_root.name}.moved"
        temp_root.rename(moved_root)
        temp_root.symlink_to(outside, target_is_directory=True)
        external_stage = outside / open_path.name
        external_stage.write_bytes(b"octets externes\n")
        substitution.update(
            {
                "temp_root": temp_root,
                "moved_root": moved_root,
                "external_stage": external_stage,
            }
        )

    monkeypatch.setattr(
        inventory_module.os,
        "fsync",
        substitute_real_temp_root,
    )

    inventory_module._apply_atomic_payloads(
        repository,
        {Path("audit/existing.txt"): "nouveaux octets\n"},
    )

    assert substitution
    assert existing.read_bytes() == b"nouveaux octets\n"
    assert substitution["external_stage"].read_bytes() == b"octets externes\n"
    assert sentinel.read_bytes() == b"ne pas supprimer\n"
    assert substitution["temp_root"].is_symlink()


def test_transaction_fails_if_repository_root_path_is_substituted_after_staging(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    moved_repository = tmp_path / "repository-original"
    outside = tmp_path / "outside"
    original_target = repository / "audit/existing.txt"
    external_target = outside / "audit/existing.txt"
    _write(original_target, "octets historiques\n")
    _write(external_target, "octets externes\n")
    original_fsync = inventory_module.os.fsync
    substituted = False

    def substitute_repository_after_stage(fd: int) -> None:
        nonlocal substituted
        original_fsync(fd)
        if substituted:
            return
        try:
            open_path = Path(os.readlink(f"/proc/self/fd/{fd}"))
        except OSError:
            return
        if not open_path.parent.name.startswith(
            ".inventory-collection-apply-"
        ):
            return
        repository.rename(moved_repository)
        repository.symlink_to(outside, target_is_directory=True)
        substituted = True

    monkeypatch.setattr(
        inventory_module.os,
        "fsync",
        substitute_repository_after_stage,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="repository root identity changed",
    ):
        inventory_module._apply_atomic_payloads(
            repository,
            {Path("audit/existing.txt"): "nouveaux octets\n"},
        )

    assert substituted
    assert (
        moved_repository / "audit/existing.txt"
    ).read_bytes() == b"octets historiques\n"
    assert external_target.read_bytes() == b"octets externes\n"
    assert list(moved_repository.glob(".inventory-collection-apply-*")) == []


def test_transaction_temp_directory_creation_uses_pinned_repository_fd(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    moved_repository = tmp_path / "repository-original"
    outside = tmp_path / "outside"
    original_target = repository / "audit/existing.txt"
    _write(original_target, "octets historiques\n")
    outside.mkdir()
    original_open_pinned = inventory_module._open_pinned_directory
    substituted = False

    def substitute_after_root_pin(path: Path, *, role: str):
        nonlocal substituted
        fd, identity = original_open_pinned(path, role=role)
        if role == "repository transaction root" and not substituted:
            repository.rename(moved_repository)
            repository.symlink_to(outside, target_is_directory=True)
            substituted = True
        return fd, identity

    monkeypatch.setattr(
        inventory_module,
        "_open_pinned_directory",
        substitute_after_root_pin,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="repository root identity changed",
    ):
        inventory_module._apply_atomic_payloads(
            repository,
            {Path("audit/existing.txt"): "nouveaux octets\n"},
        )

    assert substituted
    assert (
        moved_repository / "audit/existing.txt"
    ).read_bytes() == b"octets historiques\n"
    assert list(outside.glob(".inventory-collection-apply-*")) == []
    assert list(moved_repository.glob(".inventory-collection-apply-*")) == []


def test_transaction_refuses_internal_symlink_parent_component(
    tmp_path: Path,
    inventory_module,
) -> None:
    repository = tmp_path / "repository"
    real_parent = repository / "real-audit"
    real_parent.mkdir(parents=True)
    (repository / "audit").symlink_to(
        real_parent,
        target_is_directory=True,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="destination parent.*symlink|destination parent.*directory",
    ):
        inventory_module._apply_atomic_payloads(
            repository,
            {Path("audit/output.txt"): "contenu\n"},
        )

    assert not (real_parent / "output.txt").exists()


def test_transaction_refuses_symlink_destination_entry(
    tmp_path: Path,
    inventory_module,
) -> None:
    repository = tmp_path / "repository"
    real_target = repository / "audit/real.txt"
    symlink_target = repository / "audit/output.txt"
    _write(real_target, "octets historiques\n")
    symlink_target.symlink_to(real_target)

    with pytest.raises(
        inventory_module.InventoryError,
        match="destination target.*regular file|destination target.*symlink",
    ):
        inventory_module._apply_atomic_payloads(
            repository,
            {Path("audit/output.txt"): "nouveaux octets\n"},
        )

    assert symlink_target.is_symlink()
    assert real_target.read_bytes() == b"octets historiques\n"


def test_transaction_rejects_destination_inode_substituted_after_replace(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "audit/existing.txt"
    _write(target, "octets historiques\n")
    original_replace = inventory_module.os.replace
    substituted = False

    def replace_then_substitute(
        source: Path | str,
        destination: Path | str,
        **kwargs: object,
    ) -> None:
        nonlocal substituted
        original_replace(source, destination, **kwargs)
        if substituted or not str(source).startswith("stage-"):
            return
        destination_fd = kwargs.get("dst_dir_fd")
        assert isinstance(destination_fd, int)
        os.unlink(destination, dir_fd=destination_fd)
        foreign_fd = os.open(
            destination,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600,
            dir_fd=destination_fd,
        )
        try:
            os.write(foreign_fd, b"octets concurrents\n")
        finally:
            os.close(foreign_fd)
        substituted = True

    monkeypatch.setattr(
        inventory_module.os,
        "replace",
        replace_then_substitute,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="recoverable backup.*applied destination identity changed",
    ) as captured:
        inventory_module._apply_atomic_payloads(
            tmp_path,
            {Path("audit/existing.txt"): "nouveaux octets\n"},
        )

    recovery_match = re.search(
        r"recoverable backup: ([^;]+)",
        str(captured.value),
    )
    assert recovery_match is not None
    assert Path(
        recovery_match.group(1)
    ).read_bytes() == b"octets historiques\n"
    assert target.read_bytes() == b"octets concurrents\n"


def test_successful_replace_fsyncs_destination_parent(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parent = tmp_path / "audit"
    parent.mkdir()
    parent_identity = parent.stat()
    fsynced_parent = False
    original_fsync = inventory_module.os.fsync

    def observe_fsync(fd: int) -> None:
        nonlocal fsynced_parent
        value = os.fstat(fd)
        if (value.st_dev, value.st_ino) == (
            parent_identity.st_dev,
            parent_identity.st_ino,
        ):
            fsynced_parent = True
        original_fsync(fd)

    monkeypatch.setattr(inventory_module.os, "fsync", observe_fsync)

    inventory_module._apply_atomic_payloads(
        tmp_path,
        {Path("audit/output.txt"): "contenu\n"},
    )

    assert fsynced_parent


def test_transaction_reads_backup_through_pinned_parent_fd(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    target = repository / "audit/existing.txt"
    _write(target, "octets historiques\n")
    _write(outside / "existing.txt", "octets externes secrets\n")
    captured_payloads: list[bytes] = []
    original_write_entry = inventory_module._write_transaction_entry

    def swap_parent_after_stage(
        directory_fd: int,
        name: str,
        payload: bytes,
    ) -> os.stat_result:
        if name.startswith(("stage-", "backup-")):
            captured_payloads.append(payload)
        identity = original_write_entry(directory_fd, name, payload)
        if name.startswith("stage-"):
            (repository / "audit").rename(repository / "audit-original")
            (repository / "audit").symlink_to(
                outside,
                target_is_directory=True,
            )
        return identity

    monkeypatch.setattr(
        inventory_module,
        "_write_transaction_entry",
        swap_parent_after_stage,
    )

    with pytest.raises(inventory_module.InventoryError, match="symlink escape"):
        inventory_module._apply_atomic_payloads(
            repository,
            {Path("audit/existing.txt"): "nouveaux octets\n"},
        )

    assert captured_payloads == [
        b"nouveaux octets\n",
        b"octets historiques\n",
    ]
    assert (outside / "existing.txt").read_bytes() == b"octets externes secrets\n"


def test_cleanup_failure_on_success_is_explicit_inventory_error(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "audit/existing.txt"
    _write(target, "octets historiques\n")
    original_unlink = inventory_module.os.unlink

    def fail_backup_cleanup(
        path: Path | str,
        *args: object,
        dir_fd: int | None = None,
        **kwargs: object,
    ) -> None:
        if dir_fd is not None and str(path).startswith("backup-"):
            raise PermissionError("injection cleanup backup")
        original_unlink(path, *args, dir_fd=dir_fd, **kwargs)

    monkeypatch.setattr(inventory_module.os, "unlink", fail_backup_cleanup)

    with pytest.raises(
        inventory_module.InventoryError,
        match="transaction cleanup failed.*injection cleanup backup",
    ):
        inventory_module._apply_atomic_payloads(
            tmp_path,
            {Path("audit/existing.txt"): "nouveaux octets\n"},
        )

    assert target.read_bytes() == b"nouveaux octets\n"


def test_cleanup_failure_never_masks_primary_transaction_error(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "audit/existing.txt"
    _write(target, "octets historiques\n")
    original_unlink = inventory_module.os.unlink

    def fail_apply(
        _source: Path | str,
        _target: Path | str,
        **_kwargs: object,
    ) -> None:
        raise OSError("injection cause primaire")

    def fail_backup_cleanup(
        path: Path | str,
        *args: object,
        dir_fd: int | None = None,
        **kwargs: object,
    ) -> None:
        if dir_fd is not None and str(path).startswith("backup-"):
            raise PermissionError("injection cleanup secondaire")
        original_unlink(path, *args, dir_fd=dir_fd, **kwargs)

    monkeypatch.setattr(inventory_module.os, "replace", fail_apply)
    monkeypatch.setattr(inventory_module.os, "unlink", fail_backup_cleanup)

    with pytest.raises(
        inventory_module.InventoryError,
        match="transaction rolled back.*injection cause primaire",
    ) as captured:
        inventory_module._apply_atomic_payloads(
            tmp_path,
            {Path("audit/existing.txt"): "nouveaux octets\n"},
        )

    assert any(
        "injection cleanup secondaire" in note
        for note in getattr(captured.value, "__notes__", [])
    )


def test_transaction_root_fd_is_closed_when_temp_creation_fails(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root_fds: list[int] = []
    closed_fds: list[int] = []
    original_open_pinned = inventory_module._open_pinned_directory
    original_close = inventory_module.os.close

    def capture_root_fd(path: Path, *, role: str):
        fd, identity = original_open_pinned(path, role=role)
        if role == "repository transaction root":
            root_fds.append(fd)
        return fd, identity

    def close(fd: int) -> None:
        closed_fds.append(fd)
        original_close(fd)

    def fail_temp_creation(_root_fd: int):
        raise OSError("injection transaction directory")

    monkeypatch.setattr(
        inventory_module,
        "_open_pinned_directory",
        capture_root_fd,
    )
    monkeypatch.setattr(inventory_module.os, "close", close)
    monkeypatch.setattr(
        inventory_module,
        "_create_transaction_directory",
        fail_temp_creation,
    )

    with pytest.raises(OSError, match="injection transaction directory"):
        inventory_module._apply_atomic_payloads(
            tmp_path,
            {Path("audit/output.txt"): "contenu\n"},
        )

    assert len(root_fds) == 1
    assert root_fds[0] in closed_fds


def test_transaction_directory_open_failure_removes_created_directory(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_open = inventory_module.os.open

    def fail_transaction_directory_open(
        path: Path | str,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if (
            dir_fd is not None
            and str(path).startswith(".inventory-collection-apply-")
        ):
            raise PermissionError("injection open transaction directory")
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(
        inventory_module.os,
        "open",
        fail_transaction_directory_open,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="transaction directory cannot be pinned",
    ):
        inventory_module._apply_atomic_payloads(
            tmp_path,
            {Path("audit/output.txt"): "contenu\n"},
        )

    assert list(tmp_path.glob(".inventory-collection-apply-*")) == []


def test_failed_rollback_copies_backup_out_of_a_substituted_temp_root(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    first = repository / "audit/a-first.txt"
    second = repository / "audit/z-second.txt"
    _write(first, "premiers octets historiques\n")
    _write(second, "seconds octets historiques\n")
    outside.mkdir()
    original_fsync = inventory_module.os.fsync
    original_replace = inventory_module.os.replace
    substitution: dict[str, Path] = {}
    replacements = 0

    def substitute_real_temp_root(fd: int) -> None:
        original_fsync(fd)
        if substitution:
            return
        try:
            open_path = Path(os.readlink(f"/proc/self/fd/{fd}"))
        except OSError:
            return
        temp_root = open_path.parent
        if (
            temp_root.parent != repository
            or not temp_root.name.startswith(".inventory-collection-apply-")
        ):
            return
        moved_root = repository / f"{temp_root.name}.moved"
        temp_root.rename(moved_root)
        temp_root.symlink_to(outside, target_is_directory=True)
        external_stage = outside / open_path.name
        external_stage.write_bytes(b"octets externes\n")
        substitution.update(
            {
                "temp_root": temp_root,
                "external_stage": external_stage,
            }
        )

    def fail_apply_then_rollback(
        source: Path | str,
        target: Path | str,
        **kwargs: object,
    ) -> None:
        nonlocal replacements
        replacements += 1
        if replacements == 2:
            raise OSError(f"injection replace {replacements}")
        original_replace(source, target, **kwargs)

    def fail_rollback_exchange(
        _source_fd: int,
        source_name: str,
        _destination_fd: int,
        _destination_name: str,
    ) -> None:
        if source_name.startswith(".inventory-collection-rollback-"):
            raise OSError("injection rollback exchange")
        raise AssertionError("unexpected non-rollback exchange")

    monkeypatch.setattr(
        inventory_module.os,
        "fsync",
        substitute_real_temp_root,
    )
    monkeypatch.setattr(
        inventory_module.os,
        "replace",
        fail_apply_then_rollback,
    )
    monkeypatch.setattr(
        inventory_module,
        "_exchange_directory_entries",
        fail_rollback_exchange,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="recoverable backup",
    ) as captured:
        inventory_module._apply_atomic_payloads(
            repository,
            {
                Path("audit/a-first.txt"): "nouveaux premiers octets\n",
                Path("audit/z-second.txt"): "nouveaux seconds octets\n",
            },
        )

    match = re.search(r"recoverable backup: ([^;]+)", str(captured.value))
    assert match is not None
    recovery_path = Path(match.group(1))
    assert recovery_path.parent == repository
    assert recovery_path.name.startswith(".inventory-collection-recovery-")
    assert recovery_path.read_bytes() == b"premiers octets historiques\n"
    assert substitution["external_stage"].read_bytes() == b"octets externes\n"
    assert substitution["temp_root"].is_symlink()


def test_forward_replace_revalidates_symlink_confinement_after_staging(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    audit = repository / "audit"
    audit.mkdir(parents=True)
    outside.mkdir()
    original_fsync = inventory_module.os.fsync
    swapped = False

    def swap_parent_after_stage(fd: int) -> None:
        nonlocal swapped
        original_fsync(fd)
        if not swapped:
            swapped = True
            audit.rename(repository / "audit-original")
            audit.symlink_to(outside, target_is_directory=True)

    monkeypatch.setattr(inventory_module.os, "fsync", swap_parent_after_stage)

    with pytest.raises(inventory_module.InventoryError, match="symlink escape"):
        inventory_module._apply_atomic_payloads(
            repository,
            {Path("audit/output.txt"): "contenu\n"},
        )

    assert list(outside.iterdir()) == []


def test_rollback_uses_pinned_parent_after_path_symlink_substitution(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    existing = repository / "audit/a-existing.txt"
    _write(existing, "octets historiques\n")
    outside.mkdir()
    original_replace = inventory_module.os.replace
    replacements = 0

    def swap_parent_on_apply_failure(
        source: Path | str,
        target: Path | str,
        **kwargs: object,
    ) -> None:
        nonlocal replacements
        replacements += 1
        if replacements == 2:
            (repository / "audit").rename(repository / "audit-original")
            (repository / "audit").symlink_to(
                outside,
                target_is_directory=True,
            )
            raise OSError("injection avant rollback")
        original_replace(source, target, **kwargs)

    monkeypatch.setattr(
        inventory_module.os,
        "replace",
        swap_parent_on_apply_failure,
    )

    with pytest.raises(
        inventory_module.InventoryError,
        match="transaction rolled back.*injection avant rollback",
    ):
        inventory_module._apply_atomic_payloads(
            repository,
            {
                Path("audit/a-existing.txt"): "nouveaux octets\n",
                Path("audit/z-new.txt"): "nouveau fichier\n",
            },
        )

    assert (
        repository / "audit-original/a-existing.txt"
    ).read_bytes() == b"octets historiques\n"
    assert list(outside.iterdir()) == []
    assert list(repository.glob(".inventory-collection-recovery-*")) == []


def test_atomic_staging_failure_leaves_no_temporary_or_target(
    tmp_path: Path,
    inventory_module,
) -> None:
    target = tmp_path / "audit/invalid.txt"

    with pytest.raises(
        inventory_module.InventoryError, match="transaction rolled back"
    ):
        inventory_module._apply_atomic_payloads(
            tmp_path,
            {Path("audit/invalid.txt"): "\ud800"},
        )

    assert not target.exists()
    assert not (tmp_path / ".inventory-collection-apply").exists()
    assert list(tmp_path.glob(".inventory-collection-apply-*")) == []


def test_atomic_batch_rejects_transaction_directory_symlink_escape(
    tmp_path: Path,
    inventory_module,
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    repository.mkdir()
    outside.mkdir()
    (repository / ".inventory-collection-apply").symlink_to(
        outside,
        target_is_directory=True,
    )

    with pytest.raises(inventory_module.InventoryError, match="symlink escape"):
        inventory_module._apply_atomic_payloads(
            repository,
            {Path("audit/output.txt"): "contenu\n"},
        )

    assert not (repository / "audit/output.txt").exists()
    assert list(outside.iterdir()) == []


def test_require_clean_generation_ignores_only_its_own_transaction_files(
    tmp_path: Path,
    inventory_module,
) -> None:
    _seed_cli_repository(tmp_path)
    _commit_repository(tmp_path, "clean sources")

    result = inventory_module.build_inventory_artifacts(
        tmp_path,
        require_clean="worktree",
    )

    assert set(result["artifacts"]) == {
        "audit",
        "ecarts",
        "etat",
        "json",
        "markdown",
        "matrice",
    }
    assert not (tmp_path / inventory_module.GENERIC_LOCK_FILE).exists()


def test_second_clean_check_rejects_transaction_lookalike_created_after_preflight(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_cli_repository(tmp_path)
    _commit_repository(tmp_path, "clean sources")
    lookalike = tmp_path / ".inventory-collection-apply-user-notes"

    @contextmanager
    def inject_user_wip(_root: Path):
        _write(lookalike, "WIP utilisateur\n")
        yield {inventory_module.GENERIC_LOCK_FILE: (-1, -1)}

    monkeypatch.setattr(inventory_module, "_lock_generation", inject_user_wip)

    with pytest.raises(
        inventory_module.InventoryError, match="local modifications"
    ):
        inventory_module.build_inventory_artifacts(
            tmp_path,
            require_clean="worktree",
        )

    assert lookalike.read_text(encoding="utf-8") == "WIP utilisateur\n"
    assert not (tmp_path / "audit/INVENTAIRE_COLLECTION.json").exists()


def test_check_recomputes_untracked_provenance_instead_of_reusing_stored_status(
    tmp_path: Path,
    inventory_module,
) -> None:
    _seed_cli_repository(tmp_path)
    _commit_repository(tmp_path, "clean sources")
    inventory_module.build_inventory_artifacts(tmp_path)
    untracked = "NSI/chapitres/1NSI-TEST/cours/nouvelle source.tex"
    _write(
        tmp_path / untracked,
        _meta(id="1NSI-TEST-NOUVELLE", chapitre="1NSI-TEST"),
    )

    result = inventory_module.build_inventory_artifacts(
        tmp_path,
        check_only=True,
    )

    provenance = result["inventory"]["provenance"]
    assert provenance["dirty"] is True
    assert provenance["untracked_relevant"] == [untracked]
    assert any(
        "INVENTAIRE_COLLECTION.json" in difference
        for difference in result["diffs"]
    )


def test_check_reuses_stored_generation_provenance_and_changes_nothing(
    tmp_path: Path,
    inventory_module,
) -> None:
    _seed_cli_repository(tmp_path)
    generation_sha = _commit_repository(tmp_path, "sources")
    result = inventory_module.build_inventory_artifacts(tmp_path)
    paths = _managed_output_paths(tmp_path, result)
    relative_paths = tuple(path.relative_to(tmp_path).as_posix() for path in paths)
    _track(tmp_path, *relative_paths)
    checked_in_sha = _commit_repository(tmp_path, "generated outputs")
    stored_inventory = json.loads(
        (tmp_path / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8")
    )
    before_status = _git_status_bytes(tmp_path)
    before_contents = {path: path.read_bytes() for path in paths}
    time.sleep(1.1)

    completed = _run_inventory_cli(tmp_path, "--check")

    assert completed.returncode == 0
    assert json.loads(completed.stdout)["success"] is True
    assert _git_status_bytes(tmp_path) == before_status
    assert {path: path.read_bytes() for path in paths} == before_contents
    assert generation_sha != checked_in_sha
    assert stored_inventory["provenance"]["head_sha"] == generation_sha


def test_check_reuses_stored_tool_versions_instead_of_current_runtime_signature(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_cli_repository(tmp_path)
    _commit_repository(tmp_path, "sources")
    inventory_module.build_inventory_artifacts(tmp_path)
    paths = _managed_output_paths(
        tmp_path,
        inventory_module.build_inventory_artifacts(tmp_path),
    )
    _track(tmp_path, *(path.relative_to(tmp_path).as_posix() for path in paths))
    _commit_repository(tmp_path, "generated outputs")
    stored_inventory = json.loads(
        (tmp_path / "audit/INVENTAIRE_COLLECTION.json").read_text(
            encoding="utf-8"
        )
    )
    stored_versions = dict(
        stored_inventory["provenance"]["tool_versions"],  # type: ignore[arg-type]
    )
    before_status = _git_status_bytes(tmp_path)
    before_contents = {path: path.read_bytes() for path in paths}

    def alternate_signature(_root: Path) -> dict[str, str]:
        return {name: f"runtime:{value}" for name, value in stored_versions.items()}

    monkeypatch.setattr(
        inventory_module, "_file_version_signature", alternate_signature
    )
    time.sleep(1.0)

    completed = _run_inventory_cli(tmp_path, "--check")
    check_payload = json.loads(completed.stdout)

    assert completed.returncode == 0
    assert check_payload["success"] is True
    assert check_payload["reasons"] == []
    assert _git_status_bytes(tmp_path) == before_status
    assert {path: path.read_bytes() for path in paths} == before_contents


def test_stored_provenance_reuse_has_no_dead_assignment(
    inventory_module,
) -> None:
    tree = ast.parse(
        inspect.getsource(
            inventory_module._reuse_stored_generation_provenance
        )
    )
    reused_assignments = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "reused"
            for target in node.targets
        )
    ]

    assert len(reused_assignments) == 1


def test_check_only_never_takes_generation_lock_or_creates_temporary_files(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_cli_repository(tmp_path)
    _commit_repository(tmp_path, "sources")
    inventory_module.build_inventory_artifacts(tmp_path)
    before_status = _git_status_bytes(tmp_path)

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("check_only ne doit ni verrouiller ni écrire")

    monkeypatch.setattr(inventory_module, "_lock_generation", forbidden)
    monkeypatch.setattr(inventory_module.tempfile, "NamedTemporaryFile", forbidden)

    result = inventory_module.build_inventory_artifacts(tmp_path, check_only=True)

    assert result["diffs"] == []
    assert _git_status_bytes(tmp_path) == before_status


def test_custom_managed_outputs_are_stable_excluded_and_checked_without_writes(
    tmp_path: Path,
) -> None:
    _seed_cli_repository(tmp_path)
    _commit_repository(tmp_path, "sources")
    arguments = (
        "--audit-dir",
        "evidence/custom-audit",
        "--etat-path",
        "evidence/custom-state.md",
    )
    first = _run_inventory_cli(tmp_path, *arguments)
    managed = tuple(
        tmp_path / relative
        for relative in (
            "evidence/custom-state.md",
            "evidence/custom-audit/AUDIT_CONSOLIDE.md",
            "evidence/custom-audit/ECARTS_ET_CONTRADICTIONS.yaml",
            "evidence/custom-audit/INVENTAIRE_COLLECTION.json",
            "evidence/custom-audit/INVENTAIRE_COLLECTION.md",
            "evidence/custom-audit/MATRICE_LIVRABLES.yaml",
        )
    )
    first_bytes = {path: path.read_bytes() for path in managed}
    first_provenance = json.loads(
        (tmp_path / "evidence/custom-audit/INVENTAIRE_COLLECTION.json").read_text(
            encoding="utf-8"
        )
    )["provenance"]
    time.sleep(1.1)

    second = _run_inventory_cli(tmp_path, *arguments)
    second_bytes = {path: path.read_bytes() for path in managed}
    before_check_status = _git_status_bytes(tmp_path)
    check = _run_inventory_cli(tmp_path, *arguments, "--check")

    assert first.returncode == 0
    assert second.returncode == 0
    assert first_bytes == second_bytes
    assert first_provenance["dirty"] is False
    assert first_provenance["modified_tracked"] == []
    assert first_provenance["untracked_relevant"] == []
    assert check.returncode == 0
    assert json.loads(check.stdout)["success"] is True
    assert _git_status_bytes(tmp_path) == before_check_status
    assert {path: path.read_bytes() for path in managed} == second_bytes


def test_generator_fingerprint_covers_support_modules_and_gates_the_model(
    tmp_path: Path,
) -> None:
    _seed_cli_repository(tmp_path)
    components = _install_generator_components(tmp_path)
    _commit_repository(tmp_path, "sources and generator")
    generated = _run_repository_inventory_cli(tmp_path)
    inventory_path = tmp_path / "audit/INVENTAIRE_COLLECTION.json"
    stored = json.loads(inventory_path.read_text(encoding="utf-8"))
    before_outputs = {
        path: path.read_bytes()
        for path in (
            tmp_path / "ETAT_COLLECTION.md",
            tmp_path / "audit/AUDIT_CONSOLIDE.md",
            tmp_path / "audit/ECARTS_ET_CONTRADICTIONS.yaml",
            inventory_path,
            tmp_path / "audit/INVENTAIRE_COLLECTION.md",
            tmp_path / "audit/MATRICE_LIVRABLES.yaml",
        )
    }

    assert generated.returncode == 0
    assert set(stored["provenance"]["generator_files"]) == {
        f"scripts/{component}" for component in GENERATOR_COMPONENTS
    }
    assert stored["provenance"]["generator_sha256"] == (
        _load_inventory_module()._aggregate_generator_digest(
            stored["provenance"]["generator_files"]
        )
    )

    support_path = tmp_path / components[1]
    support_path.write_text(
        support_path.read_text(encoding="utf-8") + "\n# dérive support testée\n",
        encoding="utf-8",
    )
    check = _run_repository_inventory_cli(tmp_path, "--check")
    validate = _run_repository_inventory_cli(tmp_path, "--validate-model")

    assert check.returncode == 3
    assert any("INVENTAIRE_COLLECTION.json" in reason for reason in json.loads(check.stdout)["reasons"])
    assert validate.returncode == 6
    assert any("generator_sha256" in reason for reason in json.loads(validate.stdout)["reasons"])
    assert {path: path.read_bytes() for path in before_outputs} == before_outputs


def test_check_detects_tracked_source_drift_without_writing_outputs(
    tmp_path: Path,
    inventory_module,
) -> None:
    tracked = _seed_cli_repository(tmp_path)
    _commit_repository(tmp_path, "sources")
    result = inventory_module.build_inventory_artifacts(tmp_path)
    managed = _managed_output_paths(tmp_path, result)
    before = {path: path.read_bytes() for path in managed}
    source = tmp_path / tracked[1]
    source.write_text(
        source.read_text(encoding="utf-8") + "\nContenu source modifié.\n",
        encoding="utf-8",
    )

    check = _run_inventory_cli(tmp_path, "--check")

    assert check.returncode == 3
    reasons = json.loads(check.stdout)["reasons"]
    assert any("INVENTAIRE_COLLECTION.json" in reason for reason in reasons)
    assert {path: path.read_bytes() for path in managed} == before


def test_validate_model_gate_accepts_valid_outputs_and_rejects_digest_drift(
    tmp_path: Path, inventory_module
) -> None:
    _seed_cli_repository(tmp_path)
    _commit_repository(tmp_path, "sources")
    inventory_module.build_inventory_artifacts(tmp_path)

    valid = _run_inventory_cli(tmp_path, "--validate-model")
    valid_payload = json.loads(valid.stdout)

    assert valid.returncode == 0
    assert valid_payload["gate"] == "validate-model"
    assert valid_payload["success"] is True
    assert valid_payload["reasons"] == []

    inventory_path = tmp_path / "audit/INVENTAIRE_COLLECTION.json"
    payload = json.loads(inventory_path.read_text(encoding="utf-8"))
    payload["model_digest"] = "sha256:" + "0" * 64
    inventory_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    invalid = _run_inventory_cli(tmp_path, "--validate-model")
    invalid_payload = json.loads(invalid.stdout)

    assert invalid.returncode == 6
    assert invalid_payload["gate"] == "validate-model"
    assert invalid_payload["success"] is False
    assert invalid_payload["reasons"] == sorted(invalid_payload["reasons"])
    assert any("model_digest" in reason for reason in invalid_payload["reasons"])


@pytest.mark.parametrize(
    ("relative_path", "projection"),
    [
        pytest.param(
            "audit/ECARTS_ET_CONTRADICTIONS.yaml",
            "counts",
            id="ecarts-counts",
        ),
        pytest.param(
            "audit/ECARTS_ET_CONTRADICTIONS.yaml",
            "anomalies",
            id="ecarts-anomalies",
        ),
        pytest.param(
            "audit/ECARTS_ET_CONTRADICTIONS.yaml",
            "claims",
            id="ecarts-claims",
        ),
        pytest.param(
            "audit/MATRICE_LIVRABLES.yaml",
            "manuals",
            id="matrix-manuals",
        ),
    ],
)
def test_validate_model_rejects_schema_valid_projection_falsification(
    tmp_path: Path,
    inventory_module,
    relative_path: str,
    projection: str,
) -> None:
    _seed_cli_repository(tmp_path)
    _commit_repository(tmp_path, "sources")
    inventory_module.build_inventory_artifacts(tmp_path)
    artifact_path = tmp_path / relative_path
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    if projection == "counts":
        payload["counts"]["claims_ouverts"] += 1
    elif projection == "anomalies":
        first_category = next(iter(payload["anomalies"]))
        payload["anomalies"][first_category].append({})
    elif projection == "claims":
        payload["claims"]["ouvertes"].append({})
    else:
        payload["manuals"]["1SPE"]["publication_eligible"] = True
    artifact_path.write_text(
        "# generated by inventory_collection.py\n"
        + yaml.safe_dump(payload, allow_unicode=True, sort_keys=True, width=120),
        encoding="utf-8",
    )
    inventory_module._validate_artifact_schema(
        payload,
        root=tmp_path,
        path=Path(relative_path),
    )

    completed = _run_inventory_cli(tmp_path, "--validate-model")
    result = json.loads(completed.stdout)

    assert completed.returncode == 6
    assert result["gate"] == "validate-model"
    assert any("projection" in reason for reason in result["reasons"])


def test_release_and_debt_gates_have_independent_documented_failures(
    tmp_path: Path
) -> None:
    _seed_cli_repository(tmp_path)

    release = _run_inventory_cli(tmp_path, "--release-strict")
    release_payload = json.loads(release.stdout)
    missing = _run_inventory_cli(tmp_path, "--fail-on-new")
    missing_payload = json.loads(missing.stdout)
    provisional_baseline = _baseline_contract_payload()
    provisional_baseline["updates"] = []
    provisional_baseline["provisional"] = True
    _write(
        tmp_path / "audit/ANOMALIES_BASELINE.json",
        json.dumps(provisional_baseline, ensure_ascii=False),
    )
    provisional = _run_inventory_cli(tmp_path, "--fail-on-new")
    provisional_payload = json.loads(provisional.stdout)

    assert release.returncode == 7
    assert release_payload["gate"] == "release-strict"
    assert release_payload["blocker_count"] > 0
    assert release_payload["reasons"] == sorted(release_payload["reasons"])
    assert set(release_payload["dimensions"]) == {
        "structure",
        "pedagogy",
        "regulation",
        "mathematics",
        "execution",
        "visual",
        "print",
    }
    assert missing.returncode == 5
    assert missing_payload["gate"] == "fail-on-new"
    assert any("absente" in reason for reason in missing_payload["reasons"])
    assert provisional.returncode == 5
    assert provisional_payload["gate"] == "fail-on-new"
    assert any("provisoire" in reason for reason in provisional_payload["reasons"])


def test_fail_on_new_uses_fingerprint_v1_and_accepts_disappearance(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_repository(tmp_path)
    _install_audit_schemas(tmp_path)
    retained = _active_debt("a" * 16)
    disappeared = _active_debt(
        "b" * 16,
        locator_key="missing|1SPE|disparu",
    )
    baseline = _baseline_contract_payload()
    baseline["provisional"] = True
    baseline["active"] = [retained, disappeared]
    baseline["resolved"] = []
    baseline["updates"] = []
    _append_baseline_update(
        baseline,
        inventory_module,
        reason="Gel audité avant comparaison de dette",
        timestamp="2026-07-23T10:00:00Z",
    )
    _write(
        tmp_path / "audit/ANOMALIES_BASELINE.json",
        json.dumps(baseline, ensure_ascii=False),
    )
    monkeypatch.setattr(
        inventory_module,
        "build_inventory",
        lambda _root: {
            "anomalies": {},
            "anomaly_qualifications": {},
        },
    )
    monkeypatch.setattr(
        inventory_module,
        "_current_active_debt",
        lambda _inventory: [retained],
    )

    improvement = inventory_module._fail_on_new_gate(tmp_path)

    assert improvement["success"] is True
    assert improvement["exit_code"] == 0

    new_debt = _active_debt(
        "c" * 16,
        locator_key="missing|1SPE|nouveau",
    )
    monkeypatch.setattr(
        inventory_module,
        "_current_active_debt",
        lambda _inventory: [retained, new_debt],
    )

    regression = inventory_module._fail_on_new_gate(tmp_path)

    assert regression["success"] is False
    assert regression["exit_code"] == 5
    assert any("nouvelle" in reason for reason in regression["reasons"])


def test_require_clean_handles_dirty_unborn_and_detached_repositories(
    tmp_path: Path
) -> None:
    unborn = tmp_path / "unborn"
    _init_repository(unborn)
    unborn_result = _run_inventory_cli(unborn, "--require-clean")

    detached = tmp_path / "detached"
    _init_repository(detached)
    detached_sha = _commit_repository(detached)
    (detached / ".git/HEAD").write_text(f"{detached_sha}\n", encoding="utf-8")
    detached_result = _run_inventory_cli(detached, "--require-clean")

    dirty = tmp_path / "dirty"
    tracked = _seed_cli_repository(dirty)
    _commit_repository(dirty)
    source = dirty / tracked[0]
    source.write_text(source.read_text(encoding="utf-8") + "# dirty\n", encoding="utf-8")
    dirty_result = _run_inventory_cli(dirty, "--require-clean")
    dirty_payload = json.loads(dirty_result.stdout)

    assert unborn_result.returncode == 0
    assert json.loads(unborn_result.stdout)["success"] is True
    assert unborn_result.stderr == ""
    assert detached_result.returncode == 0
    assert json.loads(detached_result.stdout)["success"] is True
    assert detached_result.stderr == ""
    assert dirty_result.returncode == 4
    assert dirty_payload["gate"] == "require-clean"
    assert f"modified_tracked:{tracked[0]}" in dirty_payload["reasons"]


def test_require_clean_rejects_relevant_untracked_sources(tmp_path: Path) -> None:
    _init_repository(tmp_path)
    _commit_repository(tmp_path)
    untracked = "NSI/chapitres/1NSI-TEST/cours/new.tex"
    _write(tmp_path / untracked, _meta(chapitre="1NSI-TEST", status="approved"))

    completed = _run_inventory_cli(tmp_path, "--require-clean")
    payload = json.loads(completed.stdout)

    assert completed.returncode == 4
    assert payload["reasons"] == [f"untracked_relevant:{untracked}"]


@pytest.mark.parametrize(
    "untracked",
    [
        pytest.param("NSI/extras/orphan.tex", id="transversal-tex"),
        pytest.param("NSI/scripts/assemble.py", id="transversal-assembler"),
        pytest.param(
            "Mathematiques/manuel-maths/gabarits/new-root.tex",
            id="transversal-latex-root",
        ),
    ],
)
def test_require_clean_rejects_untracked_transversal_model_sources(
    tmp_path: Path,
    untracked: str,
) -> None:
    _init_repository(tmp_path)
    _commit_repository(tmp_path)
    _write(tmp_path / untracked, "contenu non suivi\n")

    completed = _run_inventory_cli(tmp_path, "--require-clean")
    payload = json.loads(completed.stdout)

    assert completed.returncode == 4
    assert payload["reasons"] == [f"untracked_relevant:{untracked}"]


def test_require_clean_ignores_untracked_transversal_non_model_file(
    tmp_path: Path,
) -> None:
    _init_repository(tmp_path)
    _commit_repository(tmp_path)
    _write(tmp_path / "NSI/notes/wip.txt", "note locale hors modèle\n")

    completed = _run_inventory_cli(tmp_path, "--require-clean")
    payload = json.loads(completed.stdout)

    assert completed.returncode == 0
    assert payload["success"] is True
    assert payload["reasons"] == []


def test_combined_gate_order_is_clean_model_check_debt_release(tmp_path: Path) -> None:
    tracked = _seed_cli_repository(tmp_path)
    _commit_repository(tmp_path)
    source = tmp_path / tracked[0]
    source.write_text(source.read_text(encoding="utf-8") + "# dirty\n", encoding="utf-8")
    arguments = (
        "--release-strict",
        "--fail-on-new",
        "--check",
        "--validate-model",
        "--require-clean",
    )

    dirty = _run_inventory_cli(tmp_path, *arguments)
    dirty_payload = json.loads(dirty.stdout)
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "--", tracked[0]],
        check=True,
    )
    _commit_repository(tmp_path, "clean fixture")
    invalid_model = _run_inventory_cli(tmp_path, *arguments)
    invalid_model_payload = json.loads(invalid_model.stdout)

    assert dirty.returncode == 4
    assert dirty_payload["gate"] == "require-clean"
    assert invalid_model.returncode == 6
    assert invalid_model_payload["gate"] == "validate-model"


def test_report_continuation_scope_does_not_leak_after_a_blank_line(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    report = "Mathematiques/manuel-maths/DIRECTIVES_EN_COURS.md"
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        f"{base}/exercices/ex-1.tex": _meta(
            id="1SPE-TEST-EX-001", type_objet="exercice", status="approved"
        ),
        report: """# Etat 1SPE
- 1SPE-TEST : 1 exercice.
Suite enveloppee : 1 exercice.

- Regle generale : 2 exercices par case.
- Référence v4.1 corrigé.
- 1SPE-TEST : 3 ex remédiation.
""",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    claims = inventory_module.build_inventory(tmp_path)["report_reconciliation"][
        "claims"
    ]
    wrapped = [claim for claim in claims if claim["line"] == 3]
    general = [claim for claim in claims if claim["line"] == 5]

    assert wrapped[0]["scope"] == "chapter:1SPE-TEST"
    assert wrapped[0]["etat"] == "confirme"
    assert general[0]["scope"] == "directive:collection"
    assert general[0]["metric"] == "seuil_exercices_declares"
    assert general[0]["calculated"] is None
    assert general[0]["etat"] == "ouvert"
    assert not any(
        claim["line"] == 6 and claim["metric"] == "corriges" for claim in claims
    )
    remediation = next(claim for claim in claims if claim["line"] == 7)
    assert remediation["scope"] == "chapter:1SPE-TEST"
    assert remediation["metric"] == "exercices_remediation_declares"
    assert remediation["calculated"] is None
    assert remediation["etat"] == "ouvert"


def test_real_reports_expose_known_exercise_contradictions(inventory_module) -> None:
    inventory = inventory_module.build_inventory(ROOT)
    claims = inventory["report_reconciliation"]["claims"]

    total = next(
        claim
        for claim in claims
        if claim["path"] == "Mathematiques/manuel-maths/RAPPORT_FINAL_1SPE.md"
        and claim["scope"] == "manual:1SPE"
        and claim["metric"] == "exercices_principaux"
        and claim["declared"] == 471
    )
    assert total["calculated"] == 473
    assert total["etat"] == "contredit"
    trigonometrie = next(
        claim
        for claim in claims
        if claim["scope"] == "chapter:1SPE-TRIGONOMETRIE"
        and claim["metric"] == "exercices_principaux"
    )
    assert trigonometrie["declared"] == 50
    assert trigonometrie["calculated"] == 20
    assert trigonometrie["etat"] == "contredit"
    directive_completeness = next(
        claim
        for claim in claims
        if claim["path"] == "Mathematiques/manuel-maths/DIRECTIVES_EN_COURS.md"
        and claim["line"] == 50
        and claim["metric"] == "completude"
    )
    assert directive_completeness["declared"] is True
    assert directive_completeness["calculated"] is False
    assert directive_completeness["etat"] == "contredit"
