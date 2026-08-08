"""Assemblage (R5/F06) : génère le .tex maître d'un chapitre ou d'un manuel
depuis les objets, puis compile (LuaLaTeX ×2).

Déclinaisons chapitre : complet|methodes|parcours1|remediation|professeur|amenagee.
Déclinaisons livre : complet|methodes|remediation|amenagee.
"""
import argparse
import json
import re
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
}
BOOK_VARIANT_LABEL = {
    "complet": "manuel complet",
    "methodes": "livret méthodes",
    "remediation": "livret remédiation",
    "amenagee": "version aménagée",
}
BOOK_VARIANTS = frozenset(BOOK_VARIANT_SUFFIX)
BOOK_MANIFEST_KEYS = frozenset({
    "book_id", "title", "subtitle", "matiere", "niveau", "author",
    "subject", "keywords", "source_date_epoch", "output_name", "chapters",
})
BOOK_STRING_FIELDS = frozenset(
    {"book_id", "title", "subtitle", "matiere", "niveau", "author",
     "subject", "keywords", "output_name"}
)
CHAPTER_ENTRY_KEYS = frozenset({"id", "title"})
SAFE_COMPONENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")
LATEX_ESCAPES = {
    "#": r"\#",
    "_": r"\_",
    "%": r"\%",
    "&": r"\&",
    "$": r"\$",
    "{": r"\{",
    "}": r"\}",
    "\\": r"\textbackslash{}",
    "^": r"\textasciicircum{}",
    "~": r"\textasciitilde{}",
}
ORDER = [  # les 9 temps du gabarit (docs/01 Partie 3)
    ("cours", "00_ouverture"), ("cours", "01_diagnostic"), ("cours", "02_activites"),
    ("cours", "1*"), ("methodes", "*"), ("exercices", "*"), ("coups_de_pouce", "*"),
    ("cours", "07_td*"), ("projet", "*"), ("qcm", "*"), ("evaluations", "*"), ("ece", "*"), ("remediation", "*"),
]
BOOK_STUDENT_ORDER = [
    ("cours", "00_ouverture"), ("cours", "01_diagnostic"), ("cours", "02_activites"),
    ("cours", "1*"), ("methodes", "*"), ("exercices", "*"), ("coups_de_pouce", "*"),
    ("cours", "07_td*"), ("projet", "*"), ("qcm", "*"), ("ece", "*"),
]


def latex_escape(value: str) -> str:
    return "".join(LATEX_ESCAPES.get(character, character) for character in value)


def _validate_component(value: object, field: str) -> str:
    if not isinstance(value, str) or not SAFE_COMPONENT.fullmatch(value):
        raise ValueError(f"{field} doit être un composant de chemin sûr.")
    return value


def _resolve_under(base: Path, relative: str, field: str) -> Path:
    resolved_base = base.resolve()
    resolved = (resolved_base / relative).resolve()
    if not resolved.is_relative_to(resolved_base):
        raise ValueError(f"{field} résout hors du dépôt.")
    return resolved


def _validate_book_manifest(manifest: object, requested_book_id: str) -> dict:
    if not isinstance(manifest, dict):
        raise ValueError("Le manifeste doit être un objet JSON.")
    if set(manifest) != BOOK_MANIFEST_KEYS:
        raise ValueError("Les clés du manifeste ne correspondent pas au schéma fermé.")
    for field in BOOK_STRING_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} doit être une chaîne non vide.")
    if manifest["book_id"] != requested_book_id:
        raise ValueError("Le book_id du manifeste ne correspond pas au fichier demandé.")
    _validate_component(manifest["book_id"], "book_id")
    _validate_component(manifest["output_name"], "output_name")
    epoch = manifest["source_date_epoch"]
    if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
        raise ValueError("source_date_epoch doit être un entier positif ou nul.")
    chapters = manifest["chapters"]
    if not isinstance(chapters, list) or not chapters:
        raise ValueError("chapters doit être une liste non vide.")
    seen = set()
    for index, entry in enumerate(chapters):
        if not isinstance(entry, dict) or set(entry) != CHAPTER_ENTRY_KEYS:
            raise ValueError(f"L'entrée chapitre {index} ne respecte pas le schéma fermé.")
        chapter_id = _validate_component(entry.get("id"), f"chapitre {index} id")
        title = entry.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"Le titre du chapitre {index} doit être une chaîne non vide.")
        if chapter_id in seen:
            raise ValueError(f"Identifiant de chapitre dupliqué : {chapter_id}")
        seen.add(chapter_id)
    return manifest


