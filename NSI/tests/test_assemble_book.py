"""Tests rouges/verts du mode assembleur manuel NSI."""
from pathlib import Path
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
    assert len(manifest["chapters"]) == 10


def test_collect_book_chapters_1nsi():
    chapters = assemble.collect_book_chapters("1NSI")

    assert chapters[0].name == "1NSI-TYPES-BASE"
    assert chapters[-1].name == "1NSI-PROJET-METHODES"
    assert len(chapters) == 10


def test_collect_book_chapters_methodes_1nsi():
    chapters = assemble.collect_book_chapters("1NSI", "methodes")

    assert [path.name for path in chapters] == ["1NSI-TYPES-CONSTRUITS"]


def test_collect_book_chapters_amenagee_1nsi():
    chapters = assemble.collect_book_chapters("1NSI", "amenagee")

    assert [path.name for path in chapters] == ["1NSI-TYPES-CONSTRUITS"]


def test_collect_book_chapters_professeur_1nsi_fails():
    with pytest.raises(ValueError, match="Aucun chapitre éligible"):
        assemble.collect_book_chapters("1NSI", "professeur")


def test_book_master_template_exists():
    assert (ROOT / "gabarits" / "book_master.tex").exists()


def test_render_book_master_contains_all_chapters():
    tex = assemble.render_book_master("1NSI")

    assert "MANUEL_1NSI_v1" not in tex
    assert "1NSI-TYPES-BASE" in tex
    assert "1NSI-PROJET-METHODES" in tex
    assert tex.count("\\chapter{") == 10


def test_render_book_master_methodes_contains_one_chapter():
    tex = assemble.render_book_master("1NSI", "methodes")

    assert "1NSI-TYPES-CONSTRUITS" in tex
    assert tex.count("\\chapter{") == 1
