"""Contract tests for the canonical 1NSI manual assembler."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
ASSEMBLER_PATH = ROOT / "scripts" / "assemble_manuel.py"
CHAPTERS = (
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
)
VARIANTS = (
    "eleve",
    "professeur",
    "methodes",
    "remediation",
    "amenagee",
    "evaluations",
    "projets",
)
STUDENT_VARIANTS = (
    "eleve",
    "methodes",
    "remediation",
    "amenagee",
    "projets",
)


def _load_assembler():
    assert ASSEMBLER_PATH.is_file(), "assemble_manuel.py doit etre cree"
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    spec = importlib.util.spec_from_file_location("assemble_manuel", ASSEMBLER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def assembler():
    return _load_assembler()


def _manifest() -> dict[str, object]:
    return {
        "book_id": "1NSI",
        "title": "Manuel NSI Premiere",
        "subtitle": "Edition de test",
        "matiere": "NSI",
        "niveau": "Premiere",
        "author": "Nexus Reussite",
        "subject": "Manuel scolaire NSI",
        "keywords": "NSI, Premiere",
        "source_date_epoch": 1786147200,
        "output_name": "MANUEL_1NSI_v1",
        "chapters": [
            {"id": chapter, "title": f"Chapitre {index}"}
            for index, chapter in enumerate(CHAPTERS, start=1)
        ],
    }


def _write_meta(path: Path, chapter: str, source_type: str, suffix: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "id": f"{chapter}-{suffix}",
        "chapitre": chapter,
        "type_objet": source_type,
        "status": "approved",
    }
    path.write_text(
        "% META: " + json.dumps(metadata, sort_keys=True) + "\nContenu.\n",
        encoding="utf-8",
    )


def _prepare_root(root: Path) -> None:
    manifest = root / "manifests" / "books" / "1NSI.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps(_manifest()), encoding="utf-8")
    master = root / "gabarits" / "book_master.tex"
    master.parent.mkdir(parents=True)
    master.write_text(
        "%%VARIANT_SETUP%%\n"
        "%%MATIERE%% %%NIVEAU%% %%TITLE%% %%SUBTITLE%%\n"
        "%%PDF_AUTHOR%% %%PDF_SUBJECT%% %%PDF_KEYWORDS%%\n"
        "%%CONTENT%%\n",
        encoding="utf-8",
    )
    for index, chapter in enumerate(CHAPTERS, start=1):
        _write_meta(
            root / "chapitres" / chapter / "cours" / f"{index:02d}_cours.tex",
            chapter,
            "cours",
            f"COURS-{index}",
        )


def _patch_root(monkeypatch, assembler, root: Path) -> None:
    monkeypatch.setattr(assembler, "ROOT", root)
    monkeypatch.setattr(assembler.legacy, "ROOT", root)


def test_canonical_literals_are_exact_and_runtime_closed(assembler):
    assert tuple(assembler.CHAPITRES) == CHAPTERS
    assert tuple(assembler.VARIANTS) == VARIANTS
    assert tuple(assembler.VARIANT_ORDERS) == VARIANTS
    assert tuple(assembler.ELEVE_VARIANTS) == STUDENT_VARIANTS
    assert assembler.VARIANT_ORDERS["professeur"] == assembler.ORDER

    business_directories = {
        "cours",
        "methodes",
        "exercices",
        "coups_de_pouce",
        "projet",
        "qcm",
        "evaluations",
        "ece",
        "remediation",
        "amenagee",
        "corriges",
        "professeur",
    }
    assert {directory for directory, _pattern in assembler.ORDER} == business_directories
    assert set(assembler.ELEVE_EXCLUDES) >= {"corriges", "evaluations", "professeur"}
    assert {"corrige", "corrige_evaluation"}.isdisjoint(
        assembler.ELEVE_ALLOWED_TYPES
    )


def test_student_selection_includes_contractual_ece_object(
    monkeypatch, tmp_path, assembler
):
    root = tmp_path / "NSI"
    _prepare_root(root)
    ece = root / "chapitres" / CHAPTERS[0] / "ece" / "01_ece.tex"
    _write_meta(ece, CHAPTERS[0], "ece", "ECE-1")
    _patch_root(monkeypatch, assembler, root)

    selected = assembler.collect_variant_objects("eleve")

    assert "ece" in assembler.ELEVE_ALLOWED_TYPES
    assert ece in selected


def test_runtime_selection_covers_all_professor_objects_and_is_student_safe(assembler):
    selected = {
        variant: assembler.collect_variant_objects(variant) for variant in VARIANTS
    }
    professor = selected["professeur"]
    corrections = [path for path in professor if path.parent.name == "corriges"]
    evaluation_types = [
        json.loads(path.read_text(encoding="utf-8").splitlines()[0][7:].strip())[
            "type_objet"
        ]
        for path in selected["evaluations"]
    ]

    assert len(professor) == 339
    assert len(corrections) == 109
    assert set(corrections) == set(ROOT.glob("chapitres/1NSI-*/corriges/*.tex"))
    assert evaluation_types.count("evaluation") == 20
    assert evaluation_types.count("corrige_evaluation") == 18
    for variant in STUDENT_VARIANTS:
        assert selected[variant]
        assert not any(path.parent.name == "corriges" for path in selected[variant])
        assert not any("professeur" in path.parts for path in selected[variant])
    assert {path.parent.name for path in selected["methodes"]} == {"methodes"}
    assert {path.parent.name for path in selected["remediation"]} == {"remediation"}
    assert {path.parent.name for path in selected["amenagee"]} == {"amenagee"}
    assert {path.parent.name for path in selected["evaluations"]} == {"evaluations"}
    assert {path.parent.name for path in selected["projets"]} == {"projet"}
    assert not {
        "evaluations",
        "remediation",
        "corriges",
        "professeur",
    } & {path.parent.name for path in selected["eleve"]}


@pytest.mark.parametrize("variant", STUDENT_VARIANTS)
def test_student_variants_render_student_setup(assembler, variant):
    tex = assembler.render_manual_master(variant)

    assert r"\nxVersionProfesseurfalse" in tex
    assert r"\RenewDocumentEnvironment{corrige}{m +b}{}{}" in tex
    assert r"\nxVersionProfesseurtrue" not in tex
    assert "%%VARIANT_SETUP%%" not in tex


@pytest.mark.parametrize("variant", ["professeur", "evaluations"])
def test_teacher_variants_render_teacher_setup_without_neutralizing_corrections(
    assembler, variant
):
    tex = assembler.render_manual_master(variant)

    assert r"\nxVersionProfesseurtrue" in tex
    assert r"\RenewDocumentEnvironment{corrige}{m +b}{}{}" not in tex
    assert "%%VARIANT_SETUP%%" not in tex


@pytest.mark.parametrize("variant", VARIANTS)
def test_canonical_output_path_is_variant_specific(assembler, variant):
    assert assembler.canonical_output_path(variant) == (
        ROOT / "build" / "MANUEL_1NSI" / f"MANUEL_1NSI_{variant}.pdf"
    )


@pytest.mark.parametrize("variant", ["", "complet", "TNSI", "unknown"])
def test_unknown_or_empty_variant_fails_before_writing(
    monkeypatch, tmp_path, assembler, variant
):
    root = tmp_path / "NSI"
    _patch_root(monkeypatch, assembler, root)

    with pytest.raises(ValueError, match="Variante"):
        assembler.build_manual(variant)

    assert not (root / "build").exists()


def test_known_variant_without_eligible_objects_fails_before_writing(
    monkeypatch, tmp_path, assembler
):
    root = tmp_path / "NSI"
    _prepare_root(root)
    _patch_root(monkeypatch, assembler, root)

    with pytest.raises(ValueError, match="Aucun objet"):
        assembler.build_manual("methodes")

    assert not (root / "build").exists()


def test_selection_rejects_object_symlink_escape(monkeypatch, tmp_path, assembler):
    root = tmp_path / "NSI"
    _prepare_root(root)
    outside = tmp_path / "outside.tex"
    _write_meta(outside, CHAPTERS[0], "methode", "METHODE-EXTERNE")
    linked = root / "chapitres" / CHAPTERS[0] / "methodes" / "linked.tex"
    linked.parent.mkdir(parents=True)
    linked.symlink_to(outside)
    _patch_root(monkeypatch, assembler, root)

    with pytest.raises(ValueError, match="hors du chapitre|symbolique"):
        assembler.collect_variant_objects("methodes")


def test_selection_rejects_business_directory_symlink_escape(
    monkeypatch, tmp_path, assembler
):
    root = tmp_path / "NSI"
    _prepare_root(root)
    outside = tmp_path / "outside-methodes"
    _write_meta(
        outside / "external.tex",
        CHAPTERS[0],
        "methode",
        "METHODE-EXTERNE",
    )
    linked = root / "chapitres" / CHAPTERS[0] / "methodes"
    linked.symlink_to(outside, target_is_directory=True)
    _patch_root(monkeypatch, assembler, root)

    with pytest.raises(ValueError, match="Objet META hors du chapitre"):
        assembler.collect_variant_objects("methodes")


@pytest.mark.parametrize(
    ("variant", "check_student_leaks"),
    [("eleve", True), ("professeur", False), ("evaluations", False)],
)
def test_build_stages_preflights_with_explicit_role_and_promotes_pdf_last(
    monkeypatch, tmp_path, assembler, variant, check_student_leaks
):
    root = tmp_path / "NSI"
    _prepare_root(root)
    if variant == "evaluations":
        for index, chapter in enumerate(CHAPTERS, start=1):
            _write_meta(
                root
                / "chapitres"
                / chapter
                / "evaluations"
                / f"{index:02d}_evaluation.tex",
                chapter,
                "evaluation",
                f"EVAL-{index}",
            )
    _patch_root(monkeypatch, assembler, root)
    preflight_calls = []
    replacements = []
    real_replace = os.replace

    def fake_compile(tex_path, staging, *, source_date_epoch):
        assert staging.parent == root / "build" / "MANUEL_1NSI"
        assert source_date_epoch == 1786147200
        (staging / f"{tex_path.stem}.pdf").write_bytes(b"fresh")
        (staging / f"{tex_path.stem}.log").write_text("clean", encoding="utf-8")
        (staging / f"{tex_path.stem}.aux").write_text("aux", encoding="utf-8")
        return 0

    def fake_preflight(pdf, log, *, check_student_leaks):
        preflight_calls.append((pdf, log, check_student_leaks))
        return 0

    def record_replace(source, destination):
        replacements.append(Path(destination))
        real_replace(source, destination)

    monkeypatch.setattr(assembler.legacy, "compile_tex", fake_compile)
    monkeypatch.setattr(assembler.legacy, "preflight_book_pdf", fake_preflight)
    monkeypatch.setattr(assembler.legacy.os, "replace", record_replace)

    assert assembler.build_manual(variant) == 0
    output = root / "build" / "MANUEL_1NSI" / f"MANUEL_1NSI_{variant}.pdf"
    assert output.read_bytes() == b"fresh"
    assert preflight_calls[0][2] is check_student_leaks
    assert replacements[-1] == output
    assert not list(output.parent.glob(f".MANUEL_1NSI_{variant}-*"))


@pytest.mark.parametrize("failure", ["compile", "preflight"])
def test_failed_build_never_promotes_a_canonical_pdf(
    monkeypatch, tmp_path, assembler, failure
):
    root = tmp_path / "NSI"
    _prepare_root(root)
    _patch_root(monkeypatch, assembler, root)
    build_dir = root / "build" / "MANUEL_1NSI"
    build_dir.mkdir(parents=True)
    canonical = build_dir / "MANUEL_1NSI_eleve.pdf"
    canonical.write_bytes(b"stale")

    def fake_compile(tex_path, staging, *, source_date_epoch):
        if failure == "compile":
            return 1
        (staging / f"{tex_path.stem}.pdf").write_bytes(b"invalid")
        (staging / f"{tex_path.stem}.log").write_text("clean", encoding="utf-8")
        return 0

    def fake_preflight(_pdf, _log, *, check_student_leaks):
        assert failure == "preflight"
        assert check_student_leaks is True
        return 1

    monkeypatch.setattr(assembler.legacy, "compile_tex", fake_compile)
    monkeypatch.setattr(assembler.legacy, "preflight_book_pdf", fake_preflight)
    monkeypatch.setattr(
        assembler.legacy,
        "_promote_book_artifacts",
        lambda *_args: pytest.fail("A failed build must not promote artifacts."),
    )

    assert assembler.build_manual("eleve") == 1
    assert not canonical.exists()
    assert not list(build_dir.glob(".MANUEL_1NSI_eleve-*"))


def test_make_book_dispatches_to_canonical_assembler():
    default_result = subprocess.run(
        ["make", "-n", "book"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    projects_result = subprocess.run(
        ["make", "-n", "book", "VARIANT=projets"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "scripts/assemble_manuel.py --variant eleve" in default_result.stdout
    assert "scripts/assemble_manuel.py --variant projets" in projects_result.stdout