def _collect_in_order(chap_dir: Path, order: list[tuple[str, str]]) -> list[Path]:
    files = []
    for sub, pat in order:
        files += sorted(
            (chap_dir / sub).glob(f"{pat}.tex" if not pat.endswith("*") else pat + ".tex")
        )
    seen, out = set(), []
    for path in files:
        if path not in seen:
            seen.add(path)
            out.append(path)
    return out


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
    return _collect_in_order(chap_dir, ORDER)


def collect_book_files(chap_dir: Path, variant: str) -> list[Path]:
    _validate_book_variant(variant)
    files = (
        _collect_in_order(chap_dir, BOOK_STUDENT_ORDER)
        if variant == "complet"
        else collect(chap_dir, variant)
    )
    return [
        path
        for path in files
        if not any(
            marker in part.lower()
            for part in path.relative_to(ROOT).parts
            for marker in ("corrige", "professeur")
        )
    ]


def compile_tex(tex_path: Path, build_dir: Path) -> int:
    import os

    env = os.environ.copy()
    env["TEXINPUTS"] = f"./gabarits/:{env.get('TEXINPUTS', '')}"
    for _ in range(2):
        proc = subprocess.run(
            ["lualatex", "-interaction=nonstopmode", "-halt-on-error",
             f"-output-directory={build_dir}", str(tex_path)],
            capture_output=True, cwd=ROOT, env=env)
        if proc.returncode != 0:
            print(proc.stdout.decode("utf-8", errors="replace")[-3000:])
            return 1
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
    _validate_component(book_id, "book_id")
    manifest_path = _resolve_under(
        ROOT / "manifests" / "books", f"{book_id}.json", "Le manifeste"
    )
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifeste introuvable : {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return _validate_book_manifest(manifest, book_id)


def _chapter_entry_id(entry: str | dict) -> str:
    if isinstance(entry, dict):
        return entry["id"]
    return entry


def _chapter_entry_title(entry: str | dict) -> str:
    if isinstance(entry, dict) and entry.get("title"):
        return entry["title"]
    return _chapter_entry_id(entry)


def collect_book_chapters(book_id: str, variant: str = "complet") -> list[Path]:
    _validate_book_variant(variant)
    manifest = load_book_manifest(book_id)
    chapter_dirs = []
    for entry in manifest["chapters"]:
        chapter_id = _chapter_entry_id(entry)
        chap_dir = _resolve_under(ROOT / "chapitres", chapter_id, "Le chapitre")
        if not chap_dir.is_dir():
            raise FileNotFoundError(f"Chapitre introuvable : {chapter_id}")
        if collect_book_files(chap_dir, variant):
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


def _validate_book_variant(variant: str) -> None:
    if variant not in BOOK_VARIANTS:
        supported = ", ".join(sorted(BOOK_VARIANTS))
        raise ValueError(
            f"Variante de livre non prise en charge : {variant}. "
            f"Variantes autorisées : {supported}."
        )


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
        chap_dir = _resolve_under(ROOT / "chapitres", chapter_id, "Le chapitre")
        inputs = "\n".join(
            f"\\input{{{path.relative_to(ROOT)}}}"
            for path in collect_book_files(chap_dir, variant)
        )
        parts.append(
            "\n".join(
                [
                    f"\\chapter{{{latex_escape(chapter_title)}}}",
                    f"\\label{{chap:{chapter_id.lower()}}}",
                    inputs,
                ]
            )
        )
    master = (ROOT / "gabarits" / "book_master.tex").read_text(encoding="utf-8")
    return (
        master.replace("%%MATIERE%%", latex_escape(manifest["matiere"]))
        .replace("%%NIVEAU%%", latex_escape(manifest["niveau"]))
        .replace("%%TITLE%%", latex_escape(_book_title(manifest, variant)))
        .replace("%%SUBTITLE%%", latex_escape(manifest["subtitle"]))
        .replace("%%PDF_AUTHOR%%", latex_escape(manifest["author"]))
        .replace("%%PDF_SUBJECT%%", latex_escape(manifest["subject"]))
        .replace("%%PDF_KEYWORDS%%", latex_escape(manifest["keywords"]))
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
    _validate_book_variant(variant)
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
        _validate_book_variant(variant)
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
