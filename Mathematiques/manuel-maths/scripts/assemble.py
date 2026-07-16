"""Assemblage (R5/F06) : génère le .tex maître d'un chapitre depuis les objets,
dans l'ordre des 9 temps du gabarit, puis compile (LuaLaTeX ×2).

Déclinaisons : --variant complet|methodes|parcours1|remediation
"""
import argparse
import subprocess
import sys
from pathlib import Path

import yaml

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
        candidats = sorted((chap_dir / sub).glob(f"{pat}.tex" if not pat.endswith("*") else pat + ".tex"))
        if sub == "exercices":
            files += [f for f in candidats if not f.name.endswith("-CDP.tex")]
            files += [f for f in candidats if f.name.endswith("-CDP.tex")]
        else:
            files += candidats
    # dédoublonner en conservant l'ordre
    seen, out = set(), []
    for f in files:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def ouverture_depuis_contrat(chap_dir: Path) -> str:
    """Construit l'ouverture normalisée à partir du contrat du chapitre."""
    contrat = yaml.safe_load((chap_dir / "contrat.yaml").read_text(encoding="utf-8"))
    capacites = "\n".join(
        f"\\item \\textbf{{{capacite['code']}}} — {capacite['libelle_eleve']}"
        for capacite in contrat["capacites"]
    )
    temps = contrat.get("temps_estime_h", {})
    temps_tex = (
        f"\\parcoursUn~{temps.get('parcours1', '—')} h \\quad "
        f"\\parcoursDeux~{temps.get('parcours2', '—')} h \\quad "
        f"\\parcoursTrois~{temps.get('parcours3', '—')} h"
    )
    accroche = contrat.get("situation_accroche", "Situation d'accroche à découvrir dans le TD fil rouge.")
    return (
        f"\\ouverturechapitre{{{contrat['titre']}}}{{\\begin{{itemize}}\n{capacites}\n\\end{{itemize}}}}"
        f"{{{accroche}}}{{{temps_tex}}}\n\\clearpage"
    )


def main(chap: str, variant: str) -> int:
    chap_dir = ROOT / "chapitres" / chap
    build = ROOT / "build" / chap
    build.mkdir(parents=True, exist_ok=True)
    files = collect(chap_dir, variant)
    if not files:
        print("Aucun objet à assembler.")
        return 1
    inputs = "\n".join(f"\\input{{{f.relative_to(ROOT)}}}" for f in files)
    ouverture = ouverture_depuis_contrat(chap_dir) if variant == "complet" else ""
    master = (ROOT / "gabarits" / "chapitre_master.tex").read_text(encoding="utf-8")
    master = (master.replace("%%CONTENT%%", inputs)
                    .replace("%%OPENING%%", ouverture)
                    .replace("%%CHAP%%", chap))
    tex_path = build / f"{chap}_{variant}.tex"
    tex_path.write_text(master, encoding="utf-8")
    for _ in range(2):
        proc = subprocess.run(
            ["lualatex", "-interaction=nonstopmode", "-halt-on-error",
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
