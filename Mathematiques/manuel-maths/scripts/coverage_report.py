"""Rapport de couverture (F01/F05) : matrice capacités × parcours + objets manquants.

Fonctionne sans base : lit contrat.yaml + les fichiers du chapitre (convention de nommage :
1SPE-SUITES-EX-###.tex contenant un en-tête `% META: {json}` conforme au schéma exercice).
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

from common import ROOT

META = re.compile(r"% META: (\{.*\})")


def load_meta(tex: Path) -> dict | None:
    m = META.search(tex.read_text(encoding="utf-8"))
    return json.loads(m.group(1)) if m else None


def report(chap: str) -> int:
    chap_dir = ROOT / "chapitres" / chap
    contrat = yaml.safe_load((chap_dir / "contrat.yaml").read_text(encoding="utf-8"))
    caps = [c["code"] for c in contrat["capacites"]]

    matrix = defaultdict(int)          # (cap, parcours) -> nb exercices
    have = defaultdict(set)            # cap -> {types d'objets présents}
    for sub in ("cours", "methodes", "exercices", "corriges", "qcm", "remediation"):
        for tex in (chap_dir / sub).glob("*"):
            meta = load_meta(tex) if tex.suffix == ".tex" else None
            if not meta:
                continue
            for cap in meta.get("capacites_codes", meta.get("capacites", [])):
                cap = cap.split("-")[-1] if cap.startswith(chap) else cap
                have[cap].add(sub)
                if sub == "exercices" and meta.get("parcours"):
                    matrix[(cap, meta["parcours"])] += 1

    print(f"\n=== Couverture {chap} ===")
    print(f"{'Capacité':10} {'◆':>4} {'◆◆':>4} {'◆◆◆':>4}  cours méth. qcm reméd.")
    missing = []
    for cap in caps:
        row = [matrix[(cap, p)] for p in (1, 2, 3)]
        flags = ["oui" if t in have[cap] else "NON"
                 for t in ("cours", "methodes", "qcm", "remediation")]
        print(f"{cap:10} {row[0]:>4} {row[1]:>4} {row[2]:>4}  {flags[0]:>5} {flags[1]:>5} {flags[2]:>3} {flags[3]:>6}")
        for p, n in zip((1, 2, 3), row):
            if n < 2:
                missing.append(f"{cap} parcours {p}: {n}/2 exercices")
        missing += [f"{cap}: {t} manquant" for t, f in
                    zip(("cours", "methodes", "qcm", "remediation"), flags) if f == "NON"]
    if missing:
        print("\nManquants (F01) :")
        for m in missing:
            print(f"  - {m}")
    else:
        print("\nCouverture complète : F01 satisfaite.")
    return len(missing)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chap", required=True)
    args = ap.parse_args()
    sys.exit(1 if report(args.chap) else 0)
