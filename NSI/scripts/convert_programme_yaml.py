"""Genere referentiel/*.json depuis corpus_nsi/00_programmes_officiels/programme_nsi_2019.yaml.

Le YAML du depot NSI est la source de verite (R7 : le mettre a jour LA-BAS si le
programme a evolue, puis relancer ce script). Tolerant sur la structure : tout item
non resolu part dans referentiel/_a_verifier.json plutot que d'etre invente.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

from common import CORPUS_NSI, ROOT

SRC_CANDIDATES = [
    CORPUS_NSI / "00_programmes_officiels" / "programme_nsi_2019.yaml",
    CORPUS_NSI / "00_programmes_officiels" / "programme_nsi.yaml",
]
NIVEAU_MAP = {"premiere": "1NSI", "première": "1NSI", "terminale": "TNSI"}


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower().replace("é", "e").replace("è", "e"))
    return s.strip("-").upper()[:28]


def main() -> int:
    src = next((p for p in SRC_CANDIDATES if p.exists()), None)
    if src is None:
        print("Programme YAML introuvable dans corpus_nsi/ -- initialiser le lien d'abord.")
        return 1
    data = yaml.safe_load(src.read_text(encoding="utf-8"))
    unresolved, count = [], 0
    ref_dir = ROOT / "referentiel"
    ref_dir.mkdir(exist_ok=True)

    # Structure reelle : programmes: {premiere: [{id, rubrique, contenu, capacite_attendue: [...]}], terminale: [...]}
    programmes = data.get("programmes", data)

    for niveau_key, items in programmes.items():
        niveau = NIVEAU_MAP.get(str(niveau_key).lower())
        if niveau is None:
            if niveau_key not in ("sources", "preuves_minimales"):
                unresolved.append({str(niveau_key): "niveau non reconnu"})
            continue
        if not isinstance(items, list):
            unresolved.append({str(niveau_key): f"attendu list, recu {type(items).__name__}"})
            continue

        # Regrouper par rubrique (theme)
        by_rubrique: dict[str, list[dict]] = defaultdict(list)
        for item in items:
            if not isinstance(item, dict):
                unresolved.append({f"{niveau_key}": str(item)[:120]})
                continue
            rubrique = item.get("rubrique", "inconnu")
            by_rubrique[rubrique].append(item)

        for rubrique, entries in by_rubrique.items():
            theme = slug(rubrique)
            caps = []
            for entry in entries:
                cap_id = entry.get("id", "")
                contenu = entry.get("contenu", "")
                cap_list = entry.get("capacite_attendue") or entry.get("capacites") or []
                if isinstance(cap_list, str):
                    cap_list = [cap_list]
                commentaire = entry.get("commentaire_officiel", "")
                for lib in cap_list:
                    caps.append({
                        "id": cap_id if cap_id else f"{niveau}-{theme}-C{len(caps)+1}",
                        "contenu_bo": str(contenu),
                        "libelle_bo": str(lib),
                        "libelle_eleve": "",
                        "commentaire_officiel": str(commentaire),
                        "demonstration_exigible": False,
                    })

            if caps:
                out = ref_dir / f"capacites_{niveau}_{theme}.json"
                out.write_text(json.dumps({
                    "niveau": niveau, "theme": theme,
                    "bo_reference": "Programme NSI, BO special n1 du 22 janvier 2019 -- a re-verifier contre le B.O. en vigueur (R7)",
                    "source_yaml": str(src),
                    "capacites": caps,
                }, ensure_ascii=False, indent=2), encoding="utf-8")
                count += len(caps)

    if unresolved:
        (ref_dir / "_a_verifier.json").write_text(
            json.dumps(unresolved, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{count} capacites generees ; {len(unresolved)} items non resolus (referentiel/_a_verifier.json).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
