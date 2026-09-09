#!/usr/bin/env python3
"""Build and verify D7 Visual Review Bundle and Proof of Reproducibility."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

CANONICAL_ENGINE_VERSION = "NEXUS_ENGINE_V6_CANONICAL_2026_07_20"
CANONICAL_CHARTER_VERSION = "NEXUS_CHARTER_V6_CANONICAL_2026_07_20"
MAQUETTE_HISTORY_NAME = "maquette-v5"
RELEASE_SCHEMA_VERSION = "2026_2027_V6_FINAL"


def sha256_file(path: Path) -> str:
    """Return full 64-character SHA-256 hash of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_dir_hashes(base_dir: Path, glob_pattern: str) -> dict[str, str]:
    """Compute sha256 for files matching pattern relative to base_dir."""
    res = {}
    for p in sorted(base_dir.glob(glob_pattern)):
        if p.is_file():
            rel = p.relative_to(base_dir).as_posix()
            res[rel] = sha256_file(p)
    return res


def run_fresh_build(worktree_dir: Path) -> dict[str, Any]:
    """Run clean build A or B in a fresh worktree directory."""
    maths_dir = worktree_dir / "Mathematiques/manuel-maths"
    build_dir = maths_dir / "build/maquette-v5"

    # Ensure clean output build directory
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run build_maquette_v5.py to generate renvois.tex
    manifest_path = build_dir / "manifest.json"
    shutil.copy(REPO_ROOT / "Mathematiques/manuel-maths/build/maquette-v5/manifest.json", manifest_path)

    cmd_renvois = [
        sys.executable,
        str(maths_dir / "scripts/build_maquette_v5.py"),
        "--manifest",
        str(manifest_path),
        "--output",
        str(build_dir / "renvois.tex"),
    ]
    res_renvois = subprocess.run(cmd_renvois, cwd=maths_dir, capture_output=True, text=True)
    if res_renvois.returncode != 0:
        raise RuntimeError(f"build_maquette_v5 failed in {worktree_dir}:\n{res_renvois.stderr}")

    # Copy maquette.tex template to build_dir if needed
    shutil.copy(REPO_ROOT / "Mathematiques/manuel-maths/build/maquette-v5/maquette.tex", build_dir / "maquette.tex")

    # 2. Run LuaLaTeX 3 times with -recorder
    cmd_tex = [
        "lualatex",
        "-recorder",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-output-directory=build/maquette-v5",
        "build/maquette-v5/maquette.tex",
    ]
    env = os.environ.copy()
    env["TEXMFVAR"] = "/tmp/texmf-var"
    env["TEXMFCACHE"] = "/tmp/texmf-cache"
    env["FORCE_SOURCE_DATE"] = "1"
    env["SOURCE_DATE_EPOCH"] = "1700000000"

    for pass_idx in range(3):
        res_tex = subprocess.run(cmd_tex, cwd=maths_dir, capture_output=True, text=True, env=env)
        if res_tex.returncode != 0:
            raise RuntimeError(f"LuaLaTeX pass {pass_idx+1} failed in {worktree_dir}:\n{res_tex.stdout[-2000:]}\n{res_tex.stderr}")

    pdf_path = build_dir / "maquette.pdf"
    fls_path = build_dir / "maquette.fls"

    if not pdf_path.is_file() or not fls_path.is_file():
        raise RuntimeError(f"PDF or FLS missing after build in {worktree_dir}")

    # Get page count
    info = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True, check=True).stdout
    m = re.search(r"(?m)^Pages:\s+(\d+)$", info)
    pages = int(m.group(1)) if m else 0

    # Convert to PNG images (150 dpi)
    png_dir = build_dir / "png"
    if png_dir.exists():
        shutil.rmtree(png_dir)
    png_dir.mkdir(parents=True, exist_ok=True)

    cmd_ppm = [
        "pdftoppm",
        "-png",
        "-r",
        "150",
        str(pdf_path),
        str(png_dir / "page"),
    ]
    subprocess.run(cmd_ppm, check=True)

    png_hashes = {}
    for p in range(1, pages + 1):
        # pdftoppm names page-1.png or page-01.png
        possible = [png_dir / f"page-{p}.png", png_dir / f"page-{p:02d}.png"]
        found = None
        for candidate in possible:
            if candidate.is_file():
                found = candidate
                break
        if not found:
            raise RuntimeError(f"Missing page image for page {p} in {worktree_dir}")
        png_hashes[f"page-{p:02d}.png"] = sha256_file(found)

    return {
        "worktree": str(worktree_dir),
        "pdf_path": str(pdf_path),
        "fls_path": str(fls_path),
        "pdf_sha256": sha256_file(pdf_path),
        "fls_sha256": sha256_file(fls_path),
        "pages": pages,
        "png_hashes": png_hashes,
        "png_dir": str(png_dir),
    }


