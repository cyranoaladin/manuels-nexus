"""Chaque fichier de style porte un scope nomme ; aucun UNKNOWN.

Vingt-quatre fichiers n'ont aucune arete de chargement. Cela ne prouve PAS
qu'ils soient historiques : ils devront etre classes HISTORICAL / FIXTURE /
OBSOLETE / DISCOVERY_GAP dans un lot ulterieur. Ce test verrouille seulement ce
qui est acquis aujourd'hui : la classification est totale et explicite, et
l'absence d'arete est mesuree separement de la classification.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit" / "STYLE_GRAPH_CLASSIFICATION.json"
NAMED_SCOPES = {"ACTIVE_CANONICAL", "ACTIVE_NONCANONICAL", "HISTORICAL_ONLY"}


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_every_style_file_carries_an_explicit_named_scope(payload: dict) -> None:
    observed = {str(row["classification"]) for row in payload["files"]}

    assert observed <= NAMED_SCOPES, f"scope non nomme: {observed - NAMED_SCOPES}"
    assert "UNKNOWN" not in observed
    assert len(payload["files"]) == payload["physical_file_count"]


def test_the_classification_counts_are_total(payload: dict) -> None:
    counts = payload["classification_counts"]

    assert sum(counts.values()) == payload["physical_file_count"]
    assert set(counts) <= NAMED_SCOPES


def test_absence_of_a_load_edge_is_measured_apart_from_the_scope(payload: dict) -> None:
    """Sans arete n'est pas un scope : c'est une observation a instruire."""

    assert payload["no_load_edge_count"] == len(payload["no_load_edge_files"])
    edgeless = set(payload["no_load_edge_files"])
    historical = {
        row["path"]
        for row in payload["files"]
        if row["classification"] == "HISTORICAL_ONLY"
    }
    assert edgeless - historical, (
        "des fichiers sans arete ne sont pas classes historiques : "
        "leur classification fine reste a instruire"
    )
