"""La forensique de `533d1919`, rejouee, ne laisse aucun objet non classe.

L'analyse precedente concluait a 1196 objets de contenu inedit. Elle
comparait des corps portant encore l'identifiant de l'objet, et ne
confrontait les creations qu'aux corps ANTERIEURS au commit : une banque
recopiee quinze fois a l'interieur du meme commit passait pour quinze
creations originales.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit/FILLER_COMMIT_FORENSICS_V2.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "filler_v2", ROOT / "scripts/build_filler_commit_forensics_v2.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["filler_v2"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_the_classification_is_total(payload: dict) -> None:
    """`UNKNOWN` interdit : une mutation non classee est une mutation non vue."""

    summary = payload["summary"]
    assert summary["UNKNOWN"] == 0
    assert summary["CLASSES_SUM_EQUALS_TOTAL"] is True
    assert sum(summary[classe] for classe in payload["classes"]) == summary[
        "PEDAGOGICAL_MUTATIONS"
    ]


def test_it_formally_supersedes_the_previous_report(payload: dict) -> None:
    assert payload["supersedes"] == "audit/FILLER_COMMIT_FORENSICS.json"
    assert payload["supersede_reason"]


def test_a_body_copied_within_the_commit_is_never_new_authoring(payload: dict) -> None:
    """Aucun des N exemplaires ne peut revendiquer d'etre l'original.

    Rien ne designe lequel le serait : la revendication demande une preuve, et
    il n'y en a pas. Les N sont donc des copies, et le groupe est publie.
    """

    copies = {
        chemin
        for groupe in payload["within_commit_groups_without_established_original"]
        for chemin in groupe["paths"]
    }
    for record in payload["records"]:
        if record["path"] in copies:
            assert record["verdict"] == "FILLER_COPY", record["path"]


def test_every_copy_names_what_it_copies(payload: dict) -> None:
    for record in payload["records"]:
        if record["verdict"] == "FILLER_COPY":
            assert record["why"], record["path"]
            assert (
                "copie de" in record["why"]
                or "cree" in record["why"]
                or "remplace" in record["why"]
            )


def test_the_committed_report_matches_the_producer(producer) -> None:
    assert producer.main(["--check"]) == 0
