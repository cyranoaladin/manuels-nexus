#!/usr/bin/env python3
"""Inventaire officiel des programmes publies en tableau (NSI), lu depuis le PDF.

Les programmes de NSI ne sont pas rediges en listes a puces comme ceux de
mathematiques : ils sont publies sous forme d'un tableau a trois colonnes
« Contenus | Capacites attendues | Commentaires », rubrique par rubrique. Un
extracteur a puces n'y trouverait rien.

La lecture se fait sur le PDF, et non sur son export texte. Un export `pdftotext`
aplatit le tableau : les colonnes n'y sont plus separees que par des espaces, et
il arrive qu'un seul espace separe la fin d'une cellule du debut de la suivante
(« Systeme de gestion de Identifier les services rendus par Il s'agit de »).
Reconstituer les colonnes a partir de cet aplatissement fait deriver des mots
d'une colonne a l'autre et corrompt le libelle officiel -- ce qui est
disqualifiant pour un texte qui doit servir de reference. Le PDF, lui, porte les
filets du tableau et les coordonnees des mots : les cellules en sortent exactes.

Il en sort aussi quelque chose que l'export texte avait definitivement perdu :
le LIEN entre une capacite attendue et le contenu de la meme ligne. Ce lien est
conserve ici (`official_row`), car c'est lui qui dit quelle connaissance une
capacite met en oeuvre.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

import pdfplumber

sys.path.insert(0, str(Path(__file__).resolve().parent))

import programme_normativity as pn  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

#: Colonnes du tableau du BO. La portee de chacune est prise dans la table
#: commune de normativite, sur la foi de l'intitule imprime par le programme :
#: les commentaires y eclairent la mise en oeuvre sans ajouter d'attendu.
COLUMNS = ("Contenus", "Capacités attendues", "Commentaires")
HEADER_CELLS = ("contenus", "capacites attendues", "commentaires")
#: Bandeau de pied de page, present sur chaque page du BO. Un passage qui
#: franchit une page le ramasserait au milieu de son texte.
FOOTER = re.compile(r"©\s*Minist[èe]re|www\.education\.gouv\.fr")
#: Les titres de rubrique sont composes en corps 14, le texte courant en 11.
HEADING_MIN_SIZE = 12.5
#: Ecart tolere, en points, entre l'ordonnee d'une ligne et celle de ses
#: caracteres.
MARGE_DE_LIGNE = 2.0
#: Une phrase se termine par un point ou un point-virgule suivi d'une majuscule.
#: Le decoupage ne coupe donc pas « (taille, encadrement de la hauteur, etc.). ».
SENTENCE = re.compile(r"(?<=[.;])\s+(?=[A-ZÀ-ÖØ-Þ«])")
#: Dans le preambule, les exigences se presentent aussi en listes dont chaque
#: element se termine par un point-virgule et commence en minuscule. Ne couper
#: que devant une majuscule y aurait ramasse six competences en un seul item.
SENTENCE_PREAMBULE = re.compile(r"(?<=[.;])\s+")
MIN_ITEM_LEN = 8


def strip_accents(texte: str) -> str:
    sans = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in sans if not unicodedata.combining(c))


def normalise(texte: str) -> str:
    return re.sub(r"\s+", " ", strip_accents(texte)).strip().lower()


def _slug(texte: str, longueur: int = 34) -> str:
    base = re.sub(r"[^A-Z0-9]+", "-", strip_accents(texte).upper()).strip("-")
    return base[:longueur].rstrip("-") or "ITEM"


def titres_de_page(page: pdfplumber.page.Page) -> list[tuple[float, str]]:
    """Releve les titres de rubrique d'une page, avec leur ordonnee."""
    lignes: dict[int, list[dict[str, Any]]] = {}
    for c in page.chars:
        if c["size"] >= HEADING_MIN_SIZE:
            lignes.setdefault(round(c["top"]), []).append(c)
    titres = []
    for y in sorted(lignes):
        texte = "".join(c["text"] for c in sorted(lignes[y], key=lambda c: c["x0"]))
        texte = re.sub(r"\s+", " ", texte).strip()
        if texte:
            titres.append((float(y), texte))
    return titres


