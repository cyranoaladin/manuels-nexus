#!/usr/bin/env python3
"""Secure archive extraction helpers for untrusted ZIP and TAR payloads."""

from __future__ import annotations

import logging
import shutil
import stat
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import IO


DEFAULT_MAX_TOTAL_UNCOMPRESSED_BYTES = 500 * 1024 * 1024
DEFAULT_MAX_FILES = 10_000
DEFAULT_MAX_COMPRESSION_RATIO = 100.0
DEFAULT_RATIO_MIN_UNCOMPRESSED_BYTES = 1024 * 1024
COPY_CHUNK_BYTES = 1024 * 1024
LOGGER = logging.getLogger(__name__)


class ArchiveSecurityError(ValueError):
    """Raised when an archive member would escape or exceed extraction limits."""


@dataclass(frozen=True)
class ArchiveSecurityLimits:
    max_total_uncompressed_bytes: int = DEFAULT_MAX_TOTAL_UNCOMPRESSED_BYTES
    max_files: int = DEFAULT_MAX_FILES
    max_compression_ratio: float = DEFAULT_MAX_COMPRESSION_RATIO
    ratio_min_uncompressed_bytes: int = DEFAULT_RATIO_MIN_UNCOMPRESSED_BYTES


def safe_extract_zip(
    archive_path: str | Path,
    destination: str | Path,
    *,
    limits: ArchiveSecurityLimits = ArchiveSecurityLimits(),
) -> None:
    """Extract a ZIP archive after zip-slip and zip-bomb validation.

    The archive is first validated from metadata, then extracted into a sibling
    ``.part`` directory. The final destination is populated only after all
    members have been copied successfully, so security failures leave no partial
    files in the official target.
    """
    archive = Path(archive_path)
    target_dir = Path(destination)
    staging: Path | None = None
    try:
        with zipfile.ZipFile(archive, "r") as handle:
            members = handle.infolist()
            _validate_member_count(len(members), limits)
            _preflight_zip_members(members, target_dir, limits)
            staging = _prepare_staging_dir(target_dir)
            total = 0
            for member in members:
                member_target = _member_target(staging, member.filename)
                if member.is_dir():
                    member_target.mkdir(parents=True, exist_ok=True)
                    continue
                member_target.parent.mkdir(parents=True, exist_ok=True)
                with handle.open(member, "r") as source:
                    total += _copy_stream_with_limit(
                        source,
                        member_target,
                        limits.max_total_uncompressed_bytes - total,
                    )
            _commit_staging_dir(staging, target_dir)
            staging = None
    except ArchiveSecurityError as exc:
        _cleanup_staging_dir(staging)
        LOGGER.warning("archive extraction refused: %s", exc)
        raise
    except Exception:
        _cleanup_staging_dir(staging)
        raise
    finally:
        _cleanup_staging_dir(staging)


def safe_extract_tar(
    archive_path: str | Path,
    destination: str | Path,
    *,
    limits: ArchiveSecurityLimits = ArchiveSecurityLimits(),
) -> None:
    """Extract a TAR archive after path, volume and file-count validation."""
    archive = Path(archive_path)
    target_dir = Path(destination)
    staging: Path | None = None
    try:
        with tarfile.open(archive, "r:*") as handle:
            members = handle.getmembers()
            _validate_member_count(len(members), limits)
            _preflight_tar_members(members, target_dir, archive.stat().st_size, limits)
            staging = _prepare_staging_dir(target_dir)
            total = 0
            for member in members:
                member_target = _member_target(staging, member.name)
                if member.isdir():
                    member_target.mkdir(parents=True, exist_ok=True)
                    continue
                if not member.isfile():
                    raise ArchiveSecurityError(f"type de membre tar refuse: {member.name}")
                member_target.parent.mkdir(parents=True, exist_ok=True)
                source = handle.extractfile(member)
                if source is None:
                    raise ArchiveSecurityError(f"membre tar illisible: {member.name}")
                with source:
                    total += _copy_stream_with_limit(
                        source,
                        member_target,
                        limits.max_total_uncompressed_bytes - total,
                    )
            _commit_staging_dir(staging, target_dir)
            staging = None
    except ArchiveSecurityError as exc:
        _cleanup_staging_dir(staging)
        LOGGER.warning("archive extraction refused: %s", exc)
        raise
    except Exception:
        _cleanup_staging_dir(staging)
        raise
    finally:
        _cleanup_staging_dir(staging)


def _preflight_zip_members(
    members: list[zipfile.ZipInfo],
    destination: Path,
    limits: ArchiveSecurityLimits,
) -> None:
    total = 0
    targets: set[Path] = set()
    for member in members:
        member_target = _member_target(destination, member.filename)
        _validate_unique_target(member_target, targets, member.filename)
        if member.is_dir():
            continue
        _validate_zip_member_type(member)
        total += member.file_size
        _validate_total_size(total, limits)
        _validate_compression_ratio(member.file_size, member.compress_size, limits)


