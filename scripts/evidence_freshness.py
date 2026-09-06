#!/usr/bin/env python3
"""Enveloppe de fraîcheur commune aux artefacts d'audit.

Un artefact peut rester valable après un changement de HEAD : ce qui compte
n'est pas le commit, ce sont les octets que le producteur a réellement lus. À
l'inverse, un artefact régénéré sur un HEAD ancien ne devient pas courant parce
qu'on l'affirme.

Quatre champs, et une seule façon de les interpréter :

    EVIDENCE_HEAD         le HEAD au moment du calcul, pour la traçabilité
    INPUT_DIGEST          empreinte des entrées telles qu'elles étaient alors
    CURRENT_INPUT_DIGEST  empreinte des mêmes entrées maintenant
    FRESHNESS_STATUS      CURRENT_BY_INPUT_DIGEST, STALE_INPUTS_CHANGED,
                          ou UNVERIFIABLE_NO_DECLARED_INPUTS

`CURRENT_BY_INPUT_DIGEST` est la seule valeur qui autorise à présenter
l'artefact comme l'état courant, et elle ne se déclare pas : elle se recalcule.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]

CURRENT = "CURRENT_BY_INPUT_DIGEST"
STALE = "STALE_INPUTS_CHANGED"
UNVERIFIABLE = "UNVERIFIABLE_NO_DECLARED_INPUTS"


def head_sha(root: Path = ROOT) -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def digest_paths(paths: Iterable[str], root: Path = ROOT) -> str:
    """Empreinte ordonnée d'un ensemble de chemins déclarés."""
    accumulator = hashlib.sha256()
    for relative in sorted(set(paths)):
        accumulator.update(relative.encode("utf-8"))
        accumulator.update(b"\x00")
        candidate = root / relative
        if candidate.is_file():
            accumulator.update(hashlib.sha256(candidate.read_bytes()).digest())
        else:
            accumulator.update(b"ABSENT")
        accumulator.update(b"\x00")
    return "sha256:" + accumulator.hexdigest()


def stamp(input_paths: Iterable[str], root: Path = ROOT) -> dict[str, Any]:
    """Enveloppe à inscrire dans un artefact au moment de sa production."""
    paths = sorted(set(input_paths))
    return {
        "EVIDENCE_HEAD": head_sha(root),
        "INPUT_PATHS": paths,
        "INPUT_DIGEST": digest_paths(paths, root),
    }


def assess(envelope: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    """Fraîcheur d'un artefact déjà produit, recalculée sur le dépôt courant.

    Un producteur qui lit le dépôt entier ne peut pas être déclaré courant sur
    la seule stabilité de ses fichiers d'entrée : sa mesure décrit un état du
    dépôt, et tout commit peut l'avoir déplacée. Pour ceux-là, la fraîcheur se
    juge sur le HEAD d'observation.
    """
    if envelope.get("WHOLE_REPOSITORY_INPUT"):
        observed = set(envelope.get("OBSERVATION_HEADS") or [])
        current = head_sha(root)
        return {
            "EVIDENCE_HEAD": envelope.get("EVIDENCE_HEAD"),
            "CURRENT_HEAD": current,
            "OBSERVATION_HEADS": sorted(observed),
            "INPUT_DIGEST": envelope.get("INPUT_DIGEST"),
            "CURRENT_INPUT_DIGEST": digest_paths(
                envelope.get("INPUT_PATHS") or [], root
            ),
            "FRESHNESS_STATUS": (
                CURRENT if observed == {current} and current
                else STALE if observed
                else UNVERIFIABLE
            ),
        }
    paths = envelope.get("INPUT_PATHS") or []
    if not paths:
        return {
            "EVIDENCE_HEAD": envelope.get("EVIDENCE_HEAD"),
            "INPUT_DIGEST": envelope.get("INPUT_DIGEST"),
            "CURRENT_INPUT_DIGEST": None,
            "FRESHNESS_STATUS": UNVERIFIABLE,
        }
    current = digest_paths(paths, root)
    return {
        "EVIDENCE_HEAD": envelope.get("EVIDENCE_HEAD"),
        "CURRENT_HEAD": head_sha(root),
        "INPUT_DIGEST": envelope.get("INPUT_DIGEST"),
        "CURRENT_INPUT_DIGEST": current,
        "FRESHNESS_STATUS": (
            CURRENT if current == envelope.get("INPUT_DIGEST") else STALE
        ),
    }


def assess_artifact(path: Path, root: Path = ROOT) -> dict[str, Any]:
    payload = json.loads((root / path).read_text(encoding="utf-8"))
    return assess(payload.get("freshness") or {}, root)
