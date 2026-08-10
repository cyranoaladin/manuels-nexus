"""Contract tests for the canonical 1NSI manual assembler."""

from __future__ import annotations

import importlib.util
import hashlib
import json
import os
from pathlib import Path
import re
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
RUN_ID = "0123456789abcdef0123456789abcdef"
TOOL_VERSIONS = {
    "lualatex": "LuaHBTeX, Version 1.17.0",
    "pdfinfo": "pdfinfo version 24.02.0",
    "pdffonts": "pdffonts version 24.02.0",
    "python": f"Python {sys.version.split()[0]}",
}


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
    monkeypatch.setattr(assembler, "REPOSITORY_ROOT", root.parent, raising=False)
    monkeypatch.setattr(assembler.legacy, "ROOT", root)
    tracked = frozenset(root.rglob("*.tex"))
    monkeypatch.setattr(assembler, "_tracked_object_paths", lambda: tracked)


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


def test_local_and_observed_manuals_share_source_date_epoch():
    manifest = json.loads(
        (ROOT / "manifests/books/1NSI.json").read_text(encoding="utf-8")
    )
    reproducibility = json.loads(
        (
            ROOT.parent
            / "Mathematiques/manuel-maths/config/reproducible-build.json"
        ).read_text(encoding="utf-8")
    )

    assert manifest["source_date_epoch"] == reproducibility["source_date_epoch"]


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


def test_runtime_selection_ignores_untracked_tex(monkeypatch, tmp_path, assembler):
    root = tmp_path / "NSI"
    _prepare_root(root)
    _patch_root(monkeypatch, assembler, root)
    untracked = root / "chapitres" / CHAPTERS[0] / "cours" / "10_local.tex"
    _write_meta(untracked, CHAPTERS[0], "cours", "LOCAL")

    selected = assembler.collect_variant_objects("eleve")

    assert untracked not in selected


def test_tracked_source_discovery_fails_closed_on_git_error(
    monkeypatch, assembler
):
    def fail_git(*_args, **_kwargs):
        raise subprocess.CalledProcessError(128, ["git", "ls-files"])

    monkeypatch.setattr(assembler.subprocess, "run", fail_git)

    with pytest.raises(RuntimeError, match="fichiers suivis Git"):
        assembler._tracked_object_paths()


@pytest.mark.parametrize(
    "metadata",
    [
        {"chapitre": CHAPTERS[0], "type_objet": "cours", "status": "approved"},
        {"id": "FIXTURE", "chapitre": CHAPTERS[0], "type_objet": "cours"},
        {
            "id": "FIXTURE",
            "chapitre": CHAPTERS[0],
            "type_objet": "cours",
            "status": " ",
        },
        {
            "id": "FIXTURE",
            "chapitre": CHAPTERS[0],
            "type_objet": "cours",
            "status": "approved",
            "sous_type": 42,
        },
        {
            "id": "FIXTURE",
            "chapitre": CHAPTERS[0],
            "type_objet": "cours",
            "status": "approved",
            "sous_type": "",
        },
    ],
    ids=("missing-id", "missing-status", "blank-status", "subtype-type", "subtype-blank"),
)
def test_runtime_selection_rejects_inventory_invalid_meta(
    monkeypatch, tmp_path, assembler, metadata
):
    root = tmp_path / "NSI"
    _prepare_root(root)
    invalid = root / "chapitres" / CHAPTERS[0] / "cours" / "10_invalid.tex"
    invalid.write_text(
        "% META: " + json.dumps(metadata) + "\nContenu.\n",
        encoding="utf-8",
    )
    _patch_root(monkeypatch, assembler, root)

    with pytest.raises(ValueError, match="META"):
        assembler.collect_variant_objects("eleve")


def test_runtime_meta_header_matches_inventory_line_normalization(
    monkeypatch, tmp_path, assembler
):
    root = tmp_path / "NSI"
    _prepare_root(root)
    invalid = root / "chapitres" / CHAPTERS[0] / "cours" / "10_indented.tex"
    invalid.write_text(
        '  % META: {"id":"X","chapitre":"1NSI-TYPES-BASE",'
        '"type_objet":"cours","status":"approved"}\nContenu.\n',
        encoding="utf-8",
    )
    _patch_root(monkeypatch, assembler, root)

    with pytest.raises(ValueError, match="En-tete META absent"):
        assembler.collect_variant_objects("eleve")


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


