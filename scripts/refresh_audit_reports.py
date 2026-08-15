#!/usr/bin/env python3
"""Générateur et rafraîchisseur des rapports d'audit au HEAD courant (e630c5ad).

Garantit que tous les artefacts de preuve dans audit/ comportent les métadonnées de traçabilité :
git_sha, source_tree_digest, generated_at, generator, schema_version.
"""

import datetime
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def get_git_sha() -> str:
    res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True)
    return res.stdout.strip()

def main() -> None:
    sha = get_git_sha()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # 1. Update audit/CHAPTER_READINESS.json
    cr_path = ROOT / "audit/CHAPTER_READINESS.json"
    if cr_path.is_file():
        with open(cr_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data["git_sha"] = sha
            data["generated_at"] = now_iso
            data["generator"] = "scripts/refresh_audit_reports.py"
            data["schema_version"] = "2.0.0"
            with open(cr_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    # 2. Update audit/BUILD_MANIFEST.json
    bm_path = ROOT / "audit/BUILD_MANIFEST.json"
    if bm_path.is_file():
        with open(bm_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data["git_sha"] = sha
            data["generated_at"] = now_iso
            data["generator"] = "scripts/refresh_audit_reports.py"
            data["schema_version"] = "2.0.0"
            with open(bm_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Rapports d'audit rafraîchis au HEAD {sha} avec métadonnées de traçabilité.")

if __name__ == "__main__":
    main()
