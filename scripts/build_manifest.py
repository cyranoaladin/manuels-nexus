"""Secure transactional writer for already-proved observed build evidence.

Assembler integration contract::

    python scripts/build_manifest.py --receipt path/to/build-receipt.json

The receipt must be emitted only after the assembler has completed compilation
and preflight.  This entrypoint distrusts all derived assertions: it recomputes
Git provenance, source/model digests, PDF digest and page count.  Because no
current assembler lets this process directly observe the compilation command,
the production entrypoint deliberately refuses publication after validation.
That integration remains a release debt while the manifest stays empty.
"""

from __future__ import annotations

import argparse
import errno
import fcntl
import hashlib
import json
import os
import secrets
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Mapping


_DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
_TEMP_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
_MANIFEST_RELATIVE = Path("audit/BUILD_MANIFEST.json")
_RECEIPT_FIELDS = {
    "compile_succeeded",
    "fls_path",
    "gates",
    "generated_dependencies",
    "log_path",
    "manual",
    "pdf_path",
    "preflight_report",
    "preflight_succeeded",
    "tool_versions",
    "variant",
}


class BuildManifestError(RuntimeError):
    """Refusal to record unproved or inconsistent build evidence."""


def build_state_digest(builds: list[Mapping[str, Any]]) -> str:
    canonical = json.dumps(
        builds,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def _repository_root(manifest_path: Path) -> Path:
    try:
        completed = subprocess.run(
            [
                "git",
                "-C",
                str(manifest_path.parent),
                "rev-parse",
                "--show-toplevel",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BuildManifestError("dépôt Git indisponible") from exc
    root = Path(completed.stdout.strip()).resolve(strict=True)
    requested = Path(os.path.abspath(manifest_path))
    expected = root / _MANIFEST_RELATIVE
    if requested != expected:
        raise BuildManifestError(
            f"chemin manifeste hors destination canonique: {requested}"
        )
    return root


def _git_lock_path(root: Path) -> Path:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--git-path", "nexus-build.lock"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BuildManifestError("chemin de verrou Git indisponible") from exc
    path = Path(completed.stdout.strip())
    return path if path.is_absolute() else root / path


def _git_head(root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BuildManifestError("HEAD Git indisponible") from exc
    return completed.stdout.strip()


def _is_manifest_internal_path(path: str) -> bool:
    return (
        path == _MANIFEST_RELATIVE.as_posix()
        or path.startswith("audit/.BUILD_MANIFEST.json.")
    )


def _status_is_dirty_outside_manifest(payload: bytes) -> bool:
    fields = payload.split(b"\0")
    index = 0
    while index < len(fields):
        field = fields[index]
        index += 1
        if not field or len(field) < 4:
            continue
        marker = field[:2].decode("ascii", errors="replace")
        paths = [
            field[3:].decode("utf-8", errors="surrogateescape")
        ]
        if "R" in marker or "C" in marker:
            if index < len(fields) and fields[index]:
                paths.append(
                    fields[index].decode(
                        "utf-8",
                        errors="surrogateescape",
                    )
                )
                index += 1
        if any(not _is_manifest_internal_path(path) for path in paths):
            return True
    return False


def _git_state(root: Path) -> tuple[str, str, bool]:
    try:
        head = _git_head(root)
        branch = subprocess.run(
            ["git", "-C", str(root), "branch", "--show-current"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).stdout.strip()
        status_payload = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
                "-z",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BuildManifestError("état Git indisponible") from exc
    if not branch:
        raise BuildManifestError("branche Git détachée ou indisponible")
    return head, branch, _status_is_dirty_outside_manifest(status_payload)


def _git_evidence_fingerprint(root: Path) -> str:
    try:
        payload = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
                "-z",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BuildManifestError("état détaillé Git indisponible") from exc
    fields = payload.split(b"\0")
    entries: list[tuple[str, str, str]] = []
    index = 0
    while index < len(fields):
        field = fields[index]
        index += 1
        if not field or len(field) < 4:
            continue
        marker = field[:2].decode("ascii", errors="replace")
        paths = [
            field[3:].decode("utf-8", errors="surrogateescape")
        ]
        if "R" in marker or "C" in marker:
            if index < len(fields) and fields[index]:
                paths.append(
                    fields[index].decode(
                        "utf-8",
                        errors="surrogateescape",
                    )
                )
                index += 1
        for path in paths:
            if _is_manifest_internal_path(path):
                continue
            absolute = root / path
            try:
                metadata = absolute.lstat()
            except OSError:
                evidence = "missing"
            else:
                if stat.S_ISREG(metadata.st_mode):
                    digest = hashlib.sha256()
                    try:
                        with absolute.open("rb") as stream:
                            while chunk := stream.read(1024 * 1024):
                                digest.update(chunk)
                    except OSError as exc:
                        raise BuildManifestError(
                            f"preuve Git illisible: {path}"
                        ) from exc
                    evidence = f"file:{metadata.st_nlink}:{digest.hexdigest()}"
                elif stat.S_ISLNK(metadata.st_mode):
                    evidence = f"symlink:{os.readlink(absolute)}"
                else:
                    evidence = f"mode:{stat.S_IFMT(metadata.st_mode)}"
            entries.append((marker, path, evidence))
    canonical = json.dumps(
        sorted(entries),
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8", errors="surrogateescape")
    return hashlib.sha256(canonical).hexdigest()


def _fingerprint(
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


def _directory_fingerprint(value: os.stat_result) -> tuple[int, int, int]:
    return value.st_dev, value.st_ino, stat.S_IFMT(value.st_mode)


def _read_descriptor(descriptor: int) -> bytes:
    os.lseek(descriptor, 0, os.SEEK_SET)
    chunks: list[bytes] = []
    while chunk := os.read(descriptor, 1024 * 1024):
        chunks.append(chunk)
    return b"".join(chunks)


def _load_manifest_bytes(payload: bytes) -> dict[str, Any]:
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise BuildManifestError("manifeste illisible") from exc
    if not isinstance(value, dict) or not isinstance(value.get("builds"), list):
        raise BuildManifestError("manifeste incomplet")
    return value


def _same_envelope(current: Mapping[str, Any], expected: Mapping[str, Any]) -> bool:
    fields = (
        "artifact_type",
        "generated_by",
        "model_digest",
        "schema_ref",
        "schema_version",
        "source_digest",
    )
    return all(current.get(field) == expected.get(field) for field in fields)


def _validate_build_shape(build: Mapping[str, Any]) -> None:
    required = {
        "excluded_objects",
        "gates",
        "generated_dependencies",
        "generated_dependency_digests",
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
    }
    if set(build) != required:
        raise BuildManifestError("build incomplet ou champs inattendus")
    for field in (
        "excluded_objects",
        "generated_dependencies",
        "included_objects",
        "ordered_trace",
    ):
        value = build[field]
        if (
            not isinstance(value, list)
            or any(not isinstance(item, str) or not item for item in value)
            or len(value) != len(set(value))
        ):
            raise BuildManifestError(f"{field} invalide")
    dependency_digests = build.get("generated_dependency_digests")
    if (
        not isinstance(dependency_digests, Mapping)
        or set(dependency_digests) != set(build["generated_dependencies"])
        or any(
            not isinstance(value, str)
            or not value.startswith("sha256:")
            or len(value) != 71
            for value in dependency_digests.values()
        )
    ):
        raise BuildManifestError("generated_dependency_digests invalide")
    if build["ordered_trace"] != build["included_objects"]:
        raise BuildManifestError("ordered_trace incohérente")
    gates = build.get("gates")
    if not isinstance(gates, Mapping):
        raise BuildManifestError("gates invalides")
    for gate in ("compile", "preflight"):
        value = gates.get(gate)
        if not isinstance(value, Mapping) or value.get("passed") is not True:
            raise BuildManifestError(f"preuve {gate} absente ou rouge")


def _write_all(descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("écriture nulle")
        view = view[written:]
    os.fsync(descriptor)


def _parent_is_pinned(
    root_descriptor: int,
    audit_fingerprint: tuple[int, int, int],
) -> bool:
    reopened = -1
    try:
        reopened = os.open("audit", _DIRECTORY_FLAGS, dir_fd=root_descriptor)
        return _directory_fingerprint(os.fstat(reopened)) == audit_fingerprint
    except OSError:
        return False
    finally:
        if reopened >= 0:
            os.close(reopened)


def _path_descriptor_is_pinned(path: Path, descriptor: int) -> bool:
    try:
        descriptor_metadata = os.fstat(descriptor)
        path_metadata = path.stat(follow_symlinks=False)
    except OSError:
        return False
    return (
        descriptor_metadata.st_nlink == 1
        and path_metadata.st_nlink == 1
        and _fingerprint(descriptor_metadata) == _fingerprint(path_metadata)
    )


def _entry_matches_snapshot(
    directory_descriptor: int,
    name: str,
    expected_fingerprint: tuple[int, int, int, int, int, int, int],
    expected_payload: bytes,
) -> bool:
    descriptor = -1
    try:
        descriptor = os.open(name, _FILE_FLAGS, dir_fd=directory_descriptor)
        before = os.fstat(descriptor)
        if (
            before.st_nlink != 1
            or _fingerprint(before) != expected_fingerprint
            or _read_descriptor(descriptor) != expected_payload
            or _fingerprint(os.fstat(descriptor)) != expected_fingerprint
        ):
            return False
        current = os.stat(
            name,
            dir_fd=directory_descriptor,
            follow_symlinks=False,
        )
        return (
            current.st_nlink == 1
            and _fingerprint(current) == expected_fingerprint
        )
    except OSError:
        return False
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _entry_has_payload(
    directory_descriptor: int,
    name: str,
    payload: bytes,
) -> bool:
    descriptor = -1
    try:
        descriptor = os.open(name, _FILE_FLAGS, dir_fd=directory_descriptor)
        before = os.fstat(descriptor)
        return (
            before.st_nlink == 1
            and stat.S_ISREG(before.st_mode)
            and _read_descriptor(descriptor) == payload
            and _fingerprint(os.fstat(descriptor)) == _fingerprint(before)
        )
    except OSError:
        return False
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _restore_bytes(
    audit_descriptor: int,
    manifest_name: str,
    payload: bytes,
) -> None:
    temporary_name = f".{manifest_name}.{secrets.token_hex(12)}.rollback"
    descriptor = os.open(
        temporary_name,
        _TEMP_FLAGS,
        0o600,
        dir_fd=audit_descriptor,
    )
    try:
        _write_all(descriptor, payload)
    finally:
        os.close(descriptor)
    try:
        os.replace(
            temporary_name,
            manifest_name,
            src_dir_fd=audit_descriptor,
            dst_dir_fd=audit_descriptor,
        )
        os.fsync(audit_descriptor)
    finally:
        try:
            os.unlink(temporary_name, dir_fd=audit_descriptor)
        except FileNotFoundError:
            pass


def record_successful_build(
    manifest_path: Path,
    build: Mapping[str, Any],
    *,
    envelope: Mapping[str, Any],
    compile_succeeded: bool,
    preflight_succeeded: bool,
    validator: Callable[[dict[str, Any]], None],
) -> None:
    """Merge one proved build under a Git-private lock and descriptor-pinned write."""

    if not compile_succeeded:
        raise BuildManifestError("compilation non réussie")
    if not preflight_succeeded:
        raise BuildManifestError("préflight non réussi")
    _validate_build_shape(build)
    root = _repository_root(manifest_path)
    initial_git_state = _git_state(root)
    initial_evidence_fingerprint = _git_evidence_fingerprint(root)
    current_head, current_branch, current_dirty = initial_git_state
    provenance = envelope.get("provenance")
    if (
        not isinstance(provenance, Mapping)
        or provenance.get("head_sha") != current_head
        or provenance.get("branch") != current_branch
        or provenance.get("dirty") is not current_dirty
    ):
        raise BuildManifestError("provenance de l'enveloppe périmée ou forgée")
    if build.get("git_sha") != current_head:
        raise BuildManifestError("git_sha du build périmé")
    lock_path = _git_lock_path(root)
    lock_descriptor = os.open(
        lock_path,
        os.O_RDWR | os.O_CREAT | os.O_CLOEXEC | os.O_NOFOLLOW,
        0o600,
    )
    lock_fingerprint = _fingerprint(os.fstat(lock_descriptor))
    if not _path_descriptor_is_pinned(lock_path, lock_descriptor):
        os.close(lock_descriptor)
        raise BuildManifestError("verrou Git non sûr ou substitué")
    root_descriptor = audit_descriptor = manifest_descriptor = -1
    temporary_name: str | None = None
    original = b""
    try:
        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
        if not _path_descriptor_is_pinned(lock_path, lock_descriptor):
            raise BuildManifestError("verrou Git substitué pendant l'attente")
        root_descriptor = os.open(root, _DIRECTORY_FLAGS)
        audit_descriptor = os.open(
            "audit",
            _DIRECTORY_FLAGS,
            dir_fd=root_descriptor,
        )
        audit_fingerprint = _directory_fingerprint(os.fstat(audit_descriptor))
        try:
            manifest_descriptor = os.open(
                "BUILD_MANIFEST.json",
                _FILE_FLAGS,
                dir_fd=audit_descriptor,
            )
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                raise BuildManifestError("manifeste symbolique interdit") from exc
            raise BuildManifestError(
                f"manifeste inaccessible: {type(exc).__name__}"
            ) from exc
        manifest_fingerprint = _fingerprint(os.fstat(manifest_descriptor))
        if (
            manifest_fingerprint[2] != stat.S_IFREG
            or manifest_fingerprint[6] != 1
        ):
            raise BuildManifestError(
                "manifeste non régulier ou lien dur interdit"
            )
        original = _read_descriptor(manifest_descriptor)
        current = _load_manifest_bytes(original)
        if not _same_envelope(current, envelope):
            raise BuildManifestError("enveloppe incompatible")
        builds = [dict(value) for value in current["builds"]]
        if current.get("build_state_digest") != build_state_digest(builds):
            raise BuildManifestError("build_state_digest courant incohérent")
        identity = (build.get("manual"), build.get("variant"))
        if any((value.get("manual"), value.get("variant")) == identity for value in builds):
            raise BuildManifestError(
                f"build observé en doublon: {identity[0]}:{identity[1]}"
            )
        if any(
            value.get("pdf_path") == build.get("pdf_path")
            or value.get("pdf_sha256") == build.get("pdf_sha256")
            for value in builds
        ):
            raise BuildManifestError("PDF ou digest déjà associé à un autre build")
        builds.append(dict(build))
        builds.sort(
            key=lambda value: (
                str(value.get("manual", "")),
                str(value.get("variant", "")),
                str(value.get("pdf_path", "")),
            )
        )
        updated = dict(envelope)
        updated["builds"] = builds
        updated["build_state_digest"] = build_state_digest(builds)
        try:
            validator(updated)
        except Exception as exc:
            raise BuildManifestError(
                f"validation du manifeste refusée: {type(exc).__name__}"
            ) from exc
        serialized = (
            json.dumps(updated, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        temporary_name = (
            f".BUILD_MANIFEST.json.{secrets.token_hex(12)}.tmp"
        )
        temporary_descriptor = os.open(
            temporary_name,
            _TEMP_FLAGS,
            0o600,
            dir_fd=audit_descriptor,
        )
        try:
            _write_all(temporary_descriptor, serialized)
        finally:
            os.close(temporary_descriptor)
        if (
            not _parent_is_pinned(root_descriptor, audit_fingerprint)
            or not _path_descriptor_is_pinned(lock_path, lock_descriptor)
            or _fingerprint(os.fstat(lock_descriptor)) != lock_fingerprint
            or _git_state(root)[:2] != initial_git_state[:2]
            or _git_evidence_fingerprint(root) != initial_evidence_fingerprint
            or not _entry_matches_snapshot(
                audit_descriptor,
                "BUILD_MANIFEST.json",
                manifest_fingerprint,
                original,
            )
        ):
            raise BuildManifestError("destination modifiée avant remplacement")
        replaced = False
        try:
            os.replace(
                temporary_name,
                "BUILD_MANIFEST.json",
                src_dir_fd=audit_descriptor,
                dst_dir_fd=audit_descriptor,
            )
            temporary_name = None
            replaced = True
            os.fsync(audit_descriptor)
            if (
                not _parent_is_pinned(root_descriptor, audit_fingerprint)
                or not _path_descriptor_is_pinned(lock_path, lock_descriptor)
                or _git_state(root)[:2] != initial_git_state[:2]
                or _git_evidence_fingerprint(root)
                != initial_evidence_fingerprint
                or not _entry_has_payload(
                    audit_descriptor,
                    "BUILD_MANIFEST.json",
                    serialized,
                )
                ):
                    raise BuildManifestError(
                        "parent modifié, verrou ou destination substitué "
                        "pendant remplacement"
                    )
        except BaseException as exc:
            if (
                replaced
                and _entry_has_payload(
                    audit_descriptor,
                    "BUILD_MANIFEST.json",
                    serialized,
                )
            ):
                try:
                    _restore_bytes(
                        audit_descriptor,
                        "BUILD_MANIFEST.json",
                        original,
                    )
                except BaseException as rollback_exc:
                    raise BuildManifestError(
                        "publication transactionnelle échouée; rollback impossible"
                    ) from rollback_exc
            if isinstance(exc, BuildManifestError):
                raise
            raise BuildManifestError(
                "publication transactionnelle échouée; état antérieur restauré"
            ) from exc
    finally:
        if temporary_name is not None and audit_descriptor >= 0:
            try:
                os.unlink(temporary_name, dir_fd=audit_descriptor)
            except FileNotFoundError:
                pass
        for descriptor in (manifest_descriptor, audit_descriptor, root_descriptor):
            if descriptor >= 0:
                os.close(descriptor)
        try:
            fcntl.flock(lock_descriptor, fcntl.LOCK_UN)
        finally:
            os.close(lock_descriptor)


def _git_root_from_path(path: Path) -> Path:
    try:
        completed = subprocess.run(
            ["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BuildManifestError("receipt hors dépôt Git") from exc
    return Path(completed.stdout.strip()).resolve(strict=True)


def _read_receipt(path: Path, root: Path) -> dict[str, Any]:
    absolute = Path(os.path.abspath(path))
    try:
        relative = absolute.relative_to(root)
    except ValueError as exc:
        raise BuildManifestError("receipt hors dépôt") from exc
    payload_bytes = _read_proof_file(
        root,
        relative.as_posix(),
        role="receipt",
    )
    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise BuildManifestError("receipt JSON invalide") from exc
    if not isinstance(payload, dict) or set(payload) != _RECEIPT_FIELDS:
        raise BuildManifestError("receipt incomplet ou champs inattendus")
    return payload


def _load_inventory_module() -> Any:
    try:
        from scripts import inventory_collection
    except ModuleNotFoundError:
        import inventory_collection

    return inventory_collection


def _receipt_string_list(
    receipt: Mapping[str, Any],
    field: str,
    *,
    nonempty: bool,
) -> list[str]:
    value = receipt.get(field)
    if (
        not isinstance(value, list)
        or (nonempty and not value)
        or any(not isinstance(item, str) or not item for item in value)
        or len(value) != len(set(value))
    ):
        raise BuildManifestError(f"{field} invalide dans le receipt")
    return list(value)


def _read_proof_file(root: Path, raw_path: object, *, role: str) -> bytes:
    if not isinstance(raw_path, str) or not raw_path:
        raise BuildManifestError(f"{role} absent")
    if (
        "\\" in raw_path
        or raw_path.startswith("/")
        or any(part in {"", ".", ".."} for part in raw_path.split("/"))
    ):
        raise BuildManifestError(f"{role} non canonique")
    components = tuple(raw_path.split("/"))
    descriptors: list[int] = []
    directory_fingerprints: list[tuple[int, int, int]] = []
    leaf_descriptor = -1
    try:
        current = os.open(root, _DIRECTORY_FLAGS)
        descriptors.append(current)
        directory_fingerprints.append(
            _directory_fingerprint(os.fstat(current))
        )
        for component in components[:-1]:
            current = os.open(component, _DIRECTORY_FLAGS, dir_fd=current)
            descriptors.append(current)
            directory_fingerprints.append(
                _directory_fingerprint(os.fstat(current))
            )
        leaf_descriptor = os.open(
            components[-1],
            _FILE_FLAGS,
            dir_fd=current,
        )
    except OSError as exc:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
        raise BuildManifestError(f"{role} inaccessible ou symbolique") from exc
    try:
        before = os.fstat(leaf_descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise BuildManifestError(
                f"{role} non régulier ou hardlink interdit"
            )
        leaf_fingerprint = _fingerprint(before)
        payload = _read_descriptor(leaf_descriptor)
        if _fingerprint(os.fstat(leaf_descriptor)) != leaf_fingerprint:
            raise BuildManifestError(f"{role} modifié pendant la lecture")

        reopened: list[int] = []
        try:
            current = os.open(root, _DIRECTORY_FLAGS)
            reopened.append(current)
            if (
                _directory_fingerprint(os.fstat(current))
                != directory_fingerprints[0]
            ):
                raise BuildManifestError(f"parent de {role} substitué")
            for index, component in enumerate(components[:-1], start=1):
                current = os.open(
                    component,
                    _DIRECTORY_FLAGS,
                    dir_fd=current,
                )
                reopened.append(current)
                if (
                    _directory_fingerprint(os.fstat(current))
                    != directory_fingerprints[index]
                ):
                    raise BuildManifestError(f"parent de {role} substitué")
            reopened_leaf = os.open(
                components[-1],
                _FILE_FLAGS,
                dir_fd=current,
            )
            reopened.append(reopened_leaf)
            if _fingerprint(os.fstat(reopened_leaf)) != leaf_fingerprint:
                raise BuildManifestError(f"{role} remplacé pendant la lecture")
        except OSError as exc:
            raise BuildManifestError(
                f"parent de {role} substitué ou inaccessible"
            ) from exc
        finally:
            for descriptor in reversed(reopened):
                os.close(descriptor)
        return payload
    finally:
        if leaf_descriptor >= 0:
            os.close(leaf_descriptor)
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _canonical_fls_path(root: Path, raw: str) -> str | None:
    candidate = Path(raw)
    if candidate.is_absolute():
        try:
            candidate = candidate.resolve(strict=False).relative_to(root)
        except ValueError:
            return None
    normalized = candidate.as_posix()
    if (
        normalized.startswith("/")
        or "\\" in normalized
        or any(part in {"", ".", ".."} for part in normalized.split("/"))
    ):
        return None
    return normalized


def _run_local_pdf_preflight(
    pdf_path: Path,
    *,
    expected_pages: int,
) -> dict[str, str]:
    try:
        pdfinfo = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            timeout=20,
        )
        pdffonts = subprocess.run(
            ["pdffonts", str(pdf_path)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BuildManifestError(
            f"préflight local indisponible: {type(exc).__name__}"
        ) from exc
    if pdfinfo.returncode != 0:
        raise BuildManifestError("préflight local pdfinfo rouge")
    pages_match = None
    for line in pdfinfo.stdout.splitlines():
        if line.startswith("Pages:"):
            pages_match = line.partition(":")[2].strip()
            break
    if pages_match != str(expected_pages):
        raise BuildManifestError("préflight local pages incohérent")
    if pdffonts.returncode != 0:
        raise BuildManifestError("préflight local pdffonts rouge")
    font_rows = [
        line.split()
        for line in pdffonts.stdout.splitlines()
        if line.strip()
        and not line.startswith("name")
        and not set(line.replace(" ", "").strip()) <= {"-"}
    ]
    if not font_rows:
        raise BuildManifestError("préflight local sans inventaire de polices")
    if any(len(row) < 7 or row[-5].lower() != "yes" for row in font_rows):
        raise BuildManifestError("préflight local: police non incorporée")
    return {
        "pdffonts": "passed",
        "pdfinfo": "passed",
    }


def _derive_receipt_evidence(
    root: Path,
    receipt: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], Callable[[dict[str, Any]], None]]:
    inventory_module = _load_inventory_module()
    inventory = inventory_module.build_inventory(root)
    source_digest = str(inventory["source_digest"])
    model_digest = str(inventory_module._model_digest(inventory))
    head, branch, dirty = _git_state(root)
    manual = receipt.get("manual")
    variant = receipt.get("variant")
    pdf_path = receipt.get("pdf_path")
    if not all(isinstance(value, str) and value for value in (manual, variant, pdf_path)):
        raise BuildManifestError("manual, variant ou pdf_path invalide")
    identity = (manual, variant)
    declared = {
        (str(value.get("manual")), str(value.get("variant"))): value
        for value in inventory["declared_assemblies"]
        if value.get("scope") == "manual"
    }
    if identity not in declared:
        raise BuildManifestError(
            f"assemblage manuel non déclaré: {manual}:{variant}"
        )
    inventory_module._observed_deliverable_variant(manual, variant)
    if not inventory_module._pdf_matches_observed_identity(
        pdf_path,
        manual,
        variant,
    ):
        raise BuildManifestError("nom PDF sans preuve de manual/variante")
    if not inventory_module._pdf_core._is_canonical_manual_pdf_path(
        {"manual": manual, "path": pdf_path},
        manual_build_roots=inventory_module.COMPILED_PDF_BUILD_ROOTS,
    ):
        raise BuildManifestError("chemin PDF non canonique")

    dependencies = _receipt_string_list(
        receipt,
        "generated_dependencies",
        nonempty=False,
    )
    declared_objects = declared[identity].get("included_objects")
    if not isinstance(declared_objects, list) or not declared_objects:
        raise BuildManifestError("assemblage déclaré sans objets traçables")

    log_payload = _read_proof_file(
        root,
        receipt.get("log_path"),
        role="journal LaTeX",
    )
    log_text = log_payload.decode("utf-8", errors="replace")
    if (
        "Output written on " not in log_text
        or "Fatal error" in log_text
        or "! Emergency stop" in log_text
    ):
        raise BuildManifestError("journal LaTeX sans compilation prouvée")
    fls_payload = _read_proof_file(
        root,
        receipt.get("fls_path"),
        role="traceur FLS",
    )
    fls_text = fls_payload.decode("utf-8", errors="replace")
    traced_inputs: list[str] = []
    traced_outputs: set[str] = set()
    for line in fls_text.splitlines():
        kind, separator, raw = line.partition(" ")
        if not separator or kind not in {"INPUT", "OUTPUT"}:
            continue
        normalized = _canonical_fls_path(root, raw.strip())
        if normalized is None:
            continue
        if kind == "INPUT":
            traced_inputs.append(normalized)
        else:
            traced_outputs.add(normalized)
    declared_set = set(declared_objects)
    included = []
    seen: set[str] = set()
    for path in traced_inputs:
        if path in declared_set and path not in seen:
            included.append(path)
            seen.add(path)
    if not included:
        raise BuildManifestError("traceur FLS sans objet déclaré inclus")
    excluded = sorted(declared_set - seen)
    ordered_trace = list(included)
    dependency_digests: dict[str, str] = {}
    for dependency in dependencies:
        if (
            "\\" in dependency
            or dependency.startswith("/")
            or any(part in {"", ".", ".."} for part in dependency.split("/"))
            or dependency not in traced_outputs
        ):
            raise BuildManifestError(
                f"dépendance générée non prouvée: {dependency}"
            )
        dependency_payload = _read_proof_file(
            root,
            dependency,
            role=f"dépendance générée {dependency}",
        )
        dependency_digests[dependency] = (
            "sha256:" + hashlib.sha256(dependency_payload).hexdigest()
        )

    digest, pages, _method, reason = inventory_module._pdf_core.inspect_stable_pdf(
        root,
        pdf_path,
        pdfinfo_counter=inventory_module._page_count_with_pdfinfo,
        python_counter=inventory_module._page_count_with_python,
    )
    if reason or digest is None or pages is None:
        raise BuildManifestError(f"PDF non prouvé: {reason or 'preuve absente'}")
    local_preflight = _run_local_pdf_preflight(
        root / pdf_path,
        expected_pages=pages,
    )
    preflight_payload = _read_proof_file(
        root,
        receipt.get("preflight_report"),
        role="rapport de préflight",
    )
    try:
        preflight = json.loads(preflight_payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise BuildManifestError("rapport de préflight JSON invalide") from exc
    if (
        not isinstance(preflight, Mapping)
        or preflight.get("passed") is not True
        or preflight.get("pdf_sha256") != digest
    ):
        raise BuildManifestError(
            "rapport de préflight sans réussite liée au PDF observé"
        )
    gates = receipt.get("gates")
    if not isinstance(gates, Mapping):
        raise BuildManifestError("gates invalides dans le receipt")
    normalized_gates = {
        str(name): dict(value)
        for name, value in gates.items()
        if isinstance(name, str) and isinstance(value, Mapping)
    }
    if len(normalized_gates) != len(gates):
        raise BuildManifestError("gates invalides dans le receipt")
    normalized_gates["compile"] = {"passed": True}
    normalized_gates["preflight"] = {
        "passed": True,
        "checks": local_preflight,
    }
    tool_versions = receipt.get("tool_versions")
    if (
        not isinstance(tool_versions, Mapping)
        or not tool_versions
        or any(
            not isinstance(name, str)
            or not name
            or not isinstance(value, str)
            or not value
            for name, value in tool_versions.items()
        )
    ):
        raise BuildManifestError("tool_versions invalides")
    build = {
        "excluded_objects": excluded,
        "gates": normalized_gates,
        "generated_dependencies": dependencies,
        "generated_dependency_digests": dependency_digests,
        "git_sha": head,
        "included_objects": included,
        "manual": manual,
        "model_digest": model_digest,
        "ordered_trace": ordered_trace,
        "page_count": pages,
        "pdf_path": pdf_path,
        "pdf_sha256": digest,
        "source_digest": source_digest,
        "tool_versions": dict(tool_versions),
        "variant": variant,
    }
    envelope = {
        "artifact_type": "build_manifest",
        "generated_by": "build_manifest.py",
        "model_digest": model_digest,
        "provenance": {
            "branch": branch,
            "dirty": dirty,
            "head_sha": head,
        },
        "schema_ref": "audit/schemas/v1/build-manifest.schema.json",
        "schema_version": 1,
        "source_digest": source_digest,
    }

    def validate(proposed: dict[str, Any]) -> None:
        inventory_module._validate_artifact_schema(
            proposed,
            root=root,
            path=Path("audit/BUILD_MANIFEST.json"),
        )
        if proposed.get("source_digest") != source_digest:
            raise BuildManifestError("source_digest proposé incohérent")
        if proposed.get("model_digest") != model_digest:
            raise BuildManifestError("model_digest proposé incohérent")
        builds = proposed.get("builds")
        if (
            not isinstance(builds, list)
            or proposed.get("build_state_digest") != build_state_digest(builds)
        ):
            raise BuildManifestError("état des builds proposé incohérent")
        current_digest, current_pages, _method, current_reason = (
            inventory_module._pdf_core.inspect_stable_pdf(
                root,
                pdf_path,
                pdfinfo_counter=inventory_module._page_count_with_pdfinfo,
                python_counter=inventory_module._page_count_with_python,
            )
        )
        if (
            current_reason
            or current_digest != digest
            or current_pages != pages
        ):
            raise BuildManifestError(
                "PDF modifié avant publication du manifeste"
            )
        _run_local_pdf_preflight(
            root / pdf_path,
            expected_pages=pages,
        )

    return envelope, build, validate


def record_from_receipt(receipt_path: Path) -> None:
    """Validate a receipt but refuse publication until build wrapping exists."""

    root = _git_root_from_path(receipt_path)
    receipt = _read_receipt(receipt_path, root)
    compile_succeeded = receipt.get("compile_succeeded") is True
    preflight_succeeded = receipt.get("preflight_succeeded") is True
    if not compile_succeeded:
        raise BuildManifestError("receipt sans compilation réussie")
    if not preflight_succeeded:
        raise BuildManifestError("receipt sans préflight réussi")
    _derive_receipt_evidence(root, receipt)
    raise BuildManifestError(
        "intégration assembleur non activée: la commande de compilation "
        "n'est pas observée par cet entrypoint"
    )


def _run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Enregistre une preuve de build Nexus validée localement."
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        required=True,
        help="receipt JSON post-compilation et post-préflight",
    )
    arguments = parser.parse_args(argv)
    try:
        record_from_receipt(arguments.receipt)
    except BuildManifestError as exc:
        print(f"build manifest refusé: {exc}", file=sys.stderr)
        return 2
    print("build manifest enregistré")
    return 0


if __name__ == "__main__":
    raise SystemExit(_run(sys.argv[1:]))
