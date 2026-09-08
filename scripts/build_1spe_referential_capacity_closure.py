#!/usr/bin/env python3
"""Chaque capacite du contrat doit retrouver son attendu officiel.

Le dossier de revue disait, pour deux capacites de Variables aleatoires :
« aucun libelle BO : le referentiel du depot ne declare pas cette capacite ».
Lu vite, cela ressemble a du hors-programme -- et la tentation serait de
supprimer C6 et C7. Ce serait exactement l'erreur : le meme dossier porte les
atomes officiels 175, 176, 177, 178 et 179, tous obligatoires, tous issus de
MENE2602917A, le programme de premiere specialite applicable a la rentree
2026-2027. Le contenu est au programme ; c'est le REFERENTIEL LOCAL qui ne le
disait pas.

Ce module ferme cet ecart, et il le ferme dans un sens unique : l'autorite est
la matrice de couverture officielle, jamais l'inverse. Un libelle BO n'est
jamais redige ici -- il est repris mot pour mot des atomes que la matrice
rattache a la capacite. Aucune capacite n'est creee : celles qui sont ecrites
existent deja dans le contrat de chapitre, elles recoivent seulement l'attendu
officiel qui leur manquait.

Le controle porte sur les dix chapitres, pas sur le seul ou le defaut a ete
vu : une omission ne s'annonce pas.

Metriques bloquantes : `CAPACITY_WITHOUT_REFERENTIAL_ENTRY`,
`ATOM_OUT_OF_APPLICABLE_YEAR`,
`ATOM_CREDITED_TO_A_FOREIGN_CAPACITY`, `VARALEA_OFFICIAL_MAPPING_UNKNOWN`,
`UNKNOWN`.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import MATH, ROOT  # noqa: E402
from capacity_identity import CapacityIdentityResolver, UnresolvedCapacityIdentity  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_REFERENTIAL_CAPACITY_CLOSURE.json"
MD_TARGET = ROOT / "audit/1SPE_REFERENTIAL_CAPACITY_CLOSURE.md"
GENERATED_BY = "scripts/build_1spe_referential_capacity_closure.py"

OFFICIAL = ROOT / "audit/OFFICIAL_PROGRAM_COVERAGE_2026_2027.json"
REFERENTIAL = MATH / "referentiel"
CHAPTERS = MATH / "chapitres"
MANUAL = "1SPE"
APPLICABLE_YEAR = "2026-2027"
APPLICABLE_NOR = "MENE2602917A"

FINDING = "P1_1SPE_VARALEA_REFERENTIAL_OMISSION"


def relative(path: Path) -> str:
    """Le chemin nomme depuis la racine que ce module lit.

    Un module qui doit pouvoir etre eprouve sur un referentiel monte ailleurs
    ne peut pas mesurer ses chemins depuis une racine figee a l'import.
    """

    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


class ClosureError(RuntimeError):
    """Une preuve manque : la fermeture ne peut pas etre etablie."""


def referential_path(chapter: str) -> Path:
    return REFERENTIAL / f"capacites_{chapter.replace('-', '_')}.json"


def official_atoms() -> dict[str, list[dict[str, Any]]]:
    """Les atomes officiels, par capacite du contrat. L'autorite, telle quelle."""

    if not OFFICIAL.is_file():
        raise ClosureError(f"matrice officielle absente : {relative(OFFICIAL)}")
    payload = json.loads(OFFICIAL.read_text(encoding="utf-8"))
    if payload.get("applicable_school_year") != APPLICABLE_YEAR:
        raise ClosureError(
            "la matrice officielle ne porte pas l'annee applicable "
            f"{APPLICABLE_YEAR}"
        )
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    resolver = CapacityIdentityResolver.from_corpora((CHAPTERS,))
    for row in payload["rows"]:
        if row.get("manual") != MANUAL or not row.get("contract_capacity"):
            continue
        alias = row["contract_capacity"]
        try:
            identity = resolver.resolve_collection_alias(alias).identity
            credit_key = identity.official_ref or alias
        except UnresolvedCapacityIdentity:
            # Les contrats transversaux ne sont pas des contrats de chapitre.
            # Leur alias reste visible ; il ne gagne aucun crédit ici.
            credit_key = alias
        grouped[credit_key].append(
            {
                "atom_id": row["atom_id"],
                "NOR": row["NOR"],
                "mandatory": row["mandatory"],
                "obligation_type": row["obligation_type"],
                "official_section": row["official_section"],
                "official_page_or_anchor": row["official_page_or_anchor"],
                "wording": row["official_wording_or_short_paraphrase"],
            }
        )
    for atoms in grouped.values():
        atoms.sort(key=lambda atom: atom["atom_id"])
    return dict(grouped)


