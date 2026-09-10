#!/usr/bin/env python3
"""Rattache chaque atome du referentiel interne a l'item officiel dont il releve.

L'inventaire officiel dit ce que le programme exige. Le referentiel interne dit
ce que les manuels declarent travailler. Tant que les deux ne sont pas relies
objet par objet, aucune affirmation de couverture n'est verifiable : compter
les atomes internes reviendrait a mesurer le manuel avec sa propre regle.

Le rattachement est etabli, jamais suppose, et son MODE est publie avec lui :

  ANCHOR   l'atome cite ses coordonnees dans le texte officiel (partie,
           rubrique, rang de la puce). Le lien est alors exact et rejouable.
  VERBATIM l'atome reprend mot pour mot le libelle officiel.
  PROPOSED aucun des deux : le rapprochement le mieux note est publie comme
           PROPOSITION, avec sa mesure et ses concurrents, et ne vaut pas
           couverture tant qu'un humain ne l'a pas tranche.

Cette distinction n'est pas une precaution de forme. Le champ `libelle_bo` du
referentiel interne porte un nom qui laisse croire au texte du BO, mais il en
est une reformulation dans la grande majorite des cas -- et le referentiel
decoupe parfois en deux atomes ce que le programme enonce en une seule capacite
(« Calculer la taille et la hauteur d'un arbre »). Traiter ces libelles comme
officiels ferait passer une reecriture pour une preuve, et le decoupage interne
pour une couverture plus large que le programme.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "audit" / "OFFICIAL_PROGRAMME_INVENTORY.json"
OUT = ROOT / "audit" / "OFFICIAL_PROGRAMME_BINDING.json"

REFERENTIELS = (
    ROOT / "Mathematiques" / "manuel-maths" / "referentiel",
    ROOT / "NSI" / "referentiel",
)
#: Coordonnees citees par un ancrage : « sous-partie / rubrique / puce N ».
ANCHOR = re.compile(r"^(?P<sub>.+?)\s*/\s*(?P<rub>[^/]+?)\s*/\s*puce\s*(?P<n>\d+)\s*$")
#: Mots-outils du francais : leur presence ne rapproche pas deux libelles.
VIDES = {
    "les", "des", "une", "der", "aux", "que", "qui", "pour", "dans", "sur",
    "avec", "par", "son", "sont", "est", "ont", "the", "and", "leur", "leurs",
    "ses", "cette", "aussi", "plus", "moins", "entre", "deux", "elle", "ils",
}
#: En dessous, le rapprochement n'a pas de sens : on ne propose rien.
PLANCHER = 0.18


def strip_accents(texte: str) -> str:
    sans = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in sans if not unicodedata.combining(c))


def normalise(texte: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", texte)).strip()


#: Equivalences typographiques. Le BO compose ses apostrophes en courbe, ses
#: variables en italique mathematique et son f de fonction en U+0192 ; le
#: referentiel interne saisit les memes phrases au clavier. Comparer les deux
#: caractere pour caractere faisait passer pour des reformulations des libelles
#: rigoureusement identiques -- « Resoudre un probleme d'optimisation. » n'y
#: differait de l'officiel que par la forme de son apostrophe.
TYPOGRAPHIE = {
    "\u2019": "'", "\u2018": "'", "\u201b": "'", "\u2032": "'",
    "\u201c": '"', "\u201d": '"', "\u00ab": '"', "\u00bb": '"',
    "\u0192": "f", "\u2212": "-", "\u2013": "-", "\u2014": "-",
    "\u00a0": " ", "\u202f": " ", "\u2009": " ",
}


def forme_typographique(texte: str) -> str:
    """Cle de comparaison : meme phrase, quelle que soit sa composition.

    Les blancs sont retires : « f(a+h) » et « f (a + h) » sont le meme
    attendu. Le risque de collision entre deux phrases distinctes est nul a
    cette longueur, alors que le risque de manquer une identite reelle, lui,
    etait avere.
    """
    texte = unicodedata.normalize("NFKC", texte)
    texte = "".join(TYPOGRAPHIE.get(c, c) for c in texte)
    return re.sub(r"\s+", "", texte)


def jetons(texte: str) -> set[str]:
    mots = re.findall(r"[a-z0-9]+", strip_accents(texte).lower())
    return {m for m in mots if len(m) >= 3 and m not in VIDES}


def proximite(a: set[str], b: set[str]) -> float:
    """Recouvrement de Jaccard : mesure simple, publiee, et donc contestable."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def charger_officiels() -> tuple[dict[str, list[dict[str, Any]]], dict[str, str]]:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    par_manuel: dict[str, list[dict[str, Any]]] = defaultdict(list)
    autorites: dict[str, str] = {}
    for entree in index["documents"]:
        if not entree["applies_to_edition"]:
            continue
        autorites[entree["manual"]] = entree["authority_ref"]
        charge = json.loads((ROOT / entree["inventory_path"]).read_text(encoding="utf-8"))
        par_manuel[entree["manual"]].extend(charge["items"])
    return par_manuel, autorites


