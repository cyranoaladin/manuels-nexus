"""La lignee anterieure au remplissage decide, pas la ressemblance des corps."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LINEAGE_JSON = ROOT / "audit/PREFILLER_LINEAGE.json"


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def lineage():
    assert LINEAGE_JSON.is_file()
    return json.loads(LINEAGE_JSON.read_text(encoding="utf-8"))


def test_every_group_receives_exactly_one_lineage_case(lineage):
    cases = {
        "CANONICAL_BY_PRE_FILLER_LINEAGE",
        "RECOVERED_BY_LATER_HISTORY",
        "MULTIPLE_PREEXISTING_CONTENT",
        "ALL_EMPTY_PRE_FILLER",
        "PLACEHOLDER_NOT_CONTENT",
    }
    for group in lineage["groups"]:
        assert group["lineage_case"] in cases
    total = sum(lineage["summary"][case] for case in cases)
    assert total == lineage["summary"]["CLONE_GROUPS"]


def test_a_canonical_is_never_a_filler(lineage):
    """Le canonique doit preexister au remplissage, jamais en descendre."""

    for group in lineage["groups"]:
        canonical = group["canonical_path"]
        if canonical is None:
            continue
        assert canonical not in group["filler_paths"], canonical


def test_resolved_groups_name_their_canonical(lineage):
    for group in lineage["groups"]:
        if group["lineage_case"] in {
            "CANONICAL_BY_PRE_FILLER_LINEAGE",
            "RECOVERED_BY_LATER_HISTORY",
        }:
            assert group["canonical_path"], group["digest"]


def test_no_group_needs_an_author_decision(lineage):
    """L'histoire doit trancher : sinon la question remonte a l'auteur."""

    assert lineage["summary"]["UNRESOLVED_AUTHOR_DECISION"] == 0


def test_placeholder_groups_elect_no_canonical(lineage):
    """Un gabarit ne devient pas canonique faute de concurrent."""

    for group in lineage["groups"]:
        if group["lineage_case"] == "PLACEHOLDER_NOT_CONTENT":
            assert group["canonical_path"] is None
            assert group["excess_objects"] == len(group["members"])


def test_the_filler_commit_is_the_declared_oracle(lineage):
    assert lineage["filler_commit"].startswith("533d1919")
    assert lineage["oracle"].endswith("^")


def test_committed_lineage_matches_the_producer(lineage):
    module = _load("prefiller_lineage", "scripts/build_prefiller_lineage.py")
    recomputed = module.classify_groups(ROOT)
    assert recomputed["summary"] == lineage["summary"]
