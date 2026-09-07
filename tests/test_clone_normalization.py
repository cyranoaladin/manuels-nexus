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


# ---------------------------------------------------------------------------
# L'identite vit aussi dans les sous-objets
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def ledger():
    return _module("clone_norm_ledger_ident", "scripts/build_p0_content_clone_ledger.py")


@pytest.mark.parametrize(
    "token,chapter",
    [
        ("TSPE-DERCONV-FR-R1", "TSPE-DERIVATION-CONVEXITE"),
        ("TSPE-LIMFCT-EX-001", "TSPE-LIMITES-FONCTIONS"),
        ("TEXP-ARI-FR-R4-EX1", "TEXP-ARITHMETIQUE"),
        ("TCOMPL-MF-RE-C06", "TCOMPL-MODELES-FONCTION"),
        ("TEXP-CAG-ME-001", "TEXP-COMPLEXES-ALGEBRE-GEOMETRIE"),
        ("TCOMPL-BAYES-EX-001", "TCOMPL-INFERENCE-BAYESIENNE"),
        ("1SPE-SECDEG-EX-001", "1SPE-SECOND-DEGRE"),
    ],
)
def test_an_abbreviation_of_the_chapter_is_identity(ledger, token, chapter) -> None:
    """Quatre styles d'abreviation coexistent, et tous nomment le chapitre."""

    assert ledger.belongs_to_chapter(token, chapter) is True


@pytest.mark.parametrize(
    "token,chapter",
    [
        # `ARI` est bien une sous-suite de `MATRICES-MARKOV` -- A-R-I dans
        # « m-A-t-R-I-ces » -- mais aucun mot n'y commence par A.
        ("TEXP-ARI-ME-001", "TEXP-MATRICES-MARKOV"),
        ("TEXP-GRA-ME-001", "TEXP-ARITHMETIQUE"),
        ("TSPE-DERCONV-ME-001", "TEXP-ARITHMETIQUE"),
        ("TCOMPL-BAYES-EX-001", "TCOMPL-CALCULS-AIRES"),
        ("TCOMPL-ECH-EX-001", "TCOMPL-INEGALITES"),
    ],
)
def test_a_reference_to_another_chapter_is_content(ledger, token, chapter) -> None:
    """Un renvoi vers un autre chapitre doit survivre a la normalisation."""

    assert ledger.belongs_to_chapter(token, chapter) is False
