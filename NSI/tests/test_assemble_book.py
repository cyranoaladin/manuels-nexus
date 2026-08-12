"""Tests rouges/verts du mode assembleur manuel NSI."""
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import assemble  # noqa: E402


def _valid_manifest(**overrides):
    manifest = {
        "book_id": "1NSI",
        "title": "Manuel NSI Première",
        "subtitle": "Édition de travail 2026-2027",
        "matiere": "NSI",
        "niveau": "Première",
        "author": "Nexus Réussite",
        "subject": "Manuel scolaire NSI",
        "keywords": "NSI, Première",
        "source_date_epoch": 1786147200,
        "output_name": "MANUEL_1NSI_v1",
        "chapters": [{"id": "1NSI-FIXTURE", "title": "Chapitre test"}],
    }
    manifest.update(overrides)
    return manifest


def _write_manifest(root: Path, manifest: dict, filename: str = "1NSI.json") -> None:
    path = root / "manifests" / "books" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest), encoding="utf-8")


def _prepare_book_root(root: Path) -> None:
    _write_manifest(root, _valid_manifest())
    course = root / "chapitres" / "1NSI-FIXTURE" / "cours" / "1-cours.tex"
    course.parent.mkdir(parents=True)
    course.write_text("Contenu élève.", encoding="utf-8")
    master = root / "gabarits" / "book_master.tex"
    master.parent.mkdir(parents=True)
    master.write_text(
        "%%MATIERE%% %%NIVEAU%% %%TITLE%% %%SUBTITLE%% "
        "%%PDF_AUTHOR%% %%PDF_SUBJECT%% %%PDF_KEYWORDS%%\n%%CONTENT%%\n",
        encoding="utf-8",
    )


def test_load_book_manifest_1nsi():
    manifest = assemble.load_book_manifest("1NSI")

    assert manifest["output_name"] == "MANUEL_1NSI_v1"
    assert manifest["matiere"] == "NSI"
    assert manifest["niveau"] == "Première"
    assert manifest["author"]
    assert manifest["subject"]
    assert manifest["keywords"]
    assert manifest["source_date_epoch"] == 1785962466
    assert len(manifest["chapters"]) == 10


@pytest.mark.parametrize("book_id", ["../escape", "folder/book", r"folder\book", ".."])
def test_load_book_manifest_rejects_unsafe_book_id(monkeypatch, tmp_path, book_id):
    root = tmp_path / "NSI"
    escaped_path = root / "manifests" / "escape.json"
    escaped_path.parent.mkdir(parents=True)
    escaped_path.write_text(json.dumps(_valid_manifest(book_id=book_id)), encoding="utf-8")
    monkeypatch.setattr(assemble, "ROOT", root)

    with pytest.raises(ValueError, match="book_id"):
        assemble.load_book_manifest(book_id)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", ""),
        ("author", 42),
        ("chapters", []),
        ("source_date_epoch", "1786147200"),
        ("source_date_epoch", True),
        ("output_name", "../MANUEL"),
    ],
)
def test_load_book_manifest_rejects_invalid_top_level_values(
    monkeypatch, tmp_path, field, value
):
    root = tmp_path / "NSI"
    _write_manifest(root, _valid_manifest(**{field: value}))
    monkeypatch.setattr(assemble, "ROOT", root)

    with pytest.raises(ValueError, match=field):
        assemble.load_book_manifest("1NSI")


def test_load_book_manifest_rejects_missing_and_extra_keys(monkeypatch, tmp_path):
    root = tmp_path / "NSI"
    missing = _valid_manifest()
    missing.pop("subject")
    _write_manifest(root, missing)
    monkeypatch.setattr(assemble, "ROOT", root)

    with pytest.raises(ValueError, match="clés"):
        assemble.load_book_manifest("1NSI")

    _write_manifest(root, _valid_manifest(unexpected="value"))
    with pytest.raises(ValueError, match="clés"):
        assemble.load_book_manifest("1NSI")


