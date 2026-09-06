"""La couverture pedagogique se mesure sur les corps, jamais sur les META.

Le P0 de clonage a montre ce qu'un compteur naif credite : dix-sept fiches
identiques declarees C1 a C16 creditaient seize capacites alors qu'une seule,
C7, etait traitee. Ce producteur retire les credits invalides avant de
compter.

Ces tests protegent surtout la mesure elle-meme contre deux erreurs qui
FABRIQUENT des lacunes inexistantes -- et une lacune inventee coute aussi cher
qu'une lacune ignoree : elle envoie reecrire du contenu qui va tres bien.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "audit/TRUE_PEDAGOGICAL_COVERAGE.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "true_coverage", ROOT / "scripts/build_true_pedagogical_coverage.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(COVERAGE.read_text(encoding="utf-8"))


def test_the_committed_coverage_matches_the_producer(producer) -> None:
    assert producer.main(["--check"]) == 0


def test_the_backlog_is_exact_and_counted_in_authoring_units(payload: dict) -> None:
    inventory = payload["inventory"]
    backlog = payload["authoring_backlog"]

    assert len(backlog) == inventory["authoring_units_required"]
    # Trois etats, pas deux : une cellule servie uniquement par des clones
    # dont le proprietaire n'est pas demontrable n'est ni pourvue ni vide.
    # La compter comme vide enverrait reecrire un contenu qui existe ; la
    # compter comme pourvue crediterait une capacite au hasard.
    assert (
        inventory["cells_with_declared_exact_identity"]
        + inventory["cells_with_indeterminate_credit"]
        + len(backlog)
        == inventory["cells"]
    )
    assert all(row["valid_objects"] == 0 for row in backlog)
    assert all(row["state"] == "MISSING" for row in backlog)
    # Une unite d'ecriture est un couple (capacite, role), jamais un fichier.
    assert len({(r["chapter"], r["capacity"], r["role"]) for r in backlog}) == len(
        backlog
    )


def test_a_correction_inherits_the_capacity_of_its_exercise(producer) -> None:
    """Sans cet heritage, 1SPE affichait vingt lacunes qui n'existent pas.

    Les corriges de 1SPE ne declarent pas de capacite : ils la tiennent de
    l'exercice qu'ils corrigent, via META.exercice_id. Un compteur qui
    l'ignore condamne un chapitre entier pour un defaut de mesure.
    """

    chapter = ROOT / "Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL"
    clone = producer._clone_module()
    sample = sorted((chapter / "corriges").glob("*.tex"))[0]
    meta = clone.read_meta(sample.read_text(encoding="utf-8"))

    assert not clone.declared_capacities(meta), "ce corrige ne declare pas de capacite"
    exercise_id = meta.get("exercice_id")
    assert exercise_id, "mais il nomme l'exercice dont il herite"

    # L'exercice nomme existe et porte, lui, une capacite : c'est elle que le
    # corrige doit se voir attribuer.
    inherited = None
    for path in (chapter / "exercices").glob("*.tex"):
        other = clone.read_meta(path.read_text(encoding="utf-8"))
        if other.get("id") == exercise_id:
            inherited = clone.declared_capacities(other)
            break
    assert inherited, f"{exercise_id} doit exister et porter une capacite"

    # Et le producteur doit effectivement la lui attribuer.
    covered = {
        (row["chapter"], row["capacity"])
        for row in producer.build_coverage()["authoring_backlog"]
        if row["role"] == "corriges"
    }
    assert (chapter.name, inherited[0]) not in covered, (
        "la capacite heritee ne doit pas etre comptee comme lacune de corrige"
    )


def test_1spe_has_no_core_gap_once_inheritance_is_applied(payload: dict) -> None:
    """L'ajout des évaluations ne doit pas réintroduire les vingt faux gaps."""

    gaps = [row for row in payload["authoring_backlog"] if row["manual"] == "1SPE"]
    assert all(row["role"] not in producer_core_roles() for row in gaps), (
        "les corriges 1SPE doivent heriter de leurs exercices ; une lacune "
        "sur un des cinq roles historiques signalerait le retour du bug"
    )


def producer_core_roles() -> set[str]:
    return {"cours", "methodes", "exercices", "corriges", "remediation"}


