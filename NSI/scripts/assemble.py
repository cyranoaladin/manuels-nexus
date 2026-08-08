"""Assemblage (R5/F06) : génère le .tex maître d'un chapitre ou d'un manuel
depuis les objets, puis compile (LuaLaTeX ×2).

Déclinaisons : --variant complet|methodes|parcours1|remediation|amenagee
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from common import ROOT
from pdf_integrity import verify_pdf

BOOK_VARIANT_SUFFIX = {
    "complet": "",
    "methodes": "_methodes",
    "remediation": "_remediation",
    "amenagee": "_amenagee",
    "professeur": "_professeur",
    "parcours1": "_parcours1",
}
BOOK_VARIANT_LABEL = {
    "complet": "manuel complet",
    "methodes": "livret méthodes",
    "remediation": "livret remédiation",
    "amenagee": "version aménagée",
    "professeur": "livret professeur",
    "parcours1": "parcours 1",
}
ORDER = [  # les 9 temps du gabarit (docs/01 Partie 3)
    ("cours", "00_ouverture"), ("cours", "01_diagnostic"), ("cours", "02_activites"),
    ("cours", "1*"), ("methodes", "*"), ("exercices", "*"), ("coups_de_pouce", "*"),
    ("cours", "07_td*"), ("projet", "*"), ("qcm", "*"), ("evaluations", "*"), ("ece", "*"), ("remediation", "*"),
]


def collect(chap_dir: Path, variant: str) -> list[Path]:
    if variant == "methodes":
        return sorted((chap_dir / "methodes").glob("*.tex"))
    if variant == "remediation":
        return sorted((chap_dir / "remediation").glob("*.tex"))
    if variant == "amenagee":
        amenagee_dir = chap_dir / "amenagee"
        if amenagee_dir.exists():
            return sorted(amenagee_dir.glob("*.tex"))
        return []
    if variant == "professeur":
        professeur_dir = chap_dir / "professeur"
        if professeur_dir.exists():
            return sorted(professeur_dir.glob("*.tex"))
        return []
    if variant == "parcours1":
        return sorted((chap_dir / "exercices").glob("*.tex"))
    files = []
    for sub, pat in ORDER:
        files += sorted((chap_dir / sub).glob(f"{pat}.tex" if not pat.endswith("*") else pat + ".tex"))
    # dédoublonner en conservant l'ordre
    seen, out = set(), []
    for f in files:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def compile_tex(tex_path: Path, build_dir: Path) -> int:
    import os

    env = os.environ.copy()
    env["TEXINPUTS"] = f"./gabarits/:{env.get('TEXINPUTS', '')}"
    for _ in range(2):
        proc = subprocess.run(
            ["lualatex", "-interaction=nonstopmode",
             f"-output-directory={build_dir}", str(tex_path)],
            capture_output=True, cwd=ROOT, env=env)
    pdf_path = build_dir / (tex_path.stem + ".pdf")
    if not pdf_path.exists():
        print(proc.stdout.decode("utf-8", errors="replace")[-3000:])
        return 1
    log_path = build_dir / (tex_path.stem + ".log")
    if verify_pdf(pdf_path, log_path):
        return 1
    print(f"PDF : {pdf_path} ({pdf_path.stat().st_size // 1024} Ko)")
    return 0


def load_book_manifest(book_id: str) -> dict:
    manifest_path = ROOT / "manifests" / "books" / f"{book_id}.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifeste introuvable : {manifest_path}")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _chapter_entry_id(entry: str | dict) -> str:
    if isinstance(entry, dict):
        return entry["id"]
    return entry


def _chapter_entry_title(entry: str | dict) -> str:
    if isinstance(entry, dict) and entry.get("title"):
        return entry["title"]
    return _chapter_entry_id(entry)


def collect_book_chapters(book_id: str, variant: str = "complet") -> list[Path]:
    manifest = load_book_manifest(book_id)
    chapter_dirs = []
    for entry in manifest["chapters"]:
        chapter_id = _chapter_entry_id(entry)
        chap_dir = ROOT / "chapitres" / chapter_id
        if not chap_dir.exists():
            raise FileNotFoundError(f"Chapitre introuvable : {chapter_id}")
        if collect(chap_dir, variant):
            chapter_dirs.append(chap_dir)
    if not chapter_dirs:
        raise ValueError(
            f"Aucun chapitre éligible pour le livre {book_id} en variante {variant}."
        )
    return chapter_dirs


def _book_title(manifest: dict, variant: str) -> str:
    if variant == "complet":
        return manifest["title"]
    return f"{manifest['title']} — {BOOK_VARIANT_LABEL[variant]}"


def _book_output_name(manifest: dict, variant: str) -> str:
    return f"{manifest['output_name']}{BOOK_VARIANT_SUFFIX[variant]}"


def render_book_master(book_id: str, variant: str = "complet") -> str:
    manifest = load_book_manifest(book_id)
    included_dirs = collect_book_chapters(book_id, variant)
    included_ids = {chap_dir.name for chap_dir in included_dirs}
    parts = []
    for entry in manifest["chapters"]:
        chapter_id = _chapter_entry_id(entry)
        if chapter_id not in included_ids:
            continue
        chapter_title = _chapter_entry_title(entry)
        chap_dir = ROOT / "chapitres" / chapter_id
        inputs = "\n".join(
            f"\\input{{{path.relative_to(ROOT)}}}" for path in collect(chap_dir, variant)
        )
        parts.append(
            "\n".join(
                [
                    f"\\chapter{{{chapter_title}}}",
                    f"\\label{{chap:{chapter_id.lower()}}}",
                    inputs,
                ]
            )
        )
    master = (ROOT / "gabarits" / "book_master.tex").read_text(encoding="utf-8")
    return (
        master.replace("%%MATIERE%%", manifest["matiere"])
        .replace("%%NIVEAU%%", manifest["niveau"])
        .replace("%%TITLE%%", _book_title(manifest, variant))
        .replace("%%SUBTITLE%%", manifest.get("subtitle", ""))
        .replace("%%CONTENT%%", "\n\n".join(parts))
    )


def build_chapter(chap: str, variant: str) -> int:
    chap_dir = ROOT / "chapitres" / chap
    build = ROOT / "build" / chap
    build.mkdir(parents=True, exist_ok=True)
    files = collect(chap_dir, variant)
    if not files:
        print("Aucun objet à assembler.")
        return 1
    inputs = "\n".join(f"\\input{{{f.relative_to(ROOT)}}}" for f in files)
    master = (ROOT / "gabarits" / "chapitre_master.tex").read_text(encoding="utf-8")
    master = master.replace("%%CONTENT%%", inputs).replace("%%CHAP%%", chap)
    tex_path = build / f"{chap}_{variant}.tex"
    tex_path.write_text(master, encoding="utf-8")
    return compile_tex(tex_path, build)


def build_book(book_id: str, variant: str) -> int:
    manifest = load_book_manifest(book_id)
    included = collect_book_chapters(book_id, variant)
    included_ids = [chap.name for chap in included]
    skipped = [
        _chapter_entry_id(entry)
        for entry in manifest["chapters"]
        if _chapter_entry_id(entry) not in set(included_ids)
    ]
    print(f"Variant {variant} — chapitres inclus : {', '.join(included_ids)}")
    if skipped:
        print(f"Variant {variant} — chapitres ignorés : {', '.join(skipped)}")
    build_dir = ROOT / "build" / "books"
    build_dir.mkdir(parents=True, exist_ok=True)
    tex_path = build_dir / f"{_book_output_name(manifest, variant)}.tex"
    tex_path.write_text(render_book_master(book_id, variant), encoding="utf-8")
    return compile_tex(tex_path, build_dir)


def main(*, chap: str | None = None, variant: str = "complet", book: str | None = None) -> int:
    if book:
        return build_book(book, variant)
    if chap is None:
        raise ValueError("Un chapitre ou un livre doit être fourni.")
    return build_chapter(chap, variant)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    target = ap.add_mutually_exclusive_group(required=True)
    target.add_argument("--chap")
    target.add_argument("--book")
    ap.add_argument("--variant", default="complet",
                    choices=["complet", "methodes", "parcours1", "remediation", "professeur", "amenagee"])
    args = ap.parse_args()
    sys.exit(main(chap=args.chap, variant=args.variant, book=args.book))
