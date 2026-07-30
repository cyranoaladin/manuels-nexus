from __future__ import annotations

import importlib
import json
import re
import tomllib
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/ci-audit-collection.yml"
REQUIREMENTS = ROOT / "requirements-ci-audit.txt"
PYPROJECT = ROOT / "pyproject.toml"
DIMENSION_NAMES = {
    "execution",
    "mathematics",
    "pedagogy",
    "print",
    "regulation",
    "structure",
    "visual",
}


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(
    loader: _UniqueKeyLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[object, object]:
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key: {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


def _workflow() -> tuple[dict[object, object], str]:
    text = WORKFLOW.read_text(encoding="utf-8")
    payload = yaml.load(text, Loader=_UniqueKeyLoader)
    assert isinstance(payload, dict)
    return payload, text


def test_ci_configuration_is_explicit_and_pinned() -> None:
    pyproject = PYPROJECT.read_text(encoding="utf-8")
    assert 'addopts = "--import-mode=importlib"' in pyproject
    assert "branch = true" in pyproject
    assert "fail_under = " in pyproject
    assert "mypy_path = \".\"" in pyproject
    assert "explicit_package_bases = true" in pyproject
    config = tomllib.loads(pyproject)
    coverage_report = config["tool"]["coverage"]["report"]
    assert coverage_report["precision"] == 2
    assert coverage_report["fail_under"] == 76.83
    assert "ignore_errors" not in config["tool"]["mypy"]
    typed_files = set(config["tool"]["mypy"]["files"])
    assert typed_files == {
        "scripts/baseline_qualification.py",
        "scripts/check_charte_sync.py",
        "scripts/ci_audit_collection.py",
        "scripts/inventory_graph.py",
        "scripts/inventory_pdf.py",
        "scripts/inventory_reports.py",
    }
    assert "Dette de typage hors gate Phase 0" in pyproject

    lines = [
        line
        for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    ]
    assert lines
    assert all(re.fullmatch(r"[A-Za-z0-9_.-]+==[^=\s]+", line) for line in lines)
    normalized = {line.split("==", 1)[0].lower(): line for line in lines}
    for package in (
        "ast-serialize",
        "coverage",
        "jsonschema",
        "librt",
        "mypy",
        "pathspec",
        "pytest",
        "pytest-cov",
        "pyyaml",
        "ruff",
        "types-jsonschema",
        "types-pyyaml",
    ):
        assert package in normalized


def test_audit_workflow_has_minimal_permissions_and_immutable_actions() -> None:
    workflow, text = _workflow()
    assert workflow["permissions"] == {"contents": "read"}
    assert "pull_request" in workflow["on"]
    assert "push" in workflow["on"]
    assert "workflow_dispatch" in workflow["on"]
    assert "contents: write" not in text
    assert "pull-requests: write" not in text

    action_refs = re.findall(r"(?m)^\s*uses:\s*([^\s#]+)", text)
    assert action_refs
    assert all(re.fullmatch(r"[^@]+@[0-9a-f]{40}", ref) for ref in action_refs)
    checkout = next(
        step
        for step in workflow["jobs"]["audit-phase-0"]["steps"]
        if str(step.get("uses", "")).startswith("actions/checkout@")
    )
    assert "ref" not in checkout.get("with", {})
    assert "git branch --show-current" in text
    assert 'branch_name="${GITHUB_HEAD_REF:-$GITHUB_REF_NAME}"' in text
    assert 'git switch --create "$branch_name"' in text
    assert 'git rev-parse HEAD)" = "$GITHUB_SHA"' in text


def test_audit_workflow_runs_the_complete_unweakened_contract() -> None:
    workflow, text = _workflow()
    forbidden = (
        "--materialize-baseline-qualifications",
        "--update-baseline",
        "continue-on-error",
        "pytest.mark.skip",
        "pytest.mark.xfail",
        "--ignore=",
        "|| true",
    )
    assert all(token not in text for token in forbidden)
    assert "python -m ruff check" in text
    assert "python -m mypy" in text
    assert "python -m pytest" in text
    assert "--no-deps" in text
    assert "python -m pip check" in text
    assert "--import-mode=importlib" in text
    assert "--cov-branch" in text
    assert "--cov-report=xml:" in text
    assert "--cov-report=html:" in text
    assert "validate-data" in text
    assert "compare-generation" in text
    assert "run-gates" in text
    for gate in (
        "--require-clean",
        "--check",
        "--validate-model",
        "--fail-on-new",
        "--release-strict",
    ):
        assert gate in text
    assert "if: always()" in text
    assert "coverage.xml" in text
    helper = (ROOT / "scripts/ci_audit_collection.py").read_text(encoding="utf-8")
    assert '"generated-a"' in helper
    assert '"generated-b"' in helper
    assert "audit/BUILD_MANIFEST.json" in text
    artifact_dir = workflow["jobs"]["audit-phase-0"]["env"]["CI_ARTIFACT_DIR"]
    assert artifact_dir.startswith("${{ runner.temp }}/")
    assert "github.workspace" not in artifact_dir


@pytest.fixture()
def ci_module():
    path = ROOT / "scripts/ci_audit_collection.py"
    spec = importlib.util.spec_from_file_location(
        "ci_audit_collection_tests",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gate_payload(
    gate: str,
    *,
    success: bool,
    exit_code: int,
    reasons: list[str] | None = None,
) -> bytes:
    reasons = reasons or []
    dimensions = {name: "not_covered" for name in DIMENSION_NAMES}
    dimensions["structure"] = "passed" if success else "failed"
    if not success:
        dimensions["execution"] = "failed"
    return (
        json.dumps(
            {
                "blocker_count": len(reasons),
                "dimensions": dimensions,
                "exit_code": exit_code,
                "gate": gate,
                "reasons": reasons,
                "success": success,
            },
            sort_keys=True,
        )
        + "\n"
    ).encode()


def test_gate_contract_requires_exact_success_codes(ci_module) -> None:
    for gate in ("require-clean", "check", "validate-model", "fail-on-new"):
        payload = _gate_payload(gate, success=True, exit_code=0)
        assert ci_module.validate_gate_result(gate, 0, payload) == []
        assert ci_module.validate_gate_result(gate, 5, payload)


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("exit_code", False),
        ("exit_code", 0.0),
        ("exit_code", "0"),
        ("success", 1),
        ("success", "true"),
        ("blocker_count", False),
        ("blocker_count", 0.0),
        ("blocker_count", "0"),
    ],
)
def test_gate_contract_rejects_json_scalar_type_confusion(
    ci_module, field: str, invalid: object
) -> None:
    payload = json.loads(_gate_payload("check", success=True, exit_code=0))
    payload[field] = invalid
    stdout = (json.dumps(payload, sort_keys=True) + "\n").encode()
    assert ci_module.validate_gate_result("check", 0, stdout)


@pytest.mark.parametrize(
    "dimensions",
    [
        None,
        {},
        {"structure": "failed"},
        {"structure": "passed", "execution": "failed"},
        {"structure": "passed", "unknown": "passed"},
        {"structure": "passed", "execution": "inconnu"},
    ],
)
def test_success_gate_contract_rejects_invalid_dimensions(
    ci_module, dimensions: object
) -> None:
    payload = json.loads(_gate_payload("check", success=True, exit_code=0))
    payload["dimensions"] = dimensions
    stdout = (json.dumps(payload, sort_keys=True) + "\n").encode()
    assert ci_module.validate_gate_result("check", 0, stdout)


def test_gate_contract_rejects_a_missing_known_dimension(ci_module) -> None:
    payload = json.loads(_gate_payload("check", success=True, exit_code=0))
    del payload["dimensions"]["mathematics"]
    stdout = (json.dumps(payload, sort_keys=True) + "\n").encode()
    assert ci_module.validate_gate_result("check", 0, stdout)


@pytest.mark.parametrize(
    "dimensions",
    [
        None,
        {},
        {"structure": "failed"},
        {"execution": "failed", "structure": "passed"},
        {"execution": "passed", "structure": "failed"},
    ],
)
def test_release_contract_requires_failed_structure_and_execution(
    ci_module, dimensions: object
) -> None:
    reasons = [
        "1SPE:dette",
        "build_receipt_producteurs_non_intégrés",
        "dimension_non_couverte:mathematics",
        "dimension_non_couverte:pedagogy",
        "dimension_non_couverte:print",
        "dimension_non_couverte:regulation",
        "dimension_non_couverte:visual",
    ]
    payload = json.loads(
        _gate_payload(
            "release-strict",
            success=False,
            exit_code=7,
            reasons=reasons,
        )
    )
    payload["dimensions"] = dimensions
    stdout = (json.dumps(payload, sort_keys=True) + "\n").encode()
    assert ci_module.validate_gate_result(
        "release-strict",
        7,
        stdout,
        repeated_stdout=stdout,
    )


def test_release_contract_requires_exact_deterministic_real_debt(ci_module) -> None:
    reasons = [
        "1SPE:anomalie:blocking_statuses:anomalies.blocking_statuses:1344",
        "build_receipt_producteurs_non_intégrés",
        "dimension_non_couverte:mathematics",
        "dimension_non_couverte:pedagogy",
        "dimension_non_couverte:print",
        "dimension_non_couverte:regulation",
        "dimension_non_couverte:visual",
    ]
    payload = _gate_payload(
        "release-strict",
        success=False,
        exit_code=7,
        reasons=reasons,
    )
    assert (
        ci_module.validate_gate_result(
            "release-strict",
            7,
            payload,
            repeated_stdout=payload,
        )
        == []
    )
    assert ci_module.validate_gate_result(
        "release-strict",
        7,
        payload,
        repeated_stdout=payload + b" ",
    )
    missing_integration = _gate_payload(
        "release-strict",
        success=False,
        exit_code=7,
        reasons=[reason for reason in reasons if "producteurs" not in reason],
    )
    assert ci_module.validate_gate_result(
        "release-strict",
        7,
        missing_integration,
        repeated_stdout=missing_integration,
    )
    wrong_code = _gate_payload(
        "release-strict",
        success=False,
        exit_code=6,
        reasons=reasons,
    )
    assert ci_module.validate_gate_result(
        "release-strict",
        7,
        wrong_code,
        repeated_stdout=wrong_code,
    )


def test_release_contract_matches_uncovered_dimensions_to_reasons(ci_module) -> None:
    reasons = [
        "1SPE:dette",
        "build_receipt_producteurs_non_intégrés",
        "dimension_non_couverte:mathematics",
        "dimension_non_couverte:pedagogy",
        "dimension_non_couverte:print",
        "dimension_non_couverte:regulation",
        "dimension_non_couverte:visual",
    ]
    payload = json.loads(
        _gate_payload(
            "release-strict",
            success=False,
            exit_code=7,
            reasons=reasons,
        )
    )

    contradictory = dict(payload)
    contradictory["dimensions"] = dict(payload["dimensions"])
    contradictory["dimensions"]["mathematics"] = "passed"
    contradictory_stdout = (
        json.dumps(contradictory, sort_keys=True) + "\n"
    ).encode()
    assert ci_module.validate_gate_result(
        "release-strict",
        7,
        contradictory_stdout,
        repeated_stdout=contradictory_stdout,
    )

    missing_reason = dict(payload)
    missing_reason["reasons"] = [
        reason
        for reason in reasons
        if reason != "dimension_non_couverte:mathematics"
    ]
    missing_reason["blocker_count"] = len(missing_reason["reasons"])
    missing_stdout = (json.dumps(missing_reason, sort_keys=True) + "\n").encode()
    assert ci_module.validate_gate_result(
        "release-strict",
        7,
        missing_stdout,
        repeated_stdout=missing_stdout,
    )

    extra_reason = dict(payload)
    extra_reason["reasons"] = reasons + ["dimension_non_couverte:execution"]
    extra_reason["blocker_count"] = len(extra_reason["reasons"])
    extra_stdout = (json.dumps(extra_reason, sort_keys=True) + "\n").encode()
    assert ci_module.validate_gate_result(
        "release-strict",
        7,
        extra_stdout,
        repeated_stdout=extra_stdout,
    )


def test_tracked_data_parser_rejects_duplicate_yaml_keys(
    tmp_path: Path, ci_module
) -> None:
    path = tmp_path / "duplicate.yaml"
    path.write_text("value: 1\nvalue: 2\n", encoding="utf-8")
    with pytest.raises(ci_module.CIAuditError, match="duplicate"):
        ci_module.parse_structured_file(path)


def test_generation_comparison_is_byte_exact(tmp_path: Path, ci_module) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    (first / "artifact.json").write_bytes(b'{"value": 1}\n')
    (second / "artifact.json").write_bytes(b'{"value": 1}\n')
    assert ci_module.compare_generated_trees(first, second) == []
    (second / "artifact.json").write_bytes(b'{ "value": 1 }\n')
    assert ci_module.compare_generated_trees(first, second) == [
        "content:artifact.json"
    ]


def test_generation_artifact_directory_refuses_stale_residue(
    tmp_path: Path, ci_module
) -> None:
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    stale = artifact_dir / "stale.json"
    stale.write_text("{}\n", encoding="utf-8")
    with pytest.raises(ci_module.CIAuditError, match="non vide"):
        ci_module.ensure_empty_artifact_directory(artifact_dir)
    assert stale.read_text(encoding="utf-8") == "{}\n"
