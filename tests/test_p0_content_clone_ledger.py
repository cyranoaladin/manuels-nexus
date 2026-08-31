"""Le clonage pedagogique est mesure, reproductible, et ne peut plus croitre.

P0_PEDAGOGICAL_CONTENT_CLONING_AND_CAPACITY_MISREPRESENTATION.

Des centaines d'objets partagent un corps rigoureusement identique tout en
declarant des capacites differentes. Le cas fondateur : dix-sept fiches de
remediation de TSPE-GEOMETRIE-ESPACE declarees C1 a C16 portaient le meme
corps, celui de C7 -- un eleve en echec sur C1 recevait la fiche C7. Ce
chapitre est desormais repare ; la collection ne l'est pas.

Ces tests fixent la mesure du defaut, la rendent reproductible depuis les
sources, interdisent qu'elle augmente pendant la reecriture, et gardent le
terrain deja assaini. Un test qui affirme la PRESENCE d'un defaut devient faux
le jour ou on le repare : ceux-ci affirment donc des invariants.
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


def test_the_remediation_sheets_of_geoespace_are_all_distinct(producer) -> None:
    """Le cas fondateur du P0, devenu garde de non-retour.

    Ce chapitre declarait dix-sept fiches de remediation et n'en possedait
    qu'une : celle de C7, produit scalaire, recopiee seize fois sous les
    etiquettes C1 a C16. Un eleve en echec sur C1 recevait la fiche C7.

    Ce test affirmait la presence du defaut tant qu'il n'etait pas repare. Les
    seize copies ayant ete retirees, il affirme desormais l'invariant : dans ce
    repertoire, deux fiches ne partagent jamais un corps. L'historique du
    defaut reste au registre et dans l'historique Git.
    """

    directory = (
        ROOT
        / "Mathematiques/manuel-maths/chapitres/TSPE-GEOMETRIE-ESPACE/remediation"
    )
    bodies = collections.defaultdict(list)
    for path in sorted(directory.glob("*.tex")):
        text = path.read_text(encoding="utf-8")
        bodies[producer.digest(producer.pedagogical_body(text))].append(path.name)

    shared = {digest: names for digest, names in bodies.items() if len(names) > 1}
    assert not shared, f"des fiches partagent un corps : {shared}"

    # Et chaque fiche sert bien la capacite qu'elle declare.
    for path in sorted(directory.glob("*.tex")):
        text = path.read_text(encoding="utf-8")
        declared = set(producer.declared_capacities(producer.read_meta(text)))
        attested = set(producer.body_attested_capacities(producer.pedagogical_body(text)))
        if attested:
            assert declared & attested, (
                f"{path.name} declare {sorted(declared)} mais son corps "
                f"annonce {sorted(attested)}"
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


def test_a_clone_group_always_keeps_exactly_one_credited_member(
    ledger: dict, producer
) -> None:
    """Invalider l'original avec ses copies fabriquerait des lacunes.

    Un corps clone credite UNE capacite, pas n : les copies perdent leur
    credit. Mais si AUCUN membre ne se nomme lui-meme -- un enonce
    d'exercice ne cite pas toujours sa capacite -- une regle qui exige une
    auto-mention pour garder le credit n'en garde aucun, et invalide le
    groupe entier.

    Le chapitre paraitrait alors depourvu d'un contenu qu'il possede : les
    cinquante exercices de TSPE-GEOMETRIE-ESPACE etaient comptes tous
    invalides, sept originaux compris, ce qui gonflait le backlog de plus de
    deux cents unites d'ecriture inexistantes.
    """

    invalid = set(ledger["objects_on_invalid_credit"])
    for group in ledger["groups"]:
        if group["disposition"] in {"BOILERPLATE_ONLY", "REDUNDANT_SAME_CAPACITY"}:
            continue
        kept = {row["path"] for row in group["members"]} - invalid
        assert len(kept) <= 1, (
            f"{group['clone_group_id']} conserve {len(kept)} credits pour un "
            "seul corps"
        )
        if not kept:
            # Le groupe ne perd la totalite de ses credits que si CHAQUE
            # membre est, independamment, dementi par son propre corps.
            contradicted = [
                row
                for row in group["members"]
                if row["body_attested_capacity"]
                and not set(row["declared_capacity"])
                & set(row["body_attested_capacity"])
            ]
            assert len(contradicted) == group["object_count"], (
                f"{group['clone_group_id']} perd tous ses credits sans que "
                "chaque membre soit dementi par son corps"
            )
        elif group["body_aligned_member_paths"]:
            assert kept == {group["body_aligned_member_paths"][0]}


def test_geoespace_exercises_are_all_distinct_and_paired(producer) -> None:
    """Le chapitre fondateur, une fois reconstruit : plus un seul clone.

    Ce test affirmait qu'au moins un exercice original gardait son credit
    parmi les clones -- il prouvait que la regle de credit ne condamnait pas
    l'original avec ses copies. Les quarante-trois paires clonees ayant ete
    retirees, sa premisse a disparu avec elles.

    Il affirme desormais l'etat atteint : dans ce chapitre, deux exercices ne
    partagent jamais un corps, deux corriges non plus, et chaque corrige
    designe un exercice qui existe.
    """

    chapter = ROOT / "Mathematiques/manuel-maths/chapitres/TSPE-GEOMETRIE-ESPACE"
    for role in ("exercices", "corriges"):
        bodies = collections.defaultdict(list)
        for path in sorted((chapter / role).glob("*.tex")):
            text = path.read_text(encoding="utf-8")
            bodies[producer.digest(producer.pedagogical_body(text))].append(path.name)
        shared = {d: names for d, names in bodies.items() if len(names) > 1}
        assert not shared, f"{role} : des objets partagent un corps : {shared}"

    exercises = {
        producer.read_meta(p.read_text(encoding="utf-8"))["id"]
        for p in (chapter / "exercices").glob("*.tex")
    }
    corrections = [
        producer.read_meta(p.read_text(encoding="utf-8"))
        for p in (chapter / "corriges").glob("*.tex")
    ]
    assert exercises, "le chapitre doit porter des exercices"
    assert len(corrections) == len(exercises)
    for meta in corrections:
        assert meta["exercice_ref"] in exercises, (
            f"{meta['id']} designe un exercice inexistant"
        )
