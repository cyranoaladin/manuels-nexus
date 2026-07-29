from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import warnings
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path

import jsonschema
import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inventory_collection.py"
GENERATOR_COMPONENTS = (
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


def _run_inventory_cli(repository: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repository), *arguments],
        capture_output=True,
        text=True,
        check=False,
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


def test_build_inventory_aggregates_objects_and_keeps_four_manuals(
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

    assert list(inventory["manuals"]) == ["1NSI", "1SPE", "TNSI", "TSPE_2026_2027"]
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
                "occurrence_count": 2,
                "owner": "équipe mathématiques",
                "severity": "blocking",
            }
        ],
        "artifact_type": "anomalies_baseline",
        "fingerprint_schema_version": 1,
        "generated_at_utc": "2026-07-22T10:00:00Z",
        "generated_by": "inventory_collection.py",
        "git_sha": git_sha,
        "model_digest": "sha256:" + "c" * 64,
        "previous_baseline_digest": None,
        "provenance": {"head_sha": git_sha},
        "provisional": True,
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
        "git_sha",
        "previous_baseline_digest",
        "provisional",
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


def _build_manifest_contract_payload() -> dict[str, object]:
    return {
        "artifact_type": "build_manifest",
        "build_state_digest": "sha256:" + "1" * 64,
        "builds": [
            {
                "gate_results": {
                    "release_strict": {"blocker_count": 42, "passed": False},
                    "validate_model": {"passed": True},
                },
                "git_sha": "2" * 40,
                "included_objects": ["OBJ-SECOND", "OBJ-FIRST"],
                "model_digest": "sha256:" + "3" * 64,
                "page_count": 128,
                "pdf": "build/manuels/1SPE-professeur.pdf",
                "sha256": "sha256:" + "4" * 64,
                "source_digest": "sha256:" + "5" * 64,
                "tool_versions": {"latexmk": "4.86a", "pdflatex": "3.141592653"},
                "variant": "manuel_professeur",
            }
        ],
        "generated_by": "inventory_collection.py",
        "provenance": {"branch": "finalisation/collection-v1"},
        "schema_ref": "audit/schemas/v1/build-manifest.schema.json",
        "schema_version": 1,
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
        "gate_results",
        "git_sha",
        "included_objects",
        "model_digest",
        "page_count",
        "pdf",
        "sha256",
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
parser.add_argument("--variant", choices=["eleve", "professeur"])
""",
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert analysis["constants"] == {
        "CHAPITRES": ["1SPE-TEST", "1SPE-AUTRE"],
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
        ("TNSI", "manuel", "aucun assembleur de manuel suivi"),
        ("TSPE_2026_2027", "manuel", "aucun assembleur de manuel suivi"),
    }
    assert {
        item["cible"] for item in inventory["anomalies"]["chapters_not_in_manual"]
    } == {"1NSI-TEST", "TNSI-TEST", "TSPE-TEST"}


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
            "status": "counted",
            "variant": "eleve",
        }
    ]


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
            "status": "page_count_unavailable",
            "variant": None,
        }
    ]


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


def test_all_relevant_tracked_tex_sources_are_scanned_for_broken_inputs(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    master = "NSI/gabarits/master.tex"
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
    math_report = "Mathematiques/manuel-maths/ETAT_COLLECTION.md"
    sources = {
        root_report: "# Ancien etat\n",
        history: "# Archive de l'ancien etat\n",
        generated: "<!-- AUTO-GENERE PAR inventory_collection.py -->\n",
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

    assert list(matrix["manuals"]) == ["1NSI", "1SPE", "TNSI", "TSPE_2026_2027"]
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
            "path": "MANUEL_1NSI_v1.pdf",
            "reason": None,
            "scope": "manual",
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
        completed = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        expected[name] = completed.stdout.splitlines()[0].strip()

    assert versions == expected
    assert not isinstance(versions["git"], bool)
    assert versions["texlive"] != versions["git"]


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

    def fail_second_replace(source: Path | str, target: Path | str) -> None:
        nonlocal replacements
        replacements += 1
        if replacements == 2:
            raise OSError("injection échec remplacement 2")
        original_replace(source, target)

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


def test_check_only_never_takes_generation_lock_or_creates_temporary_files(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_cli_repository(tmp_path)
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
    _write(
        tmp_path / "audit/ANOMALIES_BASELINE.json",
        json.dumps({"provisional": True}),
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
    assert total["calculated"] == 464
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
