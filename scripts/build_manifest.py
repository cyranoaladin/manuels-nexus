"""Secure transactional writer for already-proved observed build evidence.

Assembler integration contract::

    python scripts/build_manifest.py --receipt path/to/build-receipt.json

The receipt must be emitted only after the assembler has completed compilation
and preflight.  This entrypoint distrusts all derived assertions: it recomputes
Git provenance, source/model digests, PDF digest and page count before recording
the observed build transactionally.
"""

from __future__ import annotations

import argparse
import errno
import fcntl
import hashlib
import json
import os
import re
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
_REPRODUCIBILITY_CONFIG = (
    "Mathematiques/manuel-maths/config/reproducible-build.json"
)
_REPRODUCIBILITY_CONFIG_FIELDS = {
    "schema_version",
    "source_commit",
    "source_date_epoch",
}
_REPRODUCIBILITY_FIELDS = {
    "config_path",
    "force_source_date",
    "locale",
    "pythonhashseed",
    "source_commit",
    "source_date_epoch",
    "timezone",
}
_REPRODUCIBILITY_CONSTANTS = {
    "force_source_date": "1",
    "timezone": "UTC",
    "locale": "C.UTF-8",
    "pythonhashseed": "0",
}
_CONTROLLED_ENVIRONMENT = {
    "FORCE_SOURCE_DATE": "1",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "PYTHONHASHSEED": "0",
}
_EVIDENCE_FIELDS = {"master", "log", "fls", "pdf", "preflight"}
_TOOL_VERSION_COMMANDS = {
    "lualatex": ["lualatex", "--version"],
    "pdfinfo": ["pdfinfo", "-v"],
    "pdffonts": ["pdffonts", "-v"],
    "python": [sys.executable, "--version"],
}
_PREFLIGHT_FIELDS = {
    "run_id",
    "pdf_path",
    "pdf_sha256",
    "page_count",
    "passed",
    "checks",
    "tool_versions",
    "reproducibility",
}
_PREFLIGHT_CHECKS = {"verify_pdf", "pdfinfo", "pdffonts"}
_RECEIPT_FIELDS = {
    "compile_succeeded",
    "evidence_sha256",
    "fls_path",
    "gates",
    "generated_dependencies",
    "log_path",
    "manual",
    "master_path",
    "pdf_path",
    "preflight_report",
    "preflight_succeeded",
    "reproducibility",
    "run_id",
    "tool_versions",
    "variant",
}
_1NSI_STUDENT_VARIANTS = frozenset(
    {"eleve", "methodes", "remediation", "amenagee", "projets"}
)


class BuildManifestError(RuntimeError):
    """Refusal to record unproved or inconsistent build evidence."""


def _requires_student_separation(manual: object, variant: object) -> bool:
    """Return whether this observed manual variant must pass student gates."""

    return variant == "eleve" or (
        manual == "1NSI" and variant in _1NSI_STUDENT_VARIANTS
    )


def build_state_digest(builds: list[Mapping[str, Any]]) -> str:
    canonical = json.dumps(
        builds,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def _sanitized_git_environment() -> dict[str, str]:
    return {
        name: os.environ[name]
        for name in ("PATH", "HOME")
        if name in os.environ
    }


def _run_git(
    root: Path,
    command: list[str],
    *,
    role: str,
    check: bool = True,
    text: bool = True,
) -> subprocess.CompletedProcess[Any]:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *command],
            env=_sanitized_git_environment(),
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=text,
            errors="replace" if text else None,
            timeout=20,
        )
    except (
        OSError,
        subprocess.TimeoutExpired,
        subprocess.CalledProcessError,
    ) as exc:
        raise BuildManifestError(role) from exc


def _repository_root(manifest_path: Path) -> Path:
    completed = _run_git(
        manifest_path.parent,
        ["rev-parse", "--show-toplevel"],
        role="dépôt Git indisponible",
    )
    root = Path(completed.stdout.strip()).resolve(strict=True)
    requested = Path(os.path.abspath(manifest_path))
    expected = root / _MANIFEST_RELATIVE
    if requested != expected:
        raise BuildManifestError(
            f"chemin manifeste hors destination canonique: {requested}"
        )
    return root


def _git_lock_path(root: Path) -> Path:
    completed = _run_git(
        root,
        ["rev-parse", "--git-path", "nexus-build.lock"],
        role="chemin de verrou Git indisponible",
    )
    path = Path(completed.stdout.strip())
    return path if path.is_absolute() else root / path


def _git_head(root: Path) -> str:
    completed = _run_git(
        root,
        ["rev-parse", "HEAD"],
        role="HEAD Git indisponible",
    )
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
    head = _git_head(root)
    branch = _run_git(
        root,
        ["branch", "--show-current"],
        role="état Git indisponible",
    ).stdout.strip()
    status_payload = _run_git(
        root,
        ["status", "--porcelain=v1", "--untracked-files=all", "-z"],
        role="état Git indisponible",
        text=False,
    ).stdout
    if not branch:
        raise BuildManifestError("branche Git détachée ou indisponible")
    return head, branch, _status_is_dirty_outside_manifest(status_payload)


def _git_evidence_fingerprint(root: Path) -> str:
    payload = _run_git(
        root,
        ["status", "--porcelain=v1", "--untracked-files=all", "-z"],
        role="état détaillé Git indisponible",
        text=False,
    ).stdout
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


def _capture_git_snapshot(
    root: Path,
) -> tuple[tuple[str, str, bool], str]:
    return _git_state(root), _git_evidence_fingerprint(root)


def _require_git_snapshot(
    root: Path,
    expected: tuple[tuple[str, str, bool], str],
    *,
    phase: str,
) -> None:
    if _capture_git_snapshot(root) != expected:
        raise BuildManifestError(f"état Git ou sources modifiés {phase}")


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


