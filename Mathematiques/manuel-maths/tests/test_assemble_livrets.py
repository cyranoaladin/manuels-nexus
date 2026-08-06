from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest


MANUAL_ROOT = Path(__file__).resolve().parents[1]
GIT_ROOT = MANUAL_ROOT.parents[1]
sys.path.insert(0, str(MANUAL_ROOT / "scripts"))

import assemble_livrets  # noqa: E402
from scripts.build_manifest import _object_trace_token as manifest_trace_token  # noqa: E402


def _expected_paths(subdir: str) -> list[str]:
    return [
        path.relative_to(GIT_ROOT).as_posix()
        for chapter in assemble_livrets._manuel.CHAPITRES
        for path in assemble_livrets.collect_livret_chapter_files(
            MANUAL_ROOT / "chapitres" / chapter,
            subdir,
        )
    ]


def _marked_blocks(master: str) -> list[tuple[str, str, str]]:
    return re.findall(
        r"\\typeout\{NEXUS_OBJECT_BEGIN:([0-9a-f]{40})\}\n"
        r"(\\input\{([^}]+)\})\n"
        r"\\typeout\{NEXUS_OBJECT_END:\1\}",
        master,
    )


def _render(livret: str, run_id: str = "a" * 32) -> str:
    return assemble_livrets.render_livret_master(
        livret,
        run_id,
        git_root=GIT_ROOT,
        tracked_paths=assemble_livrets._manuel.load_tracked_paths(GIT_ROOT),
    )


@pytest.mark.parametrize(
    ("livret", "subdir"),
    [
        ("methodes", "methodes"),
        ("evaluations", "evaluations"),
        ("remediation", "remediation"),
    ],
)
def test_render_livret_master_marks_every_object_once_in_collection_order(
    livret: str, subdir: str
) -> None:
    master = _render(livret)
    expected_paths = _expected_paths(subdir)
    blocks = _marked_blocks(master)

    assert expected_paths, "fixture chapters must have content for this livret"
    assert len(blocks) == len(expected_paths)
    assert [input_path for _, _, input_path in blocks] == [
        path.removeprefix("Mathematiques/manuel-maths/") for path in expected_paths
    ]
    assert [token for token, _, _ in blocks] == [
        manifest_trace_token(path) for path in expected_paths
    ]
    assert master.count("NEXUS_OBJECT_BEGIN:") == len(expected_paths)
    assert master.count("NEXUS_OBJECT_END:") == len(expected_paths)


def test_render_livret_master_has_one_run_marker() -> None:
    run_id = "0123456789abcdef" * 2
    master = _render("methodes", run_id)

    assert re.findall(r"NEXUS_BUILD_RUN:([0-9a-f]{32})", master) == [run_id]
    assert master.count("NEXUS_BUILD_RUN:") == 1


def test_render_livret_master_rejects_unknown_livret() -> None:
    with pytest.raises(assemble_livrets.LivretError, match="livret inconnu"):
        _render("inconnu")


def test_render_livret_master_uses_professor_class_configuration() -> None:
    master = _render("evaluations")

    assert "\\nxVersionProfesseurtrue" in master
    assert "\\documentclass{gabarits/nexus-manuel}" in master


def test_render_livret_master_titles_each_present_chapter_once() -> None:
    master = _render("methodes")

    for chapter in assemble_livrets._manuel.CHAPITRES:
        chap_dir = MANUAL_ROOT / "chapitres" / chapter
        files = assemble_livrets.collect_livret_chapter_files(chap_dir, "methodes")
        if not files:
            continue
        assert master.count(f"% ===== {chapter} =====") == 1


def test_render_livret_master_raises_when_subdir_is_empty_everywhere(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(assemble_livrets._manuel, "CHAPITRES", [])

    with pytest.raises(assemble_livrets.LivretError, match="aucun contenu"):
        _render("methodes")


def test_collect_livret_chapter_files_is_sorted_and_globs_tex_only(
    tmp_path: Path,
) -> None:
    subdir = tmp_path / "methodes"
    subdir.mkdir()
    (subdir / "b.tex").write_text("% b", encoding="utf-8")
    (subdir / "a.tex").write_text("% a", encoding="utf-8")
    (subdir / "notes.txt").write_text("ignored", encoding="utf-8")

    files = assemble_livrets.collect_livret_chapter_files(tmp_path, "methodes")

    assert [f.name for f in files] == ["a.tex", "b.tex"]


def test_livrets_registry_maps_each_deliverable_to_its_own_subdir() -> None:
    assert set(assemble_livrets.LIVRETS) == {"methodes", "evaluations", "remediation"}
    for livret, spec in assemble_livrets.LIVRETS.items():
        assert spec["subdir"] == livret
        assert spec["titre"]


def test_build_argument_parser_only_accepts_known_livrets() -> None:
    parser = assemble_livrets.build_argument_parser()

    args = parser.parse_args(["--livret", "methodes"])
    assert args.livret == "methodes"

    with pytest.raises(SystemExit):
        parser.parse_args(["--livret", "inconnu"])

    with pytest.raises(SystemExit):
        parser.parse_args([])
