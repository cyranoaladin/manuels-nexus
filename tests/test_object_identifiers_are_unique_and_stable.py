"""Un identifiant d'objet désigne un objet, et un seul.

Le registre ASTRA relève 218 identifiants retirés puis réattribués à un contenu
différent : `RETIRED_IDENTIFIERS_REUSED_FOR_DIFFERENT_CONTENT`. Un même
identifiant a donc désigné deux objets au fil des générations. C'est une
ambiguïté de traçabilité : une revue, un reçu ou une référence nommant cet
identifiant ne dit pas, à lui seul, de quelle génération il parle.

Ce test ne répare pas cet historique. Il garde l'invariant qui reste
vérifiable et qui doit le rester : dans les sources COURANTES, un identifiant
ne désigne qu'un objet, et le fichier qui le porte s'accorde avec lui.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CORPORA = ("Mathematiques/manuel-maths/chapitres", "NSI/chapitres")
META = re.compile(r"^% META:\s*(\{.*?\})\s*$", re.M)
#: Hors du corpus PUBLIE. `_harvest` porte des candidats de recuperation
#: qu'aucun assembleur ne compose ; la meme exclusion est appliquee par
#: scripts/audit_editorial_diacritics.py.
UNPUBLISHED = ("_harvest",)


def published(path: Path) -> bool:
    return not any(part in UNPUBLISHED for part in path.relative_to(ROOT).parts)


def objects() -> list[tuple[str, Path]]:
    found = []
    for corpus in CORPORA:
        for path in sorted((ROOT / corpus).rglob("*.tex")):
            if not published(path):
                continue
            match = META.search(path.read_text(encoding="utf-8", errors="replace"))
            if not match:
                continue
            try:
                meta = json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
            if meta.get("id"):
                found.append((meta["id"], path))
    return found


@pytest.fixture(scope="module")
def corpus() -> list[tuple[str, Path]]:
    found = objects()
    assert found, "aucun objet lu : le test ne prouverait rien"
    return found


def test_no_identifier_designates_two_current_objects(corpus) -> None:
    by_id: dict[str, list[str]] = defaultdict(list)
    for identifier, path in corpus:
        by_id[identifier].append(str(path.relative_to(ROOT)))
    duplicates = {k: v for k, v in by_id.items() if len(v) > 1}
    assert not duplicates, f"identifiants portés par plusieurs objets : {duplicates}"


def test_every_object_carries_an_identifier(corpus) -> None:
    """Un objet sans identifiant ne peut être ni revu, ni tracé, ni retiré."""
    total = sum(1 for corpus_dir in CORPORA
                for path in (ROOT / corpus_dir).rglob("*.tex") if published(path))
    assert len(corpus) == total, (
        f"{total - len(corpus)} fichier(s) .tex sans en-tête % META exploitable"
    )