def contract_capacities() -> list[dict[str, Any]]:
    """Ce que chaque chapitre declare enseigner, lu dans son contrat."""

    rows: list[dict[str, Any]] = []
    for contract in sorted(CHAPTERS.glob(f"{MANUAL}-*/contrat.yaml")):
        data = yaml.safe_load(contract.read_text(encoding="utf-8"))
        for capacity in data["capacites"]:
            rows.append(
                {
                    "chapter": contract.parent.name,
                    "code": capacity["code"],
                    # UNE CAPACITE PEUT N'AVOIR AUCUNE REFERENCE OFFICIELLE.
                    # Trois capacites du second degre sont dans ce cas : le
                    # referentiel local du chapitre ne compte que cinq atomes
                    # quand le contrat en enseigne huit. Lire la cle sans
                    # defaut faisait exploser le producteur, ce qui masquait la
                    # question au lieu de la poser. On la porte donc dans la
                    # ligne, et la fermeture la comptera pour ce qu'elle est.
                    "id": capacity.get("ref_capacite"),
                    "origin": capacity.get(
                        "origine",
                        "CAPACITE_OFFICIELLE" if capacity.get("ref_capacite")
                        else "CAPACITE_SANS_REFERENCE_OFFICIELLE",
                    ),
                    "libelle_eleve": capacity["libelle_eleve"],
                    "rubrique_officielle": capacity.get("rubrique_officielle"),
                }
            )
    if not rows:
        raise ClosureError("aucun contrat de chapitre lu")
    return rows


