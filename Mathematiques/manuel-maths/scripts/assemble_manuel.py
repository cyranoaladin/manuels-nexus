"""Assemblage du manuel complet 1SPE : transversal + 10 chapitres.

Variantes :
  --variant professeur  (tout : cours, exercices, corriges, evaluations, baremes)
  --variant eleve       (sans corriges ni baremes d'evaluation)
"""
import argparse
import subprocess
import sys
from pathlib import Path

import yaml

from common import ROOT
from pdf_integrity import verify_pdf

CHAPITRES = [
    "1SPE-SUITES",
    "1SPE-SECOND-DEGRE",
    "1SPE-DERIVATION-LOCAL",
    "1SPE-DERIVATION-GLOBAL",
    "1SPE-EXPONENTIELLE",
    "1SPE-TRIGONOMETRIE",
    "1SPE-PRODUIT-SCALAIRE",
    "1SPE-GEOMETRIE-REPEREE",
    "1SPE-PROBA-COND",
    "1SPE-VARIABLES-ALEATOIRES",
]

ORDER = [
    ("cours", "00_ouverture"), ("cours", "01_diagnostic"), ("cours", "02_activites"),
    ("cours", "1*"), ("methodes", "*"), ("exercices", "*"),
    ("cours", "07_td*"), ("qcm", "*"), ("evaluations", "*"), ("remediation", "*"),
]

ELEVE_EXCLUDES = {"corriges", "evaluations"}


def collect_chapter(chap_dir: Path, variant: str) -> list[Path]:
    files = []
    for sub, pat in ORDER:
        if variant == "eleve" and sub in ELEVE_EXCLUDES:
            continue
        candidats = sorted((chap_dir / sub).glob(f"{pat}.tex" if not pat.endswith("*") else pat + ".tex"))
        if sub == "exercices":
            files += [f for f in candidats if not f.name.endswith("-CDP.tex")]
            files += [f for f in candidats if f.name.endswith("-CDP.tex")]
        elif sub == "evaluations" and variant == "eleve":
            files += [f for f in candidats if "corrige" not in f.name]
        else:
            files += candidats
    seen, out = set(), []
    for f in files:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def ouverture_depuis_contrat(chap_dir: Path) -> str:
    contrat = yaml.safe_load((chap_dir / "contrat.yaml").read_text(encoding="utf-8"))
    capacites = "\n".join(
        f"\\item \\textbf{{{c['code']}}} --- {c['libelle_eleve']}"
        for c in contrat["capacites"]
    )
    temps = contrat.get("temps_estime_h", {})
    temps_tex = (
        f"\\parcoursUn~{temps.get('parcours1', '---')} h \\quad "
        f"\\parcoursDeux~{temps.get('parcours2', '---')} h \\quad "
        f"\\parcoursTrois~{temps.get('parcours3', '---')} h"
    )
    accroche = contrat.get("situation_accroche", "")
    return (
        f"\\ouverturechapitre{{{contrat['titre']}}}{{\\begin{{itemize}}\n{capacites}\n\\end{{itemize}}}}"
        f"{{{accroche}}}{{{temps_tex}}}\n\\clearpage"
    )


def main(variant: str) -> int:
    build = ROOT / "build" / "MANUEL_1SPE"
    build.mkdir(parents=True, exist_ok=True)

    parts = []

    # Transversal front matter
    parts.append("\\input{transversal/page_de_garde}")
    parts.append("\\clearpage")
    parts.append("\\input{transversal/avant_propos}")
    parts.append("\\clearpage")
    parts.append("\\input{transversal/mode_emploi}")
    parts.append("\\clearpage")
    parts.append("\\tableofcontents")
    parts.append("\\clearpage")

    # Chapters
    for chap in CHAPITRES:
        chap_dir = ROOT / "chapitres" / chap
        if not chap_dir.exists():
            print(f"SKIP {chap} (directory not found)")
            continue

        opening = ouverture_depuis_contrat(chap_dir)
        files = collect_chapter(chap_dir, variant)
        inputs = "\n".join(f"\\input{{{f.relative_to(ROOT)}}}" for f in files)
        parts.append(f"% ===== {chap} =====")
        parts.append(opening)
        parts.append(inputs)

    # Back matter
    parts.append("\\appendix")
    parts.append("\\clearpage")
    parts.append("\\input{transversal/formulaire}")
    parts.append("\\clearpage")
    parts.append("\\input{transversal/memo_python}")
    parts.append("\\clearpage")
    parts.append("\\input{transversal/index_capacites}")

    content = "\n".join(parts)

    titre_var = "professeur" if variant == "professeur" else "eleve"
    master = f"""% Manuel 1SPE — variante {titre_var}
% Assemble par scripts/assemble_manuel.py
\\documentclass{{gabarits/nexus-manuel}}
\\matiere{{Mathematiques}}\\niveau{{Premiere specialite}}
\\title{{Manuel de mathematiques — Premiere specialite — Edition {titre_var}}}
\\begin{{document}}
{content}
\\end{{document}}
"""
    tex_name = f"MANUEL_1SPE_{variant}"
    tex_path = build / f"{tex_name}.tex"
    tex_path.write_text(master, encoding="utf-8")

    for i in range(3):
        proc = subprocess.run(
            ["lualatex", "-interaction=nonstopmode", "-halt-on-error",
             f"-output-directory={build}", str(tex_path)],
            capture_output=True, text=True, cwd=ROOT, errors="replace")
        if proc.returncode != 0 and i == 2:
            print(proc.stdout[-3000:])
            return 1

    pdf_path = build / f"{tex_name}.pdf"
    if verify_pdf(pdf_path, build / f"{tex_name}.log"):
        return 1
    print(f"PDF : {pdf_path}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="professeur",
                    choices=["professeur", "eleve"])
    args = ap.parse_args()
    sys.exit(main(args.variant))