def test_qcm_and_assessments_are_part_of_the_collection_wide_matrix(
    payload: dict,
) -> None:
    """Le backlog autoritaire couvre tous les rôles exigés par le contrat."""

    assert payload["measured_roles"] == [
        "cours",
        "methodes",
        "exercices",
        "corriges",
        "remediation",
        "qcm",
        "evaluations",
    ]
    assert "excluded_roles" not in payload
    assert payload["role_sources"]["qcm"] == "question JSON resolue exactement"
    assert payload["role_sources"]["evaluations"] == (
        "META de l'evaluation soumis au ledger de clones"
    )


def test_the_credit_rule_refuses_meta_only_claims(payload: dict, producer) -> None:
    """Aucun objet a credit invalide ne compte dans la couverture."""

    ledger = json.loads(
        (ROOT / "audit/P0_CONTENT_CLONE_LEDGER.json").read_text(encoding="utf-8")
    )
    invalid = set(ledger["objects_on_invalid_credit"])
    indeterminate = set(ledger["objects_with_indeterminate_credit"])
    assert "META" in payload["credit_rule"]

    # La regle vaut partout ou des clones subsistent : aucune copie ne
    # conserve le credit d'une capacite qu'elle n'enseigne pas. Ce test
    # n'exige plus la presence du defaut dans un chapitre precis -- il
    # deviendrait faux le jour ou ce chapitre serait repare.
    misrepresenting = [
        group
        for group in ledger["groups"]
        if group["disposition"] == "CAPACITY_MISREPRESENTING_CLONE"
    ]
    for group in misrepresenting:
        # Un corps ne credite jamais plus d'une capacite. Les membres d'un
        # groupe sans proprietaire demontrable ne creditent rien du tout :
        # ils ne sont ni credites ni declares manquants.
        credited = {row["path"] for row in group["members"]} - invalid - indeterminate
        capacities = {
            tuple(row["declared_capacity"])
            for row in group["members"]
            if row["path"] in credited
        }
        # L'invariant porte sur les CAPACITES creditees, pas sur le nombre de
        # fichiers : deux objets attestes par leur corps pour la meme capacite
        # la creditent une fois, pas deux.
        assert len(capacities) <= 1


def _synthetic_corpus(tmp_path: Path) -> tuple[Path, Path]:
    corpus = tmp_path / "chapitres"
    chapter = corpus / "TSPE-X"
    chapter.mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {"capacites": [{"code": "C1", "ref_capacite": "TSPE-X-C1"}]}
        ),
        encoding="utf-8",
    )
    return corpus, chapter


def _add_capacity(chapter: Path, code: str) -> None:
    contract_path = chapter / "contrat.yaml"
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    contract["capacites"].append(
        {"code": code, "ref_capacite": f"{chapter.name}-{code}"}
    )
    contract_path.write_text(yaml.safe_dump(contract), encoding="utf-8")


def _source(path: Path, meta: dict) -> Path:
    defaults = {
        "cours": "cours",
        "methodes": "methode",
        "exercices": "exercice",
        "corriges": "corrige",
        "remediation": "remediation",
        "evaluations": "evaluation",
    }
    meta = {"type_objet": defaults.get(path.parent.name), **meta}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("% META: " + json.dumps(meta) + "\nContenu.\n", encoding="utf-8")
    return path


def _empty_clone_ledger(**updates) -> dict:
    payload = {
        "objects_on_invalid_credit": [],
        "objects_with_indeterminate_credit": [],
    }
    payload.update(updates)
    return payload


def test_duplicate_object_id_fails_closed(producer, tmp_path: Path) -> None:
    corpus, chapter = _synthetic_corpus(tmp_path)
    first = _source(
        chapter / "cours/a.tex",
        {"id": "DUP", "chapitre": "TSPE-X", "capacites_codes": ["C1"]},
    )
    second = _source(
        chapter / "exercices/b.tex",
        {"id": "DUP", "chapitre": "TSPE-X", "capacites_codes": ["C1"]},
    )
    identity = producer._resolver_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))

    with pytest.raises(producer.CoverageError, match="identifiant objet duplique"):
        producer.build_coverage(
            resolver=resolver,
            clone_ledger=_empty_clone_ledger(),
            corpora=(corpus,),
            source_paths=[first, second],
        )


