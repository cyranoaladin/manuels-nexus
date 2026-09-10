#!/usr/bin/env python3
"""Retirer une approbation que le contenu ne porte plus.

Une approbation suit un contenu, pas un chemin de fichier. Quand le texte
visible a change apres l'approbation, le champ `status: approved` affirme une
chose fausse. Ce script le retire.

Il ne fabrique aucun humain : il ne repose sur AUCUNE nouvelle approbation. Il
fait retomber le statut sur `needs_review` -- l'objet attend une relecture --
et inscrit `approval_state: STALE_AFTER_SEMANTIC_EDIT`, pour que la perte
d'une approbation acquise reste visible comme telle et ne se confonde pas avec
un objet qui n'en a jamais eu.

La ligne META est reecrite au plus juste : seule la paire de statut est
touchee, le reste de la ligne est conserve caractere pour caractere.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from content_approval import (  # noqa: E402
    APPROBATION_PERIMEE,
    ROOT,
    STATUT_APRES_INVALIDATION,
)

RECUS = ROOT / "audit" / "CONTENT_APPROVAL_RECEIPTS.json"
STATUT = re.compile(r'("status"(\s*):(\s*))"approved"')


def reecrire(ligne_meta: str) -> str:
    correspondance = STATUT.search(ligne_meta)
    if correspondance is None:
        raise ValueError("ligne META sans statut approuve")
    avant_deux_points, apres_deux_points = correspondance.group(2), correspondance.group(3)
    remplacement = (
        f'"status"{avant_deux_points}:{apres_deux_points}"{STATUT_APRES_INVALIDATION}", '
        f'"approval_state"{avant_deux_points}:{apres_deux_points}"{APPROBATION_PERIMEE}"'
    )
    return STATUT.sub(lambda _: remplacement, ligne_meta, count=1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    recus = json.loads(RECUS.read_text(encoding="utf-8"))
    perimes = [
        r for r in recus["receipts"]
        if r["receipt_state"] == "STALE_AFTER_SEMANTIC_EDIT"
    ]
    if not perimes:
        print("Aucune approbation perimee.")
        return 0
    for recu in perimes:
        chemin = ROOT / recu["path"]
        texte = chemin.read_text(encoding="utf-8")
        premiere, reste = texte.split("\n", 1)
        nouvelle = reecrire(premiere)
        charge = json.loads(nouvelle[len("% META:"):].strip())
        assert charge["status"] == STATUT_APRES_INVALIDATION
        assert charge["approval_state"] == APPROBATION_PERIMEE
        if args.check:
            print(f"A INVALIDER : {recu['path']}")
            continue
        chemin.write_text(nouvelle + "\n" + reste, encoding="utf-8")
        print(f"approbation retiree : {recu['object_id']}")
    return 1 if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