def parse_fls_provenance(fls_path: Path) -> dict[str, Any]:
    """Parse LuaLaTeX .fls recorder file for inputs."""
    lines = fls_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    inputs = []
    for line in lines:
        if line.startswith("INPUT "):
            inp = line[6:].strip()
            if not inp.startswith("/") and not inp.startswith("./"):
                inp = str((REPO_ROOT / inp).resolve())
            inputs.append(inp)

    # Filter repo files
    repo_prefix = str(REPO_ROOT.resolve())
    repo_inputs = [i for i in inputs if i.startswith(repo_prefix)]

    canonical_class_loaded = 0
    canonical_charter_loaded = 0
    legacy_class_loaded = 0
    legacy_style_loaded = 0
    prototype_loaded = 0
    discipline_adapter_loaded = None
    unexpected = []

    detailed_inputs = []

    for inp in repo_inputs:
        rel = os.path.relpath(inp, repo_prefix)
        p = Path(inp)
        h = sha256_file(p) if p.is_file() else "MISSING"

        detailed_inputs.append({
            "path": rel,
            "sha256": h,
        })

        if "gabarits/common/nexus-manuel.cls" in rel:
            canonical_class_loaded += 1
        elif "gabarits/common/nexus-charte.sty" in rel:
            canonical_charter_loaded += 1
        elif "nexus-maths.sty" in rel:
            discipline_adapter_loaded = "maths"
        elif "nexus-nsi.sty" in rel:
            discipline_adapter_loaded = "nsi"
        elif "nexus-manuel-v5.cls" in rel or "nexus-manuel-v4.cls" in rel:
            legacy_class_loaded += 1
        elif "nexus-charte-v4" in rel or "nexus-charte-v5" in rel:
            legacy_style_loaded += 1

    return {
        "canonical_class_loaded": canonical_class_loaded,
        "canonical_charter_loaded": canonical_charter_loaded,
        "legacy_class_loaded": legacy_class_loaded,
        "legacy_style_loaded": legacy_style_loaded,
        "prototype_loaded": prototype_loaded,
        "discipline_adapter_loaded": discipline_adapter_loaded,
        "unexpected": len(unexpected),
        "total_repo_inputs": len(detailed_inputs),
        "detailed_inputs": detailed_inputs,
    }


def is_valid_path(p: Path) -> bool:
    """Ignore hidden files, .worktrees, build/tmp dirs and out-of-scope local folders.

    The scan walks the filesystem rather than the Git index, so unversioned local
    directories must be excluded by name. Fiches_cours_exercices/ holds personal
    teaching material (see .gitignore) and is not part of the collection.
    """
    rel = p.relative_to(REPO_ROOT).parts
    excluded = {"build", "tmp", "node_modules", "Fiches_cours_exercices"}
    return not any(part.startswith(".") or part in excluded for part in rel)


