"""Le clonage pedagogique est mesure, reproductible, et ne peut plus croitre.

P0_PEDAGOGICAL_CONTENT_CLONING_AND_CAPACITY_MISREPRESENTATION.

Des centaines d'objets partagent un corps rigoureusement identique tout en
declarant des capacites differentes. Dix-sept fiches de remediation de
TSPE-GEOMETRIE-ESPACE declarees C1 a C16 portent le meme corps, dont l'en-tete
annonce « FICHE DE REMEDIATION -- C7 : produit scalaire » : un eleve en echec
sur C1 recevait la fiche C7.

Ces tests ne pretendent pas que le defaut est repare -- il ne l'est pas. Ils
fixent sa mesure exacte, la rendent reproductible depuis les sources, et
interdisent qu'elle augmente pendant la campagne de reecriture.
"""

from __future__ import annotations

import collections
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "audit/P0_CONTENT_CLONE_LEDGER.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "p0_clone_ledger", ROOT / "scripts/build_p0_content_clone_ledger.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def test_the_committed_ledger_matches_the_producer(producer) -> None:
    """Un registre ecrit a la main derive ; celui-ci se recalcule."""

    assert producer.main(["--check"]) == 0


def test_the_measure_is_exact_and_has_no_unknown(ledger: dict) -> None:
    inventory = ledger["inventory"]
    declared = sum(
        entry["excess_objects"] for entry in ledger["dispositions"].values()
    )

    assert ledger["unknown"] == 0
    assert declared == inventory["excess_objects"]
    assert sum(
        entry["groups"] for entry in ledger["dispositions"].values()
    ) == inventory["clone_groups"]
    assert inventory["objects_scanned"] > inventory["distinct_bodies"]


def test_every_group_names_its_members_and_its_excess(ledger: dict) -> None:
    for group in ledger["groups"]:
        assert group["object_count"] == len(group["members"])
        assert group["excess_object_count"] == group["object_count"] - 1
        assert group["object_count"] > 1
        assert group["disposition"]
        assert len({row["path"] for row in group["members"]}) == group["object_count"]


def test_the_body_definition_keeps_the_pedagogical_content(ledger: dict) -> None:
    """Seule l'identite est retiree : le reste fonde la comparaison."""

    definition = ledger["body_definition"]
    assert definition["excluded"] == [
        "% META: identity line",
        "trailing and edge whitespace",
    ]
    for retained in ("enonce", "code", "solution", "diagnostic", "remediation"):
        assert retained in definition["retained"]


def test_the_seventeen_remediations_declared_c1_to_c16_are_one_body(
    producer,
) -> None:
    """La preuve la plus nette du defaut, verifiee sur les sources."""

    directory = (
        ROOT
        / "Mathematiques/manuel-maths/chapitres/TSPE-GEOMETRIE-ESPACE/remediation"
    )
    bodies = collections.defaultdict(list)
    for path in sorted(directory.glob("*.tex")):
        text = path.read_text(encoding="utf-8")
        bodies[producer.digest(producer.pedagogical_body(text))].append(path)

    shared = max(bodies.values(), key=len)
    assert len(shared) >= 17, "le groupe clone de remediation doit rester mesure"

    declared = set()
    for path in shared:
        meta = producer.read_meta(path.read_text(encoding="utf-8"))
        declared |= set(producer.declared_capacities(meta))
    assert len(declared) >= 16, "ces fiches declarent bien des capacites distinctes"

    body = producer.pedagogical_body(shared[0].read_text(encoding="utf-8"))
    attested = producer.body_attested_capacities(body)
    assert attested == ("C7",), (
        "le corps partage s'annonce lui-meme comme la fiche C7 : les autres "
        "capacites sont revendiquees sans etre servies"
    )


def test_the_clone_population_never_grows(ledger: dict, producer) -> None:
    """Garde anti-regression : la reecriture ne peut que faire baisser.

    Le defaut n'est pas encore referme -- la campagne de reconstruction est en
    cours. Ce garde interdit seulement qu'un nouveau clone s'ajoute : le
    registre committe est l'etat declare, et l'observe ne doit jamais le
    depasser.
    """

    observed = producer.build_ledger()["inventory"]
    declared = ledger["inventory"]

    assert observed["excess_objects"] <= declared["excess_objects"], (
        "un clone pedagogique a ete introduit : "
        f"{observed['excess_objects']} > {declared['excess_objects']}"
    )
    assert observed["clone_groups"] <= declared["clone_groups"]
    assert (
        observed["objects_on_invalid_credit"]
        <= declared["objects_on_invalid_credit"]
    )