@pytest.mark.parametrize(
    "chapters",
    [
        [{"id": "1NSI-FIXTURE", "title": "Chapitre", "extra": "interdit"}],
        [{"id": "../SORTIE", "title": "Chapitre"}],
        [{"id": "1NSI-FIXTURE", "title": ""}],
        [
            {"id": "1NSI-FIXTURE", "title": "Chapitre A"},
            {"id": "1NSI-FIXTURE", "title": "Chapitre B"},
        ],
    ],
)
def test_load_book_manifest_rejects_invalid_chapter_entries(
    monkeypatch, tmp_path, chapters
):
    root = tmp_path / "NSI"
    _write_manifest(root, _valid_manifest(chapters=chapters))
    monkeypatch.setattr(assemble, "ROOT", root)

    with pytest.raises(ValueError, match="chapitre|dupliqué"):
        assemble.load_book_manifest("1NSI")


def test_load_book_manifest_rejects_incoherent_book_id(monkeypatch, tmp_path):
    root = tmp_path / "NSI"
    _write_manifest(root, _valid_manifest(book_id="TNSI"))
    monkeypatch.setattr(assemble, "ROOT", root)

    with pytest.raises(ValueError, match="book_id"):
        assemble.load_book_manifest("1NSI")


def test_collect_book_chapters_rejects_symlink_escape(monkeypatch, tmp_path):
    root = tmp_path / "NSI"
    outside = tmp_path / "outside" / "1NSI-FIXTURE"
    course = outside / "cours" / "1-cours.tex"
    course.parent.mkdir(parents=True)
    course.write_text("Contenu externe.", encoding="utf-8")
    chapters_root = root / "chapitres"
    chapters_root.mkdir(parents=True)
    (chapters_root / "1NSI-FIXTURE").symlink_to(outside, target_is_directory=True)
    _write_manifest(root, _valid_manifest())
    monkeypatch.setattr(assemble, "ROOT", root)

    with pytest.raises(ValueError, match="hors du dépôt"):
        assemble.collect_book_chapters("1NSI")


def test_latex_escape_covers_manifest_special_characters():
    value = "#_%&${}\\^~"

    assert assemble.latex_escape(value) == (
        r"\#\_\%\&\$\{\}\textbackslash{}\textasciicircum{}\textasciitilde{}"
    )


def test_render_book_master_escapes_all_manifest_text(monkeypatch, tmp_path):
    root = tmp_path / "NSI"
    _prepare_book_root(root)
    special = "# _ % & $ { } \\input{injected} ^ ~"
    manifest = _valid_manifest(
        title=f"Titre {special}",
        subtitle=f"Sous-titre {special}",
        matiere=f"Matière {special}",
        niveau=f"Niveau {special}",
        author=f"Auteur {special}",
        subject=f"Sujet {special}",
        keywords=f"Mots {special}",
        chapters=[{"id": "1NSI-FIXTURE", "title": f"Chapitre {special}"}],
    )
    _write_manifest(root, manifest)
    monkeypatch.setattr(assemble, "ROOT", root)

    tex = assemble.render_book_master("1NSI")

    for field in (
        "title", "subtitle", "matiere", "niveau", "author", "subject", "keywords"
    ):
        assert assemble.latex_escape(manifest[field]) in tex
    assert assemble.latex_escape(manifest["chapters"][0]["title"]) in tex
    assert r"\input{injected}" not in tex


def test_collect_book_chapters_1nsi():
    chapters = assemble.collect_book_chapters("1NSI")

    assert chapters[0].name == "1NSI-TYPES-BASE"
    assert chapters[-1].name == "1NSI-PROJET-METHODES"
    assert len(chapters) == 10


def test_collect_complete_book_files_are_student_safe():
    chapters = assemble.collect_book_chapters("1NSI")
    selected = [
        path
        for chapter in chapters
        for path in assemble.collect_book_files(chapter, "complet")
    ]
    forbidden_markers = (
        r"\begin{corrige}",
        r"\baremeIndicatif",
        "barème",
        "réponse attendue",
    )
    violations = []
    for path in selected:
        relative = path.relative_to(ROOT)
        lowered_path = str(relative).lower()
        lowered_text = path.read_text(encoding="utf-8").lower()
        if any(part.lower() in ("evaluations", "remediation") for part in relative.parts):
            violations.append(str(relative))
        if any(marker in lowered_path for marker in ("corrige", "professeur")):
            violations.append(str(relative))
        if any(marker.lower() in lowered_text for marker in forbidden_markers):
            violations.append(str(relative))

    assert len(chapters) == 10
    assert selected
    assert violations == []