def _preflight_tar_members(
    members: list[tarfile.TarInfo],
    destination: Path,
    archive_compressed_size: int,
    limits: ArchiveSecurityLimits,
) -> None:
    total = 0
    targets: set[Path] = set()
    for member in members:
        member_target = _member_target(destination, member.name)
        _validate_unique_target(member_target, targets, member.name)
        if member.isdir():
            continue
        if not member.isfile():
            raise ArchiveSecurityError(f"type de membre tar refuse: {member.name}")
        total += member.size
        _validate_total_size(total, limits)
    _validate_compression_ratio(total, archive_compressed_size, limits)


def _member_target(root: Path, member_name: str) -> Path:
    normalized_name = member_name.replace("\\", "/")
    windows_path = PureWindowsPath(member_name)
    if (
        not normalized_name
        or normalized_name == "."
        or PurePosixPath(normalized_name).is_absolute()
        or windows_path.is_absolute()
        or bool(windows_path.drive)
        or member_name.startswith("\\")
    ):
        raise ArchiveSecurityError(
            f"Tentative de Zip-Slip détectée (zip-slip): chemin archive absolu refuse: {member_name}"
        )
    root_resolved = root.resolve()
    target = (root / normalized_name).resolve()
    try:
        target.relative_to(root_resolved)
    except ValueError as exc:
        raise ArchiveSecurityError(
            "Tentative de Zip-Slip détectée (zip-slip): "
            f"membre hors du repertoire cible: {member_name}"
        ) from exc
    return target


def _validate_unique_target(target: Path, targets: set[Path], member_name: str) -> None:
    if target in targets:
        raise ArchiveSecurityError(f"chemin archive doublon refuse: {member_name}")
    targets.add(target)


def _validate_zip_member_type(member: zipfile.ZipInfo) -> None:
    mode = (member.external_attr >> 16) & 0xFFFF
    if stat.S_IFMT(mode) == stat.S_IFLNK:
        raise ArchiveSecurityError(f"type de membre zip refuse (symlink): {member.filename}")


def _validate_member_count(count: int, limits: ArchiveSecurityLimits) -> None:
    if count > limits.max_files:
        raise ArchiveSecurityError(
            f"zip-bomb: nombre de fichiers {count} > {limits.max_files}"
        )


def _validate_total_size(total: int, limits: ArchiveSecurityLimits) -> None:
    if total > limits.max_total_uncompressed_bytes:
        raise ArchiveSecurityError(
            "zip-bomb: taille decompression "
            f"{total} > {limits.max_total_uncompressed_bytes}"
        )


def _validate_compression_ratio(
    uncompressed_size: int,
    compressed_size: int,
    limits: ArchiveSecurityLimits,
) -> None:
    if uncompressed_size <= limits.ratio_min_uncompressed_bytes:
        return
    ratio = uncompressed_size / max(compressed_size, 1)
    if ratio > limits.max_compression_ratio:
        raise ArchiveSecurityError(
            f"zip-bomb: ratio decompression {ratio:.1f}x > {limits.max_compression_ratio:.1f}x"
        )


def _prepare_staging_dir(destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.with_name(f"{destination.name}.part")
    _cleanup_staging_dir(staging)
    staging.mkdir(parents=True)
    return staging


def _commit_staging_dir(staging: Path, destination: Path) -> None:
    if not destination.exists():
        staging.rename(destination)
        return

    backup = _unique_sibling(destination, ".backup")
    destination.rename(backup)
    try:
        staging.rename(destination)
    except Exception:
        if destination.exists():
            shutil.rmtree(destination)
        backup.rename(destination)
        raise
    else:
        shutil.rmtree(backup)


def _unique_sibling(path: Path, suffix: str) -> Path:
    candidate = path.with_name(f"{path.name}{suffix}")
    counter = 2
    while candidate.exists():
        candidate = path.with_name(f"{path.name}{suffix}{counter}")
        counter += 1
    return candidate


def _cleanup_staging_dir(staging: Path | None) -> None:
    if staging is not None and staging.exists():
        shutil.rmtree(staging)


def _copy_stream_with_limit(source: IO[bytes], destination: Path, max_bytes: int) -> int:
    copied = 0
    with destination.open("wb") as output:
        while True:
            chunk = source.read(COPY_CHUNK_BYTES)
            if not chunk:
                return copied
            copied += len(chunk)
            if copied > max_bytes:
                raise ArchiveSecurityError("zip-bomb: limite de flux decompresse depassee")
            output.write(chunk)
