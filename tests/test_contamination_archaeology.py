"""On cherche le contenu authentique avant d'en ecrire un nouveau.

Ecrire neuf cents remplacements sans avoir fouille l'historique reviendrait a
jeter du travail authentique qui dort dans un blob. Ces tests verifient que la
fouille est reelle, et surtout qu'elle ne prend pas la version deposee par le
remplissage lui-meme pour un contenu retrouve.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit/CONTAMINATION_ARCHAEOLOGY.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "archaeology", ROOT / "scripts/build_contamination_archaeology.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["archaeology"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_every_contaminated_object_receives_exactly_one_state(payload: dict) -> None:
    summary = payload["summary"]
    assert summary["STATES_SUM_EQUALS_TOTAL"] is True
    assert sum(summary[etat] for etat in payload["states"]) == summary[
        "OBJECTS_CONTAMINATED_BY_533d1919"
    ]


def test_a_recovered_version_never_lived_in_another_chapter(payload: dict) -> None:
    """Sinon on restaurerait un clone en croyant restaurer un original."""

    for record in payload["records"]:
        if record["state"] in {
            "AUTHENTIC_CONTENT_RECOVERED",
            "AUTHENTIC_ALTERNATIVE_FOUND_LATER",
        }:
            assert record["evidence"], record["path"]
            assert record["evidence"]["commit"]
            assert record["evidence"]["body_chars"] >= 80


def test_the_verdict_of_absence_is_backed_by_a_real_history_scan(
    payload: dict,
) -> None:
    """Dire « rien a restaurer » exige d'avoir ouvert les versions."""

    absents = [r for r in payload["records"] if r["state"] == "NO_AUTHENTIC_CONTENT_FOUND"]
    assert absents, "un corpus sans aucun verdict d'absence serait suspect"
    for record in absents:
        assert record["known_versions"] >= 1, record["path"]
        assert record["evidence"] is None


def test_the_committed_archaeology_matches_the_producer(producer) -> None:
    assert producer.main(["--check"]) == 0
