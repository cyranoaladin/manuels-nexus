#!/usr/bin/env python3
"""
Script de génération de l'inventaire exhaustif des fichiers de style, classe et gabarit.
Génère audit/LATEX_STYLE_INVENTORY.json et audit/LATEX_STYLE_INVENTORY.md.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Dossiers hors perimetre de l'inventaire. Le balayage se fait sur le disque et non sur
# l'index Git : les dossiers locaux non versionnes doivent donc etre exclus explicitement.
# Fiches_cours_exercices/ contient des documents pedagogiques personnels (cf. .gitignore).
EXCLUDED_PARTS = {".git", ".worktrees", "Fiches_cours_exercices"}


def is_scannable(path: Path, root: Path | None = None) -> bool:
    """True si aucun segment INTERIEUR au depot n'est hors perimetre.

    Le filtre porte sur le chemin relatif a la racine, jamais sur le chemin
    absolu : un depot place sous un repertoire nomme `.worktrees` -- le cas de
    `.worktrees/t3-publish-readiness` -- verrait sinon chacun de ses fichiers
    rejete, et produirait un inventaire vide se donnant pour une preuve.
    """
    base = ROOT if root is None else root
    try:
        parts = path.relative_to(base).parts
    except ValueError:
        return False
    return EXCLUDED_PARTS.isdisjoint(parts)


def scan_style_files():
    found_files = set()

    for ext in ["*.cls", "*.sty"]:
        for p in ROOT.rglob(ext):
            if is_scannable(p, ROOT):
                found_files.add(p)

    for p in ROOT.rglob("*.tex"):
        if is_scannable(p, ROOT):
            name_lower = p.name.lower()
            if "gabarit" in name_lower or "master" in name_lower or name_lower.startswith("nexus-"):
                found_files.add(p)
                
    inventory = []
    for file_path in sorted(found_files):
        rel_path = file_path.relative_to(ROOT).as_posix()
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        sha256 = hashlib.sha256(file_path.read_bytes()).hexdigest()
        
        # Version extraction
        version_match = re.search(r"v\d+(\.\d+)*", content, re.IGNORECASE) or re.search(r"202\d[/\-]\d{2}[/\-]\d{2}", content)
        version = version_match.group(0) if version_match else "1.0.0"
        
        # Determine discipline
        if rel_path.startswith("NSI/"):
            discipline = "NSI"
        elif rel_path.startswith("Mathematiques/"):
            discipline = "Mathématiques"
        elif rel_path.startswith("gabarits/common/"):
            discipline = "Common (Tronc Commun)"
        else:
            discipline = "Transversal / Common"
            
        # Determine production / active status
        is_legacy = "reference-v4" in rel_path or "v4" in rel_path
        is_production = not is_legacy and ("gabarits/" in rel_path or "corpus" in rel_path)
        is_active = is_production
        
        # Determine role
        if rel_path.endswith(".cls"):
            role = "Classe LaTeX principale"
        elif "charte" in rel_path:
            role = "Module de charte graphique"
        elif "boites" in rel_path:
            role = "Module d'encadrés et boîtes"
        elif "exercices" in rel_path:
            role = "Module de mise en page des exercices"
        elif "pont" in rel_path:
            role = "Module de transition et liens"
        elif "couverture" in rel_path:
            role = "Module de couverture"
        elif "pages-froides" in rel_path:
            role = "Module des pages froides et mode d'emploi"
        else:
            role = "Composant LaTeX de structure / gabarit"
            
        action_finale = "Archiver dans archive/" if is_legacy else ("Consolider dans gabarits/common/" if "common" not in rel_path and not rel_path.startswith("gabarits/") else "Conserver canonique")
        
        inventory.append({
            "path": rel_path,
            "sha256": sha256,
            "version_declaree": version,
            "role": role,
            "actif": is_active,
            "production": is_production,
            "historique": is_legacy,
            "discipline": discipline,
            "loaded_by": "Classes masters & scripts de compilation",
            "replacement": "gabarits/common/" + file_path.name if is_legacy or "NSI/gabarits" in rel_path else rel_path,
            "action_finale": action_finale
        })
        
    return inventory

def main():
    inventory = scan_style_files()
    
    # Save JSON
    json_path = ROOT / "audit/LATEX_STYLE_INVENTORY.json"
    json_path.write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Save Markdown
    md_path = ROOT / "audit/LATEX_STYLE_INVENTORY.md"
    md_content = ["# INVENTAIRE EXHAUSTIF DES CLASSES, STYLES ET GABARITS LATEX\n",
                  f"Généré par `scripts/build_style_inventory.py` "
                  f"| Périmètre : dépôt hors {', '.join(sorted(EXCLUDED_PARTS))} "
                  f"| Nombre total de fichiers inventoriés : {len(inventory)}\n",
                  "| Chemin | Rôle | SHA-256 (8 premiers car.) | Discipline | Actif ? | Prod ? | Action Finale |",
                  "| :--- | :--- | :---: | :---: | :---: | :---: | :--- |"]
    
    for item in inventory:
        sha_short = item["sha256"][:8]
        actif_str = "YES" if item["actif"] else "NO"
        prod_str = "YES" if item["production"] else "NO"
        md_content.append(f"| `{item['path']}` | {item['role']} | `{sha_short}` | {item['discipline']} | {actif_str} | {prod_str} | {item['action_finale']} |")
        
    md_path.write_text("\n".join(md_content) + "\n", encoding="utf-8")
    print(f"Inventaire généré avec succès : {len(inventory)} fichiers analysés.")

if __name__ == "__main__":
    main()
