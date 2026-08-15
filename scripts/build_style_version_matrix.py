#!/usr/bin/env python3
"""Générateur de la matrice d'audit des versions et forks de charte (STYLE_VERSION_MATRIX.md).

Compare byte à byte et par hash SHA-256 tous les fichiers de gabarits et de classe
entre Mathematiques/manuel-maths/gabarits et NSI/gabarits.
"""

import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MATH_GABARITS = ROOT / "Mathematiques/manuel-maths/gabarits"
NSI_GABARITS = ROOT / "NSI/gabarits"

def calculate_sha256(path: Path) -> str:
    if not path.is_file():
        return "ABSENT"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def extract_declared_version(path: Path) -> str:
    if not path.is_file():
        return "N/A"
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        for line in content.splitlines()[:15]:
            if "ProvidesClass" in line or "ProvidesPackage" in line or "version" in line.lower() or "v4" in line.lower() or "v5" in line.lower() or "v6" in line.lower():
                return line.strip()
    except Exception:
        pass
    return "Non spécifiée"

def main() -> None:
    math_files = {p.name: p for p in MATH_GABARITS.glob("*") if p.is_file()}
    nsi_files = {p.name: p for p in NSI_GABARITS.glob("*") if p.is_file()}

    all_names = sorted(set(math_files.keys()).union(set(nsi_files.keys())))

    matrix = []

    for name in all_names:
        math_p = math_files.get(name)
        nsi_p = nsi_files.get(name)

        math_sha = calculate_sha256(math_p) if math_p else "ABSENT"
        nsi_sha = calculate_sha256(nsi_p) if nsi_p else "ABSENT"

        math_ver = extract_declared_version(math_p) if math_p else "N/A"
        nsi_ver = extract_declared_version(nsi_p) if nsi_p else "N/A"

        if math_sha == "ABSENT":
            status = "Exclusif NSI"
        elif nsi_sha == "ABSENT":
            status = "Exclusif Mathématiques"
        elif math_sha == nsi_sha:
            status = "100% Identique (Byte-per-byte)"
        else:
            status = "Divergent (Fork détecté)"

        matrix.append({
            "name": name,
            "math_path": str(math_p.relative_to(ROOT)) if math_p else "-",
            "nsi_path": str(nsi_p.relative_to(ROOT)) if nsi_p else "-",
            "math_sha": math_sha[:12] if math_sha != "ABSENT" else "ABSENT",
            "nsi_sha": nsi_sha[:12] if nsi_sha != "ABSENT" else "ABSENT",
            "math_ver": math_ver,
            "nsi_ver": nsi_ver,
            "status": status,
        })

    md_path = ROOT / "audit/STYLE_VERSION_MATRIX.md"
    with open(md_path, "w", encoding="utf-8") as out:
        out.write("# MATRICE D'AUDIT DES STYLES ET DIVERGENCES DE CHARTE (MATHS vs NSI)\n\n")
        out.write("Ce document recense les divergences byte-à-byte entre les fichiers de gabarits des Mathématiques et de la NSI.\n\n")
        out.write("| Nom Composant | Hash Maths (SHA-256) | Hash NSI (SHA-256) | Statut de Synchronisation | Version Déclarée |\n")
        out.write("| :--- | :---: | :---: | :--- | :--- |\n")
        for m in matrix:
            out.write(f"| `{m['name']}` | `{m['math_sha']}` | `{m['nsi_sha']}` | **{m['status']}** | `{m['math_ver'][:40]}` |\n")

        out.write("\n## Synthèse des Divergences Majeures\n\n")
        divergents = [m for m in matrix if m['status'] == "Divergent (Fork détecté)"]
        out.write(f"Nombre total de fichiers de style divergents identifiés : **{len(divergents)}**\n\n")
        for d in divergents:
            out.write(f"- `{d['name']}` : Maths (`{d['math_sha']}`) vs NSI (`{d['nsi_sha']}`). Nécessite unification dans la source canonique.\n")

    print(f"STYLE_VERSION_MATRIX généré avec succès : {len(matrix)} composants analysés.")

if __name__ == "__main__":
    main()