def _same_envelope(
    current: Mapping[str, Any],
    expected: Mapping[str, Any],
    *,
    root: Path | None = None,
) -> bool:
    fields = (
        "artifact_type",
        "generated_by",
        "model_digest",
        "schema_ref",
        "schema_version",
        "source_digest",
    )
    if not all(current.get(field) == expected.get(field) for field in fields):
        return False
    current_provenance = current.get("provenance")
    expected_provenance = expected.get("provenance")
    if current_provenance == expected_provenance:
        return True
    if root is None or not current.get("builds"):
        return False
    if not isinstance(current_provenance, Mapping) or not isinstance(
        expected_provenance, Mapping
    ):
        return False
    if (
        current_provenance.get("branch") != expected_provenance.get("branch")
        or current_provenance.get("dirty") is not False
        or expected_provenance.get("dirty") is not False
    ):
        return False
    old_head = current_provenance.get("head_sha")
    new_head = expected_provenance.get("head_sha")
    if not isinstance(old_head, str) or not isinstance(new_head, str):
        return False
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", old_head, new_head],
        cwd=root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return ancestor.returncode == 0


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
        "reproducibility",
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
    _validate_reproducibility(
        build.get("reproducibility"),
        role="du build",
    )
    gates = build.get("gates")
    if not isinstance(gates, Mapping):
        raise BuildManifestError("gates invalides")
    for gate in ("compile", "preflight"):
        value = gates.get(gate)
        if not isinstance(value, Mapping) or value.get("passed") is not True:
            raise BuildManifestError(f"preuve {gate} absente ou rouge")
    if _requires_student_separation(
        build.get("manual"),
        build.get("variant"),
    ):
        student_gate = gates.get("student_separation")
        if (
            not isinstance(student_gate, Mapping)
            or student_gate.get("passed") is not True
        ):
            raise BuildManifestError("preuve de séparation élève absente ou rouge")


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