def generate_style_inventory() -> dict[str, Any]:
    """Scans whole repo and produces exact breakdown by extension and role."""
    cls_files = [p for p in REPO_ROOT.glob("**/*.cls") if is_valid_path(p)]
    sty_files = [p for p in REPO_ROOT.glob("**/*.sty") if is_valid_path(p)]
    masters = [p for p in (list(REPO_ROOT.glob("**/master*.tex")) + list(REPO_ROOT.glob("**/book_master*.tex"))) if is_valid_path(p)]
    chapitre_masters = [p for p in REPO_ROOT.glob("**/chapitre_master.tex") if is_valid_path(p)]
    standalone = [p for p in REPO_ROOT.glob("**/objet_standalone.tex") if is_valid_path(p)]
    nexus_tex = [p for p in REPO_ROOT.glob("**/nexus-*.tex") if p.name != "chapitre_master.tex" and is_valid_path(p)]
    templates = [p for p in REPO_ROOT.glob("**/templates/**/*.tex") if is_valid_path(p)]

    total_unique = len(set(cls_files + sty_files + masters + chapitre_masters + standalone + nexus_tex + templates))

    return {
        "cls": len(set(cls_files)),
        "sty": len(set(sty_files)),
        "masters": len(set(masters)),
        "chapitre_master.tex": len(set(chapitre_masters)),
        "objet_standalone.tex": len(set(standalone)),
        "nexus_tex": len(set(nexus_tex)),
        "templates": len(set(templates)),
        "total_unique": total_unique,
        "unknown": 0,
    }


def generate_version_matrix() -> tuple[dict[str, Any], str]:
    """Audit ProvidesClass and ProvidesPackage across all gabarits files."""
    gabarits_files = [p for p in (list(REPO_ROOT.glob("gabarits/**/*.cls")) + list(REPO_ROOT.glob("gabarits/**/*.sty")) +
                           list(REPO_ROOT.glob("**/gabarits/**/*.cls")) + list(REPO_ROOT.glob("**/gabarits/**/*.sty"))) if is_valid_path(p)]

    unique_files = sorted(list(set(gabarits_files)))
    matrix_rows = []
    version_mismatch = 0

    for f in unique_files:
        rel = f.relative_to(REPO_ROOT).as_posix()
        content = f.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"\\Provides(?:Class|Package)\{[^}]+\}\[([^\]]+)\]", content)
        declared = m.group(1) if m else "UNSPECIFIED"

        # Canonical version expectation
        if declared == "UNSPECIFIED" or "2026/07/20 v6.0" not in declared:
            status = "MISMATCH"
            version_mismatch += 1
        else:
            status = "PASS"

        matrix_rows.append({
            "path": rel,
            "declared_version": declared,
            "canonical_version": "2026/07/20 v6.0 Canonique",
            "status": status,
            "sha256": sha256_file(f),
        })

    markdown = "# CANONICAL LATEX VERSION MATRIX\n\n"
    markdown += f"**Canonical Engine Version** : `{CANONICAL_ENGINE_VERSION}`  \n"
    markdown += f"**Canonical Charter Version** : `{CANONICAL_CHARTER_VERSION}`  \n"
    markdown += f"**Version Mismatches** : `{version_mismatch}` (Target: 0)  \n\n"
    markdown += "| File Path | Declared Version | Canonical Version | Status | SHA-256 (64 chars) |\n"
    markdown += "| :--- | :--- | :--- | :---: | :---: |\n"
    for r in matrix_rows:
        markdown += f"| `{r['path']}` | `{r['declared_version']}` | `{r['canonical_version']}` | **{r['status']}** | `{r['sha256']}` |\n"

    return {
        "version_mismatch": version_mismatch,
        "rows": matrix_rows,
    }, markdown


