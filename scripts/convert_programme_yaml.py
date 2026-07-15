"""Génère referentiel/*.json depuis corpus_nsi/00_programmes_officiels/programme_nsi_2019.yaml.

Le YAML du dépôt NSI est la source de vérité (R7 : le mettre à jour LÀ-BAS si le
programme a évolué, puis relancer ce script). Tolérant sur la structure : cherche
des listes de capacités/notions sous les clés usuelles ; tout item non résolu part
dans referentiel/_a_verifier.json plutôt que d'être inventé.
"""
import json
import re
import sys
from pathlib import Path

import yaml

from common import ROOT

SRC_CANDIDATES = [
    ROOT / "corpus_nsi" / "00_programmes_officiels" / "programme_nsi_2019.yaml",
    ROOT / "corpus_nsi" / "00_programmes_officiels" / "programme_nsi.yaml",
]
NIVEAU_MAP = {"premiere": "1NSI", "première": "1NSI", "terminale": "TNSI"}


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower().replace("é", "e").replace("è", "e"))
    return s.strip("-").upper()[:28]


def main() -> int:
    src = next((p for p in SRC_CANDIDATES if p.exists()), None)
    if src is None:
        print("Programme YAML introuvable dans corpus_nsi/ — initialiser le submodule d'abord.")
        return 1
    data = yaml.safe_load(src.read_text(encoding="utf-8"))
    unresolved, count = [], 0
    # Structure attendue (souple) : {niveau: {domaine/theme: [{contenu, capacites: [...]}]}}
    for niveau_key, domaines in (data.items() if isinstance(data, dict) else []):
        niveau = NIVEAU_MAP.get(str(niveau_key).lower())
        if niveau is None or not isinstance(domaines, dict):
            unresolved.append({niveau_key: type(domaines).__name__})
            continue
        for dom, items in domaines.items():
            theme = slug(str(dom))
            caps = []
            for i, item in enumerate(items if isinstance(items, list) else [items]):
                if isinstance(item, dict):
                    libs = item.get("capacites") or item.get("capacités") or []
                    contenu = item.get("contenu") or item.get("notion") or ""
                    for j, lib in enumerate(libs if isinstance(libs, list) else [libs]):
                        caps.append({
                            "id": f"{niveau}-{theme}-C{len(caps)+1}",
                            "contenu_bo": str(contenu),
                            "libelle_bo": str(lib),
                            "libelle_eleve": "",  # complété par l'agent au LOT 0 (langage élève)
                            "demonstration_exigible": False,
                        })
                else:
                    unresolved.append({f"{niveau}/{dom}": str(item)[:120]})
            if caps:
                out = ROOT / "referentiel" / f"capacites_{niveau}_{theme}.json"
                out.write_text(json.dumps({
                    "niveau": niveau, "theme": theme,
                    "bo_reference": "Programme NSI, BO spécial n°1 du 22 janvier 2019 — à re-vérifier contre le B.O. en vigueur (R7)",
                    "source_yaml": str(src.relative_to(ROOT)),
                    "capacites": caps}, ensure_ascii=False, indent=2), encoding="utf-8")
                count += len(caps)
    if unresolved:
        (ROOT / "referentiel" / "_a_verifier.json").write_text(
            json.dumps(unresolved, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{count} capacités générées ; {len(unresolved)} items non résolus (referentiel/_a_verifier.json).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
