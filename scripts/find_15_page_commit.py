#!/usr/bin/env python3
"""Trouve le commit exact où la maquette est passée de 15 pages à 16 pages."""

import os
import shutil
import subprocess
import sys
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMITS = [
    "81f00693",
    "ff0cdbdb",
    "e630c5ad",
    "b466fc6a",
    "533d1919",
    "ff55af2e",
    "0aab5554",
    "d8fd14e1",
    "6a1b987f",
    "b5c6f9f1",
    "1d0c3fda",
    "64cae132",
]

def fix_qcm_sha256(math_dir: Path) -> None:
    manifest_path = math_dir / "build/maquette-v5/manifest.json"
    qcm_path = math_dir / "chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.tex"
    if manifest_path.is_file() and qcm_path.is_file():
        h = hashlib.sha256(qcm_path.read_bytes()).hexdigest()
        content = manifest_path.read_text(encoding="utf-8")
        import re
        content = re.sub(r'"sha256":\s*"[a-f0-9]{64}"', f'"sha256": "{h}"', content)
        manifest_path.write_text(content, encoding="utf-8")

def check_commit_pages(commit: str, env: dict) -> tuple[int, int, str]:
    tmp = Path(f"/tmp/exp_bisect_{commit}")
    if tmp.exists():
        subprocess.run(["git", "worktree", "remove", "--force", str(tmp)], cwd=ROOT, check=False)
        shutil.rmtree(tmp, ignore_errors=True)
    
    res = subprocess.run(["git", "worktree", "add", str(tmp), commit], cwd=ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        return 1, 0, f"git worktree add failed: {res.stderr}"

    math_dir = tmp / "Mathematiques/manuel-maths"
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
        subprocess.run(["git", "worktree", "remove", "--force", str(tmp)], cwd=ROOT, check=False)
        return res_gen.returncode, 0, f"Génération renvois.tex failed: {res_gen.stderr}"

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
            subprocess.run(["git", "worktree", "remove", "--force", str(tmp)], cwd=ROOT, check=False)
            return res.returncode, 0, res.stdout + res.stderr

    pdf_path = out_dir / "maquette.pdf"
    info = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True, check=True).stdout
    pages = 0
    for line in info.splitlines():
        if line.startswith("Pages:"):
            pages = int(line.split(":")[1].strip())

    h = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    subprocess.run(["git", "worktree", "remove", "--force", str(tmp)], cwd=ROOT, check=False)
    return 0, pages, h

def main() -> None:
    env = os.environ.copy()
    env["TEXMFVAR"] = "/tmp/texmf-var"
    env["TEXMFCACHE"] = "/tmp/texmf-cache"

    print("=== RECHERCHE DU COMMIT DE DIVERGENCE DE PAGINATION ===")
    for commit in COMMITS:
        code, pages, h = check_commit_pages(commit, env)
        print(f"Commit {commit} : code={code}, pages={pages}, sha256={h[:16]}...")

if __name__ == "__main__":
    main()
