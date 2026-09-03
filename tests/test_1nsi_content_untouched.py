"""Le contenu 1NSI n'a pas bougé, et la mesure sait dire le contraire.

Quinze échecs de tests 1NSI ont été refermés pendant la campagne 1SPE, par
réobservation seule. Une charte partagée a en revanche bien changé -- elle
change la mise en page de la NSI, pas son propos. Ce module vérifie que les
deux comptes restent distincts, et qu'aucun ne peut être maquillé en l'autre.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1nsi_content_untouched as gate  # noqa: E402


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


def test_no_1nsi_content_file_changed(payload: dict[str, Any]) -> None:
    assert payload["summary"]["1NSI_CONTENT_CHANGED"] == "NO"
    assert payload["summary"]["CONTENT_FILES_CHANGED"] == 0
    assert payload["changed"]["CONTENT"] == []


def test_the_baseline_is_the_commit_the_repository_itself_named(
    payload: dict[str, Any],
) -> None:
    """Le point de comparaison n'est pas choisi par le contrôle."""

    source = ROOT / payload["baseline_is_read_not_chosen"]
    assert source.is_file()
    recorded = json.loads(source.read_text(encoding="utf-8"))["cause"]
    assert payload["baseline"]["sha"] == recorded["sha"]
    assert payload["baseline"]["subject"] == recorded["subject"]


def test_the_shared_template_change_is_reported_not_hidden(
    payload: dict[str, Any],
) -> None:
    """La charte a bougé : le dire est le contraire de le dissimuler."""

    assert payload["summary"]["SHARED_TEMPLATE_FILES_CHANGED"] > 0
    assert payload["changed"]["SHARED_TEMPLATE"]
    for path in payload["changed"]["SHARED_TEMPLATE"]:
        assert path.startswith("NSI/gabarits/"), path


def test_the_discipline_copies_still_match(payload: dict[str, Any]) -> None:
    assert payload["summary"]["SHARED_TEMPLATE_COPIES_DIVERGING"] == 0
    assert payload["shared_template_copies_diverging"] == []


# ---------------------------------------------------------------------------
#  Mutations
# ---------------------------------------------------------------------------


def test_a_content_file_change_is_blocking(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        gate,
        "changed_paths",
        lambda base: [
            "NSI/chapitres/1NSI-RESEAUX/cours/1NSI-RES-COURS-C1.tex",
            "NSI/gabarits/nexus-manuel.cls",
        ],
    )

    result = gate.build()

    assert result["summary"]["1NSI_CONTENT_CHANGED"] == "YES"
    assert result["summary"]["CONTENT_FILES_CHANGED"] == 1
    assert gate.main(["--check"]) == 1


def test_a_template_change_alone_is_not_a_content_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """L'inverse compte autant : ne pas crier au contenu pour une charte."""

    monkeypatch.setattr(
        gate, "changed_paths", lambda base: ["NSI/gabarits/nexus-manuel.cls"]
    )

    result = gate.build()

    assert result["summary"]["1NSI_CONTENT_CHANGED"] == "NO"
    assert result["summary"]["SHARED_TEMPLATE_FILES_CHANGED"] == 1
    assert gate.main(["--check"]) == 0


def test_a_wrapper_that_stops_matching_its_twin_is_seen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Un adaptateur qui diverge entre les disciplines est une régression."""

    maths = tmp_path / "maths"
    maths.mkdir()
    (maths / "nexus-decor.sty").write_text("une version", encoding="utf-8")
    monkeypatch.setattr(gate, "MATHS_TEMPLATES", maths)

    divergent = gate.diverging_copies(["NSI/gabarits/nexus-decor.sty"])

    assert len(divergent) == 1
    assert divergent[0]["file"] == "NSI/gabarits/nexus-decor.sty"


def test_a_missing_reobservation_register_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sans point de comparaison nommé, il n'y a rien à conclure."""

    monkeypatch.setattr(gate, "REOBSERVATION", tmp_path / "absent.json")

    with pytest.raises(gate.ContentError):
        gate.build()
    assert gate.main(["--check"]) == 2
