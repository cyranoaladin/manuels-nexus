"""Un manuel n'imprime pas deux fois le meme cours.

Le commit 533d1919, qui portait sur le mode d'emploi et la charte v6, a
depose 44 objets `cours` numerotes dans huit chapitres de Premiere NSI. Aucun
ne portait de contenu neuf : chacun recopiait le corps d'un objet deja
present -- un `COURS-C<n>` canonique, ou meme un TD. Et tous etaient
assembles, donc imprimes.

Deux consequences, pas une :

* le manuel imprimait le meme cours deux fois ;
* certains de ces doublons declaraient une capacite qui n'etait pas celle de
  leur corps. `1NSI-TC-COURS-01` declarait C1 alors que son corps est le TD
  « station meteo » ; `1NSI-TC-COURS-03` declarait C3 alors que son corps est
  le cours C1. C'est un faux credit de capacite, pas une simple redondance.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "NSI/chapitres"


def _body_digest(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    body = text.split("\n", 1)[1] if "\n" in text else ""
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _premiere_chapters() -> list[Path]:
    return sorted(p for p in CHAPTERS.iterdir() if p.name.startswith("1NSI-"))


def test_no_premiere_nsi_chapter_publishes_the_same_course_twice() -> None:
    """Portee : les COURS. La dette des corriges clones est distincte.

    188 des 312 corriges de Premiere NSI sont encore des clones -- six
    chapitres batissent 25 a 51 corriges sur SEPT corps distincts. C'est un
    travail d'ecriture, pas de deduplication : chaque exercice a besoin du
    corrige qui lui repond. Cette dette est suivie par le registre de clones ;
    la confondre avec celle des cours ferait passer une reecriture necessaire
    pour une suppression de doublon.
    """
    duplicates: dict[str, list[str]] = {}
    for chapter in _premiere_chapters():
        course_dir = chapter / "cours"
        if not course_dir.is_dir():
            continue
        by_digest: dict[str, list[str]] = defaultdict(list)
        for path in sorted(course_dir.glob("*.tex")):
            by_digest[_body_digest(path)].append(path.name)
        for digest, names in by_digest.items():
            if len(names) > 1:
                duplicates[f"{chapter.name}:{digest[:12]}"] = sorted(names)
    assert duplicates == {}, f"cours publies en double : {duplicates}"


def test_no_premiere_nsi_course_duplicates_a_non_course_object() -> None:
    """Un cours ne peut pas etre la copie d'un TD ou d'un exercice.

    `1NSI-TC-COURS-01` declarait la capacite C1 alors que son corps etait le
    TD « station meteo ». C'est un faux credit de capacite, la forme la plus
    couteuse du clonage : elle fait croire qu'une capacite est enseignee.
    """
    borrowed: dict[str, str] = {}
    for chapter in _premiere_chapters():
        course_dir = chapter / "cours"
        if not course_dir.is_dir():
            continue
        courses = {
            path.name: _body_digest(path)
            for path in sorted(course_dir.glob("*COURS*.tex"))
        }
        others = {
            _body_digest(path): path.name
            for path in sorted(chapter.rglob("*.tex"))
            if path.parent.name != "validations" and "COURS" not in path.name
        }
        for name, digest in courses.items():
            if digest in others:
                borrowed[f"{chapter.name}/{name}"] = others[digest]
    assert borrowed == {}, f"cours copiant un objet non-cours : {borrowed}"


