"""Des mathematiques de Terminale ne sont pas de la NSI de Premiere.

Le manuel eleve imprimait, entre un exercice Python de tri et le chapitre
suivant, une fiche « Deriver une fonction composee » declaree comme capacite
« ecrire un algorithme de recherche d'une occurrence dans un tableau ». Elle
etait `approved`, et son corps etait unique : aucune detection de clonage ne
pouvait la voir.

Ces tests fixent le critere qui la voit, et le gardent honnete dans les deux
sens : il doit condamner ce qui releve de l'analyse, et epargner ce qui
mobilise des mathematiques SANS en relever -- une distance euclidienne dans un
exercice de k plus proches voisins reste de la NSI.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "audit/NSI_CROSS_DISCIPLINE_CONTENT_LEDGER.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "nsi_cross_discipline", ROOT / "scripts/build_nsi_cross_discipline_ledger.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def test_the_committed_ledger_matches_the_producer(producer) -> None:
    assert producer.main(["--check"]) == 0


def test_the_current_cross_discipline_debt_is_exhaustively_recorded(
    payload: dict,
) -> None:
    """Le ledger peut être rouge, mais jamais incomplet ou auto-innocentant."""

    condemned = [
        row
        for row in payload["objects"]
        if row["verdict"] == "CROSS_DISCIPLINE_TERMINALE_MATHS"
    ]
    assert payload["condemned_count"] == len(condemned)
    assert payload["condemned_paths"] == sorted(row["path"] for row in condemned)
    assert payload["unknown"] == 0
    assert payload["objects_scanned"] > 0
    assert payload["counts"].get("REQUIRES_EXPLICIT_ADJUDICATION", 0) == 0


def test_every_object_receives_an_explicit_verdict(payload: dict) -> None:
    """UNKNOWN = 0 : rien n'est classe par defaut."""

    for row in payload["objects"]:
        assert row["verdict"] in {
            "CROSS_DISCIPLINE_TERMINALE_MATHS",
            "NSI_NATIVE",
            "REQUIRES_EXPLICIT_ADJUDICATION",
        }
        if row["verdict"] == "NSI_NATIVE":
            assert row["computing_evidence"], row["path"]
            assert not row["calculus_evidence"], row["path"]


def test_the_criterion_catches_calculus_wherever_it_hides(producer) -> None:
    """Le cas fondateur, reduit a son enonce."""

    body = (
        "\\begin{fichemethode}{M1}{Deriver une fonction composee}\n"
        "Utiliser cette methode lorsque la fonction a deriver fait intervenir\n"
        "une composition : $\\mathrm{e}^{u(x)}$, $\\ln(u(x))$.\n"
    )
    assert producer._evidence(producer.CALCULUS, body)

    # Et il ne se laisse pas desarmer par du vocabulaire informatique autour.
    entoure = body + "\nOn ecrit un algorithme Python avec une boucle sur un tableau.\n"
    assert producer._evidence(producer.CALCULUS, entoure), (
        "l'analyse reste de l'analyse, quel que soit le vocabulaire qui l'entoure"
    )


def test_the_criterion_spares_mathematics_that_are_not_calculus(producer) -> None:
    """FALSE_POSITIVE = 0 : une distance euclidienne reste de la NSI.

    Le critere porte sur le NIVEAU et la DISCIPLINE, pas sur la presence de
    symboles mathematiques. Un exercice de k plus proches voisins calcule une
    distance : il ne releve pas de l'analyse et ne doit pas etre condamne.
    """

    knn = (
        "def distance(a, b):\n"
        "    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5\n"
        "On classe le point par vote majoritaire de ses k plus proches voisins.\n"
    )
    assert not producer._evidence(producer.CALCULUS, knn)
    assert producer._evidence(producer.COMPUTING, knn)


def test_the_verify_block_is_read_as_evidence(producer) -> None:
    """Un bloc SymPy qui derive trahit la discipline aussi surement qu'un enonce."""

    source = (
        "% META: {\"id\": \"X\"}\n"
        "% BEGIN-VERIFY\n"
        "% from sympy import *\n"
        "% fp = diff(x**3 - 3*x**2 + 2, x)\n"
        "% END-VERIFY\n"
        "\\begin{exercice}{X}{1}{10}\nUn enonce anodin.\n\\end{exercice}\n"
    )
    body = producer._payload(source)
    assert "diff(" in body, "le bloc VERIFY doit etre lu"
    assert producer._evidence(producer.CALCULUS, body)


@pytest.mark.parametrize(
    ("source_kind", "body"),
    [
        ("YAML_CONTRACT", "prerequis: Deriver une fonction composee"),
        ("JSON_QCM", '{"erreur": "calculer une limite en +infini"}'),
        ("PYTHON_CODE", "from sympy import diff\nresultat = diff(x**2, x)"),
    ],
)
def test_structured_and_python_sources_cannot_hide_calculus(
    producer, source_kind: str, body: str
) -> None:
    row = producer._surface_row(
        chapter="1NSI-X",
        role="transversal",
        path=Path(f"fixture.{source_kind.lower()}"),
        source_kind=source_kind,
        text=body,
        pointers=["$.fixture"],
    )
    assert row["verdict"] == "CROSS_DISCIPLINE_TERMINALE_MATHS"
    assert row["calculus_evidence"]
    assert row["source_kind"] == source_kind
    assert row["sha256"].startswith("sha256:")
