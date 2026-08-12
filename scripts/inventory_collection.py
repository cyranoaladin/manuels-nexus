#!/usr/bin/env python3
"""Build the canonical, filesystem-derived inventory for the Nexus collection.

The model inventories content objects, reference graphs, declared assemblies and
tracked PDF artifacts.  Report reconciliation and rendering belong to the later
Phase 0 layers.
"""

from __future__ import annotations

import importlib
import argparse
import ctypes
import json
import hashlib
import posixpath
import re
import subprocess
import sys
import os
import secrets
import stat
import unicodedata
import shutil
import tempfile
import datetime
import time
from fnmatch import fnmatch
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Sequence
from types import MappingProxyType
from typing import Any, Mapping

import yaml

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX platforms cannot reclaim locks
    fcntl = None

_SCRIPTS_ROOT = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPTS_ROOT.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _import_legacy_module(name: str):
    """Import a sibling module when package import is unavailable."""
    spec = importlib.util.find_spec(name)
    if spec is not None:
        return importlib.import_module(name)
    module_path = _SCRIPTS_ROOT / f"{name}.py"
    if not module_path.is_file():
        raise ModuleNotFoundError(name)
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ModuleNotFoundError(name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


try:
    from scripts import inventory_assembly as _assembly_core
    from scripts import baseline_qualification as _baseline_qualification
    from scripts import inventory_graph as _graph_core
    from scripts import inventory_pdf as _pdf_core
    from scripts import inventory_reports as _report_core
except ModuleNotFoundError:  # direct execution: python scripts/inventory_collection.py
    _assembly_core = _import_legacy_module("inventory_assembly")
    _baseline_qualification = _import_legacy_module("baseline_qualification")
    _graph_core = _import_legacy_module("inventory_graph")
    _pdf_core = _import_legacy_module("inventory_pdf")
    _report_core = _import_legacy_module("inventory_reports")


SCHEMA_VERSION = 1
FINGERPRINT_SCHEMA_VERSION = 1
PDFINFO_TIMEOUT_SECONDS = 10
LOCK_TIMEOUT_SECONDS = 20
LOCK_STALE_SECONDS = 20
LOCK_POLL_SECONDS = 0.1
GENERIC_LOCK_FILE = ".inventory_collection.lock"

SOURCE_ROLES_FILE = "audit/SOURCE_ROLES.yaml"
ANOMALY_DISPOSITIONS_FILE = "audit/ANOMALY_DISPOSITIONS.yaml"
ANOMALIES_BASELINE_FILE = "audit/ANOMALIES_BASELINE.json"
BASELINE_QUALIFICATION_POLICY_FILE = "audit/BASELINE_QUALIFICATION_POLICY.yaml"
UNQUALIFIED_ANOMALIES_JSON_FILE = "audit/UNQUALIFIED_ANOMALIES.json"
UNQUALIFIED_ANOMALIES_MD_FILE = "audit/UNQUALIFIED_ANOMALIES.md"
BASELINE_UPDATE_REPORT_FILE = "audit/BASELINE_UPDATE_REPORT.md"
BASELINE_FREEZE_REPORT_FILE = "audit/BASELINE_FREEZE_REPORT.md"
BUILD_MANIFEST_FILE = "audit/BUILD_MANIFEST.json"
BUILD_PRODUCERS_FILE = "audit/BUILD_PRODUCERS.yaml"
CANONICAL_BUILD_RECORDER = "scripts/build_manifest.py"
_EMPTY_MANIFEST_REFRESH_CAPABILITY = object()
_EMPTY_MANIFEST_BRANCH_REBIND_CAPABILITY = object()
_STALE_MANIFEST_INVALIDATION_CAPABILITY = object()

SCHEMA_REGISTRY: Mapping[str, Mapping[int, str]] = MappingProxyType(
    {
        "inventory_collection": MappingProxyType(
            {1: "audit/schemas/v1/inventory-collection.schema.json"}
        ),
        "ecarts_et_contradictions": MappingProxyType(
            {1: "audit/schemas/v1/ecarts-et-contradictions.schema.json"}
        ),
        "matrice_livrables": MappingProxyType(
            {1: "audit/schemas/v1/matrice-livrables.schema.json"}
        ),
        "source_roles": MappingProxyType(
            {1: "audit/schemas/v1/source-roles.schema.json"}
        ),
        "anomaly_dispositions": MappingProxyType(
            {1: "audit/schemas/v1/anomaly-dispositions.schema.json"}
        ),
        "baseline_qualification_policy": MappingProxyType(
            {1: "audit/schemas/v1/baseline-qualification-policy.schema.json"}
        ),
        "unqualified_anomalies": MappingProxyType(
            {1: "audit/schemas/v1/unqualified-anomalies.schema.json"}
        ),
        "anomalies_baseline": MappingProxyType(
            {1: "audit/schemas/v1/anomalies-baseline.schema.json"}
        ),
        "build_manifest": MappingProxyType(
            {1: "audit/schemas/v1/build-manifest.schema.json"}
        ),
        "build_producers": MappingProxyType(
            {1: "audit/schemas/v1/build-producers.schema.json"}
        ),
        "1nsi_content_reviews": MappingProxyType(
            {1: "audit/schemas/v1/1nsi-content-review.schema.json"}
        ),
        "1nsi_p0_correction_attestation": MappingProxyType(
            {1: "audit/schemas/v1/1nsi-p0-correction-attestation.schema.json"}
        ),
    }
)

OUTPUT_FILES = (
    "INVENTAIRE_COLLECTION.json",
    "INVENTAIRE_COLLECTION.md",
    "ECARTS_ET_CONTRADICTIONS.yaml",
    "MATRICE_LIVRABLES.yaml",
)
REQUIRED_ARTIFACT_FIELDS = {
    "artifact_type",
    "generated_by",
    "model_digest",
    "schema_ref",
    "schema_version",
    "source_digest",
    "provenance",
}
REQUIRED_YAML_FIELDS = REQUIRED_ARTIFACT_FIELDS
REQUIRED_JSON_FIELDS = REQUIRED_ARTIFACT_FIELDS

CANONICAL_MODEL_FIELDS = (
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
)

ANOMALY_DISPOSITIONS = (
    "open_debt",
    "false_positive",
    "generated_dependency",
    "harvest_candidate",
    "intentional_reuse",
    "accepted_exception",
    "fixed",
)

ANOMALY_DISPOSITION_BLOCKS = {
    "open_debt": True,
    "false_positive": False,
    "generated_dependency": False,
    "harvest_candidate": False,
    "intentional_reuse": False,
    "accepted_exception": False,
    "fixed": False,
}

AUTOGEN_MARKER = "# generated by inventory_collection.py"
AUTOGEN_REPORT_MARKERS = (
    "AUTO-GENÉRÉ PAR inventory_collection.py",
    "AUTO-GÉNÉRÉ PAR inventory_collection.py",
    "generated by inventory_collection.py",
    "# generated by inventory_collection.py",
    "generated_by: inventory_collection.py",
)
AUTOGEN_REPORT_MARKER = "# generated by inventory_collection.py"
REPORT_LINE_LIMIT = 250
GATE_USAGE_CODE = 2
GATE_CHECK_CODE = 3
GATE_CLEAN_CODE = 4
GATE_BASELINE_CODE = 5
GATE_VALIDATE_CODE = 6
GATE_RELEASE_CODE = 7
GATE_BASELINE_UPDATE_CODE = 8
GATE_VALID_CLEAN_STATES = frozenset({"worktree", "head"})
BASELINE_READY_CHECK_NAMES = (
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
)

GATE_DIMENSIONS = (
    "structure",
    "pedagogy",
    "regulation",
    "mathematics",
    "execution",
    "visual",
    "print",
)
GATE_DIMENSION_STATUSES = frozenset({"passed", "failed", "not_covered"})
GATE_DIMENSION_TEMPLATE: dict[str, str] = {
    dimension: "not_covered" for dimension in GATE_DIMENSIONS
}
PUBLICATION_GATE_TEMPLATE: dict[str, bool] = {
    "structural": True,
    "pedagogical": False,
    "regulatory": False,
    "mathematical": False,
    "execution": False,
    "visual": False,
    "print": False,
}
MODEL_ARTIFACTS: Mapping[str, str] = MappingProxyType(
    {
        "audit/INVENTAIRE_COLLECTION.json": "inventory_collection",
        "audit/ECARTS_ET_CONTRADICTIONS.yaml": "ecarts_et_contradictions",
        "audit/MATRICE_LIVRABLES.yaml": "matrice_livrables",
    }
)
DEFAULT_MANAGED_OUTPUT_PATHS = frozenset(
    {
        "ETAT_COLLECTION.md",
        "audit/AUDIT_CONSOLIDE.md",
        "audit/ECARTS_ET_CONTRADICTIONS.yaml",
        "audit/INVENTAIRE_COLLECTION.json",
        "audit/INVENTAIRE_COLLECTION.md",
        "audit/MATRICE_LIVRABLES.yaml",
    }
)
GENERATOR_COMPONENT_PATHS = (
    "baseline_qualification.py",
    "build_manifest.py",
    "inventory_collection.py",
    "inventory_reports.py",
    "inventory_graph.py",
    "inventory_assembly.py",
    "inventory_pdf.py",
)

DEFAULT_SOURCE_ROLE_PATTERNS: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        "excluded": (
            ".github/**/cache/**",
            "**/__pycache__/**",
        ),
        "fixture": (
            "tests/**",
            "**/tests/**",
            "**/fixtures/**",
            "**/testdata/**",
        ),
        "harvest_candidate": (
            "**/_harvest/*.candidate.tex",
            "**/_harvest/**/*.candidate.tex",
        ),
        "visual_reference": (
            "**/gabarits/reference-*/**",
            "**/reference-*/**",
            "**/baselines/visual/**",
            "**/validations/*.visual.json",
            "**/validations/**/*.visual.json",
            "**/validations/diff_visuel*.md",
            "**/validations/**/diff_visuel*.md",
            "**/validations/v5-it*/**",
        ),
        "archive": (
            "**/archive/**",
            "**/archives/**",
            "**/historique/**",
        ),
        "generated_dependency": (
            "Mathematiques/manuel-maths/build/maquette-v5/renvois.tex",
            "**/build/*.pdf",
            "**/build/*.tex",
            "**/build/*.cls",
            "**/build/**/*.pdf",
            "**/build/**/*.tex",
            "**/build/**/*.cls",
        ),
        "validation_reference": (
            "**/validations/**",
            "audit/**",
            "audit/schemas/**/*.schema.json",
        ),
        "production_object": (
            "Mathematiques/manuel-maths/chapitres/**",
            "NSI/chapitres/**",
        ),
        "transversal": (
            "**/transversal/**",
            "**/build/**/*.log",
            "**/build/**/*.aux",
        ),
    }
)
DEFAULT_SOURCE_ROLE = "transversal"
DEFAULT_SOURCE_ROLE_ORDER = (
    "excluded",
    "fixture",
    "harvest_candidate",
    "visual_reference",
    "archive",
    "generated_dependency",
    "validation_reference",
    "production_object",
    "transversal",
)
BLOCKING_LATEX_REFERENCE_SOURCE_ROLES = frozenset(
    {"generated_dependency", "production_object", "transversal"}
)
ORPHAN_SOURCE_ROLES = frozenset({"production_object", "transversal"})
ORPHAN_ROOT_SOURCE_ROLES = frozenset(
    {"generated_dependency", "production_object", "transversal"}
)
ORPHAN_TRAVERSAL_SOURCE_ROLES = frozenset(
    {"generated_dependency", "production_object", "transversal"}
)
STATIC_ASSEMBLY_ROOT_SOURCE_ROLES = frozenset(
    {"generated_dependency", "production_object", "transversal"}
)
STATIC_ASSEMBLY_TRAVERSAL_SOURCE_ROLES = frozenset(
    {"generated_dependency", "production_object", "transversal"}
)
DECLARED_ASSEMBLER_SOURCE_ROLES = frozenset(
    {"production_object", "transversal"}
)
DECLARED_ASSEMBLER_PATH_ALLOWLIST = frozenset(
    {
        "Mathematiques/manuel-maths/scripts/assemble.py",
        "Mathematiques/manuel-maths/scripts/assemble_manuel.py",
        "NSI/scripts/assemble.py",
        "NSI/scripts/assemble_manuel.py",
    }
)
COMPILED_PDF_SOURCE_ROLES = frozenset({"generated_dependency"})
COMPILED_PDF_BUILD_ROOTS: Mapping[str, str] = MappingProxyType(
    {
        "1NSI": "NSI/build",
        "1SPE": "Mathematiques/manuel-maths/build",
        "TCOMPL": "Mathematiques/manuel-maths/build",
        "TEXPERTES": "Mathematiques/manuel-maths/build",
        "TNSI": "NSI/build",
        "TSPE_2026_2027": "Mathematiques/manuel-maths/build",
    }
)
RELEVANT_UNTRACKED_SOURCE_ROLES = frozenset(
    {
        "generated_dependency",
        "harvest_candidate",
        "production_object",
        "validation_reference",
        "visual_reference",
    }
)


def _utf8_bytes(text: str) -> bytes:
    return text.encode("utf-8")


def _load_yaml_payload(path: Path, *, default: Any = None) -> Any:
    if not path.is_file():
        return default
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError):
        return default


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: _UniqueKeySafeLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "construction du contrôle versionné",
                node.start_mark,
                "clé YAML non hachable",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "construction du contrôle versionné",
                node.start_mark,
                f"clé YAML dupliquée: {key}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _load_control_yaml_payload(path: Path, *, default: Any = None) -> Any:
    if not path.is_file():
        return default
    try:
        content = path.read_text(encoding="utf-8")
        return yaml.load(content, Loader=_UniqueKeySafeLoader)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise InventoryError(f"contrôle YAML invalide {path}: {exc}") from exc


def _load_json_payload(path: Path, *, default: Any = None) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return default


def _repo_root_path(root: Path | str) -> Path:
    root_path = Path(root).resolve()
    if not (root_path / ".git").exists():
        raise InventoryError("root doit être un dépôt git")
    return root_path


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _normalize_path_for_match(path: str) -> str:
    return path.replace("\\", "/")


def _control_digest(payload: Mapping[str, Any]) -> str:
    canonical = {
        str(key): value
        for key, value in payload.items()
        if str(key) != "control_digest"
    }
    serialized = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"sha256:{hashlib.sha256(_utf8_bytes(serialized)).hexdigest()}"


def _validate_control_payload(
    root: Path,
    relative_path: str,
    payload: Mapping[str, Any],
    *,
    artifact_type: str,
) -> dict[str, Any]:
    normalized = dict(payload)
    if normalized.get("artifact_type") != artifact_type:
        raise InventoryError(
            f"artifact_type incohérent dans {relative_path}: "
            f"attendu {artifact_type}, reçu {normalized.get('artifact_type')}"
        )
    _validate_artifact_schema(
        normalized,
        root=root,
        path=Path(relative_path),
    )
    expected_digest = _control_digest(normalized)
    if normalized.get("control_digest") != expected_digest:
        raise InventoryError(
            f"control_digest incohérent dans {relative_path}: "
            f"attendu {expected_digest}, reçu {normalized.get('control_digest')}"
        )
    return normalized


def _versioned_control_required(
    root: Path,
    relative_path: str,
    *,
    artifact_type: str,
) -> bool:
    schema_ref = SCHEMA_REGISTRY[artifact_type][SCHEMA_VERSION]
    return (root / relative_path).is_file() and (root / schema_ref).is_file()


def _default_role_patterns() -> tuple[dict[str, list[str]], str, list[str]]:
    return (
        {role: list(patterns) for role, patterns in DEFAULT_SOURCE_ROLE_PATTERNS.items()},
        DEFAULT_SOURCE_ROLE,
        list(DEFAULT_SOURCE_ROLE_ORDER),
    )


def _validate_source_role_invariants(
    role_patterns: Mapping[str, list[str]],
    default_role: str,
    role_order: list[str],
) -> None:
    expected_roles = set(DEFAULT_SOURCE_ROLE_ORDER)
    if default_role != DEFAULT_SOURCE_ROLE:
        raise InventoryError(
            f"invariant SOURCE_ROLES: default doit valoir {DEFAULT_SOURCE_ROLE}"
        )
    if set(role_patterns) != expected_roles:
        raise InventoryError(
            "invariant SOURCE_ROLES: rôles canoniques incomplets ou inattendus"
        )
    empty_roles = sorted(
        role
        for role in expected_roles
        if not role_patterns.get(role)
        or any(not isinstance(pattern, str) or not pattern for pattern in role_patterns[role])
    )
    if empty_roles:
        raise InventoryError(
            "invariant SOURCE_ROLES: rôles sans motif valide: "
            + ", ".join(empty_roles)
        )
    if role_order != list(DEFAULT_SOURCE_ROLE_ORDER):
        raise InventoryError(
            f"role_order non canonique dans {SOURCE_ROLES_FILE}"
        )
    sentinels = {
        ".github/actions/cache/item": "excluded",
        "tests/fixtures/case.tex": "fixture",
        "NSI/chapitres/1NSI-X/_harvest/direct.candidate.tex": "harvest_candidate",
        "NSI/chapitres/1NSI-X/_harvest/P04/one.candidate.tex": "harvest_candidate",
        "NSI/chapitres/1NSI-X/_harvest/P04/deep/n.candidate.tex": "harvest_candidate",
        "Mathematiques/manuel-maths/validations/v5-it1/page-13.png": "visual_reference",
        "audit/historique/ancien.md": "archive",
        "NSI/build/direct.tex": "generated_dependency",
        "NSI/build/deep/generated.pdf": "generated_dependency",
        "NSI/chapitres/1NSI-X/validations/check.json": "validation_reference",
        "NSI/chapitres/1NSI-X/cours/c1.tex": "production_object",
        "scripts/inventory_collection.py": "transversal",
    }
    failures = [
        f"{path}={actual} (attendu {expected})"
        for path, expected in sentinels.items()
        if (
            actual := _classify_source_path(
                path,
                {},
                default=default_role,
                role_patterns=role_patterns,
                role_order=role_order,
            )
        )
        != expected
    ]
    if failures:
        raise InventoryError(
            "invariant SOURCE_ROLES: sentinelles mal classées: "
            + "; ".join(failures)
        )


def _collect_role_patterns(root: Path) -> tuple[dict[str, list[str]], str, list[str]]:
    payload = _load_control_yaml_payload(root / SOURCE_ROLES_FILE, default=None)
    versioned_control_required = _versioned_control_required(
        root,
        SOURCE_ROLES_FILE,
        artifact_type="source_roles",
    )
    if not isinstance(payload, Mapping) or not payload:
        if versioned_control_required:
            raise InventoryError(
                f"contrôle versionné invalide: {SOURCE_ROLES_FILE}"
            )
        return _default_role_patterns()
    strict_control = "artifact_type" in payload
    if versioned_control_required and not strict_control:
        raise InventoryError(
            f"contrôle versionné incomplet: {SOURCE_ROLES_FILE}"
        )
    if strict_control:
        payload = _validate_control_payload(
            root,
            SOURCE_ROLES_FILE,
            payload,
            artifact_type="source_roles",
        )

    raw_roles = payload.get("roles")
    role_patterns: dict[str, list[str]] = {}
    default_role = str(payload.get("default", payload.get("default_role", "transversal")))
    role_order = payload.get("role_order") if isinstance(payload.get("role_order"), list) else []

    if isinstance(raw_roles, Mapping):
        for role, patterns in raw_roles.items():
            if not isinstance(patterns, list):
                continue
            role_patterns[str(role)] = [
                _normalize_path_for_match(str(pattern))
                for pattern in patterns
                if isinstance(pattern, str) and str(pattern).strip()
            ]
    else:
        for role, patterns in payload.items():
            if not isinstance(patterns, list) or role in {"default", "default_role", "role_order", "roles"}:
                continue
            role_patterns[str(role)] = [
                _normalize_path_for_match(str(pattern))
                for pattern in patterns
                if isinstance(pattern, str) and str(pattern).strip()
            ]

    role_order = [str(role) for role in role_order if isinstance(role, str)]
    if not role_order:
        role_order = [
            role
            for role in DEFAULT_SOURCE_ROLE_ORDER
            if role in role_patterns
        ]
    if strict_control:
        _validate_source_role_invariants(
            role_patterns,
            default_role,
            role_order,
        )

    if (
        not role_patterns.get("production_object")
        or "production_object" not in role_order
    ):
        return _default_role_patterns()

    return role_patterns, default_role, role_order


def _load_build_producers(root: Path) -> list[dict[str, Any]]:
    payload = _load_control_yaml_payload(
        root / BUILD_PRODUCERS_FILE,
        default=None,
    )
    if not isinstance(payload, Mapping) or not payload:
        raise InventoryError(
            f"contrôle versionné absent ou invalide: {BUILD_PRODUCERS_FILE}"
        )
    validated = _validate_control_payload(
        root,
        BUILD_PRODUCERS_FILE,
        payload,
        artifact_type="build_producers",
    )
    raw_producers = validated.get("producers")
    if not isinstance(raw_producers, list) or not raw_producers:
        raise InventoryError(f"producteurs invalides dans {BUILD_PRODUCERS_FILE}")

    producers = [dict(producer) for producer in raw_producers]
    producer_ids = [str(producer["producer_id"]) for producer in producers]
    if producer_ids != sorted(producer_ids):
        raise InventoryError(f"ordre des producteurs invalide dans {BUILD_PRODUCERS_FILE}")
    if len(set(producer_ids)) != len(producer_ids):
        raise InventoryError(f"producer_id dupliqué dans {BUILD_PRODUCERS_FILE}")

    claimed_assemblies: set[str] = set()
    for producer in producers:
        assembly_ids = [str(value) for value in producer["assembly_ids"]]
        if assembly_ids != sorted(assembly_ids):
            raise InventoryError(
                "ordre des assembly_ids invalide pour "
                f"producer_id={producer['producer_id']}"
            )
        duplicates = claimed_assemblies & set(assembly_ids)
        if duplicates:
            raise InventoryError(
                "assembly_id couvert par plusieurs producteurs: "
                + ", ".join(sorted(duplicates))
            )
        claimed_assemblies.update(assembly_ids)

    tracked = set(git_tracked_files(root))

    def validate_program_path(path: str, *, role: str) -> None:
        _clean_path(path, role=role, repository=root)
        if path not in tracked:
            raise InventoryError(f"{role} non suivi par Git: {path}")
        target = root / path
        try:
            metadata = target.lstat()
        except OSError as exc:
            raise InventoryError(f"{role} absent: {path}") from exc
        if stat.S_ISLNK(metadata.st_mode):
            raise InventoryError(f"{role} symbolique interdit: {path}")
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise InventoryError(
                f"{role} doit être un fichier régulier sans hardlink: {path}"
            )

    for producer in producers:
        recorder = str(producer["recorder"])
        if recorder != CANONICAL_BUILD_RECORDER:
            raise InventoryError(
                "recorder non canonique pour "
                f"producer_id={producer['producer_id']}: {recorder}"
            )
        validate_program_path(
            str(producer["assembler"]),
            role="assembleur de build",
        )
        validate_program_path(recorder, role="recorder de build")

    return [_canonicalize(producer) for producer in producers]


def _load_source_roles(
    root: Path,
    tracked_files: Iterable[str] | None = None,
) -> dict[str, str]:
    role_patterns, default_role, ordered_roles = _collect_role_patterns(root)
    assignments: dict[str, str] = {}
    tracked = git_tracked_files(root) if tracked_files is None else tracked_files
    raw_paths = sorted(set(tracked))
    normalized_paths: dict[str, list[str]] = defaultdict(list)
    for rel in raw_paths:
        normalized_paths[_normalize_path_for_match(rel)].append(rel)
    collisions = [
        (normalized, raw_group)
        for normalized, raw_group in sorted(normalized_paths.items())
        if len(raw_group) > 1
    ]
    if collisions:
        details = "; ".join(
            f"{normalized} <- {', '.join(raw_group)}"
            for normalized, raw_group in collisions
        )
        raise InventoryError(
            "collision de chemins Git après normalisation: " + details
        )
    for rel in raw_paths:
        normalized = _normalize_path_for_match(rel)
        role = default_role
        for candidate in ordered_roles:
            for pattern in role_patterns.get(candidate, ()):  # type: ignore[arg-type]
                if fnmatch(normalized, pattern):
                    role = candidate
                    break
            if role != default_role:
                break
        assignments[rel] = role
    _validate_tracked_source_role_assignments(assignments)
    return assignments


def _is_intrinsic_harvest_candidate(path: str) -> bool:
    normalized = PurePosixPath(_normalize_path_for_match(path))
    return (
        "_harvest" in normalized.parts
        and normalized.name.endswith(".candidate.tex")
    )


def _validate_tracked_source_role_assignments(
    assignments: Mapping[str, str],
) -> None:
    canonical_patterns, canonical_default, canonical_order = _default_role_patterns()
    failures: list[str] = []
    for path, assigned_role in sorted(assignments.items()):
        canonical_role = _classify_source_path(
            path,
            {},
            default=canonical_default,
            role_patterns=canonical_patterns,
            role_order=canonical_order,
        )
        if assigned_role != canonical_role:
            failures.append(
                f"{path}={assigned_role} (attendu {canonical_role})"
            )
    if failures:
        raise InventoryError(
            "invariant de classification canonique des fichiers suivis violé: "
            + "; ".join(failures)
        )


def _classify_source_path(
    path: str,
    roles: Mapping[str, str],
    *,
    default: str = "transversal",
    role_patterns: Mapping[str, list[str]] | None = None,
    role_order: list[str] | None = None,
) -> str:
    if path in roles:
        return roles[path]
    normalized = _normalize_path_for_match(path)
    if normalized in roles:
        return roles[normalized]
    if role_patterns is None or role_order is None:
        return default
    for candidate in role_order:
        for pattern in role_patterns.get(candidate, ()):  # type: ignore[arg-type]
            if fnmatch(normalized, pattern):
                return candidate
    return default


def _classify_is_production(
    path: str,
    roles: Mapping[str, str],
    *,
    role_patterns: Mapping[str, list[str]],
    role_order: list[str],
    default: str = "transversal",
) -> bool:
    return _classify_source_path(
        path,
        roles,
        default=default,
        role_patterns=role_patterns,
        role_order=role_order,
    ) == "production_object"


def _load_dispositions(root: Path) -> dict[str, dict[str, Any]]:
    payload = _load_control_yaml_payload(
        root / ANOMALY_DISPOSITIONS_FILE,
        default={},
    )
    versioned_control_required = _versioned_control_required(
        root,
        ANOMALY_DISPOSITIONS_FILE,
        artifact_type="anomaly_dispositions",
    )
    if not isinstance(payload, Mapping) or not payload:
        if versioned_control_required:
            raise InventoryError(
                f"contrôle versionné invalide: {ANOMALY_DISPOSITIONS_FILE}"
            )
        return {}
    if "artifact_type" not in payload:
        if versioned_control_required:
            raise InventoryError(
                f"contrôle versionné incomplet: {ANOMALY_DISPOSITIONS_FILE}"
            )
        return {}
    validated = _validate_control_payload(
        root,
        ANOMALY_DISPOSITIONS_FILE,
        payload,
        artifact_type="anomaly_dispositions",
    )
    if validated.get("fingerprint_schema_version") != SCHEMA_VERSION:
        raise InventoryError(
            "fingerprint_schema_version non supportée dans "
            f"{ANOMALY_DISPOSITIONS_FILE}: "
            f"{validated.get('fingerprint_schema_version')}"
        )
    dispositions = validated.get("dispositions")
    if not isinstance(dispositions, Mapping):
        raise InventoryError(
            f"dispositions invalides dans {ANOMALY_DISPOSITIONS_FILE}"
        )

    raw_dispositions: dict[str, dict[str, Any]] = {}
    for fingerprint, value in dispositions.items():
        if not isinstance(fingerprint, str):
            raise InventoryError(
                f"fingerprint non textuel dans {ANOMALY_DISPOSITIONS_FILE}"
            )
        if not isinstance(value, Mapping):
            raise InventoryError(
                f"disposition non objet pour fingerprint={fingerprint}"
            )
        if value.get("fingerprint") != fingerprint:
            raise InventoryError(
                "fingerprint de clé incohérent dans "
                f"{ANOMALY_DISPOSITIONS_FILE}: {fingerprint}"
            )
        disposition = str(value.get("disposition", ""))
        if disposition not in ANOMALY_DISPOSITIONS:
            raise InventoryError(
                f"disposition inconnue pour fingerprint={fingerprint}: {disposition}"
            )
        policy_managed = (
            "qualification_policy_digest" in value
            or (
                value.get("policy_rule")
                and value.get("policy_rule") != "historical-evidence"
            )
        )
        stored_qualification_digest = value.get("qualification_digest")
        if policy_managed and not isinstance(
            stored_qualification_digest,
            str,
        ):
            raise InventoryError(
                "qualification_digest absent pour disposition de politique "
                f"fingerprint={fingerprint}"
            )
        if (
            stored_qualification_digest is not None
            and stored_qualification_digest
            != _baseline_qualification.qualification_digest(value)
        ):
            raise InventoryError(
                "qualification_digest incohérent pour "
                f"fingerprint={fingerprint}"
            )
        if (
            disposition == "accepted_exception"
            and "expires_at" in value
            and "expiry" in value
        ):
            raise InventoryError(
                "alias d'expiration mutuellement exclusifs pour "
                f"fingerprint={fingerprint}: expires_at, expiry"
            )
        for expiry_field in ("expires_at", "expiry"):
            if expiry_field in value:
                _parse_disposition_expiry(value[expiry_field])
        raw_dispositions[fingerprint] = _canonicalize(dict(value))
    return raw_dispositions


def _schema_ref_for(artifact_type: str, schema_version: int) -> str:
    versions = SCHEMA_REGISTRY.get(artifact_type)
    if versions is None:
        raise InventoryError(f"type d'artefact inconnu: {artifact_type}")
    schema_ref = versions.get(schema_version)
    if schema_ref is None:
        raise InventoryError(
            "version de schéma inconnue "
            f"pour {artifact_type}: {schema_version}"
        )
    return schema_ref


def _load_artifact_schema(
    root: Path,
    *,
    artifact_type: str,
    schema_version: int,
    schema_ref: str,
) -> dict[str, Any]:
    expected_ref = _schema_ref_for(artifact_type, schema_version)
    if schema_ref != expected_ref:
        raise InventoryError(
            f"schema_ref incohérent pour {artifact_type}: "
            f"attendu {expected_ref}, reçu {schema_ref}"
        )
    schema_path = root / expected_ref
    if not schema_path.is_file():
        raise InventoryError(f"schéma absent pour {artifact_type}: {schema_path}")
    try:
        schema_payload = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InventoryError(
            f"schéma JSON invalide pour {artifact_type}: {schema_path}: {exc}"
        ) from exc
    if not isinstance(schema_payload, Mapping):
        raise InventoryError(
            f"schéma JSON invalide pour {artifact_type}: racine non objet"
        )
    try:
        import jsonschema
    except ImportError as exc:
        raise InventoryError("jsonschema indisponible") from exc
    try:
        jsonschema.Draft202012Validator.check_schema(schema_payload)
    except jsonschema.SchemaError as exc:
        raise InventoryError(
            f"schéma Draft 2020-12 invalide pour {artifact_type}: {exc.message}"
        ) from exc
    return dict(schema_payload)


def _validate_artifact_schema(
    payload: Mapping[str, Any],
    *,
    root: Path,
    path: Path,
) -> None:
    artifact_type = payload.get("artifact_type")
    schema_version = payload.get("schema_version")
    schema_ref = payload.get("schema_ref")
    if not isinstance(artifact_type, str) or not artifact_type:
        raise InventoryError(f"artifact_type invalide dans {path}")
    if not isinstance(schema_version, int) or isinstance(schema_version, bool):
        raise InventoryError(f"schema_version invalide dans {path}")
    if not isinstance(schema_ref, str) or not schema_ref:
        raise InventoryError(f"schema_ref invalide dans {path}")
    schema = _load_artifact_schema(
        root,
        artifact_type=artifact_type,
        schema_version=schema_version,
        schema_ref=schema_ref,
    )
    try:
        import jsonschema
    except ImportError as exc:
        raise InventoryError("jsonschema indisponible") from exc
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(payload),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        details = "; ".join(
            f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: "
            f"{error.message}"
            for error in errors
        )
        raise InventoryError(f"artefact non conforme au schéma {path}: {details}")


