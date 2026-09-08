"""Les populations mathématiques doivent s'additionner exactement.

Deux chiffres coexistaient sans être comparables : `MISSING_ORACLE = 91`
compte des objets sans bloc de vérification, tandis que `GAP` et `NO_RECEIPTS`
comptent des chapitres selon les reçus déposés. Les juxtaposer laissait croire
à une contradiction. Ces tests exigent que chaque objet soit compté une fois et
une seule.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_mathematics_population_reconciliation as reconciliation  # noqa: E402


@pytest.fixture(scope="module")
def summary():
    return reconciliation.build()["summary"]


def test_every_object_is_counted_exactly_once(summary) -> None:
    accounted = (
        summary["FORMAL_ASSERTION_OBJECTS"]
        + summary["OBJECTS_MISSING_ORACLE"]
        + summary["NON_FORMALIZABLE_OBJECTS"]
        + summary["TRULY_NOT_MATHEMATICAL"]
    )
    assert accounted == summary["MATHEMATICS_OBJECTS_TOTAL"]
    assert summary["MATHEMATICS_POPULATION_UNRECONCILED"] == 0


def test_object_and_chapter_populations_are_not_conflated(summary) -> None:
    """Un compte d'objets et un compte de chapitres ne se comparent pas."""
    assert summary["MATHEMATICS_OBJECTS_TOTAL"] > summary["CHAPTERS_TOTAL"]
    assert summary["CHAPTER_ORACLE_GAPS"] + summary["ORACLE_EVIDENCE_MISSING_RECEIPT"] \
        + summary["CHAPTER_ORACLE_COMPLETE"] == summary["CHAPTERS_TOTAL"]


def test_stored_receipts_never_exceed_executed_objects(summary) -> None:
    """Un reçu conservé suppose une exécution ; l'inverse n'est pas vrai.

    On ne compare que les reçus qui attestent une EXECUTION. Le verificateur
    depose aussi un reçu `manual_review` pour chaque objet sans bloc de
    verification : le compter ici ferait passer pour des preuves des objets
    dont il constate justement qu'ils n'en portent pas.
    """

    assert summary["EXECUTED_RECEIPTS"] == (
        summary["RECEIPT_PASS"] + summary["RECEIPT_FAIL"]
    )
    assert summary["STORED_SYMPY_RECEIPTS"] == (
        summary["EXECUTED_RECEIPTS"] + summary["RECEIPT_MANUAL_REVIEW"]
    )
    # L'invariant qui compte n'est pas une inegalite entre deux comptages
    # etablis sur des populations differentes -- l'un par objet d'inventaire,
    # l'autre par chapitre. C'est qu'AUCUN recu ne survive a sa source :
    # quatre l'avaient fait, pour des exercices de trigonometrie supprimes,
    # et ils certifiaient du vide depuis.
    assert summary["RECEIPTS_WITHOUT_LIVE_SOURCE"] == 0
    assert summary["EXECUTED_BUT_UNRECEIPTED"] == (
        summary["FORMAL_ASSERTION_OBJECTS"] - summary["EXECUTED_RECEIPTS"]
    )


def test_receipt_verdicts_add_up(summary) -> None:
    assert summary["RECEIPT_PASS"] + summary["RECEIPT_MANUAL_REVIEW"] \
        + summary["RECEIPT_FAIL"] == summary["STORED_SYMPY_RECEIPTS"]


def test_no_failing_receipt_is_hidden(summary) -> None:
    assert summary["RECEIPT_FAIL"] == 0


def test_the_reconciliation_declares_its_freshness() -> None:
    import evidence_freshness as freshness

    payload = reconciliation.build()
    assessment = freshness.assess(payload["freshness"])
    assert assessment["FRESHNESS_STATUS"] == freshness.CURRENT
