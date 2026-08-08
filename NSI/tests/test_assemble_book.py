"""Tests rouges/verts du mode assembleur manuel NSI."""
from pathlib import Path
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import assemble  # noqa: E402


def test_load_book_manifest_1nsi():
    manifest = assemble.load_book_manifest("1NSI")

    assert manifest["output_name"] == "MANUEL_1NSI_v1"
    assert manifest["matiere"] == "NSI"
    assert manifest["niveau"] == "Première"
    assert manifest["author"]
    assert manifest["subject"]
    assert manifest["keywords"]
    assert len(manifest["chapters"]) == 10


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


def test_render_book_master_contains_all_chapters():
    tex = assemble.render_book_master("1NSI")

    assert "MANUEL_1NSI_v1" not in tex
    assert "1NSI-TYPES-BASE" in tex
    assert "1NSI-PROJET-METHODES" in tex
    assert tex.count("\\chapter{") == 10


def test_render_book_master_uses_public_metadata_on_title_page():
    tex = assemble.render_book_master("1NSI")

    assert "NSI --- Première" in tex
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

    assert assemble.compile_tex(tex_path, tmp_path) == 1
    assert len(calls) == 1
    assert verified == []
    assert "latex failure" in capsys.readouterr().out


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
