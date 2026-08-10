#!/usr/bin/env python3
"""Build and validate the evidence registry for 1NSI content reviews."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = Path("audit/1NSI_CONTENT_REVIEW_POLICY.yaml")
SCHEMA_PATH = Path("audit/schemas/v1/1nsi-content-review.schema.json")
META = re.compile(r"^% META:\s*(\{.*\})\s*$", re.MULTILINE)
PYTHON_REFERENCE = re.compile(r"[A-Za-z0-9_./\\-]+\.py")
LINK_KEYS = {"exercice_ref", "exercice_id", "evaluation_ref"}
DEPENDENCY_CLASSES = (
    "protocol",
    "source",
    "contract",
    "linked_objects",
    "help",
    "correction",
    "receipt",
    "python",
)
REVIEW_RECEIPT_PATHS = frozenset(
    f"audit/reviews/1nsi/runs/2026-08-10-{name}.yaml"
    for name in (
        "contracts",
        "algorithms",
        "systems-web",
        "language-project",
        "data-basics-tables",
        "types-construits",
    )
)


class ReviewValidationError(ValueError):
    """Raised when review evidence does not satisfy the closed protocol."""


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def discover_sources(root: Path = ROOT) -> list[dict[str, Any]]:
    """Discover the exact review scope without traversing TNSI."""
    chapter_root = root / "NSI" / "chapitres"
    sources: list[dict[str, Any]] = []

    for path in sorted(chapter_root.glob("1NSI-*/**/*.tex")):
        text = path.read_text(encoding="utf-8")
        match = META.search(text)
        if not match:
            continue
        try:
            metadata = json.loads(match.group(1))
        except json.JSONDecodeError as error:
            raise ReviewValidationError(f"META invalide: {_relative(path, root)}") from error
        chapter = metadata.get("chapitre")
        object_id = metadata.get("id")
        status = metadata.get("status")
        if not all(isinstance(value, str) and value for value in (chapter, object_id, status)):
            raise ReviewValidationError(f"identite META incomplete: {_relative(path, root)}")
        relative = _relative(path, root)
        if not relative.startswith("NSI/chapitres/1NSI-") or "TNSI" in relative:
            raise ReviewValidationError(f"source hors 1NSI: {relative}")
        sources.append(
            {
                "id": object_id,
                "scope": "object",
                "chapter": chapter,
                "path": relative,
                "status": status,
                "type": metadata.get("type_objet"),
                "capacity_refs": sorted(set(metadata.get("capacites", []))),
                "metadata": metadata,
                "source_sha256": sha256_file(path),
            }
        )

    for path in sorted(chapter_root.glob("1NSI-*/contrat.yaml")):
        contract = yaml.safe_load(path.read_text(encoding="utf-8"))
        chapter = contract.get("chapitre")
        status = contract.get("statut")
        relative = _relative(path, root)
        if not isinstance(chapter, str) or not isinstance(status, str):
            raise ReviewValidationError(f"contrat incomplet: {relative}")
        sources.append(
            {
                "id": f"contract:{chapter}",
                "scope": "contract",
                "chapter": chapter,
                "path": relative,
                "status": status,
                "type": "contract",
                "capacity_refs": sorted(
                    {item["ref_capacite"] for item in contract.get("capacites", [])}
                ),
                "metadata": contract,
                "source_sha256": sha256_file(path),
            }
        )

    sources.sort(key=lambda item: (item["chapter"], item["scope"], item["id"], item["path"]))
    identities = [item["id"] for item in sources]
    if len(identities) != len(set(identities)):
        duplicates = sorted({item for item in identities if identities.count(item) > 1})
        raise ReviewValidationError(f"identites 1NSI en doublon: {duplicates}")
    return sources


def _protocol_records(policy: dict[str, Any]) -> list[dict[str, str]]:
    records = [
        {"path": item["snapshot_path"], "sha256": item["sha256"]}
        for item in policy["official_sources"]
    ]
    records.extend(
        {"path": item["path"], "sha256": item["sha256"]}
        for item in policy["contractual_documents"]
    )
    return sorted(records, key=lambda item: item["path"])


def protocol_digest_from_records(
    records: list[dict[str, str]], policy: dict[str, Any]
) -> str:
    payload = json.dumps(
        {
            "decision": policy["decision"],
            "verdicts": policy["verdicts"],
            "prohibited_transitions": policy["prohibited_transitions"],
            "review_dimensions": policy["review_dimensions"],
            "capacity_matrix": policy["capacity_matrix"],
            "source_records": records,
        },
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256_bytes(payload.encode("ascii"))


def compute_protocol_digest(root: Path, policy: dict[str, Any]) -> str:
    records = _protocol_records(policy)
    for record in records:
        observed = sha256_file(root / record["path"])
        if observed != record["sha256"]:
            raise ReviewValidationError(f"digest de protocole obsolete: {record['path']}")
    return protocol_digest_from_records(records, policy)


def load_policy(root: Path = ROOT) -> dict[str, Any]:
    policy = yaml.safe_load((root / POLICY_PATH).read_text(encoding="utf-8"))
    observed = compute_protocol_digest(root, policy)
    if observed != policy.get("protocol_digest"):
        raise ReviewValidationError("protocol_digest obsolete")
    return policy


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return sha256_bytes(payload.encode("ascii"))


def _file_record(path: Path, root: Path) -> dict[str, str]:
    return {"path": _relative(path, root), "sha256": sha256_file(path)}


def _metadata_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for value_item in value for item in _metadata_strings(value_item)]
    if isinstance(value, dict):
        return [item for value_item in value.values() for item in _metadata_strings(value_item)]
    return []


def _resolve_declared_path(raw: str, source: dict[str, Any], root: Path) -> Path | None:
    cleaned = raw.replace(r"\_", "_").strip("`'\"{}[](),;:")
    candidates = [
        root / cleaned,
        root / "NSI" / cleaned,
        root / "NSI" / "chapitres" / source["chapter"] / cleaned,
        (root / source["path"]).parent / cleaned,
    ]
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
            resolved.relative_to(root.resolve())
        except ValueError:
            continue
        if resolved.is_file():
            return resolved
    return None


def _resolve_execution_receipt(source: dict[str, Any], root: Path) -> Path | None:
    validations = root / "NSI" / "chapitres" / source["chapter"] / "validations"
    source_stem = Path(source["path"]).stem
    names = {source["id"], source_stem}
    candidates = sorted(
        (validations / f"{name}.execution.json" for name in names),
        key=lambda path: path.name,
    )
    existing = [path for path in candidates if path.is_file()]
    if len(existing) > 1:
        relative = ", ".join(_relative(path, root) for path in existing)
        raise ReviewValidationError(
            f"candidats de recu d'execution ambigus pour {source['id']}: {relative}"
        )
    return existing[0] if existing else None


def dependency_manifest(
    source: dict[str, Any], sources: list[dict[str, Any]], root: Path = ROOT
) -> dict[str, list[dict[str, str]]]:
    """Return every file dependency classified for one review entry."""
    manifest: dict[str, list[dict[str, str]]] = {
        key: [] for key in DEPENDENCY_CLASSES if key != "protocol"
    }
    source_path = root / source["path"]
    manifest["source"] = [_file_record(source_path, root)]

    contract_path = root / "NSI" / "chapitres" / source["chapter"] / "contrat.yaml"
    if not contract_path.is_file():
        raise ReviewValidationError(f"contrat introuvable pour {source['id']}")
    manifest["contract"] = [_file_record(contract_path, root)]

    if source["scope"] == "contract":
        return manifest

    metadata = source.get("metadata", {})
    linked_ids = {
        value
        for key, value in metadata.items()
        if (key in LINK_KEYS or key.endswith("_ref")) and isinstance(value, str)
    }
    linked_paths: set[str] = set()
    for key in ("fichier_tex", "corrige_tex"):
        value = metadata.get(key)
        if isinstance(value, str):
            resolved = _resolve_declared_path(value, source, root)
            if resolved:
                linked_paths.add(_relative(resolved, root))

    for other in sources:
        if other["scope"] != "object" or other["id"] == source["id"]:
            continue
        values = set(_metadata_strings(other.get("metadata", {})))
        if source["id"] in values or source["path"].removeprefix("NSI/") in values:
            linked_ids.add(other["id"])

    linked_sources = {
        item["id"]: item
        for item in sources
        if item["scope"] == "object"
        and (item["id"] in linked_ids or item["path"] in linked_paths)
    }
    linked_records = sorted(
        (_file_record(root / item["path"], root) for item in linked_sources.values()),
        key=lambda item: item["path"],
    )
    manifest["linked_objects"] = linked_records
    for linked_id, item in sorted(linked_sources.items()):
        record = _file_record(root / item["path"], root)
        object_type = item.get("type")
        if object_type == "coup_de_pouce":
            manifest["help"].append(record)
        if object_type in {"corrige", "corrige_evaluation"}:
            manifest["correction"].append(record)

    receipt = _resolve_execution_receipt(source, root)
    if receipt is not None:
        manifest["receipt"] = [_file_record(receipt, root)]

    python_paths: set[Path] = set()
    source_text = source_path.read_text(encoding="utf-8")
    candidates = PYTHON_REFERENCE.findall(source_text)
    candidates.extend(
        value for value in _metadata_strings(metadata) if value.replace(r"\_", "_").endswith(".py")
    )
    for candidate in candidates:
        resolved = _resolve_declared_path(candidate, source, root)
        if resolved:
            python_paths.add(resolved)
    manifest["python"] = sorted(
        (_file_record(path, root) for path in python_paths), key=lambda item: item["path"]
    )

    for key in manifest:
        unique = {record["path"]: record for record in manifest[key]}
        manifest[key] = [unique[path] for path in sorted(unique)]
    return manifest


def dependency_class_digests(
    source: dict[str, Any],
    sources: list[dict[str, Any]],
    root: Path,
    policy: dict[str, Any],
) -> dict[str, str]:
    manifest = dependency_manifest(source, sources, root)
    digests = {key: _canonical_digest(manifest[key]) for key in manifest}
    digests["protocol"] = policy["protocol_digest"]
    return {key: digests[key] for key in DEPENDENCY_CLASSES}


def aggregate_dependency_digest(class_digests: dict[str, str]) -> str:
    if set(class_digests) != set(DEPENDENCY_CLASSES):
        raise ReviewValidationError("classes de dependances incompletes")
    return _canonical_digest({key: class_digests[key] for key in DEPENDENCY_CLASSES})


def compute_dependency_digest(
    source: dict[str, Any],
    sources: list[dict[str, Any]],
    root: Path,
    policy: dict[str, Any],
) -> str:
    return aggregate_dependency_digest(dependency_class_digests(source, sources, root, policy))


def _tnsi_fingerprint(root: Path) -> tuple[int, str]:
    result = subprocess.run(
        ["git", "ls-files", "NSI/chapitres/TNSI-*"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    paths = sorted(line for line in result.stdout.splitlines() if line)
    digest = hashlib.sha256()
    for relative in paths:
        data = (root / relative).read_bytes()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(data).digest())
    return len(paths), "sha256:" + digest.hexdigest()


def _changed_paths(root: Path, base_sha: str) -> list[str]:
    tracked = subprocess.run(
        ["git", "diff", "--name-only", base_sha, "--"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    return sorted(set(tracked) | set(untracked))


def verify_scope(
    root: Path,
    policy: dict[str, Any],
    *,
    changed_paths: list[str] | None = None,
) -> None:
    """Refuse any source, TNSI, PDF, manifest or allowlist drift."""
    guard = policy["scope_guard"]
    observed_sources = [
        {"id": item["id"], "path": item["path"], "status": item["status"]}
        for item in discover_sources(root)
    ]
    if observed_sources != guard["sources"]:
        raise ReviewValidationError("scope drift: table ID/path/status 1NSI")

    manifest = guard["build_manifest"]
    if sha256_file(root / manifest["path"]) != manifest["sha256"]:
        raise ReviewValidationError("scope drift: BUILD_MANIFEST")
    for pdf in guard["canonical_pdfs"]:
        if sha256_file(root / pdf["path"]) != pdf["sha256"]:
            raise ReviewValidationError(f"scope drift: PDF {pdf['path']}")
    tnsi_count, tnsi_digest = _tnsi_fingerprint(root)
    if (
        tnsi_count != guard["tnsi_tracked_files_count"]
        or tnsi_digest != guard["tnsi_tracked_files_digest"]
    ):
        raise ReviewValidationError("scope drift: fichiers TNSI")

    paths = changed_paths
    if paths is None:
        paths = _changed_paths(root, guard["implementation_base_sha"])
    outside = sorted(set(paths) - set(policy["allowlist"]))
    if outside:
        raise ReviewValidationError(f"allowlist violee: {', '.join(outside)}")


def _excerpt_bytes(path: Path, line_start: int, line_end: int) -> bytes:
    if line_start < 1 or line_end < line_start:
        raise ReviewValidationError("plage de lignes invalide")
    lines = path.read_bytes().splitlines(keepends=True)
    if line_end > len(lines):
        raise ReviewValidationError("plage de lignes hors source")
    return b"".join(lines[line_start - 1 : line_end])


def _normalise_observation(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def _allowed_fact_paths(
    source: dict[str, Any],
    sources: list[dict[str, Any]],
    root: Path,
    policy: dict[str, Any],
) -> set[str]:
    manifest = dependency_manifest(source, sources, root)
    allowed = {
        record["path"] for records in manifest.values() for record in records
    }
    allowed.update(item["snapshot_path"] for item in policy["official_sources"])
    allowed.update(item["path"] for item in policy["contractual_documents"])
    return allowed


def _validate_fact(fact: dict[str, Any], allowed_paths: set[str], root: Path) -> None:
    required = {
        "path",
        "line_start",
        "line_end",
        "excerpt_sha256",
        "fact_type",
        "observation",
    }
    if set(fact) != required:
        raise ReviewValidationError("preuve incomplete ou champ inconnu")
    path = fact["path"]
    if "TNSI" in path:
        raise ReviewValidationError("preuve TNSI interdite")
    if path not in allowed_paths:
        raise ReviewValidationError(f"preuve hors dependances: {path}")
    observed = sha256_bytes(_excerpt_bytes(root / path, fact["line_start"], fact["line_end"]))
    if observed != fact["excerpt_sha256"]:
        raise ReviewValidationError(f"digest d'extrait invalide: {path}")
    if not isinstance(fact["observation"], str) or not fact["observation"].strip():
        raise ReviewValidationError("observation de preuve vide")


def _validate_review_receipt(
    provenance: dict[str, Any],
    source: dict[str, Any],
    root: Path,
    policy: dict[str, Any],
) -> None:
    receipt_path = provenance["review_receipt_path"]
    if (
        receipt_path not in REVIEW_RECEIPT_PATHS
        or receipt_path not in policy["allowlist"]
    ):
        raise ReviewValidationError("chemin du recu de revue interdit")

    expected_digest = provenance["review_receipt_sha256"]
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", expected_digest):
        raise ReviewValidationError("digest du recu de revue invalide")
    commit_sha = provenance["sealing_commit_sha"]
    if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", commit_sha):
        raise ReviewValidationError("commit de scellement invalide")

    commit = subprocess.run(
        ["git", "rev-parse", "--verify", f"{commit_sha}^{{commit}}"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if commit.returncode != 0:
        raise ReviewValidationError("commit de scellement introuvable")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit_sha, "HEAD"],
        cwd=root,
        capture_output=True,
    )
    if ancestor.returncode != 0:
        raise ReviewValidationError("commit de scellement non ancetre de HEAD")

    blob = subprocess.run(
        ["git", "show", f"{commit_sha}:{receipt_path}"],
        cwd=root,
        capture_output=True,
    )
    if blob.returncode != 0:
        raise ReviewValidationError("recu de revue absent du commit de scellement")
    if sha256_bytes(blob.stdout) != expected_digest:
        raise ReviewValidationError("digest du recu de revue incoherent avec le blob scelle")

    worktree_path = root / receipt_path
    if not worktree_path.is_file() or worktree_path.read_bytes() != blob.stdout:
        raise ReviewValidationError("octets du recu de revue differents du blob scelle")

    try:
        receipt = yaml.safe_load(blob.stdout.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as error:
        raise ReviewValidationError("YAML du recu de revue invalide") from error
    schema_path = root / SCHEMA_PATH
    if not schema_path.is_file():
        schema_path = ROOT / SCHEMA_PATH
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    receipt_schema = {
        "$schema": schema["$schema"],
        "$ref": "#/$defs/review_run_receipt",
        "$defs": schema["$defs"],
    }
    errors = sorted(
        Draft202012Validator(receipt_schema).iter_errors(receipt),
        key=lambda error: tuple(str(part) for part in error.path),
    )
    if errors:
        raise ReviewValidationError(f"schema du recu de revue invalide: {errors[0].message}")

    expected_fields = {
        "review_run_id": provenance["review_run_id"],
        "reviewer_id": provenance["reviewer_id"],
        "reviewer_model": provenance["reviewer_model"],
        "protocol_digest": policy["protocol_digest"],
    }
    for field, expected in expected_fields.items():
        if receipt[field] != expected:
            raise ReviewValidationError(f"{field} du recu de revue incoherent")

    assignment = receipt["assignment"]
    if source["id"] not in assignment["source_ids"]:
        raise ReviewValidationError(f"source non assignee dans le recu: {source['id']}")
    if source["chapter"] not in assignment["chapters"]:
        raise ReviewValidationError("chapitre d'affectation incoherent")
    if source["scope"] != assignment["scope"]:
        raise ReviewValidationError("scope d'affectation incoherent")

    matching_reviews = [review for review in receipt["reviews"] if review["id"] == source["id"]]
    if not matching_reviews:
        raise ReviewValidationError(f"review absente pour {source['id']}")
    if len(matching_reviews) > 1:
        raise ReviewValidationError(f"review dupliquee pour {source['id']}")
    review = matching_reviews[0]
    if review["chapter"] != source["chapter"]:
        raise ReviewValidationError("chapitre de review incoherent")
    if review["scope"] != source["scope"]:
        raise ReviewValidationError("scope de review incoherent")


def validate_findings(
    findings: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    root: Path,
    policy: dict[str, Any],
    *,
    require_complete: bool = True,
) -> list[dict[str, Any]]:
    """Validate reviewer-owned facts without accepting reviewer-owned digests."""
    expected = {source["id"]: source for source in sources}
    identities = [finding.get("id") for finding in findings]
    duplicates = sorted({identity for identity in identities if identities.count(identity) > 1})
    if duplicates:
        raise ReviewValidationError(f"finding en doublon: {duplicates}")
    unknown = sorted(set(identities) - set(expected))
    if unknown:
        raise ReviewValidationError(f"finding inconnue: {unknown}")
    if require_complete:
        missing = sorted(set(expected) - set(identities))
        if missing:
            raise ReviewValidationError(f"finding manquante: {missing}")

    known_refs = {row["ref"] for row in policy["capacity_matrix"]}
    seen_observations: dict[tuple[str, str], str] = {}
    forbidden_digest_fields = {"source_sha256", "dependency_digest", "protocol_digest"}
    finding_fields = {
        "id",
        "scope",
        "chapter",
        "source_path",
        "source_status",
        "capacity_refs",
        "provenance",
        "dimensions",
        "anomalies",
    }
    validated: list[dict[str, Any]] = []
    for finding in findings:
        source = expected[finding["id"]]
        supplied = forbidden_digest_fields & set(finding)
        if supplied:
            raise ReviewValidationError(f"digest fourni par le relecteur: {sorted(supplied)}")
        if "TNSI" in str(finding.get("source_path", "")):
            raise ReviewValidationError("chemin TNSI interdit")
        if "publication_approval" in finding:
            raise ReviewValidationError("publication approval interdite dans un finding")
        unknown_fields = set(finding) - finding_fields
        if unknown_fields:
            raise ReviewValidationError(f"champ inconnu dans le finding: {sorted(unknown_fields)}")
        missing_fields = finding_fields - set(finding)
        if missing_fields:
            raise ReviewValidationError(f"finding incomplet: {sorted(missing_fields)}")
        for key, observed in (
            ("scope", source["scope"]),
            ("chapter", source["chapter"]),
            ("source_path", source["path"]),
            ("source_status", source["status"]),
        ):
            if finding.get(key) != observed:
                raise ReviewValidationError(f"identite de finding incoherente: {key}")
        refs = finding.get("capacity_refs")
        if not isinstance(refs, list) or any(ref not in known_refs for ref in refs):
            raise ReviewValidationError("reference contractuelle inconnue")
        if sorted(set(refs)) != sorted(source.get("capacity_refs", [])):
            raise ReviewValidationError("references du finding incompletes")

        provenance = finding.get("provenance")
        provenance_fields = {
            "reviewer_id",
            "review_run_id",
            "reviewer_model",
            "integrator_id",
            "review_receipt_path",
            "review_receipt_sha256",
            "sealing_commit_sha",
        }
        if not isinstance(provenance, dict) or set(provenance) != provenance_fields:
            raise ReviewValidationError("provenance incomplete")
        if any(not isinstance(provenance[key], str) or not provenance[key].strip() for key in provenance):
            raise ReviewValidationError("provenance incomplete")
        if provenance["integrator_id"] != policy["integrator_id"]:
            raise ReviewValidationError("integrateur incoherent")
        if provenance["reviewer_id"] == provenance["integrator_id"]:
            raise ReviewValidationError("relecteur identique a l'integrateur")
        _validate_review_receipt(provenance, source, root, policy)

        anomalies = finding.get("anomalies")
        if not isinstance(anomalies, list):
            raise ReviewValidationError("anomalies invalides")
        anomaly_ids = [anomaly.get("id") for anomaly in anomalies]
        if len(anomaly_ids) != len(set(anomaly_ids)):
            raise ReviewValidationError("anomalie en doublon")
        allowed_paths = _allowed_fact_paths(source, sources, root, policy)
        dimensions = finding.get("dimensions")
        if not isinstance(dimensions, dict) or set(dimensions) != {"scientific", "pedagogical"}:
            raise ReviewValidationError("dimensions de revue incompletes")
        for name in ("scientific", "pedagogical"):
            dimension = dimensions[name]
            dimension_fields = {"verdict", "justification", "facts", "anomaly_ids"}
            if not isinstance(dimension, dict) or set(dimension) != dimension_fields:
                raise ReviewValidationError(f"dimension {name} incomplete ou champ inconnu")
            if dimension.get("verdict") not in policy["verdicts"]:
                raise ReviewValidationError("verdict inconnu")
            if not isinstance(dimension.get("justification"), str) or not dimension["justification"].strip():
                raise ReviewValidationError("verdict sans justification")
            facts = dimension.get("facts")
            if not isinstance(facts, list) or not facts:
                raise ReviewValidationError("verdict sans preuve")
            dimension_anomalies = [
                anomaly for anomaly in anomalies if anomaly.get("dimension") == name
            ]
            declared_ids = dimension.get("anomaly_ids")
            if not isinstance(declared_ids, list) or set(declared_ids) != {
                anomaly.get("id") for anomaly in dimension_anomalies
            }:
                raise ReviewValidationError("liens d'anomalies incoherents")
            if dimension_anomalies and dimension["verdict"] != "issue":
                raise ReviewValidationError("anomalie dimensionnelle exige un verdict issue")
            if dimension["verdict"] == "issue" and not dimension_anomalies:
                raise ReviewValidationError("verdict issue sans anomalie")
            for fact in facts:
                _validate_fact(fact, allowed_paths, root)
                normalised = _normalise_observation(fact["observation"])
                key = (source["chapter"], normalised)
                if normalised and key in seen_observations:
                    raise ReviewValidationError(
                        f"observation normalisee dupliquee: {seen_observations[key]} / {source['id']}"
                    )
                seen_observations[key] = source["id"]

        for anomaly in anomalies:
            required = {"id", "severity", "dimension", "fact", "consequence", "expected_action"}
            if set(anomaly) != required:
                raise ReviewValidationError("anomalie incomplete")
            if anomaly["severity"] not in {"P0", "P1", "P2", "P3"}:
                raise ReviewValidationError("severite d'anomalie invalide")
            if anomaly["dimension"] not in {"scientific", "pedagogical"}:
                raise ReviewValidationError("dimension d'anomalie invalide")
            _validate_fact(anomaly["fact"], allowed_paths, root)
        validated.append(copy.deepcopy(finding))
    return sorted(validated, key=lambda item: (item["chapter"], item["scope"], item["id"]))


_VERIFY_MODULE: Any | None = None


def _verify_module() -> Any:
    global _VERIFY_MODULE
    if _VERIFY_MODULE is None:
        scripts_dir = ROOT / "NSI" / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        spec = importlib.util.spec_from_file_location(
            "nsi_review_verify_python", scripts_dir / "verify_python.py"
        )
        if spec is None or spec.loader is None:
            raise ReviewValidationError("verify_python.py introuvable")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _VERIFY_MODULE = module
    return _VERIFY_MODULE


def execution_observation(source: dict[str, Any], root: Path = ROOT) -> dict[str, Any] | None:
    """Run check_object in memory and compare its stable payload to the receipt."""
    if source["scope"] != "object":
        return None
    path = root / source["path"]
    text = path.read_text(encoding="utf-8")
    verifier = _verify_module()
    if not (verifier.VERIFY.search(text) or verifier.TRACE.search(text) or verifier.PYENV.search(text)):
        return None
    result = verifier.check_object(path, no_ruff=False)
    fresh_verdict = "pass" if result["verdict"] == "verified" else result["verdict"]
    stable_result = {"verdict": fresh_verdict, "checks": result["checks"]}
    receipt_path = _resolve_execution_receipt(source, root)
    receipt: dict[str, Any] | None = None
    receipt_sha: str | None = None
    if receipt_path is not None:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt_sha = sha256_file(receipt_path)
    receipt_verdict = receipt.get("verdict") if receipt else None
    receipt_checks = receipt.get("details", {}).get("checks") if receipt else None
    matches = receipt_verdict == fresh_verdict and receipt_checks == result["checks"]
    anomalies = []
    if fresh_verdict == "fail":
        anomalies.append("fresh_execution_failed")
    elif receipt is None:
        anomalies.append("missing_receipt")
    elif not matches:
        anomalies.append("execution_receipt_diverged")
    return {
        "checker": "NSI/scripts/verify_python.py::check_object",
        "fresh_verdict": fresh_verdict,
        "receipt_verdict": receipt_verdict,
        "matches_receipt": matches,
        "checks": result["checks"],
        "check_digest": _canonical_digest(stable_result),
        "receipt_sha256": receipt_sha,
        "anomalies": anomalies,
    }


def _execution_anomaly(
    source: dict[str, Any], observation: dict[str, Any], root: Path
) -> dict[str, Any]:
    failure_class = observation["anomalies"][0]
    fresh_failure = failure_class == "fresh_execution_failed"
    anomaly_id = "1NSI-REV-EXEC-" + hashlib.sha256(source["id"].encode("utf-8")).hexdigest()[:12].upper()
    source_path = root / source["path"]
    fact = {
        "path": source["path"],
        "line_start": 1,
        "line_end": 1,
        "excerpt_sha256": sha256_bytes(_excerpt_bytes(source_path, 1, 1)),
        "fact_type": "computed_result",
        "observation": (
            f"Le controle executable frais echoue pour {source['id']}."
            if fresh_failure
            else f"La tracabilite du recu d'execution est incomplete pour {source['id']}."
        ),
    }
    return {
        "id": anomaly_id,
        "severity": "P0" if fresh_failure else "P1",
        "dimension": "scientific" if fresh_failure else "traceability",
        "fact": fact,
        "consequence": (
            "Le code publie ne satisfait pas le controle executable frais."
            if fresh_failure
            else "Le controle frais passe, mais sa tracabilite par un recu concordant n'est pas etablie."
        ),
        "expected_action": "Corriger la source ou regenerer le recu dans un lot distinct, puis refaire la revue.",
    }


def generate_register(
    findings: list[dict[str, Any]],
    root: Path,
    policy: dict[str, Any],
    *,
    sources: list[dict[str, Any]] | None = None,
    require_complete: bool = True,
) -> dict[str, Any]:
    observed_sources = discover_sources(root) if sources is None else sources
    validated = validate_findings(
        findings, observed_sources, root, policy, require_complete=require_complete
    )
    by_id = {finding["id"]: finding for finding in validated}
    entries = []
    for source in sorted(
        observed_sources, key=lambda item: (item["chapter"], item["scope"], item["id"])
    ):
        finding = by_id[source["id"]]
        dimensions = copy.deepcopy(finding["dimensions"])
        anomalies = copy.deepcopy(finding["anomalies"])
        observation = execution_observation(source, root)
        if observation and observation["anomalies"]:
            anomaly = _execution_anomaly(source, observation, root)
            anomalies.append(anomaly)
            if anomaly["dimension"] in dimensions:
                dimension = dimensions[anomaly["dimension"]]
                dimension["verdict"] = "issue"
                dimension["facts"].append(copy.deepcopy(anomaly["fact"]))
                dimension["anomaly_ids"].append(anomaly["id"])
        class_digests = dependency_class_digests(source, observed_sources, root, policy)
        entries.append(
            {
                "id": source["id"],
                "scope": source["scope"],
                "chapter": source["chapter"],
                "source_path": source["path"],
                "source_status": source["status"],
                "source_sha256": source["source_sha256"],
                "contract_path": f"NSI/chapitres/{source['chapter']}/contrat.yaml",
                "capacity_refs": source.get("capacity_refs", []),
                "protocol_digest": policy["protocol_digest"],
                "dependency_digest": aggregate_dependency_digest(class_digests),
                "dependency_digests": class_digests,
                "provenance": copy.deepcopy(finding["provenance"]),
                "dimensions": dimensions,
                "anomalies": anomalies,
                "execution_observation": observation,
                "publication_approval": False,
                "human_confirmation_required": True,
            }
        )
    document = {
        "artifact_type": "1nsi_content_reviews",
        "schema_version": 1,
        "manual": "1NSI",
        "protocol_digest": policy["protocol_digest"],
        "publication_approval": False,
        "human_confirmation_required": True,
        "entries": entries,
    }
    if len(entries) == 349:
        schema = json.loads((root / SCHEMA_PATH).read_text(encoding="utf-8"))
        errors = sorted(Draft202012Validator(schema).iter_errors(document), key=lambda error: list(error.path))
        if errors:
            raise ReviewValidationError(f"registre hors schema: {errors[0].message}")
    return document


def render_json(document: dict[str, Any]) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_summary(document: dict[str, Any]) -> str:
    counts = {
        dimension: {
            verdict: sum(
                entry["dimensions"][dimension]["verdict"] == verdict
                for entry in document["entries"]
            )
            for verdict in ("pass", "issue", "not_applicable", "human_confirmation_required")
        }
        for dimension in ("scientific", "pedagogical")
    }
    lines = [
        "# Synthese de revue 1NSI",
        "",
        f"Protocol digest: `{document['protocol_digest']}`",
        f"Entries: {len(document['entries'])}",
        "Publication approval: false",
        "Human confirmation required: true",
        "",
    ]
    for dimension in ("scientific", "pedagogical"):
        lines.append(f"## {dimension.title()}")
        lines.extend(f"- {verdict}: {count}" for verdict, count in counts[dimension].items())
        lines.append("")
    return "\n".join(lines)


def release_gate_allows(document: dict[str, Any], policy: dict[str, Any]) -> bool:
    decision = policy.get("decision", {})
    if (
        decision.get("publication_approval") is not True
        or decision.get("human_confirmation_required") is not False
        or decision.get("release_acceptance") is not True
    ):
        return False
    if (
        document.get("publication_approval") is not True
        or document.get("human_confirmation_required") is not False
    ):
        return False
    for entry in document.get("entries", []):
        if (
            entry.get("publication_approval") is not True
            or entry.get("human_confirmation_required") is not False
            or bool(entry.get("anomalies"))
        ):
            return False
        dimensions = entry.get("dimensions", {})
        if any(
            dimension.get("verdict") in {"issue", "human_confirmation_required"}
            for dimension in dimensions.values()
        ):
            return False
    return True


def load_findings(path: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("findings")
    if not isinstance(data, list):
        raise ReviewValidationError("findings absents ou invalides")
    return data


def _write_or_check(path: Path | None, content: str, check: bool) -> None:
    if path is None:
        raise ReviewValidationError("chemin de sortie manquant")
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            raise ReviewValidationError(f"sortie obsolete: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--findings", type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-summary", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--verify-scope", action="store_true")
    parser.add_argument("--release-gate", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        policy = load_policy(ROOT)
        if args.verify_scope:
            verify_scope(ROOT, policy)
        wants_register = any(
            (args.findings, args.output_json, args.output_summary, args.check, args.release_gate)
        )
        if not wants_register:
            return 0
        if args.findings is None:
            if args.release_gate:
                return 7
            raise ReviewValidationError("--findings requis")
        document = generate_register(load_findings(args.findings), ROOT, policy)
        if args.output_json or args.check:
            _write_or_check(args.output_json, render_json(document), args.check)
        if args.output_summary or args.check:
            _write_or_check(args.output_summary, render_summary(document), args.check)
        if args.release_gate:
            return 0 if release_gate_allows(document, policy) else 7
        return 0
    except (OSError, ReviewValidationError, yaml.YAMLError, json.JSONDecodeError) as error:
        print(f"review_1nsi_content: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
