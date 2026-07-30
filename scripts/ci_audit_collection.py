#!/usr/bin/env python3
"""CI-only validators for the Phase 0 collection audit contract."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml


GENERATED_ARTIFACTS = (
    "ETAT_COLLECTION.md",
    "audit/AUDIT_CONSOLIDE.md",
    "audit/ECARTS_ET_CONTRADICTIONS.yaml",
    "audit/INVENTAIRE_COLLECTION.json",
    "audit/INVENTAIRE_COLLECTION.md",
    "audit/MATRICE_LIVRABLES.yaml",
)
SUCCESS_GATES = (
    "require-clean",
    "check",
    "validate-model",
    "fail-on-new",
)
RELEASE_GATE = "release-strict"
EXPECTED_GATE_EXIT_CODES = {
    "require-clean": 0,
    "check": 0,
    "validate-model": 0,
    "fail-on-new": 0,
    "release-strict": 7,
}
GATE_DIMENSIONS = frozenset(
    {
        "execution",
        "mathematics",
        "pedagogy",
        "print",
        "regulation",
        "structure",
        "visual",
    }
)
GATE_DIMENSION_STATUSES = frozenset({"failed", "not_covered", "passed"})


class CIAuditError(RuntimeError):
    """Raised when CI evidence does not satisfy the audit contract."""


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(
    loader: _UniqueKeyLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
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


def parse_structured_file(path: Path) -> Any:
    """Parse one JSON or YAML file and reject duplicate YAML mapping keys."""

    try:
        text = path.read_text(encoding="utf-8")
        if path.suffix.casefold() == ".json":
            return json.loads(text)
        if path.suffix.casefold() in {".yaml", ".yml"}:
            return yaml.load(text, Loader=_UniqueKeyLoader)
    except (OSError, UnicodeError, json.JSONDecodeError, yaml.YAMLError) as exc:
        raise CIAuditError(f"{path}: {exc}") from exc
    raise CIAuditError(f"format structuré non pris en charge: {path}")


def _tracked_structured_files(root: Path) -> list[Path]:
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "-z",
                "--",
                "*.json",
                "*.yaml",
                "*.yml",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CIAuditError("inventaire Git des JSON/YAML indisponible") from exc
    return [
        root / os.fsdecode(value)
        for value in result.stdout.split(b"\0")
        if value
    ]


def validate_tracked_data(root: Path, output: Path) -> dict[str, Any]:
    """Parse every tracked JSON/YAML file with its real parser."""

    paths = _tracked_structured_files(root)
    failures: list[str] = []
    counts = {"json": 0, "yaml": 0}
    for path in paths:
        suffix = path.suffix.casefold()
        counts["json" if suffix == ".json" else "yaml"] += 1
        try:
            parse_structured_file(path)
        except CIAuditError as exc:
            failures.append(str(exc))
    report = {
        "failure_count": len(failures),
        "failures": failures,
        "files": len(paths),
        "formats": counts,
        "success": not failures,
    }
    _write_json(output, report)
    if failures:
        raise CIAuditError(
            f"{len(failures)} fichier(s) JSON/YAML invalide(s)"
        )
    return report


def compare_generated_trees(first: Path, second: Path) -> list[str]:
    """Return deterministic path/content differences between two trees."""

    first_files = {
        path.relative_to(first).as_posix(): path
        for path in first.rglob("*")
        if path.is_file()
    }
    second_files = {
        path.relative_to(second).as_posix(): path
        for path in second.rglob("*")
        if path.is_file()
    }
    differences = [
        f"missing-second:{path}"
        for path in sorted(first_files.keys() - second_files.keys())
    ]
    differences.extend(
        f"missing-first:{path}"
        for path in sorted(second_files.keys() - first_files.keys())
    )
    differences.extend(
        f"content:{path}"
        for path in sorted(first_files.keys() & second_files.keys())
        if first_files[path].read_bytes() != second_files[path].read_bytes()
    )
    return differences


def _assert_clean_repository(root: Path) -> None:
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CIAuditError("état Git indisponible avant génération") from exc
    if result.stdout:
        raise CIAuditError("la comparaison exige un dépôt source propre")


def _clone_clean_repository(root: Path, destination: Path) -> None:
    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--no-hardlinks",
                "--quiet",
                str(root),
                str(destination),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CIAuditError("copie Git propre impossible") from exc
    _assert_clean_repository(destination)


def _generate_inventory(root: Path) -> None:
    environment = dict(os.environ)
    environment.update(
        {
            "LC_ALL": "C.UTF-8",
            "PYTHONHASHSEED": "0",
            "TZ": "UTC",
        }
    )
    try:
        result = subprocess.run(
            [sys.executable, "scripts/inventory_collection.py"],
            cwd=root,
            env=environment,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as exc:
        raise CIAuditError("générateur d'inventaire indisponible") from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise CIAuditError(
            f"génération échouée avec le code {result.returncode}: {detail}"
        )


def _copy_generated_artifacts(root: Path, destination: Path) -> None:
    for relative in GENERATED_ARTIFACTS:
        source = root / relative
        if not source.is_file():
            raise CIAuditError(f"artefact généré absent: {relative}")
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if target.suffix.casefold() in {".json", ".yaml", ".yml"}:
            parse_structured_file(target)


def ensure_empty_artifact_directory(path: Path) -> None:
    """Create an artifact directory or reject existing residue without deleting it."""

    if path.exists():
        if not path.is_dir() or path.is_symlink():
            raise CIAuditError(f"destination d'artefacts invalide: {path}")
        if next(path.iterdir(), None) is not None:
            raise CIAuditError(
                f"destination d'artefacts non vide (résidus refusés): {path}"
            )
        return
    path.mkdir(parents=True)


def compare_generation(root: Path, artifact_dir: Path) -> dict[str, Any]:
    """Generate twice in independent clean clones and compare exact bytes."""

    _assert_clean_repository(root)
    ensure_empty_artifact_directory(artifact_dir)
    first_artifacts = artifact_dir / "generated-a"
    second_artifacts = artifact_dir / "generated-b"
    with tempfile.TemporaryDirectory(prefix="nexus-ci-generation-") as temporary:
        temporary_root = Path(temporary)
        first = temporary_root / "first"
        second = temporary_root / "second"
        _clone_clean_repository(root, first)
        _clone_clean_repository(root, second)
        _generate_inventory(first)
        _generate_inventory(second)
        _copy_generated_artifacts(first, first_artifacts)
        _copy_generated_artifacts(second, second_artifacts)
    differences = compare_generated_trees(first_artifacts, second_artifacts)
    report = {
        "artifacts": list(GENERATED_ARTIFACTS),
        "differences": differences,
        "success": not differences,
    }
    _write_json(artifact_dir / "generation-comparison.json", report)
    if differences:
        raise CIAuditError(
            "génération non déterministe: " + ", ".join(differences)
        )
    return report


def _decode_gate_payload(stdout: bytes) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = json.loads(stdout.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        return None, [f"sortie JSON invalide: {exc}"]
    if not isinstance(payload, dict):
        return None, ["la sortie du gate n'est pas un objet JSON"]
    return payload, []


def _decode_gate_stream(content: bytes) -> str:
    return content.decode("utf-8", errors="replace")


def validate_gate_result(
    gate: str,
    return_code: int,
    stdout: bytes,
    *,
    repeated_stdout: bytes | None = None,
) -> list[str]:
    """Validate exact gate exit/payload semantics without accepting soft failures."""

    payload, errors = _decode_gate_payload(stdout)
    if payload is None:
        return errors
    expected_code = EXPECTED_GATE_EXIT_CODES[gate]
    expected_success = gate != RELEASE_GATE
    for field, expected in (
        ("gate", gate),
        ("exit_code", expected_code),
        ("success", expected_success),
    ):
        actual = payload.get(field)
        if type(actual) is not type(expected) or actual != expected:
            errors.append(
                f"{gate}: {field}={actual!r}, attendu {expected!r}"
            )
    if type(return_code) is not int or return_code != expected_code:
        errors.append(
            f"{gate}: code processus {return_code}, attendu {expected_code}"
        )
    reasons = payload.get("reasons")
    blocker_count = payload.get("blocker_count")
    if not isinstance(reasons, list) or not all(
        isinstance(reason, str) for reason in reasons
    ):
        errors.append(f"{gate}: reasons invalide")
        reasons = []
    if (
        type(blocker_count) is not int
        or blocker_count < 0
        or blocker_count != len(reasons)
    ):
        errors.append(f"{gate}: blocker_count incohérent")
    dimensions = payload.get("dimensions")
    if not isinstance(dimensions, dict) or not dimensions:
        errors.append(f"{gate}: dimensions invalides")
        dimensions = {}
    else:
        if any(
            type(name) is not str or name not in GATE_DIMENSIONS
            for name in dimensions
        ):
            errors.append(f"{gate}: nom de dimension inconnu")
        if set(dimensions) != GATE_DIMENSIONS:
            errors.append(f"{gate}: ensemble de dimensions incomplet")
        if any(
            type(status) is not str
            or status not in GATE_DIMENSION_STATUSES
            for status in dimensions.values()
        ):
            errors.append(f"{gate}: statut de dimension inconnu")
    if gate == RELEASE_GATE:
        if dimensions.get("structure") != "failed":
            errors.append("release-strict: structure non échouée")
        if dimensions.get("execution") != "failed":
            errors.append("release-strict: exécution non échouée")
        if repeated_stdout != stdout:
            errors.append("release-strict: sortie non déterministe")
        if not reasons:
            errors.append("release-strict: aucune dette réelle")
        if "build_receipt_producteurs_non_intégrés" not in reasons:
            errors.append("release-strict: dette d'intégration absente")
        if not any(reason.startswith("1SPE:") for reason in reasons):
            errors.append("release-strict: dette 1SPE absente")
        uncovered_dimensions = {
            name
            for name, status in dimensions.items()
            if status == "not_covered"
        }
        dimension_reasons = [
            reason.removeprefix("dimension_non_couverte:")
            for reason in reasons
            if reason.startswith("dimension_non_couverte:")
        ]
        if (
            set(dimension_reasons) != uncovered_dimensions
            or len(dimension_reasons) != len(set(dimension_reasons))
        ):
            errors.append(
                "release-strict: raisons et dimensions non couvertes incohérentes"
            )
    else:
        if dimensions.get("structure") != "passed":
            errors.append(f"{gate}: structure non passée")
        if "failed" in dimensions.values():
            errors.append(f"{gate}: dimension échouée malgré le succès")
        if reasons:
            errors.append(f"{gate}: raisons présentes malgré le succès")
    return errors


def _run_gate(root: Path, gate: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [sys.executable, "scripts/inventory_collection.py", f"--{gate}"],
        cwd=root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_gates(root: Path, output_dir: Path) -> dict[str, Any]:
    """Run all Phase 0 gates and verify their exact expected contracts."""

    output_dir.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    results: dict[str, dict[str, Any]] = {}
    for gate in (*SUCCESS_GATES, RELEASE_GATE):
        completed = _run_gate(root, gate)
        repeated = _run_gate(root, gate) if gate == RELEASE_GATE else None
        (output_dir / f"{gate}.json").write_bytes(completed.stdout)
        gate_stdout = _decode_gate_stream(completed.stdout)
        gate_stderr = _decode_gate_stream(completed.stderr)
        if completed.stderr:
            failures.append(
                f"{gate}: stderr non vide: "
                + completed.stderr.decode("utf-8", errors="replace").strip()
            )
        if repeated is not None:
            (output_dir / f"{gate}.repeat.json").write_bytes(repeated.stdout)
            repeated_stdout = _decode_gate_stream(repeated.stdout)
            repeated_stderr = _decode_gate_stream(repeated.stderr)
            if repeated.stderr:
                failures.append(
                    f"{gate} répété: stderr non vide: "
                    + repeated.stderr.decode(
                        "utf-8", errors="replace"
                    ).strip()
                )
            if repeated.returncode != completed.returncode:
                failures.append(
                    f"{gate}: code non déterministe "
                    f"{completed.returncode}/{repeated.returncode}"
                )
        gate_failures = validate_gate_result(
            gate,
            completed.returncode,
            completed.stdout,
            repeated_stdout=(
                repeated.stdout if repeated is not None else None
            ),
        )
        failures.extend(gate_failures)
        payload, decode_errors = _decode_gate_payload(completed.stdout)
        results[gate] = {
            "contract_errors": decode_errors + gate_failures,
            "payload": payload,
            "process_code": completed.returncode,
            "stdout": gate_stdout,
            "stderr": gate_stderr,
        }
        if repeated is not None:
            results[gate]["repeat"] = {
                "process_code": repeated.returncode,
                "stdout": repeated_stdout,
                "stderr": repeated_stderr,
            }
    report = {
        "failure_count": len(failures),
        "failures": failures,
        "gates": results,
        "success": not failures,
    }
    _write_json(output_dir / "gate-summary.json", report)
    if failures:
        raise CIAuditError(
            f"contrat des gates non satisfait ({len(failures)} erreur(s))"
        )
    return report


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _root_path(value: str) -> Path:
    root = Path(value).resolve(strict=True)
    if not root.is_dir():
        raise argparse.ArgumentTypeError("la racine doit être un dossier")
    return root


def _output_path(value: str) -> Path:
    return Path(value).resolve()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-data")
    validate.add_argument("--root", type=_root_path, default=Path.cwd())
    validate.add_argument("--output", type=_output_path, required=True)

    generate = subparsers.add_parser("compare-generation")
    generate.add_argument("--root", type=_root_path, default=Path.cwd())
    generate.add_argument("--artifact-dir", type=_output_path, required=True)

    gates = subparsers.add_parser("run-gates")
    gates.add_argument("--root", type=_root_path, default=Path.cwd())
    gates.add_argument("--output-dir", type=_output_path, required=True)
    for gate in (*SUCCESS_GATES, RELEASE_GATE):
        gates.add_argument(f"--{gate}", action="store_true", required=True)
    return parser


def _run() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "validate-data":
            validate_tracked_data(args.root, args.output)
        elif args.command == "compare-generation":
            compare_generation(args.root, args.artifact_dir)
        elif args.command == "run-gates":
            run_gates(args.root, args.output_dir)
        else:  # pragma: no cover - argparse rejects unknown commands
            raise CIAuditError(f"commande inconnue: {args.command}")
    except CIAuditError as exc:
        print(f"CI AUDIT: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_run())
