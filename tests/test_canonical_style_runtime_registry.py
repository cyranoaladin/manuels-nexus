from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_canonical_style_runtime_registry.py"
REGISTRY = ROOT / "audit" / "CANONICAL_STYLE_RUNTIME_REGISTRY.json"
MARKDOWN = ROOT / "audit" / "CANONICAL_STYLE_RUNTIME_REGISTRY.md"
CONSUMER_GRAPH = ROOT / "audit" / "STYLE_CONSUMER_GRAPH.json"
CONSUMER_GRAPH_MARKDOWN = ROOT / "audit" / "STYLE_CONSUMER_GRAPH.md"
DUPLICATE_FORENSICS = ROOT / "audit" / "STYLE_DUPLICATE_FORENSICS.json"
DUPLICATE_FORENSICS_MARKDOWN = ROOT / "audit" / "STYLE_DUPLICATE_FORENSICS.md"

SPEC = importlib.util.spec_from_file_location("style_registry_builder", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)

EXCLUDED_PARTS = {".git", ".worktrees", "build", "node_modules", "tmp"}

EXPECTED_NONCANONICAL_PRODUCTION_INPUTS = {
    "Mathematiques/manuel-maths/gabarits/chapitre_master.tex",
    "Mathematiques/manuel-maths/gabarits/logo_nexus.png",
    "Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty",
    "Mathematiques/manuel-maths/gabarits/nexus-code.tex",
    "Mathematiques/manuel-maths/gabarits/nexus-figures-nsi.tex",
    "Mathematiques/manuel-maths/gabarits/nexus-figures.tex",
    "Mathematiques/manuel-maths/gabarits/nexus-icons.tex",
    "Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls",
    "Mathematiques/manuel-maths/gabarits/nexus-manuel.cls",
    "Mathematiques/manuel-maths/gabarits/nexus-margin-json.lua",
    "Mathematiques/manuel-maths/gabarits/nexus-margin-layout.lua",
    "Mathematiques/manuel-maths/gabarits/nexus-margin-rail.tex",
    "Mathematiques/manuel-maths/gabarits/nexus-margin-shipout.lua",
    "Mathematiques/manuel-maths/gabarits/nexus-signatures.tex",
    "NSI/gabarits/book_master.tex",
    "NSI/gabarits/chapitre_master.tex",
    "NSI/gabarits/logo_nexus.png",
    "NSI/gabarits/nexus-charte-v6.sty",
    "NSI/gabarits/nexus-code.tex",
    "NSI/gabarits/nexus-figures-nsi.tex",
    "NSI/gabarits/nexus-figures.tex",
    "NSI/gabarits/nexus-icons.tex",
    "NSI/gabarits/nexus-manuel-v5.cls",
    "NSI/gabarits/nexus-manuel.cls",
    "NSI/gabarits/nexus-margin-json.lua",
    "NSI/gabarits/nexus-margin-layout.lua",
    "NSI/gabarits/nexus-margin-rail.tex",
    "NSI/gabarits/nexus-margin-shipout.lua",
    "NSI/gabarits/nexus-signatures.tex",
}


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


def test_unattested_build_recorders_do_not_change_canonical_evidence(tmp_path: Path) -> None:
    build = tmp_path / "Mathematiques/manuel-maths/build/MANUEL_1SPE"
    build.mkdir(parents=True)
    (build / "MANUEL_1SPE_eleve.fls").write_text(
        "PWD /tmp/arbitrary\nINPUT ./gabarits/nexus-manuel-v5.cls\n",
        encoding="utf-8",
    )
    audit = tmp_path / "audit/proved"
    audit.mkdir(parents=True)
    (audit / "manifest.json").write_text(
        json.dumps({"git_sha": "abc123"}), encoding="utf-8"
    )
    (audit / "proved.fls").write_text(
        "PWD /tmp/arbitrary\nINPUT ./gabarits/nexus-manuel-v5.cls\n",
        encoding="utf-8",
    )

    _, recorders = builder.fls_observations(tmp_path, ())

    assert [entry["fls_path"] for entry in recorders] == ["audit/proved/proved.fls"]
    assert recorders[0]["attested_git_sha"] == "abc123"


def test_fls_freshness_requires_an_exact_source_sha_match() -> None:
    assert builder._classify_fls_freshness("abc123", "abc123") == (
        "ATTESTED_CURRENT",
        False,
    )
    assert builder._classify_fls_freshness("abc123", "def456") == (
        "STALE_ATTESTED_OTHER_SHA",
        True,
    )
    assert builder._classify_fls_freshness(None, "def456") == (
        "UNATTESTED_IGNORED",
        None,
    )


