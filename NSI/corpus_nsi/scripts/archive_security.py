#!/usr/bin/env python3
"""Compatibility wrapper for the canonical archive security helpers."""

from __future__ import annotations

from scrapping_NSI.safe_archive import (
    ArchiveSecurityError,
    ArchiveSecurityLimits,
    _copy_stream_with_limit,
    _preflight_tar_members,
    _preflight_zip_members,
    _validate_compression_ratio,
    safe_extract_tar,
    safe_extract_zip,
)

__all__ = [
    "ArchiveSecurityError",
    "ArchiveSecurityLimits",
    "_copy_stream_with_limit",
    "_preflight_tar_members",
    "_preflight_zip_members",
    "_validate_compression_ratio",
    "safe_extract_tar",
    "safe_extract_zip",
]