def _replace_manifest_transactionally(
    manifest_path: Path,
    *,
    transform: Callable[
        [dict[str, Any], tuple[str, str, bool]],
        dict[str, Any],
    ],
    expected_git_state: tuple[str, str, bool] | None = None,
    expected_evidence_fingerprint: str | None = None,
    expected_manifest_digest: str | None = None,
) -> None:
    """Replace the canonical manifest under a pinned, recoverable transaction."""

    root = _repository_root(manifest_path)
    initial_git_state = _git_state(root)
    initial_evidence_fingerprint = _git_evidence_fingerprint(root)
    if (
        expected_git_state is not None
        and initial_git_state != expected_git_state
    ):
        raise BuildManifestError("état Git modifié avant la transaction")
    if (
        expected_evidence_fingerprint is not None
        and initial_evidence_fingerprint != expected_evidence_fingerprint
    ):
        raise BuildManifestError("sources modifiées avant la transaction")
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
        if (
            expected_manifest_digest is not None
            and _sha256_payload(original) != expected_manifest_digest
        ):
            raise BuildManifestError(
                "manifeste vide modifié depuis sa validation"
            )
        current = _load_manifest_bytes(original)
        try:
            updated = transform(current, initial_git_state)
        except BuildManifestError:
            raise
        except Exception as exc:
            raise BuildManifestError(
                f"préparation du manifeste refusée: {type(exc).__name__}"
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

    def merge_build(
        current: dict[str, Any],
        _git_state_snapshot: tuple[str, str, bool],
    ) -> dict[str, Any]:
        if not _same_envelope(current, envelope, root=root):
            raise BuildManifestError("enveloppe incompatible")
        builds = [dict(value) for value in current["builds"]]
        if current.get("build_state_digest") != build_state_digest(builds):
            raise BuildManifestError("build_state_digest courant incohérent")
        identity = (build.get("manual"), build.get("variant"))
        if any(
            (value.get("manual"), value.get("variant")) == identity
            for value in builds
        ):
            raise BuildManifestError(
                f"build observé en doublon: {identity[0]}:{identity[1]}"
            )
        if any(
            value.get("pdf_path") == build.get("pdf_path")
            or value.get("pdf_sha256") == build.get("pdf_sha256")
            for value in builds
        ):
            raise BuildManifestError(
                "PDF ou digest déjà associé à un autre build"
            )
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
        return updated

    _replace_manifest_transactionally(
        manifest_path,
        transform=merge_build,
        expected_git_state=initial_git_state,
        expected_evidence_fingerprint=initial_evidence_fingerprint,
    )


def _git_root_from_path(path: Path) -> Path:
    completed = _run_git(
        path.parent,
        ["rev-parse", "--show-toplevel"],
        role="receipt hors dépôt Git",
    )
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


def _sha256_payload(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _validate_sha256(value: object, *, role: str) -> str:
    if not isinstance(value, str) or re.fullmatch(
        r"sha256:[0-9a-f]{64}",
        value,
    ) is None:
        raise BuildManifestError(f"empreinte {role} invalide")
    return value


def _validate_run_id(value: object) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{32}", value) is None:
        raise BuildManifestError("run_id invalide")
    return value


def _validate_tool_versions(value: object, *, role: str) -> dict[str, str]:
    if (
        not isinstance(value, Mapping)
        or set(value) != set(_TOOL_VERSION_COMMANDS)
        or any(
            not isinstance(version, str) or not version
            for version in value.values()
        )
    ):
        raise BuildManifestError(f"versions d'outils {role} invalides")
    return {name: str(value[name]) for name in _TOOL_VERSION_COMMANDS}


def _validate_reproducibility(
    value: object,
    *,
    role: str,
) -> dict[str, object]:
    if not isinstance(value, Mapping) or set(value) != _REPRODUCIBILITY_FIELDS:
        raise BuildManifestError(f"reproductibilité {role} non fermée")
    config_path = value.get("config_path")
    source_commit = value.get("source_commit")
    source_date_epoch = value.get("source_date_epoch")
    if config_path != _REPRODUCIBILITY_CONFIG:
        raise BuildManifestError(f"config de reproductibilité {role} invalide")
    if not isinstance(source_commit, str) or re.fullmatch(
        r"[0-9a-f]{40}",
        source_commit,
    ) is None:
        raise BuildManifestError(f"source_commit de reproductibilité {role} invalide")
    if type(source_date_epoch) is not int or source_date_epoch <= 0:
        raise BuildManifestError(
            f"source_date_epoch de reproductibilité {role} invalide"
        )
    for name, expected in _REPRODUCIBILITY_CONSTANTS.items():
        if value.get(name) != expected:
            raise BuildManifestError(
                f"constante {name} de reproductibilité {role} invalide"
            )
    return {
        "config_path": _REPRODUCIBILITY_CONFIG,
        "source_commit": source_commit,
        "source_date_epoch": source_date_epoch,
        **_REPRODUCIBILITY_CONSTANTS,
    }


def _sanitized_build_environment(
    reproducibility: Mapping[str, object],
) -> dict[str, str]:
    environment = {
        name: os.environ[name]
        for name in ("PATH", "HOME")
        if name in os.environ
    }
    environment.update(_CONTROLLED_ENVIRONMENT)
    environment["SOURCE_DATE_EPOCH"] = str(
        reproducibility["source_date_epoch"]
    )
    return environment


def _first_version_line(completed: Any, *, tool: str) -> str:
    if completed.returncode != 0:
        raise BuildManifestError(f"collecte de version {tool} en échec")
    output = "\n".join(
        value
        for value in (
            getattr(completed, "stdout", ""),
            getattr(completed, "stderr", ""),
        )
        if isinstance(value, str) and value
    )
    for line in output.splitlines():
        normalized = " ".join(line.split())
        if normalized:
            return normalized
    raise BuildManifestError(f"version {tool} absente")


def _collect_local_tool_versions(
    reproducibility: Mapping[str, object],
) -> dict[str, str]:
    environment = _sanitized_build_environment(reproducibility)
    versions: dict[str, str] = {}
    for tool, command in _TOOL_VERSION_COMMANDS.items():
        try:
            completed = subprocess.run(
                command,
                env=environment,
                capture_output=True,
                text=True,
                errors="replace",
                check=False,
                timeout=20,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise BuildManifestError(
                f"collecte de version {tool} indisponible"
            ) from exc
        versions[tool] = _first_version_line(completed, tool=tool)
    return versions


def _run_reproducibility_git(
    root: Path,
    command: list[str],
    *,
    text: bool,
) -> subprocess.CompletedProcess[Any]:
    return _run_git(
        root,
        command,
        role="validation Git de reproductibilité indisponible",
        check=False,
        text=text,
    )


def _load_reproducibility_control(
    root: Path,
) -> tuple[dict[str, object], bytes]:
    payload_bytes = _read_proof_file(
        root,
        _REPRODUCIBILITY_CONFIG,
        role="config de reproductibilité",
    )
    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise BuildManifestError("config de reproductibilité JSON invalide") from exc
    if (
        not isinstance(payload, Mapping)
        or set(payload) != _REPRODUCIBILITY_CONFIG_FIELDS
    ):
        raise BuildManifestError("config de reproductibilité non fermée")
    schema_version = payload.get("schema_version")
    source_commit = payload.get("source_commit")
    source_date_epoch = payload.get("source_date_epoch")
    if type(schema_version) is not int or schema_version != 1:
        raise BuildManifestError("schema_version de reproductibilité invalide")
    if not isinstance(source_commit, str) or re.fullmatch(
        r"[0-9a-f]{40}",
        source_commit,
    ) is None:
        raise BuildManifestError("source_commit de reproductibilité invalide")
    if type(source_date_epoch) is not int or source_date_epoch <= 0:
        raise BuildManifestError("source_date_epoch de reproductibilité invalide")

    tracked = _run_reproducibility_git(root, ["ls-files", "-z"], text=False)
    if tracked.returncode != 0:
        raise BuildManifestError("inventaire Git de reproductibilité indisponible")
    tracked_paths = {
        path.decode("utf-8", errors="surrogateescape")
        for path in tracked.stdout.split(b"\0")
        if path
    }
    if _REPRODUCIBILITY_CONFIG not in tracked_paths:
        raise BuildManifestError("config de reproductibilité non suivie par Git")

    commit = _run_reproducibility_git(
        root,
        ["cat-file", "-e", f"{source_commit}^{{commit}}"],
        text=True,
    )
    if commit.returncode != 0:
        raise BuildManifestError("source_commit absent du dépôt")
    ancestor = _run_reproducibility_git(
        root,
        ["merge-base", "--is-ancestor", source_commit, "HEAD"],
        text=True,
    )
    if ancestor.returncode != 0:
        raise BuildManifestError("source_commit non ancêtre de HEAD")
    timestamp = _run_reproducibility_git(
        root,
        ["show", "-s", "--format=%ct", source_commit],
        text=True,
    )
    if timestamp.returncode != 0:
        raise BuildManifestError("timestamp Git du source_commit indisponible")
    try:
        git_timestamp = int(timestamp.stdout.strip())
    except (AttributeError, ValueError) as exc:
        raise BuildManifestError("timestamp Git du source_commit invalide") from exc
    if git_timestamp != source_date_epoch:
        raise BuildManifestError("source_date_epoch différent du timestamp Git")
    reproducibility = _validate_reproducibility(
        {
            "config_path": _REPRODUCIBILITY_CONFIG,
            "source_commit": source_commit,
            "source_date_epoch": source_date_epoch,
            **_REPRODUCIBILITY_CONSTANTS,
        },
        role="locale",
    )
    return reproducibility, payload_bytes


def _validate_preflight_report(
    value: object,
    *,
    run_id: str,
    pdf_path: str,
    pdf_sha256: str,
    page_count: int,
    tool_versions: Mapping[str, str],
    reproducibility: Mapping[str, object],
) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != _PREFLIGHT_FIELDS:
        raise BuildManifestError("rapport de préflight incomplet ou champs inattendus")
    if value.get("run_id") != run_id:
        raise BuildManifestError("run_id du rapport de préflight incohérent")
    if value.get("pdf_path") != pdf_path:
        raise BuildManifestError("pdf_path du rapport de préflight incohérent")
    if value.get("pdf_sha256") != pdf_sha256:
        raise BuildManifestError("digest PDF du rapport de préflight incohérent")
    if type(value.get("page_count")) is not int or value.get("page_count") != page_count:
        raise BuildManifestError("pagination du rapport de préflight incohérente")
    if value.get("passed") is not True:
        raise BuildManifestError("rapport de préflight sans réussite")
    checks = value.get("checks")
    if (
        not isinstance(checks, Mapping)
        or set(checks) != _PREFLIGHT_CHECKS
        or any(
            not isinstance(check, Mapping)
            or set(check) != {"passed"}
            or check.get("passed") is not True
            for check in checks.values()
        )
    ):
        raise BuildManifestError("checks du rapport de préflight invalides")
    report_tools = _validate_tool_versions(
        value.get("tool_versions"),
        role="du rapport de préflight",
    )
    if report_tools != dict(tool_versions):
        raise BuildManifestError("versions d'outils du préflight incohérentes")
    report_reproducibility = _validate_reproducibility(
        value.get("reproducibility"),
        role="du rapport de préflight",
    )
    if report_reproducibility != dict(reproducibility):
        raise BuildManifestError("reproductibilité du préflight incohérente")
    return dict(value)


def _validate_run_marker(
    payload: bytes,
    *,
    run_id: str,
    role: str,
    tex_line: bool,
) -> None:
    text = payload.decode("utf-8", errors="replace")
    expected = (
        f"\\typeout{{NEXUS_BUILD_RUN:{run_id}}}"
        if tex_line
        else f"NEXUS_BUILD_RUN:{run_id}"
    )
    marker_lines = [
        line if tex_line else line.strip()
        for line in text.splitlines()
        if "NEXUS_BUILD_RUN:" in line
    ]
    if marker_lines != [expected]:
        raise BuildManifestError(f"marqueur run_id {role} invalide")


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


def _fls_working_directory(root: Path, fls_text: str) -> Path:
    pwd_records: list[str] = []
    for line in fls_text.splitlines():
        if line == "PWD" or line.startswith("PWD "):
            kind, separator, raw = line.partition(" ")
            if kind != "PWD" or not separator:
                raise BuildManifestError("PWD du traceur FLS invalide")
            pwd_records.append(raw)
        elif line.startswith("PWD"):
            raise BuildManifestError("PWD du traceur FLS invalide")
    if not pwd_records:
        return root.resolve(strict=True)
    if len(pwd_records) != 1:
        raise BuildManifestError("PWD du traceur FLS ambigu")

    raw = pwd_records[0]
    candidate = Path(raw)
    if (
        not raw
        or raw != raw.strip()
        or "\\" in raw
        or not candidate.is_absolute()
        or candidate.as_posix() != raw
    ):
        raise BuildManifestError("PWD du traceur FLS non canonique")
    try:
        canonical_root = root.resolve(strict=True)
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(canonical_root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise BuildManifestError(
            "PWD du traceur FLS hors dépôt ou inaccessible"
        ) from exc
    if resolved != candidate or not resolved.is_dir():
        raise BuildManifestError("PWD du traceur FLS symbolique ou non canonique")
    return resolved


def _canonical_fls_path(
    root: Path,
    raw: str,
    *,
    working_directory: Path | None = None,
) -> str | None:
    candidate = Path(raw)
    base = root if working_directory is None else working_directory
    if not candidate.is_absolute():
        candidate = base / candidate
    try:
        candidate = candidate.resolve(strict=False).relative_to(
            root.resolve(strict=True)
        )
    except (OSError, RuntimeError, ValueError):
        return None
    normalized = candidate.as_posix()
    if (
        normalized.startswith("/")
        or "\\" in normalized
        or any(part in {"", ".", ".."} for part in normalized.split("/"))
    ):
        return None
    return normalized


def _canonical_object_path(raw: object) -> str:
    if (
        not isinstance(raw, str)
        or not raw
        or raw != raw.strip()
        or raw.startswith("/")
        or "\\" in raw
        or any(part in {"", ".", ".."} for part in raw.split("/"))
    ):
        raise BuildManifestError("chemin d'objet non canonique")
    return raw


def _object_trace_token(path: str) -> str:
    """Return a one-line TeX-safe identifier bound to a canonical path."""

    canonical = _canonical_object_path(path)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:40]


def _ordered_object_trace(
    log_text: str,
    *,
    traced_inputs: list[str],
    declared_objects: list[str],
) -> list[str]:
    """Cross balanced log markers with declared objects opened by TeX."""

    prefixes = {
        "NEXUS_OBJECT_BEGIN:": "begin",
        "NEXUS_OBJECT_END:": "end",
    }
    markers: list[tuple[str, str]] = []
    for line in log_text.splitlines():
        stripped = line.strip()
        for prefix, kind in prefixes.items():
            if stripped.startswith(prefix):
                markers.append((kind, stripped.removeprefix(prefix)))
                break
    if not markers:
        raise BuildManifestError("marqueurs de trace objets absents")

    if not declared_objects:
        raise BuildManifestError("objets déclarés invalides")
    canonical_declared = [
        _canonical_object_path(path) for path in declared_objects
    ]
    if len(canonical_declared) != len(set(canonical_declared)):
        raise BuildManifestError("objets déclarés invalides")
    declared_by_token: dict[str, str] = {}
    for path in canonical_declared:
        token = _object_trace_token(path)
        if token in declared_by_token:
            raise BuildManifestError("collision d'identifiants de trace objets")
        declared_by_token[token] = path
    opened_by_tex = set(traced_inputs)
    trace: list[str] = []
    completed: set[str] = set()
    current: str | None = None

    for kind, token in markers:
        if len(token) != 40 or any(
            character not in "0123456789abcdef" for character in token
        ):
            raise BuildManifestError("identifiant de marqueur invalide")
        if kind == "begin":
            if current is not None:
                raise BuildManifestError("ordre des marqueurs objets invalide")
            if token in completed:
                raise BuildManifestError("bloc objet marqué dupliqué")
            current = token
            continue
        if current is None:
            raise BuildManifestError("ordre des marqueurs objets invalide")
        if token != current:
            raise BuildManifestError("identité BEGIN/END incohérente")
        path = declared_by_token.get(token)
        if path is None:
            raise BuildManifestError("objet marqué non déclaré")
        if path not in opened_by_tex:
            raise BuildManifestError(
                f"objet marqué absent du traceur FLS: {path}"
            )
        trace.append(path)
        completed.add(token)
        current = None

    if current is not None:
        raise BuildManifestError("marqueurs de trace objets déséquilibrés")
    return trace


def _run_local_pdf_preflight(
    pdf_path: Path,
    *,
    expected_pages: int,
    reproducibility: Mapping[str, object],
) -> dict[str, str]:
    environment = _sanitized_build_environment(reproducibility)
    try:
        pdfinfo = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            env=environment,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            timeout=20,
        )
        pdffonts = subprocess.run(
            ["pdffonts", str(pdf_path)],
            env=environment,
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


def _student_text_violations(text: str) -> list[str]:
    checks = (
        (
            "identifiant interne",
            r"\b(?:1SPE|1NSI)-[A-Z0-9]+(?:-[A-Z0-9]+)*",
        ),
        (
            "corrigé",
            r"(?im:\bcorrigés?\b|\bcorriges\b(?=[ \t]*(?:[.:;!?-][ \t]*)?$))",
        ),
        ("barème enseignant", r"(?i:\bbar[èe]me indicatif\b)"),
        (
            "note enseignant",
            r"(?i:\b(?:note|réponse|reponse)\s+(?:professeur|enseignant)\b)",
        ),
    )
    return [reason for reason, pattern in checks if re.search(pattern, text)]


def _run_local_student_separation(
    pdf_path: Path,
    *,
    reproducibility: Mapping[str, object],
) -> None:
    environment = _sanitized_build_environment(reproducibility)
    try:
        extracted = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            env=environment,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BuildManifestError(
            "contrôle local de séparation élève indisponible"
        ) from exc
    if extracted.returncode != 0:
        raise BuildManifestError("extraction textuelle élève en échec")
    violations = _student_text_violations(extracted.stdout)
    if violations:
        raise BuildManifestError(
            "séparation élève rouge: " + ", ".join(violations)
        )


def _derive_receipt_evidence(
    root: Path,
    receipt: Mapping[str, Any],
    *,
    inventory: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], Callable[[dict[str, Any]], None]]:
    inventory_module = _load_inventory_module()
    initial_git_snapshot = _capture_git_snapshot(root)
    if inventory is None:
        inventory = inventory_module.build_inventory(root)
    source_digest = str(inventory["source_digest"])
    model_digest = str(inventory_module._model_digest(inventory))
    _require_git_snapshot(
        root,
        initial_git_snapshot,
        phase="pendant la dérivation de l'inventaire",
    )
    head, branch, dirty = initial_git_snapshot[0]
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

    run_id = _validate_run_id(receipt.get("run_id"))
    evidence_sha256 = receipt.get("evidence_sha256")
    if not isinstance(evidence_sha256, Mapping) or set(
        evidence_sha256
    ) != _EVIDENCE_FIELDS:
        raise BuildManifestError("evidence_sha256 incomplet ou champs inattendus")
    expected_evidence = {
        name: _validate_sha256(
            evidence_sha256[name],
            role=f"de preuve {name}",
        )
        for name in _EVIDENCE_FIELDS
    }
    receipt_reproducibility = _validate_reproducibility(
        receipt.get("reproducibility"),
        role="du receipt",
    )
    reproducibility, config_payload = _load_reproducibility_control(root)
    if receipt_reproducibility != reproducibility:
        raise BuildManifestError(
            "reproductibilité du receipt différente de la config"
        )
    receipt_tool_versions = _validate_tool_versions(
        receipt.get("tool_versions"),
        role="du receipt",
    )
    local_tool_versions = _collect_local_tool_versions(reproducibility)
    if receipt_tool_versions != local_tool_versions:
        raise BuildManifestError(
            "versions d'outils du receipt différentes des versions locales"
        )

    dependencies = _receipt_string_list(
        receipt,
        "generated_dependencies",
        nonempty=False,
    )
    declared_objects = declared[identity].get("included_objects")
    if not isinstance(declared_objects, list) or not declared_objects:
        raise BuildManifestError("assemblage déclaré sans objets traçables")

    proof_specs = {
        "master": (receipt.get("master_path"), "master LaTeX"),
        "log": (receipt.get("log_path"), "journal LaTeX"),
        "fls": (receipt.get("fls_path"), "traceur FLS"),
        "pdf": (pdf_path, "PDF"),
        "preflight": (
            receipt.get("preflight_report"),
            "rapport de préflight",
        ),
    }
    proof_payloads = {
        name: _read_proof_file(root, path, role=role)
        for name, (path, role) in proof_specs.items()
    }
    proof_hashes = {
        name: _sha256_payload(payload)
        for name, payload in proof_payloads.items()
    }
    for name, expected in expected_evidence.items():
        if proof_hashes[name] != expected:
            raise BuildManifestError(f"digest de preuve {name} incohérent")
    proof_hashes["config"] = _sha256_payload(config_payload)

    _validate_run_marker(
        proof_payloads["master"],
        run_id=run_id,
        role="du master",
        tex_line=True,
    )
    _validate_run_marker(
        proof_payloads["log"],
        run_id=run_id,
        role="du journal",
        tex_line=False,
    )
    log_payload = proof_payloads["log"]
    log_text = log_payload.decode("utf-8", errors="replace")
    if (
        "Output written on " not in log_text
        or "Fatal error" in log_text
        or "! Emergency stop" in log_text
    ):
        raise BuildManifestError("journal LaTeX sans compilation prouvée")
    fls_payload = proof_payloads["fls"]
    fls_text = fls_payload.decode("utf-8", errors="replace")
    fls_working_directory = _fls_working_directory(root, fls_text)
    traced_inputs: list[str] = []
    traced_outputs: set[str] = set()
    for line in fls_text.splitlines():
        kind, separator, raw = line.partition(" ")
        if not separator or kind not in {"INPUT", "OUTPUT"}:
            continue
        normalized = _canonical_fls_path(
            root,
            raw.strip(),
            working_directory=fls_working_directory,
        )
        if normalized is None:
            continue
        if kind == "INPUT":
            traced_inputs.append(normalized)
        else:
            traced_outputs.add(normalized)
    master_path = receipt.get("master_path")
    if master_path not in traced_inputs:
        raise BuildManifestError("master absent des INPUT du traceur FLS")
    declared_set = set(declared_objects)
    ordered_trace = _ordered_object_trace(
        log_text,
        traced_inputs=traced_inputs,
        declared_objects=declared_objects,
    )
    included = list(ordered_trace)
    excluded = sorted(declared_set - set(included))
    object_proof_hashes = {
        path: _sha256_payload(
            _read_proof_file(
                root,
                path,
                role=f"objet inclus {path}",
            )
        )
        for path in included
    }
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

    _require_git_snapshot(
        root,
        initial_git_snapshot,
        phase="pendant la capture des preuves",
    )

    digest, pages, _method, reason = inventory_module._pdf_core.inspect_stable_pdf(
        root,
        pdf_path,
        pdfinfo_counter=inventory_module._page_count_with_pdfinfo,
        python_counter=inventory_module._page_count_with_python,
    )
    if (
        reason
        or digest is None
        or pages is None
        or type(pages) is not int
        or pages <= 0
        or digest != proof_hashes["pdf"]
    ):
        raise BuildManifestError(f"PDF non prouvé: {reason or 'preuve absente'}")
    local_preflight = _run_local_pdf_preflight(
        root / pdf_path,
        expected_pages=pages,
        reproducibility=reproducibility,
    )
    if _requires_student_separation(manual, variant):
        _run_local_student_separation(
            root / pdf_path,
            reproducibility=reproducibility,
        )
    preflight_payload = proof_payloads["preflight"]
    try:
        preflight = json.loads(preflight_payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise BuildManifestError("rapport de préflight JSON invalide") from exc
    _validate_preflight_report(
        preflight,
        run_id=run_id,
        pdf_path=pdf_path,
        pdf_sha256=digest,
        page_count=pages,
        tool_versions=local_tool_versions,
        reproducibility=reproducibility,
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
    if _requires_student_separation(manual, variant):
        receipt_student_gate = gates.get("student_separation")
        if (
            not isinstance(receipt_student_gate, Mapping)
            or receipt_student_gate.get("passed") is not True
        ):
            raise BuildManifestError(
                "receipt sans preuve de séparation élève"
            )
        normalized_gates["student_separation"] = {"passed": True}
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
        "reproducibility": dict(reproducibility),
        "source_digest": source_digest,
        "tool_versions": dict(local_tool_versions),
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
        _require_git_snapshot(
            root,
            initial_git_snapshot,
            phase="avant la validation finale",
        )
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
        for name, (path, role) in proof_specs.items():
            current_payload = _read_proof_file(root, path, role=role)
            if _sha256_payload(current_payload) != proof_hashes[name]:
                raise BuildManifestError(
                    f"preuve {name} modifiée avant publication du manifeste"
                )
        for object_path, expected_digest in object_proof_hashes.items():
            current_object = _read_proof_file(
                root,
                object_path,
                role=f"objet inclus {object_path}",
            )
            if _sha256_payload(current_object) != expected_digest:
                raise BuildManifestError(
                    f"objet inclus {object_path} modifié avant publication"
                )
        current_config_payload = _read_proof_file(
            root,
            _REPRODUCIBILITY_CONFIG,
            role="config de reproductibilité",
        )
        if _sha256_payload(current_config_payload) != proof_hashes["config"]:
            raise BuildManifestError(
                "preuve config modifiée avant publication du manifeste"
            )
        current_reproducibility, _payload = _load_reproducibility_control(root)
        if current_reproducibility != reproducibility:
            raise BuildManifestError(
                "reproductibilité modifiée avant publication du manifeste"
            )
        current_tool_versions = _collect_local_tool_versions(reproducibility)
        if current_tool_versions != local_tool_versions:
            raise BuildManifestError(
                "versions d'outils modifiées avant publication du manifeste"
            )
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
            reproducibility=reproducibility,
        )
        if _requires_student_separation(manual, variant):
            _run_local_student_separation(
                root / pdf_path,
                reproducibility=reproducibility,
            )
        current_preflight_payload = _read_proof_file(
            root,
            receipt.get("preflight_report"),
            role="rapport de préflight",
        )
        try:
            current_preflight = json.loads(
                current_preflight_payload.decode("utf-8")
            )
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise BuildManifestError(
                "rapport de préflight JSON invalide avant publication"
            ) from exc
        _validate_preflight_report(
            current_preflight,
            run_id=run_id,
            pdf_path=pdf_path,
            pdf_sha256=digest,
            page_count=pages,
            tool_versions=current_tool_versions,
            reproducibility=current_reproducibility,
        )
        _require_git_snapshot(
            root,
            initial_git_snapshot,
            phase="pendant la validation finale",
        )

    _require_git_snapshot(
        root,
        initial_git_snapshot,
        phase="avant le retour des preuves dérivées",
    )
    return envelope, build, validate


def _read_schema_valid_manifest(
    root: Path,
) -> tuple[dict[str, Any], str]:
    inventory_module = _load_inventory_module()
    try:
        snapshot = inventory_module._ConfinedJsonSnapshot(
            root=root,
            relative=inventory_module.PurePosixPath(
                _MANIFEST_RELATIVE.as_posix()
            ),
            role="manifeste de build",
        )
        snapshot.__enter__()
        payload = snapshot.json_mapping()
        inventory_module._validate_artifact_schema(
            payload,
            root=root,
            path=_MANIFEST_RELATIVE,
        )
        builds = payload.get("builds")
        if not isinstance(builds, list):
            raise BuildManifestError("builds du manifeste invalide")
        snapshot.verify()
        return dict(payload), _sha256_payload(snapshot.payload)
    except BuildManifestError:
        raise
    except Exception as exc:
        raise BuildManifestError(
            f"manifeste vide non sûr ou invalide: {type(exc).__name__}"
        ) from exc
    finally:
        if "snapshot" in locals():
            snapshot.close()


def _validate_refresh_source_is_empty(
    root: Path,
) -> tuple[dict[str, Any], str]:
    payload, manifest_digest = _read_schema_valid_manifest(root)
    if payload.get("builds") != []:
        raise BuildManifestError(
            "refresh interdit: le manifeste doit être strictement vide"
        )
    if payload.get("build_state_digest") != build_state_digest([]):
        raise BuildManifestError("build_state_digest vide incohérent")
    return payload, manifest_digest


def record_from_receipt(receipt_path: Path) -> None:
    """Validate and transactionally record one closed build receipt."""

    root = _git_root_from_path(receipt_path)
    initial_git_snapshot = _capture_git_snapshot(root)
    if initial_git_snapshot[0][2]:
        raise BuildManifestError(
            "dépôt Git sale hors manifeste canonique"
        )
    receipt = _read_receipt(receipt_path, root)
    compile_succeeded = receipt.get("compile_succeeded") is True
    preflight_succeeded = receipt.get("preflight_succeeded") is True
    if not compile_succeeded:
        raise BuildManifestError("receipt sans compilation réussie")
    if not preflight_succeeded:
        raise BuildManifestError("receipt sans préflight réussi")
    current, _current_manifest_digest = _read_schema_valid_manifest(root)
    try:
        if current["builds"] == []:
            _empty_manifest, empty_manifest_digest = (
                _validate_refresh_source_is_empty(root)
            )
            inventory_module = _load_inventory_module()
            inventory = (
                inventory_module._build_inventory_for_empty_manifest_refresh(
                    root
                )
            )
            _require_git_snapshot(
                root,
                initial_git_snapshot,
                phase="pendant le calcul borné de l'inventaire",
            )
            envelope, build, validator = _derive_receipt_evidence(
                root,
                receipt,
                inventory=inventory,
            )
        else:
            envelope, build, validator = _derive_receipt_evidence(
                root,
                receipt,
            )
    except BuildManifestError:
        raise
    except Exception as exc:
        raise BuildManifestError(
            f"dérivation du receipt refusée: {type(exc).__name__}"
        ) from exc
    _require_git_snapshot(
        root,
        initial_git_snapshot,
        phase="avant l'enregistrement du receipt",
    )
    manifest_path = root / _MANIFEST_RELATIVE
    if current["builds"] != []:
        record_successful_build(
            manifest_path,
            build,
            envelope=envelope,
            compile_succeeded=compile_succeeded,
            preflight_succeeded=preflight_succeeded,
            validator=validator,
        )
        return

    def publish_bootstrap() -> None:
        _validate_build_shape(build)
        current_head, current_branch, current_dirty = initial_git_snapshot[0]
        provenance = envelope.get("provenance")
        if (
            not isinstance(provenance, Mapping)
            or provenance.get("head_sha") != current_head
            or provenance.get("branch") != current_branch
            or provenance.get("dirty") is not current_dirty
        ):
            raise BuildManifestError(
                "provenance de l'enveloppe périmée ou forgée"
            )
        if build.get("git_sha") != current_head:
            raise BuildManifestError("git_sha du build périmé")
        inventory_module = _load_inventory_module()

        def replace_empty(
            current_manifest: dict[str, Any],
            transaction_git_state: tuple[str, str, bool],
        ) -> dict[str, Any]:
            if transaction_git_state != initial_git_snapshot[0]:
                raise BuildManifestError(
                    "état Git modifié avant le bootstrap"
                )
            try:
                inventory_module._validate_artifact_schema(
                    current_manifest,
                    root=root,
                    path=_MANIFEST_RELATIVE,
                )
            except Exception as exc:
                raise BuildManifestError(
                    "manifeste bootstrap non conforme au schéma: "
                    f"{type(exc).__name__}"
                ) from exc
            if current_manifest.get("builds") != []:
                raise BuildManifestError(
                    "bootstrap interdit: le manifeste doit être "
                    "strictement vide"
                )
            if current_manifest.get("build_state_digest") != build_state_digest([]):
                raise BuildManifestError(
                    "build_state_digest vide incohérent"
                )
            builds = [dict(build)]
            updated = dict(envelope)
            updated["builds"] = builds
            updated["build_state_digest"] = build_state_digest(builds)
            try:
                validator(updated)
            except Exception as exc:
                raise BuildManifestError(
                    f"validation du manifeste refusée: {type(exc).__name__}"
                ) from exc
            return updated

        _replace_manifest_transactionally(
            manifest_path,
            transform=replace_empty,
            expected_git_state=initial_git_snapshot[0],
            expected_evidence_fingerprint=initial_git_snapshot[1],
            expected_manifest_digest=empty_manifest_digest,
        )

    publish_bootstrap()


def _derive_empty_refresh_envelope(root: Path) -> dict[str, Any]:
    inventory_module = _load_inventory_module()
    try:
        inventory = (
            inventory_module._build_inventory_for_empty_manifest_refresh(
                root
            )
        )
        source_digest = str(inventory["source_digest"])
        model_digest = str(inventory_module._model_digest(inventory))
    except Exception as exc:
        raise BuildManifestError(
            f"calcul borné des digests impossible: {type(exc).__name__}"
        ) from exc
    head, branch, dirty = _git_state(root)
    return {
        "artifact_type": "build_manifest",
        "build_state_digest": build_state_digest([]),
        "builds": [],
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


def refresh_empty_manifest(manifest_path: Path) -> None:
    """Refresh only the stale envelope of a validated empty manifest."""

    root = _repository_root(manifest_path)
    initial_git_state = _git_state(root)
    initial_evidence_fingerprint = _git_evidence_fingerprint(root)
    _validate_refresh_source_is_empty(root)
    envelope = _derive_empty_refresh_envelope(root)
    if (
        _git_state(root) != initial_git_state
        or _git_evidence_fingerprint(root) != initial_evidence_fingerprint
    ):
        raise BuildManifestError("sources modifiées pendant le calcul des digests")
    provenance = envelope.get("provenance")
    if (
        not isinstance(provenance, Mapping)
        or provenance.get("head_sha") != initial_git_state[0]
        or provenance.get("branch") != initial_git_state[1]
        or provenance.get("dirty") is not initial_git_state[2]
    ):
        raise BuildManifestError("provenance rafraîchie incohérente")

    def replace_empty(
        current: dict[str, Any],
        _git_state_snapshot: tuple[str, str, bool],
    ) -> dict[str, Any]:
        builds = current.get("builds")
        if builds != []:
            raise BuildManifestError(
                "refresh interdit: le manifeste doit être strictement vide"
            )
        if current.get("build_state_digest") != build_state_digest([]):
            raise BuildManifestError("build_state_digest vide incohérent")
        inventory_module = _load_inventory_module()
        try:
            inventory_module._validate_artifact_schema(
                current,
                root=root,
                path=_MANIFEST_RELATIVE,
            )
            inventory_module._validate_artifact_schema(
                envelope,
                root=root,
                path=_MANIFEST_RELATIVE,
            )
        except Exception as exc:
            raise BuildManifestError(
                f"validation du manifeste refusée: {type(exc).__name__}"
            ) from exc
        return dict(envelope)

    _replace_manifest_transactionally(
        manifest_path,
        transform=replace_empty,
        expected_git_state=initial_git_state,
        expected_evidence_fingerprint=initial_evidence_fingerprint,
    )


def _validate_invalidation_source_is_stale(
    root: Path,
) -> tuple[dict[str, Any], str]:
    """Confirm a manifest is non-empty, structurally sound, and genuinely stale.

    "Stale" here means the manifest's own recorded provenance ``head_sha`` is
    a strict, non-equal ancestor of the current ``HEAD`` -- i.e. real source
    history has landed since the manifest was written. This is the only
    condition under which :func:`invalidate_stale_manifest` is allowed to
    discard the recorded builds; it refuses on a diverged, reset, or foreign
    ``head_sha`` exactly as strictly as the normal (non-invalidating) load
    path already does for ordinary builds.
    """

    payload, manifest_digest = _read_schema_valid_manifest(root)
    builds = payload.get("builds")
    if builds == []:
        raise BuildManifestError(
            "invalidation inutile: le manifeste est déjà vide, "
            "utiliser --refresh-empty"
        )
    if payload.get("build_state_digest") != build_state_digest(builds):
        raise BuildManifestError("build_state_digest incohérent")
    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise BuildManifestError("provenance du manifeste invalide")
    recorded_head = provenance.get("head_sha")
    current_head = _git_head(root)
    if recorded_head == current_head:
        raise BuildManifestError(
            "manifeste non périmé: son head_sha est déjà le HEAD courant"
        )
    inventory_module = _load_inventory_module()
    inventory_module._require_git_ancestor(
        root,
        recorded_head,
        current_head,
        role="provenance du manifeste à invalider",
    )
    return payload, manifest_digest


def _derive_stale_invalidation_envelope(root: Path) -> dict[str, Any]:
    inventory_module = _load_inventory_module()
    try:
        inventory = (
            inventory_module._build_inventory_for_stale_manifest_invalidation(
                root
            )
        )
        source_digest = str(inventory["source_digest"])
        model_digest = str(inventory_module._model_digest(inventory))
    except Exception as exc:
        raise BuildManifestError(
            f"calcul borné des digests impossible: {type(exc).__name__}"
        ) from exc
    head, branch, dirty = _git_state(root)
    return {
        "artifact_type": "build_manifest",
        "build_state_digest": build_state_digest([]),
        "builds": [],
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


def invalidate_stale_manifest(
    manifest_path: Path,
    *,
    reason: str,
    approved_by: str,
) -> None:
    """Invalidate a validated but source-mismatched, non-empty manifest.

    Unlike :func:`refresh_empty_manifest`, this accepts a manifest whose
    recorded builds no longer match the current source tree -- the case left
    behind whenever unrelated source commits land after the last observed
    build without a fresh re-attestation. It requires an explicit
    human-provided reason and approver, forbids running under CI, requires a
    clean working tree, and only proceeds when the manifest's own recorded
    provenance ``head_sha`` is a strict ancestor of the current ``HEAD``
    (never sideways or backward). The prior manifest content is never
    rewritten or deleted from Git history -- only superseded by a new commit
    -- so it remains permanently recoverable.
    """

    if os.environ.get("CI"):
        raise BuildManifestError("invalidation de manifeste interdite en CI")
    if not isinstance(reason, str) or not reason.strip():
        raise BuildManifestError("justification non vide requise")
    if not isinstance(approved_by, str) or not approved_by.strip():
        raise BuildManifestError("approbateur non vide requis")

    root = _repository_root(manifest_path)
    initial_git_state = _git_state(root)
    initial_evidence_fingerprint = _git_evidence_fingerprint(root)
    if initial_git_state[2]:
        raise BuildManifestError("dépôt Git sale : invalidation refusée")
    _validate_invalidation_source_is_stale(root)
    envelope = _derive_stale_invalidation_envelope(root)
    if (
        _git_state(root) != initial_git_state
        or _git_evidence_fingerprint(root) != initial_evidence_fingerprint
    ):
        raise BuildManifestError("sources modifiées pendant le calcul des digests")
    provenance = envelope.get("provenance")
    if (
        not isinstance(provenance, Mapping)
        or provenance.get("head_sha") != initial_git_state[0]
        or provenance.get("branch") != initial_git_state[1]
        or provenance.get("dirty") is not initial_git_state[2]
    ):
        raise BuildManifestError("provenance rafraîchie incohérente")

    def replace_stale(
        current: dict[str, Any],
        _git_state_snapshot: tuple[str, str, bool],
    ) -> dict[str, Any]:
        builds = current.get("builds")
        if not isinstance(builds, list) or builds == []:
            raise BuildManifestError(
                "invalidation interdite: le manifeste n'est plus non vide"
            )
        if current.get("build_state_digest") != build_state_digest(builds):
            raise BuildManifestError("build_state_digest incohérent")
        inventory_module = _load_inventory_module()
        try:
            inventory_module._validate_artifact_schema(
                current,
                root=root,
                path=_MANIFEST_RELATIVE,
            )
            inventory_module._validate_artifact_schema(
                envelope,
                root=root,
                path=_MANIFEST_RELATIVE,
            )
        except Exception as exc:
            raise BuildManifestError(
                f"validation du manifeste refusée: {type(exc).__name__}"
            ) from exc
        return dict(envelope)

    _replace_manifest_transactionally(
        manifest_path,
        transform=replace_stale,
        expected_git_state=initial_git_state,
        expected_evidence_fingerprint=initial_evidence_fingerprint,
    )


def _run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Enregistre une preuve de build Nexus validée localement."
    )
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument(
        "--receipt",
        type=Path,
        help="receipt JSON post-compilation et post-préflight",
    )
    actions.add_argument(
        "--refresh-empty",
        action="store_true",
        help="rafraîchit uniquement l'enveloppe du manifeste vide canonique",
    )
    actions.add_argument(
        "--invalidate-stale",
        action="store_true",
        help=(
            "invalide un manifeste non vide mais périmé (source_digest "
            "incohérent avec le HEAD courant) et le remet à l'état vide, "
            "sous conditions strictes ; requiert --reason et --approved-by"
        ),
    )
    parser.add_argument(
        "--reason",
        help="justification humaine non vide, requise avec --invalidate-stale",
    )
    parser.add_argument(
        "--approved-by",
        help="approbateur humain non vide, requis avec --invalidate-stale",
    )
    arguments = parser.parse_args(argv)
    if arguments.invalidate_stale and (
        not arguments.reason or not arguments.approved_by
    ):
        parser.error(
            "--invalidate-stale requiert --reason et --approved-by non vides"
        )
    try:
        if arguments.refresh_empty:
            refresh_empty_manifest(Path.cwd() / _MANIFEST_RELATIVE)
        elif arguments.invalidate_stale:
            invalidate_stale_manifest(
                Path.cwd() / _MANIFEST_RELATIVE,
                reason=arguments.reason,
                approved_by=arguments.approved_by,
            )
        else:
            record_from_receipt(arguments.receipt)
    except BuildManifestError as exc:
        print(f"build manifest refusé: {exc}", file=sys.stderr)
        return 2
    if arguments.refresh_empty:
        print("build manifest vide rafraîchi")
    elif arguments.invalidate_stale:
        print("build manifest périmé invalidé")
    else:
        print("build manifest enregistré")
    return 0


if __name__ == "__main__":
    raise SystemExit(_run(sys.argv[1:]))
