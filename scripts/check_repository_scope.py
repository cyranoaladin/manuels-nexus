#!/usr/bin/env python3
"""Gate de perimetre : ce depot porte SIX manuels, et rien d'autre.

Le 10 septembre 2026, un `git add -A` a fait entrer 58 Mo de documentation et
de PDF HGGSP dans l'arbre actif, par un repertoire `HLP/` apparu a la racine.
Aucun script, test ou manifeste des six manuels n'en dependait : c'etait une
collection etrangere, versionnee par accident.

Le gate refuse desormais qu'une collection etrangere soit SUIVIE par Git. Il ne
regarde pas le disque : un dossier non suivi ne gene personne, et l'instance
HGGSP travaille dans son propre chantier, qu'il ne faut pas toucher.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: Les six manuels canoniques. Toute autre collection est etrangere.
CANONICAL_MANUALS = (
    "1SPE", "TSPE_2026_2027", "TCOMPL", "TEXPERTES", "1NSI", "TNSI",
)

#: Racines interdites a l'index. Une decision humaine explicite peut en retirer
#: une, mais elle doit alors etre inscrite ici, pas contournee.
FOREIGN_COLLECTION_ROOTS = ("HLP", "HGGSP", "_SAUVEGARDES_HGGSP")

#: Prefixes interdits, pour les repertoires horodates.
FOREIGN_COLLECTION_PREFIXES = ("AUDIT_HGGSP_",)


def tracked_paths(root: Path = ROOT) -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True
    )
    return [line for line in completed.stdout.splitlines() if line]


def foreign_tracked(root: Path = ROOT) -> dict[str, list[str]]:
    """Fichiers suivis appartenant a une collection etrangere, par racine."""
    trouve: dict[str, list[str]] = {}
    for path in tracked_paths(root):
        premier = path.split("/", 1)[0]
        etrangere = premier in FOREIGN_COLLECTION_ROOTS or any(
            premier.startswith(prefixe) for prefixe in FOREIGN_COLLECTION_PREFIXES
        )
        if etrangere:
            trouve.setdefault(premier, []).append(path)
    return trouve


def is_out_of_scope(path: Path | str, root: Path = ROOT) -> bool:
    """True si un chemin appartient a une collection etrangere.

    Filtre PARTAGE par tous les balayages disque de cette instance. HLP et
    HGGSP restent presents sur le disque -- c'est intentionnel, ils sont pris
    en charge par une autre instance -- mais aucun inventaire, aucun registre
    et aucun gate de Maths/NSI ne doit les lire : ils produiraient de faux
    diagnostics et parcourraient des centaines de mega-octets sans objet.

    Mesure du 10 septembre 2026 : sans ce filtre, un `rglob('*.json')` depuis
    la racine ramenait 129 fichiers de collections etrangeres.
    """
    chemin = Path(path)
    try:
        parts = chemin.relative_to(root).parts
    except ValueError:
        parts = chemin.parts
    if not parts:
        return False
    premier = parts[0]
    return premier in FOREIGN_COLLECTION_ROOTS or any(
        premier.startswith(prefixe) for prefixe in FOREIGN_COLLECTION_PREFIXES
    )


def in_scope(paths, root: Path = ROOT):
    """Filtre un iterable de chemins sur le perimetre Maths/NSI."""
    return [chemin for chemin in paths if not is_out_of_scope(chemin, root)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)

    trouve = foreign_tracked(args.root)
    total = sum(len(v) for v in trouve.values())
    print(f"FOREIGN_COLLECTIONS_IN_ACTIVE_TREE = {total}")
    if not trouve:
        print("REPOSITORY_SCOPE_GATE = PASS")
        return 0
    for racine, fichiers in sorted(trouve.items()):
        print(f"  {racine}/ : {len(fichiers)} fichier(s) suivi(s)", file=sys.stderr)
        for fichier in fichiers[:5]:
            print(f"      {fichier}", file=sys.stderr)
        if len(fichiers) > 5:
            print(f"      … et {len(fichiers) - 5} autres", file=sys.stderr)
    print("REPOSITORY_SCOPE_GATE = FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
