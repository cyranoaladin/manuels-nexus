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
import yaml

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


def test_prerequisite_in_capacity_field_is_recorded_without_crashing_ledger(
    producer, tmp_path: Path, monkeypatch
) -> None:
    corpus = tmp_path / "chapitres"
    chapter = corpus / "TSPE-X"
    (chapter / "remediation").mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {
                "capacites": [{"code": "C1", "ref_capacite": "REF-C1"}],
                "prerequis": [{"code": "R1"}],
            }
        ),
        encoding="utf-8",
    )
    source = chapter / "remediation/r1.tex"
    source.write_text(
        '% META: {"id":"R1-RE","chapitre":"TSPE-X","type_objet":"remediation","capacites_codes":["R1"]}\nCorps.\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(producer, "CORPORA", (corpus,))
    monkeypatch.setattr(producer, "_RESOLVER", None)

    ledger = producer.build_ledger()

    assert ledger["inventory"]["capacity_identity_blockers"] == 1
    assert ledger["capacity_identity_blockers"][0]["classification"] == (
        "UNRESOLVED_CAPACITY_IDENTITY"
    )
    assert str(source) in ledger["objects_with_indeterminate_credit"]


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

    # Et chaque fiche porte une déclaration résoluble. Le corps ne s'auto-
    # atteste jamais par une occurrence lexicale `C<n>`.
    for path in sorted(directory.glob("*.tex")):
        text = path.read_text(encoding="utf-8")
        declared = set(producer.declared_capacities(producer.read_meta(text)))
        assert declared


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


def _member(
    path,
    chapter,
    declared,
    attested=(),
    manual="1NSI",
    chars=4000,
    source_type="exercices",
    payload_empty=False,
    host_refs=(),
    resolved_host_uid=None,
):
    return {
        "path": path,
        "chapter": chapter,
        "manual": manual,
        "declared_capacity": list(declared),
        "body_attested_capacity": list(attested),
        "payload_chars": chars,
        "source_type": source_type,
        "payload_empty": payload_empty,
        "host_refs": list(host_refs),
        "resolved_host_uid": resolved_host_uid,
    }


def _satellite(name, host, chapter="1SPE-X", manual="1SPE", declared=()):
    """Un satellite sans capacité, rattaché à un hôte de son propre chapitre."""

    return _member(
        f"Mathematiques/manuel-maths/chapitres/{chapter}/exercices/{name}.tex",
        chapter,
        declared,
        manual=manual,
        source_type="exercices",
        host_refs=[host],
        resolved_host_uid=f"{manual}::{chapter}::{host}",
    )


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
    assert checked == len(ledger["groups"])
    assert checked > 0, "le corpus doit etre reellement parcouru"


def test_a_local_c_token_never_proves_the_true_owner(producer) -> None:
    """Même un C4 explicite reste lexical et ne vaut pas provenance."""

    fake = _member("NSI/chapitres/CH/cours/AAA-copie.tex", "CH", ["C9"])
    true = _member("NSI/chapitres/CH/cours/ZZZ-original.tex", "CH", ["C4"], ["C4"])

    for order in ([fake, true], [true, fake]):
        selection = producer.select_canonical(
            _group(order, "CAPACITY_MISREPRESENTING_CLONE")
        )
        assert selection["status"] == "AMBIGUOUS"
        assert selection["evidence_rule"] == "NONE_CONCLUSIVE"
        assert selection["canonical_paths"] == []
        assert selection["false_copy_paths"] == []


def test_authoritative_owner_wins_when_false_path_sorts_first(producer) -> None:
    false = _member(
        "NSI/chapitres/AAA-FAUX/cours/a.tex", "AAA-FAUX", ["C1"]
    )
    true = _member(
        "NSI/chapitres/ZZZ-VRAI/cours/z.tex", "ZZZ-VRAI", ["C4"]
    )
    evidence = {
        "canonical_paths": [true["path"]],
        "authority": {
            "chapter_ownership": "programme map",
            "capacity_alignment": "contract C4",
            "official_programme_alignment": "official atom P-ALGO-04",
            "canonical_assembly": "assembler position 1",
            "source_provenance": "authored source",
            "contract_role": "cours C4",
        },
    }
    for order in ([false, true], [true, false]):
        group = _group(order, "CROSS_CHAPTER_CONTAMINATION")
        group["ownership_evidence"] = evidence
        selection = producer.select_canonical(group)
        assert selection["status"] == "SEMANTIC_CANONICAL"
        assert selection["evidence_rule"] == "AUTHORITATIVE_OWNERSHIP_MAP"
        assert selection["canonical_paths"] == [true["path"]]
        assert selection["false_copy_paths"] == [false["path"]]


def test_chapter_duplication_alone_does_not_prove_the_owner(
    producer,
) -> None:
    """La multiplicité prouve le faux crédit, pas le propriétaire authentique."""

    duplicating = [
        _member("NSI/chapitres/AAA-FAUX/cours/c1.tex", "AAA-FAUX", ["C1"]),
        _member("NSI/chapitres/AAA-FAUX/cours/c4.tex", "AAA-FAUX", ["C4"]),
    ]
    owner = [_member("NSI/chapitres/ZZZ-VRAI/cours/c1.tex", "ZZZ-VRAI", ["C1"])]

    selection = producer.select_canonical(
        _group(duplicating + owner, "CROSS_CHAPTER_CONTAMINATION")
    )
    assert selection["status"] == "AMBIGUOUS"
    assert selection["evidence_rule"] == "NONE_CONCLUSIVE"
    assert selection["canonical_paths"] == []
    assert selection["false_copy_paths"] == []


def test_body_attestation_uses_qualified_identity_across_chapters(producer) -> None:
    """Deux corps disant C1 dans deux chapitres n'attestent pas le même UID."""

    first = _member(
        "NSI/chapitres/1NSI-A/cours/a.tex",
        "1NSI-A",
        ["C1"],
        ["C1"],
    )
    second = _member(
        "NSI/chapitres/1NSI-B/cours/b.tex",
        "1NSI-B",
        ["C1"],
        ["C1"],
    )
    selection = producer.select_canonical(
        _group([first, second], "CROSS_CHAPTER_CONTAMINATION")
    )
    assert selection["status"] == "AMBIGUOUS"
    assert selection["canonical_paths"] == []


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


def test_short_pedagogical_body_is_never_cleared_as_boilerplate(producer) -> None:
    members = [
        _member("CH/exercices/a.tex", "CH", ["C1"], chars=20),
        _member("CH/exercices/b.tex", "CH", ["C2"], chars=20),
    ]
    assert producer.disposition_of(members) == "CAPACITY_MISREPRESENTING_CLONE"
    selection = producer.select_canonical(
        _group(members, producer.disposition_of(members))
    )
    assert selection["status"] == "AMBIGUOUS"


def test_boilerplate_requires_empty_payload_and_no_capacity(producer) -> None:
    empty = [
        _member("A/a.tex", "A", [], chars=0, payload_empty=True),
        _member("B/b.tex", "B", [], chars=0, payload_empty=True),
    ]
    nonempty = [
        _member("A/a.tex", "A", [], chars=1, payload_empty=False),
        _member("B/b.tex", "B", [], chars=1, payload_empty=False),
    ]
    assert producer.disposition_of(empty) == "BOILERPLATE_ONLY"
    assert producer.disposition_of(nonempty) == "CROSS_CHAPTER_CONTAMINATION"


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


def test_every_member_has_an_explicit_canonical_status(ledger: dict) -> None:
    allowed = {
        "SEMANTIC_CANONICAL",
        "FALSE_COPY",
        "LEGITIMATE_SHARED_CANONICAL",
        "AMBIGUOUS",
        "UNKNOWN",
    }
    for group in ledger["groups"]:
        statuses = [member["canonical_object_status"] for member in group["members"]]
        assert len(statuses) == group["object_count"]
        assert set(statuses) <= allowed
        selection = group["canonical_selection"]
        if selection["status"] == "SEMANTIC_CANONICAL":
            assert statuses.count("FALSE_COPY") == len(selection["false_copy_paths"])
        elif selection["status"] == "AMBIGUOUS":
            assert set(statuses) == {"AMBIGUOUS"}


def test_unknown_and_unattributed_excess_are_derived(ledger: dict) -> None:
    assert ledger["unknown"] == ledger["inventory"]["unknown_canonical_groups"]
    ambiguous_excess = sum(
        group["excess_object_count"]
        for group in ledger["groups"]
        if group["canonical_selection"]["status"] == "AMBIGUOUS"
    )
    assert ledger["unattributed_excess_objects"] == ambiguous_excess


def test_same_capacity_is_a_fully_qualified_identity(ledger: dict) -> None:
    for group in ledger["groups"]:
        if group["same_capacity"]:
            assert len(
                {
                    uid
                    for member in group["members"]
                    for uid in member["declared_capacity_uids"]
                }
            ) <= 1


def test_unknown_chapter_capacity_declaration_fails_closed(producer) -> None:
    with pytest.raises(Exception, match="chapitre"):
        producer.declared_capacities(
            {"chapitre": "ALIEN-X", "capacites_codes": ["C1"]}
        )


def producer_statuses():
    return (
        "SEMANTIC_CANONICAL",
        "LEGITIMATE_SHARED_CANONICAL",
        "AMBIGUOUS",
        "UNKNOWN",
    )


def test_identical_capacity_never_clears_a_cross_chapter_group(producer) -> None:
    """`C1` d'un chapitre n'est pas `C1` d'un autre.

    La regle « tous creditent la meme capacite, donc la duplication est
    physique » comparait les codes LOCAUX. Elle blanchissait ainsi une fiche
    methode de mathematiques de Terminale logee dans un chapitre de NSI de
    Premiere, au motif que les deux portaient un `C1` -- alors que ces deux
    `C1` designent des capacites sans aucun rapport.

    C'etait la meme erreur d'identite que le resolveur repare, commise dans
    le code qui devait s'en garder.
    """

    maths = _member(
        "Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/methodes/m.tex",
        "TSPE-DERIVATION-CONVEXITE",
        ["C1"],
        manual="TSPE",
    )
    nsi = _member(
        "NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/methodes/m.tex",
        "1NSI-ALGO-PARCOURS-TRIS",
        ["C1"],
        manual="1NSI",
    )

    selection = producer.select_canonical(
        _group([maths, nsi], "CROSS_MANUAL_CONTAMINATION")
    )
    assert selection["status"] == "AMBIGUOUS", (
        "deux capacites homonymes de manuels differents ne sont pas la meme "
        "capacite : le groupe ne peut pas etre blanchi"
    )
    assert selection["evidence_rule"] != "IDENTICAL_CAPACITY_CREDIT"

    # Même dans un chapitre, un UID commun ne prouve ni le rôle contractuel
    # ni la provenance : sans preuve supplémentaire, on ne blanchit rien.
    same = [
        _member("NSI/chapitres/CH/exercices/a.tex", "CH", ["C1"]),
        _member("NSI/chapitres/CH/exercices/b.tex", "CH", ["C1"]),
    ]
    within = producer.select_canonical(_group(same, "REDUNDANT_SAME_CAPACITY"))
    assert within["status"] == "AMBIGUOUS"
    assert within["evidence_rule"] == "NONE_CONCLUSIVE"


def test_no_cross_chapter_group_is_cleared_as_identical_capacity(ledger: dict) -> None:
    """Le controle sur le corpus reel."""

    for group in ledger["groups"]:
        if group["canonical_selection"]["evidence_rule"] != "IDENTICAL_CAPACITY_CREDIT":
            continue
        chapters = {row["chapter"] for row in group["members"]}
        assert len(chapters) == 1, (
            f"{group['clone_group_id']} blanchi alors qu'il traverse {chapters}"
        )


def test_same_uid_across_contract_roles_is_not_legitimate_sharing(producer) -> None:
    course = _member(
        "NSI/chapitres/1NSI-X/cours/c.tex",
        "1NSI-X",
        ["C1"],
        ["C1"],
        source_type="cours",
    )
    remediation = _member(
        "NSI/chapitres/1NSI-X/remediation/r.tex",
        "1NSI-X",
        ["C1"],
        ["C1"],
        source_type="remediation",
    )
    selection = producer.select_canonical(
        _group([course, remediation], "REDUNDANT_SAME_CAPACITY")
    )
    assert selection["status"] == "AMBIGUOUS"
    assert selection["canonical_paths"] == []


def test_body_tokens_never_create_invalid_capacity_credit(producer) -> None:
    """Une variable C2 ou un renvoi C3 ne dément jamais le META à elle seule."""

    false_positive = {
        "Mathematiques/manuel-maths/chapitres/TEXP-COMPLEXES-TRIGO-POLYNOMES/methodes/TEXP-CTP-ME-006.tex",
        "Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/cours/10_C1_formes_trinome.tex",
        "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/12_C3_suites_geometriques.tex",
    }
    ledger = producer.build_ledger()
    assert false_positive.isdisjoint(ledger["objects_on_invalid_credit"])
    assert all(
        "body_attested_capacity" not in member
        for group in ledger["groups"]
        for member in group["members"]
    )
    assert all(
        group["canonical_selection"]["evidence_rule"] != "BODY_SELF_ATTESTATION"
        for group in ledger["groups"]
    )


# -- Satellites a hotes distincts --------------------------------------------
#
# Un `coup de pouce` ne declare aucune capacite et ne vaut que par l'exercice
# qu'il assiste. Quand plusieurs d'entre eux partagent un corps mais assistent
# chacun un exercice DIFFERENT et REEL de leur propre chapitre, aucun ne peut
# usurper le credit d'un autre -- il n'y a aucun credit en jeu -- et en retirer
# un priverait un exercice reel de son assistance. C'est un partage legitime,
# pas une fausse copie. La regle ne nomme aucun objet : elle constate ces trois
# proprietes sur TOUS les membres, et rien d'autre ne la declenche.


def test_satellites_with_distinct_hosts_are_legitimately_shared(producer) -> None:
    members = [
        _satellite("EX-001-CDP", "EX-001"),
        _satellite("EX-002-CDP", "EX-002"),
        _satellite("EX-003-CDP", "EX-003"),
    ]
    for order in (members, list(reversed(members))):
        selection = producer.select_canonical(
            _group(order, "REDUNDANT_SAME_CAPACITY")
        )
        assert selection["status"] == "LEGITIMATE_SHARED_CANONICAL"
        assert selection["evidence_rule"] == "SATELLITE_WITH_DISTINCT_HOST"
        assert selection["canonical_paths"] == sorted(r["path"] for r in members)
        assert selection["false_copy_paths"] == []


def test_two_satellites_on_the_same_host_are_not_cleared(producer) -> None:
    """MUTATION 1 -- deux assistances pour un seul hote : vraie duplication."""

    members = [
        _satellite("EX-001-CDP", "EX-001"),
        _satellite("EX-001-CDP-bis", "EX-001"),
    ]
    selection = producer.select_canonical(_group(members, "REDUNDANT_SAME_CAPACITY"))
    assert selection["status"] == "AMBIGUOUS"
    assert selection["evidence_rule"] == "NONE_CONCLUSIVE"
    assert selection["canonical_paths"] == []


def test_a_satellite_that_declares_a_capacity_is_not_cleared(producer) -> None:
    """MUTATION 2 -- des qu'une capacite est creditee, un credit est en jeu."""

    members = [
        _satellite("EX-001-CDP", "EX-001"),
        _satellite("EX-002-CDP", "EX-002", declared=["C1"]),
    ]
    selection = producer.select_canonical(_group(members, "REDUNDANT_SAME_CAPACITY"))
    assert selection["status"] == "AMBIGUOUS"
    assert selection["evidence_rule"] == "NONE_CONCLUSIVE"
    assert selection["canonical_paths"] == []


def test_a_satellite_whose_host_is_absent_or_foreign_is_not_cleared(
    producer,
) -> None:
    """MUTATION 3 -- un hote inexistant, ou d'un autre chapitre, ne prouve rien."""

    absent = _satellite("EX-002-CDP", "EX-002")
    absent["resolved_host_uid"] = None
    missing_host = [_satellite("EX-001-CDP", "EX-001"), absent]
    selection = producer.select_canonical(
        _group(missing_host, "REDUNDANT_SAME_CAPACITY")
    )
    assert selection["status"] == "AMBIGUOUS"
    assert selection["canonical_paths"] == []

    foreign = _satellite("EX-002-CDP", "EX-002")
    foreign["resolved_host_uid"] = "1SPE::1SPE-AUTRE-CHAPITRE::EX-002"
    other_chapter = [_satellite("EX-001-CDP", "EX-001"), foreign]
    selection = producer.select_canonical(
        _group(other_chapter, "REDUNDANT_SAME_CAPACITY")
    )
    assert selection["status"] == "AMBIGUOUS"
    assert selection["canonical_paths"] == []


def test_a_satellite_without_any_host_reference_is_not_cleared(producer) -> None:
    """MUTATION 4 -- zero reference, ou deux, ne designent pas un hote unique."""

    orphan = _satellite("EX-002-CDP", "EX-002")
    orphan["host_refs"] = []
    orphan["resolved_host_uid"] = None
    selection = producer.select_canonical(
        _group([_satellite("EX-001-CDP", "EX-001"), orphan], "REDUNDANT_SAME_CAPACITY")
    )
    assert selection["status"] == "AMBIGUOUS"
    assert selection["canonical_paths"] == []

    ambivalent = _satellite("EX-002-CDP", "EX-002")
    ambivalent["host_refs"] = ["EX-002", "EX-003"]
    selection = producer.select_canonical(
        _group(
            [_satellite("EX-001-CDP", "EX-001"), ambivalent],
            "REDUNDANT_SAME_CAPACITY",
        )
    )
    assert selection["status"] == "AMBIGUOUS"
    assert selection["canonical_paths"] == []


def test_every_member_carries_its_host_link_from_the_scan(producer) -> None:
    """Le lien d'hote est materialise par `scan()`, jamais relu dans la regle."""

    records, _ = producer.scan()
    assert records
    for row in records:
        assert isinstance(row["host_refs"], list)
        assert all(isinstance(ref, str) and ref for ref in row["host_refs"])
        uid = row["resolved_host_uid"]
        assert uid is None or isinstance(uid, str)
        if uid is not None:
            assert len(row["host_refs"]) == 1
            assert uid == f"{row['manual']}::{row['chapter']}::{row['host_refs'][0]}"


def test_the_satellite_rule_clears_exactly_what_it_claims_on_the_corpus(
    ledger: dict,
) -> None:
    """Portee reelle : la regle blanchit tous les groupes qui la remplissent,
    et uniquement ceux-la. Les premisses sont ici recalculees membre a membre
    depuis le registre, sans jamais nommer un groupe ni un chapitre.
    """

    cleared = set()
    expected = set()
    for group in ledger["groups"]:
        selection = group["canonical_selection"]
        if selection["evidence_rule"] == "SATELLITE_WITH_DISTINCT_HOST":
            cleared.add(group["clone_group_id"])
            assert selection["status"] == "LEGITIMATE_SHARED_CANONICAL"
            assert selection["false_copy_paths"] == []
            assert selection["canonical_paths"] == sorted(
                row["path"] for row in group["members"]
            )
        if group["disposition"] == "BOILERPLATE_ONLY":
            continue
        hosts = [row["resolved_host_uid"] for row in group["members"]]
        holds = (
            not any(row["declared_capacity"] for row in group["members"])
            and all(len(row["host_refs"]) == 1 for row in group["members"])
            and all(host is not None for host in hosts)
            and len(set(hosts)) == len(hosts)
        )
        if holds:
            expected.add(group["clone_group_id"])

    assert cleared == expected
    assert cleared, "la regle doit etre observable sur le corpus"


def test_the_founding_case_and_hostless_sheets_stay_untouched(ledger: dict) -> None:
    """La regle reste inerte la ou aucun hote n'est designe.

    Deux temoins : les fiches `methode` recopiees d'un chapitre NSI a l'autre,
    qui ne referencent aucun exercice, et le cas fondateur du P0 -- les fiches
    de remediation de `TSPE-GEOMETRIE-ESPACE`, qui declarent des capacites.
    """

    for group in ledger["groups"]:
        rule = group["canonical_selection"]["evidence_rule"]
        members = group["members"]
        if any(row["declared_capacity"] for row in members):
            assert rule != "SATELLITE_WITH_DISTINCT_HOST", group["clone_group_id"]
        if all(not row["host_refs"] for row in members):
            assert rule != "SATELLITE_WITH_DISTINCT_HOST", group["clone_group_id"]
