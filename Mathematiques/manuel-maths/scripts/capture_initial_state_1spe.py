#!/usr/bin/env python3
"""Capture the immutable 1SPE release baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any


CATEGORIES = (
    "source_1spe",
    "referential",
    "contract",
    "directive",
    "report",
    "attestation",
)
ATTESTATION_CLASSES = ("reusable", "stale", "review_required")
DEFAULT_ORIGIN_REF = "41eaa74"
DEFAULT_CURRENT_REF = "ca16edb"
DEFAULT_SCOPE_MANIFEST_PATH = (
    Path(__file__).resolve().parents[1] / "release" / "baseline-scope-1spe.json"
)
DEFAULT_REMEDIATION_COMMITS = (
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
DEFAULT_TEST_EVIDENCE: dict[str, dict[str, Any]] = {
    "origin": {
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
    },
    "current": {
        "kind": "direct_execution",
        "command": ".venv/bin/python -m pytest -q",
        "exit_code": 0,
        "passed": 1946,
        "failed": 0,
        "skipped": 5,
        "summary": "1946 passed, 5 skipped",
        "provenance": (
            "Exécution directe sur le worktree propre au commit ca16edb, "
            "effectuée avant toute modification de Task 1B."
        ),
    },
}


class CaptureError(RuntimeError):
    """Raised when an immutable snapshot cannot be established."""


def _git_environment(git_root: Path) -> dict[str, str]:
    """Return a minimal deterministic environment for every Git subprocess."""

    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(git_root),
        "LANG": "C",
        "LC_ALL": "C",
        "TZ": "UTC",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_ASKPASS": "/bin/false",
        "SSH_ASKPASS": "/bin/false",
    }


def _run_git(
    git_root: Path,
    arguments: list[str],
    *,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=git_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=_git_environment(git_root),
    )
    if check and completed.returncode:
        diagnostic = completed.stderr.decode("utf-8", errors="replace").strip()
        raise CaptureError(
            f"git {' '.join(arguments)} a échoué"
            + (f" : {diagnostic}" if diagnostic else "")
        )
    return completed


def _decode_utf8(value: bytes, *, description: str) -> str:
    try:
        return value.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CaptureError(f"{description} n'est pas un UTF-8 sûr") from error


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _resolve_commit(git_root: Path, ref: str, *, label: str) -> str:
    completed = _run_git(
        git_root,
        ["rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}"],
        check=False,
    )
    if completed.returncode:
        raise CaptureError(f"commit {label} absent ou inaccessible : {ref}")
    commit = _decode_utf8(completed.stdout, description=f"commit {label}").strip()
    if len(commit) != 40:
        raise CaptureError(f"empreinte Git invalide pour le commit {label} : {commit}")
    return commit


def _git_context(root: Path) -> tuple[Path, str]:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise CaptureError(f"racine de projet invalide : {root}")
    git_root_raw = _run_git(root, ["rev-parse", "--show-toplevel"]).stdout
    git_root = Path(_decode_utf8(git_root_raw, description="racine Git").strip())
    git_root = git_root.resolve(strict=True)
    try:
        prefix = root.relative_to(git_root).as_posix()
    except ValueError as error:
        raise CaptureError("la racine demandée n'appartient pas au dépôt Git") from error
    return git_root, "" if prefix == "." else prefix


def _safe_relative_path(path: str) -> PurePosixPath:
    relative = PurePosixPath(path)
    if (
        not path
        or relative.is_absolute()
        or any(part in {"", ".", ".."} for part in relative.parts)
    ):
        raise CaptureError(f"chemin Git non sûr : {path!r}")
    return relative


def _tree_records(
    git_root: Path,
    project_prefix: str,
    commit: str,
) -> list[dict[str, str]]:
    arguments = ["ls-tree", "-r", "-z", "--full-tree", commit]
    if project_prefix:
        arguments.extend(["--", project_prefix])
    payload = _run_git(git_root, arguments).stdout
    prefix = f"{project_prefix}/" if project_prefix else ""
    records: list[dict[str, str]] = []
    for raw_record in payload.split(b"\0"):
        if not raw_record:
            continue
        metadata, separator, raw_path = raw_record.partition(b"\t")
        if not separator:
            raise CaptureError("sortie git ls-tree illisible")
        fields = metadata.split(b" ")
        if len(fields) != 3:
            raise CaptureError("métadonnées git ls-tree illisibles")
        mode, object_type, oid = (
            _decode_utf8(field, description="métadonnée Git") for field in fields
        )
        full_path = _decode_utf8(raw_path, description="chemin Git")
        if prefix:
            if not full_path.startswith(prefix):
                raise CaptureError(f"chemin hors projet retourné par Git : {full_path}")
            relative_path = full_path[len(prefix) :]
        else:
            relative_path = full_path
        _safe_relative_path(relative_path)
        if object_type != "blob":
            raise CaptureError(
                f"objet non fichier inattendu dans l'inventaire : {relative_path}"
            )
        records.append(
            {
                "mode": mode,
                "oid": oid,
                "path": relative_path,
            }
        )
    return records


def _read_blobs(git_root: Path, oids: set[str]) -> dict[str, bytes]:
    requested_oids = sorted(oids)
    completed = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=git_root,
        input=b"".join(oid.encode("ascii") + b"\n" for oid in requested_oids),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=_git_environment(git_root),
    )
    if completed.returncode:
        raise CaptureError(
            "git cat-file a échoué : "
            + completed.stderr.decode("utf-8", errors="replace").strip()
        )

    blobs: dict[str, bytes] = {}
    payload = completed.stdout
    offset = 0
    for requested_oid in requested_oids:
        header_end = payload.find(b"\n", offset)
        if header_end == -1:
            raise CaptureError(f"en-tête Git tronqué pour le blob {requested_oid}")
        header = payload[offset:header_end]
        offset = header_end + 1
        fields = header.split(b" ")
        if len(fields) != 3 or fields[1] != b"blob":
            raise CaptureError(
                f"blob Git inaccessible pendant la capture : {requested_oid}"
            )
        returned_oid = fields[0].decode("ascii")
        size = int(fields[2])
        content_end = offset + size
        content = payload[offset:content_end]
        terminator = payload[content_end : content_end + 1]
        if len(content) != size or terminator != b"\n":
            raise CaptureError(f"lecture Git tronquée pour le blob {requested_oid}")
        blobs[returned_oid] = content
        offset = content_end + 1
    if offset != len(payload):
        raise CaptureError("données Git résiduelles après la lecture des blobs")
    return blobs


def _changed_paths(
    git_root: Path,
    project_prefix: str,
    origin_commit: str,
    current_commit: str,
) -> list[str]:
    arguments = [
        "diff",
        "--name-only",
        "-z",
        origin_commit,
        current_commit,
    ]
    if project_prefix:
        arguments.extend(["--", project_prefix])
    prefix = f"{project_prefix}/" if project_prefix else ""
    changed: list[str] = []
    for raw_path in _run_git(git_root, arguments).stdout.split(b"\0"):
        if not raw_path:
            continue
        full_path = _decode_utf8(raw_path, description="chemin Git modifié")
        if prefix:
            if not full_path.startswith(prefix):
                raise CaptureError(f"chemin modifié hors projet : {full_path}")
            full_path = full_path[len(prefix) :]
        _safe_relative_path(full_path)
        changed.append(full_path)
    return sorted(set(changed))


def _glob_regex(pattern: str) -> re.Pattern[str]:
    _safe_relative_path(pattern.replace("*", "x"))
    escaped = re.escape(pattern)
    expression = escaped.replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
    return re.compile(f"^{expression}$")


def _matches(path: str, patterns: list[str]) -> bool:
    return any(_glob_regex(pattern).fullmatch(path) for pattern in patterns)


def load_scope_manifest(path: Path = DEFAULT_SCOPE_MANIFEST_PATH) -> dict[str, Any]:
    manifest_path = Path(path)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CaptureError(
            f"manifeste de périmètre inaccessible ou invalide : {manifest_path}"
        ) from error
    return load_scope_manifest_from_value(manifest)


def load_scope_manifest_from_value(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise CaptureError("le manifeste de périmètre doit être un objet JSON")
    if manifest.get("schema_version") != 1:
        raise CaptureError("version du manifeste de périmètre non prise en charge")
    universe = manifest.get("universe")
    rules = manifest.get("categories")
    if not isinstance(universe, dict) or not isinstance(rules, list):
        raise CaptureError("structure du manifeste de périmètre invalide")
    if set(universe) != {"include", "exclude"}:
        raise CaptureError("clés de l'univers du manifeste invalides")
    if not all(
        isinstance(universe[key], list)
        and all(isinstance(item, str) for item in universe[key])
        for key in ("include", "exclude")
    ):
        raise CaptureError("motifs d'univers invalides")
    seen_categories: list[str] = []
    for rule in rules:
        if not isinstance(rule, dict) or set(rule) != {
            "category",
            "include",
            "exclude",
        }:
            raise CaptureError("règle de catégorie invalide")
        category = rule["category"]
        if category not in CATEGORIES:
            raise CaptureError(f"catégorie de périmètre inconnue : {category}")
        if not all(
            isinstance(rule[key], list)
            and all(isinstance(item, str) for item in rule[key])
            for key in ("include", "exclude")
        ):
            raise CaptureError(f"motifs invalides pour la catégorie {category}")
        seen_categories.append(category)
    if sorted(seen_categories) != sorted(CATEGORIES):
        raise CaptureError("les six catégories doivent être déclarées exactement une fois")
    for pattern in [
        *universe["include"],
        *universe["exclude"],
        *[
            pattern
            for rule in rules
            for key in ("include", "exclude")
            for pattern in rule[key]
        ],
    ]:
        _glob_regex(pattern)
    return manifest


def _scope_analysis(
    records: list[dict[str, str]],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    universe = manifest["universe"]
    classification: dict[str, str] = {}
    candidate_records: list[dict[str, str]] = []
    unclassified: list[str] = []
    duplicates: list[dict[str, Any]] = []
    pollution: list[str] = []
    excluded: list[str] = []

    for record in records:
        path = record["path"]
        explicitly_excluded = _matches(path, universe["exclude"])
        included = _matches(path, universe["include"])
        candidate = included and not explicitly_excluded
        matching_categories = sorted(
            rule["category"]
            for rule in manifest["categories"]
            if _matches(path, rule["include"])
            and not _matches(path, rule["exclude"])
        )
        if explicitly_excluded:
            excluded.append(path)
        if not candidate:
            if matching_categories and not explicitly_excluded:
                pollution.append(path)
            continue
        candidate_records.append(record)
        if not matching_categories:
            unclassified.append(path)
        elif len(matching_categories) > 1:
            duplicates.append(
                {"path": path, "categories": matching_categories}
            )
        else:
            classification[path] = matching_categories[0]

    return {
        "candidate_records": candidate_records,
        "classification": classification,
        "unclassified_paths": sorted(unclassified),
        "duplicate_classifications": sorted(
            duplicates,
            key=lambda item: item["path"],
        ),
        "out_of_scope_pollution": sorted(pollution),
        "excluded_paths": sorted(excluded),
    }


def _safe_symlink_target(path: str, target_bytes: bytes) -> str:
    target = _decode_utf8(target_bytes, description=f"cible du lien {path}")
    pure_target = PurePosixPath(target)
    if pure_target.is_absolute():
        raise CaptureError(f"lien symbolique absolu interdit : {path} -> {target}")
    resolved_parts: list[str] = list(PurePosixPath(path).parent.parts)
    for part in pure_target.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if not resolved_parts:
                raise CaptureError(
                    f"lien symbolique sortant du projet : {path} -> {target}"
                )
            resolved_parts.pop()
        else:
            resolved_parts.append(part)
    return target


def _inventory(
    records: list[dict[str, str]],
    blobs: dict[str, bytes],
    classifications: dict[str, str],
) -> tuple[dict[str, Any], dict[str, bytes]]:
    entries: list[dict[str, Any]] = []
    scoped_blobs: dict[str, bytes] = {}
    for record in records:
        path = record["path"]
        if path not in classifications:
            continue
        content = blobs[record["oid"]]
        file_type = "symlink" if record["mode"] == "120000" else "regular"
        entry: dict[str, Any] = {
            "path": path,
            "category": classifications[path],
            "file_type": file_type,
            "git_mode": record["mode"],
            "git_blob_oid": record["oid"],
            "byte_size": len(content),
            "sha256": _sha256(content),
        }
        if file_type == "symlink":
            entry["symlink_target"] = _safe_symlink_target(path, content)
        entries.append(entry)
        scoped_blobs[path] = content
    entries.sort(key=lambda item: item["path"])
    counts = Counter(entry["category"] for entry in entries)
    inventory = {
        "entries": entries,
        "counts_by_category": {
            category: counts.get(category, 0) for category in CATEGORIES
        },
        "sha256": _sha256(_canonical_bytes(entries)),
    }
    return inventory, scoped_blobs


def _json_pointer(pointer: str, key: str) -> str:
    escaped = key.replace("~", "~0").replace("/", "~1")
    return f"{pointer}/{escaped}" if pointer else f"/{escaped}"


def _declared_fingerprints(value: Any, pointer: str = "") -> list[dict[str, str]]:
    fingerprints: list[dict[str, str]] = []
    if isinstance(value, dict):
        for key in sorted(value):
            item = value[key]
            child_pointer = _json_pointer(pointer, str(key))
            if (
                isinstance(item, str)
                and len(item) == 64
                and all(character in "0123456789abcdefABCDEF" for character in item)
                and ("sha256" in str(key).casefold() or str(key).casefold() == "hash")
            ):
                fingerprints.append(
                    {"json_pointer": child_pointer, "sha256": item.casefold()}
                )
            fingerprints.extend(_declared_fingerprints(item, child_pointer))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            fingerprints.extend(_declared_fingerprints(item, f"{pointer}/{index}"))
    return fingerprints


def _fingerprint_bindings(value: Any, pointer: str = "") -> list[dict[str, str]]:
    bindings: list[dict[str, str]] = []
    if isinstance(value, dict):
        for raw_key, raw_hash in value.items():
            key = str(raw_key)
            folded_key = key.casefold()
            if not (
                isinstance(raw_hash, str)
                and len(raw_hash) == 64
                and all(
                    character in "0123456789abcdefABCDEF"
                    for character in raw_hash
                )
                and ("sha256" in folded_key or folded_key == "hash")
            ):
                continue
            if folded_key in {"sha256", "hash"}:
                candidate_path_keys = ("path", "fichier")
            elif folded_key.endswith("_sha256"):
                stem = folded_key[: -len("_sha256")]
                candidate_path_keys = (f"{stem}_path", f"{stem}_file")
            else:
                candidate_path_keys = ()
            matching_path_key = next(
                (
                    path_key
                    for path_key in candidate_path_keys
                    if isinstance(value.get(path_key), str)
                ),
                None,
            )
            if matching_path_key is not None:
                bindings.append(
                    {
                        "json_pointer": pointer or "/",
                        "fingerprint_json_pointer": _json_pointer(pointer, key),
                        "path": value[matching_path_key],
                        "sha256": raw_hash.casefold(),
                    }
                )
        for key in sorted(value):
            bindings.extend(
                _fingerprint_bindings(
                    value[key],
                    _json_pointer(pointer, str(key)),
                )
            )
    elif isinstance(value, list):
        for index, item in enumerate(value):
            bindings.extend(_fingerprint_bindings(item, f"{pointer}/{index}"))
    return bindings


def _attestations(
    inventory: dict[str, Any],
    snapshot_blobs: dict[str, bytes],
    comparison_inventory: dict[str, Any],
) -> list[dict[str, Any]]:
    comparison_by_path = {
        entry["path"]: entry for entry in comparison_inventory["entries"]
    }
    comparison_hashes = {
        entry["path"]: entry["sha256"] for entry in comparison_inventory["entries"]
    }
    results: list[dict[str, Any]] = []
    for entry in inventory["entries"]:
        if entry["category"] != "attestation":
            continue
        path = entry["path"]
        content = snapshot_blobs[path]
        parsed: Any = None
        if path.casefold().endswith(".json"):
            try:
                parsed = json.loads(content.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                parsed = None
        declared = _declared_fingerprints(parsed) if parsed is not None else []
        bindings = _fingerprint_bindings(parsed) if parsed is not None else []
        verified: list[dict[str, str]] = []
        mismatched: list[dict[str, Any]] = []
        for binding in bindings:
            try:
                binding_path = _safe_relative_path(binding["path"]).as_posix()
            except CaptureError:
                mismatched.append(
                    {
                        **binding,
                        "current_sha256": None,
                        "reason": "unsafe_path",
                    }
                )
                continue
            current_hash = comparison_hashes.get(binding_path)
            if current_hash == binding["sha256"]:
                verified.append(binding)
            else:
                mismatched.append(
                    {
                        **binding,
                        "current_sha256": current_hash,
                        "reason": "missing_or_hash_mismatch",
                    }
                )
        comparison_entry = comparison_by_path.get(path)
        comparison_attestation_sha = (
            comparison_entry["sha256"] if comparison_entry is not None else None
        )
        bound_pointers = {
            binding["fingerprint_json_pointer"] for binding in bindings
        }
        unbound_declared = [
            fingerprint
            for fingerprint in declared
            if fingerprint["json_pointer"] not in bound_pointers
        ]
        if comparison_attestation_sha != entry["sha256"]:
            classification = "stale"
            justification = (
                "L'attestation a été modifiée ou supprimée depuis cet instantané."
            )
        elif mismatched:
            classification = "stale"
            justification = (
                "Au moins une empreinte déclarée ne correspond pas à l'objet courant."
            )
        elif unbound_declared:
            classification = "review_required"
            justification = (
                "Au moins une empreinte déclarée ne possède pas de liaison "
                "chemin–SHA-256 vérifiable."
            )
        elif declared and len(verified) == len(declared):
            classification = "reusable"
            justification = (
                "L'attestation et toutes ses empreintes déclarées "
                "correspondent à l'état courant."
            )
        else:
            classification = "review_required"
            justification = (
                "Aucune liaison chemin–SHA-256 vérifiable ne permet une réutilisation "
                "automatique."
            )
        results.append(
            {
                "path": path,
                "classification": classification,
                "justification": justification,
                "fingerprints": {
                    "attestation_sha256": entry["sha256"],
                    "comparison_attestation_sha256": comparison_attestation_sha,
                    "declared": declared,
                    "unbound_declared": unbound_declared,
                    "verified_bindings": verified,
                    "mismatched_bindings": mismatched,
                },
            }
        )
    return results


def _commit_metadata(git_root: Path, commit: str) -> dict[str, str]:
    format_string = "%H%x00%T%x00%aI%x00%cI%x00%s"
    raw = _run_git(
        git_root,
        ["show", "-s", f"--format={format_string}", commit],
    ).stdout.rstrip(b"\n")
    fields = raw.split(b"\0")
    if len(fields) != 5:
        raise CaptureError(f"métadonnées du commit illisibles : {commit}")
    sha, tree, authored_at, committed_at, subject = (
        _decode_utf8(field, description="métadonnée du commit") for field in fields
    )
    return {
        "commit_sha": sha,
        "git_tree_oid": tree,
        "authored_at": authored_at,
        "committed_at": committed_at,
        "subject": subject,
    }


def _test_execution(evidence: dict[str, Any], commit: str) -> dict[str, Any]:
    required = {
        "kind",
        "command",
        "exit_code",
        "passed",
        "failed",
        "skipped",
        "summary",
        "provenance",
    }
    missing = sorted(required - evidence.keys())
    if missing:
        raise CaptureError(f"preuve de tests incomplète : {', '.join(missing)}")
    failed = int(evidence["failed"])
    exit_code = int(evidence["exit_code"])
    state = "green" if failed == 0 and exit_code == 0 else "historical_red"
    return {
        "kind": evidence["kind"],
        "commit_sha": commit,
        "command": evidence["command"],
        "exit_code": exit_code,
        "passed": int(evidence["passed"]),
        "failed": failed,
        "skipped": int(evidence["skipped"]),
        "summary": evidence["summary"],
        "provenance": evidence["provenance"],
        "state": state,
    }


def _tags(git_root: Path, snapshot_commit: str) -> list[dict[str, Any]]:
    format_string = (
        "%(refname:short)%00%(objectname)%00%(*objectname)%00"
        "%(objecttype)%00%(creatordate:iso-strict)"
    )
    raw = _run_git(
        git_root,
        ["for-each-ref", f"--format={format_string}", "refs/tags"],
    ).stdout
    tags: list[dict[str, Any]] = []
    for line in raw.splitlines():
        if not line:
            continue
        fields = line.split(b"\0")
        if len(fields) != 5:
            raise CaptureError("métadonnées de tag Git illisibles")
        name, ref_oid, peeled_oid, object_type, created_at = (
            _decode_utf8(field, description="métadonnée du tag") for field in fields
        )
        if "1spe" not in name.casefold():
            continue
        target_commit = peeled_oid or ref_oid
        reachable = (
            _run_git(
                git_root,
                ["merge-base", "--is-ancestor", target_commit, snapshot_commit],
                check=False,
            ).returncode
            == 0
        )
        if not reachable:
            continue
        object_content = _run_git(git_root, ["cat-file", "-p", ref_oid]).stdout
        tags.append(
            {
                "name": name,
                "ref_object_oid": ref_oid,
                "target_commit_sha": target_commit,
                "object_type": object_type,
                "created_at": created_at,
                "object_sha256": _sha256(object_content),
                "reachable_from_snapshot": True,
            }
        )
    return sorted(tags, key=lambda item: item["name"])


def _remediation_history(
    git_root: Path,
    origin_commit: str,
    current_commit: str,
) -> list[dict[str, str]]:
    raw = _run_git(
        git_root,
        [
            "log",
            "--reverse",
            "--ancestry-path",
            "--format=%H%x00%P%x00%aI%x00%cI%x00%s",
            f"{origin_commit}..{current_commit}",
        ],
    ).stdout
    history: list[dict[str, str]] = []
    for line in raw.splitlines():
        if not line:
            continue
        fields = line.split(b"\0")
        if len(fields) != 5:
            raise CaptureError("historique de remédiation Git illisible")
        sha, parents, authored_at, committed_at, subject = (
            _decode_utf8(field, description="historique Git") for field in fields
        )
        if subject.startswith("[CHARTE][V5.B-it2]"):
            kind = "baseline_remediation"
        elif subject.startswith("[1SPE][BAT]"):
            kind = "release_preflight"
        else:
            raise CaptureError(
                f"commit entre origine et état courant non classé : {sha} {subject}"
            )
        history.append(
            {
                "commit_sha": sha,
                "parent_commit_sha": parents.split()[0],
                "kind": kind,
                "authored_at": authored_at,
                "committed_at": committed_at,
                "subject": subject,
            }
        )
    return history


def _working_tree(
    git_root: Path,
    project_prefix: str,
    excluded_paths: set[str],
) -> dict[str, Any]:
    arguments = ["status", "--porcelain=v1", "-z", "--untracked-files=all"]
    if project_prefix:
        arguments.extend(["--", project_prefix])
    raw_records = _run_git(git_root, arguments).stdout.split(b"\0")
    prefix = f"{project_prefix}/" if project_prefix else ""
    entries: list[dict[str, str]] = []

    def project_path(full_path: str) -> str | None:
        if prefix:
            if not full_path.startswith(prefix):
                return None
            path = full_path[len(prefix) :]
        else:
            path = full_path
        _safe_relative_path(path)
        return path

    index = 0
    while index < len(raw_records):
        raw_record = raw_records[index]
        index += 1
        if not raw_record:
            continue
        if len(raw_record) < 4:
            raise CaptureError("sortie git status illisible")
        status = _decode_utf8(raw_record[:2], description="statut Git")
        full_path = _decode_utf8(raw_record[3:], description="chemin de statut Git")
        path = project_path(full_path)
        if status[0] in {"R", "C"}:
            if index >= len(raw_records) or not raw_records[index]:
                raise CaptureError("renommage Git incomplet dans le statut")
            source_full_path = _decode_utf8(
                raw_records[index],
                description="ancien chemin de statut Git",
            )
            index += 1
            source_path = project_path(source_full_path)
            operation = "rename" if status[0] == "R" else "copy"
            for candidate_path, role in (
                (path, f"{operation}_destination"),
                (source_path, f"{operation}_source"),
            ):
                if (
                    candidate_path is not None
                    and candidate_path not in excluded_paths
                ):
                    entries.append(
                        {
                            "path": candidate_path,
                            "status": status,
                            "role": role,
                        }
                    )
        elif path is not None and path not in excluded_paths:
            entries.append(
                {"path": path, "status": status, "role": "changed"}
            )
    entries.sort(key=lambda item: (item["path"], item["status"], item["role"]))
    return {
        "status": "dirty" if entries else "clean",
        "paths": entries,
    }


def capture_repository(
    *,
    root: Path,
    origin_ref: str,
    current_ref: str,
    test_evidence: dict[str, dict[str, Any]],
    dirty_policy: str = "record",
    excluded_dirty_paths: tuple[str, ...] = (),
    scope_manifest: dict[str, Any] | None = None,
    scope_manifest_path: Path = DEFAULT_SCOPE_MANIFEST_PATH,
) -> dict[str, Any]:
    """Build deterministic origin/current snapshots from immutable Git objects."""

    root = Path(root).resolve(strict=True)
    git_root, project_prefix = _git_context(root)
    capture_head_commit = _resolve_commit(
        git_root,
        "HEAD",
        label="HEAD de capture",
    )
    if dirty_policy not in {"record", "fail"}:
        raise CaptureError(f"politique de dépôt sale inconnue : {dirty_policy}")
    excluded = {
        _safe_relative_path(path).as_posix() for path in excluded_dirty_paths
    }
    working_tree = _working_tree(git_root, project_prefix, excluded)
    if dirty_policy == "fail" and working_tree["status"] == "dirty":
        raise CaptureError("dépôt sale : la politique demandée impose un arrêt")
    origin_commit = _resolve_commit(git_root, origin_ref, label="origine")
    current_commit = _resolve_commit(git_root, current_ref, label="courant")
    ancestry = _run_git(
        git_root,
        ["merge-base", "--is-ancestor", origin_commit, current_commit],
        check=False,
    )
    if ancestry.returncode:
        raise CaptureError(
            "le commit origine n'est pas un ancêtre du commit courant"
        )

    changed_paths = _changed_paths(
        git_root,
        project_prefix,
        origin_commit,
        current_commit,
    )
    origin_records = _tree_records(git_root, project_prefix, origin_commit)
    current_records = _tree_records(git_root, project_prefix, current_commit)
    if scope_manifest is None:
        scope_manifest = load_scope_manifest(scope_manifest_path)
        manifest_bytes = Path(scope_manifest_path).read_bytes()
    else:
        manifest_bytes = _canonical_bytes(scope_manifest)
        scope_manifest = load_scope_manifest_from_value(scope_manifest)
    origin_scope = _scope_analysis(origin_records, scope_manifest)
    current_scope = _scope_analysis(current_records, scope_manifest)
    all_oids = {
        record["oid"]
        for analysis in (origin_scope, current_scope)
        for record in analysis["candidate_records"]
        if record["path"] in analysis["classification"]
    }
    blobs = _read_blobs(git_root, all_oids)
    origin_inventory, origin_blobs = _inventory(
        origin_scope["candidate_records"],
        blobs,
        origin_scope["classification"],
    )
    current_inventory, current_blobs = _inventory(
        current_scope["candidate_records"],
        blobs,
        current_scope["classification"],
    )

    origin_attestations = _attestations(
        origin_inventory,
        origin_blobs,
        current_inventory,
    )
    current_attestations = _attestations(
        current_inventory,
        current_blobs,
        current_inventory,
    )
    origin_metadata = _commit_metadata(git_root, origin_commit)
    current_metadata = _commit_metadata(git_root, current_commit)
    remediation_history = _remediation_history(
        git_root,
        origin_commit,
        current_commit,
    )
    if origin_commit.startswith(DEFAULT_ORIGIN_REF) and current_commit.startswith(
        DEFAULT_CURRENT_REF
    ):
        actual_remediations = tuple(
            (item["commit_sha"][:7], item["kind"]) for item in remediation_history
        )
        if actual_remediations != DEFAULT_REMEDIATION_COMMITS:
            raise CaptureError(
                "la chaîne de remédiations réelle diverge du contrat immuable"
            )
    report = {
        "schema_version": 1,
        "status": "initial_snapshot",
        "scope": {
            "project_path": project_prefix or ".",
            "manifest_path": "release/baseline-scope-1spe.json",
            "manifest_sha256": _sha256(manifest_bytes),
            "categories": list(CATEGORIES),
            "changed_paths_between_snapshots": changed_paths,
            "candidate_counts": {
                "origin": len(origin_scope["candidate_records"]),
                "current": len(current_scope["candidate_records"]),
            },
            "excluded_counts": {
                "origin": len(origin_scope["excluded_paths"]),
                "current": len(current_scope["excluded_paths"]),
            },
        },
        "origin": {
            "label": "origin_immutable",
            **origin_metadata,
            "inventory": origin_inventory,
            "tags": _tags(git_root, origin_commit),
            "attestations": origin_attestations,
            "test_execution": _test_execution(
                test_evidence["origin"],
                origin_commit,
            ),
        },
        "current": {
            "label": "current_preflight",
            **current_metadata,
            "inventory": current_inventory,
            "tags": _tags(git_root, current_commit),
            "attestations": current_attestations,
            "test_execution": _test_execution(
                test_evidence["current"],
                current_commit,
            ),
        },
        "remediation_history": remediation_history,
        "capture_context": {
            "capture_head_commit": capture_head_commit,
            "dirty_policy": dirty_policy,
            "working_tree": working_tree,
        },
        "completeness": {
            "duplicate_classifications": sorted(
                [
                    *origin_scope["duplicate_classifications"],
                    *current_scope["duplicate_classifications"],
                ],
                key=lambda item: (item["path"], item["categories"]),
            ),
            "unclassified_paths": sorted(
                set(
                    [
                        *origin_scope["unclassified_paths"],
                        *current_scope["unclassified_paths"],
                    ]
                )
            ),
            "out_of_scope_pollution": sorted(
                set(
                    [
                        *origin_scope["out_of_scope_pollution"],
                        *current_scope["out_of_scope_pollution"],
                    ]
                )
            ),
        },
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    """Render a concise, deterministic human-readable baseline."""

    origin = report["origin"]
    current = report["current"]
    lines = [
        "# Baseline immuable 1SPE",
        "",
        "## Deux vues distinctes",
        "",
        (
            f"- Origine immuable : `{origin['commit_sha']}` — "
            f"{origin['test_execution']['summary']} "
            f"({origin['test_execution']['kind']}, historique non rejoué)."
        ),
        (
            f"- État courant préflight : `{current['commit_sha']}` — "
            f"{current['test_execution']['summary']} "
            f"({current['test_execution']['kind']})."
        ),
        (
            "- Arbre de travail au moment de la capture : "
            f"`{report['capture_context']['working_tree']['status']}` "
            f"(politique `{report['capture_context']['dirty_policy']}`)."
        ),
        (
            "- HEAD matériel de capture : "
            f"`{report['capture_context']['capture_head_commit']}`."
        ),
        "",
        "L'état courant n'est jamais présenté comme l'état initial intact.",
        "",
        "## Remédiations ordonnées",
        "",
        "| Commit | Classe | Date déterministe | Sujet |",
        "|---|---|---|---|",
    ]
    for item in report["remediation_history"]:
        lines.append(
            f"| `{item['commit_sha']}` | `{item['kind']}` | "
            f"{item['committed_at']} | {item['subject'].replace('|', '&#124;')} |"
        )
    lines.extend(
        [
            "",
            "## Inventaires",
            "",
            "| Vue | Entrées | SHA-256 inventaire | Tags 1SPE |",
            "|---|---:|---|---:|",
            (
                f"| Origine | {len(origin['inventory']['entries'])} | "
                f"`{origin['inventory']['sha256']}` | {len(origin['tags'])} |"
            ),
            (
                f"| Courant | {len(current['inventory']['entries'])} | "
                f"`{current['inventory']['sha256']}` | {len(current['tags'])} |"
            ),
            "",
            "## Attestations",
            "",
            "| Vue | Réutilisables | Périmées | Revue requise |",
            "|---|---:|---:|---:|",
        ]
    )
    for label, snapshot in (("Origine", origin), ("Courant", current)):
        counts = Counter(
            item["classification"] for item in snapshot["attestations"]
        )
        lines.append(
            f"| {label} | {counts['reusable']} | {counts['stale']} | "
            f"{counts['review_required']} |"
        )
    completeness = report["completeness"]
    lines.append("")
    if not any(completeness.values()):
        lines.append(
            "Zéro chemin du périmètre non classé, zéro double classement "
            "et zéro pollution hors univers."
        )
    else:
        lines.append(
            "Capture bloquée par la complétude : "
            f"{len(completeness['unclassified_paths'])} non classé(s), "
            f"{len(completeness['duplicate_classifications'])} double(s) "
            "classement(s), "
            f"{len(completeness['out_of_scope_pollution'])} pollution(s) "
            "hors univers."
        )
    lines.append("")
    return "\n".join(lines)


def _lexical_output(root: Path, requested: Path) -> Path:
    if ".." in requested.parts:
        raise CaptureError(f"chemin de sortie non sûr : {requested}")
    candidate = requested if requested.is_absolute() else root / requested
    candidate = Path(os.path.abspath(candidate))
    evidence_directory = root / "validations" / "release-1spe"
    try:
        candidate.relative_to(evidence_directory)
    except ValueError as error:
        raise CaptureError(
            "les sorties sont limitées à validations/release-1spe : "
            f"{requested}"
        ) from error
    return candidate


def _reject_unsafe_output_components(root: Path, output: Path) -> None:
    relative = output.relative_to(root)
    current = root
    for index, component in enumerate(relative.parts):
        current /= component
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError:
            if index != len(relative.parts) - 1:
                raise CaptureError(
                    f"répertoire parent de sortie absent : {current}"
                )
            continue
        if stat.S_ISLNK(mode):
            raise CaptureError(
                f"composant symbolique interdit dans une sortie : {current}"
            )
        if index == len(relative.parts) - 1:
            if not stat.S_ISREG(mode):
                raise CaptureError(
                    f"la sortie existante n'est pas un fichier régulier : {current}"
                )
        elif not stat.S_ISDIR(mode):
            raise CaptureError(
                f"le parent de sortie n'est pas un répertoire : {current}"
            )


def _ensure_evidence_directory(root: Path) -> None:
    current = root
    for component in ("validations", "release-1spe"):
        current /= component
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError:
            os.mkdir(current, mode=0o755)
            mode = os.lstat(current).st_mode
        if stat.S_ISLNK(mode):
            raise CaptureError(
                f"composant symbolique interdit dans une sortie : {current}"
            )
        if not stat.S_ISDIR(mode):
            raise CaptureError(
                f"le parent de sortie n'est pas un répertoire : {current}"
            )


def _validate_output_pair(
    root: Path,
    json_requested: Path,
    markdown_requested: Path,
) -> tuple[Path, Path]:
    """Validate two publication targets without following any symlink."""

    root = root.resolve(strict=True)
    json_output = _lexical_output(root, json_requested)
    markdown_output = _lexical_output(root, markdown_requested)
    if json_output == markdown_output:
        raise CaptureError("les sorties JSON et Markdown doivent être distinctes")
    if (
        json_output in markdown_output.parents
        or markdown_output in json_output.parents
    ):
        raise CaptureError(
            "une sortie ne peut pas être l'ancêtre de l'autre sortie"
        )
    for output in (json_output, markdown_output):
        _reject_unsafe_output_components(root, output)
    return json_output, markdown_output


def _prepared_file(path: Path, content: bytes, *, prefix: str) -> Path:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=prefix,
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o644)
        return temporary
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_write_pair(
    first_path: Path,
    first_content: bytes,
    second_path: Path,
    second_content: bytes,
) -> None:
    """Publish a pair atomically from the caller's point of view.

    Both new files and any recovery copies are durable before the first
    replacement.  If either replacement fails, the complete prior pair is
    restored (or both newly-created destinations are removed).
    """

    paths = (first_path, second_path)
    contents = (first_content, second_content)
    existed: list[bool] = []
    for path in paths:
        try:
            mode = os.lstat(path).st_mode
        except FileNotFoundError:
            existed.append(False)
            continue
        existed.append(True)
        if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
            raise CaptureError(
                f"la sortie existante n'est pas un fichier régulier : {path}"
            )
    prepared: list[Path] = []
    backups: list[Path | None] = []
    try:
        for path, content in zip(paths, contents, strict=True):
            prepared.append(
                _prepared_file(path, content, prefix=f".{path.name}.new.")
            )
        for path, was_present in zip(paths, existed, strict=True):
            backups.append(
                _prepared_file(
                    path,
                    path.read_bytes(),
                    prefix=f".{path.name}.backup.",
                )
                if was_present
                else None
            )
        published = 0
        try:
            for temporary, destination in zip(
                prepared,
                paths,
                strict=True,
            ):
                os.replace(temporary, destination)
                published += 1
            for directory in {path.parent for path in paths}:
                _fsync_directory(directory)
        except BaseException:
            for index in range(published - 1, -1, -1):
                destination = paths[index]
                backup = backups[index]
                if backup is None:
                    destination.unlink(missing_ok=True)
                else:
                    os.replace(backup, destination)
            for directory in {path.parent for path in paths}:
                _fsync_directory(directory)
            raise
    finally:
        for temporary in [*prepared, *backups]:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


RFC3339_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:"
    r"\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


def _is_rfc3339(value: object) -> bool:
    if not isinstance(value, str) or not RFC3339_PATTERN.fullmatch(value):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _require_rfc3339(value: str, *, field: str) -> None:
    if not _is_rfc3339(value):
        raise CaptureError(f"date RFC 3339 invalide pour {field} : {value!r}")


def _validate_attestation_semantics(
    snapshot: dict[str, Any],
    comparison: dict[str, Any],
    *,
    label: str,
) -> None:
    entries = snapshot["inventory"]["entries"]
    inventory_by_path = {entry["path"]: entry for entry in entries}
    comparison_by_path = {
        entry["path"]: entry for entry in comparison["inventory"]["entries"]
    }
    expected_paths = sorted(
        entry["path"]
        for entry in entries
        if entry["category"] == "attestation"
    )
    attestations = snapshot["attestations"]
    actual_paths = [item["path"] for item in attestations]
    if actual_paths != expected_paths or len(actual_paths) != len(set(actual_paths)):
        raise CaptureError(
            f"couverture des attestations incohérente pour {label}"
        )

    for attestation in attestations:
        path = attestation["path"]
        fingerprints = attestation["fingerprints"]
        entry = inventory_by_path[path]
        comparison_entry = comparison_by_path.get(path)
        comparison_sha = (
            comparison_entry["sha256"] if comparison_entry is not None else None
        )
        if fingerprints["attestation_sha256"] != entry["sha256"]:
            raise CaptureError(
                f"empreinte d'attestation incohérente pour {label}:{path}"
            )
        if fingerprints["comparison_attestation_sha256"] != comparison_sha:
            raise CaptureError(
                f"empreinte de comparaison incohérente pour {label}:{path}"
            )

        declared = fingerprints["declared"]
        declared_by_pointer = {
            item["json_pointer"]: item["sha256"] for item in declared
        }
        if len(declared_by_pointer) != len(declared):
            raise CaptureError(
                f"pointeurs d'empreintes déclarées dupliqués pour {label}:{path}"
            )
        bound_pointers: set[str] = set()
        for key in ("verified_bindings", "mismatched_bindings"):
            bindings = fingerprints[key]
            for binding in bindings:
                pointer = binding["fingerprint_json_pointer"]
                if (
                    pointer not in declared_by_pointer
                    or pointer in bound_pointers
                ):
                    raise CaptureError(
                        f"partition des empreintes incohérente pour {label}:{path}"
                    )
                bound_pointers.add(pointer)
        expected_unbound = [
            item
            for item in declared
            if item["json_pointer"] not in bound_pointers
        ]
        if fingerprints["unbound_declared"] != expected_unbound:
            raise CaptureError(
                f"partition des empreintes incohérente pour {label}:{path}"
            )

        for binding in fingerprints["verified_bindings"]:
            current_entry = comparison_by_path.get(binding["path"])
            if (
                declared_by_pointer[binding["fingerprint_json_pointer"]]
                != binding["sha256"]
                or current_entry is None
                or current_entry["sha256"] != binding["sha256"]
            ):
                raise CaptureError(
                    f"liaison vérifiée incohérente pour {label}:{path}"
                )
        for binding in fingerprints["mismatched_bindings"]:
            if (
                declared_by_pointer[binding["fingerprint_json_pointer"]]
                != binding["sha256"]
            ):
                raise CaptureError(
                    f"liaison périmée incohérente pour {label}:{path}"
                )
            if binding["reason"] == "unsafe_path":
                try:
                    _safe_relative_path(binding["path"])
                except CaptureError:
                    path_is_unsafe = True
                else:
                    path_is_unsafe = False
                if not path_is_unsafe or binding["current_sha256"] is not None:
                    raise CaptureError(
                        f"liaison périmée incohérente pour {label}:{path}"
                    )
                continue
            try:
                _safe_relative_path(binding["path"])
            except CaptureError as error:
                raise CaptureError(
                    f"liaison périmée incohérente pour {label}:{path}"
                ) from error
            current_entry = comparison_by_path.get(binding["path"])
            current_sha = (
                current_entry["sha256"] if current_entry is not None else None
            )
            if (
                binding["current_sha256"] != current_sha
                or binding["sha256"] == current_sha
            ):
                raise CaptureError(
                    f"liaison périmée incohérente pour {label}:{path}"
                )

        if comparison_sha != entry["sha256"]:
            expected_classification = "stale"
        elif fingerprints["mismatched_bindings"]:
            expected_classification = "stale"
        elif fingerprints["unbound_declared"]:
            expected_classification = "review_required"
        elif declared and len(fingerprints["verified_bindings"]) == len(declared):
            expected_classification = "reusable"
        else:
            expected_classification = "review_required"
        if attestation["classification"] != expected_classification:
            raise CaptureError(
                f"verdict d'attestation incohérent pour {label}:{path}"
            )


def validate_report_semantics(report: dict[str, Any]) -> None:
    """Validate invariants that JSON Schema cannot express across fields."""

    for label in ("origin", "current"):
        snapshot = report[label]
        for field in ("authored_at", "committed_at"):
            _require_rfc3339(snapshot[field], field=f"{label}.{field}")
        for index, tag in enumerate(snapshot["tags"]):
            _require_rfc3339(
                tag["created_at"],
                field=f"{label}.tags[{index}].created_at",
            )
        if snapshot["test_execution"]["commit_sha"] != snapshot["commit_sha"]:
            raise CaptureError(
                f"preuve de test non rattachée au snapshot {label}"
            )

        entries = snapshot["inventory"]["entries"]
        paths = [entry["path"] for entry in entries]
        if paths != sorted(paths) or len(paths) != len(set(paths)):
            raise CaptureError(
                f"chemins d'inventaire non uniques ou non triés pour {label}"
            )
        expected_counts = Counter(entry["category"] for entry in entries)
        if snapshot["inventory"]["counts_by_category"] != {
            category: expected_counts.get(category, 0)
            for category in CATEGORIES
        }:
            raise CaptureError(f"compteurs d'inventaire incohérents pour {label}")
        if snapshot["inventory"]["sha256"] != _sha256(
            _canonical_bytes(entries)
        ):
            raise CaptureError(
                f"empreinte canonique d'inventaire incohérente pour {label}"
            )

    history = report["remediation_history"]
    expected_parent = report["origin"]["commit_sha"]
    seen_commits: set[str] = set()
    for index, item in enumerate(history):
        for field in ("authored_at", "committed_at"):
            _require_rfc3339(
                item[field],
                field=f"remediation_history[{index}].{field}",
            )
        if (
            item["parent_commit_sha"] != expected_parent
            or item["commit_sha"] in seen_commits
        ):
            raise CaptureError("chaîne de remédiation parentale incohérente")
        seen_commits.add(item["commit_sha"])
        expected_parent = item["commit_sha"]
    if expected_parent != report["current"]["commit_sha"]:
        raise CaptureError(
            "chaîne de remédiation non raccordée au commit courant"
        )

    _validate_attestation_semantics(
        report["origin"],
        report["current"],
        label="origin",
    )
    _validate_attestation_semantics(
        report["current"],
        report["current"],
        label="current",
    )


def _validate_report(report: dict[str, Any], schema_path: Path) -> None:
    try:
        import jsonschema
    except ImportError as error:
        raise CaptureError("jsonschema est requis pour valider la baseline") from error
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    format_checker = jsonschema.FormatChecker()
    format_checker.checkers["date-time"] = (_is_rfc3339, ())
    jsonschema.Draft202012Validator(
        schema,
        format_checker=format_checker,
    ).validate(report)
    validate_report_semantics(report)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Capture les vues immuables origine/courant de la release 1SPE."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--origin-ref", default=DEFAULT_ORIGIN_REF)
    parser.add_argument("--current-ref", default=DEFAULT_CURRENT_REF)
    parser.add_argument("--evidence-json", type=Path)
    parser.add_argument(
        "--json",
        dest="json_output",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--markdown",
        dest="markdown_output",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--dirty-policy",
        choices=("record", "fail"),
        default="record",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        root = arguments.root.resolve(strict=True)
        _ensure_evidence_directory(root)
        json_output, markdown_output = _validate_output_pair(
            root,
            arguments.json_output,
            arguments.markdown_output,
        )
        json_relative = json_output.relative_to(root).as_posix()
        markdown_relative = markdown_output.relative_to(root).as_posix()
        evidence = DEFAULT_TEST_EVIDENCE
        if arguments.evidence_json is not None:
            evidence = json.loads(
                arguments.evidence_json.read_text(encoding="utf-8")
            )
        report = capture_repository(
            root=root,
            origin_ref=arguments.origin_ref,
            current_ref=arguments.current_ref,
            test_evidence=evidence,
            dirty_policy=arguments.dirty_policy,
            excluded_dirty_paths=(json_relative, markdown_relative),
        )
        schema_path = Path(__file__).resolve().parents[1] / "schemas" / (
            "baseline_1spe.schema.json"
        )
        _validate_report(report, schema_path)
        json_content = (
            json.dumps(
                report,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8")
        markdown_content = render_markdown(report).encode("utf-8")
        _atomic_write_pair(
            json_output,
            json_content,
            markdown_output,
            markdown_content,
        )
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "json": json_relative,
                    "markdown": markdown_relative,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0
    except (
        CaptureError,
        OSError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
    ) as error:
        print(f"baseline 1SPE bloquée : {error}", file=sys.stderr)
        return 2
    except Exception as error:
        if error.__class__.__module__.startswith("jsonschema"):
            print(f"baseline 1SPE bloquée : schéma invalide : {error}", file=sys.stderr)
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
