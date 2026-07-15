"""LOT R — Récolte T0 : identifie et transpose les contenus du dépôt NSI (corpus_nsi/)
couvrant les capacités d'un chapitre du manuel.

Étapes :
1. Charger le contrat du chapitre (capacités visées, via ref_capacite).
2. Parcourir corpus_nsi : manifest.csv si présent (colonnes attendues : path, notion,
   capacites/objectifs, statut), sinon balayage des dossiers de séquences
   (03_progressions/supports/, premiere/, terminale/) avec correspondance lexicale
   entre mots-clés des capacités et frontmatter/nom des fichiers.
3. Pour chaque séquence retenue : copier les 11 fichiers types dans
   chapitres/{CHAP}/_harvest/{sequence}/ , convertir les .md en .tex candidats via
   pandoc + md2nexus.lua (suffixe .candidate.tex — JAMAIS directement dans les
   dossiers de production), recopier python/ et tests/ tels quels.
4. Écrire le rapport de transposition : capacité par capacité, sources trouvées,
   fichiers convertis, statut hérité (needs_review propagé), angles morts.

Le rapport conditionne le gate de sortie du LOT R.
"""
import argparse
import csv
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from common import ROOT, write_json

CORPUS = ROOT / "corpus_nsi"
CANON = ["cours_eleve.md", "trace_ecrite.md", "td.md", "tp.md", "fiche_methode.md",
         "aides_progressives.md", "corrige.md", "guide_professeur.md", "evaluation.md",
         "qcm.json", "projet_associe.md"]
SEQ_ROOTS = ["03_progressions/supports", "premiere/sequences", "terminale/sequences",
             "premiere", "terminale"]
STOP = {"les", "des", "une", "un", "de", "du", "la", "le", "et", "en", "d'un", "d'une", "dans", "par", "sur"}


def keywords(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-zà-ÿ]{4,}", text.lower()) if w not in STOP}


def load_contrat(chap: str) -> dict:
    return yaml.safe_load((ROOT / "chapitres" / chap / "contrat.yaml").read_text(encoding="utf-8"))


def sequences_from_manifest() -> list[dict]:
    manifest = CORPUS / "manifest.csv"
    if not manifest.exists():
        return []
    rows = list(csv.DictReader(manifest.open(encoding="utf-8")))
    out = []
    for r in rows:
        path = r.get("path") or r.get("chemin") or ""
        if path:
            out.append({"dir": CORPUS / Path(path).parent if (CORPUS / path).is_file() else CORPUS / path,
                        "meta": r, "status": r.get("statut") or r.get("status") or "unknown"})
    return out


def sequences_by_scan() -> list[dict]:
    out = []
    for root in SEQ_ROOTS:
        base = CORPUS / root
        if not base.exists():
            continue
        for d in base.rglob("*"):
            if d.is_dir() and any((d / f).exists() for f in CANON):
                out.append({"dir": d, "meta": {"path": str(d.relative_to(CORPUS))},
                            "status": "unknown"})
    # dédoublonner
    seen, uniq = set(), []
    for s in out:
        if s["dir"] not in seen:
            seen.add(s["dir"])
            uniq.append(s)
    return uniq


def score(seq: dict, cap_kw: set[str]) -> float:
    text = str(seq["meta"]) + " " + seq["dir"].name.replace("_", " ")
    for f in ("cours_eleve.md", "trace_ecrite.md"):
        p = seq["dir"] / f
        if p.exists():
            text += " " + p.read_text(encoding="utf-8", errors="replace")[:2500]
    kw = keywords(text)
    return len(kw & cap_kw) / max(1, len(cap_kw))


def convert_md(md: Path, out_tex: Path) -> bool:
    lua = ROOT / "scripts" / "md2nexus.lua"
    proc = subprocess.run(["pandoc", str(md), "-f", "markdown", "-t", "latex",
                           "--lua-filter", str(lua), "-o", str(out_tex)],
                          capture_output=True, text=True)
    return proc.returncode == 0


def harvest(chap: str, threshold: float = 0.18, top: int = 4) -> int:
    contrat = load_contrat(chap)
    chap_dir = ROOT / "chapitres" / chap
    harvest_dir = chap_dir / "_harvest"
    harvest_dir.mkdir(exist_ok=True)

    sequences = sequences_from_manifest() or sequences_by_scan()
    if not sequences:
        print("corpus_nsi vide ou submodule non initialisé — angle mort global déclaré.")
        write_json(chap_dir / "rapport_transposition.json",
                   {"chapitre": chap, "sequences": [], "capacites": {
                       c["code"]: {"sources_T0": [], "angle_mort": "corpus_nsi indisponible"}
                       for c in contrat["capacites"]}})
        return 1

    rapport = {"chapitre": chap, "sequences": [], "capacites": {}}
    retained: dict[Path, dict] = {}
    for cap in contrat["capacites"]:
        cap_kw = keywords(cap["libelle_eleve"] + " " + cap.get("ref_capacite", ""))
        scored = sorted(((score(s, cap_kw), s) for s in sequences), key=lambda x: -x[0])[:top]
        hits = [{"path": str(s["dir"].relative_to(CORPUS)), "score": round(sc, 3),
                 "status": s["status"]} for sc, s in scored if sc >= threshold]
        rapport["capacites"][cap["code"]] = {
            "sources_T0": hits,
            "angle_mort": None if hits else "aucune séquence T0 au-dessus du seuil : génération ex nihilo"}
        for sc, s in scored:
            if sc >= threshold:
                retained[s["dir"]] = s

    converted, failed = 0, 0
    for seq_dir, s in retained.items():
        dest = harvest_dir / seq_dir.name
        dest.mkdir(exist_ok=True)
        entry = {"path": str(seq_dir.relative_to(CORPUS)), "status": s["status"], "fichiers": []}
        for f in CANON:
            src = seq_dir / f
            if not src.exists():
                continue
            shutil.copy2(src, dest / f)
            if f.endswith(".md"):
                ok = convert_md(src, dest / (f[:-3] + ".candidate.tex"))
                converted += ok
                failed += (not ok)
                entry["fichiers"].append({"f": f, "converted": bool(ok)})
            else:
                entry["fichiers"].append({"f": f, "converted": None})
        for sub in ("python", "tests"):
            if (seq_dir / sub).exists():
                shutil.copytree(seq_dir / sub, dest / sub, dirs_exist_ok=True)
                entry["fichiers"].append({"f": sub + "/", "converted": None})
        rapport["sequences"].append(entry)

    rapport["conversion"] = {"ok": converted, "echecs": failed}
    write_json(chap_dir / "rapport_transposition.json", rapport)
    manquants = [c for c, v in rapport["capacites"].items() if v["angle_mort"]]
    print(f"{len(retained)} séquences récoltées, {converted} fichiers convertis "
          f"({failed} échecs pandoc), angles morts : {manquants or 'aucun'}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chap", required=True)
    ap.add_argument("--threshold", type=float, default=0.18)
    args = ap.parse_args()
    sys.exit(harvest(args.chap, args.threshold))