def test_contradictory_capacity_fields_are_ambiguous_not_unresolved(
    producer, tmp_path: Path
) -> None:
    corpus, chapter = _synthetic_corpus(tmp_path)
    _add_capacity(chapter, "C2")
    source = _source(
        chapter / "cours/a.tex",
        {
            "id": "A",
            "chapitre": chapter.name,
            "capacites_codes": ["C1"],
            "capacites": [f"{chapter.name}-C2"],
        },
    )
    identity = producer._resolver_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))
    payload = producer.build_coverage(
        resolver=resolver,
        clone_ledger=_empty_clone_ledger(),
        corpora=(corpus,),
        source_paths=[source],
        qcm_paths=[],
    )
    assert payload["capacity_identity_resolution"] == {
        "ambiguous": 1,
        "unresolved": 0,
        "unknown": 0,
    }
    assert payload["capacity_identity_blockers"][0]["classification"] == (
        "AMBIGUOUS_CAPACITY_IDENTITY"
    )


def test_correction_never_inherits_valid_credit_from_invalid_exercise(
    producer, tmp_path: Path
) -> None:
    corpus, chapter = _synthetic_corpus(tmp_path)
    exercise = _source(
        chapter / "exercices/ex.tex",
        {"id": "EX", "chapitre": "TSPE-X", "capacites_codes": ["C1"]},
    )
    correction = _source(
        chapter / "corriges/co.tex",
        {"id": "CO", "chapitre": "TSPE-X", "exercice_id": "EX"},
    )
    identity = producer._resolver_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))
    ledger = _empty_clone_ledger(
        objects_on_invalid_credit=[str(exercise)],
    )

    payload = producer.build_coverage(
        resolver=resolver,
        clone_ledger=ledger,
        corpora=(corpus,),
        source_paths=[exercise, correction],
    )
    cell = next(
        row
        for row in payload["rows"]
        if row["capacity"] == "C1" and row["role"] == "corriges"
    )
    assert cell["state"] == "MISSING"
    assert cell["valid_object_ids"] == []


def test_correction_with_invalid_declared_capacity_never_inherits_credit(
    producer, tmp_path: Path
) -> None:
    corpus, chapter = _synthetic_corpus(tmp_path)
    exercise = _source(
        chapter / "exercices/ex.tex",
        {"id": "EX", "chapitre": chapter.name, "capacites_codes": ["C1"]},
    )
    correction = _source(
        chapter / "corriges/co.tex",
        {
            "id": "CO",
            "chapitre": chapter.name,
            "capacites_codes": ["BOGUS"],
            "exercice_id": "EX",
        },
    )
    identity = producer._resolver_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))

    payload = producer.build_coverage(
        resolver=resolver,
        clone_ledger=_empty_clone_ledger(),
        corpora=(corpus,),
        source_paths=[exercise, correction],
        qcm_paths=[],
    )

    cell = next(
        row
        for row in payload["rows"]
        if row["capacity"] == "C1" and row["role"] == "corriges"
    )
    assert cell["state"] == "MISSING"
    assert cell["valid_object_ids"] == []
    assert payload["capacity_identity_resolution"]["unresolved"] == 1
    assert payload["capacity_identity_blockers"][0]["object_id"] == "CO"


def test_correction_inherits_through_authoritative_exercice_ref(
    producer, tmp_path: Path
) -> None:
    corpus, chapter = _synthetic_corpus(tmp_path)
    exercise = _source(
        chapter / "exercices/ex.tex",
        {"id": "EX", "chapitre": "TSPE-X", "capacites_codes": ["C1"]},
    )
    correction = _source(
        chapter / "corriges/co.tex",
        {"id": "CO", "chapitre": "TSPE-X", "exercice_ref": "EX"},
    )
    identity = producer._resolver_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))
    payload = producer.build_coverage(
        resolver=resolver,
        clone_ledger=_empty_clone_ledger(),
        corpora=(corpus,),
        source_paths=[exercise, correction],
        qcm_paths=[],
    )
    cell = next(
        row
        for row in payload["rows"]
        if row["capacity"] == "C1" and row["role"] == "corriges"
    )
    assert cell["state"] == "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED"
    assert cell["valid_object_ids"] == ["CO"]