def test_extended_asset_inventory_and_duplicate_counts_are_exact() -> None:
    registry, graph, forensics = builder.build_artifacts(ROOT)

    assert registry["summary"] == {
        **registry["summary"],
        # Inventaire, jamais un seuil : ces nombres suivent l'arbre suivi par
        # git. Le composant canonique d'arbres ponderes en ajoute un.
        "physical_files": 64,
        "unique_contents": 43,
        "exact_duplicate_files": 21,
        "exact_duplicate_groups": 18,
    }
    assert graph["summary"]["physical_assets"] == 127
    assert graph["summary"]["unique_asset_contents"] == 64
    assert forensics["summary"]["extended_duplicate_files"] == 63
    assert forensics["summary"]["extended_duplicate_groups"] == 39
    assert len(graph["assets"]) == 127
    assert {entry["path"] for entry in graph["assets"]} == {
        path.relative_to(ROOT).as_posix() for path in builder.asset_files(ROOT)
    }


def test_lifecycle_sets_and_noncanonical_production_inputs_are_closed() -> None:
    _, graph, forensics = builder.build_artifacts(ROOT)
    lifecycle = graph["lifecycle_sets"]

    assert set(graph["noncanonical_production_inputs"]) == EXPECTED_NONCANONICAL_PRODUCTION_INPUTS
    assert len(graph["noncanonical_production_inputs"]) == 29
    assert lifecycle["OBSOLETE_PROVED"] == []
    assert len(lifecycle["HISTORICAL_ONLY"]) == 5
    assert len(lifecycle["VISUAL_FIXTURE"]) == 4
    assert len(lifecycle["ACTIVE_COMPATIBILITY_WRAPPER"]) == 6
    assert len(lifecycle["DORMANT_COMPATIBILITY_WRAPPER"]) == 14
    assert graph["summary"]["unknown_lifecycle"] == 0
    reconciliation = graph["legacy_registry_reconciliation"]
    assert len(reconciliation["confirmed_production_inputs"]) == 15
    assert reconciliation["reference_only_false_positives"] == [
        "NSI/corpus_nsi/02_modeles_documents/nsi-preamble.sty"
    ]
    assert len(reconciliation["newly_explicit_production_inputs"]) == 14
    assert forensics["summary"]["runtime_safe_to_delete"] == 0
    assert all(
        not member["safe_to_delete"]
        for group in forensics["groups"]
        for member in group["members"]
        if member["runtime"]
    )

    evidence = graph["noncanonical_production_evidence"]
    assert {entry["path"] for entry in evidence} == EXPECTED_NONCANONICAL_PRODUCTION_INPUTS
    for entry in evidence:
        assert entry["reason_code"]
        assert entry["reason"]
        assert entry["production_consumers"]
        assert entry["proof"]
        for proof in entry["proof"]:
            source = ROOT / proof["path"]
            assert source.is_file()
            lines = source.read_text(encoding="utf-8", errors="ignore").splitlines()
            assert 1 <= proof["line"] <= len(lines)
            assert proof["needle"] in lines[proof["line"] - 1]


def test_graph_validator_rejects_missing_targets_and_runtime_deletion() -> None:
    _, graph, forensics = builder.build_artifacts(ROOT)
    broken_graph = json.loads(json.dumps(graph))
    broken_graph["edges"][0]["target"] = "missing/style/source.sty"
    try:
        builder.validate_consumer_graph(broken_graph)
    except ValueError as error:
        assert "cible absente" in str(error)
    else:
        raise AssertionError("une cible de graphe absente doit être refusée")

    broken_forensics = json.loads(json.dumps(forensics))
    runtime_member = next(
        member
        for group in broken_forensics["groups"]
        for member in group["members"]
        if member["runtime"]
    )
    runtime_member["safe_to_delete"] = True
    try:
        builder.validate_duplicate_forensics(broken_forensics)
    except ValueError as error:
        assert "runtime" in str(error)
    else:
        raise AssertionError("un duplicata runtime ne doit jamais être supprimable")


def test_all_three_style_reports_are_deterministic_and_current() -> None:
    first = builder.build_artifacts(ROOT)
    second = builder.build_artifacts(ROOT)
    assert first == second

    expected = {
        REGISTRY: builder.serialise(first[0])[0],
        MARKDOWN: builder.serialise(first[0])[1],
        CONSUMER_GRAPH: builder.serialise_consumer_graph(first[1])[0],
        CONSUMER_GRAPH_MARKDOWN: builder.serialise_consumer_graph(first[1])[1],
        DUPLICATE_FORENSICS: builder.serialise_duplicate_forensics(first[2])[0],
        DUPLICATE_FORENSICS_MARKDOWN: builder.serialise_duplicate_forensics(first[2])[1],
    }
    for path, content in expected.items():
        assert path.read_bytes() == content
