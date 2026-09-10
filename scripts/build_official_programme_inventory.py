#!/usr/bin/env python3
"""Construit l'inventaire officiel des six manuels a partir des textes du BO.

Point de depart : le texte officiel, et lui seul. Le referentiel interne du
depot dit ce que les manuels PRETENDENT couvrir ; s'en servir pour verifier la
couverture reviendrait a comparer une copie a elle-meme. L'inventaire produit
ici ne connait ni chapitre, ni contrat, ni identifiant interne.

Deux mises en page coexistent et exigent deux lectures differentes : les
programmes de mathematiques sont des listes a puces par rubrique, ceux de NSI
des tableaux a trois colonnes qu'on lit dans le PDF, seul endroit ou les
cellules restent exactes.

La configuration est declaree document par document, et non deduite. Deux
programmes n'ont ni les memes intitules de partie, ni les memes puces -- le BO
de 2019 compose les siennes en police Symbol -- ni le meme rang pour un meme
mot : « Probabilites » est une partie du programme de terminale et un simple
domaine d'automatismes en premiere. Ce qui est declare ici est donc verifiable
et discutable, plutot que devine a l'execution.

Les textes de 2026 applicables a la terminale seulement A PARTIR de la rentree
2027 sont extraits eux aussi, mais marques comme non applicables a l'edition
2026-2027 : c'est ce qui permettra de detecter qu'un chapitre de terminale
s'appuierait sur un programme qui ne le regit pas encore.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import extract_official_programme as puces
import extract_official_programme_table as tableau

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "audit" / "official"
INDEX = ROOT / "audit" / "OFFICIAL_PROGRAMME_INVENTORY.json"

#: Edition scolaire couverte par la collection.
EDITION = "2026-2027"

DOCUMENTS: tuple[dict[str, Any], ...] = (
    {
        "manual": "1SPE",
        "authority_ref": "MENE2602917A",
        "layout": "bullets",
        "source": "Mathematiques/manuel-maths/sources/txt/BO2026_1SPE_specialite.txt",
        "effective_from": "2026-09-01",
        "effective_until": None,
        "applies_to_edition": True,
        "sections": (
            "Vocabulaire ensembliste et logique",
            "Algorithmique et programmation",
            "Automatismes",
            "Algèbre",
            "Analyse",
            "Géométrie",
            "Probabilités et statistiques",
        ),
        "note": (
            "Programme du 26-02-2026, applicable des la rentree 2026 en premiere. "
            "Il porte une partie « Automatismes » qui est une composante "
            "obligatoire du programme, et non un appendice."
        ),
    },
    {
        "manual": "TSPE",
        "authority_ref": "MENE1921246A",
        "layout": "bullets",
        "source": "Mathematiques/manuel-maths/sources/txt/BO2019_TSPE_specialite.txt",
        "effective_from": "2020-09-01",
        "effective_until": "2027-08-31",
        "applies_to_edition": True,
        "sections": (
            "Algèbre et géométrie",
            "Analyse",
            "Probabilités",
            "Algorithmique et programmation",
            "Vocabulaire ensembliste et logique",
        ),
        "note": (
            "La reforme de 2026 ne touche la terminale qu'a la rentree 2027 : "
            "en 2026-2027 le programme applicable reste celui de 2019."
        ),
    },
    {
        "manual": "TCOMPL",
        "authority_ref": "MENE1921265A",
        "layout": "bullets",
        "source": "Mathematiques/manuel-maths/sources/txt/BO2019_TCOMPL_optionnel.txt",
        "effective_from": "2020-09-01",
        "effective_until": "2027-08-31",
        "applies_to_edition": True,
        "body_starts_at": 192,
        "sections": (
            "Thèmes d’étude",
            "Analyse",
            "Probabilités et statistique",
            "Algorithmique et programmation",
            "Vocabulaire ensembliste et logique",
        ),
        "note": (
            "Ce programme n'a pas de titre « Programme » isole : son corps "
            "commence aux themes d'etude, qui en font partie."
        ),
    },
    {
        "manual": "TEXPERTES",
        "authority_ref": "MENE1921264A",
        "layout": "bullets",
        "source": "Mathematiques/manuel-maths/sources/txt/BO2019_TEXPERTES_optionnel.txt",
        "effective_from": "2020-09-01",
        "effective_until": None,
        "applies_to_edition": True,
        "sections": ("Nombres complexes", "Arithmétique", "Graphes et matrices"),
        "note": (
            "Aucun arrete de 2026 ne remplace ce programme : la reforme ne "
            "s'y etend pas par analogie avec les autres enseignements."
        ),
    },
    {
        "manual": "1NSI",
        "authority_ref": "MENE1901633A",
        "layout": "table",
        "source": "NSI/corpus_nsi/00_programmes_officiels/programme_nsi_premiere.pdf",
        "effective_from": "2019-09-01",
        "effective_until": None,
        "applies_to_edition": True,
        "note": "Programme publie en tableau a trois colonnes ; lu dans le PDF.",
    },
    {
        "manual": "TNSI",
        "authority_ref": "MENE1921247A",
        "layout": "table",
        "source": "NSI/corpus_nsi/00_programmes_officiels/programme_nsi_terminale.pdf",
        "effective_from": "2020-09-01",
        "effective_until": None,
        "applies_to_edition": True,
        "note": (
            "Programme d'enseignement. La definition d'epreuve MENE2516123N "
            "reste dans un autre espace d'autorite et n'ajoute aucun contenu."
        ),
    },
    {
        "manual": "TSPE",
        "authority_ref": "MENE2602919A",
        "layout": "bullets",
        "source": "Mathematiques/manuel-maths/sources/txt/BO2026_TSPE_specialite_r2027.txt",
        "effective_from": "2027-09-01",
        "effective_until": None,
        "applies_to_edition": False,
        "sections": (
            "Vocabulaire ensembliste et logique",
            "Algorithmique et programmation",
            "Algèbre et géométrie",
            "Analyse",
            "Probabilités",
            "Automatismes",
        ),
        "note": (
            "Programme de terminale du 26-02-2026, applicable a la rentree "
            "2027. Il ne regit PAS l'edition 2026-2027 : il n'est extrait que "
            "pour pouvoir detecter qu'un chapitre s'y adosserait par avance."
        ),
    },
)


def _digest(charge: dict[str, Any]) -> str:
    canon = json.dumps(charge, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canon.encode("utf-8")).hexdigest()


def construire(doc: dict[str, Any]) -> dict[str, Any]:
    source = ROOT / doc["source"]
    if doc["layout"] == "table":
        res = tableau.extract(source, doc["authority_ref"], doc["manual"])
        items, rejets = res["items"], res["discarded"]
        comptes = {
            "table_rows": len(res["row_bindings"]),
            "non_empty_cells": res["cells"],
            "extracted_items": len(items),
            "discarded_fragments": len(rejets),
        }
        extra: dict[str, Any] = {
            "official_sections": res["rubrics"],
            "row_bindings": res["row_bindings"],
        }
    else:
        ext = puces.extract(
            source.read_text(encoding="utf-8"),
            doc["authority_ref"],
            doc["manual"],
            doc.get("body_starts_at"),
            tuple(doc.get("sections", puces.SECTION_NAMES)),
        )
        items, rejets = ext.items, ext.discarded
        total = len(items) + len(rejets)
        if total != ext.bullets_in_body:
            raise SystemExit(
                f"{doc['manual']}/{doc['authority_ref']} : "
                f"{ext.bullets_in_body} puces dans le corps mais {total} "
                f"comptabilisees -- du texte officiel serait perdu en silence"
            )
        comptes = {
            "body_starts_at_line": ext.body_starts_at,
            "pages": ext.pages,
            "bullets_in_preamble_excluded": ext.bullets_in_preamble,
            "bullets_in_body": ext.bullets_in_body,
            "extracted_items": len(items),
            "discarded_bullets": len(rejets),
            "every_body_bullet_accounted_for": True,
        }
        extra = {"declared_sections": list(doc.get("sections", puces.SECTION_NAMES))}

    for item in items:
        item["effective_from"] = doc["effective_from"]
        item["effective_until"] = doc["effective_until"]
        item["applies_to_edition_" + EDITION.replace("-", "_")] = doc["applies_to_edition"]

    kinds: dict[str, int] = {}
    for item in items:
        kinds[item["kind"]] = kinds.get(item["kind"], 0) + 1

    return {
        "artifact_type": "official_programme_inventory",
        "schema_version": 1,
        "generated_by": "scripts/build_official_programme_inventory.py",
        "edition": EDITION,
        "manual": doc["manual"],
        "authority_ref": doc["authority_ref"],
        "authority_namespace": "PROGRAMME_D_ENSEIGNEMENT",
        "layout": doc["layout"],
        "applies_to_edition": doc["applies_to_edition"],
        "effective_from": doc["effective_from"],
        "effective_until": doc["effective_until"],
        "note": doc["note"],
        "source_path": doc["source"],
        "source_sha256": "sha256:"
        + hashlib.sha256(source.read_bytes()).hexdigest(),
        "identifiers_are_locally_assigned": True,
        "accounting": comptes,
        "kind_counts": dict(sorted(kinds.items())),
        **extra,
        "items": items,
        "discarded": rejets,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="regenere sans ecrire et signale toute divergence",
    )
    args = parser.parse_args(argv)

    index: list[dict[str, Any]] = []
    divergents: list[str] = []
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for doc in DOCUMENTS:
        charge = construire(doc)
        nom = f"{doc['manual']}_{doc['authority_ref']}.json"
        chemin = OUT_DIR / nom
        texte = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
        if args.check:
            if not chemin.exists() or chemin.read_text(encoding="utf-8") != texte:
                divergents.append(str(chemin.relative_to(ROOT)))
        else:
            chemin.write_text(texte, encoding="utf-8")
        index.append({
            "manual": doc["manual"],
            "authority_ref": doc["authority_ref"],
            "applies_to_edition": doc["applies_to_edition"],
            "effective_from": doc["effective_from"],
            "effective_until": doc["effective_until"],
            "layout": doc["layout"],
            "source_path": doc["source"],
            "source_sha256": charge["source_sha256"],
            "inventory_path": str(chemin.relative_to(ROOT)),
            "inventory_digest": _digest(charge),
            "items": len(charge["items"]),
            "mandatory_items": sum(1 for i in charge["items"] if i["mandatory"]),
            "kind_counts": charge["kind_counts"],
        })

    applicables = [e for e in index if e["applies_to_edition"]]
    resume = {
        "artifact_type": "official_programme_inventory_index",
        "schema_version": 1,
        "generated_by": "scripts/build_official_programme_inventory.py",
        "edition": EDITION,
        "OFFICIAL_REFERENCES_VERIFIED": f"{len(applicables)}/6",
        "identifiers_are_locally_assigned": True,
        "identifier_note": (
            "Les official_id sont des identifiants techniques forges par ce "
            "depot pour le pipeline. Le ministere n'en publie pas : la "
            "reference reste le libelle officiel et son ancrage."
        ),
        "official_items_applicable": sum(e["items"] for e in applicables),
        "official_items_mandatory": sum(e["mandatory_items"] for e in applicables),
        "documents": index,
    }
    texte = json.dumps(resume, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not INDEX.exists() or INDEX.read_text(encoding="utf-8") != texte:
            divergents.append(str(INDEX.relative_to(ROOT)))
        if divergents:
            print("DIVERGENT :", *divergents, sep="\n  ")
            return 1
        print("Inventaire officiel conforme au generateur.")
        return 0

    INDEX.write_text(texte, encoding="utf-8")
    for e in index:
        marque = "" if e["applies_to_edition"] else "   (hors edition)"
        print(f"{e['manual']:>10} {e['authority_ref']}  {e['items']:4d} items"
              f"  dont {e['mandatory_items']:4d} obligatoires{marque}")
    print(f"\nOFFICIAL_REFERENCES_VERIFIED = {resume['OFFICIAL_REFERENCES_VERIFIED']}")
    print(f"items officiels applicables  = {resume['official_items_applicable']}")
    print(f"dont obligatoires            = {resume['official_items_mandatory']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
