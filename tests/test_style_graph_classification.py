"""Tests de la classification read-only du graphe de styles.

Le controle doit distinguer un chargement LaTeX reel d'une simple mention de
chemin, et ne jamais proposer de suppression sans preuve de consommateurs vide.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import classify_style_graph as graph  # noqa: E402

REPORT_PATH = ROOT / "audit" / "STYLE_GRAPH_CLASSIFICATION.json"
VALID_CLASSES = {
    "ACTIVE_CANONICAL",
    "ACTIVE_NONCANONICAL",
    "HISTORICAL_ONLY",
    "FIXTURE_ONLY",
    "OBSOLETE",
}


def _report() -> dict:
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def test_report_covers_every_tracked_style_file() -> None:
    tracked = {
        item
        for item in graph.tracked_files(ROOT)
        if item.endswith(graph.STYLE_SUFFIXES)
    }
    assert {entry["path"] for entry in _report()["files"]} == tracked


def test_every_file_carries_one_valid_class_and_a_rationale() -> None:
    for entry in _report()["files"]:
        assert entry["classification"] in VALID_CLASSES, entry
        assert entry["rationale"], entry["path"]


def test_the_classification_is_deterministic() -> None:
    first = graph.build_report(ROOT)
    second = graph.build_report(ROOT)
    assert first == second


def test_a_python_string_literal_is_never_a_load_edge() -> None:
    """`\\RequirePackage{...}` dans un script Python est une mention, pas un load."""

    for entry in _report()["files"]:
        for reference in entry["references"]:
            if reference["relation"] == "load":
                assert Path(reference["consumer"]).suffix in {".tex", ".sty", ".cls"}, (
                    entry["path"],
                    reference,
                )


def test_nothing_is_declared_safe_to_delete_while_it_has_a_consumer() -> None:
    for entry in _report()["files"]:
        if entry["safe_to_delete"]:
            assert entry["references"] == [], entry["path"]


def test_duplicate_groups_never_pick_an_arbitrary_survivor() -> None:
    """Entre deux copies par discipline, aucun survivant n'est derivable."""

    for group in _report()["duplicate_groups"]:
        if group["canonical_survivor"] is None:
            assert group["duplicate_kind"] == "PER_DISCIPLINE_COPY"
            assert group["resolution_required"]
            assert not any(group["safe_to_delete"].values())
        else:
            assert group["canonical_survivor"] in group["members"]


def test_the_report_is_read_only_by_construction() -> None:
    report = _report()
    assert report["read_only"] is True
    assert report["deletes_nothing"] is True


def test_no_load_edge_files_are_listed_explicitly() -> None:
    report = _report()
    listed = set(report["no_load_edge_files"])
    computed = {
        entry["path"]
        for entry in report["files"]
        if not any(ref["relation"] == "load" for ref in entry["references"])
    }
    assert listed == computed
    assert report["no_load_edge_count"] == len(listed)
