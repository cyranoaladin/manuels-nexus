"""Le programme se choisit sur l'année scolaire, pas sur la date de publication.

Un texte paru en 2026 n'est pas forcément le programme de 2026-2027. Le nouveau
programme de Terminale spécialité paraît en 2026 et n'entre en vigueur qu'en
2027-2028 : l'appliquer au manuel courant enseignerait un programme qui n'existe
pas encore pour ces élèves. La faute symétrique existe — ramener la Première au
texte de 2019 alors que le nouveau s'applique dès cette rentrée.

Ce module fige les trois interdits, et vérifie que la sélection ne repose sur
rien d'autre que l'intervalle d'application.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_programme_authority_matrix as gate  # noqa: E402

#: Ce que le Release Owner a nommé, manuel par manuel.
EXPECTED_AUTHORITY = {
    "1SPE": "MENE2602917A",
    "TSPE_2026_2027": "MENE1921246A",
    "TCOMPL": "MENE1921265A",
    "TEXPERTES": "MENE1921264A",
    "1NSI": "MENE1901633A",
    "TNSI": "MENE1921247A",
}


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


def authority(payload: dict[str, Any], manual: str) -> dict[str, Any]:
    return next(row for row in payload["authorities"] if row["manual_id"] == manual)


# ---------------------------------------------------------------------------
#  L'autorité retenue est celle de l'année
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("manual", sorted(EXPECTED_AUTHORITY))
def test_each_manual_uses_the_authority_of_its_school_year(
    payload: dict[str, Any], manual: str
) -> None:
    row = authority(payload, manual)

    assert row["official_NOR"] == EXPECTED_AUTHORITY[manual]
    assert row["school_year"] == "2026-2027"
    assert row["official_source_sha256"].startswith("sha256:")
    assert "tombe dans" in row["selected_because"]


def test_no_authority_is_wrong_year_or_ambiguous(payload: dict[str, Any]) -> None:
    for metric in gate.BLOCKING:
        assert payload["summary"][metric] == 0, metric


# ---------------------------------------------------------------------------
#  Les trois interdits
# ---------------------------------------------------------------------------


def test_terminale_2026_2027_never_uses_the_2027_2028_programme(
    payload: dict[str, Any],
) -> None:
    """Le nouveau programme de Terminale existe : il ne s'applique pas encore."""

    row = authority(payload, "TSPE_2026_2027")

    assert row["official_NOR"] == "MENE1921246A"
    assert row["successor_NOR_if_known"] == "MENE2602919A"
    assert row["successor_effective_from"] == "2027-2028"
    assert row["successor_status"] == "FUTURE_NOT_APPLICABLE"
    # Et la règle qui l'écarte est bien l'intervalle, pas une exception écrite.
    successor = {"effective_from": "2027-2028", "effective_until": None}
    assert gate.applies_to(successor, "2026-2027") is False
    assert gate.applies_to(successor, "2027-2028") is True


def test_complementaires_2026_2027_never_uses_its_future_programme(
    payload: dict[str, Any],
) -> None:
    row = authority(payload, "TCOMPL")

    assert row["official_NOR"] == "MENE1921265A"
    assert row["successor_status"] == "FUTURE_NOT_APPLICABLE"
    assert row["successor_effective_from"] == "2027-2028"
    # Le NOR du successeur n'est pas archivé : il n'est donc pas inventé.
    assert row["successor_NOR_if_known"] is None
    assert "pas invente" in row["successor_why_not_applied"]


def test_premiere_never_falls_back_to_the_2019_programme(
    payload: dict[str, Any],
) -> None:
    """La faute symétrique : revenir au texte que le nouveau a remplacé."""

    row = authority(payload, "1SPE")

    assert row["official_NOR"] == "MENE2602917A"
    assert row["effective_from"] == "2026-2027"
    # Un texte de 2019 ne couvrirait pas 2026-2027 s'il portait un terme.
    superseded = {"effective_from": "2019-2020", "effective_until": "2025-2026"}
    assert gate.applies_to(superseded, "2026-2027") is False


# ---------------------------------------------------------------------------
#  La sélection ne repose sur rien d'autre que l'intervalle
# ---------------------------------------------------------------------------


def test_a_more_recent_publication_does_not_win_by_itself() -> None:
    """« La dernière version publiée » n'est pas un critère."""

    current = {"effective_from": "2020-2021", "effective_until": "2026-2027"}
    newer = {"effective_from": "2027-2028", "effective_until": None}

    assert gate.applies_to(current, "2026-2027") is True
    assert gate.applies_to(newer, "2026-2027") is False


def test_an_authority_without_an_effective_date_never_applies() -> None:
    assert gate.applies_to({"effective_from": None}, "2026-2027") is False
    assert gate.applies_to({}, "2026-2027") is False


def test_an_expired_authority_stops_applying_after_its_term() -> None:
    entry = {"effective_from": "2020-2021", "effective_until": "2026-2027"}

    assert gate.applies_to(entry, "2026-2027") is True
    assert gate.applies_to(entry, "2027-2028") is False


def test_the_source_digest_is_verified_against_the_archived_file(
    payload: dict[str, Any],
) -> None:
    """Une autorité dont la source a changé n'est plus celle qu'on a lue."""

    import hashlib

    assert payload["summary"]["AUTHORITY_SOURCE_DIGEST_MISMATCH"] == 0
    for row in payload["authorities"]:
        source = ROOT / row["official_source"]
        assert source.is_file(), row["manual_id"]
        actual = "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()
        assert actual == row["official_source_sha256"], row["manual_id"]


def test_a_digest_drift_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """La mutation qui donne sa valeur au contrôle."""

    real = gate.registry()
    altered = {
        manual: {**entry, "local_archival_digest": "sha256:" + "0" * 64}
        for manual, entry in real.items()
    }
    monkeypatch.setattr(gate, "registry", lambda: altered)

    result = gate.build()

    assert result["summary"]["AUTHORITY_SOURCE_DIGEST_MISMATCH"] == 6
    assert gate.main(["--check"]) == 1


def test_a_manual_whose_authority_expired_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real = gate.registry()
    altered = {
        manual: (
            {**entry, "effective_until": "2024-2025"}
            if manual == "TCOMPL"
            else entry
        )
        for manual, entry in real.items()
    }
    monkeypatch.setattr(gate, "registry", lambda: altered)

    result = gate.build()

    assert result["summary"]["WRONG_YEAR_AUTHORITY"] == 1
    assert result["wrong_year_authorities"][0]["manual_id"] == "TCOMPL"
