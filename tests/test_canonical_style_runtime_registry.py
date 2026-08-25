from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_canonical_style_runtime_registry.py"
REGISTRY = ROOT / "audit" / "CANONICAL_STYLE_RUNTIME_REGISTRY.json"
MARKDOWN = ROOT / "audit" / "CANONICAL_STYLE_RUNTIME_REGISTRY.md"

EXCLUDED_PARTS = {".git", ".worktrees", "build", "node_modules", "tmp"}


def _source_style_and_template_paths() -> set[str]:
    paths: set[str] = set()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part.startswith(".") or part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if path.suffix in {".cls", ".sty"}:
            paths.add(relative.as_posix())
            continue
        if path.suffix == ".tex" and "gabarits" in relative.parts:
            paths.add(relative.as_posix())
    return paths


def _literal_assignment(path: Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                return ast.literal_eval(node.value)
    raise AssertionError(f"affectation littérale {name} absente de {path}")


def _expected_chapters() -> dict[str, list[str]]:
    maths_assembler = ROOT / "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
    chapters = _literal_assignment(maths_assembler, "CHAPITRES")
    expected = {
        "1SPE": [chapter for chapter in chapters if chapter.startswith("1SPE-")],
        "TSPE": [chapter for chapter in chapters if chapter.startswith("TSPE-")],
        "TCOMPL": [chapter for chapter in chapters if chapter.startswith("TCOMPL-")],
        "TEXPERTES": [chapter for chapter in chapters if chapter.startswith("TEXP-")],
    }
    for manual in ("1NSI", "TNSI"):
        manifest = json.loads(
            (ROOT / f"NSI/manifests/books/{manual}.json").read_text(encoding="utf-8")
        )
        expected[manual] = [entry["id"] for entry in manifest["chapters"]]
    return expected


def test_registry_builder_is_deterministic_and_current(tmp_path: Path) -> None:
    first_json = tmp_path / "first.json"
    first_md = tmp_path / "first.md"
    second_json = tmp_path / "second.json"
    second_md = tmp_path / "second.md"

    for json_path, md_path in ((first_json, first_md), (second_json, second_md)):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--json-output",
                str(json_path),
                "--md-output",
                str(md_path),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    assert first_json.read_bytes() == second_json.read_bytes()
    assert first_md.read_bytes() == second_md.read_bytes()
    assert first_json.read_bytes() == REGISTRY.read_bytes()
    assert first_md.read_bytes() == MARKDOWN.read_bytes()

    check = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert check.returncode == 0, check.stdout + check.stderr


def test_registry_covers_every_physical_style_and_gabarit_source() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entries = payload["files"]
    paths = {entry["path"] for entry in entries}

    assert paths == _source_style_and_template_paths()
    assert len(entries) == payload["summary"]["physical_files"]
    assert len({entry["sha256"] for entry in entries}) == payload["summary"][
        "unique_contents"
    ]
    assert sum(entry["duplicate_of"] is not None for entry in entries) == payload[
        "summary"
    ]["exact_duplicate_files"]

    required = {
        "path",
        "role",
        "canonical",
        "runtime_consumers",
        "sha256",
        "duplicate_of",
        "deprecated",
        "historical_only",
    }
    for entry in entries:
        assert required <= entry.keys()
        assert entry["sha256"] == hashlib.sha256((ROOT / entry["path"]).read_bytes()).hexdigest()
        consumers = entry["runtime_consumers"]
        assert set(consumers) == {"direct_references", "fls_observations"}
        for observation in consumers["fls_observations"]:
            assert observation["freshness"] in {
                "CURRENT_WORKTREE_UNATTESTED",
                "ATTESTED_CURRENT",
                "STALE_DIFFERENT_WORKTREE",
                "STALE_ATTESTED_OTHER_SHA",
            }
            assert observation["stale"] in {True, False, None}


def test_registry_identifies_canonical_implementations_without_hiding_wrappers() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    summary = payload["summary"]

    assert payload["canonical_targets"]["class"] == "gabarits/common/nexus-manuel.cls"
    assert payload["canonical_targets"]["style"] == "gabarits/common/nexus-charte.sty"
    assert summary["one_canonical_class_implementation_achieved"] is True
    assert summary["one_canonical_style_implementation_achieved"] is True
    assert summary["runtime_clean_without_compatibility_wrappers_achieved"] is False
    assert summary["noncanonical_runtime_potential"] > 0

    files = {entry["path"]: entry for entry in payload["files"]}
    assert files["gabarits/common/nexus-manuel.cls"]["canonical"] is True
    assert files["gabarits/common/nexus-charte.sty"]["canonical"] is True
    assert files["Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls"][
        "role"
    ] == "COMPATIBILITY_CLASS_WRAPPER"
    assert (
        "Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls"
        in summary["noncanonical_runtime_potential_paths"]
    )
    assert files[
        "Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/manuel.sty"
    ]["historical_only"] is True


def test_current_canonical_manifest_chapters_come_from_consumed_sources() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    actual = payload["current_canonical_manifest_chapters"]
    expected = _expected_chapters()

    assert set(actual) == set(expected)
    for manual, chapters in expected.items():
        assert actual[manual]["chapters"] == chapters
        assert actual[manual]["count"] == len(chapters)
        assert (ROOT / actual[manual]["source_path"]).is_file()
        assert actual[manual]["source_sha256"] == hashlib.sha256(
            (ROOT / actual[manual]["source_path"]).read_bytes()
        ).hexdigest()
        assert actual[manual]["consumed_by"] in {
            "Mathematiques/manuel-maths/scripts/assemble_manuel.py",
            "NSI/scripts/assemble_manuel.py",
        }