def test_professor_sources_do_not_nest_braces_in_brace_delimited_lstinline(
    assembler,
):
    offenders = []
    for path in assembler.collect_variant_objects("professeur"):
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if re.search(r"\\lstinline\{[^}\n]*\{", line):
                offenders.append(f"{path.relative_to(ROOT)}:{line_number}")

    assert offenders == []


def test_professor_sources_do_not_use_lstinline_in_tabular_cells(assembler):
    offenders = []
    for path in assembler.collect_variant_objects("professeur"):
        if path.parent.name != "corriges":
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"\\lstinline(?:\{[^}]*\}|(.).*?\1)\s*&", text):
            offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def test_known_long_inline_paragraphs_have_local_ragged_fallback():
    expected = {
        ROOT
        / "chapitres/1NSI-TYPES-CONSTRUITS/corriges/1NSI-TC-CO-024.tex": (
            "Vérification :",
        ),
        ROOT
        / "chapitres/1NSI-PROJET-METHODES/evaluations/1NSI-PM-EVAL-A.tex": (
            "Pourquoi une précondition explicite",
        ),
    }
    for path, markers in expected.items():
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            start = text.index(marker)
            paragraph = text[max(0, start - 40) : start + 400]
            assert r"{\raggedright" in paragraph
            assert r"\par}" in paragraph


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


def test_selection_ignores_untracked_business_directory_symlink_escape(
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

    assert assembler.collect_variant_objects("methodes") == []


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
def test_failed_local_build_preserves_the_previous_canonical_pdf(
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
    assert canonical.read_bytes() == b"stale"
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


def _write_reproducibility_control(repository: Path) -> int:
    epoch = 1770000000
    path = (
        repository
        / "Mathematiques"
        / "manuel-maths"
        / "config"
        / "reproducible-build.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_commit": "a" * 40,
                "source_date_epoch": epoch,
            }
        ),
        encoding="utf-8",
    )
    return epoch


def _observed_build_fakes(monkeypatch, assembler, root: Path):
    observed: dict[str, object] = {"recorder_calls": []}

    def fake_compile(tex_path, staging, *, environment):
        observed["source_date_epoch"] = environment["SOURCE_DATE_EPOCH"]
        master = tex_path.read_text(encoding="utf-8")
        run_marker = next(
            line for line in master.splitlines() if "NEXUS_BUILD_RUN:" in line
        )
        run_id = run_marker.partition("NEXUS_BUILD_RUN:")[2].partition("}")[0]
        (staging / f"{tex_path.stem}.pdf").write_bytes(b"%PDF observed")
        (staging / f"{tex_path.stem}.log").write_text(
            f"NEXUS_BUILD_RUN:{run_id}\nOutput written on observed.pdf (3 pages).\n",
            encoding="utf-8",
        )
        (staging / f"{tex_path.stem}.fls").write_text(
            f"INPUT {tex_path}\n",
            encoding="utf-8",
        )
        return 0

    def fake_recorder(receipt_path, *, environment):
        build_dir = root / "build" / "MANUEL_1NSI"
        variant = receipt_path.name.removeprefix("MANUEL_1NSI_").removesuffix(
            ".receipt.json"
        )
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        master_path = root.parent / receipt["master_path"]
        fls_path = root.parent / receipt["fls_path"]
        assert (build_dir / f"MANUEL_1NSI_{variant}.pdf").is_file()
        assert receipt_path.is_file()
        assert (build_dir / f"MANUEL_1NSI_{variant}.preflight.json").is_file()
        assert f"INPUT {master_path}\n" in fls_path.read_text(encoding="utf-8")
        observed["recorder_calls"].append(receipt_path)
        observed["recorder_environment"] = dict(environment)
        return 0

    monkeypatch.setattr(assembler, "_compile_observed", fake_compile)
    monkeypatch.setattr(
        assembler.legacy,
        "preflight_book_pdf",
        lambda *_args, **_kwargs: 0,
    )
    monkeypatch.setattr(
        assembler.legacy,
        "verify_pdf",
        lambda *_args, **_kwargs: 0,
    )
    monkeypatch.setattr(assembler, "_pdf_page_count", lambda *_args, **_kwargs: 3)
    monkeypatch.setattr(
        assembler,
        "_collect_tool_versions",
        lambda *_args, **_kwargs: dict(TOOL_VERSIONS),
    )
    monkeypatch.setattr(assembler, "_invoke_recorder", fake_recorder)
    monkeypatch.setattr(assembler.secrets, "token_hex", lambda _size: RUN_ID)
    return observed


