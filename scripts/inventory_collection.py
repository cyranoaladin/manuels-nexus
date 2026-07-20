#!/usr/bin/env python3
"""Build the canonical, filesystem-derived inventory for the Nexus collection.

The model inventories content objects, reference graphs, declared assemblies and
tracked PDF artifacts.  Report reconciliation and rendering belong to the later
Phase 0 layers.
"""

from __future__ import annotations

import importlib
import argparse
import json
import posixpath
import re
import subprocess
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

import yaml

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
    from scripts import inventory_graph as _graph_core
    from scripts import inventory_pdf as _pdf_core
    from scripts import inventory_reports as _report_core
except ModuleNotFoundError:  # direct execution: python scripts/inventory_collection.py
    _assembly_core = _import_legacy_module("inventory_assembly")
    _graph_core = _import_legacy_module("inventory_graph")
    _pdf_core = _import_legacy_module("inventory_pdf")
    _report_core = _import_legacy_module("inventory_reports")


SCHEMA_VERSION = 1
PDFINFO_TIMEOUT_SECONDS = 10

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
}

MANUAL_EXPECTED_LEVELS: dict[str, str] = {
    "1NSI": "1NSI",
    "1SPE": "1SPE",
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
}

BLOCKING_ANOMALY_CATEGORIES = frozenset(
    {
        "assembler_invalid",
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
            if isinstance(artifact, Mapping) and artifact.get("manual") == manual_id
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
        manuals[manual_id] = {
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
            "publication_eligible": not blockers,
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


def build_inventory(repository: Path | str) -> dict[str, Any]:
    """Build a deterministic canonical model from tracked chapter sources."""

    root = Path(repository).resolve()
    tracked = git_tracked_files(root)
    tracked_set = frozenset(tracked)
    content_sources = tuple(path for path in tracked if _is_relevant_source(path))
    model_sources = tuple(path for path in tracked if _is_model_source(path))

    manuals = {
        manual_id: {
            "chapters": {},
            "compiled_artifacts": [],
            "compiled_variants": _empty_variant_scopes(),
            "declared_variants": _empty_variant_scopes(),
            "edition": definition["edition"],
            "level": definition["level"],
            "statuses": {},
            "subject": definition["subject"],
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
                continue
            except MetadataError as exc:
                anomalies["metadata_invalid"].append({"path": path, "reason": str(exc)})
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
        for chapter in manual["chapters"].values():
            for key in COUNT_KEYS:
                manual["totals"][key] += chapter["counts"][key]
            manual_statuses.update(chapter["statuses"])
        manual["statuses"] = dict(sorted(manual_statuses.items()))

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
        "assemblies": [],
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
    _add_latex_graph(inventory, root, tracked_set)
    _add_assemblies(inventory, root, tracked_set)
    _aggregate_declared_variants(inventory)
    _add_orphan_files(inventory, root, tracked_set)
    inventory["pdfs"] = _inventory_pdfs(root, tracked, inventory)
    _aggregate_pdf_artifacts(inventory)
    inventory["coherence_checks"] = validate_inventory_coherence(inventory)
    inventory["deliverable_matrix"] = build_deliverable_matrix(inventory)
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
        sorted(set(model_sources) | graph_targets | set(report_sources))
    )
    inventory["source_digest"] = _source_digest(root, model_sources)
    inventory["source_file_count"] = len(model_sources)
    inventory["source_files"] = list(model_sources)
    for values in anomalies.values():
        values.sort(key=_anomaly_sort_key)
    inventory["reference_graph"].sort(key=_reference_sort_key)
    inventory["correction_links"].sort(
        key=lambda item: (item["exercise_path"], item["correction_path"])
    )
    inventory["assemblies"].sort(key=lambda item: item["assembly_id"])
    return inventory


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
) -> None:
    _graph_core.add_latex_graph(
        inventory,
        root,
        tracked,
        is_relevant_tex=_is_relevant_tex,
        resolve_latex_target=_resolve_latex_target,
    )


def _add_static_latex_assemblies(
    inventory: dict[str, Any],
    root: Path,
    tracked: frozenset[str],
) -> None:
    _graph_core.add_static_latex_assemblies(
        inventory,
        root,
        tracked,
        is_relevant_tex=_is_relevant_tex,
        chapter_id_from_source=_chapter_id_from_source,
        manual_for_chapter=_manual_for_chapter,
    )


def _add_orphan_files(
    inventory: dict[str, Any],
    root: Path,
    tracked: frozenset[str],
) -> None:
    _graph_core.add_orphan_files(
        inventory,
        root,
        tracked,
        is_relevant_tex=_is_relevant_tex,
        is_known_latex_root=_is_known_latex_root,
        chapter_context=_chapter_context,
    )


def _add_assemblies(
    inventory: dict[str, Any],
    root: Path,
    tracked: frozenset[str],
) -> None:
    _assembly_core.add_declared_assemblies(
        inventory,
        root,
        tracked,
        manual_ids=tuple(MANUALS),
        manual_for_chapter=_manual_for_chapter,
        supported_manuals=_supported_manuals_for_assembler,
        project_for_manual=_project_for_manual,
        assembly_project_name=_assembly_project_name,
        chapter_directory=_chapter_directory,
        resolve_latex_target=_resolve_latex_target,
    )
    _add_static_latex_assemblies(inventory, root, tracked)
    _assembly_core.add_unassembled_objects(inventory)


def _inventory_pdfs(
    root: Path,
    tracked: tuple[str, ...],
    inventory: dict[str, Any],
) -> list[dict[str, Any]]:
    return _pdf_core.inventory_pdfs(
        root,
        tracked,
        inventory,
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
    _pdf_core.aggregate_artifacts(inventory)


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
        return ("1SPE", "TSPE_2026_2027")
    return ("1NSI", "TNSI")


def _assembly_project_name(manual: str) -> str:
    return "nsi" if manual in {"1NSI", "TNSI"} else "math"


def _chapter_directory(manual: str, chapter: str) -> str:
    return f"{_project_for_manual(manual)}/chapitres/{chapter}"


def _manual_blockers(
    inventory: Mapping[str, Any],
    manual_id: str,
    specification: Mapping[str, Any],
) -> list[dict[str, str]]:
    manual = inventory["manuals"][manual_id]
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
            if _anomaly_manual(anomaly) == manual_id
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
    if (
        chapter.get("contract_status") != "approved"
        or not chapter.get("contract_status_valid", False)
        or not chapter["objects"]
        or any(not item["publishable"] for item in chapter["objects"])
    ):
        return False
    return not any(
        _anomaly_manual(anomaly) == manual_id
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
        _is_relevant_source(path)
        or _is_relevant_tex(path)
        or path.endswith("/scripts/assemble.py")
        or path.endswith("/scripts/assemble_manuel.py")
        or path.lower().endswith(".pdf")
    )


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


def _reference_sort_key(item: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(str(item.get(key, "")) for key in ("source", "champ", "cible", "kind"))


AUTOGEN_MARKER = "<!-- AUTO-GÉNÉRÉ PAR inventory_collection.py -->"


def build_inventory_artifacts(
    repository: Path | str,
    *,
    audit_directory: str = "audit",
    etat_path: str = "ETAT_COLLECTION.md",
    include_generated_marker: bool = True,
) -> dict[str, Any]:
    """Build inventory and materialize required Phase-0 outputs."""

    root = Path(repository).resolve()
    inventory = build_inventory(root)

    audit_root = root / audit_directory
    audit_root.mkdir(parents=True, exist_ok=True)

    json_payload = _canonicalize(inventory)
    inventory_json_path = audit_root / "INVENTAIRE_COLLECTION.json"
    inventory_json_path.write_text(
        json.dumps(json_payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    inventory_markdown_path = audit_root / "INVENTAIRE_COLLECTION.md"
    inventory_markdown_path.write_text(
        _render_inventory_markdown(inventory),
        encoding="utf-8",
    )

    etat_file = root / etat_path
    etat_file.write_text(_render_etat_collection(inventory), encoding="utf-8")

    audit_consolide_path = audit_root / "AUDIT_CONSOLIDE.md"
    audit_consolide_path.write_text(
        _render_audit_consolide(inventory),
        encoding="utf-8",
    )

    ecarts_path = audit_root / "ECARTS_ET_CONTRADICTIONS.yaml"
    ecarts_path.write_text(
        _render_ecarts_yaml(inventory, marker=include_generated_marker),
        encoding="utf-8",
    )

    matrice_path = audit_root / "MATRICE_LIVRABLES.yaml"
    matrice_path.write_text(
        _render_matrice_livrables(inventory),
        encoding="utf-8",
    )

    return {
        "audit_directory": str(audit_root.relative_to(root)),
        "artifacts": {
            "json": str(inventory_json_path.relative_to(root)),
            "markdown": str(inventory_markdown_path.relative_to(root)),
            "etat": str(etat_file.relative_to(root)),
            "audit": str(audit_consolide_path.relative_to(root)),
            "ecarts": str(ecarts_path.relative_to(root)),
            "matrice": str(matrice_path.relative_to(root)),
        },
        "inventory": inventory,
    }


def _manual_name(manual_id: str) -> str:
    return {
        "1SPE": "Mathématiques Première",
        "TSPE_2026_2027": "Mathématiques Terminale",
        "1NSI": "NSI Première",
        "TNSI": "NSI Terminale",
    }.get(manual_id, manual_id)


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


def _render_inventory_markdown(inventory: Mapping[str, Any]) -> str:
    header = (
        "# INVENTAIRE_COLLECTION\n\n" f"{AUTOGEN_MARKER}\n\n" "## Synthèse par manuel\n"
    )

    lines = [header]
    manual_rows: list[tuple[Any, ...]] = []
    for manual_id in sorted(inventory["manuals"]):
        manual = inventory["manuals"][manual_id]
        total_objects = sum(manual["totals"].values())
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
                total_objects,
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


def _render_etat_collection(inventory: Mapping[str, Any]) -> str:
    manual_blockers = inventory["anomalies"].get("blocking_statuses", [])
    unresolved = inventory["report_reconciliation"]["claims_non_resolues"]

    lines = [
        "# ETAT COLLECTION — Nexus Réussite",
        "",
        AUTOGEN_MARKER,
        "",
        "## État global",
        f"- Digest source: `{inventory['source_digest']}`",
        f"- Fichiers scannés: {inventory['source_file_count']}",
        "",
    ]
    header_rows: list[tuple[Any, ...]] = []
    for manual_id in sorted(inventory["manuals"]):
        manual = inventory["manuals"][manual_id]
        blockers = inventory["deliverable_matrix"]["manuals"][manual_id]["blockers"]
        header_rows.append(
            (
                _manual_name(manual_id),
                manual_id,
                len(manual["chapters"]),
                manual["totals"]["exercices_principaux"],
                manual["totals"]["sections_cours"],
                manual["totals"]["methodes"],
                manual["totals"]["corriges"],
                manual["statuses"],
                "OK" if not blockers else "NON",
            )
        )
    lines.append(
        _markdown_table(
            (
                "Manuel",
                "Identifiant",
                "Chapitres",
                "Exercices",
                "Sections cours",
                "Méthodes",
                "Corrigés",
                "Statuts objets",
                "Publication",
            ),
            header_rows,
        )
    )
    lines.append("")

    if manual_blockers:
        lines.append("## Bloquants globaux")
        for blocker in sorted(
            manual_blockers,
            key=lambda item: (str(item.get("manual", "")), str(item.get("code", ""))),
        ):
            lines.append(
                "- "
                + " | ".join(
                    str(value)
                    for value in (
                        blocker.get("manual"),
                        blocker.get("scope"),
                        blocker.get("code"),
                        blocker.get("status", blocker.get("detail")),
                    )
                )
            )
        lines.append("")

    lines.append("## Contradictions ouvertes")
    if not unresolved:
        lines.append("- Aucune contradiction ouverte.\n")
    else:
        for claim in unresolved:
            lines.append(
                "- "
                + " | ".join(
                    [
                        claim["path"],
                        str(claim["line"]),
                        claim["scope"],
                        claim["metric"],
                        str(claim["declared"]),
                        str(claim.get("reason", "")),
                    ]
                )
            )
        lines.append("")

    return "\n".join(lines)


def _render_audit_consolide(inventory: Mapping[str, Any]) -> str:
    lines = [
        "# AUDIT_CONSOLIDE",
        "",
        AUTOGEN_MARKER,
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
            summary = ", ".join(
                f"{key}={_to_text(item.get(key))}" for key in _sample_keys(item)
            )
            lines.append(f"- {summary}")
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


def _sample_keys(item: Mapping[str, Any]) -> list[str]:
    if "path" in item:
        return ["path", "chapter", "scope", "reason"]
    if "scope" in item:
        return ["scope", "metric", "declared", "calculated", "etat"]
    return ["id", "detail", "code"]


def _to_text(value: Any) -> str:
    if isinstance(value, bool):
        return "oui" if value else "non"
    if value is None:
        return "—"
    return str(value)


def _render_ecarts_yaml(inventory: Mapping[str, Any], marker: bool = True) -> str:
    claims = inventory["report_reconciliation"]["claims"]
    payload = {
        "generated_by": "inventory_collection.py",
        "source_digest": inventory["source_digest"],
        "anomalies": {
            category: sorted((item for item in values), key=_anomaly_sort_key)
            for category, values in sorted(inventory["anomalies"].items())
        },
        "claims": {
            "contredits": [claim for claim in claims if claim["etat"] == "contredit"],
            "ouvertes": [claim for claim in claims if claim["etat"] == "ouvert"],
            "confirmes": [claim for claim in claims if claim["etat"] == "confirme"],
        },
        "counts": {
            "claims_ouverts": len([c for c in claims if c["etat"] == "ouvert"]),
            "claims_contredits": len([c for c in claims if c["etat"] == "contredit"]),
            "claims_confirme": len([c for c in claims if c["etat"] == "confirme"]),
        },
    }
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
    matrix = inventory["deliverable_matrix"]["manuals"]
    payload = {
        "generated_by": "inventory_collection.py",
        "source_digest": inventory["source_digest"],
        "manuals": matrix,
    }
    return yaml.safe_dump(
        _canonicalize(payload),
        allow_unicode=True,
        sort_keys=True,
        width=120,
    )


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
    args = parser.parse_args()

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
