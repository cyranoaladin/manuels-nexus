from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest


MANUAL_ROOT = Path(__file__).resolve().parents[1]
GIT_ROOT = MANUAL_ROOT.parents[1]
sys.path.insert(0, str(MANUAL_ROOT / "scripts"))

import assemble_manuel  # noqa: E402
from scripts.build_manifest import _object_trace_token as manifest_trace_token  # noqa: E402


def _commit_fixture(repository: Path, *paths: Path) -> None:
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    subprocess.run(
        ["git", "-C", str(repository), "add", "--", *map(str, paths)],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "-c",
            "user.name=Observed Assembler Tests",
            "-c",
            "user.email=observed@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
    )


def _professor_paths() -> list[str]:
    return [
        path.relative_to(GIT_ROOT).as_posix()
        for chapter in assemble_manuel.CHAPITRES
        for path in assemble_manuel.collect_chapter(
            MANUAL_ROOT / "chapitres" / chapter,
            "professeur",
        )
    ]


def _marked_blocks(master: str) -> list[tuple[str, str, str]]:
    return re.findall(
        r"\\typeout\{NEXUS_OBJECT_BEGIN:([0-9a-f]{40})\}\n"
        r"(\\input\{([^}]+)\})\n"
        r"\\typeout\{NEXUS_OBJECT_END:\1\}",
        master,
    )


def test_resolve_git_root_from_nested_manual_directory() -> None:
    assert assemble_manuel.resolve_git_root(MANUAL_ROOT / "chapitres") == GIT_ROOT


def test_canonical_tracked_path_is_git_relative_and_manual_scoped() -> None:
    canonical = assemble_manuel.canonical_tracked_path(
        "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/00_ouverture.tex",
        GIT_ROOT,
    )

    assert canonical.startswith("Mathematiques/manuel-maths/")
    assert not Path(canonical).is_absolute()


@pytest.mark.parametrize(
    "hostile_path",
    [
        str(
            GIT_ROOT
            / "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/00_ouverture.tex"
        ),
        "Mathematiques/manuel-maths/../manuel-maths/scripts/assemble_manuel.py",
        r"Mathematiques\manuel-maths\scripts\assemble_manuel.py",
    ],
    ids=["absolute", "parent", "backslash"],
)
def test_canonical_tracked_path_rejects_hostile_spelling(hostile_path: str) -> None:
    with pytest.raises(ValueError, match="canonique"):
        assemble_manuel.canonical_tracked_path(hostile_path, GIT_ROOT)


def test_canonical_tracked_path_rejects_tracked_symlink(tmp_path: Path) -> None:
    target = tmp_path / "Mathematiques/manuel-maths/objects/target.tex"
    target.parent.mkdir(parents=True)
    target.write_text("Objet suivi\n", encoding="utf-8")
    link = target.with_name("link.tex")
    link.symlink_to(target.name)
    _commit_fixture(tmp_path, target.relative_to(tmp_path), link.relative_to(tmp_path))

    with pytest.raises(ValueError, match="symbolique"):
        assemble_manuel.canonical_tracked_path(
            link.relative_to(tmp_path).as_posix(),
            tmp_path,
        )


