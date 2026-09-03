#!/usr/bin/env python3
"""Les paquets de relecture humaine 1SPE : vingt attendus, vingt présents.

Un paquet manquant est une relecture qui n'aura pas lieu. Le défaut n'est pas
visible : le dossier existe, les autres paquets sont là, et rien ne dit qu'il
en manque seize -- sauf à compter ce qui est ATTENDU avant de compter ce qui
est présent.

Ce que le contrôle attend n'est écrit nulle part ici : les chapitres sont lus
sur l'assembleur, les deux rôles de relecture sur le gabarit d'instructions que
le dépôt donne aux relecteurs. Ajouter un onzième chapitre fait donc monter
l'attendu tout seul.

Un paquet ne compte que s'il est utilisable : il doit nommer son chapitre, son
rôle, l'ensemble d'objets qu'il couvre, et porter la vue humaine qui va avec --
un JSON de quarante kilo-octets n'est pas une relecture.

Métriques bloquantes : `HUMAN_PACKETS_MISSING`, `HUMAN_READING_VIEWS_MISSING`,
`PACKETS_WITHOUT_REQUIRED_FIELDS`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT, manual_chapters  # noqa: E402

def _label(path: Path) -> str:
    """Chemin lisible, y compris pour un paquet fabriqué hors du dépôt."""

    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


JSON_TARGET = ROOT / "audit/1SPE_HUMAN_PACKET_COMPLETENESS.json"
MD_TARGET = ROOT / "audit/1SPE_HUMAN_PACKET_COMPLETENESS.md"
GENERATED_BY = "scripts/build_1spe_human_packet_completeness.py"

MANUAL = "1SPE"
REVIEWS = ROOT / "audit/reviews/human"
INSTRUCTIONS = REVIEWS / "ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md"

# Ce qu'un paquet doit porter pour qu'un humain puisse s'en servir : de quoi
# il parle, qui le relit, ce qu'il couvre exactement, ce qu'on lui demande de
# contrôler, et quels verdicts il a le droit de rendre.
REQUIRED_FIELDS = (
    "chapter_id",
    "review_role",
    "objects",
    "object_set_digest",
    "minimum_controls",
    "permitted_verdicts",
)


class PacketError(RuntimeError):
    """Une preuve manque : la complétude ne peut pas être établie."""


def reviewer_roles() -> list[str]:
    """Les rôles de relecture, lus sur les instructions données aux relecteurs."""

    if not INSTRUCTIONS.is_file():
        raise PacketError(f"instructions de relecture absentes : {INSTRUCTIONS}")
    text = INSTRUCTIONS.read_text(encoding="utf-8")
    roles = sorted(set(re.findall(r"\b([AB])-([A-Z_]{4,})\b", text)))
    if not roles:
        raise PacketError("les instructions ne nomment aucun rôle de relecture")
    return [f"{letter}-{name}" for letter, name in roles]


def inspect(chapter: str, role: str) -> dict[str, Any]:
    directory = REVIEWS / chapter
    packet = directory / f"packet-{role}.json"
    view = directory / f"view-{role}.md"
    row: dict[str, Any] = {
        "chapter": chapter,
        "role": role,
        "packet": _label(packet),
        "packet_present": packet.is_file(),
        "view": _label(view),
        "view_present": view.is_file(),
        "missing_fields": [],
        "objects": 0,
        "render_evidence": None,
    }
    if not packet.is_file():
        row["missing_fields"] = list(REQUIRED_FIELDS)
        return row
    try:
        content = json.loads(packet.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        row["missing_fields"] = list(REQUIRED_FIELDS)
        row["unreadable"] = str(error)
        return row
    row["missing_fields"] = [
        field for field in REQUIRED_FIELDS if not content.get(field)
    ]
    objects = content.get("objects")
    row["objects"] = len(objects) if isinstance(objects, list) else 0
    row["render_evidence"] = content.get("render_evidence")
    if row["objects"] == 0 and "objects" not in row["missing_fields"]:
        row["missing_fields"].append("objects")
    return row


def build() -> dict[str, Any]:
    chapters = manual_chapters(MANUAL)
    if not chapters:
        raise PacketError(f"l'assembleur ne déclare aucun chapitre pour {MANUAL}")
    roles = reviewer_roles()
    rows = [inspect(chapter, role) for chapter in chapters for role in roles]

    expected = len(rows)
    packets_present = sum(1 for row in rows if row["packet_present"])
    views_present = sum(1 for row in rows if row["view_present"])
    incomplete = [row for row in rows if row["missing_fields"]]
    without_render = [row for row in rows if row["render_evidence"] != "PRESENT"]
    return {
        "artifact_type": "1spe_human_packet_completeness",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "what_is_expected_is_read_not_written": {
            "chapters": "l'assembleur canonique",
            "reviewer_roles": _label(INSTRUCTIONS),
        },
        "a_packet_without_a_reading_view_is_not_a_review": (
            "Un JSON de quarante kilo-octets n'est pas une relecture : chaque "
            "paquet doit porter la vue lisible qui va avec."
        ),
        "rendered_evidence_is_reported_not_required_here": (
            "Les paquets ne portent pas les pages rendues : le relecteur lit "
            "les sources et la vue. Le compte est publié parce qu'il compte, "
            "mais l'ajouter maintenant changerait le condensat de chaque "
            "paquet et romprait le gel de relecture -- ce serait une décision "
            "de gouvernance, pas une correction."
        ),
        "required_fields": list(REQUIRED_FIELDS),
        "chapters": chapters,
        "reviewer_roles": roles,
        "packets": rows,
        "summary": {
            "HUMAN_PACKETS_EXPECTED": expected,
            "HUMAN_PACKETS_PRESENT": packets_present,
            "HUMAN_PACKETS_MISSING": expected - packets_present,
            "HUMAN_READING_VIEWS_EXPECTED": expected,
            "HUMAN_READING_VIEWS_PRESENT": views_present,
            "HUMAN_READING_VIEWS_MISSING": expected - views_present,
            "PACKETS_WITHOUT_REQUIRED_FIELDS": len(incomplete),
            "OBJECTS_OFFERED_FOR_REVIEW": sum(row["objects"] for row in rows),
            "PACKETS_WITHOUT_RENDERED_EVIDENCE": len(without_render),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Paquets de relecture humaine — 1SPE",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"> {payload['a_packet_without_a_reading_view_is_not_a_review']}",
        "",
        "L'attendu est lu, jamais écrit : chapitres sur "
        f"`{payload['what_is_expected_is_read_not_written']['chapters']}`, rôles sur "
        f"`{payload['what_is_expected_is_read_not_written']['reviewer_roles']}`.",
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    lines += [
        "",
        "## Paquets",
        "",
        "| Chapitre | Rôle | Paquet | Vue | Objets | Champs manquants |",
        "|---|---|---|---|---:|---|",
    ]
    for row in payload["packets"]:
        lines.append(
            f"| {row['chapter']} | {row['role']} | "
            f"{'oui' if row['packet_present'] else '**NON**'} | "
            f"{'oui' if row['view_present'] else '**NON**'} | {row['objects']} | "
            f"{', '.join(row['missing_fields']) or '—'} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build()
    except PacketError as error:
        print(f"1SPE-HUMAN-PACKET-COMPLETENESS-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {JSON_TARGET.name} et {MD_TARGET.name}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    summary = payload["summary"]
    return (
        1
        if summary["HUMAN_PACKETS_MISSING"]
        or summary["HUMAN_READING_VIEWS_MISSING"]
        or summary["PACKETS_WITHOUT_REQUIRED_FIELDS"]
        else 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
