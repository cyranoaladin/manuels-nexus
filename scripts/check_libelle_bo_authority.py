#!/usr/bin/env python3
"""Interdit d'invoquer `libelle_bo` comme s'il portait le texte du BO.

Le champ s'appelle `libelle_bo` et son nom vaut certificat d'authenticite. La
comparaison avec les programmes montre qu'il n'est le plus souvent qu'une
reformulation pedagogique : sur 313 capacites internes, la moitie environ
s'ecarte du texte officiel. Tant que ce nom survit, quelqu'un finira par citer
sa valeur comme preuve devant le programme.

Ce controle n'interdit pas le champ -- le supprimer casserait quinze
consommateurs pour rien. Il interdit son USAGE comme autorite : aucun artefact
publie ne doit exposer, sous un nom qui promet le Bulletin officiel, un texte
qui n'en vient pas. Le texte officiel exact vit dans l'inventaire, sous
`official_wording`, lu du BO et de lui seul.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_official_programme_binding import REFERENTIELS, forme_typographique

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
OUT = AUDIT / "LIBELLE_BO_AUTHORITY_GATE.json"

#: Noms de champs qui promettent le texte du Bulletin officiel a leur lecteur
#: alors que rien ne garantit qu'ils le portent.
#:
#: `official_wording` n'y figure pas : dans les artefacts produits par cette
#: chaine, il est recopie de l'inventaire officiel et vient donc du BO par
#: construction. Ce que traque ce controle est le champ dont le NOM sert de
#: certificat sans qu'aucun producteur ne l'ait verifie.
CHAMPS_D_AUTORITE = ("libelle_bo", "bo_wording", "texte_bo")


def _verbatims() -> set[str]:
    """Tous les libelles inventories, applicables ou non.

    Un libelle du programme de 2019 vient bien du Bulletin officiel, meme s'il
    ne regit plus l'edition : le differentiel doit pouvoir le citer. Ce que ce
    controle traque est le libelle qui ne vient d'aucun programme -- savoir si
    le bon millesime est invoque releve d'un autre controle.
    """
    index = json.loads(
        (ROOT / "audit" / "OFFICIAL_PROGRAMME_INVENTORY.json").read_text(
            encoding="utf-8"
        )
    )
    formes: set[str] = set()
    for entree in index["documents"]:
        charge = json.loads(
            (ROOT / entree["inventory_path"]).read_text(encoding="utf-8")
        )
        formes.update(
            forme_typographique(i["official_wording"]) for i in charge["items"]
        )
    return formes


def _parcourir(noeud: Any, chemin: str = "") -> list[tuple[str, str, str]]:
    """Releve les champs d'autorite qui ne s'annoncent pas comme incertains.

    Un objet qui porte `libelle_bo_is_verbatim` a fait le travail : il dit
    lui-meme si son libelle vient du BO. Ce qui reste a signaler, c'est le
    champ dont le nom promet le Bulletin officiel sans que rien, alentour, ne
    vienne relativiser cette promesse.
    """
    trouves: list[tuple[str, str, str]] = []
    if isinstance(noeud, dict):
        declare = "libelle_bo_is_verbatim" in noeud
        for cle, valeur in noeud.items():
            if (
                not declare
                and cle in CHAMPS_D_AUTORITE
                and isinstance(valeur, str)
                and valeur.strip()
            ):
                trouves.append((f"{chemin}/{cle}", cle, valeur))
            trouves.extend(_parcourir(valeur, f"{chemin}/{cle}"))
    elif isinstance(noeud, list):
        for rang, valeur in enumerate(noeud):
            trouves.extend(_parcourir(valeur, f"{chemin}[{rang}]"))
    return trouves


#: Les archives d'audit conservent l'etat passe du depot ; leur corriger un
#: champ reecrirait la preuve qu'elles constituent. Elles sont donc tolerees,
#: mais seulement si elles annoncent elles-memes que leurs libelles restent a
#: verifier -- sans quoi il suffirait de deposer un fichier dans `historique/`
#: pour echapper au controle.
def _archive_declaree(chemin: Path, charge: Any) -> bool:
    if "historique" not in chemin.parts:
        return False
    note = charge.get("note", "") if isinstance(charge, dict) else ""
    return "re-verifier" in note.lower() or "re-verifie" in note.lower()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    verbatims = _verbatims()
    manquements: list[dict[str, str]] = []
    archives: list[str] = []
    for chemin in sorted(AUDIT.rglob("*.json")):
        if chemin == OUT:
            continue
        try:
            charge = json.loads(chemin.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if _archive_declaree(chemin, charge):
            archives.append(str(chemin.relative_to(ROOT)))
            continue
        for pointeur, cle, valeur in _parcourir(charge):
            if forme_typographique(valeur) in verbatims:
                continue
            manquements.append({
                "artifact": str(chemin.relative_to(ROOT)),
                "pointer": pointeur,
                "field": cle,
                "value": valeur[:180],
                "reason": (
                    "champ promettant le texte du Bulletin officiel alors que "
                    "sa valeur ne figure dans aucun programme applicable"
                ),
            })

    # Les referentiels eux-memes conservent `libelle_bo` pour compatibilite,
    # mais chaque capacite doit dire si ce libelle est reellement verbatim :
    # sans ce drapeau, le nom du champ reste la seule indication, et il ment.
    sans_drapeau: list[str] = []
    for dossier in REFERENTIELS:
        for chemin in sorted(dossier.glob("capacites_*.json")):
            charge = json.loads(chemin.read_text(encoding="utf-8"))
            for capacite in charge.get("capacites", []):
                if "libelle_bo" in capacite and (
                    "libelle_bo_is_verbatim" not in capacite
                    or "libelle_interne" not in capacite
                ):
                    sans_drapeau.append(f"{chemin.relative_to(ROOT)}::{capacite['id']}")

    charge_sortie = {
        "artifact_type": "libelle_bo_authority_gate",
        "schema_version": 1,
        "generated_by": "scripts/check_libelle_bo_authority.py",
        "checked_field_names": list(CHAMPS_D_AUTORITE),
        "summary": {
            "MISLEADING_LIBELLE_BO_FIELDS_USED_AS_AUTHORITY": len(manquements),
            "REFERENTIAL_CAPACITIES_WITHOUT_VERBATIM_FLAG": len(sans_drapeau),
            "HISTORICAL_ARCHIVES_DECLARING_THEIR_OWN_UNCERTAINTY": len(archives),
            "LIBELLE_BO_AUTHORITY_GATE": (
                "PASS" if not manquements and not sans_drapeau else "FAIL"
            ),
        },
        "historical_archives_accepted": sorted(archives),
        "violations": manquements,
        "capacities_without_verbatim_flag": sans_drapeau,
    }
    texte = json.dumps(charge_sortie, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texte:
            print(f"DIVERGENT : {OUT.relative_to(ROOT)}")
            return 1
        print("Barriere libelle_bo conforme.")
        return 0
    OUT.write_text(texte, encoding="utf-8")
    resume = charge_sortie["summary"]
    assert isinstance(resume, dict)
    for cle, valeur in resume.items():
        print(f"{cle} = {valeur}")
    for m in manquements[:10]:
        print(f"  {m['artifact']} {m['pointer']}\n      {m['value'][:110]}")
    return 0 if not manquements and not sans_drapeau else 1


if __name__ == "__main__":
    sys.exit(main())
