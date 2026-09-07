"""Le garde aurait refuse `533d1919`, et n'accuse pas les commits honnetes.

Un garde qui ne refuse rien ne protege rien ; un garde qui refuse tout est
desarme le lendemain. Ces tests verifient les deux bords sur des commits
reels du depot.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FILLER = "533d19198eb7810699a41a7b5275744691420859"


@pytest.fixture(scope="module")
def guard():
    spec = importlib.util.spec_from_file_location(
        "provenance_guard", ROOT / "scripts/guard_commit_content_provenance.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["provenance_guard"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def filler_report(guard):
    return guard.inspect(ROOT, FILLER)


def test_the_filler_commit_would_have_been_refused(filler_report) -> None:
    """Rejeu du commit historique : le garde le refuse, et dit pourquoi."""

    assert filler_report["verdict"] == "REFUSED"
    codes = {finding["code"] for finding in filler_report["findings"]}
    assert "MASS_CONTENT_MUTATION" in codes
    assert "CROSS_MANUAL_CLONE_CONTAMINATION" in codes


def test_the_refusal_names_the_chapters_the_message_hid(filler_report) -> None:
    """Un commit annonce « [LATEX] charte » qui touche cinquante chapitres."""

    assert len(filler_report["chapters_mutated_but_not_declared"]) > 40
    assert filler_report["declared_scope"] == []


def test_the_refusal_names_the_copied_objects(filler_report) -> None:
    contamination = next(
        f for f in filler_report["findings"]
        if f["code"] == "CROSS_MANUAL_CLONE_CONTAMINATION"
    )
    assert contamination["object_count"] > 500
    for objet in contamination["objects"]:
        assert objet["copied_from"]
        assert objet["source_chapter"] != objet["chapter"]


def test_the_message_alone_never_decides(guard) -> None:
    """Le perimetre declare vient du message ; le verdict vient du diff."""

    source = (ROOT / "scripts/guard_commit_content_provenance.py").read_text(
        encoding="utf-8"
    )
    assert "declared_scope" in source
    # Le message ne peut produire un finding qu'en creusant le diff : les deux
    # findings sont construits a partir de `payload_mutes` et `contaminations`,
    # tous deux derives du diff.
    assert "payload_mutes" in source and "contaminations" in source


@pytest.mark.parametrize(
    "commit",
    [
        "66f51a24",  # [TSPE-DERIVATION-CONVEXITE][LOT-2-4] chapitre nomme
        "399e994f",  # [1SPE-TRIGONOMETRIE][LOT-0-7] chapitre nomme
    ],
)
def test_an_honest_chapter_commit_is_accepted(guard, commit: str) -> None:
    """Un commit qui nomme le chapitre qu'il ecrit passe sans friction."""

    rapport = guard.inspect(ROOT, commit)
    assert rapport["verdict"] == "ACCEPTED", rapport["findings"]


def test_an_explicit_provenance_trailer_lifts_the_scope_finding(guard) -> None:
    """Un commit d'infrastructure qui DOIT toucher au contenu peut le dire."""

    assert guard.has_explicit_provenance(
        "[LATEX] refonte\n\nEXPLICIT_CONTENT_CHANGE_PROVENANCE: migration charte v6\n"
    )
    assert not guard.has_explicit_provenance("[LATEX] refonte\n")
    assert not guard.has_explicit_provenance(
        "[LATEX] refonte\n\nEXPLICIT_CONTENT_CHANGE_PROVENANCE:\n"
    )
