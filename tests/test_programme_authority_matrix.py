"""La matrice des autorités doit être corroborée, et croiser deux NOR doit échouer.

Un registre a réellement attribué au programme de mathématiques de première
2019 le NOR du programme de NSI de terminale. Une table d'autorités qui se
déclarerait vraie n'aurait rien détecté ; celle-ci est vérifiée contre les
registres de sources et les fichiers déposés, et ces tests s'assurent qu'elle
sait redevenir rouge.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_programme_authority_matrix as matrix  # noqa: E402

#: Autorités applicables, telles que tranchées par le Release Owner.
EXPECTED = {
    ("1SPE", "ACTIVE"): "MENE2602917A",
    ("1SPE", "SUPERSEDED"): "MENE1901632A",
    ("1NSI", "ACTIVE"): "MENE1901633A",
    ("TSPE_2026_2027", "ACTIVE"): "MENE1921246A",
    ("TNSI", "ACTIVE"): "MENE1921247A",
    ("TCOMPL", "ACTIVE"): "MENE1921265A",
    ("TEXPERTES", "ACTIVE"): "MENE1921264A",
}


@pytest.fixture(scope="module")
def payload():
    return matrix.build()


@pytest.mark.parametrize("key,nor", sorted(EXPECTED.items()))
def test_each_manual_is_bound_to_its_official_authority(payload, key, nor) -> None:
    manual, state = key
    rows = [
        e for e in payload["authorities"]
        if e["manual"] == manual and e["state"] == state
    ]
    assert len(rows) == 1, f"{manual}/{state}"
    assert rows[0]["nor"] == nor


def test_every_authority_is_corroborated_by_its_registry(payload) -> None:
    uncorroborated = [
        f"{e['manual']}/{e['state']}" for e in payload["authorities"]
        if not e["corroborated_by_registry"]
    ]
    assert uncorroborated == []
    assert payload["summary"]["AUTHORITY_MATRIX_FINDINGS"] == 0


def test_the_2019_maths_programme_is_not_the_nsi_terminale_arrete(payload) -> None:
    """La contradiction historique exacte : MENE1921247A est le NOR de TNSI."""
    legacy = next(
        e for e in payload["authorities"]
        if e["manual"] == "1SPE" and e["state"] == "SUPERSEDED"
    )
    assert legacy["nor"] != "MENE1921247A"
    assert legacy["nor"] == "MENE1901632A"
    assert legacy["superseded_by"] == "MENE2602917A"


def test_the_registry_actually_carries_the_corrected_nor() -> None:
    rows = matrix.registry_rows(matrix.MATHS_REGISTRY)
    assert rows["BO2019_1SPE_specialite.pdf"]["nor"] == "MENE1901632A"


# --- Mutations ----------------------------------------------------------------

def test_crossing_two_nors_is_detected(monkeypatch) -> None:
    """Réattribuer à 1SPE le NOR de TNSI doit faire échouer la corroboration."""
    crossed = tuple(
        {**entry, "nor": "MENE1921247A"}
        if entry["manual"] == "1SPE" and entry["state"] == "SUPERSEDED" else entry
        for entry in matrix.DECLARED
    )
    monkeypatch.setattr(matrix, "DECLARED", crossed)
    payload = matrix.build()
    codes = [f["code"] for f in payload["findings"]]
    assert "AUTHORITY_REGISTRY_MISMATCH" in codes
    assert payload["summary"]["AUTHORITY_MATRIX_FINDINGS"] > 0


def test_one_nor_cannot_be_active_for_two_manuals(monkeypatch) -> None:
    duplicated = tuple(
        {**entry, "nor": "MENE1921247A"}
        if entry["manual"] == "TCOMPL" else entry
        for entry in matrix.DECLARED
    )
    monkeypatch.setattr(matrix, "DECLARED", duplicated)
    codes = [f["code"] for f in matrix.build()["findings"]]
    assert "AUTHORITY_SHARED_BETWEEN_MANUALS" in codes


def test_an_authority_absent_from_the_registry_is_detected(monkeypatch) -> None:
    unknown = tuple(
        {**entry, "registry_file": "BO_INEXISTANT.pdf"}
        if entry["manual"] == "TNSI" else entry
        for entry in matrix.DECLARED
    )
    monkeypatch.setattr(matrix, "DECLARED", unknown)
    codes = [f["code"] for f in matrix.build()["findings"]]
    assert "AUTHORITY_NOT_IN_REGISTRY" in codes


# --- Aucun référentiel ne contredit la matrice --------------------------------

def test_no_referential_contradicts_the_matrix(payload) -> None:
    active = {e["manual"]: e["nor"] for e in payload["authorities"] if e["state"] == "ACTIVE"}
    levels = {
        "1NSI": "1NSI", "TNSI": "TNSI", "1SPE": "1SPE",
        "TSPE": "TSPE_2026_2027", "TCOMPL": "TCOMPL", "TEXPERTES": "TEXPERTES",
    }
    offenders = []
    for directory in ("NSI/referentiel", "Mathematiques/manuel-maths/referentiel"):
        for path in sorted((ROOT / directory).glob("capacites_*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            declared = (data.get("authority") or {}).get("nor")
            expected = active[levels[data["niveau"]]]
            if declared != expected:
                offenders.append((path.name, declared, expected))
    assert offenders == [], offenders


def test_no_referential_still_asks_to_be_reverified() -> None:
    pending = []
    for directory in ("NSI/referentiel", "Mathematiques/manuel-maths/referentiel"):
        for path in sorted((ROOT / directory).glob("capacites_*.json")):
            text = path.read_text(encoding="utf-8")
            if "re-verifier" in text or "re-vérifier" in text:
                data = json.loads(text)
                if (data.get("authority") or {}).get("reverify_resolution") != "VERIFIED_CURRENT":
                    pending.append(path.name)
    assert pending == []
