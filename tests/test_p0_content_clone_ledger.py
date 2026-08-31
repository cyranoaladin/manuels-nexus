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
import random
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


def test_a_clone_group_never_yields_more_than_one_credit(
    ledger: dict, producer
) -> None:
    """Un corps credite au plus UNE capacite, et jamais par tirage au sort.

    Ce test exigeait autrefois qu'exactement un membre garde le credit. Il
    supposait donc qu'un canonique puisse toujours etre designe -- ce qui
    n'est vrai que si l'on accepte de le choisir par ordre alphabetique.

    Depuis que la selection se fait par preuve, un groupe sans preuve n'a
    pas de canonique : ses membres ne creditent rien et partent en revue.
    L'invariant qui reste est le bon : le nombre de CREDITS accordes a un
    corps clone ne depasse jamais un.
    """

    invalid = set(ledger["objects_on_invalid_credit"])
    indeterminate = set(ledger["objects_with_indeterminate_credit"])
    assert invalid.isdisjoint(indeterminate)

    for group in ledger["groups"]:
        selection = group["canonical_selection"]
        members = {row["path"] for row in group["members"]}
        credited = members - invalid - indeterminate

        if selection["status"] == "AMBIGUOUS":
            assert credited == set(), (
                f"{group['clone_group_id']} credite sans preuve de proprietaire"
            )
            continue
        if selection["status"] == "LEGITIMATE_SHARED_CANONICAL":
            # Tous creditent la meme capacite : le total des credits reste un.
            declared = {tuple(r["declared_capacity"]) for r in group["members"]}
            assert len(declared) == 1 or group["disposition"] == "BOILERPLATE_ONLY"
            continue

        assert selection["status"] == "SEMANTIC_CANONICAL"
        assert credited == set(selection["canonical_paths"])
        capacities = {
            tuple(row["declared_capacity"])
            for row in group["members"]
            if row["path"] in credited
        }
        assert len(capacities) == 1, (
            f"{group['clone_group_id']} credite {len(capacities)} capacites "
            "distinctes pour un seul corps"
        )


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


# -- Le canonique ne peut pas dependre de l'ordre des chemins ----------------


def _member(path, chapter, declared, attested=(), manual="1NSI", chars=4000):
    return {
        "path": path,
        "chapter": chapter,
        "manual": manual,
        "declared_capacity": list(declared),
        "body_attested_capacity": list(attested),
        "payload_chars": chars,
    }


def _group(members, disposition):
    return {"members": list(members), "disposition": disposition}


def test_canonical_selection_is_invariant_under_path_permutation(producer) -> None:
    """La preuve decide, pas l'ordre du systeme de fichiers.

    L'ancienne regle retenait `members[0]`, le premier chemin par ordre
    alphabetique. Dans le groupe des cours 1NSI elle tombait juste par
    chance : le fichier authentique s'appelait `1NSI-ADGK-...` et triait
    avant ses copies `1NSI-ALGO-PARCOURS-TRIS-...`. Un simple renommage
    aurait deplace l'authenticite d'un chapitre a l'autre.
    """

    ledger = producer.build_ledger()
    checked = 0
    for group in ledger["groups"]:
        reference = group["canonical_selection"]
        for seed in (1, 2, 3):
            shuffled = list(group["members"])
            random.Random(seed).shuffle(shuffled)
            permuted = producer.select_canonical(
                {"members": shuffled, "disposition": group["disposition"]}
            )
            assert permuted == reference, group["clone_group_id"]
        checked += 1
    assert checked > 300, "le corpus doit etre reellement parcouru"


def test_the_true_owner_wins_even_when_the_copy_sorts_first(producer) -> None:
    """La fixture qui aurait pris l'ancienne regle en defaut.

    Le faux fichier est nomme pour trier AVANT le vrai. Seul le vrai est
    atteste par son corps. L'ancienne regle, en l'absence d'attestation,
    aurait retenu le premier chemin ; ici l'attestation tranche, et elle
    doit gagner quel que soit le nom.
    """

    fake = _member("NSI/chapitres/CH/cours/AAA-copie.tex", "CH", ["C9"])
    true = _member("NSI/chapitres/CH/cours/ZZZ-original.tex", "CH", ["C4"], ["C4"])

    for order in ([fake, true], [true, fake]):
        selection = producer.select_canonical(
            _group(order, "CAPACITY_MISREPRESENTING_CLONE")
        )
        assert selection["status"] == "SEMANTIC_CANONICAL"
        assert selection["evidence_rule"] == "BODY_SELF_ATTESTATION"
        assert selection["canonical_paths"] == [
            "NSI/chapitres/CH/cours/ZZZ-original.tex"
        ]
        assert selection["false_copy_paths"] == [
            "NSI/chapitres/CH/cours/AAA-copie.tex"
        ]


def test_a_chapter_that_duplicates_a_body_loses_it_to_the_one_that_does_not(
    producer,
) -> None:
    """Le cas 1NSI reel, reduit et avec les noms inverses.

    Un chapitre qui detient le meme corps sous DEUX capacites distinctes le
    represente faussement : un seul corps ne sert pas deux capacites. Le
    chapitre qui le detient une seule fois en est le proprietaire -- meme
    quand ses chemins trient en dernier.
    """

    duplicating = [
        _member("NSI/chapitres/AAA-FAUX/cours/c1.tex", "AAA-FAUX", ["C1"]),
        _member("NSI/chapitres/AAA-FAUX/cours/c4.tex", "AAA-FAUX", ["C4"]),
    ]
    owner = [_member("NSI/chapitres/ZZZ-VRAI/cours/c1.tex", "ZZZ-VRAI", ["C1"])]

    selection = producer.select_canonical(
        _group(duplicating + owner, "CROSS_CHAPTER_CONTAMINATION")
    )
    assert selection["status"] == "SEMANTIC_CANONICAL"
    assert selection["evidence_rule"] == "CHAPTER_SELF_DUPLICATION"
    assert selection["canonical_paths"] == ["NSI/chapitres/ZZZ-VRAI/cours/c1.tex"]
    assert len(selection["false_copy_paths"]) == 2


def test_without_evidence_the_selection_refuses_to_choose(producer) -> None:
    """Pas de tirage au sort deguise en resultat."""

    members = [
        _member("NSI/chapitres/CH/exercices/a.tex", "CH", ["C1"]),
        _member("NSI/chapitres/CH/exercices/b.tex", "CH", ["C2"]),
    ]
    selection = producer.select_canonical(
        _group(members, "CAPACITY_MISREPRESENTING_CLONE")
    )
    assert selection["status"] == "AMBIGUOUS"
    assert selection["canonical_paths"] == []
    assert selection["false_copy_paths"] == []


def test_no_group_is_ever_left_unknown(ledger: dict) -> None:
    """UNKNOWN = 0 : tout groupe recoit un statut explicite."""

    counts = ledger["canonical_selection_counts"]
    assert counts["UNKNOWN"] == 0
    assert sum(counts.values()) == ledger["inventory"]["clone_groups"]
    for group in ledger["groups"]:
        selection = group["canonical_selection"]
        assert selection["status"] in set(producer_statuses())
        assert selection["reason"]
        if selection["status"] == "AMBIGUOUS":
            assert not selection["canonical_paths"]


def producer_statuses():
    return (
        "SEMANTIC_CANONICAL",
        "LEGITIMATE_SHARED_CANONICAL",
        "AMBIGUOUS",
        "UNKNOWN",
    )
