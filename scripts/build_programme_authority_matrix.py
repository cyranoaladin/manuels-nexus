#!/usr/bin/env python3
"""Choisir le programme par l'annee scolaire, jamais par la date de publication.

Un programme publie en 2026 n'est pas forcement le programme de 2026-2027. Le
nouveau texte de Terminale specialite parait en 2026 et n'entre en vigueur
qu'en 2027-2028 ; l'appliquer au manuel courant reviendrait a enseigner un
programme qui n'existe pas encore pour ces eleves. La faute symetrique existe
aussi : ramener la Premiere au texte de 2019 alors que le nouveau programme
s'applique des cette rentree.

Le choix ne se fait donc ni sur le nom du fichier, ni sur « la derniere version
publiee », ni sur une intuition de recence. Il se fait sur une seule question :
l'annee scolaire de la release tombe-t-elle dans l'intervalle d'application de
cette autorite.

Un successeur connu mais pas encore en vigueur n'est pas ignore -- il est
enregistre `FUTURE_NOT_APPLICABLE`, avec sa date d'entree. Le taire laisserait
croire qu'on ne l'a pas vu.

Metriques bloquantes : `WRONG_YEAR_AUTHORITY`, `AMBIGUOUS_AUTHORITY`,
`MANUAL_WITHOUT_AUTHORITY`, `AUTHORITY_SOURCE_DIGEST_MISMATCH`, `UNKNOWN`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT  # noqa: E402

JSON_TARGET = ROOT / "audit/PROGRAMME_AUTHORITY_MATRIX.json"
MD_TARGET = ROOT / "audit/PROGRAMME_AUTHORITY_MATRIX.md"
GENERATED_BY = "scripts/build_programme_authority_matrix.py"

REGISTRY = ROOT / "audit/OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml"

#: L'annee scolaire de la release. Tout le choix d'autorite en depend.
RELEASE_SCHOOL_YEAR = "2026-2027"

#: Niveau et discipline de chaque manuel canonique. Ce sont des faits
#: d'edition, pas des deductions : un manuel de Premiere specialite ne se
#: devine pas depuis un identifiant.
MANUAL_IDENTITY = {
    "1SPE": ("premiere", "mathematiques"),
    "TSPE_2026_2027": ("terminale", "mathematiques"),
    "TCOMPL": ("terminale", "mathematiques complementaires"),
    "TEXPERTES": ("terminale", "mathematiques expertes"),
    "1NSI": ("premiere", "numerique et sciences informatiques"),
    "TNSI": ("terminale", "numerique et sciences informatiques"),
}

#: Les successeurs publies mais pas encore applicables. Les nommer est ce qui
#: rend l'erreur impossible : sans eux, rien ne dirait qu'un texte plus recent
#: existe et qu'il ne s'applique pas encore.
KNOWN_SUCCESSORS = {
    "TSPE_2026_2027": {
        "successor_NOR": "MENE2602919A",
        "successor_effective_from": "2027-2028",
        "status": "FUTURE_NOT_APPLICABLE",
        "why": (
            "publie en 2026, il entre en vigueur a la rentree 2027-2028 ; "
            "l'appliquer a la release 2026-2027 enseignerait un programme qui "
            "n'existe pas encore pour ces eleves"
        ),
    },
    "TCOMPL": {
        "successor_NOR": None,
        "successor_effective_from": "2027-2028",
        "status": "FUTURE_NOT_APPLICABLE",
        "why": (
            "un successeur 2026 est connu pour l'enseignement optionnel de "
            "terminale ; il n'entre pas en vigueur pour 2026-2027. Son NOR "
            "n'est pas archive dans le depot : il n'est donc pas invente ici"
        ),
    },
}


class AuthorityError(RuntimeError):
    """Une preuve manque : la matrice ne peut pas etre etablie."""


def year_start(school_year: str) -> int:
    return int(school_year.split("-")[0])


def applies_to(entry: dict[str, Any], school_year: str) -> bool:
    """L'annee scolaire tombe-t-elle dans l'intervalle d'application ?

    C'est la seule question. Ni le nom du fichier, ni la date de publication,
    ni la recence n'entrent dans la reponse.
    """

    start = entry.get("effective_from")
    end = entry.get("effective_until")
    if not start:
        return False
    if year_start(school_year) < year_start(start):
        return False
    if end and year_start(school_year) > year_start(end):
        return False
    return True


def registry() -> dict[str, Any]:
    if not REGISTRY.is_file():
        raise AuthorityError(f"registre d'autorite absent : {REGISTRY}")
    return yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))[
        "programme_d_enseignement"
    ]


def build() -> dict[str, Any]:
    declared = registry()

    rows: list[dict[str, Any]] = []
    wrong_year: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    without: list[str] = []
    digest_mismatch: list[dict[str, Any]] = []

    for manual, (level, subject) in sorted(MANUAL_IDENTITY.items()):
        entry = declared.get(manual)
        if entry is None:
            without.append(manual)
            continue

        applicable = applies_to(entry, RELEASE_SCHOOL_YEAR)
        if not applicable:
            wrong_year.append(
                {
                    "manual_id": manual,
                    "official_NOR": entry.get("official_ref"),
                    "effective_from": entry.get("effective_from"),
                    "effective_until": entry.get("effective_until"),
                    "why": (
                        f"l'annee {RELEASE_SCHOOL_YEAR} ne tombe pas dans "
                        "l'intervalle d'application"
                    ),
                }
            )

        # Le registre declare aussi son propre verdict d'applicabilite ; s'il
        # contredit le calcul par intervalle, l'autorite est ambigue et rien
        # ne permet de trancher sans decision.
        if bool(entry.get("applicable_2026_2027")) != applicable:
            ambiguous.append(
                {
                    "manual_id": manual,
                    "declared_applicable": entry.get("applicable_2026_2027"),
                    "computed_applicable": applicable,
                }
            )

        source = ROOT / entry["local_archival_file"]
        recorded = entry.get("local_archival_digest")
        if not source.is_file():
            digest_mismatch.append(
                {"manual_id": manual, "why": "source officielle absente"}
            )
        else:
            actual = "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()
            if actual != recorded:
                digest_mismatch.append(
                    {
                        "manual_id": manual,
                        "recorded": recorded,
                        "actual": actual,
                        "why": "la source officielle archivee a change",
                    }
                )

        successor = KNOWN_SUCCESSORS.get(manual, {})
        rows.append(
            {
                "manual_id": manual,
                "school_year": RELEASE_SCHOOL_YEAR,
                "level": level,
                "subject": subject,
                "official_NOR": entry.get("official_ref"),
                "official_publication_date": entry.get("bo_date"),
                "official_decree_date": entry.get("arrete_date"),
                "effective_from": entry.get("effective_from"),
                "effective_until_if_known": entry.get("effective_until"),
                "official_source": entry["local_archival_file"],
                "official_source_sha256": recorded,
                "official_url": entry.get("authority_url"),
                "selected_because": (
                    f"{RELEASE_SCHOOL_YEAR} tombe dans "
                    f"[{entry.get('effective_from')} ; "
                    f"{entry.get('effective_until') or 'sans terme connu'}]"
                ),
                "successor_NOR_if_known": successor.get("successor_NOR"),
                "successor_effective_from": successor.get("successor_effective_from"),
                "successor_status": successor.get("status"),
                "successor_why_not_applied": successor.get("why"),
            }
        )

    return {
        "artifact_type": "programme_authority_matrix",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "release_school_year": RELEASE_SCHOOL_YEAR,
        "the_year_decides_not_the_publication_date": (
            "Un programme publie en 2026 n'est pas forcement le programme de "
            "2026-2027. Le choix se fait sur une seule question : l'annee "
            "scolaire tombe-t-elle dans l'intervalle d'application. Ni le nom "
            "du fichier, ni « la derniere version publiee » n'y entrent."
        ),
        "a_known_successor_is_named_not_hidden": (
            "Un texte plus recent mais pas encore en vigueur est enregistre "
            "FUTURE_NOT_APPLICABLE avec sa date d'entree. Le taire laisserait "
            "croire qu'on ne l'a pas vu."
        ),
        "authorities": rows,
        "wrong_year_authorities": wrong_year,
        "ambiguous_authorities": ambiguous,
        "manuals_without_authority": without,
        "authority_source_digest_mismatch": digest_mismatch,
        "summary": {
            "MANUALS": len(MANUAL_IDENTITY),
            "AUTHORITIES_RESOLVED": len(rows),
            "KNOWN_FUTURE_SUCCESSORS": len(KNOWN_SUCCESSORS),
            "WRONG_YEAR_AUTHORITY": len(wrong_year),
            "AMBIGUOUS_AUTHORITY": len(ambiguous),
            "MANUAL_WITHOUT_AUTHORITY": len(without),
            "AUTHORITY_SOURCE_DIGEST_MISMATCH": len(digest_mismatch),
            "UNKNOWN": 0,
        },
    }


BLOCKING = (
    "WRONG_YEAR_AUTHORITY",
    "AMBIGUOUS_AUTHORITY",
    "MANUAL_WITHOUT_AUTHORITY",
    "AUTHORITY_SOURCE_DIGEST_MISMATCH",
    "UNKNOWN",
)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Matrice d'autorité programme — " + payload["release_school_year"],
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"> {payload['the_year_decides_not_the_publication_date']}",
        "",
        f"> {payload['a_known_successor_is_named_not_hidden']}",
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
        "## Autorité retenue par manuel",
        "",
        "| Manuel | Niveau | Discipline | NOR | BO | Application | Successeur connu |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in payload["authorities"]:
        successor = (
            f"`{row['successor_NOR_if_known'] or 'NOR non archivé'}` "
            f"→ {row['successor_effective_from']} "
            f"({row['successor_status']})"
            if row["successor_status"]
            else "—"
        )
        lines.append(
            f"| `{row['manual_id']}` | {row['level']} | {row['subject']} | "
            f"`{row['official_NOR']}` | {row['official_publication_date']} | "
            f"{row['effective_from']} → "
            f"{row['effective_until_if_known'] or 'sans terme'} | {successor} |"
        )
    for row in payload["authorities"]:
        if row["successor_why_not_applied"]:
            lines += [
                "",
                f"**`{row['manual_id']}`** — {row['successor_why_not_applied']}.",
            ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien ecrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build()
    except AuthorityError as error:
        print(f"AUTHORITY-MATRIX-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"ecrit {JSON_TARGET.name} et {MD_TARGET.name}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    return 1 if any(payload["summary"][name] for name in BLOCKING) else 0


if __name__ == "__main__":
    raise SystemExit(main())
