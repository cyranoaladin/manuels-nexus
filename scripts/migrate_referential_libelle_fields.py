#!/usr/bin/env python3
"""Deprecie `libelle_bo`, dont le nom affirme ce qui est generalement faux.

Le champ s'appelle `libelle_bo` et laisse donc croire qu'il porte le texte du
Bulletin officiel. La comparaison avec les programmes reels montre qu'il n'en
est le plus souvent qu'une reformulation pedagogique -- et que le referentiel
decoupe parfois en deux atomes ce que le programme enonce en une capacite. Un
champ dont le nom vaut certificat d'authenticite ne peut pas rester tel quel :
il finirait par etre cite comme preuve officielle.

La migration ne casse aucun consommateur. `libelle_bo` demeure, a l'identique,
et deux champs viennent l'encadrer :

  libelle_interne         la formulation pedagogique du projet, sous son vrai nom
  libelle_bo_is_verbatim  faux des que le texte s'ecarte du programme applicable

Le texte officiel exact, lui, ne vit pas ici : il vit dans l'inventaire
officiel, sous `official_wording`, ou il est lu du BO et de lui seul.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_official_programme_binding import (
    REFERENTIELS,
    charger_officiels,
    forme_typographique,
    normalise,
)

ROOT = Path(__file__).resolve().parents[1]

NOTE = (
    "Le champ `libelle_bo` est deprecie : son nom affirme un texte officiel "
    "qu'il ne porte pas dans la plupart des cas. Utiliser `libelle_interne` "
    "pour la formulation du projet, et `official_wording` de "
    "audit/OFFICIAL_PROGRAMME_INVENTORY.json pour le texte du BO. "
    "`libelle_bo_is_verbatim` dit, atome par atome, si les deux coincident."
)


def migrer(charge: dict[str, Any], officiels: list[dict[str, Any]]) -> bool:
    """Ajoute les deux champs. Retourne vrai si le fichier a change."""
    formes = {forme_typographique(i["official_wording"]) for i in officiels}
    modifie = False
    for capacite in charge.get("capacites", []):
        libelle = normalise(capacite.get("libelle_bo", ""))
        verbatim = bool(libelle) and forme_typographique(libelle) in formes
        if capacite.get("libelle_interne") != capacite.get("libelle_bo", ""):
            capacite["libelle_interne"] = capacite.get("libelle_bo", "")
            modifie = True
        if capacite.get("libelle_bo_is_verbatim") is not verbatim:
            capacite["libelle_bo_is_verbatim"] = verbatim
            modifie = True
    if charge.get("libelle_bo_status") != NOTE:
        charge["libelle_bo_status"] = NOTE
        modifie = True
    return modifie


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    officiels, _ = charger_officiels()
    divergents: list[str] = []
    total = verbatim = 0
    for dossier in REFERENTIELS:
        for chemin in sorted(dossier.glob("capacites_*.json")):
            charge = json.loads(chemin.read_text(encoding="utf-8"))
            items = officiels.get(charge.get("niveau") or "", [])
            migrer(charge, items)
            total += len(charge.get("capacites", []))
            verbatim += sum(
                1 for c in charge.get("capacites", []) if c["libelle_bo_is_verbatim"]
            )
            texte = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
            if chemin.read_text(encoding="utf-8") != texte:
                if args.check:
                    divergents.append(str(chemin.relative_to(ROOT)))
                else:
                    chemin.write_text(texte, encoding="utf-8")

    if args.check:
        if divergents:
            print("NON MIGRE :", *divergents, sep="\n  ")
            return 1
        print("Referentiels migres et a jour.")
        return 0
    print(f"capacites internes                 {total}")
    print(f"  dont libelle_bo reellement verbatim {verbatim}")
    print(f"  dont le nom du champ induit en erreur {total - verbatim}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