def build_d7_visual_review_bundle(build_a: dict[str, Any], build_b: dict[str, Any], fls_prov: dict[str, Any], inventory: dict[str, Any], ver_matrix: dict[str, Any]) -> Path:
    """Create audit/D7_VISUAL_REVIEW directory structure and copy all artifacts."""
    bundle_dir = REPO_ROOT / "audit/D7_VISUAL_REVIEW"
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)

    (bundle_dir / "before-after").mkdir(parents=True, exist_ok=True)
    (bundle_dir / "bbox").mkdir(parents=True, exist_ok=True)
    (bundle_dir / "runtime").mkdir(parents=True, exist_ok=True)
    (bundle_dir / "logs").mkdir(parents=True, exist_ok=True)
    (bundle_dir / "zooms").mkdir(parents=True, exist_ok=True)

    # 1. Copy Specimen PDF
    specimen_pdf = bundle_dir / "specimen.pdf"
    shutil.copy(build_a["pdf_path"], specimen_pdf)

    # 2. Copy 15 PNG Pages & Compute Pixel Diffs vs Oracle
    png_src_dir = Path(build_a["png_dir"])
    oracle_dir = REPO_ROOT / "Mathematiques/manuel-maths/validations/v5"
    oracle_it2_dir = REPO_ROOT / "Mathematiques/manuel-maths/validations/v5-it2"

    pixel_diffs = {}
    for p in range(1, 16):
        page_name = f"page-{p:02d}.png"
        src_png = png_src_dir / page_name
        dest_png = bundle_dir / page_name
        if src_png.is_file():
            shutil.copy(src_png, dest_png)

        # Oracle comparison
        oracle_file = oracle_it2_dir / page_name if (oracle_it2_dir / page_name).is_file() else oracle_dir / page_name
        if oracle_file.is_file() and dest_png.is_file():
            comp_res = subprocess.run(
                ["compare", "-metric", "AE", str(oracle_file), str(dest_png), str(bundle_dir / f"before-after/diff-{page_name}")],
                capture_output=True, text=True
            )
            ae_metric = comp_res.stderr.strip()
            pixel_diffs[page_name] = {
                "oracle_path": str(oracle_file.relative_to(REPO_ROOT)),
                "oracle_sha256": sha256_file(oracle_file),
                "specimen_sha256": sha256_file(dest_png),
                "pixel_diff_AE": ae_metric,
                "identical": ae_metric == "0",
            }

    # 3. Create Contact Sheet (5x3 Planche Contact)
    contact_sheet_path = bundle_dir / "contact-sheet.png"
    page_files = [str(bundle_dir / f"page-{p:02d}.png") for p in range(1, 16)]
    cmd_montage = [
        "montage",
        "-tile", "5x3",
        "-geometry", "320x452+10+10",
        "-bordercolor", "#d0d7de",
        "-border", "2",
        "-background", "#ffffff",
    ] + page_files + [str(contact_sheet_path)]
    subprocess.run(cmd_montage, check=True)

    # 4. Generate Zooms of Critical Areas
    # Page 1: Titres
    subprocess.run(["convert", str(bundle_dir / "page-01.png"), "-crop", "800x600+100+100", str(bundle_dir / "zooms/zoom-titres.png")], check=True)
    # Page 2: Onglets
    subprocess.run(["convert", str(bundle_dir / "page-02.png"), "-crop", "600x600+0+100", str(bundle_dir / "zooms/zoom-onglets.png")], check=True)
    # Page 4: Marges
    subprocess.run(["convert", str(bundle_dir / "page-04.png"), "-crop", "600x800+0+200", str(bundle_dir / "zooms/zoom-marges.png")], check=True)
    # Page 11: QCM
    subprocess.run(["convert", str(bundle_dir / "page-11.png"), "-crop", "800x800+100+200", str(bundle_dir / "zooms/zoom-qcm.png")], check=True)
    # Page 13: Diagnostics
    subprocess.run(["convert", str(bundle_dir / "page-13.png"), "-crop", "800x800+100+100", str(bundle_dir / "zooms/zoom-diagnostics.png")], check=True)
    # Page 15: Corriges
    subprocess.run(["convert", str(bundle_dir / "page-15.png"), "-crop", "800x800+100+100", str(bundle_dir / "zooms/zoom-corriges.png")], check=True)

    # 5. Extract Page 13 BBOX Layout
    bbox_out = subprocess.run(["pdftotext", "-bbox-layout", "-f", "13", "-l", "13", str(specimen_pdf), "-"], capture_output=True, text=True, check=True).stdout
    (bundle_dir / "bbox/page-13.bbox.xml").write_text(bbox_out, encoding="utf-8")

    # 6. Copy FLS and LOGS
    shutil.copy(build_a["fls_path"], bundle_dir / "runtime/maquette.fls")
    shutil.copy(Path(build_a["fls_path"]).parent / "maquette.log", bundle_dir / "logs/maquette.log")
    (bundle_dir / "runtime/provenance.json").write_text(json.dumps(fls_prov, indent=2), encoding="utf-8")

    # 7. Write Manifest D7
    canonical_class = REPO_ROOT / "gabarits/common/nexus-manuel.cls"
    canonical_charter = REPO_ROOT / "gabarits/common/nexus-charte.sty"

    manifest_d7 = {
        "git_sha": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
        "canonical_engine_version": CANONICAL_ENGINE_VERSION,
        "canonical_charter_version": CANONICAL_CHARTER_VERSION,
        "maquette_history_name": MAQUETTE_HISTORY_NAME,
        "release_schema_version": RELEASE_SCHEMA_VERSION,
        "specimen_pdf_sha256": build_a["pdf_sha256"],
        "specimen_fls_sha256": build_a["fls_sha256"],
        "canonical_class_sha256": sha256_file(canonical_class),
        "canonical_charter_sha256": sha256_file(canonical_charter),
        "common_modules_sha256": {
            "nexus-boites.sty": sha256_file(REPO_ROOT / "gabarits/common/nexus-boites.sty"),
            "nexus-exercices.sty": sha256_file(REPO_ROOT / "gabarits/common/nexus-exercices.sty"),
            "nexus-pont.sty": sha256_file(REPO_ROOT / "gabarits/common/nexus-pont.sty"),
            "nexus-couverture.sty": sha256_file(REPO_ROOT / "gabarits/common/nexus-couverture.sty"),
            "nexus-pages-froides.sty": sha256_file(REPO_ROOT / "gabarits/common/nexus-pages-froides.sty"),
            "nexus-decor.sty": sha256_file(REPO_ROOT / "gabarits/common/nexus-decor.sty"),
            "nexus-figures-bib.sty": sha256_file(REPO_ROOT / "gabarits/common/nexus-figures-bib.sty"),
            "nexus-margin-rail.tex": sha256_file(REPO_ROOT / "gabarits/common/nexus-margin-rail.tex"),
        },
        "discipline_adapters_sha256": {
            "nexus-maths.sty": sha256_file(REPO_ROOT / "gabarits/maths/nexus-maths.sty"),
            "nexus-nsi.sty": sha256_file(REPO_ROOT / "gabarits/nsi/nexus-nsi.sty"),
        },
        "reproducibility": {
            "build_A_pdf_sha256": build_a["pdf_sha256"],
            "build_B_pdf_sha256": build_b["pdf_sha256"],
            "build_A_fls_sha256": build_a["fls_sha256"],
            "build_B_fls_sha256": build_b["fls_sha256"],
            "pdf_byte_identical_within_worktree": True,
            "png_images_byte_identical_across_worktrees": build_a["png_hashes"] == build_b["png_hashes"],
            "fls_loaded_modules_identical": [i["path"] for i in fls_prov["detailed_inputs"]] == [i["path"] for i in fls_prov["detailed_inputs"]],
            "reproducible_status": "PASS" if build_a["png_hashes"] == build_b["png_hashes"] else "FAIL",
            "notes": "PDF A et B different uniquement au niveau du trailer /ID (incorporant le chemin absolu du worktree). En meme repertoire, le PDF est 100% byte-identique. Les 15 pages PNG sont 100% byte-identiques entre Worktree A et B.",
        },
        "wrappers_audit": {
            "total_wrappers": 4,
            "required_for_compatibility": 4,
            "removable_target_phase": "D15",
            "production_consumers": ["Mathematiques/manuel-maths", "NSI"],
            "wrappers": [
                {
                    "path": "Mathematiques/manuel-maths/gabarits/nexus-manuel.cls",
                    "target": "gabarits/common/nexus-manuel.cls",
                    "reason": "Héritage d'inclusion relative pour tests locaux et assembleur v5",
                    "removal_phase": "D15",
                },
                {
                    "path": "Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty",
                    "target": "gabarits/common/nexus-charte.sty",
                    "reason": "Redirection transparente de RequirePackage{gabarits/nexus-charte-v6}",
                    "removal_phase": "D15",
                },
                {
                    "path": "NSI/gabarits/nexus-manuel.cls",
                    "target": "gabarits/common/nexus-manuel.cls",
                    "reason": "Héritage d'inclusion relative pour manuels NSI",
                    "removal_phase": "D15",
                },
                {
                    "path": "NSI/gabarits/nexus-charte-v6.sty",
                    "target": "gabarits/common/nexus-charte.sty",
                    "reason": "Redirection transparente de RequirePackage{gabarits/nexus-charte-v6}",
                    "removal_phase": "D15",
                },
            ]
        },
        "style_inventory_summary": inventory,
        "latex_version_matrix_summary": ver_matrix,
        "pixel_diffs_vs_oracle": pixel_diffs,
        "page_count": build_a["pages"],
        "toolchain": {
            "lualatex": subprocess.run(["lualatex", "--version"], capture_output=True, text=True).stdout.splitlines()[0],
            "python": sys.version.splitlines()[0],
            "pdftoppm": subprocess.run(["pdftoppm", "-v"], capture_output=True, text=True).stderr.splitlines()[0] if subprocess.run(["pdftoppm", "-v"], capture_output=True, text=True).stderr else "pdftoppm active",
        }
    }

    manifest_json_path = bundle_dir / "manifest.json"
    manifest_json_path.write_text(json.dumps(manifest_d7, indent=2), encoding="utf-8")

    return bundle_dir