def test_declared_correction_capacity_must_equal_referenced_exercise(
    producer, tmp_path: Path
) -> None:
    corpus, chapter = _synthetic_corpus(tmp_path)
    _add_capacity(chapter, "C2")
    exercise = _source(
        chapter / "exercices/ex.tex",
        {"id": "EX", "chapitre": chapter.name, "capacites_codes": ["C1"]},
    )
    correction = _source(
        chapter / "corriges/co.tex",
        {
            "id": "CO",
            "chapitre": chapter.name,
            "capacites_codes": ["C2"],
            "exercice_id": "EX",
        },
    )
    identity = producer._resolver_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))

    payload = producer.build_coverage(
        resolver=resolver,
        clone_ledger=_empty_clone_ledger(),
        corpora=(corpus,),
        source_paths=[exercise, correction],
        qcm_paths=[],
    )

    c2 = next(
        row
        for row in payload["rows"]
        if row["capacity"] == "C2" and row["role"] == "corriges"
    )
    assert c2["state"] == "MISSING"
    assert payload["ex_co_relationship_blockers"] == [
        {
            "classification": "MISMATCHED_CAPACITY",
            "correction_id": "CO",
            "correction_path": str(correction),
            "correction_capacities": ["C2"],
            "exercise_id": "EX",
            "exercise_path": str(exercise),
            "exercise_capacities": ["C1"],
        }
    ]


def test_declared_correction_capacity_equal_to_exercise_is_accepted(
    producer, tmp_path: Path
) -> None:
    corpus, chapter = _synthetic_corpus(tmp_path)
    exercise = _source(
        chapter / "exercices/ex.tex",
        {"id": "EX", "chapitre": chapter.name, "capacites_codes": ["C1"]},
    )
    correction = _source(
        chapter / "corriges/co.tex",
        {
            "id": "CO",
            "chapitre": chapter.name,
            "capacites_codes": ["C1"],
            "exercice_ref": "EX",
        },
    )
    identity = producer._resolver_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))
    payload = producer.build_coverage(
        resolver=resolver,
        clone_ledger=_empty_clone_ledger(),
        corpora=(corpus,),
        source_paths=[exercise, correction],
        qcm_paths=[],
    )
    cell = next(
        row
        for row in payload["rows"]
        if row["capacity"] == "C1" and row["role"] == "corriges"
    )
    assert cell["state"] == "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED"
    assert payload["ex_co_relationship_blockers"] == []


def test_correction_reference_target_must_be_an_exercise(
    producer, tmp_path: Path
) -> None:
    corpus, chapter = _synthetic_corpus(tmp_path)
    method = _source(
        chapter / "methodes/me.tex",
        {"id": "NOT-EX", "chapitre": chapter.name, "capacites_codes": ["C1"]},
    )
    correction = _source(
        chapter / "corriges/co.tex",
        {"id": "CO", "chapitre": chapter.name, "exercice_id": "NOT-EX"},
    )
    identity = producer._resolver_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))
    payload = producer.build_coverage(
        resolver=resolver,
        clone_ledger=_empty_clone_ledger(),
        corpora=(corpus,),
        source_paths=[method, correction],
        qcm_paths=[],
    )
    cell = next(
        row
        for row in payload["rows"]
        if row["capacity"] == "C1" and row["role"] == "corriges"
    )
    assert cell["state"] == "MISSING"
    assert payload["ex_co_relationship_blockers"][0]["classification"] == (
        "MISMATCHED_CONTENT"
    )


def test_contradictory_exercise_inheritance_fields_fail_closed(
    producer, tmp_path: Path
) -> None:
    corpus, chapter = _synthetic_corpus(tmp_path)
    exercise = _source(
        chapter / "exercices/ex.tex",
        {"id": "EX", "chapitre": "TSPE-X", "capacites_codes": ["C1"]},
    )
    correction = _source(
        chapter / "corriges/co.tex",
        {
            "id": "CO",
            "chapitre": "TSPE-X",
            "exercice_id": "EX",
            "exercice_ref": "AUTRE",
        },
    )
    identity = producer._resolver_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))
    with pytest.raises(producer.CoverageError, match="heritage contradictoire"):
        producer.build_coverage(
            resolver=resolver,
            clone_ledger=_empty_clone_ledger(),
            corpora=(corpus,),
            source_paths=[exercise, correction],
            qcm_paths=[],
        )


