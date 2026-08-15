#!/usr/bin/env python3
"""Script forensique d'analyse comparative des builds A, B et C.

Expérience A (Témoin) : SHA 81f00693 sans modifs Phase C.
Expérience B (Onglets Seuls) : SHA 81f00693 + uniquement modifs onglets dans nexus-charte-v6.sty.
Expérience C (Phase C complète) : Arbre courant avec tous les fichiers Phase C.
"""

import os
import shutil
import subprocess
import sys
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def fix_qcm_sha256(math_dir: Path) -> None:
    manifest_path = math_dir / "build/maquette-v5/manifest.json"
    qcm_path = math_dir / "chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.tex"
    if manifest_path.is_file() and qcm_path.is_file():
        h = hashlib.sha256(qcm_path.read_bytes()).hexdigest()
        content = manifest_path.read_text(encoding="utf-8")
        # replace sha256
        import re
        content = re.sub(r'"sha256":\s*"[a-f0-9]{64}"', f'"sha256": "{h}"', content)
        manifest_path.write_text(content, encoding="utf-8")

def compile_maquette(work_dir: Path, env: dict) -> tuple[int, str, str]:
    math_dir = work_dir / "Mathematiques/manuel-maths"
    manifest = math_dir / "build/maquette-v5/manifest.json"
    renvois = math_dir / "build/maquette-v5/renvois.tex"
    tex_path = math_dir / "build/maquette-v5/maquette.tex"
    out_dir = math_dir / "build/maquette-v5"

    fix_qcm_sha256(math_dir)

    # Step 1: Generate renvois.tex
    gen_cmd = [
        sys.executable,
        str(math_dir / "scripts/build_maquette_v5.py"),
        "--manifest",
        str(manifest),
        "--output",
        str(renvois)
    ]
    res_gen = subprocess.run(gen_cmd, cwd=math_dir, capture_output=True, text=True)
    if res_gen.returncode != 0:
        return res_gen.returncode, "", f"Génération renvois.tex en échec: {res_gen.stdout} {res_gen.stderr}"

    # Step 2: Run lualatex x3
    cmd = [
        "lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={out_dir}",
        str(tex_path)
    ]
    for _ in range(3):
        res = subprocess.run(cmd, cwd=math_dir, env=env, capture_output=True, text=True)
        if res.returncode != 0:
            return res.returncode, "", res.stdout + res.stderr

    pdf_path = out_dir / "maquette.pdf"
    if not pdf_path.is_file():
        return 1, "", "PDF non produit"

    # Get page count
    info = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True, check=True).stdout
    pages = 0
    for line in info.splitlines():
        if line.startswith("Pages:"):
            pages = int(line.split(":")[1].strip())

    # SHA256 of PDF
    h = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    return 0, str(pages), h

def main() -> None:
    env = os.environ.copy()
    env["TEXMFVAR"] = "/tmp/texmf-var"
    env["TEXMFCACHE"] = "/tmp/texmf-cache"

    print("=== DÉBUT DES EXPÉRIENCES FORENSIQUES ===")

    # 1. BUILD A (Commit 81f00693 pur)
    print("\n--- Expérience A (Témoin 81f00693) ---")
    tmp_a = Path("/tmp/exp_a")
    if tmp_a.exists():
        subprocess.run(["git", "worktree", "remove", "--force", str(tmp_a)], cwd=ROOT, check=False)
        shutil.rmtree(tmp_a, ignore_errors=True)
    subprocess.run(["git", "worktree", "add", str(tmp_a), "81f00693"], cwd=ROOT, check=True)
    
    code_a, pages_a, sha_a = compile_maquette(tmp_a, env)
    print(f"Expérience A : code={code_a}, pages={pages_a}, sha256={sha_a}")

    # 2. BUILD B (Commit 81f00693 + ONGLET SEUL)
    print("\n--- Expérience B (Onglets Seuls 16mm/6mm/6pt) ---")
    tmp_b = Path("/tmp/exp_b")
    if tmp_b.exists():
        subprocess.run(["git", "worktree", "remove", "--force", str(tmp_b)], cwd=ROOT, check=False)
        shutil.rmtree(tmp_b, ignore_errors=True)
    subprocess.run(["git", "worktree", "add", str(tmp_b), "81f00693"], cwd=ROOT, check=True)
    
    # Modify ONLY the tab parameters in nexus-charte-v6.sty
    sty_b = tmp_b / "Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty"
    content = sty_b.read_text(encoding="utf-8")
    content = content.replace(r"\fontsize{5.5}{5.5}", r"\fontsize{6}{6}")
    content = content.replace(r"+5mm\relax}", r"+6mm\relax}")
    content = content.replace(r"<14mm", r"<16mm")
    content = content.replace(r"{14mm}\fi", r"{16mm}\fi")
    sty_b.write_text(content, encoding="utf-8")

    code_b, pages_b, sha_b = compile_maquette(tmp_b, env)
    print(f"Expérience B : code={code_b}, pages={pages_b}, sha256={sha_b}")

    # 3. BUILD C (Arbre courant Phase C)
    print("\n--- Expérience C (Phase C complète courant) ---")
    code_c, pages_c, sha_c = compile_maquette(ROOT, env)
    print(f"Expérience C : code={code_c}, pages={pages_c}, sha256={sha_c}")

    # Cleanup worktrees
    subprocess.run(["git", "worktree", "remove", "--force", str(tmp_a)], cwd=ROOT, check=False)
    subprocess.run(["git", "worktree", "remove", "--force", str(tmp_b)], cwd=ROOT, check=False)

    print("\n=== SYNTHÈSE DES EXPÉRIENCES ===")
    print(f"Expérience A (81f00693)          : {pages_a} pages | SHA: {sha_a}")
    print(f"Expérience B (Onglets Seuls)     : {pages_b} pages | SHA: {sha_b}")
    print(f"Expérience C (Phase C complète)  : {pages_c} pages | SHA: {sha_c}")

if __name__ == "__main__":
    main()