def test_canonical_tracked_path_rejects_untracked_file(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    source = tmp_path / "Mathematiques/manuel-maths/objects/untracked.tex"
    source.parent.mkdir(parents=True)
    source.write_text("Objet non suivi\n", encoding="utf-8")

    with pytest.raises(ValueError, match="non suivi"):
        assemble_manuel.canonical_tracked_path(
            source.relative_to(tmp_path).as_posix(),
            tmp_path,
        )


def test_canonical_tracked_path_treats_git_metacharacters_literally(
    tmp_path: Path,
) -> None:
    tracked = tmp_path / "Mathematiques/manuel-maths/objects/object1.tex"
    tracked.parent.mkdir(parents=True)
    tracked.write_text("Objet suivi\n", encoding="utf-8")
    _commit_fixture(tmp_path, tracked.relative_to(tmp_path))
    untracked_pathspec = tracked.with_name("object?.tex")
    untracked_pathspec.write_text("Objet non suivi\n", encoding="utf-8")

    with pytest.raises(ValueError, match="non suivi"):
        assemble_manuel.canonical_tracked_path(
            untracked_pathspec.relative_to(tmp_path).as_posix(),
            tmp_path,
        )


def test_assembler_trace_token_is_the_manifest_protocol_token() -> None:
    canonical = (
        "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/"
        "cours/00_ouverture.tex"
    )

    assert assemble_manuel.object_trace_token(canonical) == manifest_trace_token(
        canonical
    )


def test_wrap_object_input_uses_exact_balanced_markers() -> None:
    canonical = (
        "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/"
        "cours/00_ouverture.tex"
    )
    token = manifest_trace_token(canonical)

    assert assemble_manuel.wrap_object_input(
        "chapitres/1SPE-SUITES/cours/00_ouverture.tex",
        canonical,
    ) == "\n".join(
        [
            f"\\typeout{{NEXUS_OBJECT_BEGIN:{token}}}",
            "\\input{chapitres/1SPE-SUITES/cours/00_ouverture.tex}",
            f"\\typeout{{NEXUS_OBJECT_END:{token}}}",
        ]
    )


def test_render_master_loads_tracked_inventory_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_loader = assemble_manuel.load_tracked_paths
    calls: list[Path] = []

    def recording_loader(git_root: Path) -> frozenset[str]:
        calls.append(git_root)
        return real_loader(git_root)

    monkeypatch.setattr(assemble_manuel, "load_tracked_paths", recording_loader)

    master = assemble_manuel.render_master("professeur", "b" * 32)

    assert master.count("NEXUS_OBJECT_BEGIN:") > 1
    assert calls == [GIT_ROOT]


def test_render_master_marks_every_object_once_in_collection_order() -> None:
    master = assemble_manuel.render_master("professeur", "a" * 32)
    expected_paths = _professor_paths()
    blocks = _marked_blocks(master)

    assert len(blocks) == len(expected_paths)
    assert [input_path for _, _, input_path in blocks] == [
        path.removeprefix("Mathematiques/manuel-maths/") for path in expected_paths
    ]
    assert [token for token, _, _ in blocks] == [
        manifest_trace_token(path) for path in expected_paths
    ]
    assert master.count("NEXUS_OBJECT_BEGIN:") == len(expected_paths)
    assert master.count("NEXUS_OBJECT_END:") == len(expected_paths)
    assert len(re.findall(r"NEXUS_OBJECT_BEGIN:[0-9a-f]{40}", master)) == len(
        expected_paths
    )
    assert len(re.findall(r"NEXUS_OBJECT_END:[0-9a-f]{40}", master)) == len(
        expected_paths
    )


def test_render_master_has_one_run_marker_and_no_marked_transversal_input() -> None:
    run_id = "0123456789abcdef" * 2
    master = assemble_manuel.render_master("professeur", run_id)

    assert re.findall(r"NEXUS_BUILD_RUN:([0-9a-f]{32})", master) == [run_id]
    assert master.count("NEXUS_BUILD_RUN:") == 1
    marked_inputs = {input_path for _, _, input_path in _marked_blocks(master)}
    for path in (
        "transversal/page_de_garde",
        "transversal/avant_propos",
        "transversal/mode_emploi",
        "transversal/index_capacites",
        "transversal/formulaire",
        "transversal/memo_python",
    ):
        assert master.count(f"\\input{{{path}}}") == 1
        assert path not in marked_inputs
        assert not re.search(
            rf"NEXUS_OBJECT_BEGIN:[^\n]+\n\\input\{{{re.escape(path)}\}}",
            master,
        )


def test_real_professor_order_matches_declared_inventory() -> None:
    inventory = json.loads(
        (GIT_ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8")
    )
    assembly = next(
        item
        for item in inventory["assemblies"]
        if item["assembly_id"] == "math:manual:1SPE:professeur"
    )
    professor_paths = _professor_paths()

    assert len(professor_paths) == 870
    assert all(
        path.startswith("Mathematiques/manuel-maths/") for path in professor_paths
    )
    assert professor_paths == assembly["included_objects"]
