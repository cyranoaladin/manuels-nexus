"""Assemblage (R5/F06) : génère le .tex maître d'un chapitre depuis les objets,
dans l'ordre des 9 temps du gabarit, puis compile (pdflatex ×2).

Déclinaisons : --variant complet|methodes|parcours1|remediation
"""
import argparse
import subprocess
import sys
from pathlib import Path

from common import ROOT

ORDER = [  # les 9 temps du gabarit (docs/01 Partie 3)
    ("cours", "00_ouverture"), ("cours", "01_diagnostic"), ("cours", "02_activites"),
    ("cours", "1*"), ("methodes", "*"), ("exercices", "*"),
    ("cours", "07_td*"), ("qcm", "*"), ("evaluations", "*"), ("remediation", "*"),
]


def collect(chap_dir: Path, variant: str) -> list[Path]:
    if variant == "methodes":
        return sorted((chap_dir / "methodes").glob("*.tex"))
    if variant == "remediation":
        return sorted((chap_dir / "remediation").glob("*.tex"))
    files = []
    for sub, pat in ORDER:
        files += sorted((chap_dir / sub).glob(f"{pat}.tex" if not pat.endswith("*") else pat + ".tex"))
    # dédoublonner en conservant l'ordre
    seen, out = set(), []
    for f in files:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def main(chap: str, variant: str) -> int:
    chap_dir = ROOT / "chapitres" / chap
    build = ROOT / "build" / chap
    build.mkdir(parents=True, exist_ok=True)
    files = collect(chap_dir, variant)
    if not files:
        print("Aucun objet à assembler.")
        return 1
    inputs = "\n".join(f"\\input{{{f.relative_to(ROOT)}}}" for f in files)
    master = (ROOT / "gabarits" / "chapitre_master.tex").read_text(encoding="utf-8")
    master = master.replace("%%CONTENT%%", inputs).replace("%%CHAP%%", chap)
    tex_path = build / f"{chap}_{variant}.tex"
    tex_path.write_text(master, encoding="utf-8")
    for _ in range(2):
        proc = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
             f"-output-directory={build}", str(tex_path)],
            capture_output=True, text=True, cwd=ROOT, errors="replace")
    if proc.returncode != 0:
        print(proc.stdout[-3000:])
        return 1
    print(f"PDF : {build / (tex_path.stem + '.pdf')}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chap", required=True)
    ap.add_argument("--variant", default="complet",
                    choices=["complet", "methodes", "parcours1", "remediation"])
    args = ap.parse_args()
    sys.exit(main(args.chap, args.variant))
