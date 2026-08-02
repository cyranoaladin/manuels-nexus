"""Assemblage du manuel complet 1SPE : transversal + 10 chapitres.

Variantes :
  --variant professeur  (tout : cours, exercices, corriges, evaluations, baremes)
  --variant eleve       (sans corriges ni baremes d'evaluation)
"""
import argparse
import hashlib
import os
import re
import secrets
import stat
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


def resolve_git_root(start: Path) -> Path:
    completed = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(completed.stdout.strip()).resolve(strict=True)


def load_tracked_paths(git_root: Path) -> frozenset[str]:
    completed = subprocess.run(
        ["git", "-C", str(git_root), "ls-files", "-z"],
        check=True,
        capture_output=True,
        encoding="utf-8",
    )
    return frozenset(path for path in completed.stdout.split("\0") if path)


def canonical_tracked_path(
    raw_path: str | Path,
    git_root: Path,
    tracked_paths: frozenset[str] | None = None,
) -> str:
    raw = os.fspath(raw_path)
    candidate_path = Path(raw)
    if (
        not raw
        or raw != raw.strip()
        or candidate_path.is_absolute()
        or "\\" in raw
        or any(part in {"", ".", ".."} for part in raw.split("/"))
    ):
        raise ValueError("chemin suivi non canonique")

    root = git_root.resolve(strict=True)
    candidate = root
    for part in raw.split("/"):
        candidate /= part
        try:
            mode = candidate.lstat().st_mode
        except FileNotFoundError as error:
            raise ValueError("chemin suivi absent") from error
        if stat.S_ISLNK(mode):
            raise ValueError("chemin symbolique interdit")
    if not stat.S_ISREG(candidate.stat().st_mode):
        raise ValueError("chemin suivi non régulier")

    if tracked_paths is None:
        tracked_paths = load_tracked_paths(root)
    if raw not in tracked_paths:
        raise ValueError("chemin non suivi par Git")
    return raw


def object_trace_token(canonical_path: str) -> str:
    return hashlib.sha256(canonical_path.encode("utf-8")).hexdigest()[:40]


def wrap_object_input(input_path: str, canonical_path: str) -> str:
    token = object_trace_token(canonical_path)
    return "\n".join(
        [
            f"\\typeout{{NEXUS_OBJECT_BEGIN:{token}}}",
            f"\\input{{{input_path}}}",
            f"\\typeout{{NEXUS_OBJECT_END:{token}}}",
        ]
    )


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


def render_master(variant: str, run_id: str) -> str:
    if variant not in {"eleve", "professeur"}:
        raise ValueError("variante inconnue")
    if re.fullmatch(r"[0-9a-f]{32}", run_id) is None:
        raise ValueError("identifiant de build invalide")
    git_root = resolve_git_root(ROOT)
    tracked_paths = load_tracked_paths(git_root)
    parts = []

    # Transversal front matter
    parts.append("\\input{transversal/page_de_garde}")
    parts.append("\\newpage")
    parts.append("\\input{transversal/avant_propos}")
    parts.append("\\newpage")
    parts.append("\\input{transversal/mode_emploi}")
    parts.append("\\newpage")
    parts.append("\\tableofcontents")
    parts.append("\\newpage")
    parts.append("\\input{transversal/index_capacites}")
    parts.append("\\newpage")

    # Chapters
    for chap in CHAPITRES:
        chap_dir = ROOT / "chapitres" / chap
        if not chap_dir.exists():
            print(f"SKIP {chap} (directory not found)")
            continue

        opening = ouverture_depuis_contrat(chap_dir)
        files = collect_chapter(chap_dir, variant)
        inputs = "\n".join(
            wrap_object_input(
                f.relative_to(ROOT).as_posix(),
                canonical_tracked_path(
                    f.relative_to(git_root).as_posix(),
                    git_root,
                    tracked_paths,
                ),
            )
            for f in files
        )
        parts.append(f"% ===== {chap} =====")
        parts.append(opening)
        parts.append(inputs)

    # Back matter
    parts.append("\\appendix")
    parts.append("\\clearpage")
    parts.append("\\input{transversal/formulaire}")
    parts.append("\\clearpage")
    parts.append("\\input{transversal/memo_python}")

    content = "\n".join(parts)

    titre_var = "professeur" if variant == "professeur" else "eleve"
    master = f"""% Manuel 1SPE — variante {titre_var}
% Assemble par scripts/assemble_manuel.py
\\documentclass{{gabarits/nexus-manuel}}
\\matiere{{Mathématiques}}\\niveau{{Première spécialité}}
\\title{{Manuel de mathématiques — Première spécialité — Édition {titre_var}}}
\\begin{{document}}
\\typeout{{NEXUS_BUILD_RUN:{run_id}}}
{content}
\\end{{document}}
"""
    return master


def main(variant: str) -> int:
    build = ROOT / "build" / "MANUEL_1SPE"
    build.mkdir(parents=True, exist_ok=True)

    master = render_master(variant, secrets.token_hex(16))
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