def test_correction_cannot_inherit_from_another_chapter(
    producer, tmp_path: Path
) -> None:
    corpus, chapter_a = _synthetic_corpus(tmp_path)
    chapter_b = corpus / "TSPE-Y"
    chapter_b.mkdir()
    (chapter_b / "contrat.yaml").write_text(
        yaml.safe_dump(
            {"capacites": [{"code": "C1", "ref_capacite": "TSPE-Y-C1"}]}
        ),
        encoding="utf-8",
    )
    exercise = _source(
        chapter_b / "exercices/ex.tex",
        {"id": "EX-B", "chapitre": "TSPE-Y", "capacites_codes": ["C1"]},
    )
    correction = _source(
        chapter_a / "corriges/co.tex",
        {"id": "CO-A", "chapitre": "TSPE-X", "exercice_id": "EX-B"},
    )
    identity = producer._resolver_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))

    with pytest.raises(producer.CoverageError, match="autre chapitre"):
        producer.build_coverage(
            resolver=resolver,
            clone_ledger=_empty_clone_ledger(),
            corpora=(corpus,),
            source_paths=[exercise, correction],
        )


def test_every_coverage_cell_carries_exact_ids_and_digests(payload: dict) -> None:
    for row in payload["rows"]:
        assert len(row["valid_object_ids"]) == row["valid_objects"]
        assert len(row["indeterminate_object_ids"]) == row["indeterminate_objects"]
        assert row["valid_object_ids_digest"].startswith("sha256:")
        assert row["indeterminate_object_ids_digest"].startswith("sha256:")


def test_every_backlog_projection_carries_the_exact_set_and_digest(
    payload: dict, producer
) -> None:
    units = {
        f"{row['chapter']}/{row['capacity']}/{row['role']}"
        for row in payload["authoring_backlog"]
    }
    dimensions = {
        "per_manual": lambda row: row["manual"],
        "per_chapter": lambda row: row["chapter"],
        "per_capacity": lambda row: row["canonical_capacity_uid"],
        "per_role": lambda row: row["role"],
    }
    for dimension, key_of in dimensions.items():
        projection = payload["authoring_backlog_projections"][dimension]
        projected_union: set[str] = set()
        buckets: list[set[str]] = []
        for key, bucket in projection.items():
            expected = {
                f"{row['chapter']}/{row['capacity']}/{row['role']}"
                for row in payload["authoring_backlog"]
                if key_of(row) == key
            }
            assert bucket["count"] == len(expected)
            assert set(bucket["unit_ids"]) == expected
            assert bucket["set_digest"] == producer._set_digest(expected)
            buckets.append(expected)
            projected_union |= expected
        assert projected_union == units
        assert all(
            left.isdisjoint(right)
            for index, left in enumerate(buckets)
            for right in buckets[index + 1 :]
        )
        assert payload["projection_invariants"][dimension] == {
            "pairwise_intersections": 0,
            "union_matches_authoring_backlog": True,
        }


def test_qcm_question_capacity_is_resolved_exactly(producer, tmp_path: Path) -> None:
    corpus, chapter = _synthetic_corpus(tmp_path)
    qcm = chapter / "qcm/TSPE-X-QCM.json"
    qcm.parent.mkdir(parents=True)
    qcm.write_text(
        json.dumps(
            {
                "chapitre": "TSPE-X",
                "questions": [
                    {"id": "Q1", "capacite": "TSPE-X-C1", "options": {}}
                ],
            }
        ),
        encoding="utf-8",
    )
    identity = producer._resolver_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))

    measured = producer.build_coverage(
        resolver=resolver,
        clone_ledger=_empty_clone_ledger(),
        corpora=(corpus,),
        source_paths=[],
        qcm_paths=[qcm],
    )
    cell = next(row for row in measured["rows"] if row["role"] == "qcm")
    assert cell["state"] == "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED"
    assert cell["valid_object_ids"] == ["TSPE-X/TSPE-X-QCM.json#Q1"]