def charger_atomes() -> list[dict[str, Any]]:
    atomes: list[dict[str, Any]] = []
    for dossier in REFERENTIELS:
        for chemin in sorted(dossier.glob("capacites_*.json")):
            charge = json.loads(chemin.read_text(encoding="utf-8"))
            for capacite in charge.get("capacites", []):
                atomes.append({
                    "atom_id": capacite["id"],
                    "manual": charge.get("niveau"),
                    "theme": charge.get("theme"),
                    "referential_path": str(chemin.relative_to(ROOT)),
                    "bo_reference": charge.get("bo_reference", ""),
                    "declared_authority": (charge.get("authority") or {}).get("nor"),
                    "libelle_bo": capacite.get("libelle_bo", ""),
                    "contenu_bo": capacite.get("contenu_bo"),
                    "source_anchor": capacite.get("source_anchor"),
                })
    return atomes


def resoudre_ancrage(
    ancrage: str, items: list[dict[str, Any]]
) -> dict[str, Any] | None:
    m = ANCHOR.match(normalise(ancrage))
    if not m:
        return None
    sub = strip_accents(m["sub"]).lower()
    rub = strip_accents(m["rub"]).lower()
    rang = int(m["n"])
    for item in items:
        contexte = item["official_subsection"] or item["official_section"] or ""
        if (
            strip_accents(contexte).lower() == sub
            and strip_accents(item["official_rubric"]).lower() == rub
            and item["official_rubric_index"] == rang
        ):
            return item
    return None


