#!/usr/bin/env python3
"""Extraire de manière déterministe le programme officiel 1SPE 2026."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = "SRC-BO2026-1SPE-MATHS"
EXPECTED_TEXT_SHA256 = (
    "4e70f1989cdb47caf184cb138d839799e895fcdc5addec3737f0216b6bfa33df"
)
MINIMUM_POPPLER_VERSION = (24, 2)
PROCESS_ENV = {"LANG": "C", "LC_ALL": "C", "TZ": "UTC"}
VERSION_TIMEOUT_SECONDS = 10
EXTRACTION_TIMEOUT_SECONDS = 60


class ExtractionError(RuntimeError):
    """Erreur contrôlée qui ne doit jamais remplacer une extraction valide."""


@dataclass(frozen=True)
class OpenSource:
    descriptor: int
    resolved_path: Path
    identity: tuple[int, int]
    expected_sha256: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_source_entry(registry_path: Path) -> dict[str, Any]:
    try:
        registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ExtractionError(f"registre illisible : {registry_path}: {exc}") from exc
    if not isinstance(registry, dict) or not isinstance(registry.get("sources"), list):
        raise ExtractionError(f"registre invalide : {registry_path}")
    matches = [
        entry
        for entry in registry["sources"]
        if isinstance(entry, dict) and entry.get("id") == SOURCE_ID
    ]
    if len(matches) != 1:
        raise ExtractionError(
            f"le registre doit contenir exactement une entrée {SOURCE_ID}"
        )
    return matches[0]


def lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def open_registered_source(source: Path, entry: dict[str, Any]) -> OpenSource:
    registered = lexical_absolute(ROOT / str(entry.get("local_path", "")))
    candidate = lexical_absolute(source)
    if candidate != registered:
        raise ExtractionError(
            f"source refusée : {candidate} ; source enregistrée attendue : {registered}"
        )
    expected = entry.get("sha256")
    if not isinstance(expected, str) or len(expected) != 64:
        raise ExtractionError("SHA-256 attendu absent ou invalide dans le registre")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise ExtractionError(f"source inaccessible : {candidate}: {exc}") from exc
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(resolved, flags)
    except OSError as exc:
        raise ExtractionError(f"ouverture sûre de la source impossible : {exc}") from exc
    try:
        source_stat = os.fstat(descriptor)
    except OSError as exc:
        os.close(descriptor)
        raise ExtractionError(f"inspection de la source impossible : {exc}") from exc
    if not stat.S_ISREG(source_stat.st_mode):
        os.close(descriptor)
        raise ExtractionError(f"source non régulière : {resolved}")
    return OpenSource(
        descriptor=descriptor,
        resolved_path=resolved,
        identity=(source_stat.st_dev, source_stat.st_ino),
        expected_sha256=expected,
    )


def snapshot_source(source: OpenSource, directory: Path) -> Path:
    snapshot = directory / "official-source.pdf"
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        snapshot_descriptor = os.open(snapshot, flags, 0o400)
        digest = hashlib.sha256()
        try:
            os.lseek(source.descriptor, 0, os.SEEK_SET)
            while True:
                block = os.read(source.descriptor, 1024 * 1024)
                if not block:
                    break
                digest.update(block)
                view = memoryview(block)
                while view:
                    written = os.write(snapshot_descriptor, view)
                    view = view[written:]
            os.fchmod(snapshot_descriptor, 0o400)
            os.fsync(snapshot_descriptor)
        finally:
            os.close(snapshot_descriptor)
    except OSError as exc:
        raise ExtractionError(f"snapshot privé de la source impossible : {exc}") from exc
    actual = digest.hexdigest()
    if actual != source.expected_sha256:
        raise ExtractionError(
            f"SHA-256 source incorrect : attendu {source.expected_sha256}, obtenu {actual}"
        )
    return snapshot


def resolve_pdftotext() -> Path:
    executable = shutil.which("pdftotext")
    if executable is None:
        raise ExtractionError("binaire bloquant absent : pdftotext")
    try:
        resolved = Path(executable).resolve(strict=True)
        executable_stat = resolved.stat()
    except OSError as exc:
        raise ExtractionError(f"binaire pdftotext inaccessible : {exc}") from exc
    if not stat.S_ISREG(executable_stat.st_mode) or not os.access(resolved, os.X_OK):
        raise ExtractionError(f"binaire pdftotext non exécutable régulier : {resolved}")
    try:
        result = subprocess.run(
            [os.fspath(resolved), "-v"],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=PROCESS_ENV,
            timeout=VERSION_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ExtractionError(f"contrôle de version pdftotext impossible : {exc}") from exc
    version_output = (result.stdout + result.stderr).decode(
        "utf-8", errors="replace"
    )
    match = re.search(r"\bpdftotext version (\d+)\.(\d+)(?:\.(\d+))?\b", version_output)
    if result.returncode != 0 or match is None:
        raise ExtractionError("identité/version Poppler pdftotext invalide")
    version = tuple(int(match.group(index) or 0) for index in (1, 2, 3))
    if version[:2] < MINIMUM_POPPLER_VERSION:
        raise ExtractionError(
            "version Poppler pdftotext trop ancienne : "
            f"{version[0]}.{version[1]:02d} ; minimum 24.02"
        )
    return resolved


def run_pdftotext(executable: Path, snapshot: Path) -> bytes:
    try:
        result = subprocess.run(
            [os.fspath(executable), "-layout", os.fspath(snapshot), "-"],
            cwd=snapshot.parent,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=PROCESS_ENV,
            timeout=EXTRACTION_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ExtractionError(f"échec d’exécution de pdftotext : {exc}") from exc
    if result.returncode != 0:
        diagnostic = result.stderr.decode("utf-8", errors="replace").strip()
        raise ExtractionError(
            f"pdftotext a retourné {result.returncode}: {diagnostic}"
        )
    try:
        text = result.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ExtractionError("sortie pdftotext non UTF-8") from exc
    content = text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    actual = hashlib.sha256(content).hexdigest()
    if actual != EXPECTED_TEXT_SHA256:
        raise ExtractionError(
            f"SHA-256 texte incorrect : attendu {EXPECTED_TEXT_SHA256}, obtenu {actual}"
        )
    return content


def open_output_directory(output: Path) -> tuple[Path, int]:
    output = lexical_absolute(output)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ExtractionError(
            f"répertoire de sortie inaccessible : {output.parent}: {exc}"
        ) from exc
    flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open("/", flags)
    try:
        for component in output.parent.parts[1:]:
            next_descriptor = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
    except OSError as exc:
        os.close(descriptor)
        raise ExtractionError(
            f"parent symbolique ou non sûr de sortie : {output.parent}: {exc}"
        ) from exc
    return output, descriptor


def check_output_alias(
    output: Path,
    directory_descriptor: int,
    source: OpenSource,
) -> os.stat_result | None:
    if output.resolve(strict=False) == source.resolved_path:
        raise ExtractionError("la sortie ne peut pas remplacer la source")
    try:
        output_stat = os.stat(
            output.name,
            dir_fd=directory_descriptor,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise ExtractionError(f"inspection sûre de la sortie impossible : {exc}") from exc
    if stat.S_ISLNK(output_stat.st_mode):
        raise ExtractionError(f"sortie symbolique refusée : {output}")
    if not stat.S_ISREG(output_stat.st_mode):
        raise ExtractionError(f"sortie non régulière refusée : {output}")
    if (output_stat.st_dev, output_stat.st_ino) == source.identity:
        raise ExtractionError("la sortie ne peut pas être un alias de la source")
    return output_stat


def _fsync_directory(directory_descriptor: int) -> None:
    os.fsync(directory_descriptor)


def atomic_write(
    output: Path,
    directory_descriptor: int,
    content: bytes,
    source: OpenSource,
) -> None:
    temporary_name = f".{output.name}.{next(tempfile._get_candidate_names())}.tmp"
    backup_name = f".{output.name}.{next(tempfile._get_candidate_names())}.bak"
    temporary_exists = False
    backup_exists = False
    published = False
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(temporary_name, flags, 0o600, dir_fd=directory_descriptor)
        temporary_exists = True
        try:
            view = memoryview(content)
            while view:
                written = os.write(descriptor, view)
                view = view[written:]
            os.fchmod(descriptor, 0o644)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

        existing = check_output_alias(output, directory_descriptor, source)
        if existing is not None:
            os.replace(
                output.name,
                backup_name,
                src_dir_fd=directory_descriptor,
                dst_dir_fd=directory_descriptor,
            )
            backup_exists = True
        try:
            os.replace(
                temporary_name,
                output.name,
                src_dir_fd=directory_descriptor,
                dst_dir_fd=directory_descriptor,
            )
            temporary_exists = False
            published = True
            _fsync_directory(directory_descriptor)
        except OSError as publication_error:
            try:
                if published:
                    os.unlink(output.name, dir_fd=directory_descriptor)
                    published = False
                if backup_exists:
                    os.replace(
                        backup_name,
                        output.name,
                        src_dir_fd=directory_descriptor,
                        dst_dir_fd=directory_descriptor,
                    )
                    backup_exists = False
                _fsync_directory(directory_descriptor)
            except OSError as rollback_error:
                raise ExtractionError(
                    "écriture atomique échouée et état de sortie indéterminé : "
                    f"publication={publication_error}; rollback={rollback_error}"
                ) from rollback_error
            raise ExtractionError(
                f"écriture atomique annulée avant commit : {publication_error}"
            ) from publication_error

        # Commit point: the rename of the fully synced 0644 file and the
        # directory entry are durable. Cleanup errors cannot invalidate output.
        if backup_exists:
            try:
                os.unlink(backup_name, dir_fd=directory_descriptor)
                backup_exists = False
                _fsync_directory(directory_descriptor)
            except OSError:
                pass
    except ExtractionError:
        raise
    except OSError as exc:
        raise ExtractionError(f"écriture atomique impossible : {output}: {exc}") from exc
    finally:
        if temporary_exists:
            try:
                os.unlink(temporary_name, dir_fd=directory_descriptor)
            except OSError:
                pass
        if backup_exists and not published:
            try:
                os.replace(
                    backup_name,
                    output.name,
                    src_dir_fd=directory_descriptor,
                    dst_dir_fd=directory_descriptor,
                )
            except OSError:
                pass


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=ROOT / "sources" / "BO2026_1SPE_specialite.pdf",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "sources" / "txt" / "BO2026_1SPE_specialite.txt",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=ROOT / "sources" / "registry.yaml",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source: OpenSource | None = None
    output_directory_descriptor = -1
    try:
        entry = load_source_entry(lexical_absolute(args.registry))
        source = open_registered_source(lexical_absolute(args.source), entry)
        output, output_directory_descriptor = open_output_directory(args.output)
        check_output_alias(output, output_directory_descriptor, source)
        executable = resolve_pdftotext()
        with tempfile.TemporaryDirectory(prefix="nexus-bo2026-") as raw_directory:
            snapshot = snapshot_source(source, Path(raw_directory))
            content = run_pdftotext(executable, snapshot)
        atomic_write(output, output_directory_descriptor, content, source)
    except ExtractionError as exc:
        print(f"ERREUR : {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERREUR : opération système refusée : {exc}", file=sys.stderr)
        return 2
    finally:
        if output_directory_descriptor >= 0:
            os.close(output_directory_descriptor)
        if source is not None:
            os.close(source.descriptor)
    print(f"{output} {hashlib.sha256(content).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