def test_collect_book_files_ignores_markers_in_repository_parent(monkeypatch, tmp_path):
    root = tmp_path / "professeur-archive" / "NSI"
    chapter = root / "chapitres" / "1NSI-FIXTURE"
    course = chapter / "cours" / "1-cours.tex"
    course.parent.mkdir(parents=True)
    course.write_text("Contenu élève.", encoding="utf-8")
    monkeypatch.setattr(assemble, "ROOT", root)

    assert assemble.collect_book_files(chapter, "complet") == [course]


def test_collect_book_chapters_methodes_1nsi():
    chapters = assemble.collect_book_chapters("1NSI", "methodes")

    assert [path.name for path in chapters] == ["1NSI-TYPES-CONSTRUITS"]


def test_collect_book_chapters_amenagee_1nsi():
    chapters = assemble.collect_book_chapters("1NSI", "amenagee")

    assert [path.name for path in chapters] == ["1NSI-TYPES-CONSTRUITS"]


@pytest.mark.parametrize("variant", ["professeur", "parcours1"])
def test_collect_book_chapters_rejects_chapter_only_variants(variant):
    with pytest.raises(ValueError, match="Variante de livre non prise en charge"):
        assemble.collect_book_chapters("1NSI", variant)


def test_collect_chapter_parcours1_remains_available():
    chapter = ROOT / "chapitres" / "1NSI-TYPES-BASE"

    files = assemble.collect(chapter, "parcours1")

    assert files
    assert all(path.parent.name == "exercices" for path in files)


def test_book_master_template_exists():
    assert (ROOT / "gabarits" / "book_master.tex").exists()


def test_book_master_reserves_room_for_three_digit_toc_page_numbers():
    template = (ROOT / "gabarits" / "book_master.tex").read_text(
        encoding="utf-8"
    )

    assert r"\renewcommand*{\@pnumwidth}{2em}" in template


def test_render_book_master_contains_all_chapters():
    tex = assemble.render_book_master("1NSI")

    assert "MANUEL_1NSI_v1" not in tex
    assert "1NSI-TYPES-BASE" in tex
    assert "1NSI-PROJET-METHODES" in tex
    assert tex.count("\\chapter{") == 10


def test_render_book_master_uses_public_metadata_on_title_page():
    tex = assemble.render_book_master("1NSI")

    # Charte v6 : la page de titre est la couverture de collection, qui
    # reçoit la matière et le niveau publics du manifeste.
    assert "\\couvertureManuel{NSI}{Première}" in tex
    assert "@matiere" not in tex
    assert "@niveau" not in tex


@pytest.mark.parametrize("variant", sorted(assemble.BOOK_VARIANTS))
def test_render_book_master_configures_pdf_metadata_and_navigation(variant):
    manifest = assemble.load_book_manifest("1NSI")
    tex = assemble.render_book_master("1NSI", variant)

    assert "{hyperref}" in tex
    assert r"\hypersetup{" in tex
    assert f"pdftitle={{{assemble._book_title(manifest, variant)}}}" in tex
    assert f"pdfauthor={{{manifest['author']}}}" in tex
    assert f"pdfsubject={{{manifest['subject']}}}" in tex
    assert f"pdfkeywords={{{manifest['keywords']}}}" in tex
    assert "bookmarks=true" in tex
    assert "bookmarksopen=true" in tex
    assert "%%PDF_" not in tex


def test_render_complete_book_master_is_explicitly_student_safe():
    tex = assemble.render_book_master("1NSI", "complet")
    lowered = tex.lower()

    assert r"\nxVersionProfesseurfalse" in tex
    assert "/evaluations/" not in lowered
    assert "/remediation/" not in lowered
    assert "/corriges/" not in lowered
    assert "-corrige.tex" not in lowered
    assert "/professeur/" not in lowered


def test_render_book_master_discards_correction_bodies_in_student_variants():
    tex = assemble.render_book_master("1NSI", "remediation")

    assert r"\RenewDocumentEnvironment{corrige}{m +b}{}{}" in tex


def test_render_book_master_uses_ragged_alignment_for_left_margin_notes():
    tex = assemble.render_book_master("1NSI", "complet")

    assert r"\renewcommand*{\raggedleftmarginnote}{\raggedleft}" in tex


def test_render_book_master_methodes_contains_one_chapter():
    tex = assemble.render_book_master("1NSI", "methodes")

    assert "1NSI-TYPES-CONSTRUITS" in tex
    assert tex.count("\\chapter{") == 1