def lier(atome: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, Any]:
    if atome["source_anchor"]:
        cible = resoudre_ancrage(atome["source_anchor"], items)
        if cible is not None:
            return {
                "binding_method": "ANCHOR",
                "official_id": cible["official_id"],
                "official_wording": cible["official_wording"],
                "official_kind": cible["kind"],
                "binding_score": 1.0,
                "review_status": "CONFIRMED_BY_SOURCE_ANCHOR",
                "candidates": [],
            }
        return {
            "binding_method": "ANCHOR_UNRESOLVABLE",
            "official_id": None,
            "official_wording": None,
            "official_kind": None,
            "binding_score": 0.0,
            "review_status": "ANCHOR_DOES_NOT_RESOLVE_IN_THE_OFFICIAL_TEXT",
            "candidates": [],
        }

    libelle = normalise(atome["libelle_bo"])
    if libelle:
        cle = forme_typographique(libelle)
        for item in items:
            if forme_typographique(item["official_wording"]) == cle:
                return {
                    "binding_method": "VERBATIM",
                    "official_id": item["official_id"],
                    "official_wording": item["official_wording"],
                    "official_kind": item["kind"],
                    "binding_score": 1.0,
                    "review_status": "CONFIRMED_BY_VERBATIM_OFFICIAL_WORDING",
                    "candidates": [],
                }

    reference = jetons(libelle) | jetons(
        " ".join(atome["contenu_bo"])
        if isinstance(atome["contenu_bo"], list)
        else (atome["contenu_bo"] or "")
    )
    notes = sorted(
        (
            (proximite(reference, jetons(i["official_wording"])), i)
            for i in items
            if i["mandatory"]
        ),
        key=lambda t: (-t[0], t[1]["official_id"]),
    )[:3]
    if not notes or notes[0][0] < PLANCHER:
        return {
            "binding_method": "NONE",
            "official_id": None,
            "official_wording": None,
            "official_kind": None,
            "binding_score": round(notes[0][0], 3) if notes else 0.0,
            "review_status": "NO_OFFICIAL_PARENT_FOUND",
            "candidates": [],
        }
    return {
        "binding_method": "PROPOSED",
        "official_id": None,
        "official_wording": None,
        "official_kind": None,
        "binding_score": round(notes[0][0], 3),
        "review_status": "PROPOSED_REQUIRES_HUMAN_CONFIRMATION",
        "candidates": [
            {
                "official_id": i["official_id"],
                "official_wording": i["official_wording"],
                "kind": i["kind"],
                "score": round(s, 3),
            }
            for s, i in notes
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    officiels, autorites = charger_officiels()
    atomes = charger_atomes()
    liens: list[dict[str, Any]] = []
    for atome in atomes:
        items = officiels.get(atome["manual"] or "", [])
        lien = lier(atome, items) if items else {
            "binding_method": "NONE",
            "official_id": None,
            "official_wording": None,
            "official_kind": None,
            "binding_score": 0.0,
            "review_status": "MANUAL_HAS_NO_OFFICIAL_INVENTORY",
            "candidates": [],
        }
        liens.append({**atome, **lien})

    confirmes = [
        lien for lien in liens
        if lien["binding_method"] in ("ANCHOR", "VERBATIM")
    ]
    revendiques = {lien["official_id"] for lien in confirmes}

    # Un item officiel revendique par des atomes de plusieurs chapitres n'est
    # pas une anomalie en soi -- une capacite peut se travailler a plusieurs
    # endroits -- mais tant que rien ne le justifie, il ne doit pas etre compte
    # deux fois : ce serait gonfler la couverture avec le meme attendu.
    par_item: dict[str, set[str]] = defaultdict(set)
    for lien in confirmes:
        par_item[lien["official_id"]].add(f"{lien['manual']}/{lien['theme']}")
    multiples = {k: sorted(v) for k, v in par_item.items() if len(v) > 1}

    # Un referentiel ne doit invoquer que l'autorite applicable a son manuel.
    mauvaise_annee = []
    espace_viole = []
    for lien in liens:
        cite = set(re.findall(r"MENE\d{7}[A-Z]", lien["bo_reference"] or ""))
        if lien["declared_authority"]:
            cite.add(lien["declared_authority"])
        attendue = autorites.get(lien["manual"] or "")
        for nor in cite:
            if nor == "MENE2516123N":
                espace_viole.append({"atom_id": lien["atom_id"], "cited": nor})
            elif attendue and nor != attendue:
                mauvaise_annee.append(
                    {"atom_id": lien["atom_id"], "cited": nor, "expected": attendue}
                )

    resume_par_manuel: dict[str, dict[str, Any]] = {}
    for manuel, items in sorted(officiels.items()):
        obligatoires = [i for i in items if i["mandatory"]]
        couverts = [i for i in obligatoires if i["official_id"] in revendiques]
        atomes_manuel = [lien for lien in liens if lien["manual"] == manuel]
        # Le denominateur se ventile par nature, faute de quoi il ne veut rien
        # dire. Le referentiel interne est un referentiel de CAPACITES : il ne
        # peut pas, et n'a pas a, porter les « Contenus » du programme, dont la
        # trace se cherche dans le cours et non dans une capacite. Les compter
        # ensemble ferait passer pour un defaut de couverture ce qui n'est
        # qu'une difference de nature entre les deux objets.
        par_nature: dict[str, dict[str, int]] = {}
        for item in obligatoires:
            stat = par_nature.setdefault(
                item["kind"], {"mandatory": 0, "bound_confirmed": 0}
            )
            stat["mandatory"] += 1
            if item["official_id"] in revendiques:
                stat["bound_confirmed"] += 1
        resume_par_manuel[manuel] = {
            "authority_ref": autorites[manuel],
            "official_items": len(items),
            "official_mandatory": len(obligatoires),
            "official_mandatory_bound_confirmed": len(couverts),
            "OFFICIAL_REQUIRED_UNMAPPED": len(obligatoires) - len(couverts),
            "internal_atoms": len(atomes_manuel),
            "internal_atoms_confirmed": sum(
                1 for a in atomes_manuel
                if a["binding_method"] in ("ANCHOR", "VERBATIM")
            ),
            "INTERNAL_ATOM_WITHOUT_OFFICIAL_PARENT": sum(
                1 for a in atomes_manuel
                if a["binding_method"] not in ("ANCHOR", "VERBATIM")
            ),
            "by_official_kind": dict(sorted(par_nature.items())),
        }

    charge = {
        "artifact_type": "official_programme_binding",
        "schema_version": 1,
        "generated_by": "scripts/build_official_programme_binding.py",
        "edition": json.loads(INDEX.read_text(encoding="utf-8"))["edition"],
        "binding_methods": {
            "ANCHOR": "coordonnees citees dans le texte officiel ; exact et rejouable",
            "VERBATIM": "libelle repris mot pour mot du texte officiel",
            "PROPOSED": "rapprochement mesure, soumis a arbitrage humain ; ne vaut pas couverture",
            "NONE": "aucun parent officiel trouve",
        },
        "summary": {
            "internal_atoms": len(liens),
            "bound_confirmed": len(confirmes),
            "bound_proposed": sum(1 for lien in liens if lien["binding_method"] == "PROPOSED"),
            "unbound": sum(
                1 for lien in liens
                if lien["binding_method"] in ("NONE", "ANCHOR_UNRESOLVABLE", "MANUAL_HAS_NO_OFFICIAL_INVENTORY")
            ),
            "INTERNAL_ATOM_WITHOUT_OFFICIAL_PARENT": len(liens) - len(confirmes),
            "OFFICIAL_REQUIRED_UNMAPPED": sum(
                r["OFFICIAL_REQUIRED_UNMAPPED"] for r in resume_par_manuel.values()
            ),
            "UNJUSTIFIED_MULTIPLE_ASSIGNMENT": len(multiples),
            "WRONG_YEAR_USED_AS_AUTHORITY": len(mauvaise_annee),
            "AUTHORITY_NAMESPACE_VIOLATION": len(espace_viole),
            "binding_method_counts": dict(
                sorted(Counter(lien["binding_method"] for lien in liens).items())
            ),
        },
        "per_manual": resume_par_manuel,
        "multiple_assignment": multiples,
        "wrong_year_citations": mauvaise_annee,
        "authority_namespace_violations": espace_viole,
        "bindings": liens,
    }
    texte = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texte:
            print(f"DIVERGENT : {OUT.relative_to(ROOT)}")
            return 1
        print("Rattachement conforme au generateur.")
        return 0
    OUT.write_text(texte, encoding="utf-8")

    s = charge["summary"]
    print(f"atomes internes                          {s['internal_atoms']:5d}")
    print(f"  rattaches de facon etablie             {s['bound_confirmed']:5d}")
    print(f"  proposes, en attente d'arbitrage       {s['bound_proposed']:5d}")
    print(f"  sans parent officiel trouve            {s['unbound']:5d}")
    print()
    for manuel, r in resume_par_manuel.items():
        print(f"{manuel:>10} {r['authority_ref']}  obligatoires {r['official_mandatory']:4d}"
              f"  rattaches {r['official_mandatory_bound_confirmed']:4d}")
        for nature, stat in r["by_official_kind"].items():
            print(f"             {nature:<22s} {stat['bound_confirmed']:3d} / "
                  f"{stat['mandatory']:3d}")
    print()
    for cle in (
        "INTERNAL_ATOM_WITHOUT_OFFICIAL_PARENT",
        "OFFICIAL_REQUIRED_UNMAPPED",
        "UNJUSTIFIED_MULTIPLE_ASSIGNMENT",
        "WRONG_YEAR_USED_AS_AUTHORITY",
        "AUTHORITY_NAMESPACE_VIOLATION",
    ):
        print(f"{cle} = {s[cle]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