def test_observed_master_wraps_every_object_with_canonical_trace_markers(
    monkeypatch, tmp_path, assembler
):
    root = tmp_path / "repository" / "NSI"
    _prepare_root(root)
    _patch_root(monkeypatch, assembler, root)
    context = assembler._manual_context("eleve")

    master = assembler._render_context(
        context,
        run_id=RUN_ID,
        repository_root=root.parent,
    )

    assert master.count(f"NEXUS_BUILD_RUN:{RUN_ID}") == 1
    for path in assembler.collect_variant_objects("eleve"):
        canonical = path.relative_to(root.parent).as_posix()
        token = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:40]
        assert master.count(f"NEXUS_OBJECT_BEGIN:{token}") == 1
        assert master.count(f"NEXUS_OBJECT_END:{token}") == 1


def test_observed_compiler_uses_shared_lualatex_recorder_primitive(
    monkeypatch, tmp_path, assembler
):
    staging = tmp_path / "staging"
    staging.mkdir()
    tex_path = staging / "MANUEL_1NSI_eleve.tex"
    tex_path.write_text("master", encoding="utf-8")
    calls = []

    def compile_tex(path, build_dir, **kwargs):
        calls.append((path, build_dir, kwargs))
        (staging / "MANUEL_1NSI_eleve.pdf").write_bytes(b"%PDF")
        (staging / "MANUEL_1NSI_eleve.log").write_text("log", encoding="utf-8")
        (staging / "MANUEL_1NSI_eleve.fls").write_text("fls", encoding="utf-8")
        return 0

    monkeypatch.setattr(assembler.legacy, "compile_tex", compile_tex)
    runner = object()
    environment = {"SOURCE_DATE_EPOCH": "1770000000"}

    assert (
        assembler._compile_observed(
            tex_path,
            staging,
            environment=environment,
            runner=runner,
        )
        == 0
    )
    assert calls == [
        (
            tex_path,
            staging,
            {
                "environment": environment,
                "recorder": True,
                "runner": runner,
                "source_date_epoch": 1770000000,
            },
        )
    ]


@pytest.mark.parametrize("variant", VARIANTS)
def test_observed_build_emits_closed_receipt_after_promotion(
    monkeypatch, tmp_path, assembler, variant
):
    root = tmp_path / "repository" / "NSI"
    _prepare_root(root)
    if variant != "eleve":
        directory, source_type = {
            "professeur": ("corriges", "corrige"),
            "methodes": ("methodes", "methode"),
            "remediation": ("remediation", "remediation"),
            "amenagee": ("amenagee", "amenagee"),
            "evaluations": ("evaluations", "evaluation"),
            "projets": ("projet", "projet"),
        }[variant]
        _write_meta(
            root / "chapitres" / CHAPTERS[0] / directory / "01_variant.tex",
            CHAPTERS[0],
            source_type,
            variant.upper(),
        )
    _patch_root(monkeypatch, assembler, root)
    epoch = _write_reproducibility_control(root.parent)
    observed = _observed_build_fakes(monkeypatch, assembler, root)

    assert assembler.build_manual(variant, record_observed=True) == 0

    build_dir = root / "build" / "MANUEL_1NSI"
    receipt_path = build_dir / f"MANUEL_1NSI_{variant}.receipt.json"
    report_path = build_dir / f"MANUEL_1NSI_{variant}.preflight.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert set(receipt) == assembler.RECEIPT_FIELDS
    assert not {"included_objects", "excluded_objects", "ordered_trace"} & set(
        receipt
    )
    assert receipt["manual"] == "1NSI"
    assert receipt["variant"] == variant
    assert receipt["run_id"] == RUN_ID
    assert receipt["pdf_path"] == (
        f"NSI/build/MANUEL_1NSI/MANUEL_1NSI_{variant}.pdf"
    )
    assert receipt["master_path"].startswith("NSI/build/MANUEL_1NSI/")
    assert receipt["log_path"].startswith("NSI/build/MANUEL_1NSI/")
    assert receipt["fls_path"].startswith("NSI/build/MANUEL_1NSI/")
    assert receipt["preflight_report"].startswith("NSI/build/MANUEL_1NSI/")
    assert receipt["generated_dependencies"] == []
    assert receipt["tool_versions"] == TOOL_VERSIONS
    assert receipt["reproducibility"]["source_date_epoch"] == epoch
    assert observed["source_date_epoch"] == str(epoch)
    assert len(observed["recorder_calls"]) == 1
    assert set(report) == assembler.PREFLIGHT_FIELDS
    assert report["pdf_sha256"] == receipt["evidence_sha256"]["pdf"]
    if variant in STUDENT_VARIANTS:
        assert receipt["gates"]["student_separation"] == {"passed": True}
    else:
        assert "student_separation" not in receipt["gates"]