def est_entete(cellules: list[str | None]) -> bool:
    return tuple(normalise(c or "") for c in cellules[:3]) == HEADER_CELLS


def sections_de_preambule(
    page: pdfplumber.page.Page, voulues: tuple[str, ...]
) -> list[tuple[str, str]]:
    """Recupere le texte des parties prescriptives du preambule.

    Le preambule d'un programme de NSI n'est pas que du cadrage : il y impose
    aussi des obligations, dont « Un quart au moins de l'horaire total de la
    specialite est reserve a la conception et a l'elaboration de projets ».
    Ces exigences n'apparaissent dans aucun tableau ; ne lire que les tableaux
    les faisait disparaitre du programme, alors qu'elles engagent le manuel.

    Les parties retenues sont DECLAREES a l'appel. Deviner lesquelles d'un
    preambule sont prescriptives et lesquelles sont de simples intentions
    demanderait un jugement que ce script n'a pas a rendre seul.
    """
    if not voulues:
        return []
    attendus = {normalise(v) for v in voulues}
    titres = titres_de_page(page)
    if not titres:
        return []
    bas = min((t.bbox[1] for t in page.find_tables()), default=page.height)
    trouves: list[tuple[str, str]] = []
    for rang, (y, texte) in enumerate(titres):
        if normalise(texte) not in attendus:
            continue
        fin = titres[rang + 1][0] if rang + 1 < len(titres) else bas
        mots = [
            m for m in page.extract_words()
            if y < float(m["top"]) < fin
        ]
        corps = re.sub(r"\s+", " ", " ".join(m["text"] for m in mots)).strip()
        if corps:
            trouves.append((texte, corps))
    return trouves


def lignes_de_page(page: pdfplumber.page.Page) -> list[tuple[float, str]]:
    """Lignes de la page, dans l'ordre, avec leur ordonnee.

    On s'appuie sur le decoupage de pdfplumber plutot que sur un regroupement
    par ordonnee arrondie : deux lignes voisines s'y confondaient, et leurs
    mots ressortaient melanges -- « Elle permet a jusqu'a la remettre en cause
    [...] chacun de faire evoluer sa pensee ».
    """
    return [
        (float(ligne["top"]), ligne["text"]) for ligne in page.extract_text_lines()
    ]


def passages_de_preambule(
    page: pdfplumber.page.Page, passages: tuple[tuple[str, str], ...]
) -> list[tuple[str, str]]:
    """Recupere des passages prescriptifs du preambule, designes par une amorce.

    Certaines exigences du preambule n'ont pas de titre a elles : le programme
    les introduit par une phrase (« Il permet de developper des competences : »)
    au fil du texte. Les objets du manuel s'y referent pourtant, sous un
    espace de noms qui leur est propre. Les laisser hors de l'inventaire
    faisait de ces references des capacites fantomes -- des metadonnees bien
    remplies designant quelque chose qui n'existe pas.

    Chaque passage est DECLARE par son amorce, jamais devine : deviner quelles
    phrases d'un preambule sont prescriptives demanderait un jugement que ce
    script n'a pas a rendre seul.
    """
    if not passages:
        return []
    lignes = plignes = lignes_de_page(page)
    titres = [y for y, _ in titres_de_page(page)]
    bas_tableau = min((t.bbox[1] for t in page.find_tables()), default=page.height)
    trouves: list[tuple[str, str]] = []
    for slug, amorce in passages:
        depart = next(
            (i for i, (_, texte) in enumerate(plignes) if re.search(amorce, texte)),
            None,
        )
        if depart is None:
            continue
        y_depart = lignes[depart][0]
        fins = [y for y in titres if y > y_depart] + [
            y for y, _ in (
                (ly, lt) for ly, lt in plignes
                if ly > y_depart
                and any(re.search(a, lt) for s2, a in passages if s2 != slug)
            )
        ] + [bas_tableau]
        y_fin = min(fins)
        # La marge absorbe l'ecart de quelques points entre l'ordonnee d'une
        # ligne et celle de ses caracteres : sans elle, le titre suivant --
        # « Demarche de projet » -- se retrouvait aspire dans le passage.
        # Les pieds de page sont ecartes : un passage qui franchit une page en
        # ramassait le bandeau du ministere.
        corps = " ".join(
            texte for y, texte in lignes
            if y_depart <= y < y_fin - MARGE_DE_LIGNE and not FOOTER.search(texte)
        )
        corps = re.sub(r"\s+", " ", corps).strip()
        if corps:
            trouves.append((slug, corps))
    return trouves