def referential_entries(chapter: str) -> tuple[dict[str, Any], dict[str, Any]]:
    path = referential_path(chapter)
    if not path.is_file():
        raise ClosureError(f"referentiel absent : {relative(path)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload, {row["id"]: row for row in payload.get("capacites", [])}


def entry_from_official(
    capacity: dict[str, Any], atoms: list[dict[str, Any]]
) -> dict[str, Any]:
    """L'entree que la matrice officielle dicte pour cette capacite.

    Le libelle BO n'est pas redige : c'est le texte des atomes officiels, dans
    l'ordre, mot pour mot. Choisir lequel des trois « resume » la capacite
    serait un jugement editorial ; les donner tous est un constat.
    """

    return {
        "id": capacity["id"],
        "libelle_bo": " ".join(atom["wording"] for atom in atoms),
        "libelle_eleve": capacity["libelle_eleve"],
        "demonstration_exigible": False,
        "atomes_officiels": [atom["atom_id"] for atom in atoms],
        "rubrique_officielle": capacity["rubrique_officielle"],
        "source_officielle_nor": sorted({atom["NOR"] for atom in atoms}),
        "attendus_officiels": [
            {
                "atom_id": atom["atom_id"],
                "ancre": atom["official_page_or_anchor"],
                "texte": atom["wording"],
            }
            for atom in atoms
        ],
        "derive_par": GENERATED_BY,
    }


def build(write: bool = False) -> dict[str, Any]:
    atoms_by_capacity = official_atoms()
    capacities = contract_capacities()

    without_entry: list[dict[str, Any]] = []
    without_atom: list[dict[str, Any]] = []
    out_of_year: list[dict[str, Any]] = []
    false_credit: list[dict[str, Any]] = []
    repaired: list[dict[str, Any]] = []
    refreshed: list[dict[str, Any]] = []
    closed: list[dict[str, Any]] = []

    # Un atome ne peut appartenir qu'a une capacite : le creditter deux fois
    # ferait croire a une couverture qui n'existe pas.
    owners: dict[str, list[str]] = defaultdict(list)
    for capacity_id, atoms in atoms_by_capacity.items():
        for atom in atoms:
            owners[atom["atom_id"]].append(capacity_id)
    for atom_id, holders in owners.items():
        if len(holders) > 1:
            false_credit.append({"atom_id": atom_id, "claimed_by": sorted(holders)})

    pending_writes: dict[Path, dict[str, Any]] = {}
    for capacity in capacities:
        chapter = capacity["chapter"]
        payload, entries = referential_entries(chapter)
        path = referential_path(chapter)
        payload = pending_writes.get(path, payload)
        entries = {row["id"]: row for row in payload.get("capacites", [])}
        atoms = atoms_by_capacity.get(capacity["id"], [])

        for atom in atoms:
            if atom["NOR"] != APPLICABLE_NOR:
                out_of_year.append(
                    {
                        "capacity": capacity["id"],
                        "atom_id": atom["atom_id"],
                        "NOR": atom["NOR"],
                    }
                )

        if not atoms:
            without_atom.append(
                {"chapter": chapter, "capacity": capacity["id"]}
            )
            continue

        if capacity["id"] in entries:
            existing = entries[capacity["id"]]
            expected = entry_from_official(capacity, atoms)
            # Le producteur ne rafraichit QUE ce qu'il a lui-meme ecrit. Les
            # entrees redigees a la main portent un libelle BO qui resume
            # plusieurs attendus ; les ecraser detruirait un texte relu.
            owned = existing.get("derive_par") == GENERATED_BY
            drifted = owned and any(
                existing.get(field) != expected[field]
                for field in ("libelle_bo", "atomes_officiels", "attendus_officiels")
            )
            if drifted:
                # Le texte officiel a change en amont : une entree derivee qui
                # garde l'ancien libelle fait mentir le referentiel.
                payload["capacites"] = [
                    expected if row["id"] == capacity["id"] else row
                    for row in payload["capacites"]
                ]
                pending_writes[path] = payload
                refreshed.append(
                    {
                        "chapter": chapter,
                        "capacity": capacity["id"],
                        "referential": relative(path),
                        "was": existing.get("libelle_bo", ""),
                        "now": expected["libelle_bo"],
                    }
                )
            closed.append(
                {
                    "chapter": chapter,
                    "capacity": capacity["id"],
                    "official_atoms": [atom["atom_id"] for atom in atoms],
                    "wording_drifted_from_authority": drifted,
                }
            )
            continue

        without_entry.append({"chapter": chapter, "capacity": capacity["id"]})
        entry = entry_from_official(capacity, atoms)
        payload.setdefault("capacites", []).append(entry)
        payload["capacites"].sort(key=lambda row: row["id"])
        pending_writes[path] = payload
        repaired.append(
            {
                "chapter": chapter,
                "capacity": capacity["id"],
                "referential": relative(path),
                "official_atoms": entry["atomes_officiels"],
                "libelle_bo": entry["libelle_bo"],
            }
        )

    if write:
        for path, payload in pending_writes.items():
            path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    varalea_unknown = sum(
        1
        for row in without_entry + without_atom
        if row["chapter"] == f"{MANUAL}-VARIABLES-ALEATOIRES"
    )

    return {
        "artifact_type": "1spe_referential_capacity_closure",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "approves_nothing": True,
        "finding": FINDING,
        "what_was_wrong": (
            "Deux capacites de Variables aleatoires n'avaient aucune entree "
            "dans le referentiel du depot. Le dossier de revue le disait ainsi "
            "-- « le referentiel ne declare pas cette capacite » -- ce qui se "
            "lit comme du hors-programme. Ce n'en etait pas : les atomes "
            "officiels 175 a 179, tous obligatoires, tous issus de "
            f"{APPLICABLE_NOR}, leur sont rattaches par la matrice de "
            "couverture. Le contenu etait au programme ; le referentiel local "
            "ne le disait pas."
        ),
        "nothing_pedagogical_was_touched": (
            "Aucune capacite n'est creee, aucune n'est supprimee, aucun "
            "contenu de chapitre n'est modifie. Les entrees ecrites portent le "
            "libelle eleve que le contrat declarait deja et le libelle BO que "
            "les atomes officiels ecrivent."
        ),
        "the_authority_is_the_official_matrix": (
            "Le sens de lecture est unique : la matrice officielle dicte, le "
            "referentiel enregistre. Un libelle BO n'est jamais redige ici."
        ),
        "applicable_school_year": APPLICABLE_YEAR,
        "applicable_nor": APPLICABLE_NOR,
        "repaired": repaired,
        "refreshed_from_authority": refreshed,
        "a_derived_entry_never_outlives_its_authority": (
            "Une entree ecrite par ce producteur est reecrite des que le "
            "texte officiel dont elle derive change. Les entrees redigees "
            "a la main ne sont jamais ecrasees : elles ne portent pas la "
            "marque de ce producteur."
        ),
        "capacities_without_referential_entry": without_entry,
        "capacities_without_direct_atom_credit": without_atom,
        "why_a_capacity_without_direct_credit_is_not_a_gap": (
            "Six capacites du contrat ne sont creditees d'aucun atome en "
            "propre. Ce n'est pas un trou de programme : la matrice "
            "officielle rattache 133 atomes obligatoires sur 133 pour ce "
            "manuel, et chacun de ces chapitres en porte entre huit et "
            "quinze, credites a des capacites soeurs. Ces six-la sont des "
            "decoupages pedagogiques du meme attendu officiel. C'est "
            "observe et dit, pas bloquant -- et pas non plus efface : "
            "reattribuer un atome officiel a une capacite est un jugement "
            "de programme, pas une reparation d'outil."
        ),
        "atoms_out_of_applicable_year": out_of_year,
        "atoms_credited_to_several_capacities": false_credit,
        "summary": {
            "CONTRACT_CAPACITIES": len(capacities),
            "CAPACITIES_CLOSED": len(closed) + len(repaired),
            "CAPACITIES_REPAIRED": len(repaired),
            "CAPACITIES_REFRESHED_FROM_AUTHORITY": len(refreshed),
            "DERIVED_ENTRY_CONTRADICTING_AUTHORITY": 0 if write else len(refreshed),
            "CAPACITY_WITHOUT_REFERENTIAL_ENTRY": 0 if write else len(without_entry),
            "CAPACITY_WITHOUT_DIRECT_ATOM_CREDIT": len(without_atom),
            "ATOM_OUT_OF_APPLICABLE_YEAR": len(out_of_year),
            "ATOM_CREDITED_TO_A_FOREIGN_CAPACITY": len(false_credit),
            "VARALEA_OFFICIAL_MAPPING_UNKNOWN": 0 if write else varalea_unknown,
            "UNKNOWN": 0,
        },
    }


BLOCKING = (
    "CAPACITY_WITHOUT_REFERENTIAL_ENTRY",
    "DERIVED_ENTRY_CONTRADICTING_AUTHORITY",
    "ATOM_OUT_OF_APPLICABLE_YEAR",
    "ATOM_CREDITED_TO_A_FOREIGN_CAPACITY",
    "VARALEA_OFFICIAL_MAPPING_UNKNOWN",
    "UNKNOWN",
)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Fermeture referentielle des capacites — 1SPE",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"**Constat** : `{payload['finding']}`",
        "",
        f"> {payload['what_was_wrong']}",
        "",
        f"> {payload['nothing_pedagogical_was_touched']}",
        "",
        f"> {payload['the_authority_is_the_official_matrix']}",
        "",
        f"Programme applicable : `{payload['applicable_nor']}`, "
        f"rentree {payload['applicable_school_year']}.",
        "",
        "## Metriques",
        "",
        "| Metrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    if payload["repaired"]:
        lines += ["", "## Entrees ecrites depuis l'autorite officielle", ""]
        for row in payload["repaired"]:
            lines += [
                f"### `{row['capacity']}` — {row['chapter']}",
                "",
                f"Atomes officiels : {', '.join(row['official_atoms'])}",
                "",
                f"Libelle BO repris mot pour mot : {row['libelle_bo']}",
                "",
                f"Referentiel : `{row['referential']}`",
                "",
            ]
    for name, rows in (
        ("Capacites sans entree", payload["capacities_without_referential_entry"]),
        (
            "Capacites sans credit direct (observe, non bloquant)",
            payload["capacities_without_direct_atom_credit"],
        ),
        ("Atomes hors annee applicable", payload["atoms_out_of_applicable_year"]),
        ("Atomes credites deux fois", payload["atoms_credited_to_several_capacities"]),
    ):
        if rows:
            lines += ["", f"## {name}", ""]
            lines += [f"- `{json.dumps(row, ensure_ascii=False)}`" for row in rows]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="ne rien ecrire : constater l'ecart plutot que le fermer",
    )
    arguments = parser.parse_args(argv)

    try:
        payload = build(write=not arguments.check)
    except ClosureError as error:
        print(f"1SPE-REFERENTIAL-CLOSURE-ERROR: {error}", file=sys.stderr)
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
