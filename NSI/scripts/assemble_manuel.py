"""Build the seven canonical variants of the 1NSI manual."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import assemble as legacy
from common import ROOT as PROJECT_ROOT


ROOT = PROJECT_ROOT
BOOK_ID = "1NSI"
CHAPITRES = [
    "1NSI-TYPES-BASE",
    "1NSI-TYPES-CONSTRUITS",
    "1NSI-TABLES",
    "1NSI-LANGAGE",
    "1NSI-ALGO-PARCOURS-TRIS",
    "1NSI-ALGO-DICHO-GLOUTON-KNN",
    "1NSI-WEB-IHM",
    "1NSI-ARCHITECTURE-OS",
    "1NSI-RESEAUX",
    "1NSI-PROJET-METHODES",
]
ORDER = [
    ("cours", "00_ouverture"),
    ("cours", "01_diagnostic"),
    ("cours", "02_activites"),
    ("cours", "1*"),
    ("methodes", "*"),
    ("exercices", "*"),
    ("coups_de_pouce", "*"),
    ("cours", "07_td*"),
    ("projet", "*"),
    ("qcm", "*"),
    ("evaluations", "*"),
    ("ece", "*"),
    ("remediation", "*"),
    ("amenagee", "*"),
    ("corriges", "*"),
    ("professeur", "*"),
]
VARIANTS = [
    "eleve",
    "professeur",
    "methodes",
    "remediation",
    "amenagee",
    "evaluations",
    "projets",
]
VARIANT_ORDERS = {
    "eleve": [
        ("cours", "00_ouverture"),
        ("cours", "01_diagnostic"),
        ("cours", "02_activites"),
        ("cours", "1*"),
        ("methodes", "*"),
        ("exercices", "*"),
        ("coups_de_pouce", "*"),
        ("cours", "07_td*"),
        ("projet", "*"),
        ("qcm", "*"),
        ("ece", "*"),
    ],
    "professeur": [
        ("cours", "00_ouverture"),
        ("cours", "01_diagnostic"),
        ("cours", "02_activites"),
        ("cours", "1*"),
        ("methodes", "*"),
        ("exercices", "*"),
        ("coups_de_pouce", "*"),
        ("cours", "07_td*"),
        ("projet", "*"),
        ("qcm", "*"),
        ("evaluations", "*"),
        ("ece", "*"),
        ("remediation", "*"),
        ("amenagee", "*"),
        ("corriges", "*"),
        ("professeur", "*"),
    ],
    "methodes": [("methodes", "*")],
    "remediation": [("remediation", "*")],
    "amenagee": [("amenagee", "*")],
    "evaluations": [("evaluations", "*")],
    "projets": [("projet", "*")],
}
ELEVE_VARIANTS = ["eleve", "methodes", "remediation", "amenagee", "projets"]
ELEVE_ALLOWED_TYPES = [
    "cours",
    "td",
    "methode",
    "exercice",
    "coup_de_pouce",
    "projet",
    "qcm",
    "qcm_diagnostics",
    "ece",
    "remediation",
    "amenagee",
]
ELEVE_EXCLUDES = ["corriges", "evaluations", "professeur"]

META_PREFIX = "% META:"
REQUIRED_META_FIELDS = ("id", "chapitre", "type_objet", "status")
TEACHER_VARIANT_SETUP = r"\nxVersionProfesseurtrue"
VARIANT_LABELS = {
    "eleve": "manuel élève",
    "professeur": "manuel professeur",
    "methodes": "livret méthodes",
    "remediation": "livret remédiation",
    "amenagee": "version aménagée",
    "evaluations": "banque d'évaluations",
    "projets": "livret projets",
}


@dataclass(frozen=True)
class ManualContext:
    variant: str
    manifest: dict[str, object]
    files_by_chapter: dict[str, tuple[Path, ...]]
    output_stem: str


def _validate_variant(variant: str) -> None:
    if variant not in VARIANTS:
        supported = VARIANTS[0]
        for index in range(1, VARIANTS.__len__()):
            supported = f"{supported}, {VARIANTS[index]}"
        raise ValueError(
            f"Variante manuelle non prise en charge : {variant!r}. "
            f"Variantes autorisees : {supported}."
        )


def _metadata(path: Path, chapter: str) -> dict[str, object]:
    try:
        with path.open(encoding="utf-8") as stream:
            first_line = stream.readline().strip()
    except (OSError, UnicodeError) as error:
        raise ValueError(f"Objet META illisible : {path}") from error
    if not first_line.startswith(META_PREFIX):
        raise ValueError(f"En-tete META absent : {path}")
    try:
        metadata = json.loads(first_line.removeprefix(META_PREFIX).strip())
    except json.JSONDecodeError as error:
        raise ValueError(f"En-tete META invalide : {path}") from error
    if not isinstance(metadata, dict):
        raise ValueError(f"En-tete META non objet : {path}")
    invalid_fields = [
        field
        for field in REQUIRED_META_FIELDS
        if not isinstance(metadata.get(field), str) or not metadata[field].strip()
    ]
    if invalid_fields:
        raise ValueError(
            f"Champs META absents ou invalides ({', '.join(invalid_fields)}) : {path}"
        )
    source_subtype = metadata.get("sous_type")
    if "sous_type" in metadata and (
        not isinstance(source_subtype, str) or not source_subtype.strip()
    ):
        raise ValueError(f"Champ META sous_type invalide : {path}")
    if metadata.get("chapitre") != chapter:
        raise ValueError(f"Chapitre META incoherent : {path}")
    return metadata


def _tracked_object_paths() -> frozenset[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--", "chapitres"],
            cwd=ROOT,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError("Impossible de lire les fichiers suivis Git 1NSI.") from error
    return frozenset(
        ROOT / os.fsdecode(relative)
        for relative in result.stdout.split(b"\0")
        if relative and relative.endswith(b".tex")
    )


def _confined_object(chapter_dir: Path, path: Path) -> Path:
    if path.is_symlink():
        raise ValueError(f"Objet META symbolique interdit : {path}")
    relative = path.relative_to(chapter_dir).as_posix()
    try:
        resolved = legacy._resolve_under(chapter_dir, relative, "L'objet META")
    except ValueError as error:
        raise ValueError(f"Objet META hors du chapitre : {path}") from error
    if resolved != path.absolute():
        raise ValueError(f"Chemin d'objet META symbolique interdit : {path}")
    return resolved


def collect_variant_objects(variant: str) -> list[Path]:
    """Select META objects in the same chapter/rule order as the inventory."""

    _validate_variant(variant)
    if VARIANT_ORDERS["professeur"] != ORDER:
        raise RuntimeError("ORDER et la variante professeur divergent.")
    # The AST gate requires audited mutable literals to remain indexed in place.
    student_variant = variant in ELEVE_VARIANTS
    tracked_objects = _tracked_object_paths()
    selected: list[Path] = []
    seen: set[Path] = set()
    for chapter in CHAPITRES:
        chapter_dir = legacy._resolve_under(
            ROOT / "chapitres", chapter, "Le chapitre"
        )
        if not chapter_dir.is_dir():
            raise FileNotFoundError(f"Chapitre introuvable : {chapter}")
        if variant == "professeur":
            rule_count = ORDER.__len__()
        else:
            rule_count = VARIANT_ORDERS[variant].__len__()
        for rule_index in range(rule_count):
            if variant == "professeur":
                directory = ORDER[rule_index][0]
                pattern = ORDER[rule_index][1]
            else:
                directory = VARIANT_ORDERS[variant][rule_index][0]
                pattern = VARIANT_ORDERS[variant][rule_index][1]
            if student_variant and directory in ELEVE_EXCLUDES:
                continue
            for path in sorted((chapter_dir / directory).glob(f"{pattern}.tex")):
                if path not in tracked_objects:
                    continue
                path = _confined_object(chapter_dir, path)
                metadata = _metadata(path, chapter)
                if (
                    student_variant
                    and metadata["type_objet"] not in ELEVE_ALLOWED_TYPES
                ):
                    continue
                if path not in seen:
                    seen.add(path)
                    selected.append(path)
    return selected


def _load_manifest() -> dict[str, object]:
    manifest = legacy.load_book_manifest(BOOK_ID)
    declared_chapters = [entry["id"] for entry in manifest["chapters"]]
    if declared_chapters != CHAPITRES:
        raise ValueError("Le manifeste 1NSI diverge du contrat CHAPITRES.")
    return manifest


def _manual_context(variant: str) -> ManualContext:
    _validate_variant(variant)
    manifest = _load_manifest()
    selected = collect_variant_objects(variant)
    if not selected:
        raise ValueError(f"Aucun objet eligible pour la variante {variant}.")
    files_by_chapter: dict[str, list[Path]] = {chapter: [] for chapter in CHAPITRES}
    chapters_root = (ROOT / "chapitres").resolve()
    for path in selected:
        chapter = path.resolve().relative_to(chapters_root).parts[0]
        files_by_chapter[chapter].append(path)
    return ManualContext(
        variant=variant,
        manifest=manifest,
        files_by_chapter={
            chapter: tuple(files) for chapter, files in files_by_chapter.items()
        },
        output_stem=f"MANUEL_1NSI_{variant}",
    )


def _title(manifest: dict[str, object], variant: str) -> str:
    title = str(manifest["title"])
    if variant == "eleve":
        return title
    return f"{title} - {VARIANT_LABELS[variant]}"


def _variant_setup(variant: str) -> str:
    return (
        legacy.STUDENT_VARIANT_SETUP
        if variant in ELEVE_VARIANTS
        else TEACHER_VARIANT_SETUP
    )


def _render_context(context: ManualContext) -> str:
    return legacy.render_book_master_from_files(
        context.manifest,
        context.files_by_chapter,
        title=_title(context.manifest, context.variant),
        variant_setup=_variant_setup(context.variant),
    )


def render_manual_master(variant: str) -> str:
    return _render_context(_manual_context(variant))


def canonical_output_path(variant: str) -> Path:
    _validate_variant(variant)
    build_dir = legacy._resolve_under(
        ROOT, "build/MANUEL_1NSI", "Le repertoire de sortie"
    )
    return legacy._book_output_path(build_dir, f"MANUEL_1NSI_{variant}.pdf")


def build_manual(variant: str) -> int:
    _validate_variant(variant)
    context = _manual_context(variant)
    build_dir = legacy._resolve_under(
        ROOT, "build/MANUEL_1NSI", "Le repertoire de sortie"
    )
    build_dir.mkdir(parents=True, exist_ok=True)
    canonical_pdf = legacy._book_output_path(
        build_dir, f"{context.output_stem}.pdf"
    )
    canonical_pdf.unlink(missing_ok=True)
    promoted = False
    student_variant = variant in ELEVE_VARIANTS
    try:
        with tempfile.TemporaryDirectory(
            prefix=f".{context.output_stem}-", dir=build_dir
        ) as staging_name:
            staging = Path(staging_name).resolve()
            if not staging.is_relative_to(build_dir):
                raise ValueError("Le staging resout hors du repertoire de sortie.")
            tex_path = staging / f"{context.output_stem}.tex"
            tex_path.write_text(_render_context(context), encoding="utf-8")
            result = legacy.compile_tex(
                tex_path,
                staging,
                source_date_epoch=int(context.manifest["source_date_epoch"]),
            )
            if result:
                return result
            staged_pdf = staging / f"{context.output_stem}.pdf"
            staged_log = staging / f"{context.output_stem}.log"
            if legacy.preflight_book_pdf(
                staged_pdf,
                staged_log,
                check_student_leaks=student_variant,
            ):
                return 1
            legacy._promote_book_artifacts(staging, build_dir, context.output_stem)
            promoted = True
            print(f"PDF canonique : {canonical_pdf}")
            return 0
    finally:
        if not promoted:
            canonical_pdf.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", default="eleve")
    arguments = parser.parse_args(argv)
    return build_manual(arguments.variant)


if __name__ == "__main__":
    sys.exit(main())