def extract(
    pdf_path: Path,
    authority: str,
    manual: str,
    preamble_sections: tuple[str, ...] = (),
    preamble_passages: tuple[tuple[str, str], ...] = (),
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    rejets: list[dict[str, Any]] = []
    rubriques: list[str] = []
    liaisons: list[dict[str, Any]] = []
    cellules_vues = 0
    rubrique = "(rubrique non identifiee)"
    ligne_globale = 0

    with pdfplumber.open(str(pdf_path)) as pdf:
        for numero_page, page in enumerate(pdf.pages, start=1):
            prescriptifs = [
                (titre, corps, pn.PROJECT_REQUIREMENT)
                for titre, corps in sections_de_preambule(page, preamble_sections)
            ]
            descriptifs = [
                (slug, texte, pn.for_preamble_passage(slug))
                for slug, texte in passages_de_preambule(page, preamble_passages)
            ]
            for titre, corps, portee_p in prescriptifs + descriptifs:
                for rang, phrase in enumerate(
                    (m.strip() for m in SENTENCE_PREAMBULE.split(corps)), start=1
                ):
                    if len(phrase) < MIN_ITEM_LEN:
                        continue
                    empreinte = hashlib.sha256(phrase.encode("utf-8")).hexdigest()[:8]
                    items.append({
                        "official_id": "::".join(
                            [authority, _slug(titre),
                             portee_p.local_kind, empreinte]
                        ),
                        "locally_assigned_identifier": True,
                        "manual": manual,
                        "authority_ref": authority,
                        "official_section": "Préambule",
                        "official_subsection": titre,
                        "official_subheading": None,
                        "official_heading": titre,
                        "official_rubric": titre,
                        "official_rubric_index": rang,
                        "official_normativity": portee_p.normativity,
                        "normativity_basis": portee_p.basis,
                        "local_kind": portee_p.local_kind,
                        "exact_example_imposed": True,
                        "official_row": None,
                        "rubric_is_implicit_in_source": False,
                        "official_wording": phrase,
                        "kind": portee_p.local_kind,
                        "mandatory": portee_p.mandatory,
                        "source_page_or_anchor": f"page={numero_page};preamble={_slug(titre)}",
                    })
                if titre not in rubriques:
                    rubriques.append(titre)
            titres = titres_de_page(page)
            tableaux = page.find_tables()
            for tableau in sorted(tableaux, key=lambda t: t.bbox[1]):
                haut = tableau.bbox[1]
                # Un tableau peut se poursuivre sur la page suivante sans titre
                # ni ligne d'entete : la rubrique en vigueur est alors celle
                # relevee precedemment, et non « rubrique non identifiee ».
                for y, texte in titres:
                    if y < haut:
                        rubrique = texte
                if rubrique not in rubriques:
                    rubriques.append(rubrique)
                for rangee in tableau.extract():
                    if est_entete(rangee):
                        continue
                    if not any((c or "").strip() for c in rangee[:3]):
                        continue
                    ligne_globale += 1
                    liaison: dict[str, Any] = {
                        "official_row": ligne_globale,
                        "official_section": rubrique,
                        "page": numero_page,
                        "knowledge": [],
                        "expected_capacity": [],
                        "commentary": [],
                    }
                    for index, titre in enumerate(COLUMNS):
                        portee = pn.resolve(None, titre)
                        nature = portee.local_kind
                        brut = rangee[index] if index < len(rangee) else None
                        texte = re.sub(r"\s+", " ", (brut or "")).strip()
                        if not texte:
                            continue
                        cellules_vues += 1
                        morceaux = [m.strip() for m in SENTENCE.split(texte)]
                        # Le decoupage en phrases ne coupe que sur des blancs :
                        # recoller les morceaux doit redonner la cellule. Si ce
                        # n'est pas le cas, du texte officiel a ete perdu.
                        if " ".join(morceaux) != texte:
                            rejets.append({
                                "official_section": rubrique,
                                "column": titre,
                                "reason": "SENTENCE_SPLIT_IS_NOT_LOSSLESS",
                                "text": texte,
                            })
                            continue
                        for rang, morceau in enumerate(morceaux, start=1):
                            if len(morceau) < MIN_ITEM_LEN:
                                if morceau:
                                    rejets.append({
                                        "official_section": rubrique,
                                        "column": titre,
                                        "reason": "FRAGMENT_TOO_SHORT_TO_BE_AN_ITEM",
                                        "text": morceau,
                                    })
                                continue
                            empreinte = hashlib.sha256(
                                morceau.encode("utf-8")
                            ).hexdigest()[:8]
                            oid = "::".join(
                                [authority, _slug(rubrique), _slug(titre),
                                 nature, empreinte]
                            )
                            liaison[
                                ("knowledge", "expected_capacity", "commentary")[index]
                            ].append(oid)
                            items.append({
                                "official_id": oid,
                                "locally_assigned_identifier": True,
                                "manual": manual,
                                "authority_ref": authority,
                                "official_section": rubrique,
                                "official_subsection": None,
                                "official_subheading": None,
                                "official_heading": titre,
                                "official_rubric": titre,
                                "official_normativity": portee.normativity,
                                "normativity_basis": portee.basis,
                                "local_kind": nature,
                                "exact_example_imposed": portee.exact_example_imposed,
                                "official_row": ligne_globale,
                                "rubric_is_implicit_in_source": False,
                                "official_wording": morceau,
                                "kind": nature,
                                "mandatory": portee.mandatory,
                                "source_page_or_anchor": (
                                    f"page={numero_page};row={ligne_globale}"
                                ),
                            })
                    liaisons.append(liaison)
    return {
        "items": items,
        "discarded": rejets,
        "rubrics": rubriques,
        "row_bindings": liaisons,
        "cells": cellules_vues,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--authority", required=True)
    parser.add_argument("--manual", required=True)
    parser.add_argument("--effective-from", required=True)
    parser.add_argument("--effective-until", default=None)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    source = args.source.resolve()
    res = extract(source, args.authority, args.manual)
    for item in res["items"]:
        item["effective_from"] = args.effective_from
        item["effective_until"] = args.effective_until

    doublons = [
        oid for oid, n in Counter(i["official_id"] for i in res["items"]).items() if n > 1
    ]
    charge = {
        "artifact_type": "official_programme_inventory",
        "schema_version": 1,
        "generated_by": "scripts/extract_official_programme_table.py",
        "manual": args.manual,
        "authority_ref": args.authority,
        "effective_from": args.effective_from,
        "effective_until": args.effective_until,
        "source_path": str(source.relative_to(ROOT)),
        "source_sha256": "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest(),
        "identifiers_are_locally_assigned": True,
        "official_sections": res["rubrics"],
        "accounting": {
            "table_rows": len(res["row_bindings"]),
            "non_empty_cells": res["cells"],
            "extracted_items": len(res["items"]),
            "discarded_fragments": len(res["discarded"]),
            "duplicate_official_ids": len(doublons),
        },
        "kind_counts": dict(sorted(Counter(i["kind"] for i in res["items"]).items())),
        "items": res["items"],
        "row_bindings": res["row_bindings"],
        "discarded_bullets": res["discarded"],
    }
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(charge, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(f"{args.manual} / {args.authority} : {len(res['items'])} items officiels")
    print(f"   {len(res['row_bindings'])} lignes de tableau, {res['cells']} cellules,"
          f" {len(res['discarded'])} fragments ecartes")
    print(f"   rubriques : {len(res['rubrics'])}")
    for nature, n in charge["kind_counts"].items():
        print(f"   {n:4d}  {nature}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
