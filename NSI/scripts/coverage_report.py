"""Diagnostic historique F01/F05, explicitement non autoritaire.

La vérité de release est `scripts/build_true_pedagogical_coverage.py`, qui
consomme aussi le ledger de clones et l'héritage EX/CO. Ce rapport conserve
uniquement une vue de travail par parcours et ne peut jamais déclarer READY.
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

from common import ROOT

REPOSITORY_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "scripts/capacity_identity.py").is_file()
)
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))
from scripts.capacity_identity import (  # noqa: E402
    AmbiguousCapacityIdentity,
    CapacityIdentityResolver,
    PREREQUISITE,
    UnresolvedCapacityIdentity,
)

META = re.compile(r"% META: (\{.*\})")
AUTHORITATIVE = False


def load_meta(tex: Path) -> dict | None:
    m = META.search(tex.read_text(encoding="utf-8"))
    return json.loads(m.group(1)) if m else None


def collect_coverage(
    chap: str,
    chap_dir: Path,
    resolver: CapacityIdentityResolver,
) -> dict:
    caps = [identity.local_code for identity in resolver.capacities_of(chap)]
    matrix = defaultdict(int)          # (cap, parcours) -> nb exercices
    have = defaultdict(set)            # cap -> {types d'objets présents}
    for sub in ("cours", "methodes", "exercices", "corriges", "remediation"):
        for tex in (chap_dir / sub).glob("*"):
            meta = load_meta(tex) if tex.suffix == ".tex" else None
            if not meta:
                continue
            for cap in resolver.resolve_meta_codes(chap, meta):
                have[cap].add(sub)
                if sub == "exercices" and meta.get("parcours"):
                    matrix[(cap, meta["parcours"])] += 1
    qcm_paths = sorted((chap_dir / "qcm").glob("*-QCM.json"))
    if len(qcm_paths) > 1:
        raise ValueError(f"{chap}: MULTIPLE_QCM_SOURCES")
    for qcm_path in qcm_paths:
        document = json.loads(qcm_path.read_text(encoding="utf-8"))
        if document.get("chapitre") != chap:
            raise ValueError(f"{qcm_path}: chapitre QCM incoherent")
        for question in document.get("questions") or []:
            resolution = resolver.resolve(chap, question.get("capacite"))
            if resolution.rule == PREREQUISITE:
                raise UnresolvedCapacityIdentity(
                    f"{chap}/{question.get('id')}: prerequis utilise comme capacite QCM"
                )
            have[resolution.identity.local_code].add("qcm")
    return {"caps": caps, "matrix": matrix, "have": have}


def report(chap: str) -> int:
    chap_dir = ROOT / "chapitres" / chap
    resolver = CapacityIdentityResolver.from_corpora()
    coverage = collect_coverage(chap, chap_dir, resolver)
    caps = coverage["caps"]
    matrix = coverage["matrix"]
    have = coverage["have"]

    print("NON_AUTHORITATIVE_LEGACY_DIAGNOSTIC — utiliser TRUE_PEDAGOGICAL_COVERAGE")
    print(f"\n=== Couverture indicative {chap} ===")
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
        print("\nAucun manque indicatif ; aucun verdict READY n'est émis.")
    return max(1, len(missing))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chap", required=True)
    args = ap.parse_args()
    sys.exit(1 if report(args.chap) else 0)
