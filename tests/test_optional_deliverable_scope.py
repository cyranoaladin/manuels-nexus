"""Un livrable optionnel ne bloque pas la release ; un livrable requis, si.

Décision humaine du Release Owner : `1SPE::banque_evaluations` et
`TSPE_2026_2027::banque_evaluations` restent `PROPOSED_NOT_APPROVED`,
`OPTIONAL = true`, et sont `NOT_REQUIRED_FOR_2026_2027_RELEASE`. Elles ne
doivent donc plus produire de `PRODUCT_P1`.

Le risque de cette décision est qu'elle serve de gabarit : qu'un livrable
requis devienne muet parce qu'il ressemble à un optionnel. Les tests
ci-dessous essaient d'obtenir ce silence.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import inventory_collection as ic  # noqa: E402


def test_the_two_banks_are_named_not_pattern_matched() -> None:
    """La liste est nominative : ni un motif, ni un suffixe."""
    assert set(ic.NOT_REQUIRED_FOR_2026_2027_RELEASE) == {
        ("1SPE", "banque_evaluations"),
        ("TSPE_2026_2027", "banque_evaluations"),
    }
    for reference in ic.NOT_REQUIRED_FOR_2026_2027_RELEASE.values():
        assert "abenrhouma" in reference or "RELEASE_OWNER" in reference


def test_an_optional_bank_is_not_required() -> None:
    assert ic._variant_is_required("1SPE", "banque_evaluations") is False
    assert ic._variant_is_required("TSPE_2026_2027", "banque_evaluations") is False


def test_every_other_variant_stays_required() -> None:
    """L'exemption ne déborde pas sur ses voisins."""
    for manual, variant in (
        ("1SPE", "livret_methodes"),
        ("1SPE", "manuel_eleve"),
        ("1SPE", "livret_remediation"),
        ("TSPE_2026_2027", "livret_methodes"),
        ("TSPE_2026_2027", "manuel_professeur"),
        ("1NSI", "evaluations"),
        ("TNSI", "banque_ecrite"),
        ("TNSI", "banque_pratique"),
    ):
        assert ic._variant_is_required(manual, variant) is True, (manual, variant)


def test_the_same_variant_name_stays_required_on_another_manual() -> None:
    """`banque_evaluations` n'est pas exempté en tant que NOM."""
    assert ic._variant_is_required("TCOMPL", "banque_evaluations") is True
    assert ic._variant_is_required("1NSI", "banque_evaluations") is True


def test_promoting_a_bank_to_required_makes_it_block_again(monkeypatch) -> None:
    """Passage explicite futur à required -> blocker tant qu'elle n'est pas prête."""
    monkeypatch.setattr(ic, "NOT_REQUIRED_FOR_2026_2027_RELEASE", {})
    assert ic._variant_is_required("1SPE", "banque_evaluations") is True


def test_the_gate_no_longer_counts_the_two_banks() -> None:
    """Sur l'observation courante, aucun motif ne vise ces deux livrables."""
    import json

    observation = ROOT / "audit/gate_observations"
    fichiers = sorted(observation.glob("release-strict-*.json"))
    if not fichiers:
        pytest.skip("aucune observation release-strict déposée")
    reasons = json.loads(fichiers[-1].read_text(encoding="utf-8"))["reasons"]
    fautifs = [
        r for r in reasons
        if "banque_evaluations" in r
        and any(m in r for m in ("1SPE", "TSPE_2026_2027"))
    ]
    assert fautifs == [], fautifs


def test_a_missing_required_deliverable_still_blocks() -> None:
    """Le contrôle reste vivant : un requis absent produit toujours un motif."""
    assert ic._variant_is_required("TNSI", "version_amenagee") is True
    assert ic._variant_is_required("1NSI", "livret_methodes") is True