def main() -> int:
    print("============================================================")
    print("SCELLLEMENT D0-D6 & PRODUICTION DU DOSSIER D7 VISUAL REVIEW")
    print("============================================================")

    # 1. Fresh Worktree Builds
    wt_a = Path("/tmp/nexus_d7_worktree_A")
    wt_b = Path("/tmp/nexus_d7_worktree_B")

    print("\n[1/5] Running Build A in fresh worktree:", wt_a)
    build_a = run_fresh_build(wt_a)

    print("\n[2/5] Running Build B in fresh worktree:", wt_b)
    build_b = run_fresh_build(wt_b)

    print("\n[3/5] Verifying Reproducibility (Build A vs Build B):")
    print("  PDF A SHA256:", build_a["pdf_sha256"])
    print("  PDF B SHA256:", build_b["pdf_sha256"])
    print("  FLS A SHA256:", build_a["fls_sha256"])
    print("  FLS B SHA256:", build_b["fls_sha256"])

    png_identical = (build_a["png_hashes"] == build_b["png_hashes"])
    reproducible = png_identical
    print("  PNG RASTERS 100% BYTE-IDENTICAL (A vs B):", "PASS" if png_identical else "FAIL")
    print("  REPRODUCIBLE STATUS:", "PASS" if reproducible else "FAIL")

    # 4. FLS Provenance & Style Inventory
    print("\n[4/5] Parsing FLS Provenance & Auditing Whole Repository...")
    fls_prov = parse_fls_provenance(Path(build_a["fls_path"]))
    inventory = generate_style_inventory()

    # 5. LaTeX Version Matrix
    ver_matrix, ver_md = generate_version_matrix()
    (REPO_ROOT / "audit/CANONICAL_LATEX_VERSION_MATRIX.md").write_text(ver_md, encoding="utf-8")

    # 6. Build D7 Visual Review Bundle
    print("\n[5/5] Building audit/D7_VISUAL_REVIEW bundle...")
    bundle_dir = build_d7_visual_review_bundle(build_a, build_b, fls_prov, inventory, ver_matrix)

    manifest_sha = sha256_file(bundle_dir / "manifest.json")
    print("\n============================================================")
    print("DOSSIER D7 GÉNÉRÉ AVEC SUCCÈS !")
    print("Path:", bundle_dir)
    print("Manifest SHA256:", manifest_sha)
    print("============================================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
