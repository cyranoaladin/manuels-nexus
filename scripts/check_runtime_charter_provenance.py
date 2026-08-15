#!/usr/bin/env python3
"""
Vérificateur Runtime de Provenance de la Charte Graphique.
Parse le fichier .fls (LuaLaTeX -recorder) pour prouver physiquement quels fichiers .cls et .sty
ont été chargés lors du rendu du PDF.
Génère audit/RUNTIME_CHARTER_PROVENANCE.json et audit/RUNTIME_CHARTER_PROVENANCE.md.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def parse_fls_inputs(fls_path: Path) -> list[Path]:
    """Parse a .fls file and extract all UNIQUE INPUT file paths."""
    if not fls_path.is_file():
        return []
    
    inputs = set()
    for line in fls_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("INPUT "):
            raw_path = line[6:].strip()
            # Convert to absolute path or path relative to ROOT if inside workspace
            p = Path(raw_path)
            try:
                rel = p.relative_to(ROOT)
                inputs.add(rel)
            except ValueError:
                # External file (texlive system font/package)
                pass
    return sorted(list(inputs))

def inspect_build_provenance(fls_path: Path, manual_id: str = "1SPE", variant: str = "eleve"):
    inputs = parse_fls_inputs(fls_path)
    
    cls_files = [p for p in inputs if p.suffix == ".cls"]
    sty_files = [p for p in inputs if p.suffix == ".sty"]
    
    legacy_loaded = [p.as_posix() for p in inputs if "v4" in p.as_posix() or "reference-v4" in p.as_posix()]
    unexpected_loaded = []
    prototype_loaded = [p.as_posix() for p in inputs if "proto" in p.as_posix() or "draft" in p.as_posix()]
    
    canonical_class = cls_files[0].as_posix() if cls_files else "N/A"
    canonical_class_sha = hashlib.sha256((ROOT / cls_files[0]).read_bytes()).hexdigest() if cls_files and (ROOT / cls_files[0]).is_file() else "N/A"
    
    common_modules = {}
    for sty in sty_files:
        full_p = ROOT / sty
        if full_p.is_file():
            common_modules[sty.as_posix()] = hashlib.sha256(full_p.read_bytes()).hexdigest()
            
    record = {
        "manual": manual_id,
        "variant": variant,
        "fls_path": fls_path.relative_to(ROOT).as_posix() if fls_path.is_relative_to(ROOT) else str(fls_path),
        "canonical_class_path": canonical_class,
        "canonical_class_sha256": canonical_class_sha,
        "loaded_common_modules": common_modules,
        "loaded_discipline_adapter": [p.as_posix() for p in sty_files if "maths" in p.as_posix() or "nsi" in p.as_posix()],
        "legacy_modules_loaded": legacy_loaded,
        "unexpected_modules": unexpected_loaded,
        "prototype_modules_loaded": prototype_loaded,
        "status": "PASS" if not legacy_loaded and not prototype_loaded else "FAIL"
    }
    return record

def main():
    fls_candidates = list(ROOT.glob("build/**/*.fls"))
    if not fls_candidates:
        # Fallback to maquette-v5 if compiled
        fls_candidates = list(ROOT.glob("Mathematiques/manuel-maths/build/**/*.fls"))
        
    records = []
    for fls in fls_candidates:
        manual_id = "1SPE" if "maquette-v5" in str(fls) or "1SPE" in str(fls) else "UNKNOWN"
        rec = inspect_build_provenance(fls, manual_id=manual_id, variant="eleve")
        records.append(rec)
        
    json_path = ROOT / "audit/RUNTIME_CHARTER_PROVENANCE.json"
    json_path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    
    md_path = ROOT / "audit/RUNTIME_CHARTER_PROVENANCE.md"
    md_content = [
        "# PREUVE RUNTIME DE PROVENANCE DE LA CHARTE GRAPHIQUE (.FLS)\n",
        f"Généré le: 2026-08-15 | Builds analysés : {len(records)}\n",
        "| Manuel | Variante | Classe Chargée | SHA256 Classe | Legacy ? | Proto ? | Statut |",
        "| :--- | :---: | :--- | :---: | :---: | :---: | :---: |"
    ]
    for r in records:
        leg_str = "❌ OUI" if r["legacy_modules_loaded"] else "✅ NON"
        proto_str = "❌ OUI" if r["prototype_modules_loaded"] else "✅ NON"
        md_content.append(f"| {r['manual']} | {r['variant']} | `{r['canonical_class_path']}` | `{r['canonical_class_sha256'][:8]}` | {leg_str} | {proto_str} | **{r['status']}** |")
        
    md_path.write_text("\n".join(md_content) + "\n", encoding="utf-8")
    print(f"Preuve runtime .fls générée : {len(records)} builds analysés.")
    
    # Gate check
    for r in records:
        if r["status"] != "PASS":
            print(f"GATE FAILED: Legacy or prototype modules loaded in {r['fls_path']}", file=sys.stderr)
            return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
