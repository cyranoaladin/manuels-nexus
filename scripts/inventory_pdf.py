"""PDF attribution and bounded page-count helpers."""

from __future__ import annotations

import errno
import os
import re
import stat
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping


PDF_MUTATION_REASON = "fichier PDF modifié pendant le comptage sécurisé"
_PDF_COPY_CHUNK_SIZE = 1024 * 1024
_DIRECTORY_OPEN_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_PDF_OPEN_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
_SNAPSHOT_OPEN_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC


class _PdfAccessError(Exception):
    """Expected refusal while pinning or snapshotting a tracked PDF."""


def page_count_with_pdfinfo(
    path: Path,
    *,
    runner: Callable[..., Any],
    timeout_seconds: int,
) -> tuple[int | None, str | None]:
    try:
        completed = runner(
            ["pdfinfo", str(path)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return None, f"pdfinfo timeout ({timeout_seconds}s)"
    except OSError as exc:
        return None, f"pdfinfo indisponible: {type(exc).__name__}"
    if completed.returncode != 0:
        return None, f"pdfinfo en echec (code {completed.returncode})"
    match = re.search(r"(?m)^Pages:\s*(\d+)\s*$", completed.stdout)
    if match is None:
        return None, "pdfinfo ne fournit pas le nombre de pages"
    return int(match.group(1)), None


def attribute_pdf(path: str, inventory: Mapping[str, Any]) -> dict[str, Any]:
    pure = PurePosixPath(path)
    stem = pure.stem
    for manual_id, manual_model in inventory["manuals"].items():
        for chapter_id in manual_model["chapters"]:
            if chapter_id in pure.parts or stem.startswith(chapter_id + "_"):
                prefix = chapter_id + "_"
                return {
                    "chapter": chapter_id,
                    "manual": manual_id,
                    "scope": "chapter",
                    "variant": stem[len(prefix) :] if stem.startswith(prefix) else None,
                }
    aliases = (
        ("MANUEL_TSPE_2026-2027", "TSPE_2026_2027"),
        ("MANUEL_TSPE_2026_2027", "TSPE_2026_2027"),
        ("MANUEL_1SPE", "1SPE"),
        ("MANUEL_1NSI", "1NSI"),
        ("MANUEL_TNSI", "TNSI"),
    )
    for prefix, manual_id in aliases:
        if stem == prefix or stem.startswith(prefix + "_"):
            return {
                "chapter": None,
                "manual": manual_id,
                "scope": "manual",
                "variant": (
                    stem[len(prefix) + 1 :] if stem.startswith(prefix + "_") else None
                ),
            }
    return {"chapter": None, "manual": None, "scope": None, "variant": None}


def aggregate_artifacts(
    inventory: dict[str, Any],
    *,
    compiled_source_roles: frozenset[str],
    manual_build_roots: Mapping[str, str],
) -> None:
    manual_variants: dict[tuple[str, str], set[str]] = defaultdict(set)
    chapter_variants: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for artifact in inventory["pdfs"]:
        if not is_compilation_evidence(
            artifact,
            compiled_source_roles=compiled_source_roles,
            manual_build_roots=manual_build_roots,
        ):
            continue
        manual_id = artifact["manual"]
        if manual_id is None or manual_id not in inventory["manuals"]:
            continue
        manual = inventory["manuals"][manual_id]
        manual["compiled_artifacts"].append(dict(artifact))
        scope = artifact["scope"]
        if artifact["variant"] and scope in {"chapter", "manual", "static"}:
            manual_variants[(manual_id, scope)].add(artifact["variant"])
        chapter_id = artifact["chapter"]
        if chapter_id is None or chapter_id not in manual["chapters"]:
            continue
        chapter = manual["chapters"][chapter_id]
        chapter["compiled_artifacts"].append(dict(artifact))
        if artifact["variant"] and scope in {"chapter", "manual", "static"}:
            chapter_variants[(manual_id, chapter_id, scope)].add(artifact["variant"])
    for manual_id, manual in inventory["manuals"].items():
        for scope in ("chapter", "manual", "static"):
            manual["compiled_variants"][scope] = sorted(
                manual_variants[(manual_id, scope)]
            )
        for chapter_id, chapter in manual["chapters"].items():
            for scope in ("chapter", "manual", "static"):
                chapter["compiled_variants"][scope] = sorted(
                    chapter_variants[(manual_id, chapter_id, scope)]
                )


def is_compilation_evidence(
    artifact: Mapping[str, Any],
    *,
    compiled_source_roles: frozenset[str],
    manual_build_roots: Mapping[str, str],
) -> bool:
    page_count = artifact.get("page_count")
    return (
        artifact.get("source_role") in compiled_source_roles
        and artifact.get("status") == "counted"
        and isinstance(page_count, int)
        and not isinstance(page_count, bool)
        and page_count > 0
        and _is_canonical_manual_pdf_path(
            artifact,
            manual_build_roots=manual_build_roots,
        )
    )


def _is_canonical_manual_pdf_path(
    artifact: Mapping[str, Any],
    *,
    manual_build_roots: Mapping[str, str],
) -> bool:
    path = artifact.get("path")
    manual = artifact.get("manual")
    build_root = manual_build_roots.get(manual) if isinstance(manual, str) else None
    if not isinstance(path, str) or not isinstance(build_root, str):
        return False
    if "\\" in path:
        return False
    raw_parts = path.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        return False
    pure_path = PurePosixPath(path)
    pure_root = PurePosixPath(build_root)
    try:
        relative = pure_path.relative_to(pure_root)
    except ValueError:
        return False
    return bool(relative.parts) and relative.suffix.lower() == ".pdf"


def _stat_fingerprint(value: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        stat.S_IFMT(value.st_mode),
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def _close_file_descriptors(descriptors: list[int]) -> None:
    for descriptor in reversed(descriptors):
        try:
            os.close(descriptor)
        except OSError:
            pass


def _pdf_path_components(path: str) -> tuple[str, ...]:
    if not isinstance(path, str) or path.startswith("/"):
        raise _PdfAccessError("chemin du fichier PDF suivi non canonique")
    components = tuple(path.split("/"))
    if len(components) < 2 or any(
        component in {"", ".", ".."} for component in components
    ):
        raise _PdfAccessError("chemin du fichier PDF suivi non canonique")
    return components


def _open_error_reason(exc: OSError, *, leaf: bool) -> str:
    if isinstance(exc, FileNotFoundError):
        return "fichier PDF suivi absent du checkout"
    if leaf and exc.errno == errno.ELOOP:
        return "fichier PDF suivi non régulier: lien symbolique interdit"
    if leaf:
        return (
            "fichier PDF suivi inaccessible sans suivi de lien: "
            f"{type(exc).__name__}"
        )
    return "composant parent du PDF non sûr ou non répertoire: " f"{type(exc).__name__}"


def _open_pinned_pdf(
    root: Path,
    path: str,
) -> tuple[tuple[str, ...], list[int], list[tuple[int, int, int, int, int, int]], int]:
    components = _pdf_path_components(path)
    parent_descriptors: list[int] = []
    parent_fingerprints: list[tuple[int, int, int, int, int, int]] = []
    try:
        try:
            current = os.open(root, _DIRECTORY_OPEN_FLAGS)
        except OSError as exc:
            raise _PdfAccessError(
                "racine du dépôt inaccessible sans suivi de lien: "
                f"{type(exc).__name__}"
            ) from exc
        parent_descriptors.append(current)
        parent_fingerprints.append(_stat_fingerprint(os.fstat(current)))
        for component in components[:-1]:
            try:
                current = os.open(
                    component,
                    _DIRECTORY_OPEN_FLAGS,
                    dir_fd=current,
                )
            except OSError as exc:
                raise _PdfAccessError(_open_error_reason(exc, leaf=False)) from exc
            parent_descriptors.append(current)
            parent_fingerprints.append(_stat_fingerprint(os.fstat(current)))
        try:
            source_descriptor = os.open(
                components[-1],
                _PDF_OPEN_FLAGS,
                dir_fd=current,
            )
        except OSError as exc:
            raise _PdfAccessError(_open_error_reason(exc, leaf=True)) from exc
    except BaseException:
        _close_file_descriptors(parent_descriptors)
        raise
    return (
        components,
        parent_descriptors,
        parent_fingerprints,
        source_descriptor,
    )


def _copy_pdf_to_private_snapshot(
    source_descriptor: int,
    source_fingerprint: tuple[int, int, int, int, int, int],
    snapshot_descriptor: int,
) -> bool:
    if _stat_fingerprint(os.fstat(source_descriptor)) != source_fingerprint:
        return False
    os.lseek(source_descriptor, 0, os.SEEK_SET)
    copied = 0
    while True:
        chunk = os.read(source_descriptor, _PDF_COPY_CHUNK_SIZE)
        if not chunk:
            break
        copied += len(chunk)
        view = memoryview(chunk)
        while view:
            written = os.write(snapshot_descriptor, view)
            if written <= 0:
                raise OSError("écriture nulle du snapshot PDF")
            view = view[written:]
    os.fsync(snapshot_descriptor)
    return (
        copied == source_fingerprint[3]
        and _stat_fingerprint(os.fstat(source_descriptor)) == source_fingerprint
    )


def _pinned_pdf_is_unchanged(
    components: tuple[str, ...],
    parent_descriptors: list[int],
    parent_fingerprints: list[tuple[int, int, int, int, int, int]],
    source_descriptor: int,
    source_fingerprint: tuple[int, int, int, int, int, int],
) -> bool:
    try:
        if _stat_fingerprint(os.fstat(source_descriptor)) != source_fingerprint:
            return False
        for descriptor, expected in zip(
            parent_descriptors,
            parent_fingerprints,
            strict=True,
        ):
            if _stat_fingerprint(os.fstat(descriptor)) != expected:
                return False
    except OSError:
        return False

    reopened_descriptors: list[int] = []
    current = parent_descriptors[0]
    try:
        for index, component in enumerate(components[:-1], start=1):
            current = os.open(
                component,
                _DIRECTORY_OPEN_FLAGS,
                dir_fd=current,
            )
            reopened_descriptors.append(current)
            if _stat_fingerprint(os.fstat(current)) != parent_fingerprints[index]:
                return False
        reopened_leaf = os.open(
            components[-1],
            _PDF_OPEN_FLAGS,
            dir_fd=current,
        )
        reopened_descriptors.append(reopened_leaf)
        return _stat_fingerprint(os.fstat(reopened_leaf)) == source_fingerprint
    except OSError:
        return False
    finally:
        _close_file_descriptors(reopened_descriptors)


def _count_stable_pdf(
    root: Path,
    path: str,
    *,
    pdfinfo_counter: Callable[[Path], tuple[int | None, str | None]],
    python_counter: Callable[[Path], tuple[int | None, str | None]],
) -> tuple[int | None, str | None, str | None]:
    try:
        (
            components,
            parent_descriptors,
            parent_fingerprints,
            source_descriptor,
        ) = _open_pinned_pdf(root, path)
    except _PdfAccessError as exc:
        return None, None, str(exc)

    try:
        source_fingerprint = _stat_fingerprint(os.fstat(source_descriptor))
        if source_fingerprint[2] != stat.S_IFREG:
            return (
                None,
                None,
                "fichier PDF suivi non régulier: type de fichier interdit",
            )
        try:
            with tempfile.TemporaryDirectory(
                prefix="nexus-inventory-pdf-"
            ) as temporary:
                temporary_path = Path(temporary)
                temporary_descriptor = os.open(
                    temporary_path,
                    _DIRECTORY_OPEN_FLAGS,
                )
                try:
                    snapshot_descriptor = os.open(
                        "snapshot.pdf",
                        _SNAPSHOT_OPEN_FLAGS,
                        0o600,
                        dir_fd=temporary_descriptor,
                    )
                    try:
                        os.fchmod(snapshot_descriptor, 0o600)
                        stable_copy = _copy_pdf_to_private_snapshot(
                            source_descriptor,
                            source_fingerprint,
                            snapshot_descriptor,
                        )
                    finally:
                        os.close(snapshot_descriptor)
                finally:
                    os.close(temporary_descriptor)
                if not stable_copy:
                    return None, None, PDF_MUTATION_REASON

                snapshot_path = temporary_path / "snapshot.pdf"
                count, pdfinfo_reason = pdfinfo_counter(snapshot_path)
                if count is not None:
                    method = "pdfinfo"
                    reason = None
                else:
                    count, python_reason = python_counter(snapshot_path)
                    if count is not None:
                        method = "python"
                        reason = None
                    else:
                        method = None
                        reasons = [
                            item for item in (pdfinfo_reason, python_reason) if item
                        ]
                        reason = "; ".join(reasons) or "aucun lecteur PDF disponible"
                if not _pinned_pdf_is_unchanged(
                    components,
                    parent_descriptors,
                    parent_fingerprints,
                    source_descriptor,
                    source_fingerprint,
                ):
                    return None, None, PDF_MUTATION_REASON
                return count, method, reason
        except OSError as exc:
            return (
                None,
                None,
                "snapshot PDF privé indisponible: " f"{type(exc).__name__}",
            )
    finally:
        os.close(source_descriptor)
        _close_file_descriptors(parent_descriptors)


def inventory_pdfs(
    root: Path,
    tracked: tuple[str, ...],
    inventory: dict[str, Any],
    *,
    source_roles: Mapping[str, str],
    pdfinfo_counter: Callable[[Path], tuple[int | None, str | None]],
    python_counter: Callable[[Path], tuple[int | None, str | None]],
) -> list[dict[str, Any]]:
    """Attribute and count every tracked PDF with bounded fallbacks."""

    artifacts: list[dict[str, Any]] = []
    for path in (path for path in tracked if path.lower().endswith(".pdf")):
        attribution = attribute_pdf(path, inventory)
        base = {
            "chapter": attribution["chapter"],
            "manual": attribution["manual"],
            "path": path,
            "scope": attribution["scope"],
            "source_role": source_roles[path],
            "variant": attribution["variant"],
        }
        if attribution["manual"] is None:
            inventory["anomalies"]["unattributed_pdfs"].append(
                {
                    "champ": "attribution",
                    "cible": path,
                    "raison": "PDF suivi sans attribution fiable a un livrable",
                    "source": path,
                }
            )
        count, method, reason = _count_stable_pdf(
            root,
            path,
            pdfinfo_counter=pdfinfo_counter,
            python_counter=python_counter,
        )
        artifacts.append(
            base
            | {
                "page_count": count,
                "page_count_method": method,
                "reason": reason,
                "status": (
                    "counted" if count is not None else "page_count_unavailable"
                ),
            }
        )
    return artifacts
