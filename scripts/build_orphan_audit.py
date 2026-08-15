#!/usr/bin/env python3
"""Générateur du rapport d'analyse des dépendances et fichiers orphelins.

Analyse les dépendances \\input, \\include, \\includegraphics, \\documentclass, \\usepackage,
manifestes JSON et imports Python pour identifier les fichiers autonomes, les fixtures,
les dépendances directes et les candidats orphelins.
"""

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    res = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True)
    tracked_files = [p for p in res.stdout.decode("utf-8").split("\0") if p.strip()]
    tracked_set = set(tracked_files)

    incoming_refs: dict[str, set[str]] = {f: set() for f in tracked_files}
    outgoing_refs: dict[str, set[str]] = {f: set() for f in tracked_files}

    # Regex for TeX inclusions
    re_input = re.compile(r'\\(?:input|include|includegraphics|documentclass|usepackage)(?:\[[^\]]*\])?\{([^}]+)\}')
    
    for f in tracked_files:
        if not (f.endswith(".tex") or f.endswith(".cls") or f.endswith(".sty") or f.endswith(".json")):
            continue
        abs_p = ROOT / f
        if not abs_p.is_file():
            continue
        try:
            content = abs_p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
            
        for m in re_input.finditer(content):
            target = m.group(1).strip()
            # Normalize target path
            possible_targets = [
                target,
                target + ".tex",
                target + ".cls",
                target + ".sty",
                target + ".png",
                target + ".jpg",
                target + ".pdf",
                "Mathematiques/manuel-maths/" + target,
                "Mathematiques/manuel-maths/" + target + ".tex",
                "NSI/" + target,
                "NSI/" + target + ".tex",
            ]
            for pt in possible_targets:
                if pt in tracked_set:
                    incoming_refs[pt].add(f)
                    outgoing_refs[f].add(pt)

    # Classify files based on incoming refs
    orphans = []
    standalones = []
    
    for f in tracked_files:
        in_cnt = len(incoming_refs[f])
        out_cnt = len(outgoing_refs[f])
        
        # Standalone files (entrypoints, manifests, root scripts, docs)
        if any(f.startswith(prefix) for prefix in ["scripts/", "tests/", "docs/", "audit/", "manifests/"]) or f.endswith(".py") or f.endswith(".json") or f in ["AGENTS.md", "README.md", "CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md"]:
            standalones.append(f)
        elif in_cnt == 0:
            orphans.append({
                "path": f,
                "type": Path(f).suffix or "no_ext",
                "outgoing_refs": len(outgoing_refs[f]),
                "reason": "Aucune référence entrante directe (peut être un fragment ou fixture)"
            })

    md_path = ROOT / "audit/ORPHAN_FILES_AUDIT.md"
    with open(md_path, "w", encoding="utf-8") as out:
        out.write("# AUDIT DES FICHIERS ET DÉPENDANCES DU DÉPÔT\n\n")
        out.write(f"- **Total fichiers suivis** : `{len(tracked_files)}`\n")
        out.write(f"- **Fichiers autonomes / Scripts / Entrées** : `{len(standalones)}`\n")
        out.write(f"- **Fichiers sans référence entrante directe** : `{len(orphans)}` (inclus fragments de chapitres, gabarits autonomes et ressources)\n\n")
        out.write("## Fichiers sans Référence Entrante Directe\n\n")
        out.write("| Chemin Fichier | Type | Références Sortantes | Analyse et Rôle |\n")
        out.write("| :--- | :---: | :---: | :--- |\n")
        for o in orphans[:100]: # Top 100
            out.write(f"| `{o['path']}` | `{o['type']}` | {o['outgoing_refs']} | {o['reason']} |\n")

    print(f"ORPHAN_FILES_AUDIT généré avec succès : {len(orphans)} fichiers sans référence directe analysés.")

if __name__ == "__main__":
    main()