def test_compile_tex_rejects_lualatex_failure_even_with_stale_pdf(
    monkeypatch, tmp_path, capsys
):
    tex_path = tmp_path / "manuel.tex"
    tex_path.write_text("fixture", encoding="utf-8")
    (tmp_path / "manuel.pdf").write_bytes(b"stale")
    calls = []
    verified = []

    def failing_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 1, stdout=b"latex failure")

    monkeypatch.setattr(assemble.subprocess, "run", failing_run)
    monkeypatch.setattr(
        assemble,
        "verify_pdf",
        lambda *_args, **_kwargs: verified.append(True) or 0,
    )

    assert assemble.compile_tex(
        tex_path, tmp_path, source_date_epoch=1786147200
    ) == 1
    assert len(calls) == 1
    assert verified == []
    assert "latex failure" in capsys.readouterr().out
    assert not (tmp_path / "manuel.pdf").exists()
    environment = calls[0][1]["env"]
    assert environment["SOURCE_DATE_EPOCH"] == "1786147200"
    assert environment["FORCE_SOURCE_DATE"] == "1"
    assert environment["TZ"] == "UTC"
    assert "-recorder" not in calls[0][0]


def test_compile_tex_adds_recorder_to_every_lualatex_pass_when_requested(
    monkeypatch, tmp_path
):
    tex_path = tmp_path / "manuel.tex"
    tex_path.write_text("fixture", encoding="utf-8")
    calls = []

    def successful_run(command, **kwargs):
        calls.append((command, kwargs))
        (tmp_path / "manuel.pdf").write_bytes(b"%PDF")
        (tmp_path / "manuel.log").write_text("clean", encoding="utf-8")
        (tmp_path / "manuel.fls").write_text(
            f"INPUT {tex_path}\n",
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(command, 0, stdout=b"")

    monkeypatch.setattr(assemble.subprocess, "run", successful_run)
    monkeypatch.setattr(assemble, "verify_pdf", lambda *_args, **_kwargs: 0)

    assert assemble.compile_tex(
        tex_path,
        tmp_path,
        source_date_epoch=1786147200,
        recorder=True,
    ) == 0
    assert len(calls) == 2
    assert all("-recorder" in command for command, _kwargs in calls)


def test_build_book_stages_preflights_and_promotes_with_one_manifest_read(
    monkeypatch, tmp_path
):
    root = tmp_path / "NSI"
    _prepare_book_root(root)
    build_dir = root / "build" / "books"
    build_dir.mkdir(parents=True)
    canonical_pdf = build_dir / "MANUEL_1NSI_v1.pdf"
    canonical_pdf.write_bytes(b"stale")
    manifest_reads = []
    preflight_calls = []
    original_load = assemble.load_book_manifest

    def counting_load(book_id):
        manifest_reads.append(book_id)
        return original_load(book_id)

    def fake_compile(tex_path, staging_dir, *, source_date_epoch):
        assert staging_dir.parent == build_dir
        assert staging_dir.name.startswith(".MANUEL_1NSI_v1-")
        assert source_date_epoch == 1786147200
        assert not canonical_pdf.exists()
        (staging_dir / f"{tex_path.stem}.pdf").write_bytes(b"fresh")
        (staging_dir / f"{tex_path.stem}.log").write_text("clean", encoding="utf-8")
        (staging_dir / f"{tex_path.stem}.aux").write_text("aux", encoding="utf-8")
        return 0

    def fake_preflight(pdf, log):
        preflight_calls.append((pdf, log))
        assert pdf.parent != build_dir
        assert not canonical_pdf.exists()
        return 0

    monkeypatch.setattr(assemble, "ROOT", root)
    monkeypatch.setattr(assemble, "load_book_manifest", counting_load)
    monkeypatch.setattr(assemble, "compile_tex", fake_compile)
    monkeypatch.setattr(assemble, "preflight_book_pdf", fake_preflight)

    assert assemble.build_book("1NSI", "complet") == 0
    assert manifest_reads == ["1NSI"]
    assert len(preflight_calls) == 1
    assert canonical_pdf.read_bytes() == b"fresh"
    assert (build_dir / "MANUEL_1NSI_v1.log").read_text(encoding="utf-8") == "clean"
    assert not list(build_dir.glob(".MANUEL_1NSI_v1-*"))


def test_build_book_preflight_failure_removes_canonical_pdf(monkeypatch, tmp_path):
    root = tmp_path / "NSI"
    _prepare_book_root(root)
    build_dir = root / "build" / "books"
    build_dir.mkdir(parents=True)
    canonical_pdf = build_dir / "MANUEL_1NSI_v1.pdf"
    canonical_pdf.write_bytes(b"stale")

    def fake_compile(tex_path, staging_dir, *, source_date_epoch):
        (staging_dir / f"{tex_path.stem}.pdf").write_bytes(b"invalid")
        (staging_dir / f"{tex_path.stem}.log").write_text("clean", encoding="utf-8")
        return 0

    monkeypatch.setattr(assemble, "ROOT", root)
    monkeypatch.setattr(assemble, "compile_tex", fake_compile)
    monkeypatch.setattr(assemble, "preflight_book_pdf", lambda *_args: 1)

    assert assemble.build_book("1NSI", "complet") == 1
    assert not canonical_pdf.exists()
    assert not list(build_dir.glob(".MANUEL_1NSI_v1-*"))


def test_promote_book_artifacts_promotes_pdf_last(monkeypatch, tmp_path):
    staging = tmp_path / "staging"
    destination = tmp_path / "books"
    staging.mkdir()
    destination.mkdir()
    for suffix in (".pdf", ".log", ".tex", ".aux"):
        (staging / f"MANUEL{suffix}").write_text(suffix, encoding="utf-8")
    destinations = []
    real_replace = os.replace

    def record_replace(source, target):
        destinations.append(Path(target))
        real_replace(source, target)

    monkeypatch.setattr(assemble.os, "replace", record_replace)

    assemble._promote_book_artifacts(staging, destination, "MANUEL")

    assert destinations[-1].suffix == ".pdf"


def test_build_book_rejects_output_symlink_escape(monkeypatch, tmp_path):
    root = tmp_path / "NSI"
    _prepare_book_root(root)
    build_dir = root / "build" / "books"
    build_dir.mkdir(parents=True)
    outside = tmp_path / "outside.pdf"
    outside.write_bytes(b"outside")
    (build_dir / "MANUEL_1NSI_v1.pdf").symlink_to(outside)
    monkeypatch.setattr(assemble, "ROOT", root)

    with pytest.raises(ValueError, match="hors du dépôt"):
        assemble.build_book("1NSI", "complet")

    assert outside.read_bytes() == b"outside"


def test_build_book_rejects_internal_output_symlink_before_unlink(
    monkeypatch, tmp_path
):
    root = tmp_path / "NSI"
    _prepare_book_root(root)
    build_dir = root / "build" / "books"
    build_dir.mkdir(parents=True)
    target = build_dir / "archive.pdf"
    target.write_bytes(b"archive")
    (build_dir / "MANUEL_1NSI_v1.pdf").symlink_to(target.name)
    monkeypatch.setattr(assemble, "ROOT", root)
    monkeypatch.setattr(
        assemble,
        "compile_tex",
        lambda *_args, **_kwargs: pytest.fail("Le build ne doit pas démarrer."),
    )

    with pytest.raises(ValueError, match="symbolique"):
        assemble.build_book("1NSI", "complet")

    assert target.read_bytes() == b"archive"


@pytest.mark.parametrize("variant", ["professeur", "parcours1"])
def test_build_book_rejects_chapter_only_variants_before_loading_manifest(
    monkeypatch, variant
):
    def unexpected_manifest_load(_book_id):
        raise AssertionError("book validation must run before manifest loading")

    monkeypatch.setattr(assemble, "load_book_manifest", unexpected_manifest_load)

    with pytest.raises(ValueError, match="Variante de livre non prise en charge"):
        assemble.build_book("1NSI", variant)


@pytest.mark.parametrize("variant", ["professeur", "parcours1"])
def test_main_rejects_chapter_only_variants_before_build(monkeypatch, variant):
    def unexpected_build(_book_id, _variant):
        raise AssertionError("main validation must run before book build")

    monkeypatch.setattr(assemble, "build_book", unexpected_build)

    with pytest.raises(ValueError, match="Variante de livre non prise en charge"):
        assemble.main(book="1NSI", variant=variant)
