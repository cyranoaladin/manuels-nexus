#!/usr/bin/env python3
"""Dérivation du référentiel 1SPE depuis le texte officiel 2026.

Autorité curriculaire de l'édition 1SPE 2026-2027, tranchée par le Release
Owner : `MENE2602917A`, BO n°14 du 2 avril 2026, applicable à la rentrée
2026-2027.

La chaîne de dérivation est unique et vérifiable :

    sources/txt/BO2026_1SPE_specialite.txt   (texte officiel déposé, sha256 au
                                              registre sources/SOURCES.md)
      -> segments officiels (Contenus, Capacités attendues, Démonstration)
      -> référentiel de chapitre
      -> mapping du contrat de chapitre
      -> contenu pédagogique

Rien n'est dérivé de l'ancien référentiel 2019, d'un résumé, d'une matrice
d'audit ni du texte d'un manuel. Le producteur extrait les libellés **mot pour
mot** du bulletin et enregistre l'empreinte de sa source : un libellé retouché
sans mise à jour de l'empreinte devient détectable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Mathematiques/manuel-maths/sources/txt/BO2026_1SPE_specialite.txt"
REFERENTIAL_DIR = ROOT / "Mathematiques/manuel-maths/referentiel"

OFFICIAL_NOR = "MENE2602917A"
OFFICIAL_BULLETIN = "BO n°14 du 2 avril 2026"
EFFECTIVE_SCHOOL_YEAR = "2026-2027"

#: Rubriques du bulletin, et le fichier de référentiel qui les porte.
SECTIONS = {
    "Équations, fonctions polynômes du second degré": "capacites_1SPE_SECOND_DEGRE.json",
}

#: Les intitulés qui structurent une rubrique du bulletin.
BLOCK_TITLES = (
    "Contenus",
    "Capacités attendues",
    "Démonstration",
    "Démonstrations",
    "Approfondissements possibles",
    "Exemples d’algorithme",
    "Exemples d'algorithme",
)


def _normalise(text: str) -> str:
    """Espaces insécables et césures de PDF ramenés à une forme stable."""
    text = text.replace(" ", " ").replace("’", "’")
    return re.sub(r"[ \t]+", " ", text).strip()


def section_bounds(lines: list[str], title: str) -> tuple[int, int]:
    """Bornes de la rubrique : de son titre jusqu'au titre de premier niveau suivant."""
    starts = [i for i, line in enumerate(lines) if _normalise(line) == title]
    if not starts:
        raise SystemExit(f"rubrique introuvable dans la source officielle : {title!r}")
    start = starts[-1]  # la table des matières précède le corps
    for index in range(start + 1, len(lines)):
        stripped = lines[index].rstrip()
        if not stripped:
            continue
        # Un titre de rubrique frère n'est pas indenté et n'est pas une puce.
        if (
            stripped == stripped.lstrip()
            and not stripped.startswith(("−", "-", "•"))
            and _normalise(stripped) not in BLOCK_TITLES
            and len(_normalise(stripped)) < 80
            and index > start + 3
        ):
            return start, index
    return start, len(lines)


def parse_blocks(lines: list[str]) -> dict[str, list[str]]:
    """Puces officielles regroupées par intitulé de bloc."""
    blocks: dict[str, list[str]] = {}
    current: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        if current and buffer:
            joined = _normalise(" ".join(buffer))
            if joined:
                blocks.setdefault(current, []).append(joined)

    for raw in lines:
        line = _normalise(raw)
        if line in BLOCK_TITLES:
            flush()
            buffer = []
            current = line
            continue
        if not line:
            continue
        if line.startswith(("−", "-", "•")):
            flush()
            buffer = [line.lstrip("−-• ").strip()]
        elif buffer:
            buffer.append(line)
    flush()
    return blocks


def derive_section(title: str) -> dict[str, Any]:
    raw = SOURCE.read_text(encoding="utf-8")
    lines = raw.splitlines()
    start, end = section_bounds(lines, title)
    blocks = parse_blocks(lines[start:end])

    expectations = blocks.get("Capacités attendues", [])
    if not expectations:
        raise SystemExit(f"aucune capacité attendue extraite pour {title!r}")
    demonstrations = blocks.get("Démonstration", []) + blocks.get("Démonstrations", [])

    slug = "1SPE-SECOND-DEGRE"
    capacities = []
    for index, wording in enumerate(expectations, start=1):
        capacities.append({
            "id": f"{slug}-2026-C{index}",
            "libelle_bo": wording,
            "contenu_bo": blocks.get("Contenus", []),
            "demonstration_exigible": False,
            "source_anchor": f"{title} / Capacités attendues / puce {index}",
            "source_digest": "sha256:" + hashlib.sha256(wording.encode("utf-8")).hexdigest(),
        })
    for index, wording in enumerate(demonstrations, start=1):
        capacities.append({
            "id": f"{slug}-2026-D{index}",
            "libelle_bo": wording,
            "contenu_bo": blocks.get("Contenus", []),
            "demonstration_exigible": True,
            "source_anchor": f"{title} / Démonstration / puce {index}",
            "source_digest": "sha256:" + hashlib.sha256(wording.encode("utf-8")).hexdigest(),
        })

    return {
        "niveau": "1SPE",
        "theme": "SECOND-DEGRE",
        "bo_reference": (
            f"Programme d'enseignement de spécialité de mathématiques de la classe de "
            f"première de la voie générale, {OFFICIAL_BULLETIN}, arrêté {OFFICIAL_NOR}, "
            f"algèbre : {title} (application à la rentrée {EFFECTIVE_SCHOOL_YEAR})."
        ),
        "authority": {
            "nor": OFFICIAL_NOR,
            "bulletin": OFFICIAL_BULLETIN,
            "effective_school_year": EFFECTIVE_SCHOOL_YEAR,
            "source_path": str(SOURCE.relative_to(ROOT)),
            "source_digest": "sha256:" + hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "derived_by": "scripts/derive_1spe_referential_2026.py",
        },
        "capacites": capacities,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="écrit le référentiel dérivé")
    args = parser.parse_args()

    for title, filename in SECTIONS.items():
        payload = derive_section(title)
        rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        if args.write:
            (REFERENTIAL_DIR / filename).write_text(rendered, encoding="utf-8")
            print(f"écrit : {filename}")
        else:
            print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
