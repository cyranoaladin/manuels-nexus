#!/usr/bin/env python3
"""Extraire de manière déterministe le programme officiel 1SPE 2026."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = "SRC-BO2026-1SPE-MATHS"


class ExtractionError(RuntimeError):
    """Erreur contrôlée qui ne doit jamais remplacer une extraction valide."""


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


def validate_source(source: Path, entry: dict[str, Any]) -> str:
    registered = lexical_absolute(ROOT / str(entry.get("local_path", "")))
    candidate = lexical_absolute(source)
    if candidate != registered:
        raise ExtractionError(
            f"source refusée : {candidate} ; source enregistrée attendue : {registered}"
        )
    try:
        mode = candidate.stat().st_mode
    except OSError as exc:
        raise ExtractionError(f"source inaccessible : {candidate}: {exc}") from exc
    if not stat.S_ISREG(mode):
        raise ExtractionError(f"source non régulière : {candidate}")
    expected = entry.get("sha256")
    if not isinstance(expected, str) or len(expected) != 64:
        raise ExtractionError("SHA-256 attendu absent ou invalide dans le registre")
    actual = sha256(candidate)
    if actual != expected:
        raise ExtractionError(
            f"SHA-256 source incorrect : attendu {expected}, obtenu {actual}"
        )
    return actual


def validate_output(output: Path) -> Path:
    output = lexical_absolute(output)
    if output.exists() and output.is_dir():
        raise ExtractionError(f"sortie refusée : répertoire existant : {output}")
    if output.is_symlink():
        raise ExtractionError(f"sortie symbolique refusée : {output}")
    parent = output.parent
    for ancestor in (parent, *parent.parents):
        if ancestor.is_symlink():
            raise ExtractionError(
                f"parent symbolique de sortie refusé : {ancestor}"
            )
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ExtractionError(f"répertoire de sortie inaccessible : {parent}: {exc}") from exc
    if not parent.is_dir():
        raise ExtractionError(f"parent de sortie non régulier : {parent}")
    for ancestor in (parent, *parent.parents):
        if ancestor.is_symlink():
            raise ExtractionError(
                f"parent symbolique de sortie refusé : {ancestor}"
            )
    return output


def run_pdftotext(source: Path) -> bytes:
    executable = shutil.which("pdftotext")
    if executable is None:
        raise ExtractionError("binaire bloquant absent : pdftotext")
    try:
        result = subprocess.run(
            [str(Path(executable).absolute()), "-layout", os.fspath(source), "-"],
            cwd=source.parent,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
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
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def atomic_write(output: Path, content: bytes) -> None:
    descriptor = -1
    temporary: Path | None = None
    try:
        descriptor, raw_temporary = tempfile.mkstemp(
            prefix=f".{output.name}.",
            suffix=".tmp",
            dir=output.parent,
        )
        temporary = Path(raw_temporary)
        os.fchmod(descriptor, 0o644)
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            descriptor = -1
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if output.is_symlink():
            raise ExtractionError(f"sortie devenue symbolique : {output}")
        os.replace(temporary, output)
        temporary = None
        os.chmod(output, 0o644, follow_symlinks=False)
        directory_descriptor = os.open(output.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    except OSError as exc:
        raise ExtractionError(f"écriture atomique impossible : {output}: {exc}") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary is not None:
            temporary.unlink(missing_ok=True)


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
    try:
        entry = load_source_entry(lexical_absolute(args.registry))
        source = lexical_absolute(args.source)
        validate_source(source, entry)
        if lexical_absolute(args.output) == source:
            raise ExtractionError("la sortie ne peut pas remplacer la source")
        output = validate_output(args.output)
        content = run_pdftotext(source)
        atomic_write(output, content)
    except ExtractionError as exc:
        print(f"ERREUR : {exc}", file=sys.stderr)
        return 2
    print(f"{output} {hashlib.sha256(content).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
