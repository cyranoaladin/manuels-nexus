#!/usr/bin/env python3
"""Surface de sources publiee d'un manuel, lue sur l'assembleur canonique.

Aucun gate ne doit reconstruire sa propre idee de « ce qui est publie ». La
seule autorite est `Mathematiques/manuel-maths/scripts/assemble_manuel.py` :
c'est lui qui choisit, pour chaque variante, les fichiers qui entrent dans le
maitre LaTeX. Ce module se contente de l'interroger et d'exposer la META de
chaque objet, sans jamais coder en dur ni un chapitre, ni un identifiant, ni
un chemin d'objet.
"""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
MATH = ROOT / "Mathematiques" / "manuel-maths"
CHAPTERS = MATH / "chapitres"
VARIANTS = ("eleve", "professeur")


@lru_cache(maxsize=1)
def assembler() -> Any:
    """Return the canonical assembler module."""

    path = str(MATH / "scripts")
    if path not in sys.path:
        sys.path.insert(0, path)
    import assemble_manuel  # noqa: PLC0415

    return assemble_manuel


def manual_chapters(manual: str) -> list[str]:
    """Chapters of `manual`, read from the assembler's own routing table."""

    return list(assembler().MANUAL_CHAPTERS[manual])


def level_label(manual: str) -> str:
    return assembler().MANUAL_LEVEL_LABELS[manual]


def foreign_level_labels(manual: str) -> list[str]:
    """Level labels of every OTHER manual assembled from the same tree."""

    labels = assembler().MANUAL_LEVEL_LABELS
    own = labels[manual]
    return sorted({value for key, value in labels.items() if labels[key] != own})


def published_sources(manual: str, variant: str) -> list[Path]:
    """Files the assembler puts in `manual`'s `variant` master, in build order."""

    if variant not in VARIANTS:
        raise ValueError(f"variante inconnue: {variant}")
    files: list[Path] = []
    for chapter in manual_chapters(manual):
        files.extend(assembler().collect_chapter(CHAPTERS / chapter, variant))
    return files


def published_union(manual: str) -> list[Path]:
    """Every file published by at least one variant of `manual`."""

    seen: dict[Path, None] = {}
    for variant in VARIANTS:
        for path in published_sources(manual, variant):
            seen.setdefault(path, None)
    return sorted(seen)


def object_meta(text: str) -> dict[str, Any]:
    """Parse the single `% META:` header line an object must carry."""

    for line in text.split("\n")[:10]:
        if line.startswith("% META:"):
            try:
                payload = json.loads(line.removeprefix("% META:").strip())
            except json.JSONDecodeError:
                return {}
            return payload if isinstance(payload, dict) else {}
    return {}


def read_meta(path: Path) -> dict[str, Any]:
    return object_meta(path.read_text(encoding="utf-8"))


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def comment_mask(text: str) -> list[bool]:
    """True where a character is inside a TeX line comment (unescaped `%`)."""

    mask = [False] * len(text)
    commented = False
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\n":
            commented = False
            index += 1
            continue
        if commented:
            mask[index] = True
            index += 1
            continue
        if char == "\\" and index + 1 < len(text):
            index += 2
            continue
        if char == "%":
            commented = True
            mask[index] = True
        index += 1
    return mask


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def sha256_of(paths: Iterable[Path]) -> str:
    import hashlib

    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(relative(path).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"