def _build_state_digest(builds: list[Mapping[str, Any]]) -> str:
    canonical = json.dumps(
        builds,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"sha256:{hashlib.sha256(_utf8_bytes(canonical)).hexdigest()}"


def _observed_deliverable_variant(manual: str, raw_variant: str) -> str:
    specification = DELIVERABLE_SPECS.get(manual)
    if specification is None:
        raise InventoryError(f"manual inconnu dans le manifeste: {manual}")
    matches = [
        deliverable
        for deliverable, aliases in specification["variants"].items()
        if raw_variant in aliases
    ]
    if len(matches) != 1:
        raise InventoryError(
            "variant de build sans mapping explicite ou ambigu: "
            f"{manual}:{raw_variant}"
        )
    return matches[0]


def _control_file_fingerprint(
    value: os.stat_result,
) -> tuple[int, int, int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        stat.S_IFMT(value.st_mode),
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
        value.st_nlink,
    )


class _ConfinedJsonSnapshot:
    def __init__(
        self,
        *,
        root: Path,
        relative: PurePosixPath,
        role: str,
    ) -> None:
        self.root = root.resolve()
        self.relative = relative
        self.role = role
        self.root_fd = -1
        self.parent_fd = -1
        self.target_fd = -1
        self.root_stat: os.stat_result | None = None
        self.parent_stat: os.stat_result | None = None
        self.target_fingerprint: tuple[int, int, int, int, int, int, int] | None = None
        self.payload = b""

    def __enter__(self) -> "_ConfinedJsonSnapshot":
        try:
            _clean_path(
                self.relative.as_posix(),
                role=self.role,
                repository=self.root,
            )
            self.root_fd, self.root_stat = _open_pinned_directory(
                self.root,
                role=f"{self.role} repository root",
            )
            self.parent_fd, self.parent_stat = _open_destination_parent(
                self.root_fd,
                self.relative,
                create=False,
            )
            flags = (
                os.O_RDONLY
                | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_NONBLOCK", 0)
            )
            self.target_fd = os.open(
                self.relative.name,
                flags,
                dir_fd=self.parent_fd,
            )
        except Exception as exc:
            self.close()
            if isinstance(exc, InventoryError):
                raise
            raise InventoryError(
                f"{self.role} symbolique ou inaccessible"
            ) from exc
        metadata = os.fstat(self.target_fd)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            self.close()
            raise InventoryError(
                f"{self.role} doit être un fichier régulier sans hardlink"
            )
        self.target_fingerprint = _control_file_fingerprint(metadata)
        self.payload = self._read_current_bytes()
        self.verify()
        return self

    def _read_current_bytes(self) -> bytes:
        os.lseek(self.target_fd, 0, os.SEEK_SET)
        chunks: list[bytes] = []
        while chunk := os.read(self.target_fd, 1024 * 1024):
            chunks.append(chunk)
        return b"".join(chunks)

    def verify(self) -> None:
        if (
            self.root_stat is None
            or self.parent_stat is None
            or self.target_fingerprint is None
        ):
            raise InventoryError(f"snapshot {self.role} non initialisé")
        metadata = os.fstat(self.target_fd)
        if (
            metadata.st_nlink != 1
            or _control_file_fingerprint(metadata) != self.target_fingerprint
            or self._read_current_bytes() != self.payload
            or _control_file_fingerprint(os.fstat(self.target_fd))
            != self.target_fingerprint
        ):
            raise InventoryError(f"{self.role} modifié pendant la validation")
        _require_repository_root_identity(self.root, self.root_stat)
        _revalidate_destination_parent(
            self.root_fd,
            self.relative,
            self.parent_stat,
        )
        current = os.stat(
            self.relative.name,
            dir_fd=self.parent_fd,
            follow_symlinks=False,
        )
        if _control_file_fingerprint(current) != self.target_fingerprint:
            raise InventoryError(f"{self.role} remplacé pendant la validation")

    def json_mapping(self) -> dict[str, Any]:
        try:
            decoded = json.loads(self.payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InventoryError(f"{self.role} JSON invalide") from exc
        if not isinstance(decoded, Mapping):
            raise InventoryError(f"{self.role} JSON doit être un objet")
        return dict(decoded)

    def close(self) -> None:
        for descriptor in (self.target_fd, self.parent_fd, self.root_fd):
            if descriptor >= 0:
                os.close(descriptor)
        self.target_fd = self.parent_fd = self.root_fd = -1

    def __exit__(self, *_args: object) -> None:
        self.close()


def _observed_git_state(
    root: Path,
    *,
    ignore_manifest: bool = False,
    allowed_generation_paths: Mapping[str, tuple[int, int]] | None = None,
) -> tuple[str, str, bool]:
    status = _exclude_owned_generation_paths(
        root,
        _git_status(root, required=True),
        allowed_generation_paths,
    )
    dirty = bool(status) and not (
        ignore_manifest
        and all(
            all(path == BUILD_MANIFEST_FILE for path in paths)
            for _marker, paths in status
        )
    )
    return (
        _git_required_value(
            root,
            ("rev-parse", "HEAD"),
            description="git HEAD",
        ),
        _git_required_value(
            root,
            ("branch", "--show-current"),
            description="git branch",
        ),
        dirty,
    )


def _pdf_matches_observed_identity(
    pdf_path: str,
    manual: str,
    variant: str,
) -> bool:
    attribution = _pdf_core.attribute_pdf(
        pdf_path,
        {
            "manuals": {
                manual_id: {"chapters": {}}
                for manual_id in DELIVERABLE_SPECS
            }
        },
    )
    return (
        attribution.get("scope") == "manual"
        and attribution.get("manual") == manual
        and attribution.get("variant") == variant
    )


def _tracked_source_set_digest(root: Path) -> str:
    try:
        payload = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise InventoryError("ensemble des sources suivies Git indisponible") from exc
    return hashlib.sha256(payload).hexdigest()


def _require_git_ancestor(
    root: Path,
    recorded_sha: object,
    current_head: object,
    *,
    role: str,
) -> None:
    if (
        not isinstance(recorded_sha, str)
        or re.fullmatch(r"[0-9a-f]{40}", recorded_sha) is None
        or not isinstance(current_head, str)
        or re.fullmatch(r"[0-9a-f]{40}", current_head) is None
    ):
        raise InventoryError(f"{role} Git invalide")
    try:
        ancestry = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "merge-base",
                "--is-ancestor",
                recorded_sha,
                current_head,
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise InventoryError(f"{role} Git invérifiable") from exc
    if ancestry.returncode == 1:
        raise InventoryError(f"{role} sans ancêtre Git valide")
    if ancestry.returncode != 0:
        raise InventoryError(f"{role} Git invérifiable")


def _load_observed_build_manifest(
    root: Path,
    *,
    source_digest: str,
    model_digest: str,
    declared_assemblies: list[Mapping[str, Any]],
    pdfinfo_counter: Any,
    python_counter: Any,
    source_files: tuple[str, ...] | None = None,
    empty_manifest_refresh_capability: object | None = None,
    owned_generation_lock: Mapping[str, tuple[int, int]] | None = None,
) -> list[dict[str, Any]]:
    manifest_path = root / BUILD_MANIFEST_FILE
    if not manifest_path.exists() and not manifest_path.is_symlink():
        return []
    try:
        snapshot = _ConfinedJsonSnapshot(
            root=root,
            relative=PurePosixPath(BUILD_MANIFEST_FILE),
            role="manifeste de build",
        )
        snapshot.__enter__()
        payload = snapshot.json_mapping()
    except InventoryError as exc:
        raise InventoryError(f"manifeste de build non sûr: {exc}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InventoryError(
            f"manifeste de build illisible: {type(exc).__name__}"
        ) from exc
    try:
        _validate_artifact_schema(payload, root=root, path=Path(BUILD_MANIFEST_FILE))
        builds = payload.get("builds")
        if not isinstance(builds, list):
            raise InventoryError("builds du manifeste invalide")
        if payload.get("build_state_digest") != _build_state_digest(builds):
            raise InventoryError("build_state_digest incohérent")
        may_refresh_empty = (
            empty_manifest_refresh_capability
            is _EMPTY_MANIFEST_REFRESH_CAPABILITY
            and not builds
        )
        may_rebind_empty_branch = (
            empty_manifest_refresh_capability
            is _EMPTY_MANIFEST_BRANCH_REBIND_CAPABILITY
            and not builds
        )
        may_invalidate_stale = (
            empty_manifest_refresh_capability
            is _STALE_MANIFEST_INVALIDATION_CAPABILITY
            and bool(builds)
        )
        tolerate_digest_mismatch = (
            may_refresh_empty
            or may_rebind_empty_branch
            or may_invalidate_stale
        )
        if (
            not tolerate_digest_mismatch
            and payload.get("source_digest") != source_digest
        ):
            raise InventoryError("source_digest du manifeste de build incohérent")
        if (
            not tolerate_digest_mismatch
            and payload.get("model_digest") != model_digest
        ):
            raise InventoryError("model_digest du manifeste de build incohérent")

        ignore_manifest_dirty = (
            may_refresh_empty
            or may_rebind_empty_branch
            or may_invalidate_stale
        )
        initial_git_state = _observed_git_state(
            root,
            ignore_manifest=ignore_manifest_dirty,
            allowed_generation_paths=owned_generation_lock,
        )
        initial_tracked_source_set = _tracked_source_set_digest(root)
        head_sha, branch, dirty = initial_git_state
        provenance = payload.get("provenance")
        if not isinstance(provenance, Mapping):
            raise InventoryError("provenance du manifeste invalide")
        if dirty:
            raise InventoryError("dépôt Git sale pour le manifeste observé")
        recorded_branch = provenance.get("branch")
        branch_differs = recorded_branch != branch
        if may_rebind_empty_branch and not branch:
            raise InventoryError("branche Git détachée ou indisponible")
        if branch_differs and not may_rebind_empty_branch:
            raise InventoryError("branche de provenance du manifeste incohérente")
        if (
            branch_differs
            and may_rebind_empty_branch
            and provenance.get("head_sha") == head_sha
        ):
            raise InventoryError(
                "provenance du manifeste sans ancêtre Git strict"
            )
        if builds and provenance.get("dirty") is not False:
            raise InventoryError(
                "provenance du manifeste sale pour des builds observés"
            )
        _require_git_ancestor(
            root,
            provenance.get("head_sha"),
            head_sha,
            role="provenance du manifeste",
        )

        def revalidate_state() -> None:
            snapshot.verify()
            if (
                _observed_git_state(
                    root,
                    ignore_manifest=ignore_manifest_dirty,
                    allowed_generation_paths=owned_generation_lock,
                )
                != initial_git_state
            ):
                raise InventoryError(
                    "état Git modifié pendant la validation du manifeste"
                )
            if _tracked_source_set_digest(root) != initial_tracked_source_set:
                raise InventoryError(
                    "ensemble des sources suivies modifié pendant la validation"
                )
            if (
                source_files is not None
                and _source_digest(root, source_files) != source_digest
            ):
                raise InventoryError(
                    "source_digest modifié pendant la validation du manifeste"
                )

        revalidate_state()
        declared = {
            (str(value.get("manual")), str(value.get("variant"))): value
            for value in declared_assemblies
            if value.get("scope") == "manual"
        }
        observed: list[dict[str, Any]] = []
        identities: set[tuple[str, str]] = set()
        pdf_paths: set[str] = set()
        pdf_digests: set[str] = set()
        dependency_snapshots: dict[
            str,
            list[tuple[str, tuple[int, int, int, int, int, int, int]]],
        ] = {}

        def revalidate_dependencies() -> None:
            for dependency, snapshots in dependency_snapshots.items():
                for relative, expected in snapshots:
                    try:
                        metadata = (root / relative).lstat()
                    except OSError as exc:
                        raise InventoryError(
                            f"generated_dependencies modifiée: {dependency}"
                        ) from exc
                    if (
                        stat.S_ISLNK(metadata.st_mode)
                        or _control_file_fingerprint(metadata) != expected
                    ):
                        raise InventoryError(
                            f"generated_dependencies modifiée: {dependency}"
                        )

        original_revalidate_state = revalidate_state

        def revalidate_state() -> None:
            original_revalidate_state()
            revalidate_dependencies()

        if may_invalidate_stale:
            builds = []

        for index, raw_build in enumerate(builds):
            if not isinstance(raw_build, Mapping):
                raise InventoryError(f"build[{index}] non objet")
            build = dict(raw_build)
            manual = str(build["manual"])
            variant = str(build["variant"])
            identity = (manual, variant)
            if identity in identities:
                raise InventoryError(
                    f"build observé en doublon: {manual}:{variant}"
                )
            identities.add(identity)
            _observed_deliverable_variant(manual, variant)
            if identity not in declared:
                raise InventoryError(
                    f"variant non déclaré dans les assemblages: {manual}:{variant}"
                )
            _require_git_ancestor(
                root,
                build["git_sha"],
                head_sha,
                role=f"git_sha pour {manual}:{variant}",
            )
            if build["source_digest"] != source_digest:
                raise InventoryError(
                    f"source_digest périmé pour {manual}:{variant}"
                )
            if build["model_digest"] != model_digest:
                raise InventoryError(
                    f"model_digest périmé pour {manual}:{variant}"
                )
            included = build["included_objects"]
            excluded = build["excluded_objects"]
            trace = build["ordered_trace"]
            if trace != included:
                raise InventoryError(
                    f"ordered_trace incohérente pour {manual}:{variant}"
                )
            if set(included) & set(excluded):
                raise InventoryError(
                    f"included_objects et excluded_objects se chevauchent "
                    f"pour {manual}:{variant}"
                )
            declared_objects = declared[identity].get("included_objects")
            if (
                isinstance(declared_objects, list)
                and (set(included) | set(excluded)) != set(declared_objects)
            ):
                raise InventoryError(
                    f"included_objects/excluded_objects ne couvrent pas "
                    f"l'assemblage déclaré pour {manual}:{variant}"
                )
            dependency_digests = build["generated_dependency_digests"]
            if set(dependency_digests) != set(build["generated_dependencies"]):
                raise InventoryError(
                    f"generated_dependency_digests incomplet pour "
                    f"{manual}:{variant}"
                )
            for dependency in build["generated_dependencies"]:
                if (
                    "\\" in dependency
                    or dependency.startswith("/")
                    or any(
                        part in {"", ".", ".."}
                        for part in dependency.split("/")
                    )
                ):
                    raise InventoryError(
                        f"generated_dependencies non canonique pour "
                        f"{manual}:{variant}"
                    )
                current = root
                relative_parts: list[str] = []
                snapshots: list[
                    tuple[
                        str,
                        tuple[int, int, int, int, int, int, int],
                    ]
                ] = []
                try:
                    for part in PurePosixPath(dependency).parts:
                        relative_parts.append(part)
                        current = current / part
                        metadata = current.lstat()
                        if stat.S_ISLNK(metadata.st_mode):
                            raise InventoryError(
                                "generated_dependencies symbolique interdite "
                                f"pour {manual}:{variant}"
                            )
                        snapshots.append(
                            (
                                "/".join(relative_parts),
                                _control_file_fingerprint(metadata),
                            )
                        )
                    if (
                        not stat.S_ISREG(metadata.st_mode)
                        or metadata.st_nlink != 1
                    ):
                        raise InventoryError(
                            "generated_dependencies non régulière ou hardlink "
                            f"pour {manual}:{variant}"
                        )
                except FileNotFoundError as exc:
                    raise InventoryError(
                        f"generated_dependencies absente pour {manual}:{variant}"
                    ) from exc
                try:
                    dependency_payload = current.read_bytes()
                except OSError as exc:
                    raise InventoryError(
                        f"generated_dependencies illisible pour "
                        f"{manual}:{variant}"
                    ) from exc
                if _control_file_fingerprint(current.lstat()) != snapshots[-1][1]:
                    raise InventoryError(
                        f"generated_dependencies modifiée pour "
                        f"{manual}:{variant}"
                    )
                actual_dependency_digest = (
                    "sha256:"
                    + hashlib.sha256(dependency_payload).hexdigest()
                )
                if dependency_digests[dependency] != actual_dependency_digest:
                    raise InventoryError(
                        f"generated_dependency_digests incohérent pour "
                        f"{manual}:{variant}"
                    )
                dependency_snapshots[dependency] = snapshots
            gates = build["gates"]
            for gate in ("compile", "preflight"):
                if gates[gate].get("passed") is not True:
                    raise InventoryError(
                        f"gate {gate} rouge pour {manual}:{variant}"
                    )
            pdf_path = str(build["pdf_path"])
            pdf_digest = str(build["pdf_sha256"])
            if not _pdf_core._is_canonical_manual_pdf_path(
                {"manual": manual, "path": pdf_path},
                manual_build_roots=COMPILED_PDF_BUILD_ROOTS,
            ):
                raise InventoryError(
                    f"chemin PDF non canonique pour {manual}:{variant}"
                )
            if not _pdf_matches_observed_identity(
                pdf_path,
                manual,
                variant,
            ):
                raise InventoryError(
                    f"PDF sans preuve de manual/variante pour {manual}:{variant}"
                )
            if pdf_path in pdf_paths or pdf_digest in pdf_digests:
                raise InventoryError(
                    f"PDF ou digest réutilisé entre variantes: {pdf_path}"
                )
            pdf_paths.add(pdf_path)
            pdf_digests.add(pdf_digest)
            revalidate_state()
            digest, page_count, _method, reason = _pdf_core.inspect_stable_pdf(
                root,
                pdf_path,
                pdfinfo_counter=pdfinfo_counter,
                python_counter=python_counter,
            )
            revalidate_state()
            if reason:
                raise InventoryError(
                    f"PDF invalide pour {manual}:{variant}: {reason}"
                )
            if digest != build["pdf_sha256"]:
                raise InventoryError(
                    f"pdf_sha256 incohérent pour {manual}:{variant}"
                )
            if page_count != build["page_count"]:
                raise InventoryError(
                    f"page_count incohérent pour {manual}:{variant}"
                )
            observed.append(_canonicalize(build))
        revalidate_state()
        return observed
    finally:
        snapshot.close()


def _observed_build_coverage(
    declared_assemblies: list[Mapping[str, Any]],
    observed_builds: list[Mapping[str, Any]],
) -> dict[str, Any]:
    declared: dict[str, set[str]] = defaultdict(set)
    for assembly in declared_assemblies:
        if assembly.get("scope") == "manual":
            declared[str(assembly.get("manual"))].add(
                str(assembly.get("variant"))
            )
    observed: dict[str, set[str]] = defaultdict(set)
    for build in observed_builds:
        observed[str(build["manual"])].add(str(build["variant"]))

    coverage: dict[str, Any] = {}
    for manual, specification in sorted(DELIVERABLE_SPECS.items()):
        variants: dict[str, Any] = {}
        for deliverable, aliases in sorted(specification["variants"].items()):
            declared_aliases = sorted(declared[manual] & set(aliases))
            observed_aliases = sorted(observed[manual] & set(aliases))
            variants[deliverable] = {
                "declared_variants": declared_aliases,
                "observed_variants": observed_aliases,
                "ready": bool(declared_aliases and observed_aliases),
            }
        coverage[manual] = {
            "observed_build_ready": bool(variants)
            and all(value["ready"] for value in variants.values()),
            "variants": variants,
        }
    return coverage


def _observed_build_integration(
    declared_assemblies: list[Mapping[str, Any]],
    observed_builds: list[Mapping[str, Any]],
    producers: list[Mapping[str, Any]],
) -> dict[str, Any]:
    declared_by_id: dict[str, Mapping[str, Any]] = {}
    declared_by_identity: dict[tuple[str, str], str] = {}
    for assembly in declared_assemblies:
        if assembly.get("scope") != "manual":
            continue
        assembly_id = str(assembly.get("assembly_id", ""))
        manual = str(assembly.get("manual", ""))
        variant = str(assembly.get("variant", ""))
        if not assembly_id or not manual or not variant:
            continue
        declared_by_id[assembly_id] = assembly
        declared_by_identity[(manual, variant)] = assembly_id

    observed_ids = {
        assembly_id
        for build in observed_builds
        if (
            assembly_id := declared_by_identity.get(
                (str(build.get("manual", "")), str(build.get("variant", "")))
            )
        )
        is not None
    }
    claims: dict[str, list[str]] = defaultdict(list)
    producer_by_id: dict[str, Mapping[str, Any]] = {}
    for producer in producers:
        producer_id = str(producer.get("producer_id", ""))
        if producer_id:
            producer_by_id[producer_id] = producer
        for assembly_id in producer.get("assembly_ids", []):
            claims[str(assembly_id)].append(producer_id)

    required_ids = set(declared_by_id)
    registered_ids = set(claims)
    duplicate_ids = sorted(
        assembly_id
        for assembly_id, producer_ids in claims.items()
        if len(producer_ids) != 1
    )
    missing_ids = sorted(required_ids - registered_ids)
    unexpected_ids = sorted(registered_ids - required_ids)
    unobserved_ids = sorted(required_ids - observed_ids)
    assembler_mismatches = sorted(
        assembly_id
        for assembly_id in required_ids & registered_ids
        if len(claims[assembly_id]) == 1
        and str(declared_by_id[assembly_id].get("assembler", ""))
        != str(producer_by_id[claims[assembly_id][0]].get("assembler", ""))
    )
    recorder_mismatches = sorted(
        producer_id
        for producer_id, producer in producer_by_id.items()
        if producer.get("recorder") != CANONICAL_BUILD_RECORDER
    )

    integrated_producers: list[str] = []
    for producer_id, producer in sorted(producer_by_id.items()):
        assembly_ids = {str(value) for value in producer.get("assembly_ids", [])}
        if (
            assembly_ids
            and assembly_ids <= required_ids
            and assembly_ids <= observed_ids
            and not (assembly_ids & set(duplicate_ids))
            and not (assembly_ids & set(assembler_mismatches))
            and producer_id not in recorder_mismatches
        ):
            integrated_producers.append(producer_id)

    required_producers = sorted(producer_by_id)
    diagnostics = (
        duplicate_ids
        + missing_ids
        + unexpected_ids
        + unobserved_ids
        + assembler_mismatches
        + recorder_mismatches
    )
    status = (
        "integrated"
        if not diagnostics
        and integrated_producers == required_producers
        else "not_integrated"
    )
    return {
        "assembler_mismatches": assembler_mismatches,
        "duplicate_assembly_ids": duplicate_ids,
        "entrypoint": (
            "python scripts/build_manifest.py --receipt <build-receipt.json>"
        ),
        "integrated_producers": integrated_producers,
        "missing_assembly_ids": missing_ids,
        "recorder_mismatches": recorder_mismatches,
        "required_producers": required_producers,
        "status": status,
        "unexpected_assembly_ids": unexpected_ids,
        "unobserved_assembly_ids": unobserved_ids,
    }


def _build_anomaly_fingerprint_table(
    anomalies: Mapping[str, list[dict[str, Any]]]
) -> dict[str, list[str]]:
    signatures: dict[str, list[str]] = {}
    for category, values in anomalies.items():
        signatures[category] = []
        for anomaly in values:
            signatures[category].append(
                _anomaly_fingerprint(anomaly, category=category)
            )
        signatures[category].sort()
    return signatures


def _build_anomaly_signature_index(
    anomalies: Mapping[str, list[dict[str, Any]]],
) -> dict[tuple[str, str], list[dict[str, Any]]]:
    index: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for category, values in anomalies.items():
        for value in values:
            fingerprint = _anomaly_fingerprint(value, category=category)
            index.setdefault((category, fingerprint), []).append(value)
    return index


def _build_baseline_payload(
    inventory: Mapping[str, Any], source_digest: str
) -> dict[str, Any]:
    active = _current_active_debt(inventory)
    qualified_active = [
        entry for entry in active if entry.get("qualified") is True
    ]
    provenance = inventory.get("provenance")
    if not isinstance(provenance, Mapping):
        raise InventoryError("provenance absente pour la baseline")
    git_sha = provenance.get("head_sha")
    generated_at = provenance.get("generated_at_utc")
    if not isinstance(git_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", git_sha):
        raise InventoryError("SHA Git absent pour la baseline")
    if not isinstance(generated_at, str) or not generated_at:
        raise InventoryError("horodatage absent pour la baseline")
    return {
        "active": qualified_active,
        "artifact_type": "anomalies_baseline",
        "baseline_purpose": "debt_regression_control",
        "fingerprint_schema_version": FINGERPRINT_SCHEMA_VERSION,
        "generated_at_utc": generated_at,
        "generated_by": "inventory_collection.py",
        "git_sha": git_sha,
        "model_digest": _model_digest(inventory),
        "previous_baseline_digest": None,
        "provenance": dict(provenance),
        "provisional": True,
        "release_acceptance": False,
        "resolved": [],
        "schema_ref": "audit/schemas/v1/anomalies-baseline.schema.json",
        "schema_version": SCHEMA_VERSION,
        "source_digest": source_digest,
        "summary": {
            "active_qualified": len(qualified_active),
            "active_unqualified": len(active) - len(qualified_active),
            "resolved": 0,
        },
        "updates": [],
    }


def _baseline_disposition_by_fingerprint(
    baseline: Mapping[str, Any]
) -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    for entry in baseline.get("entries", []):
        if (
            not isinstance(entry, Mapping)
            or not isinstance(entry.get("fingerprint"), str)
            or not isinstance(entry.get("category"), str)
        ):
            continue
        key = f"{entry['category']}::{entry['fingerprint']}"
        values[key] = dict(entry)
    return values


def _load_baseline_payload(path: Path) -> Mapping[str, Any] | None:
    if not path:
        return None
    payload = _load_json_payload(path, default=None)
    if not isinstance(payload, Mapping):
        return None
    return payload


def _load_validated_baseline(root: Path) -> dict[str, Any]:
    payload = _read_confined_json_mapping(
        root,
        PurePosixPath(ANOMALIES_BASELINE_FILE),
        role="baseline",
    )
    _validate_artifact_schema(
        payload,
        root=root,
        path=Path(ANOMALIES_BASELINE_FILE),
    )
    if payload.get("baseline_purpose") != "debt_regression_control":
        raise InventoryError(
            "baseline_purpose doit valoir debt_regression_control"
        )
    if payload.get("release_acceptance") is not False:
        raise InventoryError("release_acceptance doit rester false")
    if payload.get("fingerprint_schema_version") != FINGERPRINT_SCHEMA_VERSION:
        raise InventoryError(
            "fingerprint_schema_version baseline non supportée:"
            f"{payload.get('fingerprint_schema_version')}"
        )
    updates = payload.get("updates")
    if not isinstance(updates, list):
        raise InventoryError("historique d'audit de baseline invalide")
    if payload.get("provisional") is False and not updates:
        raise InventoryError(
            "baseline finale sans mise à jour d'audit approuvée"
        )
    if updates:
        for previous, current in zip(updates, updates[1:]):
            if (
                not isinstance(previous, Mapping)
                or not isinstance(current, Mapping)
                or current.get("previous_baseline_digest")
                != previous.get("new_baseline_digest")
            ):
                raise InventoryError(
                    "chaîne d'empreintes de baseline incohérente"
                )
        last_update = updates[-1]
        if (
            not isinstance(last_update, Mapping)
            or payload.get("previous_baseline_digest")
            != last_update.get("previous_baseline_digest")
            or last_update.get("new_baseline_digest")
            != _baseline_payload_digest(payload)
        ):
            raise InventoryError("empreinte de baseline incohérente")
    return dict(payload)


_ANOMALY_SEVERITY_RANK = MappingProxyType(
    {
        "info": 0,
        "warning": 1,
        "error": 2,
        "blocking": 3,
        "regression": 4,
    }
)


def _coalesce_active_debt(
    entries: Iterable[Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    coalesced: dict[str, dict[str, Any]] = {}
    for raw_entry in entries:
        entry = dict(raw_entry)
        fingerprint = str(entry.get("fingerprint", ""))
        if not fingerprint:
            continue
        occurrence_count = entry.get("occurrence_count", 1)
        if not isinstance(occurrence_count, int) or isinstance(
            occurrence_count, bool
        ):
            occurrence_count = 0
        if fingerprint in coalesced:
            previous = coalesced[fingerprint]
            if str(previous.get("locator_key", "")) != str(
                entry.get("locator_key", "")
            ):
                raise InventoryError(
                    "fingerprint partagé par des locators distincts: "
                    f"{fingerprint}"
                )
            previous["occurrence_count"] = (
                int(previous.get("occurrence_count", 0)) + occurrence_count
            )
            continue
        entry["occurrence_count"] = occurrence_count
        coalesced[fingerprint] = entry
    return coalesced


def _active_debt_qualification_failures(
    entries: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    failures: list[str] = []
    for fingerprint, entry in sorted(entries.items()):
        owner = entry.get("owner")
        justification = entry.get("justification")
        qualification_digest = entry.get("qualification_digest")
        qualified = entry.get("qualified")
        if (
            not isinstance(owner, str)
            or not owner.strip()
            or owner not in _baseline_qualification.APPROVED_OWNERS
            or not isinstance(justification, str)
            or not justification.strip()
            or not isinstance(qualification_digest, str)
            or not re.fullmatch(
                r"sha256:[0-9a-f]{64}",
                qualification_digest,
            )
            or qualified is not True
        ):
            failures.append(
                "qualification active incomplète "
                f"fp={fingerprint}: owner/justification/"
                "qualification_digest/qualified requis; "
                "owner logique inconnu ou absent"
            )
    return failures


def _compare_anomaly_debt(
    current_active: Iterable[Mapping[str, Any]],
    baseline_active: Iterable[Mapping[str, Any]],
    resolved_history: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Compare two anomaly multisets without mutating either registry."""
    current = _coalesce_active_debt(current_active)
    previous = _coalesce_active_debt(baseline_active)
    history = [
        _canonicalize(dict(entry))
        for entry in resolved_history
        if isinstance(entry, Mapping)
    ]
    history.sort(
        key=lambda entry: (
            str(entry.get("fingerprint", "")),
            str(entry.get("resolved_at", "")),
        )
    )
    resolved_fingerprints = {
        str(entry.get("fingerprint", ""))
        for entry in history
        if entry.get("fingerprint")
    }

    failures = _active_debt_qualification_failures(current)
    improvements: list[str] = []
    unchanged: list[str] = []
    new: list[str] = []
    resolved: list[str] = []
    regressions: list[str] = []
    modified: list[dict[str, str]] = []

    for fingerprint in sorted(set(current) & resolved_fingerprints):
        regressions.append(fingerprint)
        failures.append(
            f"réapparition d'une anomalie résolue fp={fingerprint}"
        )

    exact = sorted(set(current) & set(previous))
    for fingerprint in exact:
        current_entry = current[fingerprint]
        previous_entry = previous[fingerprint]
        unchanged.append(fingerprint)
        current_count = int(current_entry.get("occurrence_count", 0))
        previous_count = int(previous_entry.get("occurrence_count", 0))
        if current_count > previous_count:
            failures.append(
                "croissance d'occurrences "
                f"fp={fingerprint}: {previous_count}→{current_count}"
            )
        elif current_count < previous_count:
            improvements.append(
                "diminution d'occurrences "
                f"fp={fingerprint}: {previous_count}→{current_count}"
            )
        current_severity = str(current_entry.get("severity", "blocking"))
        previous_severity = str(previous_entry.get("severity", "blocking"))
        if _ANOMALY_SEVERITY_RANK.get(
            current_severity, len(_ANOMALY_SEVERITY_RANK)
        ) > _ANOMALY_SEVERITY_RANK.get(previous_severity, -1):
            failures.append(
                "aggravation de sévérité "
                f"fp={fingerprint}: {previous_severity}→{current_severity}"
            )
        if (
            previous_entry.get("blocking") is False
            and current_entry.get("blocking") is True
        ):
            failures.append(
                "aggravation du caractère bloquant "
                f"fp={fingerprint}: False→True"
            )
        current_disposition = str(
            current_entry.get("disposition", "open_debt")
        )
        previous_disposition = str(
            previous_entry.get("disposition", "open_debt")
        )
        if current_disposition != previous_disposition:
            failures.append(
                "perte ou modification de disposition "
                f"fp={fingerprint}: "
                f"{previous_disposition}→{current_disposition}"
            )
        if current_entry.get("qualification_digest") != previous_entry.get(
            "qualification_digest"
        ):
            failures.append(
                f"qualification modifiée fp={fingerprint}: "
                "qualification_digest différent"
            )

    unmatched_current = set(current) - set(exact)
    unmatched_previous = set(previous) - set(exact)
    previous_by_locator: dict[str, list[str]] = defaultdict(list)
    current_by_locator: dict[str, list[str]] = defaultdict(list)
    for fingerprint in unmatched_previous:
        locator = str(previous[fingerprint].get("locator_key", ""))
        if locator:
            previous_by_locator[locator].append(fingerprint)
    for fingerprint in unmatched_current:
        locator = str(current[fingerprint].get("locator_key", ""))
        if locator:
            current_by_locator[locator].append(fingerprint)
    for locator in sorted(set(previous_by_locator) & set(current_by_locator)):
        old_values = sorted(previous_by_locator[locator])
        new_values = sorted(current_by_locator[locator])
        for old_fingerprint, new_fingerprint in zip(old_values, new_values):
            old_entry = previous[old_fingerprint]
            new_entry = current[new_fingerprint]
            modified.append(
                {
                    "current": new_fingerprint,
                    "previous": old_fingerprint,
                }
            )
            failures.append(
                "anomalie modifiée "
                f"locator={locator}: {old_fingerprint}→{new_fingerprint}"
            )
            old_count = int(old_entry.get("occurrence_count", 0))
            new_count = int(new_entry.get("occurrence_count", 0))
            if new_count > old_count:
                failures.append(
                    "croissance d'occurrences sur anomalie modifiée "
                    f"locator={locator}: {old_count}→{new_count}"
                )
            elif new_count < old_count:
                improvements.append(
                    "diminution d'occurrences sur anomalie modifiée "
                    f"locator={locator}: {old_count}→{new_count}"
                )
            old_severity = str(old_entry.get("severity", "blocking"))
            new_severity = str(new_entry.get("severity", "blocking"))
            if _ANOMALY_SEVERITY_RANK.get(
                new_severity, len(_ANOMALY_SEVERITY_RANK)
            ) > _ANOMALY_SEVERITY_RANK.get(old_severity, -1):
                failures.append(
                    "aggravation de sévérité sur anomalie modifiée "
                    f"locator={locator}: {old_severity}→{new_severity}"
                )
            if (
                old_entry.get("blocking") is False
                and new_entry.get("blocking") is True
            ):
                failures.append(
                    "aggravation du caractère bloquant sur anomalie modifiée "
                    f"locator={locator}: False→True"
                )
            old_disposition = str(
                old_entry.get("disposition", "open_debt")
            )
            new_disposition = str(
                new_entry.get("disposition", "open_debt")
            )
            if old_disposition != new_disposition:
                failures.append(
                    "perte ou modification de disposition sur anomalie modifiée "
                    f"locator={locator}: "
                    f"{old_disposition}→{new_disposition}"
                )
            unmatched_previous.discard(old_fingerprint)
            unmatched_current.discard(new_fingerprint)

    for fingerprint in sorted(unmatched_previous):
        resolved.append(fingerprint)
        improvements.append(f"disparition fp={fingerprint}")

    for fingerprint in sorted(unmatched_current):
        if fingerprint in resolved_fingerprints:
            if fingerprint not in regressions:
                regressions.append(fingerprint)
                failures.append(
                    f"réapparition d'une anomalie résolue fp={fingerprint}"
                )
        else:
            new.append(fingerprint)
            failures.append(f"anomalie nouvelle fp={fingerprint}")

    return {
        "failures": sorted(set(failures)),
        "improvements": sorted(set(improvements)),
        "modified": modified,
        "new": new,
        "regressions": regressions,
        "resolved": resolved,
        "resolved_history": history,
        "success": not failures,
        "unchanged": unchanged,
    }


_QUALIFICATION_DIGEST_FAILURE_PREFIX = "qualification modifiée fp="
_QUALIFICATION_DIGEST_FAILURE_SUFFIX = ": qualification_digest différent"
_QUALIFICATION_DIGEST_BOOTSTRAP_EXEMPT_FIELDS = frozenset({"qualification_digest"})


def _qualification_digest_bootstrap_diagnosis(
    current_active: Sequence[Mapping[str, Any]],
    baseline_active: Sequence[Mapping[str, Any]],
    comparison: Mapping[str, Any],
) -> tuple[bool, list[str]]:
    """Decide whether a fail-on-new drift is exclusively a mechanical
    qualification_digest realignment (e.g. after a reviewed policy
    control_digest change) with zero other change of any kind.

    ``_compare_anomaly_debt`` does not itself compare every field (notably
    ``owner`` and ``category`` are outside its regression contract), so this
    function independently re-verifies every field of every matched
    fingerprint — not just the failures ``_compare_anomaly_debt`` happened to
    report — before a bootstrap is allowed to bypass any precondition.

    Returns ``(True, [])`` only when the active fingerprint set is byte-for-
    byte identical before and after except for ``qualification_digest``, and
    every reported failure is a ``qualification_digest`` mismatch. Anything
    else — a new anomaly, a resolved/regressed fingerprint, an occurrence/
    severity/blocking/disposition/owner/category change, a locator-based
    substitution — is surfaced verbatim in the second element and makes the
    diagnosis impure.
    """

    offending = [
        str(failure)
        for failure in comparison.get("failures", [])
        if not (
            str(failure).startswith(_QUALIFICATION_DIGEST_FAILURE_PREFIX)
            and str(failure).endswith(_QUALIFICATION_DIGEST_FAILURE_SUFFIX)
        )
    ]
    for key in ("new", "resolved", "regressions", "modified", "improvements"):
        if comparison.get(key):
            offending.append(f"jeu non vide de type '{key}' pendant un bootstrap")

    current = _coalesce_active_debt(current_active)
    previous = _coalesce_active_debt(baseline_active)
    if set(current) != set(previous):
        offending.append(
            "ensemble de fingerprints modifié pendant un bootstrap"
        )
    else:
        for fingerprint in sorted(current):
            current_entry = current[fingerprint]
            previous_entry = previous[fingerprint]
            fields = (
                set(current_entry)
                | set(previous_entry)
            ) - _QUALIFICATION_DIGEST_BOOTSTRAP_EXEMPT_FIELDS
            for field in sorted(fields):
                if current_entry.get(field) != previous_entry.get(field):
                    offending.append(
                        "champ non cryptographique modifié "
                        f"fp={fingerprint}:{field}"
                    )

    pure = not offending and bool(comparison.get("failures"))
    return pure, sorted(set(offending))


def _approved_baseline_extension_diagnosis(
    root: Path,
    current_active: Sequence[Mapping[str, Any]],
    baseline_payload: Mapping[str, Any],
    comparison: Mapping[str, Any],
    *,
    approved_by: str,
) -> tuple[bool, list[str]]:
    """Verify that baseline drift is exactly the human-approved transition."""

    offending: list[str] = []
    try:
        policy = _baseline_qualification.load_policy(
            root / BASELINE_QUALIFICATION_POLICY_FILE
        )
        dispositions = _load_dispositions(root)
    except (
        InventoryError,
        OSError,
        _baseline_qualification.QualificationError,
    ) as exc:
        return False, [f"politique ou dispositions indisponibles:{exc}"]

    decision = policy.get("decision")
    approved_set = policy.get("approved_set")
    if not isinstance(decision, Mapping) or not isinstance(
        approved_set,
        Mapping,
    ):
        return False, ["contrat de décision ou jeu approuvé absent"]
    if decision.get("approved_by") != approved_by.strip():
        offending.append("approbateur différent de la décision de politique")
    if decision.get("baseline_purpose") != "debt_regression_control":
        offending.append("baseline_purpose non limité au contrôle de dette")
    if decision.get("release_acceptance") is not False:
        offending.append("release_acceptance doit rester false")

    baseline_active = baseline_payload.get("active")
    baseline_resolved = baseline_payload.get("resolved")
    if not isinstance(baseline_active, list) or not isinstance(
        baseline_resolved, list
    ):
        return False, ["payload de baseline initiale invalide"]

    current = _coalesce_active_debt(current_active)
    previous = _coalesce_active_debt(baseline_active)
    recomputed_comparison = _compare_anomaly_debt(
        current_active,
        baseline_active,
        baseline_resolved,
    )
    if _canonicalize(comparison) != _canonicalize(recomputed_comparison):
        offending.append("comparaison de baseline fournie incohérente")
    comparison = recomputed_comparison
    new_fingerprints = sorted(set(current) - set(previous))
    retained_fingerprints = sorted(set(current) & set(previous))
    for fingerprint in retained_fingerprints:
        if _canonicalize(current[fingerprint]) != _canonicalize(
            previous[fingerprint]
        ):
            offending.append(
                "fingerprint conservé modifié intégralement:"
                f"{fingerprint}"
            )
    transition = policy.get("approved_transition")

    if transition is None:
        if set(previous) - set(current):
            offending.append(
                "fingerprint historique supprimé pendant l'extension"
            )
        if comparison.get("modified"):
            offending.append(
                "anomalie historique modifiée pendant l'extension"
            )
        if comparison.get("resolved"):
            offending.append("anomalie résolue pendant l'extension")
        if comparison.get("regressions"):
            offending.append(
                "anomalie résolue réapparue pendant l'extension"
            )
        if sorted(str(value) for value in comparison.get("new", [])) != (
            new_fingerprints
        ):
            offending.append(
                "jeu new incohérent avec les fingerprints ajoutés"
            )
        expected_failures = {
            f"anomalie nouvelle fp={fingerprint}"
            for fingerprint in new_fingerprints
        }
        if {
            str(value) for value in comparison.get("failures", [])
        } != expected_failures:
            offending.append("dérive non exclusivement constituée d'ajouts")
    elif not isinstance(transition, Mapping):
        offending.append("contrat approved_transition invalide")
    else:
        resolved_fingerprints = sorted(set(previous) - set(current))
        modified_pairs = [
            {
                "current": str(value.get("current", "")),
                "previous": str(value.get("previous", "")),
            }
            for value in comparison.get("modified", [])
            if isinstance(value, Mapping)
        ]
        expected_modified_pairs = transition.get("modified_pairs")
        if modified_pairs != expected_modified_pairs:
            offending.append("paires de remplacement différentes du contrat")
        serialized_pairs = json.dumps(
            _canonicalize(modified_pairs),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        modified_pairs_digest = (
            "sha256:"
            + hashlib.sha256(_utf8_bytes(serialized_pairs)).hexdigest()
        )
        if modified_pairs_digest != transition.get("modified_pairs_digest"):
            offending.append("digest des paires de remplacement différent")

        modified_current = {
            pair["current"] for pair in modified_pairs if pair["current"]
        }
        modified_previous = {
            pair["previous"] for pair in modified_pairs if pair["previous"]
        }
        expected_new = sorted(set(new_fingerprints) - modified_current)
        expected_resolved = sorted(
            set(resolved_fingerprints) - modified_previous
        )
        if sorted(str(value) for value in comparison.get("new", [])) != (
            expected_new
        ):
            offending.append("jeu new différent de la transition approuvée")
        if sorted(str(value) for value in comparison.get("resolved", [])) != (
            expected_resolved
        ):
            offending.append(
                "jeu resolved différent de la transition approuvée"
            )
        if comparison.get("regressions"):
            offending.append("anomalie resolved réapparue pendant l'extension")

        expected_failures = {
            f"anomalie nouvelle fp={fingerprint}"
            for fingerprint in expected_new
        }
        for pair in modified_pairs:
            previous_record = previous.get(pair["previous"], {})
            locator = str(previous_record.get("locator_key", ""))
            expected_failures.add(
                "anomalie modifiée "
                f"locator={locator}: {pair['previous']}→{pair['current']}"
            )
        if {
            str(value) for value in comparison.get("failures", [])
        } != expected_failures:
            offending.append(
                "échecs de comparaison hors transition approuvée"
            )

        if _baseline_payload_digest(baseline_payload) != transition.get(
            "initial_baseline_digest"
        ):
            offending.append("digest de baseline initiale différent")
        if len(previous) != transition.get(
            "initial_active_fingerprint_count"
        ):
            offending.append("nombre actif initial différent")
        if len(baseline_resolved) != transition.get(
            "initial_resolved_fingerprint_count"
        ):
            offending.append("historique resolved initial différent")
        if len(retained_fingerprints) != transition.get(
            "retained_fingerprint_count"
        ):
            offending.append("nombre de fingerprints conservés différent")
        if len(resolved_fingerprints) != transition.get(
            "resolved_fingerprint_count"
        ):
            offending.append("nombre de fingerprints résolus différent")
        if len(current) != transition.get("final_active_fingerprint_count"):
            offending.append("nombre actif final différent")
        if _baseline_qualification.fingerprint_set_digest(
            resolved_fingerprints
        ) != transition.get("resolved_fingerprint_digest"):
            offending.append("digest des fingerprints résolus différent")
        resolved_category_counts = Counter(
            str(previous[fingerprint].get("category", ""))
            for fingerprint in resolved_fingerprints
        )
        if dict(sorted(resolved_category_counts.items())) != dict(
            sorted(transition.get("resolved_category_counts", {}).items())
        ):
            offending.append("catégories des fingerprints résolus différentes")

    if len(new_fingerprints) != approved_set.get("fingerprint_count"):
        offending.append("nombre de fingerprints différent du jeu approuvé")
    if _baseline_qualification.fingerprint_set_digest(
        new_fingerprints
    ) != approved_set.get("fingerprint_digest"):
        offending.append("digest des fingerprints différent du jeu approuvé")

    added_records = [current[fingerprint] for fingerprint in new_fingerprints]
    category_counts = Counter(
        str(record.get("category", "")) for record in added_records
    )
    owner_counts = Counter(
        str(record.get("owner", "")) for record in added_records
    )
    if dict(sorted(category_counts.items())) != dict(
        sorted(approved_set.get("category_counts", {}).items())
    ):
        offending.append("catégories différentes du jeu approuvé")
    if dict(sorted(owner_counts.items())) != dict(
        sorted(approved_set.get("owner_counts", {}).items())
    ):
        offending.append("propriétaires différents du jeu approuvé")

    policy_digest = str(policy.get("control_digest", ""))
    for record in added_records:
        fingerprint = str(record.get("fingerprint", ""))
        disposition = dispositions.get(fingerprint)
        if (
            record.get("qualified") is not True
            or record.get("disposition") != "open_debt"
            or record.get("blocking") is not True
        ):
            offending.append(f"ajout non qualifié comme open_debt:{fingerprint}")
        if not isinstance(disposition, Mapping):
            offending.append(f"disposition ajoutée absente:{fingerprint}")
            continue
        if (
            disposition.get("fingerprint") != fingerprint
            or disposition.get("qualification_policy_digest") != policy_digest
            or disposition.get("disposition") != "open_debt"
            or disposition.get("release_blocking") is not True
            or disposition.get("owner") != record.get("owner")
        ):
            offending.append(
                f"disposition ajoutée non conforme à open_debt:{fingerprint}"
            )

    approved = not offending and bool(new_fingerprints)
    return approved, sorted(set(offending))


def _evaluate_baseline(
    inventory: Mapping[str, Any], baseline_path: Path
) -> list[str]:
    payload = _load_baseline_payload(baseline_path)
    if payload is None:
        return [f"baseline introuvable ou invalide: {baseline_path}"]
    if payload.get("schema_version") != SCHEMA_VERSION:
        return ["schema_version baseline inattendu"]
    if payload.get("provisional") is True:
        return ["baseline provisoire"]
    if payload.get("fingerprint_schema_version") != FINGERPRINT_SCHEMA_VERSION:
        return ["fingerprint_schema_version baseline inattendue"]
    if not isinstance(payload.get("active"), list) or not isinstance(
        payload.get("resolved"), list
    ):
        return ["champs active/resolved baseline invalides"]
    return list(
        _compare_anomaly_debt(
            _current_active_debt(inventory),
            payload["active"],
            payload["resolved"],
        )["failures"]
    )


def canonical_model_payload(inventory: Mapping[str, Any]) -> dict[str, Any]:
    if (
        "assemblies" in inventory
        and "declared_assemblies" in inventory
        and _canonicalize(inventory["assemblies"])
        != _canonicalize(inventory["declared_assemblies"])
    ):
        raise InventoryError(
            "alias assemblies divergent de declared_assemblies"
        )
    missing = [
        field
        for field in CANONICAL_MODEL_FIELDS
        if field not in inventory
        and not (field == "declared_assemblies" and "assemblies" in inventory)
    ]
    if missing:
        raise InventoryError(
            "modèle canonique incomplet: " + ", ".join(sorted(missing))
        )
    return {
        field: _canonicalize(
            inventory[field]
            if field in inventory
            else inventory["assemblies"]
        )
        for field in CANONICAL_MODEL_FIELDS
    }


def _serialize_canonical_model(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _model_digest(inventory: Mapping[str, Any]) -> str:
    serialized = _serialize_canonical_model(canonical_model_payload(inventory))
    return f"sha256:{hashlib.sha256(_utf8_bytes(serialized)).hexdigest()}"


def _now_utc() -> str:
    return (
        datetime.datetime.now(datetime.UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _format_epoch_utc(epoch: int) -> str:
    try:
        instant = datetime.datetime.fromtimestamp(epoch, tz=datetime.UTC)
    except (OverflowError, OSError, ValueError) as exc:
        raise InventoryError(f"timestamp hors plage: {epoch}") from exc
    return instant.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _generation_timestamp(
    root: Path,
    *,
    required: bool = False,
) -> str | None:
    source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if source_date_epoch is not None:
        try:
            epoch = int(source_date_epoch)
            if epoch < 0:
                raise ValueError
            return _format_epoch_utc(epoch)
        except (InventoryError, ValueError):
            pass
    commit_epoch = (
        _git_required_value(
            root,
            ("show", "-s", "--format=%ct", "HEAD"),
            description="git commit timestamp",
        )
        if required
        else _git_value(root, ("show", "-s", "--format=%ct", "HEAD"), "")
    )
    if not commit_epoch:
        return None
    try:
        epoch = int(commit_epoch)
        if epoch < 0:
            raise ValueError
    except ValueError as exc:
        if required:
            raise InventoryError(
                f"git commit timestamp unavailable: {commit_epoch!r}"
            ) from exc
        return None
    return _format_epoch_utc(epoch)


def _git_value(repository: Path, args: tuple[str, ...], default: str = "") -> str:
    try:
        return (
            subprocess.run(
                ["git", "-C", str(repository), *args],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            .stdout.decode("utf-8", errors="replace")
            .strip()
        )
    except (subprocess.CalledProcessError, OSError):
        return default


def _git_required_value(
    repository: Path,
    args: tuple[str, ...],
    *,
    description: str,
) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repository), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (subprocess.CalledProcessError, OSError) as exc:
        raise InventoryError(f"{description} unavailable") from exc
    value = completed.stdout.decode("utf-8", errors="replace").strip()
    if not value:
        raise InventoryError(f"{description} unavailable")
    return value


GitStatusEntry = tuple[str, tuple[str, ...]]


def _parse_git_status_z(payload: bytes) -> list[GitStatusEntry]:
    entries: list[GitStatusEntry] = []
    fields = payload.split(b"\0")
    index = 0
    while index < len(fields):
        field = fields[index]
        index += 1
        if not field:
            continue
        if len(field) < 4 or field[2:3] != b" ":
            continue
        marker = field[:2].decode("ascii", errors="replace")
        current_path = field[3:].decode("utf-8", errors="surrogateescape")
        paths = (current_path,)
        if "R" in marker or "C" in marker:
            if index >= len(fields) or not fields[index]:
                continue
            original_path = fields[index].decode(
                "utf-8", errors="surrogateescape"
            )
            index += 1
            paths = (original_path, current_path)
        entries.append((marker, paths))
    return entries


def _git_status(
    repository: Path,
    *,
    required: bool = False,
) -> list[GitStatusEntry]:
    try:
        completed = subprocess.run(
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
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, OSError) as exc:
        if required:
            raise InventoryError("git status unavailable") from exc
        return []
    return _parse_git_status_z(completed.stdout)


def _git_modified_tracked(
    repository: Path, *, status: Iterable[GitStatusEntry] | None = None
) -> list[str]:
    modified: set[str] = set()
    for marker, paths in _git_status(repository) if status is None else status:
        if marker == "??" or not marker.strip():
            continue
        modified.update(paths)
    return sorted(modified)


def _git_relevant_untracked(
    repository: Path,
    *,
    tracked: Mapping[str, str],
    role_patterns: Mapping[str, list[str]],
    role_order: list[str],
    status: Iterable[GitStatusEntry] | None = None,
) -> list[str]:
    canonical_patterns, canonical_default, canonical_order = _default_role_patterns()
    untracked: list[str] = []
    for path in _git_untracked(repository, status=status):
        configured_role = _classify_source_path(
            path,
            tracked,
            default="transversal",
            role_patterns=role_patterns,
            role_order=role_order,
        )
        canonical_role = _classify_source_path(
            path,
            {},
            default=canonical_default,
            role_patterns=canonical_patterns,
            role_order=canonical_order,
        )
        if (
            configured_role in RELEVANT_UNTRACKED_SOURCE_ROLES
            or canonical_role in RELEVANT_UNTRACKED_SOURCE_ROLES
            or (
                "transversal" in {configured_role, canonical_role}
                and _is_model_source(path)
            )
        ):
            untracked.append(path)
    return sorted(untracked)


def _git_untracked(
    repository: Path, *, status: Iterable[GitStatusEntry] | None = None
) -> list[str]:
    return sorted(
        path
        for marker, paths in (
            _git_status(repository) if status is None else status
        )
        if marker == "??"
        for path in paths
    )


def _status_paths(entry: GitStatusEntry) -> tuple[str, ...]:
    return entry[1]


def _is_generation_internal_path(
    path: str, managed_output_paths: frozenset[str]
) -> bool:
    normalized = _normalize_path_for_match(path)
    return (
        normalized in managed_output_paths
        or _is_active_generation_internal_path(normalized)
    )


def _is_active_generation_internal_path(path: str) -> bool:
    normalized = _normalize_path_for_match(path)
    return normalized == GENERIC_LOCK_FILE


def _git_generation_status(
    repository: Path,
    *,
    managed_output_paths: Iterable[str] = (),
    required: bool = False,
) -> list[GitStatusEntry]:
    excluded_outputs = frozenset(
        DEFAULT_MANAGED_OUTPUT_PATHS
        | {
            _normalize_path_for_match(path)
            for path in managed_output_paths
        }
    )
    return [
        entry
        for entry in _git_status(repository, required=required)
        if not _status_paths(entry)
        or not all(
            _is_generation_internal_path(path, excluded_outputs)
            for path in _status_paths(entry)
        )
    ]


def _path_matches_identity(
    repository: Path,
    path: str,
    expected: tuple[int, int],
) -> bool:
    normalized = _normalize_path_for_match(path)
    try:
        metadata = (repository / normalized).stat(follow_symlinks=False)
    except OSError:
        return False
    return (metadata.st_dev, metadata.st_ino) == expected


def _exclude_owned_generation_paths(
    repository: Path,
    status: Iterable[GitStatusEntry],
    allowed_generation_paths: Mapping[str, tuple[int, int]] | None,
) -> list[GitStatusEntry]:
    entries = list(status)
    if not allowed_generation_paths:
        return entries
    allowed = {
        _normalize_path_for_match(path): identity
        for path, identity in allowed_generation_paths.items()
    }

    def is_owned_generation_path(path: str) -> bool:
        normalized = _normalize_path_for_match(path)
        expected = allowed.get(normalized)
        if expected is None or not _path_matches_identity(
            repository,
            normalized,
            expected,
        ):
            return False
        if normalized == GENERIC_LOCK_FILE:
            return True
        parts = PurePosixPath(normalized).parts
        return bool(
            len(parts) == 2
            and _TRANSACTION_DIRECTORY_RE.fullmatch(parts[0])
            and (
                parts[1]
                in {
                    "journal-ready",
                    "journal.json",
                    "preparing.json",
                    "transaction-owner",
                }
                or _TRANSACTION_ENTRY_RE.fullmatch(parts[1])
            )
        )

    return [
        entry
        for entry in entries
        if not _status_paths(entry)
        or not all(
            is_owned_generation_path(path)
            for path in _status_paths(entry)
        )
    ]


def _repo_branch(root: Path, *, required: bool = False) -> str | None:
    branch = (
        _git_required_value(
            root,
            ("rev-parse", "--abbrev-ref", "HEAD"),
            description="git branch",
        )
        if required
        else _git_value(root, ("rev-parse", "--abbrev-ref", "HEAD"), "")
    )
    if not branch or branch == "HEAD":
        if required:
            raise InventoryError("git branch unavailable or detached")
        return None
    return branch


def _repo_head_sha(root: Path, *, required: bool = False) -> str | None:
    head = (
        _git_required_value(
            root,
            ("rev-parse", "HEAD"),
            description="git HEAD",
        )
        if required
        else _git_value(root, ("rev-parse", "HEAD"), "")
    )
    if not head:
        if required:
            raise InventoryError("git HEAD unavailable")
        return None
    return head


def _file_sha256(path: Path) -> str:
    if not path.exists():
        return "sha256:missing"
    return _sha256_file(path)


def _command_version(command: list[str]) -> str:
    executable = (
        command[0]
        if Path(command[0]).is_absolute()
        else shutil.which(command[0])
    )
    if not executable:
        return "unavailable"
    try:
        completed = subprocess.run(
            [str(executable), *command[1:]],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=PDFINFO_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return "unavailable"
    return next(
        (line.strip() for line in completed.stdout.splitlines() if line.strip()),
        "unavailable",
    )


def _file_version_signature(root: Path) -> dict[str, str]:
    del root
    return {
        "git": _command_version(["git", "--version"]),
        "latexmk": _command_version(["latexmk", "-version"]),
        "pdfinfo": _command_version(["pdfinfo", "-v"]),
        "python": _command_version([sys.executable, "--version"]),
        "texlive": _command_version(["pdflatex", "--version"]),
    }


def _generator_file_digests() -> dict[str, str]:
    digests: dict[str, str] = {}
    for filename in GENERATOR_COMPONENT_PATHS:
        path = _SCRIPTS_ROOT / filename
        if not path.is_file():
            raise InventoryError(f"composant du générateur absent: scripts/{filename}")
        digests[f"scripts/{filename}"] = _sha256_file(path)
    return dict(sorted(digests.items()))


def _aggregate_generator_digest(generator_files: Mapping[str, str]) -> str:
    payload = json.dumps(
        dict(sorted(generator_files.items())),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"sha256:{hashlib.sha256(_utf8_bytes(payload)).hexdigest()}"


def _generator_sha256() -> str:
    return _aggregate_generator_digest(_generator_file_digests())


def _build_provenance(
    root: Path,
    *,
    source_roles: Mapping[str, str],
    role_patterns: Mapping[str, list[str]],
    role_order: list[str],
    managed_output_paths: Iterable[str] = (),
    require_git: bool = False,
) -> dict[str, Any]:
    generator_files = _generator_file_digests()
    common = {
        "generator_version": SCHEMA_VERSION,
        "generator_sha256": _aggregate_generator_digest(generator_files),
        "generator_files": generator_files,
        "tool_versions": _file_version_signature(root),
    }
    try:
        head_sha = _repo_head_sha(root, required=True)
        branch = _repo_branch(root, required=True)
        generation_status = _git_generation_status(
            root,
            managed_output_paths=managed_output_paths,
            required=True,
        )
        generated_at_utc = _generation_timestamp(root, required=True)
    except InventoryError as exc:
        if require_git:
            raise InventoryError(
                f"Git provenance unavailable: {exc}"
            ) from exc
        return {
            **common,
            "git_available": False,
            "head_sha": None,
            "branch": None,
            "dirty": None,
            "modified_tracked": [],
            "untracked_relevant": [],
            "generated_at_utc": None,
            "errors": [str(exc)],
        }
    return {
        **common,
        "git_available": True,
        "head_sha": head_sha,
        "branch": branch,
        "dirty": bool(generation_status),
        "modified_tracked": _git_modified_tracked(root, status=generation_status),
        "untracked_relevant": _git_relevant_untracked(
            root,
            tracked=source_roles,
            role_patterns=role_patterns,
            role_order=role_order,
            status=generation_status,
        ),
        "generated_at_utc": generated_at_utc,
        "errors": [],
    }


def _clean_path(path: str, *, role: str, repository: Path) -> None:
    if path is None:
        return
    repository = repository.resolve()
    if "://" in path or Path(path).is_absolute():
        raise InventoryError(f"{role}: outside repository (absolute path)")
    parsed = PurePosixPath(path)
    if ".." in parsed.parts:
        raise InventoryError(f"{role}: outside repository (parent traversal)")
    candidate = repository / path
    absolute = candidate.resolve()
    if not absolute.is_relative_to(repository):
        current = repository
        escaped_by_symlink = False
        for part in parsed.parts:
            current /= part
            if current.is_symlink():
                escaped_by_symlink = True
                break
            if not current.exists():
                break
        if escaped_by_symlink:
            raise InventoryError(f"{role}: symlink escape outside repository")
        raise InventoryError(f"{role}: outside repository")


def _ensure_output_paths(*, root: Path, audit_dir: str, etat_path: str) -> tuple[Path, Path]:
    _clean_path(audit_dir, role="--audit-dir", repository=root)
    _clean_path(etat_path, role="--etat-path", repository=root)
    audit_root = root / audit_dir
    etat_file = root / etat_path
    if not etat_file.is_relative_to(root):
        raise InventoryError("--etat-path doit rester dans le dépôt")
    return audit_root, etat_file


def _write_text_atomically(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=str(path.parent),
        delete=False,
    ) as handle:
        temp_path = Path(handle.name)
        try:
            handle.write(content)
            handle.flush()
        except OSError:
            temp_path.unlink(missing_ok=True)
            raise
    try:
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)


def _validate_output_payload(
    path: Path,
    content: str,
    *,
    required_fields: set[str] | None = None,
    require_mapping: bool = True,
) -> dict[str, Any]:
    if not isinstance(content, str):
        raise InventoryError(f"artefact non textuel: {path}")
    if not content.strip():
        raise InventoryError(f"artefact vide: {path}")
    try:
        _utf8_bytes(content)
    except UnicodeEncodeError as exc:  # pragma: no cover
        raise InventoryError(f"encodage UTF-8 invalide pour {path}: {exc}") from exc

    payload: Any
    suffix = path.suffix.lower()
    if suffix == ".md":
        return {}
    if suffix == ".json":
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise InventoryError(f"artefact JSON invalide {path}: {exc}") from exc
    else:
        try:
            payload = yaml.safe_load(content)
        except yaml.YAMLError as exc:
            raise InventoryError(f"artefact YAML invalide {path}: {exc}") from exc

    if require_mapping and not isinstance(payload, Mapping):
        raise InventoryError(f"artefact {path}: payload racine non objet")
    if required_fields:
        if not isinstance(payload, Mapping):
            missing = sorted(required_fields)
            raise InventoryError(
                f"champs manquants dans {path}: {', '.join(missing)}"
            )
        missing = sorted(required_fields - set(payload.keys()))
        if missing:
            raise InventoryError(
                f"champs manquants dans {path}: {', '.join(missing)}"
            )
    return payload


def _ensure_clean_tree(
    repository: Path,
    *,
    mode: str | None = None,
    allowed_generation_paths: Mapping[str, tuple[int, int]] | None = None,
) -> None:
    if mode is None:
        return
    if mode not in {"worktree", "head"}:
        raise InventoryError(f"unknown clean mode: {mode}")
    if mode == "head":
        if _git_value(repository, ("rev-parse", "--is-inside-work-tree"), "") != "true":
            raise InventoryError("head clean mode requires a Git repository")
        head = _repo_head_sha(repository)
        if not head:
            raise InventoryError("head clean mode requires a resolved HEAD")
        branch = _git_value(
            repository, ("symbolic-ref", "--quiet", "--short", "HEAD"), ""
        )
        if not branch:
            raise InventoryError("head clean mode requires an attached branch")
    status = _git_status(repository)
    status = _exclude_owned_generation_paths(
        repository,
        status,
        allowed_generation_paths,
    )
    if status:
        raise InventoryError(f"{mode} clean mode found local modifications")


def _process_start_token(pid: int) -> str | None:
    try:
        stat = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
        fields = stat.rsplit(")", 1)[1].strip().split()
        return fields[19]
    except (IndexError, OSError, UnicodeError):
        pass
    try:
        completed = subprocess.run(
            ["ps", "-o", "lstart=", "-p", str(pid)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=1,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    started = completed.stdout.strip()
    if not started:
        return None
    return hashlib.sha256(_utf8_bytes(started)).hexdigest()


def _parse_lock_timestamp(value: object) -> datetime.datetime | None:
    if not isinstance(value, str):
        return None
    try:
        timestamp = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if timestamp.tzinfo is None:
        return None
    return timestamp.astimezone(datetime.UTC)


def _parse_lock_record(raw: bytes) -> dict[str, Any] | None:
    try:
        if len(raw) > 64 * 1024:
            return None
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    pid = payload.get("pid")
    token = payload.get("process_start_token")
    created = _parse_lock_timestamp(payload.get("created_at_utc"))
    if (
        not isinstance(pid, int)
        or isinstance(pid, bool)
        or pid <= 0
        or not isinstance(token, str)
        or not token
        or created is None
    ):
        return None
    return payload


def _read_lock_record_fd(fd: int) -> dict[str, Any] | None:
    try:
        os.lseek(fd, 0, os.SEEK_SET)
        raw = os.read(fd, 64 * 1024 + 1)
    except OSError:
        return None
    return _parse_lock_record(raw)


def _lock_owner_is_live(record: Mapping[str, Any]) -> bool:
    pid = int(record["pid"])
    expected_token = str(record["process_start_token"])
    current_token = _process_start_token(pid)
    if current_token is not None:
        return current_token == expected_token
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _quarantine_stale_lock(lock_path: Path) -> bool:
    if fcntl is None:
        return False
    open_flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    try:
        fd = os.open(lock_path, open_flags)
    except OSError:
        return False
    try:
        stale_stat = os.fstat(fd)
        if not stat.S_ISREG(stale_stat.st_mode):
            return False
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return False
        record = _read_lock_record_fd(fd)
        if record is None:
            return False
        created = _parse_lock_timestamp(record["created_at_utc"])
        if created is None:
            return False
        age = (datetime.datetime.now(datetime.UTC) - created).total_seconds()
        if age < LOCK_STALE_SECONDS or _lock_owner_is_live(record):
            return False
        snapshot_identity = (stale_stat.st_dev, stale_stat.st_ino)
        try:
            current_stat = lock_path.stat(follow_symlinks=False)
        except OSError:
            return False
        if (
            not stat.S_ISREG(current_stat.st_mode)
            or (current_stat.st_dev, current_stat.st_ino) != snapshot_identity
        ):
            return False
        quarantine_path = lock_path.with_name(
            f"{lock_path.name}.stale.{stale_stat.st_dev:x}-{stale_stat.st_ino:x}"
        )
        try:
            os.link(
                lock_path,
                quarantine_path,
                follow_symlinks=False,
            )
        except FileExistsError:
            pass
        except OSError:
            return False
        try:
            current_stat = lock_path.stat(follow_symlinks=False)
            quarantine_stat = quarantine_path.stat(follow_symlinks=False)
        except OSError:
            return False
        if (
            not stat.S_ISREG(current_stat.st_mode)
            or (current_stat.st_dev, current_stat.st_ino) != snapshot_identity
            or (quarantine_stat.st_dev, quarantine_stat.st_ino)
            != snapshot_identity
        ):
            return False
        lock_path.unlink()
        return True
    finally:
        os.close(fd)


@contextmanager
def _lock_generation(root: Path):
    lock_path = root / GENERIC_LOCK_FILE
    deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
    start_token = _process_start_token(os.getpid())
    if start_token is None:
        raise InventoryError("cannot identify generation lock owner")
    owner_record = _utf8_bytes(
        json.dumps(
            {
                "created_at_utc": _now_utc(),
                "pid": os.getpid(),
                "process_start_token": start_token,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    )
    fd: int | None = None
    owner_stat: os.stat_result | None = None
    while True:
        try:
            fd = os.open(
                lock_path,
                os.O_CREAT
                | os.O_EXCL
                | os.O_WRONLY
                | getattr(os, "O_CLOEXEC", 0),
                0o600,
            )
            owner_stat = os.fstat(fd)
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_EX)
            _write_all(fd, owner_record)
            os.fsync(fd)
            break
        except FileExistsError:
            if _quarantine_stale_lock(lock_path):
                continue
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise InventoryError("generation lock timeout")
            time.sleep(min(LOCK_POLL_SECONDS, remaining))
        except Exception:
            if fd is not None:
                os.close(fd)
                fd = None
            try:
                current_stat = lock_path.stat(follow_symlinks=False)
                if owner_stat is not None and (
                    current_stat.st_dev,
                    current_stat.st_ino,
                ) == (
                    owner_stat.st_dev,
                    owner_stat.st_ino,
                ):
                    lock_path.unlink()
            except OSError:
                pass
            raise
    try:
        assert owner_stat is not None
        yield {
            GENERIC_LOCK_FILE: (
                owner_stat.st_dev,
                owner_stat.st_ino,
            )
        }
    finally:
        try:
            current_stat = lock_path.stat(follow_symlinks=False)
            if owner_stat is not None and (
                current_stat.st_dev,
                current_stat.st_ino,
            ) == (
                owner_stat.st_dev,
                owner_stat.st_ino,
            ):
                lock_path.unlink()
        except OSError:
            pass
        if fd is not None:
            os.close(fd)

MANUALS: dict[str, dict[str, str]] = {
    "1NSI": {
        "subject": "NSI",
        "level": "Premiere",
        "edition": "courante",
    },
    "1SPE": {
        "subject": "Mathematiques",
        "level": "Premiere specialite",
        "edition": "2026-2027",
    },
    "TNSI": {
        "subject": "NSI",
        "level": "Terminale",
        "edition": "courante",
    },
    "TSPE_2026_2027": {
        "subject": "Mathematiques",
        "level": "Terminale specialite",
        "edition": "2026-2027",
    },
    "TCOMPL": {
        "subject": "Mathematiques",
        "level": "Terminale mathematiques complementaires",
        "edition": "courante",
    },
    "TEXPERTES": {
        "subject": "Mathematiques",
        "level": "Terminale mathematiques expertes",
        "edition": "courante",
    },
}

MANUAL_EXPECTED_LEVELS: dict[str, str] = {
    "1NSI": "1NSI",
    "1SPE": "1SPE",
    "TCOMPL": "TCOMPL",
    "TEXPERTES": "TEXPERTES",
    "TNSI": "TNSI",
    "TSPE_2026_2027": "TSPE",
}

CHAPTER_ROOTS: tuple[PurePosixPath, ...] = (
    PurePosixPath("Mathematiques/manuel-maths/chapitres"),
    PurePosixPath("NSI/chapitres"),
)

COUNT_KEYS: tuple[str, ...] = (
    "capacites",
    "sections_cours",
    "methodes",
    "exercices_principaux",
    "corriges",
    "coups_de_pouce",
    "qcm",
    "diagnostics",
    "remediations",
    "td",
    "evaluations",
    "projets",
)

TYPE_CATEGORIES: dict[str, str] = {
    "cours": "sections_cours",
    "methode": "methodes",
    "exercice": "exercices_principaux",
    "corrige": "corriges",
    "corrige_evaluation": "corriges",
    "evaluation_corrige": "corriges",
    "coup_de_pouce": "coups_de_pouce",
    "qcm": "qcm",
    "diagnostic": "diagnostics",
    "diagnostics": "diagnostics",
    "qcm_diagnostics": "diagnostics",
    "remediation": "remediations",
    "td": "td",
    "evaluation": "evaluations",
    "projet": "projets",
}

SUBTYPE_CATEGORIES: dict[str, str | None] = {
    "diagnostic": "diagnostics",
    "ouverture": None,
    "td_contextualise": "td",
    "td_fil_rouge": "td",
}

KNOWN_UNCOUNTED_TYPES = frozenset({"amenagee"})
KNOWN_UNCOUNTED_SUBTYPES = frozenset({"ouverture"})

REQUIRED_META_FIELDS: tuple[str, ...] = (
    "id",
    "chapitre",
    "type_objet",
    "status",
)

# Object states are the union of the Math and NSI schema enums, plus the
# explicit final approval state required by the collection release policy.
KNOWN_OBJECT_STATUSES = frozenset(
    {
        "approved",
        "draft",
        "generated",
        "manual_review",
        "needs_review",
        "ready",
        "rejected",
        "verified",
    }
)

# Contracts predate the object schemas.  ``draft`` and ``complete`` are present
# in tracked contracts; ``valide`` is the documented post-review transition in
# their own comments.  None implies approval: only an explicit ``approved``
# contract is publishable.
KNOWN_CONTRACT_STATUSES = frozenset({"approved", "complete", "draft", "valide"})

APPROVED_OBJECT_STATUSES = frozenset({"approved"})
APPROVED_CONTRACT_STATUSES = frozenset({"approved"})

# These are release objectives stated by the mission, not observations.  Every
# current state recorded beside them is derived later from the canonical model.
DELIVERABLE_SPECS: dict[str, dict[str, Any]] = {
    "1NSI": {
        "directive": "MISSION_PRIORITAIRE §9",
        "target_chapters": 10,
        "variants": {
            "evaluations": ("evaluations",),
            "livret_methodes": ("methodes",),
            "manuel_eleve": ("eleve",),
            "manuel_professeur": ("professeur",),
            "projets": ("projets",),
            "remediations": ("remediation", "remediations"),
            "version_amenagee": ("amenagee", "amenage"),
        },
    },
    "1SPE": {
        "directive": "MISSION_PRIORITAIRE §8",
        "target_chapters": 10,
        "variants": {
            "banque_evaluations": ("evaluations",),
            "livret_methodes": ("methodes",),
            "livret_remediation": ("remediation", "remediations"),
            "manuel_eleve": ("eleve",),
            "manuel_professeur": ("professeur",),
        },
    },
    "TNSI": {
        "directive": "MISSION_PRIORITAIRE §11",
        "target_chapters": 12,
        "variants": {
            "banque_ecrite": ("banque_ecrite", "ecrite"),
            "banque_pratique": ("banque_pratique", "pratique"),
            "manuel_eleve": ("eleve",),
            "manuel_professeur": ("professeur",),
            "projets": ("projets",),
            "remediations": ("remediation", "remediations"),
            "version_amenagee": ("amenagee", "amenage"),
        },
    },
    "TSPE_2026_2027": {
        "directive": "MISSION_PRIORITAIRE §10",
        # The current mission deliberately requires Phase 1 to settle the
        # edition scope.  Older reports disagree between 12 and 13 chapters.
        "target_chapters": None,
        "variants": {
            "banque_evaluations": ("evaluations",),
            "livret_methodes": ("methodes",),
            "livret_remediation": ("remediation", "remediations"),
            "manuel_eleve": ("eleve",),
            "manuel_professeur": ("professeur",),
        },
    },
    "TCOMPL": {
        "directive": "docs/11_perimetre_terminale_complementaires.md",
        "target_chapters": 9,
        "variants": {
            "manuel_eleve": ("eleve",),
            "manuel_professeur": ("professeur",),
        },
    },
    "TEXPERTES": {
        "directive": "docs/12_perimetre_terminale_expertes.md",
        "target_chapters": 5,
        "variants": {
            "manuel_eleve": ("eleve",),
            "manuel_professeur": ("professeur",),
        },
    },
}

BLOCKING_ANOMALY_CATEGORIES = frozenset(
    {
        "assembler_invalid",
        "missing_corrections",
        "blocking_statuses",
        "broken_assembly_references",
        "broken_latex_references",
        "broken_meta_references",
        "chapters_not_in_manual",
        "context_mismatches",
        "contract_invalid",
        "contract_missing",
        "duplicate_assembly_objects",
        "duplicate_capacity_refs",
        "duplicate_ids",
        "invalid_capacities",
        "invalid_meta_references",
        "invalid_statuses",
        "latex_cycles",
        "metadata_invalid",
        "metadata_missing",
        "missing_assemblers",
        "orphan_files",
        "unassembled_objects",
        "unknown_chapter_prefixes",
        "unclassified_types",
    }
)

STRUCTURAL_ANOMALY_CATEGORIES = frozenset(
    {
        "blocking_statuses",
        "missing_corrections",
        "broken_assembly_references",
        "chapters_not_in_manual",
        "missing_assemblers",
        "unassembled_objects",
        "broken_latex_references",
        "broken_meta_references",
        "orphan_files",
        "metadata_missing",
        "metadata_invalid",
        "invalid_statuses",
        "contract_invalid",
        "contract_missing",
    }
)


class InventoryError(ValueError):
    """Base error for an invalid collection source."""


class ContractError(InventoryError):
    """Raised when a chapter contract cannot be read as a mapping."""


class MetadataError(InventoryError):
    """Raised when a TeX metadata header is missing or malformed."""


class MetadataMissingError(MetadataError):
    """Raised when a TeX content source has no ``% META`` header."""


def git_tracked_files(repository: Path | str) -> tuple[str, ...]:
    """Return repository-relative, sorted paths known to Git.

    Untracked and ignored build products are intentionally invisible to the
    inventory, even when they exist in the working tree.
    """

    root = Path(repository)
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        stdout=subprocess.PIPE,
    )
    paths = completed.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    return tuple(sorted(path for path in paths if path))


def load_contract(path: Path | str) -> dict[str, Any]:
    """Read a chapter YAML contract and validate its top-level shape."""

    source = Path(path)
    try:
        value = yaml.safe_load(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ContractError(f"contrat YAML invalide: {exc}") from exc
    if not isinstance(value, Mapping):
        raise ContractError("le contrat YAML doit etre un objet")
    return _canonicalize_mapping(value)


def read_meta(path: Path | str) -> dict[str, Any]:
    """Read and validate the first-line ``% META: {...}`` JSON header."""

    source = Path(path)
    try:
        with source.open("r", encoding="utf-8") as stream:
            first_line = stream.readline().lstrip("\ufeff").rstrip("\r\n")
    except (OSError, UnicodeError) as exc:
        raise MetadataError(f"lecture META impossible: {exc}") from exc

    prefix = "% META:"
    if not first_line.startswith(prefix):
        raise MetadataMissingError("en-tete % META absent")

    payload = first_line[len(prefix) :].strip()
    try:
        metadata = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise MetadataError(f"JSON META invalide: {exc.msg}") from exc
    if not isinstance(metadata, Mapping):
        raise MetadataError("JSON META doit etre un objet")

    missing = [
        field
        for field in REQUIRED_META_FIELDS
        if not isinstance(metadata.get(field), str) or not metadata[field].strip()
    ]
    if missing:
        raise MetadataError("champs META absents ou invalides: " + ", ".join(missing))
    source_subtype = metadata.get("sous_type")
    if "sous_type" in metadata and not isinstance(source_subtype, str):
        raise MetadataError("champ META sous_type invalide: texte attendu")
    if isinstance(source_subtype, str) and not source_subtype.strip():
        raise MetadataError("champ META sous_type invalide: texte non vide attendu")
    return _canonicalize_mapping(metadata)


def canonical_category(
    source_type: str, source_subtype: str | None = None
) -> str | None:
    """Map a source taxonomy value to a required inventory counter."""

    if isinstance(source_subtype, str) and source_subtype in SUBTYPE_CATEGORIES:
        return SUBTYPE_CATEGORIES[source_subtype]
    return TYPE_CATEGORIES.get(source_type)


def report_source_paths(
    repository: Path | str, tracked_files: tuple[str, ...]
) -> tuple[str, ...]:
    return _report_core.report_source_paths(repository, tracked_files)


def validate_inventory_coherence(inventory: Mapping[str, Any]) -> dict[str, Any]:
    """Cross-check the redundant aggregates kept in the canonical model."""

    sum_violations: list[dict[str, Any]] = []
    status_violations: list[dict[str, Any]] = []
    artifact_violations: list[dict[str, Any]] = []
    pdf_paths = {
        artifact["path"]
        for artifact in inventory.get("pdfs", [])
        if isinstance(artifact, Mapping) and isinstance(artifact.get("path"), str)
    }
    for manual_id, manual in sorted(inventory["manuals"].items()):
        calculated_counts = Counter()
        calculated_statuses = Counter()
        for chapter in manual["chapters"].values():
            calculated_counts.update(chapter["counts"])
            calculated_statuses.update(chapter["statuses"])
        for metric in COUNT_KEYS:
            declared = manual["totals"].get(metric)
            calculated = calculated_counts[metric]
            if declared != calculated:
                sum_violations.append(
                    {
                        "calculated": calculated,
                        "declared": declared,
                        "manual": manual_id,
                        "metric": metric,
                    }
                )
        declared_statuses = dict(sorted(manual["statuses"].items()))
        calculated_status_mapping = dict(sorted(calculated_statuses.items()))
        if declared_statuses != calculated_status_mapping:
            status_violations.append(
                {
                    "calculated": calculated_status_mapping,
                    "declared": declared_statuses,
                    "manual": manual_id,
                }
            )
        manual_paths = [
            artifact.get("path")
            for artifact in manual.get("compiled_artifacts", [])
            if isinstance(artifact, Mapping)
        ]
        expected_manual_paths = [
            artifact["path"]
            for artifact in inventory.get("pdfs", [])
            if isinstance(artifact, Mapping)
            and artifact.get("manual") == manual_id
            and _pdf_core.is_compilation_evidence(
                artifact,
                compiled_source_roles=COMPILED_PDF_SOURCE_ROLES,
                manual_build_roots=COMPILED_PDF_BUILD_ROOTS,
            )
        ]
        if len(manual_paths) != len(expected_manual_paths):
            artifact_violations.append(
                {
                    "actual": len(manual_paths),
                    "expected": len(expected_manual_paths),
                    "manual": manual_id,
                    "scope": "manual",
                }
            )
        duplicates = sorted(
            path
            for path, count in Counter(manual_paths).items()
            if isinstance(path, str) and count > 1
        )
        unknown = sorted(
            path
            for path in manual_paths
            if isinstance(path, str) and path not in pdf_paths
        )
        if (
            duplicates
            or unknown
            or any(not isinstance(path, str) for path in manual_paths)
        ):
            artifact_violations.append(
                {
                    "duplicate_paths": duplicates,
                    "manual": manual_id,
                    "unknown_paths": unknown,
                }
            )
    return {
        "artifact_cardinality": {
            "ok": not artifact_violations,
            "violations": artifact_violations,
        },
        "chapter_manual_sums": {
            "ok": not sum_violations,
            "violations": sum_violations,
        },
        "status_distribution": {
            "ok": not status_violations,
            "violations": status_violations,
        },
    }


def build_deliverable_matrix(inventory: Mapping[str, Any]) -> dict[str, Any]:
    """Derive release readiness for every manual and required deliverable."""
    manuals: dict[str, Any] = {}
    for manual_id, specification in sorted(DELIVERABLE_SPECS.items()):
        source = inventory["manuals"][manual_id]
        publication_coverage = dict(PUBLICATION_GATE_TEMPLATE)
        blockers = _manual_blockers(inventory, manual_id, specification)
        variants = {
            variant_id: _variant_state(source, aliases)
            for variant_id, aliases in sorted(specification["variants"].items())
        }
        for variant_id, variant in variants.items():
            if variant["state"] != "compiled":
                blockers.append(
                    {
                        "code": "livrable_non_compile",
                        "detail": variant["state"],
                        "source": f"deliverable_matrix.{manual_id}.variants.{variant_id}",
                    }
                )
        blockers.sort(key=lambda item: (item["code"], item["source"], item["detail"]))
        structural_blockers = {
            blocker["code"]
            for blocker in blockers
            if blocker["code"].startswith("anomalie:")
            and blocker["code"].removeprefix("anomalie:")
            in STRUCTURAL_ANOMALY_CATEGORIES
            or blocker["code"] == "statuts_non_approuves"
            or blocker["code"] == "chapitres_manquants"
            or blocker["code"] == "objectif_chapitres_non_fige"
        }
        structural_compile_ready = all(
            variant["state"] == "compiled" for variant in variants.values()
        )
        phase0_structural_eligible = not bool(structural_blockers)
        manuals[manual_id] = {
            "structural_blockers": sorted(structural_blockers),
            "structural_compile_ready": structural_compile_ready,
            "blockers": blockers,
            "current": {
                "artifacts": sorted(
                    artifact["path"] for artifact in source["compiled_artifacts"]
                ),
                "chapter_count": len(source["chapters"]),
                "chapters": sorted(source["chapters"]),
                "statuses": dict(sorted(source["statuses"].items())),
                "totals": dict(source["totals"]),
            },
            "objective": {
                "directive": specification["directive"],
                "target_chapters": specification["target_chapters"],
            },
            "publication_gate_coverage": publication_coverage,
            "phase0_structural_eligible": phase0_structural_eligible,
            "publication_eligible": bool(
                phase0_structural_eligible
                and all(
                    publication_coverage[dimension]
                    for dimension in publication_coverage
                )
                and structural_compile_ready
            ),
            "variants": variants,
        }
    return {"manuals": manuals}


def reconcile_reports(
    repository: Path | str,
    inventory: Mapping[str, Any],
    report_paths: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    if report_paths is None:
        report_paths = report_source_paths(repository, git_tracked_files(repository))
    return _report_core.reconcile_reports(
        repository,
        inventory,
        report_paths,
        resolve_claim=_calculate_claim,
    )


def _build_inventory(
    repository: Path | str,
    *,
    managed_output_paths: Iterable[str] = (),
    require_git_provenance: bool = False,
    qualification_today: datetime.date | None = None,
    empty_manifest_refresh_capability: object | None = None,
    owned_generation_lock: Mapping[str, tuple[int, int]] | None = None,
) -> dict[str, Any]:
    """Build a deterministic canonical model from tracked chapter sources."""

    root = Path(repository).resolve()
    if require_git_provenance:
        try:
            _repo_head_sha(root, required=True)
            _repo_branch(root, required=True)
            _git_status(root, required=True)
            _generation_timestamp(root, required=True)
        except InventoryError as exc:
            raise InventoryError(
                f"Git provenance unavailable: {exc}"
            ) from exc
    try:
        tracked = git_tracked_files(root)
    except (OSError, subprocess.CalledProcessError) as exc:
        if require_git_provenance:
            raise InventoryError(
                "Git provenance unavailable: git tracked files unavailable"
            ) from exc
        raise
    tracked_set = frozenset(tracked)
    role_patterns, default_role, role_order = _collect_role_patterns(root)
    source_roles = _load_source_roles(root, tracked)
    dispositions = _load_dispositions(root)

    def _is_production(path: str) -> bool:
        return _classify_is_production(
            path,
            source_roles,
            role_patterns=role_patterns,
            role_order=role_order,
            default=default_role,
        )

    content_sources = tuple(
        path
        for path in tracked
        if _is_relevant_source(path) and _is_production(path)
    )
    model_sources = tuple(
        path
        for path in tracked
        if _is_digest_model_source(path, source_roles[path]) or _is_production(path)
    )
    metadata_error_paths: set[str] = set()

    manuals = {
        manual_id: {
            "chapters": {},
            "content_file_count": 0,
            "editorial_object_count": 0,
            "compiled_artifacts": [],
            "compiled_variants": _empty_variant_scopes(),
            "declared_variants": _empty_variant_scopes(),
            "edition": definition["edition"],
            "level": definition["level"],
            "statuses": {},
            "subject": definition["subject"],
            "object_count": 0,
            "objects_by_status": {},
            "objects_by_type": {},
            "totals": _zero_counts(),
        }
        for manual_id, definition in sorted(MANUALS.items())
    }
    anomalies: dict[str, list[dict[str, Any]]] = {
        "blocking_statuses": [],
        "assembler_invalid": [],
        "broken_latex_references": [],
        "broken_meta_references": [],
        "broken_assembly_references": [],
        "chapters_not_in_manual": [],
        "context_mismatches": [],
        "contract_invalid": [],
        "contract_missing": [],
        "duplicate_assembly_objects": [],
        "duplicate_capacity_refs": [],
        "duplicate_ids": [],
        "invalid_capacities": [],
        "invalid_meta_references": [],
        "invalid_statuses": [],
        "metadata_invalid": [],
        "metadata_missing": [],
        "latex_cycles": [],
        "missing_assemblers": [],
        "missing_corrections": [],
        "orphan_files": [],
        "unknown_chapter_prefixes": [],
        "unassembled_objects": [],
        "unattributed_pdfs": [],
        "unavailable_inspiration_sources": [],
        "unclassified_types": [],
    }

    chapter_sources: dict[tuple[str, str], list[str]] = defaultdict(list)
    for path in content_sources:
        context = _chapter_context(path)
        if context is None:
            chapter_id = _chapter_id_from_source(path)
            anomalies["unknown_chapter_prefixes"].append(
                {
                    "chapter": chapter_id,
                    "path": path,
                    "reason": "prefixe de chapitre sans manuel canonique",
                }
            )
            continue
        chapter_sources[context].append(path)

    id_paths: dict[str, list[str]] = defaultdict(list)
    capacity_ref_occurrences: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for (manual_id, chapter_id), paths in sorted(chapter_sources.items()):
        chapter = _empty_chapter(chapter_id)
        contract_path = next(
            (path for path in paths if PurePosixPath(path).name == "contrat.yaml"),
            None,
        )
        if contract_path is None:
            anomalies["contract_missing"].append(
                {"chapter": chapter_id, "manual": manual_id}
            )
        else:
            chapter["contract_path"] = contract_path
            try:
                contract = load_contract(root / contract_path)
            except ContractError as exc:
                anomalies["contract_invalid"].append(
                    {"path": contract_path, "reason": str(exc)}
                )
            else:
                chapter["contract"] = contract
                _record_context_mismatch(
                    anomalies,
                    actual=contract.get("chapitre"),
                    expected=chapter_id,
                    field="chapitre",
                    path=contract_path,
                    scope="contract",
                )
                _record_context_mismatch(
                    anomalies,
                    actual=contract.get("niveau"),
                    expected=MANUAL_EXPECTED_LEVELS[manual_id],
                    field="niveau",
                    path=contract_path,
                    scope="contract",
                )
                capacities = contract.get("capacites")
                valid_capacities: list[dict[str, Any]] = []
                if not isinstance(capacities, list):
                    anomalies["invalid_capacities"].append(
                        {
                            "index": None,
                            "path": contract_path,
                            "reason": "capacites doit etre une liste",
                        }
                    )
                else:
                    for index, capacity in enumerate(capacities):
                        if not isinstance(capacity, Mapping):
                            anomalies["invalid_capacities"].append(
                                {
                                    "index": index,
                                    "path": contract_path,
                                    "reason": "capacite doit etre un objet",
                                }
                            )
                            continue
                        reference = capacity.get("ref_capacite")
                        if not isinstance(reference, str) or not reference.strip():
                            anomalies["invalid_capacities"].append(
                                {
                                    "index": index,
                                    "path": contract_path,
                                    "reason": "ref_capacite doit etre un texte non vide",
                                }
                            )
                            continue
                        valid_capacity = _canonicalize_mapping(capacity)
                        valid_capacities.append(valid_capacity)
                        capacity_ref_occurrences[reference].append(
                            {
                                "chapter": chapter_id,
                                "index": index,
                                "manual": manual_id,
                                "path": contract_path,
                            }
                        )
                chapter["capacities"] = valid_capacities
                chapter["counts"]["capacites"] = len(valid_capacities)
                contract_source_status = contract.get("statut")
                contract_status, status_valid, status_reason = _normalize_status(
                    contract_source_status, KNOWN_CONTRACT_STATUSES
                )
                chapter["contract_status"] = contract_status
                chapter["contract_status_valid"] = status_valid
                if not status_valid:
                    anomalies["invalid_statuses"].append(
                        {
                            "normalized_status": contract_status,
                            "path": contract_path,
                            "reason": status_reason,
                            "scope": "contract",
                            "source_status": contract_source_status,
                        }
                    )
                if (
                    not status_valid
                    or contract_status not in APPROVED_CONTRACT_STATUSES
                ):
                    anomalies["blocking_statuses"].append(
                        {
                            "chapter": chapter_id,
                            "id": None,
                            "manual": manual_id,
                            "path": contract_path,
                            "scope": "contract",
                            "status": contract_source_status,
                        }
                    )

        for path in sorted(paths):
            if not path.endswith(".tex"):
                continue
            try:
                metadata = read_meta(root / path)
            except MetadataMissingError as exc:
                anomalies["metadata_missing"].append({"path": path, "reason": str(exc)})
                metadata_error_paths.add(path)
                continue
            except MetadataError as exc:
                anomalies["metadata_invalid"].append({"path": path, "reason": str(exc)})
                metadata_error_paths.add(path)
                continue

            source_type = metadata["type_objet"]
            _record_context_mismatch(
                anomalies,
                actual=metadata.get("chapitre"),
                expected=chapter_id,
                field="chapitre",
                path=path,
                scope="object",
            )
            source_subtype = metadata.get("sous_type")
            category = canonical_category(source_type, source_subtype)
            source_status = metadata["status"]
            status, status_valid, status_reason = _normalize_status(
                source_status, KNOWN_OBJECT_STATUSES
            )
            object_id = metadata["id"]
            chapter["objects"].append(
                {
                    "canonical_category": category,
                    "id": object_id,
                    "metadata": metadata,
                    "path": path,
                    "path_chapter": chapter_id,
                    "publishable": status_valid and status in APPROVED_OBJECT_STATUSES,
                    "source_status": source_status,
                    "source_subtype": source_subtype,
                    "source_type": source_type,
                    "status": status,
                    "status_valid": status_valid,
                }
            )
            chapter["source_taxonomy"][source_type] += 1
            if isinstance(source_subtype, str) and source_subtype:
                chapter["source_subtypes"][source_subtype] += 1
            chapter["statuses"][status] += 1
            if category is not None:
                chapter["counts"][category] += 1
            elif not _is_known_uncounted(source_type, source_subtype):
                anomalies["unclassified_types"].append(
                    {
                        "id": object_id,
                        "path": path,
                        "source_subtype": source_subtype,
                        "source_type": source_type,
                    }
                )
            if not status_valid:
                anomalies["invalid_statuses"].append(
                    {
                        "normalized_status": status,
                        "path": path,
                        "reason": status_reason,
                        "scope": "object",
                        "source_status": source_status,
                    }
                )
            if not status_valid or status not in APPROVED_OBJECT_STATUSES:
                anomalies["blocking_statuses"].append(
                    {
                        "chapter": chapter_id,
                        "id": object_id,
                        "manual": manual_id,
                        "path": path,
                        "scope": "object",
                        "status": source_status,
                    }
                )
            id_paths[object_id].append(path)

        chapter["source_taxonomy"] = dict(sorted(chapter["source_taxonomy"].items()))
        chapter["source_subtypes"] = dict(sorted(chapter["source_subtypes"].items()))
        chapter["statuses"] = dict(sorted(chapter["statuses"].items()))
        chapter["objects"].sort(key=lambda item: item["path"])
        manuals[manual_id]["chapters"][chapter_id] = chapter

    for manual in manuals.values():
        manual["chapters"] = dict(sorted(manual["chapters"].items()))
        manual_statuses: Counter[str] = Counter()
        object_types: Counter[str] = Counter()
        for chapter in manual["chapters"].values():
            manual["object_count"] += len(chapter["objects"])
            manual["editorial_object_count"] += chapter["counts"]["capacites"]
            manual["content_file_count"] += len(chapter["objects"])
            for key in COUNT_KEYS:
                manual["totals"][key] += chapter["counts"][key]
            manual_statuses.update(chapter["statuses"])
            object_types.update(chapter["source_taxonomy"])
        manual["statuses"] = dict(sorted(manual_statuses.items()))
        manual["objects_by_status"] = {
            status: int(count) for status, count in sorted(manual_statuses.items())
        }
        manual["objects_by_type"] = {
            source: int(count) for source, count in sorted(object_types.items())
        }

    anomalies["duplicate_ids"] = [
        {"id": object_id, "paths": sorted(paths)}
        for object_id, paths in sorted(id_paths.items())
        if len(paths) > 1
    ]
    anomalies["duplicate_capacity_refs"] = [
        {
            "occurrences": sorted(
                occurrences,
                key=lambda occurrence: (
                    occurrence["path"],
                    occurrence["index"],
                ),
            ),
            "ref_capacite": reference,
        }
        for reference, occurrences in sorted(capacity_ref_occurrences.items())
        if len(occurrences) > 1
    ]
    inventory = {
        "anomalies": anomalies,
        "anomaly_qualifications": {},
        "assemblies": [],
        "declared_assemblies": [],
        "correction_links": [],
        "manuals": manuals,
        "pdfs": [],
        "reference_graph": [],
        "schema_version": SCHEMA_VERSION,
        "source_digest": None,
        "source_file_count": 0,
        "source_files": [],
    }
    _add_reference_graph(inventory, root, tracked_set)
    _add_latex_graph(inventory, root, tracked_set, source_roles=source_roles)
    _add_assemblies(
        inventory,
        root,
        tracked_set,
        source_roles=source_roles,
    )
    _aggregate_declared_variants(inventory)
    _add_orphan_files(
        inventory,
        root,
        tracked_set,
        source_roles=source_roles,
        candidate_paths=frozenset(
            path
            for path in tracked_set
            if source_roles[path] in ORPHAN_SOURCE_ROLES
        ),
        skipped_paths=metadata_error_paths,
    )
    inventory["pdfs"] = _inventory_pdfs(
        root,
        tuple(path for path in tracked if source_roles[path] != "validation_reference"),
        inventory,
        source_roles=source_roles,
    )
    _aggregate_pdf_artifacts(inventory)
    inventory["anomalies"] = {
        key: sorted(values, key=_anomaly_sort_key)
        for key, values in anomalies.items()
    }
    inventory["anomaly_qualifications"] = _build_anomaly_qualification_view(
        inventory["anomalies"],
        dispositions,
        today=(
            qualification_today
            if qualification_today is not None
            else _qualification_evaluation_date(
                root,
                require_git=require_git_provenance,
            )
        ),
    )
    inventory["coherence_checks"] = validate_inventory_coherence(inventory)
    inventory["deliverable_matrix"] = build_deliverable_matrix(inventory)
    inventory["generated_by"] = "inventory_collection.py"
    inventory["provenance"] = _build_provenance(
        root,
        source_roles=source_roles,
        role_patterns=role_patterns,
        role_order=role_order,
        managed_output_paths=managed_output_paths,
        require_git=require_git_provenance,
    )
    report_sources = report_source_paths(root, tracked)
    inventory["report_reconciliation"] = reconcile_reports(
        root, inventory, report_sources
    )
    graph_targets = {
        item["cible"]
        for item in inventory["reference_graph"]
        if item["resolved"]
        and item["kind"] in {"latex", "meta_path"}
        and item["cible"] in tracked_set
    }
    model_sources = tuple(
        sorted(
            (
                set(model_sources)
                | graph_targets
                | set(report_sources)
            )
            - {BUILD_MANIFEST_FILE}
        )
    )
    inventory["source_digest"] = _source_digest(root, model_sources)
    inventory["source_file_count"] = len(model_sources)
    inventory["source_files"] = list(model_sources)
    for values in anomalies.values():
        values.sort(key=_anomaly_sort_key)
    inventory["reference_graph"].sort(key=_reference_sort_key)
    inventory["anomalies"] = {
        key: sorted(values, key=_anomaly_sort_key) for key, values in anomalies.items()
    }
    inventory["correction_links"].sort(
        key=lambda item: (item["exercise_path"], item["correction_path"])
    )
    inventory["assemblies"].sort(key=lambda item: item["assembly_id"])
    inventory["declared_assemblies"] = inventory["assemblies"]
    static_model_digest = _model_digest(inventory)
    inventory["observed_builds"] = _load_observed_build_manifest(
        root,
        source_digest=inventory["source_digest"],
        model_digest=static_model_digest,
        declared_assemblies=inventory["declared_assemblies"],
        pdfinfo_counter=_page_count_with_pdfinfo,
        python_counter=_page_count_with_python,
        source_files=model_sources,
        empty_manifest_refresh_capability=empty_manifest_refresh_capability,
        owned_generation_lock=owned_generation_lock,
    )
    inventory["observed_build_coverage"] = _observed_build_coverage(
        inventory["declared_assemblies"],
        inventory["observed_builds"],
    )
    producer_path = root / BUILD_PRODUCERS_FILE
    producers = (
        _load_build_producers(root)
        if BUILD_PRODUCERS_FILE in tracked_set
        or producer_path.exists()
        or producer_path.is_symlink()
        else []
    )
    inventory["observed_build_integration"] = _observed_build_integration(
        inventory["declared_assemblies"],
        inventory["observed_builds"],
        producers,
    )
    return inventory


def build_inventory(
    repository: Path | str,
    *,
    managed_output_paths: Iterable[str] = (),
    require_git_provenance: bool = False,
    qualification_today: datetime.date | None = None,
) -> dict[str, Any]:
    """Build the strict deterministic canonical model."""

    return _build_inventory(
        repository,
        managed_output_paths=managed_output_paths,
        require_git_provenance=require_git_provenance,
        qualification_today=qualification_today,
    )


def _build_inventory_for_empty_manifest_refresh(
    repository: Path | str,
) -> dict[str, Any]:
    """Build digests while tolerating only a validated stale empty manifest."""

    return _build_inventory(
        repository,
        require_git_provenance=True,
        empty_manifest_refresh_capability=_EMPTY_MANIFEST_REFRESH_CAPABILITY,
    )


def _build_inventory_for_empty_manifest_branch_rebind(
    repository: Path | str,
) -> dict[str, Any]:
    """Build digests while rebinding only an empty ancestor manifest."""

    return _build_inventory(
        repository,
        require_git_provenance=True,
        empty_manifest_refresh_capability=(
            _EMPTY_MANIFEST_BRANCH_REBIND_CAPABILITY
        ),
    )


def _build_inventory_for_stale_manifest_invalidation(
    repository: Path | str,
) -> dict[str, Any]:
    """Build digests while discarding a validated but source-mismatched manifest.

    Unlike :func:`_build_inventory_for_empty_manifest_refresh`, this tolerates a
    *non-empty* ``builds`` list on disk, provided every other manifest
    invariant (schema, branch, clean tree, provenance ancestry) still holds.
    The discarded observed builds are treated as ``[]`` for this computation;
    callers are responsible for the higher-level preconditions (explicit
    human reason/approver, CI refusal) before invoking this.
    """

    return _build_inventory(
        repository,
        require_git_provenance=True,
        empty_manifest_refresh_capability=_STALE_MANIFEST_INVALIDATION_CAPABILITY,
    )


def analyze_assembler(path: Path | str) -> dict[str, Any]:
    try:
        return _assembly_core.analyze_assembler(path)
    except _assembly_core.AssemblyAnalysisError as exc:
        raise InventoryError(str(exc)) from exc


def _add_reference_graph(
    inventory: dict[str, Any],
    root: Path,
    tracked: frozenset[str],
) -> None:
    anomalies = inventory["anomalies"]
    objects = _all_objects(inventory)
    objects_by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    objects_by_path = {item["path"]: item for item in objects}
    for item in objects:
        objects_by_id[item["id"]].append(item)
    capacity_refs: dict[str, set[str]] = defaultdict(set)
    capacity_codes: dict[str, dict[str, str]] = defaultdict(dict)
    prerequisite_codes: dict[str, set[str]] = defaultdict(set)
    for manual in inventory["manuals"].values():
        for chapter_id, chapter in manual["chapters"].items():
            for capacity in chapter["capacities"]:
                reference = capacity.get("ref_capacite")
                code = capacity.get("code")
                if isinstance(reference, str):
                    capacity_refs[chapter_id].add(reference)
                    if isinstance(code, str):
                        capacity_codes[chapter_id][code] = reference
            contract = chapter.get("contract")
            prerequisites = (
                contract.get("prerequis", []) if isinstance(contract, Mapping) else []
            )
            if isinstance(prerequisites, list):
                prerequisite_codes[chapter_id].update(
                    prerequisite["code"]
                    for prerequisite in prerequisites
                    if isinstance(prerequisite, Mapping)
                    and isinstance(prerequisite.get("code"), str)
                )
    methods = [item for item in objects if item["source_type"] == "methode"]
    method_aliases = _graph_core.index_method_aliases(methods)
    for method in methods:
        aliases = _graph_core.method_aliases(method)
        if not aliases:
            anomalies["broken_meta_references"].append(
                _reference_anomaly(
                    method["path"],
                    method["id"],
                    "methodes",
                    "alias de methode absent et suffixe ID inexploitable",
                )
            )
    for chapter_aliases in method_aliases.values():
        for alias, candidates in chapter_aliases.items():
            if len(candidates) <= 1:
                continue
            for candidate in candidates:
                anomalies["broken_meta_references"].append(
                    _reference_anomaly(
                        candidate["path"],
                        alias,
                        "methodes",
                        "alias de methode ambigu ou duplique",
                    )
                )

    path_fields = ("fichier_tex", "corrige_tex")
    id_fields = ("evaluation_ref", "exercice_id", "exercice_ref")
    for item in objects:
        metadata = item["metadata"]
        for field in path_fields:
            value = metadata.get(field)
            if not isinstance(value, str) or not value.strip():
                continue
            target = _resolve_reference_target(item["path"], value, latex=False)
            resolved = target in tracked
            _append_reference(
                inventory,
                source=item["path"],
                target=target,
                field=field,
                kind="meta_path",
                resolved=resolved,
            )
            if not resolved:
                anomalies["broken_meta_references"].append(
                    _reference_anomaly(
                        item["path"],
                        target,
                        field,
                        "chemin META absent des sources suivies",
                    )
                )
        inspirations = metadata.get("sources_inspiration")
        if isinstance(inspirations, list):
            for index, value in enumerate(inspirations):
                if not _looks_like_local_path(value):
                    continue
                field = f"sources_inspiration[{index}]"
                target = _resolve_reference_target(item["path"], value, latex=False)
                resolved = target in tracked
                _append_reference(
                    inventory,
                    source=item["path"],
                    target=target,
                    field=field,
                    kind="meta_path",
                    resolved=resolved,
                )
                if not resolved:
                    anomalies["unavailable_inspiration_sources"].append(
                        _reference_anomaly(
                            item["path"],
                            target,
                            field,
                            "source d'inspiration absente des sources suivies",
                        )
                    )
        for field in id_fields:
            value = metadata.get(field)
            if not isinstance(value, str) or not value.strip():
                continue
            resolved = len(objects_by_id.get(value, [])) == 1
            _append_reference(
                inventory,
                source=item["path"],
                target=value,
                field=field,
                kind="meta_id",
                resolved=resolved,
            )
            if not resolved:
                reason = (
                    "identifiant META ambigu"
                    if len(objects_by_id.get(value, [])) > 1
                    else "identifiant META absent"
                )
                anomalies["broken_meta_references"].append(
                    _reference_anomaly(item["path"], value, field, reason)
                )
        chapter_id = item["path_chapter"]
        declared_capacities = metadata.get("capacites")
        if isinstance(declared_capacities, list):
            for index, value in enumerate(declared_capacities):
                if not isinstance(value, str) or not value:
                    continue
                field = f"capacites[{index}]"
                target = capacity_codes[chapter_id].get(value, value)
                resolved = target in capacity_refs[chapter_id]
                _append_reference(
                    inventory,
                    source=item["path"],
                    target=target,
                    field=field,
                    kind="capacity",
                    resolved=resolved,
                )
                if not resolved:
                    anomalies["broken_meta_references"].append(
                        _reference_anomaly(
                            item["path"],
                            target,
                            field,
                            "capacite META absente du contrat du chapitre",
                        )
                    )
        for family in ("capacites_codes", "methodes", "coups_de_pouce"):
            values = metadata.get(family)
            if values is None:
                continue
            if not isinstance(values, list):
                anomalies["invalid_meta_references"].append(
                    _invalid_reference_anomaly(
                        item["path"], family, values, "liste attendue"
                    )
                )
                continue
            for index, value in enumerate(values):
                field = f"{family}[{index}]"
                if not isinstance(value, str) or not value:
                    anomalies["invalid_meta_references"].append(
                        _invalid_reference_anomaly(
                            item["path"], field, value, "texte non vide attendu"
                        )
                    )
                    continue
                target = value
                kind = family
                resolved = False
                if family == "capacites_codes":
                    if value in capacity_codes[chapter_id]:
                        target = capacity_codes[chapter_id][value]
                        kind = "capacity"
                        resolved = True
                    elif value in capacity_refs[chapter_id]:
                        kind = "capacity"
                        resolved = True
                    elif value in prerequisite_codes[chapter_id]:
                        target = f"{chapter_id}:prerequis:{value}"
                        kind = "prerequisite"
                        resolved = True
                    else:
                        kind = "capacity_or_prerequisite"
                elif family == "methodes":
                    kind = "method"
                    if _graph_core.METHOD_ALIAS_RE.fullmatch(value):
                        candidates = method_aliases.get(chapter_id, {}).get(value, [])
                        if len(candidates) == 1:
                            target = candidates[0]["id"]
                            resolved = True
                    else:
                        candidates = [
                            candidate
                            for candidate in objects_by_id.get(value, [])
                            if candidate["path_chapter"] == chapter_id
                        ]
                        resolved = (
                            len(candidates) == 1
                            and candidates[0]["source_type"] == "methode"
                        )
                else:
                    if _looks_like_local_path(value):
                        target = _resolve_reference_target(
                            item["path"], value, latex=False
                        )
                        candidate = objects_by_path.get(target)
                        kind = "hint_path"
                        resolved = (
                            candidate is not None
                            and candidate["source_type"] == "coup_de_pouce"
                        )
                    else:
                        candidates = objects_by_id.get(value, [])
                        kind = "hint_id"
                        resolved = (
                            len(candidates) == 1
                            and candidates[0]["source_type"] == "coup_de_pouce"
                        )
                _append_reference(
                    inventory,
                    source=item["path"],
                    target=target,
                    field=field,
                    kind=kind,
                    resolved=resolved,
                )
                if not resolved:
                    reason = f"reference {family} absente ou ambigue"
                    if family == "methodes" and _graph_core.METHOD_ALIAS_RE.fullmatch(
                        value
                    ):
                        alias_candidates = method_aliases.get(chapter_id, {}).get(
                            value, []
                        )
                        if len(alias_candidates) > 1:
                            reason = "alias de methode ambigu ou duplique"
                    anomalies["broken_meta_references"].append(
                        _reference_anomaly(
                            item["path"],
                            target,
                            field,
                            reason,
                        )
                    )

    reverse_corrections: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for correction in objects:
        if correction["source_type"] not in {
            "corrige",
            "corrige_evaluation",
            "evaluation_corrige",
        }:
            continue
        for field in ("exercice_id", "exercice_ref"):
            reference = correction["metadata"].get(field)
            if isinstance(reference, str) and reference:
                reverse_corrections[reference].append(correction)

    for exercise in (item for item in objects if item["source_type"] == "exercice"):
        correction: dict[str, Any] | None = None
        mode: str | None = None
        explicit = exercise["metadata"].get("corrige_tex")
        explicit_target: str | None = None
        if isinstance(explicit, str) and explicit:
            explicit_target = _resolve_reference_target(
                exercise["path"], explicit, latex=False
            )
            candidate = objects_by_path.get(explicit_target)
            if candidate is not None and candidate["source_type"] in {
                "corrige",
                "corrige_evaluation",
                "evaluation_corrige",
            }:
                correction = candidate
                mode = "corrige_tex"
        if correction is None:
            candidates = reverse_corrections.get(exercise["id"], [])
            if len(candidates) == 1:
                correction = candidates[0]
                mode = "reverse_meta"
        if correction is None and "-EX-" in exercise["id"]:
            conventional_id = exercise["id"].replace("-EX-", "-CO-", 1)
            candidates = objects_by_id.get(conventional_id, [])
            if len(candidates) == 1 and candidates[0]["source_type"] == "corrige":
                correction = candidates[0]
                mode = "id_convention"
        if correction is None:
            anomalies["missing_corrections"].append(
                _reference_anomaly(
                    exercise["path"],
                    explicit_target or exercise["id"].replace("-EX-", "-CO-", 1),
                    "corrige_tex" if explicit_target else "correction",
                    "aucun corrige suivi ne resout cet exercice",
                )
            )
            continue
        inventory["correction_links"].append(
            {
                "correction_id": correction["id"],
                "correction_path": correction["path"],
                "exercise_id": exercise["id"],
                "exercise_path": exercise["path"],
                "mode": mode,
            }
        )


def _add_latex_graph(
    inventory: dict[str, Any],
    root: Path,
    tracked: frozenset[str],
    *,
    source_roles: Mapping[str, str],
) -> None:
    _graph_core.add_latex_graph(
        inventory,
        root,
        tracked,
        source_roles=source_roles,
        blocking_source_roles=BLOCKING_LATEX_REFERENCE_SOURCE_ROLES,
        is_relevant_tex=_is_relevant_tex,
        resolve_latex_target=_resolve_latex_target,
    )


def _add_static_latex_assemblies(
    inventory: dict[str, Any],
    root: Path,
    tracked: frozenset[str],
    *,
    source_roles: Mapping[str, str],
) -> None:
    _graph_core.add_static_latex_assemblies(
        inventory,
        root,
        tracked,
        source_roles=source_roles,
        root_source_roles=STATIC_ASSEMBLY_ROOT_SOURCE_ROLES,
        traversal_source_roles=STATIC_ASSEMBLY_TRAVERSAL_SOURCE_ROLES,
        is_relevant_tex=_is_relevant_tex,
        chapter_id_from_source=_chapter_id_from_source,
        manual_for_chapter=_manual_for_chapter,
    )


def _add_orphan_files(
    inventory: dict[str, Any],
    root: Path,
    tracked: frozenset[str],
    *,
    source_roles: Mapping[str, str],
    candidate_paths: frozenset[str],
    skipped_paths: set[str] | None = None,
) -> None:
    _graph_core.add_orphan_files(
        inventory,
        root,
        tracked,
        candidate_paths=candidate_paths,
        source_roles=source_roles,
        root_source_roles=ORPHAN_ROOT_SOURCE_ROLES,
        traversal_source_roles=ORPHAN_TRAVERSAL_SOURCE_ROLES,
        skipped_paths=skipped_paths or set(),
        is_relevant_tex=_is_relevant_tex,
        is_known_latex_root=_is_known_latex_root,
        chapter_context=_chapter_context,
    )


def _add_assemblies(
    inventory: dict[str, Any],
    root: Path,
    tracked: frozenset[str],
    *,
    source_roles: Mapping[str, str],
) -> None:
    _assembly_core.add_declared_assemblies(
        inventory,
        root,
        tracked,
        source_roles=source_roles,
        assembler_source_roles=DECLARED_ASSEMBLER_SOURCE_ROLES,
        assembler_path_allowlist=DECLARED_ASSEMBLER_PATH_ALLOWLIST,
        manual_ids=tuple(MANUALS),
        manual_for_chapter=_manual_for_chapter,
        supported_manuals=_supported_manuals_for_assembler,
        project_for_manual=_project_for_manual,
        assembly_project_name=_assembly_project_name,
        chapter_directory=_chapter_directory,
        resolve_latex_target=_resolve_latex_target,
    )
    _add_static_latex_assemblies(
        inventory,
        root,
        tracked,
        source_roles=source_roles,
    )
    _assembly_core.add_unassembled_objects(inventory)


def _inventory_pdfs(
    root: Path,
    tracked: tuple[str, ...],
    inventory: dict[str, Any],
    *,
    source_roles: Mapping[str, str],
) -> list[dict[str, Any]]:
    return _pdf_core.inventory_pdfs(
        root,
        tracked,
        inventory,
        source_roles=source_roles,
        pdfinfo_counter=_page_count_with_pdfinfo,
        python_counter=_page_count_with_python,
    )


def _attribute_pdf(path: str, inventory: Mapping[str, Any]) -> dict[str, Any]:
    return _pdf_core.attribute_pdf(path, inventory)


def _aggregate_declared_variants(inventory: dict[str, Any]) -> None:
    manual_variants: dict[tuple[str, str], set[str]] = defaultdict(set)
    chapter_variants: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for assembly in inventory["assemblies"]:
        manual_id = assembly["manual"]
        scope = assembly["scope"]
        variant = assembly["variant"]
        if (
            manual_id not in inventory["manuals"]
            or scope not in {"chapter", "manual", "static"}
            or not isinstance(variant, str)
            or not variant
        ):
            continue
        manual_variants[(manual_id, scope)].add(variant)
        for chapter_id in assembly["chapters"]:
            if chapter_id in inventory["manuals"][manual_id]["chapters"]:
                chapter_variants[(manual_id, chapter_id, scope)].add(variant)
    for manual_id, manual in inventory["manuals"].items():
        for scope in ("chapter", "manual", "static"):
            manual["declared_variants"][scope] = sorted(
                manual_variants[(manual_id, scope)]
            )
        for chapter_id, chapter in manual["chapters"].items():
            for scope in ("chapter", "manual", "static"):
                chapter["declared_variants"][scope] = sorted(
                    chapter_variants[(manual_id, chapter_id, scope)]
                )


def _aggregate_pdf_artifacts(inventory: dict[str, Any]) -> None:
    _pdf_core.aggregate_artifacts(
        inventory,
        compiled_source_roles=COMPILED_PDF_SOURCE_ROLES,
        manual_build_roots=COMPILED_PDF_BUILD_ROOTS,
    )


def _page_count_with_pdfinfo(path: Path) -> tuple[int | None, str | None]:
    return _pdf_core.page_count_with_pdfinfo(
        path,
        runner=subprocess.run,
        timeout_seconds=PDFINFO_TIMEOUT_SECONDS,
    )


def _page_count_with_python(path: Path) -> tuple[int | None, str | None]:
    errors: list[str] = []
    for module_name in ("pypdf", "PyPDF2"):
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            continue
        try:
            reader = module.PdfReader(str(path))
            return len(reader.pages), None
        except Exception as exc:  # the reader defines backend-specific errors
            errors.append(f"{module_name}: {type(exc).__name__}")
    if errors:
        return None, "lecteur PDF Python en echec: " + "; ".join(errors)
    return None, "lecteur PDF Python indisponible"


def _all_objects(inventory: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        (
            item
            for manual in inventory["manuals"].values()
            for chapter in manual["chapters"].values()
            for item in chapter["objects"]
        ),
        key=lambda item: item["path"],
    )


def _append_reference(
    inventory: dict[str, Any],
    *,
    source: str,
    target: str,
    field: str,
    kind: str,
    resolved: bool,
) -> None:
    inventory["reference_graph"].append(
        {
            "champ": field,
            "cible": target,
            "kind": kind,
            "resolved": resolved,
            "source": source,
        }
    )


def _reference_anomaly(
    source: str,
    target: str,
    field: str,
    reason: str,
) -> dict[str, str]:
    return {
        "champ": field,
        "cible": target,
        "raison": reason,
        "source": source,
    }


def _invalid_reference_anomaly(
    source: str,
    field: str,
    value: Any,
    reason: str,
) -> dict[str, str]:
    try:
        target = json.dumps(value, ensure_ascii=False, sort_keys=True)
    except (TypeError, ValueError):
        target = type(value).__name__
    return _reference_anomaly(source, target, field, reason)


def _resolve_reference_target(source: str, target: str, *, latex: bool) -> str:
    normalized_target = target.strip().replace("\\", "/")
    if latex and PurePosixPath(normalized_target).suffix == "":
        normalized_target += ".tex"
    if normalized_target.startswith(("Mathematiques/", "NSI/")):
        candidate = normalized_target
    else:
        project = _project_root_for_path(source)
        candidate = f"{project}/{normalized_target}"
    return posixpath.normpath(candidate)


def _resolve_latex_target(
    source: str,
    target: str,
    tracked: frozenset[str],
) -> str:
    project_target = _resolve_reference_target(source, target, latex=True)
    if project_target in tracked:
        return project_target
    normalized = target.strip().replace("\\", "/")
    if PurePosixPath(normalized).suffix == "":
        normalized += ".tex"
    local_target = posixpath.normpath(str(PurePosixPath(source).parent / normalized))
    return local_target if local_target in tracked else project_target


def _looks_like_local_path(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    lowered = value.lower()
    if lowered.startswith(("http://", "https://", "doi:")):
        return False
    return "/" in value or PurePosixPath(value).suffix.lower() in {
        ".json",
        ".md",
        ".pdf",
        ".tex",
        ".yaml",
        ".yml",
    }


def _latex_inputs(source: str) -> list[tuple[str, str]]:
    return _graph_core.latex_inputs(source)


def _strip_latex_comment(line: str) -> str:
    return _graph_core.strip_latex_comment(line)


def _project_root_for_path(path: str) -> str:
    return "NSI" if path.startswith("NSI/") else "Mathematiques/manuel-maths"


def _project_for_manual(manual: str) -> str:
    return "NSI" if manual in {"1NSI", "TNSI"} else "Mathematiques/manuel-maths"


def _supported_manuals_for_assembler(path: str) -> tuple[str, ...]:
    if path.startswith("Mathematiques/manuel-maths/"):
        return ("1SPE", "TSPE_2026_2027", "TCOMPL", "TEXPERTES")
    if path == "NSI/scripts/assemble_manuel.py":
        return ("1NSI",)
    return ("1NSI", "TNSI")


def _assembly_project_name(manual: str) -> str:
    return "nsi" if manual in {"1NSI", "TNSI"} else "math"


def _chapter_directory(manual: str, chapter: str) -> str:
    return f"{_project_for_manual(manual)}/chapitres/{chapter}"


def _anomaly_is_blocking(
    anomaly: Mapping[str, Any],
    *,
    category: str,
    manual_id: str,
    qualifications: Mapping[str, Mapping[str, Any]],
) -> bool:
    if _anomaly_manual(anomaly) != manual_id:
        return False
    qualification = qualifications.get(
        _anomaly_fingerprint(anomaly, category=category)
    )
    if qualification is None:
        return True
    return bool(qualification.get("blocking", True))


def _manual_blockers(
    inventory: Mapping[str, Any],
    manual_id: str,
    specification: Mapping[str, Any],
) -> list[dict[str, str]]:
    manual = inventory["manuals"][manual_id]
    qualifications = inventory.get("anomaly_qualifications", {})
    if not isinstance(qualifications, Mapping):
        raise InventoryError("vue de qualification absente ou invalide")
    blockers: list[dict[str, str]] = []
    target = specification["target_chapters"]
    chapter_count = len(manual["chapters"])
    if target is None:
        blockers.append(
            {
                "code": "objectif_chapitres_non_fige",
                "detail": "cible a figer en Phase 1",
                "source": specification["directive"],
            }
        )
    elif chapter_count < target:
        blockers.append(
            {
                "code": "chapitres_manquants",
                "detail": f"{chapter_count}/{target}",
                "source": f"manuals.{manual_id}.chapters",
            }
        )
    non_approved = sum(
        count for status, count in manual["statuses"].items() if status != "approved"
    )
    non_approved_contracts = sum(
        chapter.get("contract_status") != "approved"
        or not chapter.get("contract_status_valid", False)
        for chapter in manual["chapters"].values()
    )
    if non_approved or non_approved_contracts:
        blockers.append(
            {
                "code": "statuts_non_approuves",
                "detail": f"objets={non_approved}; contrats={non_approved_contracts}",
                "source": f"manuals.{manual_id}.statuses",
            }
        )
    for category in sorted(BLOCKING_ANOMALY_CATEGORIES):
        affected = [
            anomaly
            for anomaly in inventory["anomalies"].get(category, [])
            if _anomaly_is_blocking(
                anomaly,
                category=category,
                manual_id=manual_id,
                qualifications=qualifications,
            )
        ]
        if affected:
            blockers.append(
                {
                    "code": f"anomalie:{category}",
                    "detail": str(len(affected)),
                    "source": f"anomalies.{category}",
                }
            )
    return blockers


def _anomaly_manual(anomaly: Mapping[str, Any]) -> str | None:
    manual = anomaly.get("manual")
    if isinstance(manual, str) and manual in MANUALS:
        return manual
    chapter = anomaly.get("chapter")
    if not isinstance(chapter, str):
        chapter = anomaly.get("cible") if anomaly.get("champ") == "chapitre" else None
    if isinstance(chapter, str):
        resolved = _manual_for_chapter(chapter)
        if resolved is not None:
            return resolved
    for key in ("path", "source", "cible"):
        value = anomaly.get(key)
        if not isinstance(value, str):
            continue
        context = _chapter_context(value)
        if context is not None:
            return context[0]
    return None


def _variant_state(
    manual: Mapping[str, Any], aliases: tuple[str, ...]
) -> dict[str, Any]:
    normalized_aliases = {_normalize_text(alias).replace(" ", "_") for alias in aliases}

    def matches(value: Any) -> bool:
        return (
            isinstance(value, str)
            and _normalize_text(value).replace(" ", "_") in normalized_aliases
        )

    artifacts = sorted(
        artifact["path"]
        for artifact in manual["compiled_artifacts"]
        if matches(artifact.get("variant")) and artifact.get("scope") == "manual"
    )
    if artifacts:
        state = "compiled"
    elif any(matches(value) for value in manual["declared_variants"]["manual"]):
        state = "declared"
    elif any(matches(value) for value in manual["declared_variants"]["chapter"]):
        state = "partial"
    else:
        state = "absent"
    return {
        "artifacts": artifacts,
        "declared_chapter_variants": sorted(
            value for value in manual["declared_variants"]["chapter"] if matches(value)
        ),
        "declared_manual_variants": sorted(
            value for value in manual["declared_variants"]["manual"] if matches(value)
        ),
        "state": state,
    }


def _calculate_claim(
    inventory: Mapping[str, Any], scope: str, metric: str
) -> tuple[int | bool | None, str | None, str | None]:
    if scope.startswith("chapter:"):
        chapter_id = scope.removeprefix("chapter:")
        manual_id = _manual_for_chapter(chapter_id)
        chapter = (
            inventory["manuals"].get(manual_id, {}).get("chapters", {}).get(chapter_id)
            if manual_id
            else None
        )
        if chapter is None:
            return None, None, "chapitre non resolu dans l'inventaire"
        base = f"manuals.{manual_id}.chapters.{chapter_id}"
        if metric in COUNT_KEYS:
            return chapter["counts"][metric], f"{base}.counts.{metric}", None
        if metric == "chapitres":
            return None, None, "un nombre de chapitres exige une portee manuel"
        if metric == "completude":
            value = _chapter_publication_eligible(inventory, manual_id, chapter_id)
            return value, f"{base}.publication_eligible", None
        if metric == "pages_compilees":
            pages = [
                artifact["page_count"]
                for artifact in chapter["compiled_artifacts"]
                if artifact.get("page_count") is not None
            ]
            if len(pages) == 1:
                return pages[0], f"{base}.compiled_artifacts[0].page_count", None
            return None, None, "aucun artefact chapitre unique suivi et attribue"
    if scope.startswith("manual:"):
        manual_id = scope.removeprefix("manual:")
        manual = inventory["manuals"].get(manual_id)
        if manual is None:
            return None, None, "manuel non resolu dans l'inventaire"
        base = f"manuals.{manual_id}"
        if metric in COUNT_KEYS:
            return manual["totals"][metric], f"{base}.totals.{metric}", None
        if metric == "chapitres":
            return len(manual["chapters"]), f"{base}.chapters", None
        if metric == "completude":
            matrix = inventory.get("deliverable_matrix", {}).get("manuals", {})
            value = matrix.get(manual_id, {}).get("publication_eligible")
            return (
                value,
                f"deliverable_matrix.manuals.{manual_id}.publication_eligible",
                None,
            )
        if metric == "pages_compilees":
            pages = [
                artifact["page_count"]
                for artifact in manual["compiled_artifacts"]
                if artifact.get("scope") == "manual"
                and artifact.get("page_count") is not None
            ]
            if len(pages) == 1:
                return pages[0], f"{base}.compiled_artifacts[0].page_count", None
            return None, None, "aucun artefact manuel unique suivi et attribue"
    if scope.startswith("variant:"):
        _, manual_id, variant = scope.split(":", 2)
        manual = inventory["manuals"].get(manual_id)
        if manual is not None and metric == "pages_compilees":
            artifacts = [
                artifact
                for artifact in manual["compiled_artifacts"]
                if _normalize_text(str(artifact.get("variant", ""))).replace(" ", "_")
                == variant
                and artifact.get("page_count") is not None
            ]
            if len(artifacts) == 1:
                return (
                    artifacts[0]["page_count"],
                    f"pdfs.{artifacts[0]['path']}.page_count",
                    None,
                )
            return None, None, "aucun artefact variante unique suivi et attribue"
    if metric in {
        "pages_compilees",
        "qcm_items_declares",
        "exercices_increment_declares",
        "exercices_remediation_declares",
        "remediations_items_declares",
        "seuil_exercices_declares",
        "tests_passes",
        "verify_assertions",
    }:
        return None, None, "unite ou preuve machine non disponible dans le modele"
    return None, None, "portee non resolue"


def _chapter_publication_eligible(
    inventory: Mapping[str, Any], manual_id: str, chapter_id: str
) -> bool:
    chapter = inventory["manuals"][manual_id]["chapters"][chapter_id]
    qualifications = inventory.get("anomaly_qualifications", {})
    if not isinstance(qualifications, Mapping):
        raise InventoryError("vue de qualification absente ou invalide")
    if (
        chapter.get("contract_status") != "approved"
        or not chapter.get("contract_status_valid", False)
        or not chapter["objects"]
        or any(not item["publishable"] for item in chapter["objects"])
    ):
        return False
    return not any(
        _anomaly_is_blocking(
            anomaly,
            category=category,
            manual_id=manual_id,
            qualifications=qualifications,
        )
        and (
            anomaly.get("chapter") == chapter_id
            or _chapter_context(str(anomaly.get("path", ""))) == (manual_id, chapter_id)
            or _chapter_context(str(anomaly.get("source", "")))
            == (manual_id, chapter_id)
        )
        for category in BLOCKING_ANOMALY_CATEGORIES
        for anomaly in inventory["anomalies"].get(category, [])
    )


def _normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_letters = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    return " ".join(re.findall(r"[a-z0-9]+", ascii_letters.lower()))


def _canonicalize_mapping(value: Mapping[Any, Any]) -> dict[str, Any]:
    return {
        str(key): _canonicalize(item)
        for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
    }


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _canonicalize_mapping(value)
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return str(value)


def _is_relevant_source(path: str) -> bool:
    pure = PurePosixPath(path)
    if not any(_is_relative_to(pure, root) for root in CHAPTER_ROOTS):
        return False
    return pure.name == "contrat.yaml" or pure.suffix == ".tex"


def _is_model_source(path: str) -> bool:
    return (
        path
        in {
            SOURCE_ROLES_FILE,
            ANOMALY_DISPOSITIONS_FILE,
            BUILD_PRODUCERS_FILE,
        }
        or
        _is_relevant_source(path)
        or _is_relevant_tex(path)
        or path.endswith("/scripts/assemble.py")
        or path.endswith("/scripts/assemble_manuel.py")
        or path.lower().endswith(".pdf")
    )


def _is_digest_model_source(path: str, source_role: str) -> bool:
    if path.lower().endswith(".pdf"):
        return source_role != "validation_reference"
    return _is_model_source(path)


def _is_relevant_tex(path: str) -> bool:
    pure = PurePosixPath(path)
    if pure.suffix.lower() not in {".cls", ".tex"}:
        return False
    roots = (PurePosixPath("Mathematiques/manuel-maths"), PurePosixPath("NSI"))
    if not any(_is_relative_to(pure, root) for root in roots):
        return False
    return "backlog_tspe_v2" not in pure.parts


def _is_known_latex_root(root: Path, path: str) -> bool:
    pure = PurePosixPath(path)
    if pure.name in {"chapitre_master.tex", "objet_standalone.tex"}:
        return True
    try:
        source = (root / path).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False
    return bool(
        re.search(r"\\documentclass(?:\[[^]]*\])?\s*\{", source)
        or "%%CONTENT%%" in source
        or "%%OBJ%%" in source
    )


def _is_relative_to(path: PurePosixPath, parent: PurePosixPath) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _chapter_context(path: str) -> tuple[str, str] | None:
    pure = PurePosixPath(path)
    for root in CHAPTER_ROOTS:
        try:
            relative = pure.relative_to(root)
        except ValueError:
            continue
        if len(relative.parts) < 2:
            return None
        chapter_id = relative.parts[0]
        manual_id = _manual_for_chapter(chapter_id)
        if manual_id is None:
            return None
        return manual_id, chapter_id
    return None


def _chapter_id_from_source(path: str) -> str | None:
    pure = PurePosixPath(path)
    for root in CHAPTER_ROOTS:
        try:
            relative = pure.relative_to(root)
        except ValueError:
            continue
        return relative.parts[0] if len(relative.parts) >= 2 else None
    return None


def _manual_for_chapter(chapter_id: str) -> str | None:
    if chapter_id.startswith("1SPE-"):
        return "1SPE"
    if chapter_id.startswith("TSPE-"):
        return "TSPE_2026_2027"
    if chapter_id.startswith("TCOMPL-"):
        return "TCOMPL"
    if chapter_id.startswith("TEXP-"):
        return "TEXPERTES"
    if chapter_id.startswith("1NSI-"):
        return "1NSI"
    if chapter_id.startswith("TNSI-"):
        return "TNSI"
    return None


def _zero_counts() -> dict[str, int]:
    return {key: 0 for key in COUNT_KEYS}


def _empty_variant_scopes() -> dict[str, list[str]]:
    return {scope: [] for scope in ("chapter", "manual", "static")}


def _empty_chapter(chapter_id: str) -> dict[str, Any]:
    return {
        "capacities": [],
        "chapter_id": chapter_id,
        "compiled_artifacts": [],
        "compiled_variants": _empty_variant_scopes(),
        "contract": None,
        "contract_path": None,
        "contract_status": None,
        "contract_status_valid": False,
        "counts": _zero_counts(),
        "objects": [],
        "source_subtypes": Counter(),
        "source_taxonomy": Counter(),
        "statuses": Counter(),
        "declared_variants": _empty_variant_scopes(),
    }


def _normalize_status(
    source_status: Any, known_statuses: frozenset[str]
) -> tuple[str, bool, str | None]:
    if not isinstance(source_status, str):
        return "", False, "statut absent ou non textuel"
    normalized = source_status.strip().lower()
    if source_status != normalized:
        return normalized, False, "statut non canonique"
    if normalized not in known_statuses:
        return normalized, False, "statut inconnu"
    return normalized, True, None


def _is_known_uncounted(source_type: str, source_subtype: Any) -> bool:
    return source_type in KNOWN_UNCOUNTED_TYPES or (
        isinstance(source_subtype, str) and source_subtype in KNOWN_UNCOUNTED_SUBTYPES
    )


def _record_context_mismatch(
    anomalies: dict[str, list[dict[str, Any]]],
    *,
    actual: Any,
    expected: str,
    field: str,
    path: str,
    scope: str,
) -> None:
    if actual == expected:
        return
    anomalies["context_mismatches"].append(
        {
            "actual": actual,
            "expected": expected,
            "field": field,
            "path": path,
            "scope": scope,
        }
    )


def _source_digest(root: Path, paths: tuple[str, ...]) -> str:
    return _graph_core.source_digest(root, paths)


def _anomaly_sort_key(item: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        str(item.get(key, ""))
        for key in (
            "path",
            "source",
            "cible",
            "champ",
            "manual",
            "chapter",
            "id",
            "raison",
        )
    )


def _anomaly_disposition(
    anomaly: Mapping[str, Any],
    defaults: dict[str, dict[str, Any]],
    *,
    category: str | None = None,
) -> dict[str, Any]:
    fingerprint = _anomaly_fingerprint(anomaly, category=category)
    disposition = defaults.get(fingerprint, {}).copy()
    disposition_value = str(disposition.get("disposition", "open_debt"))
    if disposition_value not in ANOMALY_DISPOSITIONS:
        disposition_value = "open_debt"
    resolved = dict(disposition)
    resolved.setdefault("disposition", disposition_value)
    resolved.setdefault("blocking", ANOMALY_DISPOSITION_BLOCKS[disposition_value])
    resolved.setdefault("author", "")
    resolved.setdefault("date", "")
    resolved.setdefault("proof", None)
    resolved.setdefault("expires_at", None)
    resolved["fingerprint"] = fingerprint
    return resolved


def _parse_disposition_expiry(value: Any) -> datetime.date:
    if not isinstance(value, str):
        raise InventoryError("expiration de disposition non textuelle")
    try:
        return datetime.date.fromisoformat(value)
    except ValueError as exc:
        raise InventoryError(
            f"expiration de disposition invalide: {value}"
        ) from exc


def _accepted_exception_is_expired(
    record: Mapping[str, Any],
    *,
    today: datetime.date,
) -> bool:
    expiry = record.get("expires_at", record.get("expiry"))
    if expiry is None:
        return False
    return _parse_disposition_expiry(expiry) < today


def _qualification_evaluation_date(
    root: Path,
    *,
    require_git: bool,
) -> datetime.date:
    timestamp = _generation_timestamp(root, required=require_git)
    if timestamp is None:
        return datetime.date.min
    try:
        return datetime.datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        ).date()
    except ValueError as exc:
        raise InventoryError(
            f"date de qualification invalide: {timestamp}"
        ) from exc


def _fingerprint_source(
    value: Any,
    *,
    repository_root: Path | None,
) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    normalized = posixpath.normpath(value.strip().replace("\\", "/"))
    if repository_root is not None:
        root_text = posixpath.normpath(repository_root.as_posix())
        prefix = f"{root_text.rstrip('/')}/"
        if normalized.startswith(prefix):
            return normalized[len(prefix) :]
    if normalized.startswith("/"):
        for anchor in (
            "Mathematiques/",
            "NSI/",
            "audit/",
            "docs/",
            "scripts/",
            "tests/",
        ):
            marker = f"/{anchor}"
            if marker in normalized:
                return normalized.split(marker, 1)[1].join((anchor, ""))
    return normalized


def _normalize_fallback_reason(
    value: Any,
    *,
    repository_root: Path | None,
) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    if repository_root is not None:
        normalized = normalized.replace(
            repository_root.as_posix().casefold(),
            "<repository>",
        )
    normalized = re.sub(
        r"\b\d{4}-\d{2}-\d{2}t\d{2}:\d{2}:\d{2}(?:\.\d+)?z\b",
        "<timestamp>",
        normalized,
    )
    normalized = re.sub(
        r"\b(?:line|ligne|column|colonne|char|caractère)\s*[:#]?\s*\d+\b",
        lambda match: re.sub(r"\d+", "<position>", match.group(0)),
        normalized,
    )
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


_LEGACY_REASONLESS_IDENTITIES = frozenset(
    {
        (
            "broken_latex_references",
            "cible latex absente des sources suivies",
        ),
        (
            "duplicate_assembly_objects",
            "objet inclus 2 fois dans le meme assemblage latex",
        ),
    }
)


def _fallback_reason_code(
    item: Mapping[str, Any],
    *,
    category: str,
    repository_root: Path | None,
) -> Any:
    explicit = item.get(
        "reason_code",
        item.get("raison_code", item.get("code", "")),
    )
    if explicit not in (None, ""):
        return explicit

    reason = next(
        (
            item[key]
            for key in ("reason", "raison", "detail")
            if key in item and item[key] not in (None, "")
        ),
        "",
    )
    normalized_reason = _normalize_fallback_reason(
        reason,
        repository_root=repository_root,
    )
    if (category, normalized_reason) in _LEGACY_REASONLESS_IDENTITIES:
        normalized_reason = ""
    stable_reason = ""
    reason_families = (
        ("en-tete % meta absent", "meta_header_absent"),
        ("json meta invalide", "meta_json_invalid"),
        ("json meta doit etre un objet", "meta_json_not_object"),
        ("champs meta absents ou invalides", "meta_fields_missing_or_invalid"),
        ("champ meta sous_type invalide", "meta_subtype_invalid"),
        ("lecture meta impossible", "meta_read_failed"),
    )
    for marker, code in reason_families:
        if marker in normalized_reason:
            stable_reason = code
            break
    if not stable_reason and normalized_reason:
        stable_reason = f"fallback:{normalized_reason}"

    semantic: dict[str, Any] = {}
    if stable_reason:
        semantic["reason"] = stable_reason
    for key in ("scope", "status"):
        if item.get(key) not in (None, ""):
            semantic[key] = item[key]
    return semantic if semantic else ""


def _anomaly_identity_fields(
    item: Mapping[str, Any],
    *,
    category: str | None = None,
    repository_root: Path | None = None,
) -> dict[str, Any]:
    target = next(
        (
            item[key]
            for key in ("target", "cible", "id", "object_id")
            if key in item and item[key] not in (None, "")
        ),
        "",
    )
    return {
        "category": category if category is not None else item.get("category", ""),
        "chapter": item.get("chapter", item.get("chapitre", "")),
        "field": item.get("field", item.get("champ", "")),
        "manual": item.get("manual", item.get("manuel", "")),
        "reason_code": _fallback_reason_code(
            item,
            category=str(
                category
                if category is not None
                else item.get("category", "")
            ),
            repository_root=repository_root,
        ),
        "source": _fingerprint_source(
            item.get("source", item.get("path", "")),
            repository_root=repository_root,
        ),
        "target_or_id": target,
    }


def _canonicalize_fingerprint_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _canonicalize_fingerprint_value(item)
            for key, item in sorted(
                value.items(),
                key=lambda pair: str(pair[0]),
            )
        }
    if isinstance(value, (list, tuple, set, frozenset)):
        normalized = [
            _canonicalize_fingerprint_value(item)
            for item in value
        ]
        return sorted(
            normalized,
            key=lambda item: json.dumps(
                item,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
    return value


def _anomaly_fingerprint(
    item: Mapping[str, Any],
    *,
    category: str | None = None,
    repository_root: Path | None = None,
) -> str:
    payload = json.dumps(
        _canonicalize_fingerprint_value(
            _anomaly_identity_fields(
                item,
                category=category,
                repository_root=repository_root,
            )
        ),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _anomaly_locator_key(
    item: Mapping[str, Any],
    *,
    category: str,
    repository_root: Path | None = None,
) -> str:
    identity = _anomaly_identity_fields(
        item,
        category=category,
        repository_root=repository_root,
    )
    identity.pop("reason_code", None)
    return json.dumps(
        _canonicalize(identity),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _anomaly_severity(
    anomaly: Mapping[str, Any],
    qualification: Mapping[str, Any],
) -> str:
    if qualification.get("regression") is True:
        return "regression"
    severity = str(anomaly.get("severity", "")).lower()
    if severity in _ANOMALY_SEVERITY_RANK:
        return severity
    return "blocking" if qualification.get("blocking", True) else "warning"


def _current_active_debt(
    inventory: Mapping[str, Any],
) -> list[dict[str, Any]]:
    anomalies = inventory.get("anomalies")
    qualifications = inventory.get("anomaly_qualifications")
    if not isinstance(anomalies, Mapping) or not isinstance(
        qualifications, Mapping
    ):
        raise InventoryError("modèle d'anomalies/qualifications invalide")
    representative: dict[str, tuple[str, Mapping[str, Any]]] = {}
    for category, values in sorted(anomalies.items()):
        if not isinstance(values, list):
            raise InventoryError(f"catégorie d'anomalie invalide: {category}")
        for anomaly in values:
            if not isinstance(anomaly, Mapping):
                raise InventoryError(f"anomalie brute invalide: {category}")
            fingerprint = _anomaly_fingerprint(
                anomaly,
                category=str(category),
            )
            representative.setdefault(
                fingerprint,
                (str(category), anomaly),
            )

    active: list[dict[str, Any]] = []
    for fingerprint, qualification in sorted(qualifications.items()):
        if not isinstance(qualification, Mapping):
            raise InventoryError(
                f"qualification invalide: {fingerprint}"
            )
        if (
            qualification.get("disposition") == "fixed"
            and qualification.get("regression") is not True
        ):
            continue
        case = representative.get(str(fingerprint))
        if case is None:
            raise InventoryError(
                f"qualification sans anomalie brute: {fingerprint}"
            )
        category, anomaly = case
        entry = {
            "blocking": bool(qualification.get("blocking", True)),
            "category": category,
            "disposition": str(
                qualification.get("disposition", "open_debt")
            ),
            "fingerprint": str(fingerprint),
            "justification": str(qualification.get("justification", "")),
            "locator_key": _anomaly_locator_key(
                anomaly,
                category=category,
            ),
            "occurrence_count": int(
                qualification.get("occurrence_count", 1)
            ),
            "owner": str(qualification.get("owner", "")),
            "qualification_digest": str(
                qualification.get("qualification_digest", "")
            ),
            "qualified": qualification.get("qualified") is True,
            "severity": _anomaly_severity(anomaly, qualification),
        }
        active.append(entry)
    return sorted(
        active,
        key=lambda entry: (
            entry["fingerprint"],
            entry["locator_key"],
        ),
    )


def _baseline_qualification_records(
    inventory: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Project the raw anomaly model into the pure policy input contract."""

    anomalies = inventory.get("anomalies")
    qualifications = inventory.get("anomaly_qualifications")
    manuals = inventory.get("manuals")
    if (
        not isinstance(anomalies, Mapping)
        or not isinstance(qualifications, Mapping)
        or not isinstance(manuals, Mapping)
    ):
        raise InventoryError("modèle incomplet pour la qualification baseline")

    object_types: dict[str, str] = {}
    for manual in manuals.values():
        if not isinstance(manual, Mapping):
            continue
        chapters = manual.get("chapters", {})
        if not isinstance(chapters, Mapping):
            continue
        for chapter in chapters.values():
            if not isinstance(chapter, Mapping):
                continue
            objects = chapter.get("objects", [])
            if not isinstance(objects, list):
                continue
            for value in objects:
                if (
                    isinstance(value, Mapping)
                    and isinstance(value.get("path"), str)
                    and isinstance(value.get("source_type"), str)
                ):
                    object_types[str(value["path"])] = str(value["source_type"])

    representatives: dict[str, tuple[str, Mapping[str, Any]]] = {}
    for category, values in sorted(anomalies.items()):
        if not isinstance(values, list):
            continue
        for anomaly in values:
            if not isinstance(anomaly, Mapping):
                continue
            fingerprint = _anomaly_fingerprint(
                anomaly,
                category=str(category),
            )
            representatives.setdefault(
                fingerprint,
                (str(category), anomaly),
            )

    records: list[dict[str, Any]] = []
    for fingerprint, qualification in sorted(qualifications.items()):
        if not isinstance(qualification, Mapping):
            raise InventoryError(f"qualification invalide: {fingerprint}")
        representative = representatives.get(str(fingerprint))
        if representative is None:
            raise InventoryError(
                f"qualification sans anomalie brute: {fingerprint}"
            )
        category, raw_anomaly = representative
        anomaly = dict(raw_anomaly)
        object_path = anomaly.get("path", anomaly.get("source"))
        if (
            anomaly.get("scope") == "object"
            and isinstance(object_path, str)
            and object_path in object_types
        ):
            anomaly["object_type"] = object_types[object_path]
        source = anomaly.get("source", anomaly.get("path"))
        records.append(
            {
                "anomaly": _canonicalize(anomaly),
                "category": category,
                "chapter": anomaly.get("chapter")
                or (
                    _chapter_context(str(source))[1]
                    if isinstance(source, str)
                    and _chapter_context(str(source)) is not None
                    else None
                ),
                "fingerprint": str(fingerprint),
                "fingerprint_schema_version": FINGERPRINT_SCHEMA_VERSION,
                "manual": anomaly.get("manual")
                or (
                    _chapter_context(str(source))[0]
                    if isinstance(source, str)
                    and _chapter_context(str(source)) is not None
                    else None
                ),
                "qualified": qualification.get("qualified") is True,
                "severity": _anomaly_severity(anomaly, qualification),
                "source": source if isinstance(source, str) else None,
            }
        )
    return records


def _raw_anomaly_identity(category: str, anomaly: Mapping[str, Any]) -> str:
    payload = json.dumps(
        {
            "anomaly": _canonicalize(anomaly),
            "category": category,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(_utf8_bytes(payload)).hexdigest()


def _build_anomaly_qualification_view(
    anomalies: Mapping[str, list[dict[str, Any]]],
    dispositions: Mapping[str, dict[str, Any]],
    *,
    today: datetime.date | None = None,
) -> dict[str, dict[str, Any]]:
    evaluation_date = today or datetime.datetime.now(datetime.UTC).date()
    grouped: dict[str, list[tuple[str, Mapping[str, Any], str]]] = defaultdict(list)
    for category, values in sorted(anomalies.items()):
        for anomaly in values:
            fingerprint = _anomaly_fingerprint(
                anomaly,
                category=category,
            )
            grouped[fingerprint].append(
                (
                    category,
                    anomaly,
                    _raw_anomaly_identity(category, anomaly),
                )
            )

    qualifications: dict[str, dict[str, Any]] = {}
    for fingerprint, occurrences in sorted(grouped.items()):
        categories = sorted({category for category, _, _ in occurrences})
        raw_identities = sorted({identity for _, _, identity in occurrences})
        configured = dispositions.get(fingerprint)
        if configured is not None and len(raw_identities) > 1:
            raise InventoryError(
                "disposition ambiguë: fingerprint configuré partagé par "
                f"{len(raw_identities)} anomalies brutes distinctes: {fingerprint}"
            )
        common = {
            "categories": categories,
            "category": categories[0] if len(categories) == 1 else None,
            "fingerprint": fingerprint,
            "occurrence_count": len(occurrences),
            "raw_identities": raw_identities,
        }
        if configured is None:
            record = {
                **common,
                "blocking": True,
                "disposition": "open_debt",
                "qualified": False,
            }
        else:
            disposition = str(configured["disposition"])
            expired = (
                _accepted_exception_is_expired(
                    configured,
                    today=evaluation_date,
                )
                if disposition == "accepted_exception"
                else False
            )
            regression = disposition == "fixed"
            blocking = (
                bool(configured.get("blocking", False))
                if disposition == "accepted_exception"
                else ANOMALY_DISPOSITION_BLOCKS[disposition]
            )
            record = {
                **_canonicalize(configured),
                **common,
                "blocking": blocking or expired or regression,
                "expired": expired,
                "qualified": True,
                "regression": regression,
            }
        qualifications[fingerprint] = record
    return dict(sorted(qualifications.items()))


def _reference_sort_key(item: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(str(item.get(key, "")) for key in ("source", "champ", "cible", "kind"))


def _artifact_envelope(
    inventory: Mapping[str, Any], artifact_type: str, model_digest: str
) -> dict[str, Any]:
    return {
        "artifact_type": artifact_type,
        "generated_by": "inventory_collection.py",
        "model_digest": model_digest,
        "provenance": inventory.get("provenance", {}),
        "schema_ref": _schema_ref_for(artifact_type, SCHEMA_VERSION),
        "schema_version": SCHEMA_VERSION,
        "source_digest": inventory["source_digest"],
    }


def _machine_artifact_payloads(
    inventory: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    model_digest = _model_digest(inventory)
    claims = inventory["report_reconciliation"]["claims"]
    json_payload = {
        **_canonicalize(inventory),
        **_artifact_envelope(inventory, "inventory_collection", model_digest),
    }
    ecarts_payload = {
        **_artifact_envelope(
            inventory, "ecarts_et_contradictions", model_digest
        ),
        "claims": {
            "contredits": [claim for claim in claims if claim["etat"] == "contredit"],
            "ouvertes": [claim for claim in claims if claim["etat"] == "ouvert"],
            "confirmes": [claim for claim in claims if claim["etat"] == "confirme"],
        },
        "counts": {
            "claims_ouverts": len(
                [claim for claim in claims if claim["etat"] == "ouvert"]
            ),
            "claims_contredits": len(
                [claim for claim in claims if claim["etat"] == "contredit"]
            ),
            "claims_confirme": len(
                [claim for claim in claims if claim["etat"] == "confirme"]
            ),
        },
        "anomalies": {
            category: sorted((item for item in values), key=_anomaly_sort_key)
            for category, values in sorted(inventory["anomalies"].items())
        },
    }
    matrix_payload = {
        **_artifact_envelope(inventory, "matrice_livrables", model_digest),
        "manuals": inventory["deliverable_matrix"]["manuals"],
    }
    return {
        "ECARTS_ET_CONTRADICTIONS.yaml": _canonicalize(ecarts_payload),
        "INVENTAIRE_COLLECTION.json": _canonicalize(json_payload),
        "MATRICE_LIVRABLES.yaml": _canonicalize(matrix_payload),
    }


def _render_inventory_artifacts(
    inventory: Mapping[str, Any],
    *,
    repo_root: Path,
    audit_root: Path,
    include_generated_marker: bool = True,
) -> dict[Path, str]:
    marker = AUTOGEN_MARKER if include_generated_marker else ""
    machine_payloads = _machine_artifact_payloads(inventory)

    payloads: dict[Path, str] = {
        audit_root / "INVENTAIRE_COLLECTION.json": json.dumps(
            machine_payloads["INVENTAIRE_COLLECTION.json"],
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        audit_root / "INVENTAIRE_COLLECTION.md": _render_inventory_markdown(
            inventory, marker=marker, root=repo_root
        ),
        audit_root / "AUDIT_CONSOLIDE.md": _render_audit_consolide(
            inventory, marker=marker, root=repo_root
        ),
        audit_root / "ECARTS_ET_CONTRADICTIONS.yaml": yaml.safe_dump(
            machine_payloads["ECARTS_ET_CONTRADICTIONS.yaml"],
            allow_unicode=True,
            sort_keys=True,
            width=120,
        ),
        audit_root / "MATRICE_LIVRABLES.yaml": yaml.safe_dump(
            machine_payloads["MATRICE_LIVRABLES.yaml"],
            allow_unicode=True,
            sort_keys=True,
            width=120,
        ),
    }
    for payload_path, content in payloads.items():
        suffix = payload_path.suffix.lower()
        if suffix == ".json":
            parsed = _validate_output_payload(
                payload_path, content, required_fields=REQUIRED_JSON_FIELDS
            )
            _validate_artifact_schema(parsed, root=repo_root, path=payload_path)
        elif suffix in {".yaml", ".yml"}:
            if include_generated_marker:
                content = f"{marker}\n{content}"
                payloads[payload_path] = content
            parsed = _validate_output_payload(
                payload_path, content, required_fields=REQUIRED_YAML_FIELDS
            )
            _validate_artifact_schema(parsed, root=repo_root, path=payload_path)
        else:
            _validate_output_payload(payload_path, content)

    return payloads


def _compare_rendered_artifacts(
    root: Path,
    rendered_artifacts: dict[Path, str],
) -> list[str]:
    mismatches: list[str] = []
    for relative_path, content in rendered_artifacts.items():
        absolute = root / relative_path if not relative_path.is_absolute() else relative_path
        existing = _utf8_bytes(content)
        if not absolute.exists():
            mismatches.append(f"manquant: {relative_path}")
            continue
        current = absolute.read_bytes()
        if existing != current:
            mismatches.append(f"diff: {relative_path}")
    return mismatches


def _stat_identity(value: os.stat_result) -> tuple[int, int]:
    return value.st_dev, value.st_ino


def _directory_open_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


def _path_matches_directory_identity(
    path: Path,
    expected: os.stat_result,
) -> bool:
    try:
        current = path.stat(follow_symlinks=False)
    except OSError:
        return False
    return stat.S_ISDIR(current.st_mode) and _stat_identity(
        current
    ) == _stat_identity(expected)


def _directory_entry_matches_identity(
    parent_fd: int,
    name: str,
    expected: os.stat_result,
) -> bool:
    try:
        current = os.stat(
            name,
            dir_fd=parent_fd,
            follow_symlinks=False,
        )
    except OSError:
        return False
    return stat.S_ISDIR(current.st_mode) and _stat_identity(
        current
    ) == _stat_identity(expected)


def _open_pinned_directory(
    path: Path,
    *,
    role: str,
) -> tuple[int, os.stat_result]:
    try:
        fd = os.open(path, _directory_open_flags())
    except OSError as exc:
        raise InventoryError(f"{role}: cannot pin directory ({path})") from exc
    try:
        pinned = os.fstat(fd)
        if not stat.S_ISDIR(pinned.st_mode):
            raise InventoryError(f"{role}: not a directory ({path})")
        if not _path_matches_directory_identity(path, pinned):
            raise InventoryError(f"{role}: directory identity changed ({path})")
    except Exception:
        os.close(fd)
        raise
    return fd, pinned


def _create_transaction_directory(
    root_fd: int,
) -> tuple[str, int, os.stat_result, os.stat_result]:
    name = ""
    for _ in range(128):
        name = f".inventory-collection-apply-{secrets.token_hex(12)}"
        try:
            os.mkdir(name, 0o700, dir_fd=root_fd)
            break
        except FileExistsError:
            continue
        except OSError as exc:
            raise InventoryError(
                "transaction directory cannot be created safely"
            ) from exc
    else:
        raise InventoryError("cannot allocate transaction directory")
    try:
        created = os.stat(
            name,
            dir_fd=root_fd,
            follow_symlinks=False,
        )
    except OSError as exc:
        raise InventoryError(
            "transaction directory identity unavailable"
        ) from exc
    if not stat.S_ISDIR(created.st_mode):
        raise InventoryError("transaction directory is not a directory")
    try:
        fd = os.open(
            name,
            _directory_open_flags(),
            dir_fd=root_fd,
        )
    except OSError as exc:
        if _directory_entry_matches_identity(root_fd, name, created):
            try:
                os.rmdir(name, dir_fd=root_fd)
            except OSError:
                pass
        raise InventoryError(
            "transaction directory cannot be pinned"
        ) from exc
    pinned: os.stat_result | None = None
    try:
        pinned = os.fstat(fd)
        if not stat.S_ISDIR(pinned.st_mode):
            raise InventoryError("transaction directory is not a directory")
        if _stat_identity(pinned) != _stat_identity(created):
            raise InventoryError("transaction directory identity changed")
        if not _directory_entry_matches_identity(root_fd, name, pinned):
            raise InventoryError("transaction directory identity changed")
        owner_snapshot = _write_transaction_entry(
            fd,
            "transaction-owner",
            b"",
        )
        os.fsync(fd)
        os.fsync(root_fd)
        return name, fd, pinned, owner_snapshot
    except Exception:
        try:
            os.unlink("transaction-owner", dir_fd=fd)
        except OSError:
            pass
        os.close(fd)
        if pinned is not None and _directory_entry_matches_identity(
            root_fd,
            name,
            pinned,
        ):
            try:
                os.rmdir(name, dir_fd=root_fd)
            except OSError:
                pass
        raise


def _open_destination_parent(
    root_fd: int,
    relative: PurePosixPath,
    *,
    create: bool,
) -> tuple[int, os.stat_result]:
    current_fd = os.dup(root_fd)
    try:
        for component in relative.parent.parts:
            try:
                next_fd = os.open(
                    component,
                    _directory_open_flags(),
                    dir_fd=current_fd,
                )
            except FileNotFoundError as exc:
                if not create:
                    raise InventoryError(
                        "destination parent identity changed or disappeared: "
                        f"{relative.parent}"
                    ) from exc
                try:
                    os.mkdir(component, 0o755, dir_fd=current_fd)
                except FileExistsError:
                    pass
                except OSError as mkdir_exc:
                    raise InventoryError(
                        "destination parent cannot be created safely: "
                        f"{relative.parent}"
                    ) from mkdir_exc
                try:
                    next_fd = os.open(
                        component,
                        _directory_open_flags(),
                        dir_fd=current_fd,
                    )
                except OSError as open_exc:
                    raise InventoryError(
                        "destination parent: symlink escape or "
                        f"non-directory component ({relative.parent})"
                    ) from open_exc
            except OSError as exc:
                raise InventoryError(
                    "destination parent: symlink escape or "
                    f"non-directory component ({relative.parent})"
                ) from exc
            os.close(current_fd)
            current_fd = next_fd
        parent_stat = os.fstat(current_fd)
        if not stat.S_ISDIR(parent_stat.st_mode):
            raise InventoryError(
                f"destination parent is not a directory: {relative.parent}"
            )
        return current_fd, parent_stat
    except Exception:
        os.close(current_fd)
        raise


def _revalidate_destination_parent(
    root_fd: int,
    relative: PurePosixPath,
    expected: os.stat_result,
) -> None:
    current_fd, current_stat = _open_destination_parent(
        root_fd,
        relative,
        create=False,
    )
    try:
        if _stat_identity(current_stat) != _stat_identity(expected):
            raise InventoryError(
                f"destination parent identity changed: {relative.parent}"
            )
    finally:
        os.close(current_fd)


def _read_destination_backup(
    parent_fd: int,
    basename: str,
) -> tuple[bytes, os.stat_result] | None:
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    try:
        fd = os.open(basename, flags, dir_fd=parent_fd)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise InventoryError(
            f"destination target: symlink or unavailable regular file ({basename})"
        ) from exc
    try:
        target_stat = os.fstat(fd)
        if not stat.S_ISREG(target_stat.st_mode):
            raise InventoryError(
                f"destination target is not a regular file: {basename}"
            )
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks), target_stat
    finally:
        os.close(fd)


def _read_confined_json_mapping(
    root: Path,
    relative: PurePosixPath,
    *,
    role: str,
) -> dict[str, Any]:
    root = root.resolve()
    _clean_path(relative.as_posix(), role=role, repository=root)
    root_fd, root_stat = _open_pinned_directory(
        root,
        role=f"{role} repository root",
    )
    parent_fd: int | None = None
    try:
        parent_fd, parent_stat = _open_destination_parent(
            root_fd,
            relative,
            create=False,
        )
        value = _read_destination_backup(parent_fd, relative.name)
        if value is None:
            raise InventoryError(f"{role} absente: {relative}")
        payload, target_stat = value
        _require_repository_root_identity(root, root_stat)
        _revalidate_destination_parent(root_fd, relative, parent_stat)
        _revalidate_destination_entry(
            parent_fd,
            relative.name,
            target_stat,
        )
        try:
            decoded = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InventoryError(
                f"{role} absente ou JSON invalide: {relative}"
            ) from exc
        if not isinstance(decoded, Mapping):
            raise InventoryError(f"{role} JSON doit être un objet: {relative}")
        return dict(decoded)
    finally:
        if parent_fd is not None:
            os.close(parent_fd)
        os.close(root_fd)


def _revalidate_destination_entry(
    parent_fd: int,
    basename: str,
    expected: os.stat_result | None,
) -> None:
    try:
        current = os.stat(
            basename,
            dir_fd=parent_fd,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        if expected is None:
            return
        raise InventoryError(
            f"destination target identity changed or disappeared: {basename}"
        )
    if expected is None:
        raise InventoryError(
            f"destination target appeared during transaction: {basename}"
        )
    if (
        not stat.S_ISREG(current.st_mode)
        or _stat_identity(current) != _stat_identity(expected)
    ):
        raise InventoryError(
            f"destination target identity changed: {basename}"
        )


def _require_repository_root_identity(
    root: Path,
    expected: os.stat_result,
) -> None:
    if not _path_matches_directory_identity(root, expected):
        raise InventoryError("repository root identity changed")


def _write_all(fd: int, payload: bytes) -> None:
    offset = 0
    while offset < len(payload):
        written = os.write(fd, payload[offset:])
        if written <= 0:
            raise OSError("short write")
        offset += written


def _write_transaction_entry(
    directory_fd: int,
    name: str,
    payload: bytes,
) -> os.stat_result:
    flags = (
        os.O_CREAT
        | os.O_EXCL
        | os.O_WRONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    fd = os.open(name, flags, 0o600, dir_fd=directory_fd)
    identity = os.fstat(fd)
    try:
        if not stat.S_ISREG(identity.st_mode) or identity.st_nlink != 1:
            raise InventoryError(
                f"transaction entry creation is not exclusive: {name}"
            )
        _write_all(fd, payload)
        os.fsync(fd)
        return identity
    finally:
        os.close(fd)


def _publish_transaction_entry(
    directory_fd: int,
    *,
    temporary_name: str,
    final_name: str,
    payload: bytes,
) -> os.stat_result:
    identity = _write_transaction_entry(
        directory_fd,
        temporary_name,
        payload,
    )
    try:
        os.rename(
            temporary_name,
            final_name,
            src_dir_fd=directory_fd,
            dst_dir_fd=directory_fd,
        )
        _revalidate_transaction_entry_snapshot(
            directory_fd,
            final_name,
            identity,
        )
        os.fsync(directory_fd)
        return identity
    except Exception:
        try:
            os.unlink(temporary_name, dir_fd=directory_fd)
        except FileNotFoundError:
            pass
        raise


def _transaction_entry_is_regular(directory_fd: int, name: str) -> bool:
    try:
        value = os.stat(
            name,
            dir_fd=directory_fd,
            follow_symlinks=False,
        )
    except OSError:
        return False
    return stat.S_ISREG(value.st_mode)


def _copy_recovery_payload(
    root: Path,
    *,
    root_fd: int,
    payload: bytes,
) -> Path:
    destination_fd: int | None = None
    recovery_name = ""
    for _ in range(128):
        recovery_name = (
            f".inventory-collection-recovery-{secrets.token_hex(16)}.bak"
        )
        try:
            destination_fd = os.open(
                recovery_name,
                os.O_CREAT
                | os.O_EXCL
                | os.O_RDWR
                | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                0o600,
                dir_fd=root_fd,
            )
            break
        except FileExistsError:
            continue
    if destination_fd is None:
        raise InventoryError("cannot allocate recovery backup")
    destination_stat = os.fstat(destination_fd)
    try:
        if (
            not stat.S_ISREG(destination_stat.st_mode)
            or destination_stat.st_nlink != 1
        ):
            raise InventoryError(
                "recovery backup creation is not exclusive"
            )
        _write_all(destination_fd, payload)
        os.fsync(destination_fd)
        os.lseek(destination_fd, 0, os.SEEK_SET)
        chunks: list[bytes] = []
        while True:
            chunk = os.read(destination_fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        verified_stat = os.fstat(destination_fd)
        if (
            b"".join(chunks) != payload
            or _stat_identity(verified_stat)
            != _stat_identity(destination_stat)
            or verified_stat.st_nlink != 1
        ):
            raise InventoryError(
                f"recovery backup content changed: {root / recovery_name}"
            )
        current = os.stat(
            recovery_name,
            dir_fd=root_fd,
            follow_symlinks=False,
        )
        if (
            not stat.S_ISREG(current.st_mode)
            or _stat_identity(current) != _stat_identity(destination_stat)
            or current.st_nlink != 1
        ):
            raise InventoryError("recovery backup identity changed")
        os.lseek(destination_fd, 0, os.SEEK_SET)
        final_chunks: list[bytes] = []
        while True:
            chunk = os.read(destination_fd, 1024 * 1024)
            if not chunk:
                break
            final_chunks.append(chunk)
        if b"".join(final_chunks) != payload:
            raise InventoryError(
                f"recovery backup content changed: {root / recovery_name}"
            )
        os.fsync(root_fd)
        os.lseek(destination_fd, 0, os.SEEK_SET)
        durable_chunks: list[bytes] = []
        while True:
            chunk = os.read(destination_fd, 1024 * 1024)
            if not chunk:
                break
            durable_chunks.append(chunk)
        durable_fd_stat = os.fstat(destination_fd)
        durable_name_stat = os.stat(
            recovery_name,
            dir_fd=root_fd,
            follow_symlinks=False,
        )
        if (
            b"".join(durable_chunks) != payload
            or _stat_identity(durable_fd_stat)
            != _stat_identity(destination_stat)
            or durable_fd_stat.st_nlink != 1
            or not stat.S_ISREG(durable_name_stat.st_mode)
            or _stat_identity(durable_name_stat)
            != _stat_identity(destination_stat)
            or durable_name_stat.st_nlink != 1
        ):
            raise InventoryError("recovery backup identity changed")
        return root / recovery_name
    finally:
        os.close(destination_fd)


def _exchange_directory_entries(
    source_fd: int,
    source_name: str,
    destination_fd: int,
    destination_name: str,
) -> None:
    renameat2 = getattr(ctypes.CDLL(None, use_errno=True), "renameat2", None)
    if renameat2 is None:
        raise InventoryError("atomic entry exchange is unavailable")
    renameat2.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    )
    renameat2.restype = ctypes.c_int
    result = renameat2(
        source_fd,
        os.fsencode(source_name),
        destination_fd,
        os.fsencode(destination_name),
        2,  # RENAME_EXCHANGE
    )
    if result != 0:
        error_number = ctypes.get_errno()
        raise OSError(
            error_number,
            os.strerror(error_number),
            source_name,
            destination_name,
        )


def _restore_authenticated_payload(
    parent_fd: int,
    basename: str,
    payload: bytes,
    *,
    preserved_entries: list[str],
) -> os.stat_result:
    for _attempt in range(3):
        rollback_name = ""
        rollback_snapshot: os.stat_result | None = None
        for _ in range(128):
            rollback_name = (
                f".inventory-collection-rollback-{secrets.token_hex(16)}.tmp"
            )
            try:
                rollback_snapshot = _write_transaction_entry(
                    parent_fd,
                    rollback_name,
                    payload,
                )
                break
            except FileExistsError:
                continue
        if rollback_snapshot is None:
            raise InventoryError("cannot allocate rollback entry")
        _revalidate_transaction_entry_snapshot(
            parent_fd,
            rollback_name,
            rollback_snapshot,
        )
        _exchange_directory_entries(
            parent_fd,
            rollback_name,
            parent_fd,
            basename,
        )
        preserved_entries.append(rollback_name)
        os.fsync(parent_fd)
        restored = _read_destination_backup(parent_fd, basename)
        if restored is None:
            continue
        restored_payload, restored_snapshot = restored
        if (
            _stat_identity(restored_snapshot)
            == _stat_identity(rollback_snapshot)
            and restored_payload == payload
        ):
            _revalidate_destination_entry(
                parent_fd,
                basename,
                restored_snapshot,
            )
            return restored_snapshot
        _revalidate_destination_entry(
            parent_fd,
            basename,
            restored_snapshot,
        )
        quarantine_name = ""
        quarantine_snapshot: os.stat_result | None = None
        for _ in range(128):
            quarantine_name = (
                ".inventory-collection-preserved-rollback-"
                f"{secrets.token_hex(16)}.wip"
            )
            try:
                quarantine_snapshot = _write_transaction_entry(
                    parent_fd,
                    quarantine_name,
                    b"",
                )
                break
            except FileExistsError:
                continue
        if quarantine_snapshot is None:
            raise InventoryError("cannot allocate rollback quarantine")
        _revalidate_transaction_entry_snapshot(
            parent_fd,
            quarantine_name,
            quarantine_snapshot,
        )
        _exchange_directory_entries(
            parent_fd,
            basename,
            parent_fd,
            quarantine_name,
        )
        preserved_entries.append(quarantine_name)
        os.fsync(parent_fd)
        _revalidate_destination_entry(
            parent_fd,
            basename,
            quarantine_snapshot,
        )
        quarantined = _read_destination_backup(
            parent_fd,
            quarantine_name,
        )
        if quarantined is None:
            raise InventoryError(
                "preserved rollback entry disappeared: "
                f"{quarantine_name}"
            )
        _quarantined_payload, quarantined_snapshot = quarantined
        _revalidate_destination_entry(
            parent_fd,
            quarantine_name,
            quarantined_snapshot,
        )
    raise InventoryError("rollback entry changed repeatedly")


_TRANSACTION_DIRECTORY_RE = re.compile(
    r"^\.inventory-collection-apply-[0-9a-f]{24}$"
)
_TRANSACTION_ENTRY_RE = re.compile(r"^(?:stage|backup)-[0-9]{8}$")


def _transaction_payload_digest(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _revalidate_transaction_entry_snapshot(
    transaction_fd: int,
    entry: str,
    expected: os.stat_result,
) -> None:
    try:
        current = os.stat(
            entry,
            dir_fd=transaction_fd,
            follow_symlinks=False,
        )
    except OSError as exc:
        raise InventoryError(
            f"transaction validation entry unavailable: {entry}"
        ) from exc
    if not stat.S_ISREG(current.st_mode):
        raise InventoryError(
            f"transaction validation entry is not regular: {entry}"
        )
    if _stat_identity(current) != _stat_identity(expected):
        raise InventoryError(
            f"transaction validation entry identity changed: {entry}"
        )
    if expected.st_nlink != 1 or current.st_nlink != 1:
        raise InventoryError(
            f"transaction validation entry link count changed: {entry}"
        )


def _owned_transaction_entry_identities(
    transaction_name: str,
    transaction_fd: int,
    expected_entries: Mapping[str, os.stat_result],
) -> dict[str, tuple[int, int]]:
    actual_entries = set(os.listdir(transaction_fd))
    if actual_entries != set(expected_entries):
        raise InventoryError("transaction entries changed before validation")
    identities: dict[str, tuple[int, int]] = {}
    for entry, expected in sorted(expected_entries.items()):
        _revalidate_transaction_entry_snapshot(
            transaction_fd,
            entry,
            expected,
        )
        identities[f"{transaction_name}/{entry}"] = _stat_identity(expected)
    return identities


def _recover_interrupted_transactions(
    root: Path,
    *,
    root_fd: int,
    root_stat: os.stat_result,
) -> None:
    candidates: list[tuple[int, str, os.stat_result]] = []
    for name in os.listdir(root_fd):
        if not _TRANSACTION_DIRECTORY_RE.fullmatch(name):
            continue
        value = os.stat(name, dir_fd=root_fd, follow_symlinks=False)
        if not stat.S_ISDIR(value.st_mode):
            raise InventoryError(
                f"interrupted transaction is not a directory: {name}"
            )
        candidates.append((value.st_mtime_ns, name, value))

    for _mtime, name, expected_directory in sorted(
        candidates,
        reverse=True,
    ):
        _require_repository_root_identity(root, root_stat)
        transaction_fd = os.open(
            name,
            _directory_open_flags(),
            dir_fd=root_fd,
        )
        try:
            pinned = os.fstat(transaction_fd)
            if (
                _stat_identity(pinned)
                != _stat_identity(expected_directory)
                or not _directory_entry_matches_identity(
                    root_fd,
                    name,
                    pinned,
                )
            ):
                raise InventoryError(
                    f"interrupted transaction identity changed: {name}"
                )
            if not os.listdir(transaction_fd):
                os.rmdir(name, dir_fd=root_fd)
                os.fsync(root_fd)
                continue
            preparing_value = _read_destination_backup(
                transaction_fd,
                "preparing.json",
            )
            preparing_record = (
                _parse_lock_record(preparing_value[0])
                if preparing_value is not None
                else None
            )
            ready_value = _read_destination_backup(
                transaction_fd,
                "journal-ready",
            )
            transaction_owner = _read_destination_backup(
                transaction_fd,
                "transaction-owner",
            )
            if transaction_owner is None or transaction_owner[0] != b"":
                raise InventoryError(
                    f"interrupted transaction owner marker is invalid: {name}"
                )
            if ready_value is not None and ready_value[0] != b"":
                raise InventoryError(
                    f"interrupted transaction ready marker is invalid: {name}"
                )
            journal_value = _read_destination_backup(
                transaction_fd,
                "journal.json",
            )
            if journal_value is None:
                remaining = set(os.listdir(transaction_fd))
                if remaining.issubset({"committed"}):
                    for entry_name in remaining:
                        if not _transaction_entry_is_regular(
                            transaction_fd,
                            entry_name,
                        ):
                            raise InventoryError(
                                "interrupted transaction contains a "
                                f"non-regular entry: {entry_name}"
                            )
                        os.unlink(entry_name, dir_fd=transaction_fd)
                    os.fsync(transaction_fd)
                    if not _directory_entry_matches_identity(
                        root_fd,
                        name,
                        expected_directory,
                    ):
                        raise InventoryError(
                            "interrupted transaction identity changed: "
                            f"{name}"
                        )
                    os.rmdir(name, dir_fd=root_fd)
                    os.fsync(root_fd)
                    continue
            journal: Any = None
            owner_record: dict[str, Any] | None = None
            if journal_value is not None:
                journal_bytes, _journal_stat = journal_value
                try:
                    journal = json.loads(journal_bytes.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    pass
                owner_record = _parse_lock_record(journal_bytes)
            published = (
                ready_value is not None
                and isinstance(journal, Mapping)
                and journal.get("schema_version") == 1
                and isinstance(journal.get("entries"), list)
                and bool(journal["entries"])
                and owner_record is not None
            )
            if not published:
                if (
                    ready_value is not None
                    or (
                        preparing_record is not None
                        and _lock_owner_is_live(preparing_record)
                    )
                ):
                    raise InventoryError(
                        f"interrupted transaction journal is invalid: {name}"
                    )
                actual_entries = set(os.listdir(transaction_fd))
                if any(
                    entry
                    not in {
                        "journal.json",
                        "journal.tmp",
                        "preparing.json",
                        "preparing.tmp",
                        "transaction-owner",
                    }
                    and not _TRANSACTION_ENTRY_RE.fullmatch(entry)
                    for entry in actual_entries
                ):
                    raise InventoryError(
                        "unpublished transaction contains unexpected entries: "
                        + ", ".join(sorted(actual_entries))
                    )
                for entry_name in sorted(actual_entries):
                    if not _transaction_entry_is_regular(
                        transaction_fd,
                        entry_name,
                    ):
                        raise InventoryError(
                            "unpublished transaction contains a non-regular "
                            f"entry: {entry_name}"
                        )
                    os.unlink(entry_name, dir_fd=transaction_fd)
                os.fsync(transaction_fd)
                if not _directory_entry_matches_identity(
                    root_fd,
                    name,
                    expected_directory,
                ):
                    raise InventoryError(
                        f"interrupted transaction identity changed: {name}"
                    )
                os.rmdir(name, dir_fd=root_fd)
                os.fsync(root_fd)
                continue
            assert isinstance(journal, Mapping)
            assert owner_record is not None
            if _lock_owner_is_live(owner_record):
                raise InventoryError(
                    f"transaction owner is still active: {name}"
                )

            committed_value = _read_destination_backup(
                transaction_fd,
                "committed",
            )
            if (
                committed_value is not None
                and committed_value[0] != b""
            ):
                raise InventoryError(
                    f"interrupted transaction commit marker is invalid: {name}"
                )
            committed = committed_value is not None
            allowed_entries = {
                "committed",
                "journal-ready",
                "journal.json",
                "preparing.json",
                "transaction-owner",
            }
            seen_targets: set[PurePosixPath] = set()
            for raw_entry in journal["entries"]:
                if not isinstance(raw_entry, Mapping):
                    raise InventoryError(
                        f"interrupted transaction entry is invalid: {name}"
                    )
                relative_text = raw_entry.get("relative")
                stage_name = raw_entry.get("stage_name")
                stage_digest = raw_entry.get("stage_digest")
                backup_name = raw_entry.get("backup_name")
                backup_digest = raw_entry.get("backup_digest")
                if (
                    not isinstance(relative_text, str)
                    or not isinstance(stage_name, str)
                    or not _TRANSACTION_ENTRY_RE.fullmatch(stage_name)
                    or not isinstance(stage_digest, str)
                    or not re.fullmatch(r"sha256:[0-9a-f]{64}", stage_digest)
                    or (
                        backup_name is not None
                        and (
                            not isinstance(backup_name, str)
                            or not _TRANSACTION_ENTRY_RE.fullmatch(backup_name)
                            or not isinstance(backup_digest, str)
                            or not re.fullmatch(
                                r"sha256:[0-9a-f]{64}",
                                backup_digest,
                            )
                        )
                    )
                    or (backup_name is None and backup_digest is not None)
                ):
                    raise InventoryError(
                        f"interrupted transaction entry is invalid: {name}"
                    )
                relative = PurePosixPath(relative_text)
                _clean_path(
                    relative.as_posix(),
                    role="transaction recovery target",
                    repository=root,
                )
                if not relative.name or relative in seen_targets:
                    raise InventoryError(
                        f"interrupted transaction target is invalid: {relative}"
                    )
                seen_targets.add(relative)
                allowed_entries.add(stage_name)
                if isinstance(backup_name, str):
                    allowed_entries.add(backup_name)

                stage = _read_destination_backup(
                    transaction_fd,
                    stage_name,
                )
                if (
                    stage is not None
                    and _transaction_payload_digest(stage[0]) != stage_digest
                ):
                    raise InventoryError(
                        f"staged recovery payload is corrupted: {relative}"
                    )
                backup = (
                    _read_destination_backup(transaction_fd, backup_name)
                    if isinstance(backup_name, str)
                    else None
                )
                if (
                    backup is not None
                    and _transaction_payload_digest(backup[0]) != backup_digest
                ):
                    raise InventoryError(
                        f"recovery backup is corrupted: {relative}"
                    )

                parent_fd, parent_stat = _open_destination_parent(
                    root_fd,
                    relative,
                    create=False,
                )
                try:
                    _revalidate_destination_parent(
                        root_fd,
                        relative,
                        parent_stat,
                    )
                    current = _read_destination_backup(
                        parent_fd,
                        relative.name,
                    )
                    current_digest = (
                        _transaction_payload_digest(current[0])
                        if current is not None
                        else None
                    )
                    _revalidate_destination_entry(
                        parent_fd,
                        relative.name,
                        current[1] if current is not None else None,
                    )
                    expected_digest: str | None
                    if committed:
                        if current_digest != stage_digest:
                            raise InventoryError(
                                "committed recovery target is incoherent: "
                                f"{relative}"
                            )
                        expected_digest = stage_digest
                    elif isinstance(backup_name, str):
                        if current_digest == stage_digest:
                            if backup is None:
                                raise InventoryError(
                                    "recovery backup unavailable for applied "
                                    f"target: {relative}"
                                )
                            os.replace(
                                backup_name,
                                relative.name,
                                src_dir_fd=transaction_fd,
                                dst_dir_fd=parent_fd,
                            )
                        elif current_digest != backup_digest:
                            raise InventoryError(
                                "recovery target was modified concurrently: "
                                    f"{relative}"
                                )
                        expected_digest = str(backup_digest)
                    elif current_digest == stage_digest:
                        os.unlink(relative.name, dir_fd=parent_fd)
                        expected_digest = None
                    elif current_digest is not None:
                        raise InventoryError(
                            "recovery target was modified concurrently: "
                            f"{relative}"
                        )
                    else:
                        expected_digest = None
                    os.fsync(parent_fd)
                    recovered = _read_destination_backup(
                        parent_fd,
                        relative.name,
                    )
                    recovered_digest = (
                        _transaction_payload_digest(recovered[0])
                        if recovered is not None
                        else None
                    )
                    if recovered_digest != expected_digest:
                        raise InventoryError(
                            f"recovery postcondition failed: {relative}"
                        )
                    _revalidate_destination_entry(
                        parent_fd,
                        relative.name,
                        recovered[1] if recovered is not None else None,
                    )
                    _require_repository_root_identity(root, root_stat)
                    _revalidate_destination_parent(
                        root_fd,
                        relative,
                        parent_stat,
                    )
                finally:
                    os.close(parent_fd)

            actual_entries = set(os.listdir(transaction_fd))
            unexpected = actual_entries - allowed_entries
            if unexpected:
                raise InventoryError(
                    "interrupted transaction contains unexpected entries: "
                    + ", ".join(sorted(unexpected))
                )
            for entry_name in sorted(
                actual_entries,
                key=lambda value: (
                    value == "committed",
                    value == "journal.json",
                    value,
                ),
            ):
                if not _transaction_entry_is_regular(
                    transaction_fd,
                    entry_name,
                ):
                    raise InventoryError(
                        "interrupted transaction contains a non-regular entry: "
                        f"{entry_name}"
                    )
                os.unlink(entry_name, dir_fd=transaction_fd)
            os.fsync(transaction_fd)
        finally:
            os.close(transaction_fd)
        if not _directory_entry_matches_identity(
            root_fd,
            name,
            expected_directory,
        ):
            raise InventoryError(
                f"interrupted transaction identity changed: {name}"
            )
        os.rmdir(name, dir_fd=root_fd)
        os.fsync(root_fd)


def _recover_repository_transactions(root: Path) -> None:
    root = root.resolve()
    root_fd, root_stat = _open_pinned_directory(
        root,
        role="repository recovery root",
    )
    try:
        _recover_interrupted_transactions(
            root,
            root_fd=root_fd,
            root_stat=root_stat,
        )
    finally:
        os.close(root_fd)


def _apply_atomic_payloads(
    root: Path,
    rendered_artifacts: dict[Path, str],
    *,
    validate_before_apply: (
        Callable[[Mapping[str, tuple[int, int]]], None] | None
    ) = None,
    validate_state: Callable[[], None] | None = None,
) -> None:
    root = root.resolve()
    targets: dict[PurePosixPath, str] = {}
    for path, content in rendered_artifacts.items():
        if path.is_absolute():
            try:
                relative_path = path.relative_to(root)
            except ValueError as exc:
                raise InventoryError(
                    f"output: outside repository ({path})"
                ) from exc
        else:
            relative_path = path
        relative = PurePosixPath(relative_path.as_posix())
        _clean_path(relative.as_posix(), role="output", repository=root)
        if not relative.name:
            raise InventoryError("output: missing destination basename")
        if relative in targets:
            raise InventoryError(f"duplicate output target: {relative}")
        targets[relative] = content

    destination_parents: dict[
        PurePosixPath,
        tuple[int, os.stat_result],
    ] = {}
    destination_snapshots: dict[
        PurePosixPath,
        os.stat_result | None,
    ] = {}
    stage_snapshots: dict[PurePosixPath, os.stat_result] = {}
    applied_snapshots: dict[PurePosixPath, os.stat_result] = {}
    staged: dict[PurePosixPath, str] = {}
    stage_digests: dict[PurePosixPath, str] = {}
    backups: dict[PurePosixPath, str] = {}
    backup_payloads: dict[PurePosixPath, bytes] = {}
    backup_digests: dict[PurePosixPath, str] = {}
    transaction_entries: set[str] = set()
    transaction_entry_snapshots: dict[str, os.stat_result] = {}
    preserved_transaction_entries: set[str] = set()
    preserved_rollback_entries: list[Path] = []
    replaced: list[PurePosixPath] = []
    legacy_temp_root = root / ".inventory-collection-apply"
    if (
        legacy_temp_root.is_symlink()
        and not legacy_temp_root.resolve().is_relative_to(root)
    ):
        raise InventoryError(
            "transaction directory: symlink escape outside repository"
        )
    root_fd, root_stat = _open_pinned_directory(
        root,
        role="repository transaction root",
    )
    try:
        _recover_interrupted_transactions(
            root,
            root_fd=root_fd,
            root_stat=root_stat,
        )
        (
            temp_name,
            temp_fd,
            temp_stat,
            owner_snapshot,
        ) = _create_transaction_directory(root_fd)
        transaction_entries.add("transaction-owner")
        transaction_entry_snapshots["transaction-owner"] = owner_snapshot
    except Exception:
        os.close(root_fd)
        raise
    try:
        _require_repository_root_identity(root, root_stat)
        if validate_state is not None:
            validate_state()
        process_start_token = _process_start_token(os.getpid())
        if not process_start_token:
            raise InventoryError(
                "cannot identify transaction journal owner"
            )
        owner_record = {
            "created_at_utc": datetime.datetime.now(datetime.UTC)
            .isoformat()
            .replace("+00:00", "Z"),
            "pid": os.getpid(),
            "process_start_token": process_start_token,
            "schema_version": 1,
        }
        preparing_snapshot = _publish_transaction_entry(
            temp_fd,
            temporary_name="preparing.tmp",
            final_name="preparing.json",
            payload=_utf8_bytes(
                json.dumps(
                    owner_record,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
            ),
        )
        transaction_entries.add("preparing.json")
        transaction_entry_snapshots["preparing.json"] = preparing_snapshot
        for relative in targets:
            destination_parents[relative] = _open_destination_parent(
                root_fd,
                relative,
                create=True,
            )
        for index, (relative, content) in enumerate(targets.items()):
            parent_fd, _parent_stat = destination_parents[relative]
            stage_name = f"stage-{index:08d}"
            stage_payload = _utf8_bytes(content)
            stage_snapshots[relative] = _write_transaction_entry(
                temp_fd,
                stage_name,
                stage_payload,
            )
            transaction_entry_snapshots[stage_name] = stage_snapshots[
                relative
            ]
            staged[relative] = stage_name
            stage_digests[relative] = _transaction_payload_digest(
                stage_payload
            )
            transaction_entries.add(stage_name)
            backup = _read_destination_backup(
                parent_fd,
                relative.name,
            )
            if backup is None:
                destination_snapshots[relative] = None
            else:
                backup_payload, target_stat = backup
                destination_snapshots[relative] = target_stat
                backup_name = f"backup-{index:08d}"
                backup_snapshot = _write_transaction_entry(
                    temp_fd,
                    backup_name,
                    backup_payload,
                )
                backup_payloads[relative] = backup_payload
                transaction_entry_snapshots[backup_name] = backup_snapshot
                backups[relative] = backup_name
                backup_digests[relative] = _transaction_payload_digest(
                    backup_payload
                )
                transaction_entries.add(backup_name)

        journal = {
            **owner_record,
            "entries": [
                {
                    "backup_digest": backup_digests.get(relative),
                    "backup_name": backups.get(relative),
                    "relative": relative.as_posix(),
                    "stage_digest": stage_digests[relative],
                    "stage_name": staged[relative],
                }
                for relative in sorted(targets, key=str)
            ],
        }
        journal_snapshot = _publish_transaction_entry(
            temp_fd,
            temporary_name="journal.tmp",
            final_name="journal.json",
            payload=_utf8_bytes(
                json.dumps(
                    journal,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
            ),
        )
        transaction_entries.add("journal.json")
        transaction_entry_snapshots["journal.json"] = journal_snapshot
        journal_ready_snapshot = _write_transaction_entry(
            temp_fd,
            "journal-ready",
            b"",
        )
        transaction_entries.add("journal-ready")
        transaction_entry_snapshots[
            "journal-ready"
        ] = journal_ready_snapshot
        os.fsync(temp_fd)
        _require_repository_root_identity(root, root_stat)
        if validate_before_apply is not None:
            validate_before_apply(
                _owned_transaction_entry_identities(
                    temp_name,
                    temp_fd,
                    transaction_entry_snapshots,
                )
            )
        for relative, stage_name in sorted(
            staged.items(),
            key=lambda item: str(item[0]),
        ):
            _require_repository_root_identity(root, root_stat)
            if validate_state is not None:
                validate_state()
            parent_fd, parent_stat = destination_parents[relative]
            _revalidate_transaction_entry_snapshot(
                temp_fd,
                stage_name,
                stage_snapshots[relative],
            )
            _revalidate_destination_parent(
                root_fd,
                relative,
                parent_stat,
            )
            _revalidate_destination_entry(
                parent_fd,
                relative.name,
                destination_snapshots[relative],
            )
            os.replace(
                stage_name,
                relative.name,
                src_dir_fd=temp_fd,
                dst_dir_fd=parent_fd,
            )
            replaced.append(relative)
            applied_stat = os.stat(
                relative.name,
                dir_fd=parent_fd,
                follow_symlinks=False,
            )
            if not stat.S_ISREG(applied_stat.st_mode):
                raise InventoryError(
                    f"applied destination is not regular: {relative}"
                )
            if _stat_identity(applied_stat) != _stat_identity(
                stage_snapshots[relative]
            ):
                raise InventoryError(
                    f"applied destination identity changed: {relative}"
                )
            applied_snapshots[relative] = applied_stat
            os.fsync(parent_fd)
            if validate_state is not None:
                validate_state()
        _require_repository_root_identity(root, root_stat)
        for relative, (parent_fd, parent_stat) in destination_parents.items():
            _revalidate_destination_parent(
                root_fd,
                relative,
                parent_stat,
            )
            _revalidate_destination_entry(
                parent_fd,
                relative.name,
                applied_snapshots[relative],
            )
        if validate_state is not None:
            validate_state()
        committed_snapshot = _write_transaction_entry(
            temp_fd,
            "committed",
            b"",
        )
        transaction_entries.add("committed")
        transaction_entry_snapshots["committed"] = committed_snapshot
        os.fsync(temp_fd)
        if validate_state is not None:
            validate_state()
    except Exception as exc:
        rollback_errors: list[str] = []
        recoverable_backups: list[Path] = []
        for relative in sorted(replaced, reverse=True):
            parent_fd, _parent_stat = destination_parents[relative]
            try:
                applied_stat = applied_snapshots.get(relative)
                if applied_stat is None:
                    raise InventoryError(
                        f"applied destination identity unavailable: {relative}"
                    )
                _revalidate_destination_entry(
                    parent_fd,
                    relative.name,
                    applied_stat,
                )
                backup_payload = backup_payloads.get(relative)
                if backup_payload is not None:
                    quarantined_names: list[str] = []
                    try:
                        _restore_authenticated_payload(
                            parent_fd,
                            relative.name,
                            backup_payload,
                            preserved_entries=quarantined_names,
                        )
                    finally:
                        preserved_rollback_entries.extend(
                            Path(relative.parent.as_posix()) / name
                            for name in quarantined_names
                        )
                else:
                    os.unlink(relative.name, dir_fd=parent_fd)
                os.fsync(parent_fd)
            except Exception as rollback_exc:
                backup_payload = backup_payloads.get(relative)
                if backup_payload is not None:
                    try:
                        recoverable_backups.append(
                            _copy_recovery_payload(
                                root,
                                root_fd=root_fd,
                                payload=backup_payload,
                            )
                        )
                    except Exception as recovery_exc:
                        rollback_errors.append(
                            f"recovery backup failed: {recovery_exc}"
                        )
                rollback_errors.append(str(rollback_exc))
        if preserved_transaction_entries:
            preserved_transaction_entries.add("journal.json")
        message = "transaction rolled back"
        if rollback_errors:
            message += " incompletely: " + "; ".join(rollback_errors)
        if recoverable_backups:
            message += "; " + "; ".join(
                f"recoverable backup: {path}"
                for path in recoverable_backups
            )
        if preserved_rollback_entries:
            message += "; " + "; ".join(
                f"preserved rollback entry: {path}"
                for path in preserved_rollback_entries
            )
        raise InventoryError(f"{message}; cause: {exc}") from exc
    finally:
        active_error = sys.exc_info()[1]
        cleanup_errors: list[str] = []
        try:
            for name in sorted(
                transaction_entries,
                key=lambda value: (
                    value == "committed",
                    value == "journal.json",
                    value,
                ),
            ):
                if name in preserved_transaction_entries:
                    continue
                try:
                    os.stat(
                        name,
                        dir_fd=temp_fd,
                        follow_symlinks=False,
                    )
                except FileNotFoundError:
                    continue
                except OSError as cleanup_exc:
                    preserved_transaction_entries.add(name)
                    preserved_transaction_entries.add("journal.json")
                    cleanup_errors.append(
                        f"preserved transaction entry {name}: {cleanup_exc}"
                    )
                    continue
                expected_snapshot = transaction_entry_snapshots.get(name)
                try:
                    if expected_snapshot is None:
                        raise InventoryError(
                            "transaction validation entry identity "
                            f"unavailable: {name}"
                        )
                    _revalidate_transaction_entry_snapshot(
                        temp_fd,
                        name,
                        expected_snapshot,
                    )
                except InventoryError as cleanup_exc:
                    preserved_transaction_entries.add(name)
                    preserved_transaction_entries.add("journal.json")
                    cleanup_errors.append(
                        "preserved foreign transaction entry "
                        f"{name}: {cleanup_exc}"
                    )
                    continue
                try:
                    os.unlink(name, dir_fd=temp_fd)
                except FileNotFoundError:
                    pass
                except OSError as cleanup_exc:
                    cleanup_errors.append(f"unlink {name}: {cleanup_exc}")
            try:
                os.fsync(temp_fd)
            except OSError as cleanup_exc:
                cleanup_errors.append(f"fsync transaction directory: {cleanup_exc}")
            if (
                not preserved_transaction_entries
                and _directory_entry_matches_identity(
                    root_fd,
                    temp_name,
                    temp_stat,
                )
            ):
                try:
                    os.rmdir(temp_name, dir_fd=root_fd)
                except OSError as cleanup_exc:
                    cleanup_errors.append(
                        f"rmdir transaction directory: {cleanup_exc}"
                    )
        finally:
            for relative, (parent_fd, _parent_stat) in sorted(
                destination_parents.items(),
                key=lambda item: str(item[0]),
            ):
                try:
                    os.close(parent_fd)
                except OSError as cleanup_exc:
                    cleanup_errors.append(
                        f"close destination parent {relative.parent}: "
                        f"{cleanup_exc}"
                    )
            try:
                os.close(temp_fd)
            except OSError as cleanup_exc:
                cleanup_errors.append(f"close transaction directory: {cleanup_exc}")
            try:
                os.close(root_fd)
            except OSError as cleanup_exc:
                cleanup_errors.append(f"close repository root: {cleanup_exc}")
        if cleanup_errors:
            detail = "; ".join(cleanup_errors)
            if active_error is not None:
                active_error.add_note(f"transaction cleanup failed: {detail}")
            else:
                raise InventoryError(
                    f"transaction cleanup failed: {detail}"
                )


def _reuse_stored_generation_provenance(
    root: Path,
    audit_root: Path,
    inventory: dict[str, Any],
) -> None:
    inventory_path = audit_root / "INVENTAIRE_COLLECTION.json"
    if not inventory_path.is_file():
        return
    relative_path = inventory_path.relative_to(root).as_posix()
    stored_inventory = _load_model_artifact(root, relative_path)
    if stored_inventory.get("model_digest") != _model_digest(stored_inventory):
        raise InventoryError(
            f"inventaire existant invalide pour --check: {relative_path}"
        )
    stored_provenance = stored_inventory.get("provenance")
    current_provenance = inventory.get("provenance")
    if not isinstance(stored_provenance, Mapping) or not isinstance(
        current_provenance, Mapping
    ):
        raise InventoryError(
            f"provenance existante invalide pour --check: {relative_path}"
        )
    # A check reproduit l'instant de génération attesté. En particulier,
    # head_sha reste le SHA stocké de cette génération, pas le HEAD courant qui
    # inclut éventuellement le commit des artefacts et créerait une boucle.
    # Le fingerprint du générateur reste toutefois courant pour détecter toute
    # dérive du code de génération.
    reused = dict(current_provenance)
    # Les versions d'outils sont dépendantes de l'environnement d'exécution.
    # On réutilise les versions enregistrées pour que --check reste stable entre
    # CI et exécutions locales hors-différence de machine.
    for field in ("generated_at_utc", "head_sha", "tool_versions"):
        reused[field] = stored_provenance.get(field)
    inventory["provenance"] = _canonicalize_mapping(reused)


def _render_managed_artifacts(
    inventory: Mapping[str, Any],
    *,
    root: Path,
    audit_root: Path,
    etat_file: Path,
    include_generated_marker: bool,
) -> dict[Path, str]:
    rendered = _render_inventory_artifacts(
        inventory,
        repo_root=root,
        audit_root=audit_root,
        include_generated_marker=include_generated_marker,
    )
    rendered[etat_file.relative_to(root)] = _render_etat_collection(
        inventory,
        marker=AUTOGEN_MARKER if include_generated_marker else "",
        root=root,
    )
    return rendered


def build_inventory_artifacts(
    repository: Path | str,
    *,
    audit_directory: str = "audit",
    etat_path: str = "ETAT_COLLECTION.md",
    include_generated_marker: bool = True,
    check_only: bool = False,
    require_clean: str | None = None,
    baseline_path: str | None = None,
) -> dict[str, Any]:
    root = Path(repository).resolve()
    _clean_path(audit_directory, role="--audit-dir", repository=root)
    _clean_path(etat_path, role="--etat-path", repository=root)
    audit_root = root / audit_directory
    etat_file = root / etat_path
    managed_output_paths = tuple(
        path.relative_to(root).as_posix()
        for path in (
            etat_file,
            audit_root / "AUDIT_CONSOLIDE.md",
            audit_root / "ECARTS_ET_CONTRADICTIONS.yaml",
            audit_root / "INVENTAIRE_COLLECTION.json",
            audit_root / "INVENTAIRE_COLLECTION.md",
            audit_root / "MATRICE_LIVRABLES.yaml",
        )
    )
    if check_only:
        _ensure_clean_tree(root, mode=require_clean)
        inventory = build_inventory(
            root,
            managed_output_paths=managed_output_paths,
            require_git_provenance=True,
        )
        _reuse_stored_generation_provenance(root, audit_root, inventory)
        rendered = _render_managed_artifacts(
            inventory,
            root=root,
            audit_root=audit_root,
            etat_file=etat_file,
            include_generated_marker=include_generated_marker,
        )
        diffs = _compare_rendered_artifacts(root, rendered)
        return {"inventory": inventory, "artifacts": rendered, "diffs": diffs}

    with _lock_generation(root) as lock_identity:
        _recover_repository_transactions(root)
        _ensure_clean_tree(
            root,
            mode=require_clean,
            allowed_generation_paths=lock_identity,
        )
        if baseline_path:
            baseline_failures = _evaluate_baseline(
                _build_inventory(
                    root,
                    managed_output_paths=managed_output_paths,
                    require_git_provenance=True,
                    owned_generation_lock=lock_identity,
                ),
                Path(baseline_path),
            )
            if baseline_failures:
                raise InventoryError(
                    "baseline invalide: " + ", ".join(baseline_failures)
                )
        inventory = _build_inventory(
            root,
            managed_output_paths=managed_output_paths,
            require_git_provenance=True,
            owned_generation_lock=lock_identity,
        )
        rendered = _render_managed_artifacts(
            inventory,
            root=root,
            audit_root=audit_root,
            etat_file=etat_file,
            include_generated_marker=include_generated_marker,
        )
        diffs = _compare_rendered_artifacts(root, rendered)
        _ensure_clean_tree(
            root,
            mode=require_clean,
            allowed_generation_paths=lock_identity,
        )
        _apply_atomic_payloads(root, rendered)
    return {
        "audit_directory": str(audit_root.relative_to(root)),
        "artifacts": {
            name: str(path.relative_to(root)) for name, path in (
                ("json", audit_root / "INVENTAIRE_COLLECTION.json"),
                ("markdown", audit_root / "INVENTAIRE_COLLECTION.md"),
                ("etat", etat_file),
                ("audit", audit_root / "AUDIT_CONSOLIDE.md"),
                ("ecarts", audit_root / "ECARTS_ET_CONTRADICTIONS.yaml"),
                ("matrice", audit_root / "MATRICE_LIVRABLES.yaml"),
            )
        },
        "diffs": diffs,
        "inventory": inventory,
    }


def _manual_name(manual_id: str) -> str:
    return {
        "1SPE": "Mathématiques Première",
        "TSPE_2026_2027": "Mathématiques Terminale",
        "1NSI": "NSI Première",
        "TNSI": "NSI Terminale",
        "TCOMPL": "Mathématiques Terminale complémentaires",
        "TEXPERTES": "Mathématiques Terminale expertes",
    }.get(manual_id, manual_id)


def _read_baseline_anomaly_summary(root: Path) -> dict[str, int]:
    try:
        payload = _load_validated_baseline(root)
    except InventoryError:
        return {}
    summary = payload.get("summary")
    if isinstance(summary, Mapping):
        return {str(k): int(v) for k, v in summary.items() if isinstance(v, int)}
    entries = payload.get("entries")
    if not isinstance(entries, list):
        return {}
    totals: dict[str, int] = {}
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        category = str(entry.get("category", ""))
        totals[category] = totals.get(category, 0) + 1
    return totals


def _anomaly_severity_rows(inventory: Mapping[str, Any]) -> list[tuple[str, int, int]]:
    rows: list[tuple[str, int, int]] = []
    for category, values in sorted(inventory["anomalies"].items()):
        if not values:
            continue
        rows.append(
            (
                category,
                len(values),
                len([item for item in values if item.get("blocking", True)]),
            )
        )
    return rows


def _markdown_table(header: tuple[str, ...], rows: list[tuple[Any, ...]]) -> str:
    if not rows:
        return "|Aucune donnée|\n|---|\n|—|"
    lines = [
        "|" + "|".join(f" {value} " for value in header) + "|",
        "|" + "|".join("---" for _ in header) + "|",
    ]
    for row in rows:
        lines.append("|" + "|".join(f" {str(cell)} " for cell in row) + "|")
    return "\n".join(lines)


def _render_inventory_markdown(
    inventory: Mapping[str, Any],
    *,
    marker: str = AUTOGEN_MARKER,
    root: Path | None = None,
) -> str:
    header = (
        "# INVENTAIRE_COLLECTION\n\n" f"{marker}\n\n" "## Synthèse par manuel\n"
    )

    lines = [header]
    manual_rows: list[tuple[Any, ...]] = []
    for manual_id in sorted(inventory["manuals"]):
        manual = inventory["manuals"][manual_id]
        manual_rows.append(
            (
                manual_id,
                _manual_name(manual_id),
                manual["subject"],
                manual["level"],
                manual["edition"],
                len(manual["chapters"]),
                manual["totals"]["capacites"],
                manual["totals"]["exercices_principaux"],
                manual["content_file_count"],
                manual["object_count"],
                ", ".join(
                    sorted(
                        scope
                        for scope, artifact in manual["compiled_variants"].items()
                        if artifact
                    )
                )
                or "—",
            )
        )
    lines.append(
        _markdown_table(
            (
                "ID",
                "Manuel",
                "Matière",
                "Niveau",
                "Édition",
                "Chapitres",
                "Capacités",
                "Exercices",
                "Fichiers contenu",
                "Objets",
                "Variantes compilées",
            ),
            manual_rows,
        )
    )
    lines.append("")

    anomaly_rows = [
        (
            category,
            len(values),
        )
        for category, values in sorted(inventory["anomalies"].items())
        if values
    ]
    if not anomaly_rows:
        lines.append("## Anomalies\nAucune anomalie détectée.\n")
    else:
        lines.append("## Anomalies détectées\n")
        lines.append(
            _markdown_table(
                ("Catégorie", "Nombre"),
                sorted(anomaly_rows, key=lambda item: (-item[1], item[0])),
            )
        )
        lines.append("")
        lines.append("### Échantillon déterministe")
        for category, values in sorted(inventory["anomalies"].items()):
            for item in values[:5]:
                lines.append(f"- {category}: {_format_anomaly(item)}")
        lines.append("")

    lines.append("## Réconciliation des rapports\n")
    claims = inventory["report_reconciliation"]["claims"]
    lines.append(f"- Assertions lues: {len(claims)}")
    lines.append(
        f"- Ouvertes: {len(inventory['report_reconciliation']['claims_non_resolues'])}"
    )
    lines.append(
        f"- Contradictoires: {len([c for c in claims if c['etat'] == 'contredit'])}"
    )
    lines.append("")

    sample = [c for c in claims if c["etat"] in {"contredit", "ouvert"}][:30]
    for claim in sample:
        lines.append(
            "- "
            + " | ".join(
                [
                    claim["path"],
                    str(claim["line"]),
                    claim["scope"],
                    claim["metric"],
                    str(claim["declared"]),
                    str(claim["calculated"]),
                    claim["etat"],
                ]
            )
        )
    lines.append("")
    return "\n".join(lines)


def _render_etat_collection(
    inventory: Mapping[str, Any],
    *,
    marker: str = AUTOGEN_MARKER,
    root: Path | None = None,
) -> str:
    release_gate = _release_strict_gate(inventory)

    lines = [
        "# ETAT COLLECTION — Nexus Réussite",
        "",
        marker,
        "",
        "## État global",
        f"- Digest source: `{inventory['source_digest']}`",
        f"- Digest modèle: `{_model_digest(inventory)}`",
        f"- Fichiers scannés: {inventory['source_file_count']}",
        f"- Gate `release-strict`: {'VERT' if release_gate['success'] else 'ROUGE'} "
        f"({release_gate['blocker_count']} bloqueurs)",
        "",
    ]
    provenance = inventory.get("provenance", {})
    if isinstance(provenance, Mapping):
        lines.extend(
            [
                "## Provenance synthétique",
                f"- SHA Git: `{provenance.get('head_sha') or 'indisponible'}`",
                f"- Branche: `{provenance.get('branch') or 'indisponible'}`",
                f"- Dépôt sale: {'oui' if provenance.get('dirty') else 'non'}",
                "",
            ]
        )
    header_rows: list[tuple[Any, ...]] = []
    for manual_id in sorted(inventory["manuals"]):
        manual = inventory["manuals"][manual_id]
        matrix = inventory["deliverable_matrix"]["manuals"][manual_id]
        header_rows.append(
            (
                _manual_name(manual_id),
                manual_id,
                len(manual["chapters"]),
                manual["content_file_count"],
                manual["object_count"],
                len(matrix["blockers"]),
                "OUI" if matrix["phase0_structural_eligible"] else "NON",
                "OUI" if matrix["publication_eligible"] else "NON",
            )
        )
    lines.append(
        _markdown_table(
            (
                "Manuel",
                "Identifiant",
                "Chapitres",
                "Fichiers contenu",
                "Objets réels",
                "Bloqueurs",
                "Structure Phase 0",
                "Publication",
            ),
            header_rows,
        )
    )
    lines.append("")
    lines.extend(
        [
            "## Détails exhaustifs",
            "Les listes complètes et leurs champs structurés restent dans les artefacts machine:",
            "- [Inventaire JSON](audit/INVENTAIRE_COLLECTION.json)",
            "- [Écarts et contradictions YAML](audit/ECARTS_ET_CONTRADICTIONS.yaml)",
            "- [Matrice des livrables YAML](audit/MATRICE_LIVRABLES.yaml)",
            "",
            "Les rapports humains détaillés restent disponibles dans "
            "[l’inventaire](audit/INVENTAIRE_COLLECTION.md) et "
            "[l’audit consolidé](audit/AUDIT_CONSOLIDE.md).",
            "",
        ]
    )

    return "\n".join(lines)


def _render_audit_consolide(
    inventory: Mapping[str, Any],
    *,
    marker: str = AUTOGEN_MARKER,
    root: Path | None = None,
) -> str:
    lines = [
        "# AUDIT_CONSOLIDE",
        "",
        marker,
        "",
        "## Vérifications de cohérence",
    ]
    for check_name in sorted(inventory["coherence_checks"]):
        check = inventory["coherence_checks"][check_name]
        status = "OK" if check["ok"] else "KO"
        lines.append(f"- {check_name} : {status}")
    lines.append("")

    lines.append("## Anomalies classées")
    for category, anomalies in sorted(inventory["anomalies"].items()):
        lines.append(f"### {category} ({len(anomalies)})")
        if not anomalies:
            lines.append("- Aucune.\n")
            continue
        for item in anomalies[:30]:
            lines.append(f"- {_format_anomaly(item)}")
        if len(anomalies) > 30:
            lines.append(f"- … {len(anomalies) - 30} autres.")
        lines.append("")

    lines.append("## Livrables")
    for manual_id in sorted(inventory["deliverable_matrix"]["manuals"]):
        matrix = inventory["deliverable_matrix"]["manuals"][manual_id]
        lines.append(f"### {_manual_name(manual_id)}")
        lines.append(f"- Éligible publication: {matrix['publication_eligible']}")
        for variant_id, variant in matrix["variants"].items():
            lines.append(
                f"- {variant_id} : {variant['state']} (artifacts={len(variant['artifacts'])})"
            )
        lines.append("")
    return "\n".join(lines)


ANOMALY_FIELD_PRIORITY = (
    "path",
    "source",
    "cible",
    "champ",
    "manual",
    "chapter",
    "id",
    "scope",
    "status",
    "reason",
    "raison",
    "field",
    "expected",
    "actual",
    "ref_capacite",
    "paths",
    "occurrences",
    "assembly_id",
    "variant",
    "normalized_status",
    "source_status",
    "index",
    "kind",
    "detail",
    "code",
)


def _sample_keys(item: Mapping[str, Any], *, limit: int = 5) -> list[str]:
    preferred = [key for key in ANOMALY_FIELD_PRIORITY if _has_report_value(item, key)]
    remaining = sorted(
        key
        for key in item
        if key not in ANOMALY_FIELD_PRIORITY and _has_report_value(item, key)
    )
    return (preferred + remaining)[:limit]


def _has_report_value(item: Mapping[str, Any], key: str) -> bool:
    value = item.get(key)
    return value is not None and value != "" and value != [] and value != {}


def _format_anomaly(item: Mapping[str, Any]) -> str:
    keys = _sample_keys(item)
    if not keys:
        return "aucun champ descriptif non nul"
    return ", ".join(f"{key}={_to_text(item[key])}" for key in keys)


def _to_text(value: Any) -> str:
    if isinstance(value, bool):
        return "oui" if value else "non"
    if isinstance(value, (Mapping, list, tuple)):
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def _render_ecarts_yaml(inventory: Mapping[str, Any], marker: bool = True) -> str:
    payload = _machine_artifact_payloads(inventory)[
        "ECARTS_ET_CONTRADICTIONS.yaml"
    ]
    serialized = yaml.safe_dump(
        _canonicalize(payload),
        allow_unicode=True,
        sort_keys=True,
        width=120,
    )
    if marker:
        return f"{AUTOGEN_MARKER}\n{serialized}"
    return serialized


def _render_matrice_livrables(inventory: Mapping[str, Any]) -> str:
    payload = _machine_artifact_payloads(inventory)["MATRICE_LIVRABLES.yaml"]
    return yaml.safe_dump(
        _canonicalize(payload),
        allow_unicode=True,
        sort_keys=True,
        width=120,
    )


def _gate_result(
    name: str,
    *,
    success: bool,
    failure_code: int,
    dimensions: Mapping[str, str] | None = None,
    reasons: Iterable[str] = (),
) -> dict[str, Any]:
    coverage = dict(GATE_DIMENSION_TEMPLATE)
    for dimension, status in (dimensions or {}).items():
        if dimension not in coverage:
            raise InventoryError(f"dimension de gate inconnue: {dimension}")
        if status not in GATE_DIMENSION_STATUSES:
            raise InventoryError(f"statut de dimension inconnu: {status}")
        coverage[dimension] = status
    sorted_reasons = sorted({str(reason) for reason in reasons if str(reason)})
    return {
        "blocker_count": len(sorted_reasons),
        "dimensions": dict(sorted(coverage.items())),
        "exit_code": 0 if success else failure_code,
        "gate": name,
        "reasons": sorted_reasons,
        "success": success,
    }


def _stable_gate_reason(reason: object, root: Path) -> str:
    return str(reason).replace(f"{root.as_posix()}/", "")


def _require_clean_gate(root: Path) -> dict[str, Any]:
    try:
        tracked_files = git_tracked_files(root)
        role_patterns, _, role_order = _collect_role_patterns(root)
        source_roles = _load_source_roles(root, tracked_files)
        reasons = [
            f"modified_tracked:{path}" for path in _git_modified_tracked(root)
        ]
        reasons.extend(
            f"untracked_relevant:{path}"
            for path in _git_relevant_untracked(
                root,
                tracked=source_roles,
                role_patterns=role_patterns,
                role_order=role_order,
            )
        )
    except (OSError, subprocess.CalledProcessError, InventoryError) as exc:
        reasons = [f"git_status_error:{_stable_gate_reason(exc, root)}"]
    return _gate_result(
        "require-clean",
        success=not reasons,
        failure_code=GATE_CLEAN_CODE,
        dimensions={"structure": "passed" if not reasons else "failed"},
        reasons=reasons,
    )


def _load_model_artifact(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    if not path.is_file():
        raise InventoryError(f"artefact absent: {relative_path}")
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise InventoryError(f"artefact illisible: {relative_path}: {exc}") from exc
    payload = _validate_output_payload(path, content, required_fields=REQUIRED_ARTIFACT_FIELDS)
    _validate_artifact_schema(payload, root=root, path=Path(relative_path))
    return payload


def _qualification_unqualified_report_failures(
    root: Path,
    policy: Mapping[str, Any],
) -> list[str]:
    failures: list[str] = []
    json_path = root / UNQUALIFIED_ANOMALIES_JSON_FILE
    markdown_path = root / UNQUALIFIED_ANOMALIES_MD_FILE
    if not json_path.is_file():
        failures.append("UNQUALIFIED_ANOMALIES.json absent")
    if not markdown_path.is_file():
        failures.append("UNQUALIFIED_ANOMALIES.md absent")
    if failures:
        return failures
    try:
        payload = _read_confined_json_mapping(
            root,
            PurePosixPath(UNQUALIFIED_ANOMALIES_JSON_FILE),
            role="unqualified anomalies",
        )
        if (
            root
            / "audit/schemas/v1/unqualified-anomalies.schema.json"
        ).is_file():
            _validate_artifact_schema(
                payload,
                root=root,
                path=Path(UNQUALIFIED_ANOMALIES_JSON_FILE),
            )
        markdown = markdown_path.read_text(encoding="utf-8")
    except (InventoryError, OSError, UnicodeError) as exc:
        return [f"rapports anomalies non qualifiées invalides:{exc}"]
    anomalies = payload.get("anomalies")
    summary = payload.get("summary")
    values = anomalies if isinstance(anomalies, list) else []
    if not isinstance(anomalies, list):
        failures.append("UNQUALIFIED_ANOMALIES.json anomalies invalide")
    if not isinstance(summary, Mapping) or summary.get(
        "unqualified"
    ) != len(values):
        failures.append("UNQUALIFIED_ANOMALIES.json compteur incohérent")
    if payload.get("policy_digest") != policy.get("control_digest"):
        failures.append("UNQUALIFIED_ANOMALIES.json policy digest différent")
    expected_markdown = (
        _baseline_qualification.render_unqualified_markdown(
            [
                value
                for value in values
                if isinstance(value, Mapping)
            ],
            policy_digest=str(policy.get("control_digest", "")),
        )
    )
    if markdown != expected_markdown:
        failures.append("UNQUALIFIED_ANOMALIES.md non canonique")
    if values:
        failures.append(f"anomalies_non_qualifiées:{len(values)}")
    return failures


def _qualification_policy_control_failures(
    root: Path,
    *,
    inventory: Mapping[str, Any] | None = None,
) -> list[str]:
    policy_path = root / BASELINE_QUALIFICATION_POLICY_FILE
    if not policy_path.is_file():
        activated = any(
            (root / relative).is_file()
            for relative in (
                UNQUALIFIED_ANOMALIES_JSON_FILE,
                UNQUALIFIED_ANOMALIES_MD_FILE,
            )
        )
        try:
            tracked = subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "ls-files",
                    "--error-unmatch",
                    "--",
                    BASELINE_QUALIFICATION_POLICY_FILE,
                ],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode == 0
        except OSError:
            tracked = False
        if activated or tracked:
            return ["policy_gate:politique absente après activation du contrat"]
        return []
    try:
        policy = _baseline_qualification.load_policy(policy_path)
        _validate_artifact_schema(
            policy,
            root=root,
            path=Path(BASELINE_QUALIFICATION_POLICY_FILE),
        )
        dispositions = _load_dispositions(root)
    except (
        InventoryError,
        OSError,
        UnicodeError,
        _baseline_qualification.QualificationError,
    ) as exc:
        return [f"policy_gate:contrôle invalide:{_stable_gate_reason(exc, root)}"]
    failures = _baseline_qualification.validate_materialized_registry(
        policy,
        dispositions,
    )
    failures.extend(
        _qualification_unqualified_report_failures(root, policy)
    )
    try:
        current_inventory = (
            inventory if inventory is not None else build_inventory(root)
        )
        active_records = _baseline_qualification_records(
            current_inventory
        )
        active = _coalesce_active_debt(
            _current_active_debt(current_inventory)
        )
    except (InventoryError, OSError, subprocess.CalledProcessError) as exc:
        failures.append(
            "couverture active non recalculable:"
            f"{_stable_gate_reason(exc, root)}"
        )
    else:
        failures.extend(
            _baseline_qualification.validate_materialized_registry(
                policy,
                dispositions,
                active_records=active_records,
            )
        )
        failures.extend(_active_debt_qualification_failures(active))
    return sorted(
        {
            f"policy_gate:{failure}"
            for failure in failures
            if failure
        }
    )


def _validate_model_gate(
    root: Path,
    *,
    today: datetime.date | None = None,
) -> dict[str, Any]:
    evaluation_date = today or datetime.datetime.now(datetime.UTC).date()
    reasons: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    reasons.extend(
        _qualification_policy_control_failures(root, inventory=None)
    )
    try:
        _load_source_roles(root, git_tracked_files(root))
        _load_dispositions(root)
    except (InventoryError, OSError, subprocess.CalledProcessError) as exc:
        reasons.append(f"contrôles_versionnés:{_stable_gate_reason(exc, root)}")
    if (root / ANOMALIES_BASELINE_FILE).is_file():
        try:
            _load_validated_baseline(root)
        except InventoryError as exc:
            reasons.append(
                "baseline_non_regression:"
                f"{_stable_gate_reason(exc, root)}"
            )
    for relative_path, expected_type in MODEL_ARTIFACTS.items():
        try:
            payload = _load_model_artifact(root, relative_path)
        except InventoryError as exc:
            reasons.append(
                f"{relative_path}:{_stable_gate_reason(exc, root)}"
            )
            continue
        payloads[relative_path] = payload
        if payload.get("artifact_type") != expected_type:
            reasons.append(
                f"{relative_path}:artifact_type attendu={expected_type} "
                f"reçu={payload.get('artifact_type')}"
            )

    inventory_payload = payloads.get("audit/INVENTAIRE_COLLECTION.json")
    if len(payloads) == len(MODEL_ARTIFACTS):
        for field in ("schema_version", "source_digest", "model_digest", "provenance"):
            values = {
                json.dumps(payload[field], ensure_ascii=False, sort_keys=True)
                for payload in payloads.values()
            }
            if len(values) != 1:
                reasons.append(f"cohérence_inter_artefacts:{field}")
    if inventory_payload is not None:
        try:
            recalculated_digest = _model_digest(inventory_payload)
        except InventoryError as exc:
            reasons.append(f"inventaire:modèle_incomplet:{exc}")
        else:
            if inventory_payload.get("model_digest") != recalculated_digest:
                reasons.append(
                    "inventaire:model_digest incohérent:"
                    f"attendu={recalculated_digest}:"
                    f"reçu={inventory_payload.get('model_digest')}"
                )
        try:
            expected_payloads = _machine_artifact_payloads(inventory_payload)
        except (InventoryError, KeyError, TypeError) as exc:
            reasons.append(f"inventaire:projections_impossibles:{exc}")
        else:
            for relative_path, payload in payloads.items():
                expected = expected_payloads.get(Path(relative_path).name)
                if expected is None:
                    continue
                if _canonicalize(payload) != _canonicalize(expected):
                    reasons.append(
                        f"{relative_path}:projection canonique incohérente"
                    )
        try:
            current_inventory = build_inventory(
                root,
                qualification_today=evaluation_date,
            )
        except (InventoryError, OSError, subprocess.CalledProcessError) as exc:
            reasons.append(f"inventaire:recalcul_impossible:{_stable_gate_reason(exc, root)}")
        else:
            for fingerprint, qualification in current_inventory.get(
                "anomaly_qualifications",
                {},
            ).items():
                if (
                    qualification.get("disposition") == "accepted_exception"
                    and qualification.get("expired") is True
                ):
                    reasons.append(
                        f"inventaire:accepted_exception_expirée:{fingerprint}"
                    )
            if inventory_payload.get("source_digest") != current_inventory["source_digest"]:
                reasons.append(
                    "inventaire:source_digest différent des sources courantes"
                )
            current_model_digest = _model_digest(current_inventory)
            if inventory_payload.get("model_digest") != current_model_digest:
                reasons.append(
                    "inventaire:model_digest différent du modèle courant"
                )
            artifact_provenance = inventory_payload.get("provenance")
            current_provenance = current_inventory.get("provenance")
            if isinstance(artifact_provenance, Mapping) and isinstance(
                current_provenance, Mapping
            ):
                for field in ("generator_files", "generator_sha256"):
                    if artifact_provenance.get(field) != current_provenance.get(field):
                        reasons.append(
                            f"inventaire:{field} différent du générateur courant"
                        )

    return _gate_result(
        "validate-model",
        success=not reasons,
        failure_code=GATE_VALIDATE_CODE,
        dimensions={"structure": "passed" if not reasons else "failed"},
        reasons=reasons,
    )


def _baseline_check_phase0_tests(root: Path) -> list[str]:
    test_path = root / "tests/test_inventory_collection.py"
    if not test_path.is_file():
        return ["suite Phase 0 absente: tests/test_inventory_collection.py"]
    try:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(test_path),
                "-q",
            ],
            cwd=root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=300,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [f"suite Phase 0 inexécutable: {exc}"]
    if completed.returncode:
        tail = " | ".join(completed.stdout.splitlines()[-3:])
        return [f"suite Phase 0 rouge: {tail}"]
    return []


def _baseline_check_artifact_schemas(root: Path) -> list[str]:
    reasons: list[str] = []
    try:
        import jsonschema
    except ImportError:
        return ["jsonschema indisponible"]
    for schema_path in sorted((root / "audit/schemas").rglob("*.json")):
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            jsonschema.Draft202012Validator.check_schema(schema)
        except (
            OSError,
            UnicodeError,
            json.JSONDecodeError,
            jsonschema.SchemaError,
        ) as exc:
            reasons.append(
                f"schéma invalide:{schema_path.relative_to(root)}:{exc}"
            )
    if not list((root / "audit/schemas").rglob("*.json")):
        reasons.append("aucun schéma versionné")
    try:
        _load_source_roles(root, git_tracked_files(root))
        _load_dispositions(root)
        for relative_path in MODEL_ARTIFACTS:
            _load_model_artifact(root, relative_path)
        if (root / ANOMALIES_BASELINE_FILE).is_file():
            _load_validated_baseline(root)
    except (InventoryError, OSError, subprocess.CalledProcessError) as exc:
        reasons.append(f"artefact/contrôle invalide:{_stable_gate_reason(exc, root)}")
    return reasons


def _baseline_check_renderers(root: Path) -> list[str]:
    result = _check_gate(
        root,
        audit_directory="audit",
        etat_path="ETAT_COLLECTION.md",
    )
    reasons = list(result["reasons"])
    for relative in (
        "ETAT_COLLECTION.md",
        "audit/AUDIT_CONSOLIDE.md",
        "audit/INVENTAIRE_COLLECTION.md",
    ):
        path = root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            reasons.append(f"renderer illisible:{relative}:{exc}")
            continue
        if "=—" in text or "id=—, detail=—, code=—" in text:
            reasons.append(f"placeholder interdit:{relative}")
        if relative == "ETAT_COLLECTION.md" and len(text.splitlines()) >= 250:
            reasons.append(
                f"ETAT_COLLECTION.md non synthétique:{len(text.splitlines())} lignes"
            )
    return reasons


def _baseline_check_object_counts(root: Path) -> list[str]:
    try:
        inventory = build_inventory(root)
        checks = validate_inventory_coherence(inventory)
    except (InventoryError, OSError, subprocess.CalledProcessError) as exc:
        return [f"compteurs non recalculables:{_stable_gate_reason(exc, root)}"]
    reasons: list[str] = []
    for name, value in sorted(checks.items()):
        if isinstance(value, Mapping) and value.get("ok") is not True:
            reasons.append(f"compteurs incohérents:{name}")
    return reasons


def _baseline_check_harvest_candidates(root: Path) -> list[str]:
    try:
        assignments = _load_source_roles(root, git_tracked_files(root))
    except (InventoryError, OSError, subprocess.CalledProcessError) as exc:
        return [f"classification indisponible:{_stable_gate_reason(exc, root)}"]
    candidates = sorted(
        path
        for path in assignments
        if _is_intrinsic_harvest_candidate(path)
    )
    reasons: list[str] = []
    if len(candidates) != 19:
        reasons.append(f"candidats _harvest attendus=19 observés={len(candidates)}")
    invalid = [
        path
        for path in candidates
        if assignments.get(path) != "harvest_candidate"
    ]
    reasons.extend(
        f"candidat mal classé:{path}={assignments.get(path)}"
        for path in invalid
    )
    return reasons


def _baseline_check_generated_renvois(root: Path) -> list[str]:
    target = "Mathematiques/manuel-maths/build/maquette-v5/renvois.tex"
    try:
        assignments = _load_source_roles(root, git_tracked_files(root))
        dispositions = _load_dispositions(root)
    except (InventoryError, OSError, subprocess.CalledProcessError) as exc:
        return [f"preuve renvois indisponible:{_stable_gate_reason(exc, root)}"]
    reasons: list[str] = []
    role_patterns, default_role, role_order = _collect_role_patterns(root)
    role = _classify_source_path(
        target,
        assignments,
        default=default_role,
        role_patterns=role_patterns,
        role_order=role_order,
    )
    if role != "generated_dependency":
        reasons.append(f"renvois.tex={role} (attendu generated_dependency)")
    qualified = [
        value
        for value in dispositions.values()
        if value.get("disposition") == "generated_dependency"
        and isinstance(value.get("proof"), (str, Mapping))
        and target
        in json.dumps(value.get("proof"), ensure_ascii=False, sort_keys=True)
    ]
    if len(qualified) != 1:
        reasons.append(
            f"preuve generated_dependency renvois attendue=1 observée={len(qualified)}"
        )
    return reasons


def _baseline_check_intentional_reuse_decisions(root: Path) -> list[str]:
    try:
        dispositions = _load_dispositions(root)
    except InventoryError as exc:
        return [f"dispositions invalides:{_stable_gate_reason(exc, root)}"]
    records = [
        value
        for value in dispositions.values()
        if value.get("disposition") == "intentional_reuse"
    ]
    reasons: list[str] = []
    expected_ids = {
        "1SPE-DERLOCAL-EX-001",
        "1SPE-DERLOCAL-EX-002",
        "1SPE-DERLOCAL-EX-005",
    }
    observed_ids = {
        str(value.get("proof", {}).get("object_id", ""))
        for value in records
        if isinstance(value.get("proof"), Mapping)
    }
    if observed_ids != expected_ids:
        reasons.append(
            "réutilisations intentionnelles non prouvées:"
            f"attendu={sorted(expected_ids)} observé={sorted(observed_ids)}"
        )
    for record in records:
        if not all(
            isinstance(record.get(field), str) and record[field].strip()
            for field in ("approved_by", "decision_ref", "justification")
        ) or not isinstance(record.get("proof"), (str, Mapping)):
            reasons.append(
                "réutilisation sans preuve/décision:"
                f"{record.get('fingerprint', '')}"
            )
    return reasons


def _baseline_check_disposition_coverage(root: Path) -> list[str]:
    try:
        inventory = build_inventory(root)
        dispositions = _load_dispositions(root)
        active = _current_active_debt(inventory)
    except (InventoryError, OSError, subprocess.CalledProcessError) as exc:
        return [f"couverture non recalculable:{_stable_gate_reason(exc, root)}"]
    reasons = _active_debt_qualification_failures(
        _coalesce_active_debt(active)
    )
    reasons.extend(
        _qualification_policy_control_failures(
            root,
            inventory=inventory,
        )
    )
    for fingerprint, record in sorted(dispositions.items()):
        if record.get("disposition") == "false_positive" and (
            not isinstance(record.get("justification"), str)
            or not record["justification"].strip()
            or not isinstance(record.get("proof"), (str, Mapping))
        ):
            reasons.append(
                f"faux positif non prouvé:{fingerprint}"
            )
    return reasons


def _baseline_check_fingerprint_determinism(root: Path) -> list[str]:
    try:
        first = build_inventory(root)
        second = build_inventory(root)
        first_active = _current_active_debt(first)
        second_active = _current_active_debt(second)
    except (InventoryError, OSError, subprocess.CalledProcessError) as exc:
        return [f"fingerprints non recalculables:{_stable_gate_reason(exc, root)}"]
    reasons: list[str] = []
    if FINGERPRINT_SCHEMA_VERSION != 1:
        reasons.append(
            f"fingerprint_schema_version non supportée:{FINGERPRINT_SCHEMA_VERSION}"
        )
    if first_active != second_active:
        reasons.append("recalcul de fingerprints non déterministe")
    return reasons


def _run_baseline_readiness_check(
    root: Path,
    name: str,
) -> dict[str, Any]:
    checkers = {
        "phase0_tests": _baseline_check_phase0_tests,
        "artifact_schemas": _baseline_check_artifact_schemas,
        "renderers": _baseline_check_renderers,
        "object_counts": _baseline_check_object_counts,
        "harvest_candidates": _baseline_check_harvest_candidates,
        "generated_renvois": _baseline_check_generated_renvois,
        "intentional_reuse_decisions": _baseline_check_intentional_reuse_decisions,
        "disposition_coverage": _baseline_check_disposition_coverage,
        "fingerprint_determinism": _baseline_check_fingerprint_determinism,
        "validate_model": lambda repository: list(
            _validate_model_gate(repository)["reasons"]
        ),
    }
    if name not in checkers:
        raise InventoryError(f"check baseline_ready inconnu: {name}")
    reasons = sorted(
        {
            str(reason)
            for reason in checkers[name](root)
            if str(reason)
        }
    )
    return {
        "name": name,
        "reasons": reasons,
        "success": not reasons,
    }


def _baseline_ready_gate(
    root: Path,
    *,
    override_checks: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    overrides = override_checks or {}
    checks = [
        dict(overrides[name])
        if name in overrides
        else _run_baseline_readiness_check(root, name)
        for name in BASELINE_READY_CHECK_NAMES
    ]
    reasons = [
        reason
        for check in checks
        for reason in check["reasons"]
    ]
    result = _gate_result(
        "baseline-ready",
        success=not reasons,
        failure_code=GATE_BASELINE_UPDATE_CODE,
        dimensions={"structure": "passed" if not reasons else "failed"},
        reasons=reasons,
    )
    result["checks"] = checks
    return result


def _check_gate(root: Path, *, audit_directory: str, etat_path: str) -> dict[str, Any]:
    try:
        result = build_inventory_artifacts(
            root,
            audit_directory=audit_directory,
            etat_path=etat_path,
            check_only=True,
        )
        reasons = [
            _stable_gate_reason(reason, root) for reason in result["diffs"]
        ]
    except (InventoryError, OSError, subprocess.CalledProcessError) as exc:
        reasons = [f"check_error:{_stable_gate_reason(exc, root)}"]
    return _gate_result(
        "check",
        success=not reasons,
        failure_code=GATE_CHECK_CODE,
        dimensions={"structure": "passed" if not reasons else "failed"},
        reasons=reasons,
    )


def _fail_on_new_gate(root: Path) -> dict[str, Any]:
    comparison: dict[str, Any] | None = None
    try:
        baseline = _load_validated_baseline(root)
        if baseline.get("provisional") is True:
            reasons = [
                "baseline provisoire: comparaison de dette non obligatoire"
            ]
        else:
            inventory = build_inventory(root)
            comparison = _compare_anomaly_debt(
                _current_active_debt(inventory),
                baseline.get("active", []),
                baseline.get("resolved", []),
            )
            reasons = list(comparison["failures"])
    except (InventoryError, OSError, subprocess.CalledProcessError) as exc:
        reasons = [
            "comparaison fingerprint-v1 impossible:"
            f"{_stable_gate_reason(exc, root)}"
        ]
    result = _gate_result(
        "fail-on-new",
        success=not reasons,
        failure_code=GATE_BASELINE_CODE,
        dimensions={"structure": "passed" if not reasons else "failed"},
        reasons=reasons,
    )
    if comparison is not None:
        result["comparison"] = comparison
    return result


def _baseline_payload_digest(payload: Mapping[str, Any]) -> str:
    normalized = _canonicalize(dict(payload))
    updates = normalized.get("updates")
    if isinstance(updates, list) and updates:
        last_update = updates[-1]
        if (
            isinstance(last_update, dict)
            and "new_baseline_digest" in last_update
        ):
            last_update["new_baseline_digest"] = "sha256:" + "0" * 64
    serialized = json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"sha256:{hashlib.sha256(_utf8_bytes(serialized)).hexdigest()}"


def _resolved_entry(
    active: Mapping[str, Any],
    *,
    timestamp: str,
    git_sha: str,
) -> dict[str, Any]:
    return {
        "blocking": False,
        "category": str(active.get("category", "unknown")),
        "disposition": "fixed",
        "fingerprint": str(active["fingerprint"]),
        "resolved_at": timestamp,
        "resolved_git_sha": git_sha,
    }


def _render_baseline_update_report(
    *,
    approved_by: str,
    comparison: Mapping[str, Any],
    git_sha: str,
    new_digest: str,
    previous_digest: str | None,
    reason: str,
    readiness: Mapping[str, Any],
    timestamp: str,
) -> str:
    lines = [
        "<!-- AUTO-GENÉRÉ PAR inventory_collection.py -->",
        "# Mise à jour de la baseline d’anomalies",
        "",
        f"- Date : `{timestamp}`",
        f"- Approbateur : {approved_by}",
        f"- Raison : {reason}",
        f"- SHA Git : `{git_sha}`",
        f"- Empreinte précédente : `{previous_digest or 'aucune'}`",
        f"- Nouvelle empreinte : `{new_digest}`",
        "",
        "## Transition",
        "",
    ]
    for key in (
        "new",
        "unchanged",
        "resolved",
        "regressions",
    ):
        values = comparison.get(key, [])
        lines.append(f"- {key} : {len(values) if isinstance(values, list) else 0}")
        if isinstance(values, list):
            lines.extend(f"  - `{value}`" for value in values)
    modified = comparison.get("modified", [])
    lines.append(
        f"- modified : {len(modified) if isinstance(modified, list) else 0}"
    )
    if isinstance(modified, list):
        for value in modified:
            if isinstance(value, Mapping):
                lines.append(
                    "  - "
                    f"`{value.get('previous', '')}` → "
                    f"`{value.get('current', '')}`"
                )
    lines.extend(["", "## Préconditions baseline_ready", ""])
    for check in readiness.get("checks", []):
        if not isinstance(check, Mapping):
            continue
        status = "VERT" if check.get("success") is True else "ROUGE"
        lines.append(f"- {check.get('name', 'inconnu')} : {status}")
        bypass = check.get("bootstrap_bypass")
        if isinstance(bypass, str) and bypass:
            lines.append(f"  - bootstrap : {bypass}")
    return "\n".join(lines) + "\n"


def _freeze_report_count_table(
    title: str,
    values: Mapping[str, int],
) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| Valeur | Nombre |",
        "|---|---:|",
    ]
    lines.extend(
        f"| `{key}` | {values[key]} |" for key in sorted(values)
    )
    return lines + [""]


def _render_baseline_freeze_report(
    *,
    approved_by: str,
    dispositions: Mapping[str, Mapping[str, Any]],
    git_sha: str,
    new_digest: str,
    payload: Mapping[str, Any],
    previous_digest: str | None,
    reason: str,
    timestamp: str,
) -> str:
    raw_active = payload.get("active", [])
    active = [
        dict(entry)
        for entry in raw_active
        if isinstance(entry, Mapping)
    ] if isinstance(raw_active, list) else []
    active_fingerprints = {
        str(entry.get("fingerprint", "")) for entry in active
    }
    policy_fingerprints = {
        str(fingerprint)
        for fingerprint, record in dispositions.items()
        if (
            fingerprint in active_fingerprints
            and isinstance(record.get("qualification_policy_digest"), str)
            and bool(record["qualification_policy_digest"])
        )
    }
    policy_entries = [
        entry
        for entry in active
        if str(entry.get("fingerprint", "")) in policy_fingerprints
    ]
    category_counts = Counter(
        str(entry.get("category", "unknown")) for entry in active
    )
    disposition_counts = Counter(
        str(entry.get("disposition", "unknown")) for entry in active
    )
    owner_counts = Counter(
        str(entry.get("owner", "unknown")) for entry in active
    )
    policy_owner_counts = Counter(
        str(entry.get("owner", "unknown")) for entry in policy_entries
    )
    blocking_counts = {
        "Bloquantes": sum(
            1 for entry in active if entry.get("blocking") is True
        ),
        "Non bloquantes": sum(
            1 for entry in active if entry.get("blocking") is not True
        ),
    }
    unqualified_count = sum(
        1 for entry in active if entry.get("qualified") is not True
    )
    lines = [
        "<!-- AUTO-GENÉRÉ PAR inventory_collection.py -->",
        "# Rapport de gel de la baseline de non-régression",
        "",
        f"- Date : `{timestamp}`",
        f"- SHA Git : `{git_sha}`",
        f"- Approbateur : {approved_by}",
        f"- Raison du gel : {reason}",
        "- baseline_purpose: `debt_regression_control`",
        "- release_acceptance: `false`",
        f"- Empreinte précédente : `{previous_digest or 'aucune'}`",
        f"- Nouvelle empreinte : `{new_digest}`",
        f"- Fingerprints actifs : `{len(active)}`",
        (
            "- Anomalies qualifiées par la politique : "
            f"`{len(policy_entries)}`"
        ),
        f"- Anomalies non qualifiées : `{unqualified_count}`",
        "",
    ]
    lines.extend(
        _freeze_report_count_table(
            "Décompte par catégorie",
            category_counts,
        )
    )
    lines.extend(
        _freeze_report_count_table(
            "Décompte par disposition",
            disposition_counts,
        )
    )
    lines.extend(
        _freeze_report_count_table(
            "Décompte par propriétaire — registre complet",
            owner_counts,
        )
    )
    lines.extend(
        _freeze_report_count_table(
            "Décompte par propriétaire — lot politique",
            policy_owner_counts,
        )
    )
    lines.extend(
        _freeze_report_count_table(
            "Caractère bloquant",
            blocking_counts,
        )
    )
    return "\n".join(lines).rstrip() + "\n"


def _update_baseline_gate(
    root: Path,
    *,
    reason: str,
    approved_by: str,
    allow_qualification_digest_bootstrap: bool = False,
    allow_approved_baseline_extension: bool = False,
) -> dict[str, Any]:
    reasons: list[str] = []
    if os.environ.get("CI"):
        reasons.append("mise à jour de baseline interdite en CI")
    if not isinstance(reason, str) or not reason.strip():
        reasons.append("justification non vide requise")
    if not isinstance(approved_by, str) or not approved_by.strip():
        reasons.append("approbateur non vide requis")
    if (
        allow_qualification_digest_bootstrap
        and allow_approved_baseline_extension
    ):
        reasons.append("les deux dérogations de baseline sont incompatibles")
    if reasons:
        return _gate_result(
            "update-baseline",
            success=False,
            failure_code=GATE_BASELINE_UPDATE_CODE,
            dimensions={"structure": "failed"},
            reasons=reasons,
        )

    with _lock_generation(root):
        _recover_repository_transactions(root)
    clean = _require_clean_gate(root)
    if not clean["success"]:
        return _gate_result(
            "update-baseline",
            success=False,
            failure_code=GATE_BASELINE_UPDATE_CODE,
            dimensions={"structure": "failed"},
            reasons=[
                "dépôt propre requis: " + value
                for value in clean["reasons"]
            ],
        )
    model = _validate_model_gate(root)
    if not model["success"]:
        return _gate_result(
            "update-baseline",
            success=False,
            failure_code=GATE_BASELINE_UPDATE_CODE,
            dimensions={"structure": "failed"},
            reasons=[
                "modèle invalide: " + value
                for value in model["reasons"]
            ],
        )
    try:
        validated_baseline = _load_validated_baseline(root)
    except InventoryError as exc:
        return _gate_result(
            "update-baseline",
            success=False,
            failure_code=GATE_BASELINE_UPDATE_CODE,
            dimensions={"structure": "failed"},
            reasons=[
                "baseline invalide: " + _stable_gate_reason(exc, root)
            ],
        )
    validated_baseline_digest = _baseline_payload_digest(
        validated_baseline
    )
    validated_head = _repo_head_sha(root, required=True)
    override_checks: dict[str, dict[str, Any]] = {}
    if (
        allow_qualification_digest_bootstrap
        and validated_baseline.get("provisional") is not True
    ):
        try:
            probe_inventory = build_inventory(root)
            probe_current_active = _current_active_debt(probe_inventory)
        except (
            InventoryError,
            OSError,
            subprocess.CalledProcessError,
        ) as exc:
            return _gate_result(
                "update-baseline",
                success=False,
                failure_code=GATE_BASELINE_UPDATE_CODE,
                dimensions={"structure": "failed"},
                reasons=[
                    "bootstrap_digest_realignment: inventaire indisponible:"
                    f"{_stable_gate_reason(exc, root)}"
                ],
            )
        probe_old_active = validated_baseline.get("active", [])
        probe_old_resolved = validated_baseline.get("resolved", [])
        probe_comparison = _compare_anomaly_debt(
            probe_current_active,
            probe_old_active,
            probe_old_resolved,
        )
        if probe_comparison["failures"]:
            pure, offending = _qualification_digest_bootstrap_diagnosis(
                probe_current_active,
                probe_old_active,
                probe_comparison,
            )
            if not pure:
                return _gate_result(
                    "update-baseline",
                    success=False,
                    failure_code=GATE_BASELINE_UPDATE_CODE,
                    dimensions={"structure": "failed"},
                    reasons=[
                        "bootstrap_digest_realignment refusé: dérive non "
                        "exclusivement liée à qualification_digest"
                    ]
                    + [
                        f"bootstrap_digest_realignment:{value}"
                        for value in offending
                    ],
                )
            override_checks["phase0_tests"] = {
                "name": "phase0_tests",
                "reasons": [],
                "success": True,
                "bootstrap_bypass": (
                    "qualification_digest_bootstrap: dérive fail-on-new "
                    "vérifiée structurellement comme exclusivement "
                    "constituée de qualification_digest (mêmes "
                    "fingerprints, catégories, owners, dispositions, "
                    "sévérités)"
                ),
            }
    if (
        allow_approved_baseline_extension
        and validated_baseline.get("provisional") is not True
    ):
        try:
            probe_inventory = build_inventory(root)
            probe_current_active = _current_active_debt(probe_inventory)
        except (
            InventoryError,
            OSError,
            subprocess.CalledProcessError,
        ) as exc:
            return _gate_result(
                "update-baseline",
                success=False,
                failure_code=GATE_BASELINE_UPDATE_CODE,
                dimensions={"structure": "failed"},
                reasons=[
                    "approved_baseline_extension: inventaire indisponible:"
                    f"{_stable_gate_reason(exc, root)}"
                ],
            )
        probe_old_active = validated_baseline.get("active", [])
        probe_old_resolved = validated_baseline.get("resolved", [])
        probe_comparison = _compare_anomaly_debt(
            probe_current_active,
            probe_old_active,
            probe_old_resolved,
        )
        if probe_comparison["failures"]:
            approved, offending = _approved_baseline_extension_diagnosis(
                root,
                probe_current_active,
                validated_baseline,
                probe_comparison,
                approved_by=approved_by,
            )
            if not approved:
                return _gate_result(
                    "update-baseline",
                    success=False,
                    failure_code=GATE_BASELINE_UPDATE_CODE,
                    dimensions={"structure": "failed"},
                    reasons=[
                        "approved_baseline_extension refusée: dérive hors "
                        "du jeu explicitement approuvé"
                    ]
                    + [
                        f"approved_baseline_extension:{value}"
                        for value in offending
                    ],
                )
            override_checks["phase0_tests"] = {
                "name": "phase0_tests",
                "reasons": [],
                "success": True,
                "approved_extension_bypass": (
                    "extension vérifiée comme exclusivement constituée du "
                    "jeu de fingerprints approuvé, tous open_debt et "
                    "release_acceptance=false"
                ),
            }
    readiness = (
        _baseline_ready_gate(root, override_checks=override_checks)
        if override_checks
        else _baseline_ready_gate(root)
    )
    if not readiness["success"]:
        result = _gate_result(
            "update-baseline",
            success=False,
            failure_code=GATE_BASELINE_UPDATE_CODE,
            dimensions={"structure": "failed"},
            reasons=[
                "baseline_ready: " + value
                for value in readiness["reasons"]
            ],
        )
        result["checks"] = readiness["checks"]
        return result

    with _lock_generation(root) as lock_identity:
        _ensure_clean_tree(
            root,
            mode="head",
            allowed_generation_paths=lock_identity,
        )
        inventory = _build_inventory(
            root,
            require_git_provenance=True,
            owned_generation_lock=lock_identity,
        )
        provenance = inventory.get("provenance")
        if not isinstance(provenance, Mapping):
            raise InventoryError(
                "provenance absente pendant la mise à jour de baseline"
            )
        git_sha = provenance.get("head_sha")
        timestamp = provenance.get("generated_at_utc")
        if (
            not isinstance(git_sha, str)
            or not re.fullmatch(r"[0-9a-f]{40}", git_sha)
            or not isinstance(timestamp, str)
            or not timestamp
        ):
            raise InventoryError(
                "provenance Git incohérente pendant la mise à jour de baseline"
            )
        if git_sha != validated_head:
            raise InventoryError(
                "HEAD modifié pendant la construction de la provenance"
            )
        current_active = _current_active_debt(inventory)
        old_payload = _load_validated_baseline(root)
        if _baseline_payload_digest(old_payload) != validated_baseline_digest:
            raise InventoryError(
                "baseline modifiée pendant les préconditions"
            )
        if _repo_head_sha(root, required=True) != validated_head:
            raise InventoryError(
                "HEAD modifié pendant les préconditions"
            )
        old_active = (
            old_payload.get("active", [])
            if isinstance(old_payload, Mapping)
            and isinstance(old_payload.get("active"), list)
            else []
        )
        old_resolved = (
            old_payload.get("resolved", [])
            if isinstance(old_payload, Mapping)
            and isinstance(old_payload.get("resolved"), list)
            else []
        )
        comparison = _compare_anomaly_debt(
            current_active,
            old_active,
            old_resolved,
        )
        if allow_qualification_digest_bootstrap and comparison["failures"]:
            pure, offending = _qualification_digest_bootstrap_diagnosis(
                current_active,
                old_active,
                comparison,
            )
            if not pure:
                raise InventoryError(
                    "bootstrap_digest_realignment refusé pendant "
                    "l'écriture: dérive non exclusivement liée à "
                    "qualification_digest (" + "; ".join(offending[:5]) + ")"
                )
        if allow_approved_baseline_extension and comparison["failures"]:
            approved, offending = _approved_baseline_extension_diagnosis(
                root,
                current_active,
                old_payload,
                comparison,
                approved_by=approved_by,
            )
            if not approved:
                raise InventoryError(
                    "approved_baseline_extension refusée pendant l'écriture: "
                    + "; ".join(offending[:5])
                )
        resolved_by_fingerprint = {
            str(entry.get("fingerprint", "")): dict(entry)
            for entry in old_resolved
            if isinstance(entry, Mapping) and entry.get("fingerprint")
        }
        old_active_by_fingerprint = {
            str(entry.get("fingerprint", "")): entry
            for entry in old_active
            if isinstance(entry, Mapping) and entry.get("fingerprint")
        }
        newly_resolved = list(comparison["resolved"]) + [
            str(value["previous"])
            for value in comparison["modified"]
            if isinstance(value, Mapping) and value.get("previous")
        ]
        for fingerprint in sorted(set(newly_resolved)):
            previous_entry = old_active_by_fingerprint.get(fingerprint)
            if previous_entry is not None:
                resolved_by_fingerprint.setdefault(
                    fingerprint,
                    _resolved_entry(
                        previous_entry,
                        timestamp=timestamp,
                        git_sha=git_sha,
                    ),
                )
        previous_digest = (
            _baseline_payload_digest(old_payload)
            if isinstance(old_payload, Mapping)
            else None
        )
        updates = (
            [
                dict(value)
                for value in old_payload.get("updates", [])
                if isinstance(value, Mapping)
            ]
            if isinstance(old_payload, Mapping)
            and isinstance(old_payload.get("updates"), list)
            else []
        )
        payload: dict[str, Any] = {
            "active": current_active,
            "artifact_type": "anomalies_baseline",
            "baseline_purpose": "debt_regression_control",
            "fingerprint_schema_version": FINGERPRINT_SCHEMA_VERSION,
            "generated_at_utc": timestamp,
            "generated_by": "inventory_collection.py",
            "git_sha": git_sha,
            "model_digest": _model_digest(inventory),
            "previous_baseline_digest": previous_digest,
            "provenance": inventory["provenance"],
            "provisional": False,
            "release_acceptance": False,
            "resolved": [
                resolved_by_fingerprint[fingerprint]
                for fingerprint in sorted(resolved_by_fingerprint)
            ],
            "schema_ref": (
                "audit/schemas/v1/anomalies-baseline.schema.json"
            ),
            "schema_version": SCHEMA_VERSION,
            "source_digest": inventory["source_digest"],
            "summary": {
                "active": len(current_active),
                "resolved": len(resolved_by_fingerprint),
            },
            "updates": updates,
        }
        update = {
            "approved_by": approved_by.strip(),
            "git_sha": git_sha,
            "new_baseline_digest": "sha256:" + "0" * 64,
            "previous_baseline_digest": previous_digest,
            "reason": reason.strip(),
            "timestamp": timestamp,
        }
        payload["updates"].append(update)
        new_digest = _baseline_payload_digest(payload)
        update["new_baseline_digest"] = new_digest
        _validate_artifact_schema(
            payload,
            root=root,
            path=Path(ANOMALIES_BASELINE_FILE),
        )
        report = _render_baseline_update_report(
            approved_by=approved_by.strip(),
            comparison=comparison,
            git_sha=git_sha,
            new_digest=new_digest,
            previous_digest=previous_digest,
            reason=reason.strip(),
            readiness=readiness,
            timestamp=timestamp,
        )
        dispositions = _load_dispositions(root)
        freeze_report = _render_baseline_freeze_report(
            approved_by=approved_by.strip(),
            dispositions=dispositions,
            git_sha=git_sha,
            new_digest=new_digest,
            payload=payload,
            previous_digest=previous_digest,
            reason=reason.strip(),
            timestamp=timestamp,
        )
        _ensure_clean_tree(
            root,
            mode="head",
            allowed_generation_paths=lock_identity,
        )

        def require_unchanged_head() -> None:
            if _repo_head_sha(root, required=True) != git_sha:
                raise InventoryError(
                    "HEAD modifié avant l'écriture de la baseline"
                )

        require_unchanged_head()
        _apply_atomic_payloads(
            root,
            {
                root / ANOMALIES_BASELINE_FILE: (
                    json.dumps(
                        payload,
                        ensure_ascii=False,
                        indent=2,
                        sort_keys=True,
                    )
                    + "\n"
                ),
                root / BASELINE_UPDATE_REPORT_FILE: report,
                root / BASELINE_FREEZE_REPORT_FILE: freeze_report,
            },
            validate_state=require_unchanged_head,
        )

    result = _gate_result(
        "update-baseline",
        success=True,
        failure_code=GATE_BASELINE_UPDATE_CODE,
        dimensions={"structure": "passed"},
        reasons=[],
    )
    result["checks"] = readiness["checks"]
    result["comparison"] = comparison
    result["new_baseline_digest"] = new_digest
    result["previous_baseline_digest"] = previous_digest
    return result


def _safe_update_baseline_gate(
    root: Path,
    *,
    reason: str,
    approved_by: str,
    allow_qualification_digest_bootstrap: bool = False,
    allow_approved_baseline_extension: bool = False,
) -> dict[str, Any]:
    try:
        return _update_baseline_gate(
            root,
            reason=reason,
            approved_by=approved_by,
            allow_qualification_digest_bootstrap=(
                allow_qualification_digest_bootstrap
            ),
            allow_approved_baseline_extension=(
                allow_approved_baseline_extension
            ),
        )
    except (
        InventoryError,
        OSError,
        subprocess.CalledProcessError,
    ) as exc:
        return _gate_result(
            "update-baseline",
            success=False,
            failure_code=GATE_BASELINE_UPDATE_CODE,
            dimensions={"structure": "failed"},
            reasons=[f"update_error:{_stable_gate_reason(exc, root)}"],
        )


def _baseline_materialization_plan(
    root: Path,
    *,
    owned_generation_lock: Mapping[str, tuple[int, int]] | None = None,
) -> dict[str, Any]:
    policy = _baseline_qualification.load_policy(
        root / BASELINE_QUALIFICATION_POLICY_FILE
    )
    _validate_artifact_schema(
        policy,
        root=root,
        path=Path(BASELINE_QUALIFICATION_POLICY_FILE),
    )
    inventory = _build_inventory(
        root,
        owned_generation_lock=owned_generation_lock,
    )
    plan = _baseline_qualification.plan_materialization(
        policy,
        _baseline_qualification_records(inventory),
        _load_dispositions(root),
        observed_source_digest=str(inventory["source_digest"]),
        observed_model_digest=_model_digest(inventory),
        allow_unqualified=True,
    )
    dispositions = plan["dispositions_payload"]
    unqualified = plan["unqualified_json"]
    _validate_artifact_schema(
        dispositions,
        root=root,
        path=Path(ANOMALY_DISPOSITIONS_FILE),
    )
    _validate_artifact_schema(
        unqualified,
        root=root,
        path=Path(UNQUALIFIED_ANOMALIES_JSON_FILE),
    )
    rendered = {
        Path(UNQUALIFIED_ANOMALIES_JSON_FILE): (
            json.dumps(
                unqualified,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ),
        Path(UNQUALIFIED_ANOMALIES_MD_FILE): plan[
            "unqualified_markdown"
        ],
    }
    if not plan["unqualified"]:
        rendered[Path(ANOMALY_DISPOSITIONS_FILE)] = yaml.safe_dump(
            dispositions,
            allow_unicode=True,
            sort_keys=True,
        )
    plan["rendered"] = rendered
    plan["policy_file_digest"] = _sha256_file(
        root / BASELINE_QUALIFICATION_POLICY_FILE
    )
    disposition_path = root / ANOMALY_DISPOSITIONS_FILE
    plan["dispositions_file_digest"] = (
        _sha256_file(disposition_path)
        if disposition_path.is_file()
        else None
    )
    return plan


def _materialization_plan_identity(plan: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: _canonicalize(plan.get(key))
        for key in (
            "approved_fingerprint_count",
            "approved_fingerprint_digest",
            "dispositions_file_digest",
            "observed_model_digest",
            "observed_source_digest",
            "owner_counts",
            "policy_file_digest",
            "rendered",
            "unqualified",
        )
    }


def _validate_materialization_destinations(
    root: Path,
    rendered: Mapping[Path, str],
) -> None:
    for relative in rendered:
        target = root / relative
        try:
            metadata = target.lstat()
        except FileNotFoundError:
            continue
        if (
            not stat.S_ISREG(metadata.st_mode)
            or metadata.st_nlink != 1
        ):
            raise InventoryError(
                "materialization destination must be a regular file "
                f"without symlink or hardlink: {relative}"
            )


def _materialize_baseline_qualifications(
    root: Path,
    *,
    check_only: bool,
) -> dict[str, Any]:
    initial_head = _repo_head_sha(root, required=True)
    plan = _baseline_materialization_plan(root)
    rendered = plan["rendered"]
    _validate_materialization_destinations(root, rendered)
    diffs = _compare_rendered_artifacts(root, rendered)

    def revalidate_plan(
        *,
        owned_generation_lock: Mapping[str, tuple[int, int]] | None = None,
    ) -> None:
        if _repo_head_sha(root, required=True) != initial_head:
            raise InventoryError(
                "HEAD modifié pendant la validation de matérialisation"
            )
        revalidated = _baseline_materialization_plan(
            root,
            owned_generation_lock=owned_generation_lock,
        )
        if _materialization_plan_identity(
            revalidated
        ) != _materialization_plan_identity(plan):
            raise InventoryError(
                "jeu approuvé ou digests modifiés avant matérialisation"
            )
        _validate_materialization_destinations(
            root,
            revalidated["rendered"],
        )

    if check_only:
        revalidate_plan()
        success = not diffs and not plan["unqualified"]
        reasons: list[str] = []
        if diffs:
            reasons.append("matérialisation requise")
        if plan["unqualified"]:
            reasons.append(
                f"anomalies_non_qualifiées:{len(plan['unqualified'])}"
            )
        result = _gate_result(
            "materialize-baseline-qualifications",
            success=success,
            failure_code=GATE_CHECK_CODE,
            dimensions={"structure": "passed" if success else "failed"},
            reasons=reasons,
        )
    else:
        with _lock_generation(root) as lock_identity:
            _recover_repository_transactions(root)
            revalidate_plan(owned_generation_lock=lock_identity)

            def require_unchanged_head() -> None:
                if _repo_head_sha(root, required=True) != initial_head:
                    raise InventoryError(
                        "HEAD modifié pendant la matérialisation"
                    )

            _apply_atomic_payloads(
                root,
                rendered,
                validate_before_apply=lambda transaction_identity: revalidate_plan(
                    owned_generation_lock={
                        **lock_identity,
                        **transaction_identity,
                    }
                ),
                validate_state=require_unchanged_head,
            )
        success = not plan["unqualified"]
        result = _gate_result(
            "materialize-baseline-qualifications",
            success=success,
            failure_code=GATE_CHECK_CODE,
            dimensions={"structure": "passed" if success else "failed"},
            reasons=(
                []
                if success
                else [
                    f"anomalies_non_qualifiées:{len(plan['unqualified'])}; "
                    "registre dispositions inchangé"
                ]
            ),
        )
    result["approved_fingerprint_count"] = plan[
        "approved_fingerprint_count"
    ]
    result["approved_fingerprint_digest"] = plan[
        "approved_fingerprint_digest"
    ]
    result["diffs"] = [
        reason.split(": ", 1)[1] if ": " in reason else reason
        for reason in diffs
    ]
    result["owner_counts"] = plan["owner_counts"]
    result["unqualified"] = len(plan["unqualified"])
    return result


def _safe_materialize_baseline_qualifications(
    root: Path,
    *,
    check_only: bool,
) -> dict[str, Any]:
    try:
        return _materialize_baseline_qualifications(
            root,
            check_only=check_only,
        )
    except (
        InventoryError,
        OSError,
        subprocess.CalledProcessError,
        _baseline_qualification.QualificationError,
    ) as exc:
        return _gate_result(
            "materialize-baseline-qualifications",
            success=False,
            failure_code=GATE_CHECK_CODE,
            dimensions={"structure": "failed"},
            reasons=[_stable_gate_reason(exc, root)],
        )


def _release_strict_gate(inventory: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    matrix = inventory["deliverable_matrix"]["manuals"]
    observed_coverage = inventory.get("observed_build_coverage", {})
    observed_integration = inventory.get("observed_build_integration")
    integration_ready = (
        isinstance(observed_integration, Mapping)
        and observed_integration.get("status") == "integrated"
    )
    if not integration_ready:
        reasons.append("build_receipt_producteurs_non_intégrés")
    for manual_id, manual in sorted(matrix.items()):
        for blocker in manual["blockers"]:
            reasons.append(
                f"{manual_id}:{blocker['code']}:"
                f"{blocker['source']}:{blocker['detail']}"
            )
        manual_coverage = (
            observed_coverage.get(manual_id, {})
            if isinstance(observed_coverage, Mapping)
            else {}
        )
        variant_coverage = (
            manual_coverage.get("variants", {})
            if isinstance(manual_coverage, Mapping)
            else {}
        )
        for variant in sorted(manual["variants"]):
            coverage = (
                variant_coverage.get(variant, {})
                if isinstance(variant_coverage, Mapping)
                else {}
            )
            if not coverage.get("declared_variants"):
                reasons.append(
                    f"{manual_id}:assemblage_déclaré_absent:{variant}"
                )
            elif not coverage.get("observed_variants"):
                reasons.append(f"{manual_id}:build_observé_absent:{variant}")

    dimensions = dict(GATE_DIMENSION_TEMPLATE)
    dimensions["structure"] = (
        "passed"
        if all(manual["phase0_structural_eligible"] for manual in matrix.values())
        else "failed"
    )
    dimensions["execution"] = (
        "passed"
        if all(
            isinstance(observed_coverage.get(manual_id), Mapping)
            and observed_coverage[manual_id].get("observed_build_ready") is True
            for manual_id in matrix
        )
        and integration_ready
        else "failed"
    )
    for dimension, status in dimensions.items():
        if status == "not_covered":
            reasons.append(f"dimension_non_couverte:{dimension}")
    success = bool(matrix) and all(
        manual["publication_eligible"] for manual in matrix.values()
    )
    return _gate_result(
        "release-strict",
        success=success and not reasons,
        failure_code=GATE_RELEASE_CODE,
        dimensions=dimensions,
        reasons=reasons,
    )


def _release_strict_gate_for_root(
    root: Path,
    *,
    today: datetime.date | None = None,
) -> dict[str, Any]:
    evaluation_date = today or datetime.datetime.now(datetime.UTC).date()
    try:
        inventory = build_inventory(
            root,
            qualification_today=evaluation_date,
        )
    except (InventoryError, OSError, subprocess.CalledProcessError) as exc:
        return _gate_result(
            "release-strict",
            success=False,
            failure_code=GATE_RELEASE_CODE,
            dimensions={"structure": "failed", "execution": "failed"},
            reasons=[f"inventaire_indisponible:{_stable_gate_reason(exc, root)}"],
        )
    return _release_strict_gate(inventory)


def _print_gate_result(result: Mapping[str, Any]) -> None:
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


def _run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=".",
        help="Chemin racine du dépôt (par défaut : répertoire courant).",
    )
    parser.add_argument(
        "--audit-dir",
        default="audit",
        help="Dossier de sortie pour les rapports audit (par défaut : audit).",
    )
    parser.add_argument(
        "--etat-path",
        default="ETAT_COLLECTION.md",
        help="Chemin cible pour l’état collection dérivé.",
    )
    parser.add_argument(
        "--without-marker",
        action="store_true",
        help="Ne pas ajouter le marqueur auto-généré dans les rapports.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Sortie non nulle si des contradictions ouvertes ou bloquantes existent.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Comparer tous les rendus gérés sans modifier les fichiers.",
    )
    parser.add_argument(
        "--validate-model",
        action="store_true",
        help="Valider parsing, schémas, digests et cohérence des artefacts machine.",
    )
    parser.add_argument(
        "--release-strict",
        action="store_true",
        help="Refuser toute dette incompatible avec la publication.",
    )
    parser.add_argument(
        "--fail-on-new",
        action="store_true",
        help="Refuser une dette nouvelle par rapport à la baseline stabilisée.",
    )
    parser.add_argument(
        "--require-clean",
        action="store_true",
        help="Refuser les modifications suivies et les fichiers non suivis pertinents.",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Mettre à jour explicitement la baseline après les dix préconditions.",
    )
    parser.add_argument(
        "--allow-qualification-digest-bootstrap",
        action="store_true",
        help=(
            "Avec --update-baseline uniquement : autorise le bootstrap "
            "quand l'unique dérive fail-on-new est un réalignement "
            "mécanique de qualification_digest (nouveau control_digest de "
            "politique), vérifié structurellement comme n'ajoutant, "
            "supprimant ni modifiant aucun fingerprint, disposition, "
            "owner, catégorie ou sévérité."
        ),
    )
    parser.add_argument(
        "--allow-approved-baseline-extension",
        action="store_true",
        help=(
            "Avec --update-baseline uniquement : autorise l'ajout exact du "
            "jeu de fingerprints défini par la politique approuvée et, si "
            "approved_transition est présent, la réconciliation exacte des "
            "résolutions et remplacements contractuels. Chaque ajout reste "
            "open_debt et release_acceptance=false."
        ),
    )
    parser.add_argument(
        "--materialize-baseline-qualifications",
        action="store_true",
        help="Matérialiser explicitement le lot de dette approuvé par politique.",
    )
    parser.add_argument(
        "--reason",
        default="",
        help="Justification auditée de la mise à jour de baseline.",
    )
    parser.add_argument(
        "--approved-by",
        default="",
        help="Responsable humain approuvant la mise à jour de baseline.",
    )
    args = parser.parse_args()

    if args.allow_qualification_digest_bootstrap and not args.update_baseline:
        parser.error(
            "--allow-qualification-digest-bootstrap exige --update-baseline"
        )
    if args.allow_approved_baseline_extension and not args.update_baseline:
        parser.error(
            "--allow-approved-baseline-extension exige --update-baseline"
        )
    if (
        args.allow_qualification_digest_bootstrap
        and args.allow_approved_baseline_extension
    ):
        parser.error("les deux dérogations de baseline sont incompatibles")

    if args.materialize_baseline_qualifications:
        incompatible = (
            args.require_clean
            or args.validate_model
            or args.fail_on_new
            or args.release_strict
            or args.update_baseline
            or args.strict
        )
        if incompatible:
            parser.error(
                "--materialize-baseline-qualifications accepte seulement --check"
            )
        try:
            root = _repo_root_path(args.root)
        except InventoryError as exc:
            result = _gate_result(
                "materialize-baseline-qualifications",
                success=False,
                failure_code=GATE_CHECK_CODE,
                dimensions={"structure": "failed"},
                reasons=[str(exc)],
            )
        else:
            result = _safe_materialize_baseline_qualifications(
                root,
                check_only=args.check,
            )
        _print_gate_result(result)
        return int(result["exit_code"])

    requested_gates = (
        args.require_clean,
        args.validate_model,
        args.check,
        args.fail_on_new,
        args.release_strict,
        args.update_baseline,
    )
    if any(requested_gates):
        if args.strict:
            parser.error("--strict ne se combine pas avec les gates structurés")
        try:
            root = _repo_root_path(args.root)
        except InventoryError as exc:
            first_name, first_code = next(
                (name, code)
                for enabled, name, code in (
                    (args.require_clean, "require-clean", GATE_CLEAN_CODE),
                    (args.validate_model, "validate-model", GATE_VALIDATE_CODE),
                    (args.check, "check", GATE_CHECK_CODE),
                    (args.fail_on_new, "fail-on-new", GATE_BASELINE_CODE),
                    (args.release_strict, "release-strict", GATE_RELEASE_CODE),
                    (
                        args.update_baseline,
                        "update-baseline",
                        GATE_BASELINE_UPDATE_CODE,
                    ),
                )
                if enabled
            )
            failure = _gate_result(
                first_name,
                success=False,
                failure_code=first_code,
                dimensions={"structure": "failed"},
                reasons=[str(exc)],
            )
            _print_gate_result(failure)
            return int(failure["exit_code"])

        evaluations = []
        if args.require_clean:
            evaluations.append(_require_clean_gate(root))
        if args.validate_model:
            evaluations.append(_validate_model_gate(root))
        if args.check:
            evaluations.append(
                _check_gate(
                    root,
                    audit_directory=args.audit_dir,
                    etat_path=args.etat_path,
                )
            )
        if args.fail_on_new:
            evaluations.append(_fail_on_new_gate(root))
        if args.release_strict:
            evaluations.append(_release_strict_gate_for_root(root))
        if args.update_baseline:
            evaluations.append(
                _safe_update_baseline_gate(
                    root,
                    reason=args.reason,
                    approved_by=args.approved_by,
                    allow_qualification_digest_bootstrap=(
                        args.allow_qualification_digest_bootstrap
                    ),
                    allow_approved_baseline_extension=(
                        args.allow_approved_baseline_extension
                    ),
                )
            )
        result = next(
            (evaluation for evaluation in evaluations if not evaluation["success"]),
            evaluations[-1],
        )
        _print_gate_result(result)
        return int(result["exit_code"])

    global AUTOGEN_MARKER
    marker = not args.without_marker
    result = build_inventory_artifacts(
        args.root,
        audit_directory=args.audit_dir,
        etat_path=args.etat_path,
        include_generated_marker=marker,
    )
    inventory = result["inventory"]
    blocking = inventory["coherence_checks"]["status_distribution"]["ok"]
    if args.strict and not blocking:
        return 3
    open_claims = len(inventory["report_reconciliation"]["claims_non_resolues"])
    if args.strict and open_claims:
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(_run())
