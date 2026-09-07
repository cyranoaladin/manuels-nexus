"""La normalisation des clones ne se trompe dans aucun des deux sens.

Un FAUX POSITIF fusionne deux objets differents : on declarerait clone un
exercice authentique, on le retirerait, et l'eleve perdrait un contenu reel.
Un FAUX NEGATIF laisse passer une copie -- c'est ce qui s'est produit neuf
cents fois, parce que le corps compare portait encore l'identifiant de
l'objet.

Les fixtures vivent dans `scripts/clone_normalization_fixtures.py`, ou elles
restent lisibles et contestables. Ces tests les executent.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import clone_normalization_fixtures as fixtures  # noqa: E402


def _module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def normalize():
    ledger = _module("clone_norm_ledger", "scripts/build_p0_content_clone_ledger.py")
    return ledger.pedagogical_body


@pytest.mark.parametrize(
    "label,gauche,droite",
    fixtures.MUST_MATCH,
    ids=[row[0] for row in fixtures.MUST_MATCH],
)
def test_only_a_technical_identity_separates_them(
    normalize, label: str, gauche: str, droite: str
) -> None:
    assert normalize(gauche) == normalize(droite), (
        f"faux negatif : {label} -- deux copies restent invisibles"
    )


@pytest.mark.parametrize(
    "label,gauche,droite",
    fixtures.MUST_DIFFER,
    ids=[row[0] for row in fixtures.MUST_DIFFER],
)
def test_a_real_difference_survives_normalisation(
    normalize, label: str, gauche: str, droite: str
) -> None:
    assert normalize(gauche) != normalize(droite), (
        f"faux positif : {label} -- un contenu authentique serait declare clone"
    )


def test_the_bench_is_not_empty_and_covers_both_directions() -> None:
    """Un banc vide prouverait zero dans les deux sens sans rien mesurer."""

    assert len(fixtures.MUST_MATCH) >= 5
    assert len(fixtures.MUST_DIFFER) >= 10
    exigees = {
        "valeur numerique",
        "formule",
        "contexte",
        "question ajoutee",
        "donnee modifiee",
        "capacite differente",
    }
    libelles = " ".join(row[0] for row in fixtures.MUST_DIFFER)
    for exigee in exigees:
        assert exigee in libelles, f"le banc ne couvre pas : {exigee}"