@pytest.mark.parametrize(
    "failure",
    ["compile", "preflight", "verify", "promotion", "receipt"],
)
def test_observed_failure_before_recording_removes_receipt_and_report(
    monkeypatch, tmp_path, assembler, failure
):
    root = tmp_path / "repository" / "NSI"
    _prepare_root(root)
    _patch_root(monkeypatch, assembler, root)
    _write_reproducibility_control(root.parent)
    observed = _observed_build_fakes(monkeypatch, assembler, root)
    build_dir = root / "build" / "MANUEL_1NSI"
    build_dir.mkdir(parents=True)
    receipt = build_dir / "MANUEL_1NSI_eleve.receipt.json"
    report = build_dir / "MANUEL_1NSI_eleve.preflight.json"
    receipt.write_text("stale", encoding="utf-8")
    report.write_text("stale", encoding="utf-8")
    if failure == "compile":
        monkeypatch.setattr(
            assembler,
            "_compile_observed",
            lambda *_args, **_kwargs: 1,
        )
    elif failure == "preflight":
        monkeypatch.setattr(
            assembler.legacy,
            "preflight_book_pdf",
            lambda *_args, **_kwargs: 1,
        )
    elif failure == "verify":
        monkeypatch.setattr(
            assembler.legacy,
            "verify_pdf",
            lambda *_args, **_kwargs: 1,
        )
    elif failure == "promotion":
        monkeypatch.setattr(
            assembler.legacy,
            "_promote_book_artifacts",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(
                OSError("promotion refusee")
            ),
        )
    else:
        real_atomic_write = assembler._atomic_write_json

        def fail_receipt_write(path, payload):
            real_atomic_write(path, payload)
            if path == receipt:
                raise OSError("receipt refuse")

        monkeypatch.setattr(assembler, "_atomic_write_json", fail_receipt_write)

    assert assembler.build_manual("eleve", record_observed=True) == 1

    assert not receipt.exists()
    assert not report.exists()
    assert observed["recorder_calls"] == []
    if failure in {"compile", "preflight", "verify", "promotion"}:
        assert not (build_dir / "MANUEL_1NSI_eleve.pdf").exists()


def test_observed_recorder_failure_rolls_back_receipt_and_report(
    monkeypatch, tmp_path, assembler
):
    root = tmp_path / "repository" / "NSI"
    _prepare_root(root)
    _patch_root(monkeypatch, assembler, root)
    _write_reproducibility_control(root.parent)
    _observed_build_fakes(monkeypatch, assembler, root)
    build_dir = root / "build" / "MANUEL_1NSI"
    build_dir.mkdir(parents=True)
    canonical_pdf = build_dir / "MANUEL_1NSI_eleve.pdf"
    canonical_pdf.write_bytes(b"%PDF-previous-canonical")
    calls = []
    monkeypatch.setattr(
        assembler,
        "_invoke_recorder",
        lambda receipt_path, *, environment: calls.append(receipt_path) or 1,
    )

    assert assembler.build_manual("eleve", record_observed=True) == 1

    assert calls == [build_dir / "MANUEL_1NSI_eleve.receipt.json"]
    assert not (build_dir / "MANUEL_1NSI_eleve.receipt.json").exists()
    assert not (build_dir / "MANUEL_1NSI_eleve.preflight.json").exists()
    assert canonical_pdf.read_bytes() == b"%PDF-previous-canonical"
    assert not list(build_dir.glob("*.pdf.backup"))


def test_cli_forwards_record_observed(monkeypatch, assembler):
    calls = []
    monkeypatch.setattr(
        assembler,
        "build_manual",
        lambda variant, record_observed=False: calls.append(
            (variant, record_observed)
        )
        or 0,
    )

    assert assembler.main(["--variant", "projets", "--record-observed"]) == 0
    assert calls == [("projets", True)]
