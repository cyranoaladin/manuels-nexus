"""Triage des fausses couvertures : nommer la source, ou constater la lacune."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TRIAGE_JSON = ROOT / "audit/FALSE_COVERAGE_TRIAGE.json"


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def triage():
    assert TRIAGE_JSON.is_file()
    return json.loads(TRIAGE_JSON.read_text(encoding="utf-8"))


def test_every_atom_receives_one_of_the_three_states(triage):
    states = {"COVERED_BY_REAL_CONTENT", "TRUE_CONTENT_GAP", "NON_APPLICABLE_MAPPING_ERROR"}
    for entry in triage["entries"]:
        assert entry["state"] in states
    total = sum(triage["summary"][state] for state in states)
    assert total == triage["summary"]["FALSE_COVERAGE_TRIAGED"]


def test_a_covered_atom_must_name_its_source(triage):
    """Sans source nommee, « couvert » n'est qu'une affirmation."""

    for entry in triage["entries"]:
        if entry["state"] != "COVERED_BY_REAL_CONTENT":
            continue
        assert entry["candidate_source"], entry["atom_id"]
        assert (ROOT / entry["candidate_source"]).is_file(), entry["candidate_source"]
        assert entry["candidate_source_term_hits"] >= 2
        assert entry["missing_terms"] == [], entry["atom_id"]


def test_a_covered_source_belongs_to_the_declaring_manual(triage, ):
    """Un atome de premiere ne peut pas etre couvert par un chapitre de terminale."""

    module = _load("false_coverage_triage", "scripts/build_false_coverage_triage.py")
    for entry in triage["entries"]:
        source = entry.get("candidate_source")
        if not source:
            continue
        prefix = module.MANUAL_CHAPTER_PREFIX[entry["manual"]]
        chapter = source.split("/chapitres/", 1)[1].split("/", 1)[0]
        assert chapter.startswith(prefix), f"{entry['atom_id']} -> {source}"


def test_a_gap_names_the_missing_notion(triage):
    """Une lacune doit dire ce qui manque, pas seulement qu'il manque."""

    for entry in triage["entries"]:
        if entry["state"] != "TRUE_CONTENT_GAP":
            continue
        assert entry["why"]
        assert entry["official_wording"]


def test_generic_words_cannot_carry_a_covered_verdict(triage):
    """Un mot present partout ne prouve pas qu'une notion est enseignee."""

    module = _load("false_coverage_triage_2", "scripts/build_false_coverage_triage.py")
    assert module.GENERIC_CEILING > module.EVIDENCE_THRESHOLD
    for entry in triage["entries"]:
        if entry["state"] != "COVERED_BY_REAL_CONTENT":
            continue
        assert entry["discriminating_terms"], entry["atom_id"]


def test_committed_triage_matches_the_producer(triage):
    module = _load("false_coverage_triage_3", "scripts/build_false_coverage_triage.py")
    recomputed = module.build(ROOT)
    assert recomputed["summary"] == triage["summary"]
