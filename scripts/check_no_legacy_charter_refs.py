#!/usr/bin/env python3
"""
Gate CI : Interdiction absolue de charger l'ancien moteur (V4/V4.1 legacy) ou des forks non autorisés
dans les chemins de compilation de production.
"""
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# References that indicate legacy charter usage in production paths
LEGACY_PATTERNS = [
    r"nexus-manuel-v4",
    r"reference-v4",
    r"gabarits/v4",
]

# Files to inspect (assemblers, masters, scripts, CI workflows)
TARGET_PATTERNS = [
    "**/scripts/*.py",
    "**/gabarits/*.cls",
    "**/gabarits/*.sty",
    "**/*.master.tex",
    "**/*_master.tex",
    ".github/workflows/*.yml",
]

def check_legacy_refs():
    violations = []
    scanned_count = 0
    
    for pattern in TARGET_PATTERNS:
        for file_path in ROOT.glob(pattern):
            if ".worktrees" in file_path.parts or ".git" in file_path.parts or "archive" in file_path.parts:
                continue
            if file_path.name in ["check_no_legacy_charter_refs.py", "build_style_inventory.py"]:
                continue
            scanned_count += 1
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            
            for leg_pat in LEGACY_PATTERNS:
                matches = re.finditer(leg_pat, content, re.IGNORECASE)
                for m in matches:
                    line_no = content[:m.start()].count("\n") + 1
                    violations.append(f"{file_path.relative_to(ROOT)}:{line_no} — Motif legacy interdit trouvé: '{m.group(0)}'")
                    
    print(f"CHECK NO LEGACY CHARTER REFS: {scanned_count} fichiers analysés.")
    if violations:
        print("ERREUR: Références legacy trouvées dans les chemins de production :", file=sys.stderr)
        for v in violations:
            print(f"  ❌ {v}", file=sys.stderr)
        return 1
    
    print("SUCCESS: Aucune référence legacy ni fork interdit détecté dans les chemins de production.")
    return 0

if __name__ == "__main__":
    sys.exit(check_legacy_refs())