def test_multiple_qcm_sources_never_union_their_capacity_credits(
    producer, tmp_path: Path
) -> None:
    corpus, chapter = _synthetic_corpus(tmp_path)
    paths = []
    for name in ("A-QCM.json", "B-QCM.json"):
        qcm = chapter / "qcm" / name
        qcm.parent.mkdir(parents=True, exist_ok=True)
        qcm.write_text(
            json.dumps(
                {
                    "chapitre": "TSPE-X",
                    "questions": [{"id": "Q1", "capacite": "C1"}],
                }
            ),
            encoding="utf-8",
        )
        paths.append(qcm)
    identity = producer._resolver_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))
    with pytest.raises(producer.CoverageError, match="MULTIPLE_QCM_SOURCES"):
        producer.build_coverage(
            resolver=resolver,
            clone_ledger=_empty_clone_ledger(),
            corpora=(corpus,),
            source_paths=[],
            qcm_paths=paths,
        )


def test_evaluation_credit_is_subject_to_clone_indeterminacy(
    producer, tmp_path: Path
) -> None:
    corpus, chapter = _synthetic_corpus(tmp_path)
    evaluation = _source(
        chapter / "evaluations/ev.tex",
        {
            "id": "EV",
            "chapitre": "TSPE-X",
            "type_objet": "evaluation",
            "capacites": ["TSPE-X-C1"],
        },
    )
    identity = producer._resolver_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))
    measured = producer.build_coverage(
        resolver=resolver,
        clone_ledger=_empty_clone_ledger(
            objects_with_indeterminate_credit=[str(evaluation)]
        ),
        corpora=(corpus,),
        source_paths=[evaluation],
        qcm_paths=[],
    )
    cell = next(row for row in measured["rows"] if row["role"] == "evaluations")
    assert cell["state"] == "INDETERMINATE_CLONE_CREDIT"


def test_an_assessment_correction_alone_never_credits_the_assessment_role(
    producer, tmp_path: Path
) -> None:
    corpus, chapter = _synthetic_corpus(tmp_path)
    correction = _source(
        chapter / "evaluations/ev-corrige.tex",
        {
            "id": "EV-CORRIGE",
            "chapitre": "TSPE-X",
            "type_objet": "corrige_evaluation",
            "capacites": ["TSPE-X-C1"],
        },
    )
    identity = producer._resolver_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))
    measured = producer.build_coverage(
        resolver=resolver,
        clone_ledger=_empty_clone_ledger(),
        corpora=(corpus,),
        source_paths=[correction],
        qcm_paths=[],
    )
    cell = next(row for row in measured["rows"] if row["role"] == "evaluations")
    assert cell["state"] == "MISSING"


def test_hint_inside_exercises_never_credits_the_exercise_role(
    producer, tmp_path: Path
) -> None:
    corpus, chapter = _synthetic_corpus(tmp_path)
    hint = _source(
        chapter / "exercices/hint.tex",
        {
            "id": "HINT",
            "chapitre": "TSPE-X",
            "type_objet": "coup_de_pouce",
            "capacites_codes": ["C1"],
        },
    )
    identity = producer._resolver_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))
    measured = producer.build_coverage(
        resolver=resolver,
        clone_ledger=_empty_clone_ledger(),
        corpora=(corpus,),
        source_paths=[hint],
        qcm_paths=[],
    )
    cell = next(row for row in measured["rows"] if row["role"] == "exercices")
    assert cell["state"] == "MISSING"
    assert measured["role_type_mismatches"] == [
        {
            "path": str(hint),
            "role": "exercices",
            "type_objet": "coup_de_pouce",
        }
    ]


def test_invalid_and_indeterminate_credit_sets_are_disjoint(payload: dict) -> None:
    """OLD : `unresolved: 124`, le nombre d'objets qui declaraient un prerequis
    dans le champ des capacites.
    POURQUOI : ce compte devait rester VISIBLE, pour qu'aucune identite
    irresolue ne se fonde dans le decor.
    NEW : le contrat du resolveur est fail-closed -- une identite est resolue
    exactement, ou elle bloque. Les 124 ont ete rendues a leur namespace, donc
    l'exigence n'est plus « exactement 124 » mais ZERO, et chaque blocker
    restant doit etre nomme un par un.
    POURQUOI PLUS FORT : l'ancien pin tolerait 124 irresolues et cassait si
    elles disparaissaient ; celui-ci n'en tolere aucune."""

    assert payload["invariants"]["invalid_and_indeterminate_disjoint"] is True
    assert payload["capacity_identity_resolution"] == {
        "ambiguous": 0,
        "unresolved": 0,
        "unknown": 0,
    }
    assert payload["capacity_identity_blockers"] == []
