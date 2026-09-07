"""La matrice de publication consomme la vérité capacité/clones courante."""

from __future__ import annotations

import importlib.util
import hashlib
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "publish_readiness_matrix",
        ROOT / "scripts/build_publish_readiness_chapter_matrix.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _fixtures(producer):
    invalid: list[str] = []
    indeterminate: list[str] = []
    clone = {
        "objects_on_invalid_credit": invalid,
        "objects_with_indeterminate_credit": indeterminate,
        "groups": [],
    }
    coverage = {
        "capacity_identity_resolution": {"ambiguous": 0, "unresolved": 0, "unknown": 0},
        "invalid_credit_paths_digest": producer._set_digest(invalid),
        "indeterminate_credit_paths_digest": producer._set_digest(indeterminate),
        "rows": [
            {
                "manual": "1NSI",
                "chapter": "1NSI-X",
                "capacity": "C1",
                "canonical_capacity_uid": "1NSI::1NSI-X::C1",
                "role": "cours",
                "state": "SEMANTICALLY_VALIDATED_CONTENT",
            }
        ],
    }
    return coverage, clone


def test_clean_capacity_truth_is_complete(producer) -> None:
    coverage, clone = _fixtures(producer)
    truth = producer._capacity_truth("1NSI-X", coverage, clone)
    assert truth["capacity_identity"]["status"] == "COMPLETE"
    assert truth["pedagogical_role_coverage"]["status"] == "COMPLETE"
    assert truth["clone_capacity_integrity"]["status"] == "COMPLETE"


@pytest.mark.parametrize(
    ("state", "expected_missing", "expected_indeterminate"),
    [
        ("MISSING", 1, 0),
        ("INDETERMINATE_CLONE_CREDIT", 0, 1),
        ("DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED", 0, 0),
    ],
)
def test_missing_or_indeterminate_capacity_role_blocks_machine_complete(
    producer, state, expected_missing, expected_indeterminate
) -> None:
    coverage, clone = _fixtures(producer)
    coverage["rows"][0]["state"] = state
    truth = producer._capacity_truth("1NSI-X", coverage, clone)
    role = truth["pedagogical_role_coverage"]
    assert role["status"] == "GAP"
    assert role["missing"] == expected_missing
    assert role["indeterminate"] == expected_indeterminate
    if state == "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED":
        assert role["semantically_unvalidated"] == 1


def test_false_copy_or_ambiguous_group_blocks_clone_integrity(producer) -> None:
    coverage, clone = _fixtures(producer)
    clone["objects_on_invalid_credit"] = ["NSI/chapitres/1NSI-X/cours/faux.tex"]
    coverage["invalid_credit_paths_digest"] = producer._set_digest(
        clone["objects_on_invalid_credit"]
    )
    clone["groups"] = [
        {
            "clone_group_id": "CG-X",
            "canonical_selection": {"status": "AMBIGUOUS"},
            "members": [
                {
                    "chapter": "1NSI-X",
                    "path": "NSI/chapitres/1NSI-X/cours/faux.tex",
                    "canonical_object_status": "FALSE_COPY",
                }
            ],
        }
    ]
    truth = producer._capacity_truth("1NSI-X", coverage, clone)
    integrity = truth["clone_capacity_integrity"]
    assert integrity["status"] == "GAP"
    assert integrity["false_copy_paths"] == [
        "NSI/chapitres/1NSI-X/cours/faux.tex"
    ]
    assert integrity["ambiguous_group_ids"] == ["CG-X"]


def test_nonzero_identity_unknown_blocks_identity_dimension(producer) -> None:
    coverage, clone = _fixtures(producer)
    coverage["capacity_identity_resolution"]["unknown"] = 1
    truth = producer._capacity_truth("1NSI-X", coverage, clone)
    assert truth["capacity_identity"]["status"] == "GAP"


def test_coverage_and_clone_credit_sets_must_match(producer) -> None:
    coverage, clone = _fixtures(producer)
    coverage["invalid_credit_paths_digest"] = producer._set_digest(["stale.tex"])
    with pytest.raises(producer.ReadinessError, match="invalid_credit"):
        producer._capacity_truth("1NSI-X", coverage, clone)


def test_current_matrix_records_capacity_dimensions_and_input_digests(producer) -> None:
    payload = producer.build_matrix()
    assert payload["input_digests"]["capacity_alias_map"].startswith("sha256:")
    assert payload["input_digests"]["clone_ledger"].startswith("sha256:")
    assert payload["input_digests"]["true_coverage"].startswith("sha256:")
    assert payload["input_digests"]["chapter_richness"].startswith("sha256:")
    assert payload["input_digests"]["human_review_queue"].startswith("sha256:")
    for row in payload["chapters"]:
        assert {
            "capacity_identity",
            "pedagogical_role_coverage",
            "clone_capacity_integrity",
            "pedagogical_richness",
        } <= set(row["machine_dimensions"])
        if any(
            row["machine_dimensions"][key] != "COMPLETE"
            for key in (
                "capacity_identity",
                "pedagogical_role_coverage",
                "clone_capacity_integrity",
            )
        ):
            assert row["vertical_machine_status"] == "INCOMPLETE"


def test_unknown_semantic_richness_blocks_machine_completion(producer) -> None:
    truth = producer._richness_truth(
        "1NSI-X",
        {
            "chapters": {
                "1NSI-X": {
                    "machine_status": "GAP",
                    "semantic_validation_status": "UNKNOWN",
                    "unknown": 1,
                    "insufficient": [],
                    "capacity_identity_blockers": [],
                    "excluded_credit_objects": [],
                    "capacities_digest": "sha256:test",
                }
            }
        },
    )
    assert truth["status"] == "GAP"
    assert truth["unknown"] == 1


def test_risk_score_increases_for_capacity_and_clone_debt(producer) -> None:
    base = {
        "programme": {"status": "COMPLETE", "wrong_year": 0},
        "qcm": {"present": False},
        "diacritics": {"unambiguous": 0},
        "oracle": {"fail": 0},
        "assessments": {"status": "COMPLETE"},
        "human": {"review_a": "PENDING_UNASSIGNED", "review_b": "PENDING_UNASSIGNED"},
        "pedagogical_role_coverage": {"missing": 0, "indeterminate": 0},
        "clone_capacity_integrity": {
            "false_copy_count": 0,
            "ambiguous_groups": 0,
            "unknown_groups": 0,
        },
    }
    clean = producer._risk_score(base)
    base["pedagogical_role_coverage"] = {"missing": 2, "indeterminate": 3}
    base["clone_capacity_integrity"] = {
        "false_copy_count": 1,
        "ambiguous_groups": 1,
        "unknown_groups": 0,
    }
    assert producer._risk_score(base) > clean


def test_qcm_unknown_capacity_fails_closed(producer, tmp_path: Path) -> None:
    corpus = tmp_path / "chapitres"
    chapter = corpus / "1NSI-X"
    (chapter / "qcm").mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {"chapitre": "1NSI-X", "capacites": [{"code": "C1", "ref_capacite": "REF-C1"}]}
        ),
        encoding="utf-8",
    )
    (chapter / "qcm/x-QCM.json").write_text(
        json.dumps(
            {
                "chapitre": "1NSI-X",
                "questions": [
                    {
                        "id": "Q1",
                        "capacite": "FAUSSE-C999",
                        "correcte": "A",
                        "options": {"A": "a", "B": "b", "C": "c", "D": "d"},
                        "diagnostics": {
                            key: {"erreur": "e", "renvoi": "C1"}
                            for key in "BCD"
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    resolver = producer.capacity_identity.CapacityIdentityResolver.from_corpora(
        (corpus,)
    )
    with pytest.raises(producer.capacity_identity.UnresolvedCapacityIdentity):
        producer._qcm("1NSI-X", chapter, resolver)


def test_qcm_missing_a_contract_capacity_is_a_gap(producer, tmp_path: Path) -> None:
    corpus = tmp_path / "chapitres"
    chapter = corpus / "1NSI-X"
    (chapter / "qcm").mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {
                "chapitre": "1NSI-X",
                "capacites": [
                    {"code": "C1", "ref_capacite": "REF-C1"},
                    {"code": "C2", "ref_capacite": "REF-C2"},
                ],
            }
        ),
        encoding="utf-8",
    )
    questions = []
    for index, key in enumerate("ABCD", start=1):
        questions.append(
                {
                    "id": f"Q{index}",
                    "enonce": "Question test",
                    "capacite": "C1",
                "correcte": key,
                "options": {letter: letter for letter in "ABCD"},
                "diagnostics": {
                    letter: {"erreur": "e", "renvoi": "C1"}
                    for letter in "ABCD"
                    if letter != key
                },
            }
        )
    (chapter / "qcm/x-QCM.json").write_text(
        json.dumps({"chapitre": "1NSI-X", "questions": questions}),
        encoding="utf-8",
    )
    resolver = producer.capacity_identity.CapacityIdentityResolver.from_corpora(
        (corpus,)
    )
    result = producer._qcm("1NSI-X", chapter, resolver)
    assert result["distribution_contract_met"] is True
    assert result["missing_capacities"] == ["C2"]
    assert result["status"] == "GAP"


def test_publish_matrix_refuses_multiple_qcm_sources(producer, tmp_path: Path) -> None:
    corpus = tmp_path / "chapitres"
    chapter = corpus / "1NSI-X"
    (chapter / "qcm").mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {"chapitre": "1NSI-X", "capacites": [{"code": "C1"}]}
        ),
        encoding="utf-8",
    )
    payload = {"chapitre": "1NSI-X", "questions": []}
    for name in ("A-QCM.json", "B-QCM.json"):
        (chapter / "qcm" / name).write_text(json.dumps(payload), encoding="utf-8")
    resolver = producer.capacity_identity.CapacityIdentityResolver.from_corpora(
        (corpus,)
    )
    with pytest.raises(producer.ReadinessError, match="MULTIPLE_QCM_SOURCES"):
        producer._qcm("1NSI-X", chapter, resolver)


def _assessment_source(path: Path, meta: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("% META: " + json.dumps(meta) + "\nContenu.\n", encoding="utf-8")


def _assessment_corpus(tmp_path: Path, producer):
    corpus = tmp_path / "chapitres"
    chapter = corpus / "1NSI-X"
    chapter.mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {
                "chapitre": "1NSI-X",
                "capacites": [{"code": "C1", "ref_capacite": "REF-C1"}],
            }
        ),
        encoding="utf-8",
    )
    resolver = producer.capacity_identity.CapacityIdentityResolver.from_corpora(
        (corpus,)
    )
    return chapter, resolver


def test_assessment_unknown_capacity_fails_closed(producer, tmp_path: Path) -> None:
    chapter, resolver = _assessment_corpus(tmp_path, producer)
    _assessment_source(
        chapter / "evaluations/A.tex",
        {
            "id": "A",
            "chapitre": "1NSI-X",
            "type_objet": "evaluation",
            "capacites": ["C999"],
            "status": "approved",
        },
    )
    with pytest.raises(producer.capacity_identity.UnresolvedCapacityIdentity):
        producer._assessments("1NSI-X", chapter, resolver)


def test_assessment_orphan_correction_is_a_gap(producer, tmp_path: Path) -> None:
    chapter, resolver = _assessment_corpus(tmp_path, producer)
    _assessment_source(
        chapter / "evaluations/A-corrige.tex",
        {
            "id": "A-CORRIGE",
            "chapitre": "1NSI-X",
            "type_objet": "corrige_evaluation",
            "evaluation_ref": "ABSENT",
            "capacites": ["C1"],
            "status": "approved",
        },
    )
    result = producer._assessments("1NSI-X", chapter, resolver)
    assert result["orphan_corrections"] == ["A-CORRIGE"]
    assert result["status"] == "GAP"


def _bind_passing_receipt(chapter: Path, stem: str) -> None:
    """Un recu SymPy `pass` reellement lie au contenu actuel de la source."""
    source = chapter / "evaluations" / f"{stem}.tex"
    digest = "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()
    receipts = chapter / "validations"
    receipts.mkdir(parents=True, exist_ok=True)
    (receipts / f"{stem}.sympy.json").write_text(
        json.dumps(
            {
                "objet_id": stem,
                "gate": "sympy",
                "verdict": "pass",
                "source_path": str(source),
                "source_sha256": digest,
            }
        ),
        encoding="utf-8",
    )


def _assessment_pair(chapter: Path, suffix: str, subject_status: str,
                     correction_status: str) -> None:
    subject_id = f"EV-{suffix}"
    _assessment_source(
        chapter / f"evaluations/{subject_id}.tex",
        {
            "id": subject_id,
            "chapitre": "1NSI-X",
            "type_objet": "evaluation",
            "capacites": ["C1"],
            "version": suffix,
            "status": subject_status,
        },
    )
    _assessment_source(
        chapter / f"evaluations/{subject_id}-corrige.tex",
        {
            "id": f"{subject_id}-corrige",
            "chapitre": "1NSI-X",
            "type_objet": "corrige_evaluation",
            "evaluation_ref": subject_id,
            "capacites": ["C1"],
            "status": correction_status,
        },
    )


@pytest.mark.parametrize("status", ["needs_review", "foobar", "approved", "verified"])
def test_no_declared_status_replaces_current_machine_evidence(
    producer, tmp_path: Path, status: str
) -> None:
    """Aucun statut declare ne vaut preuve, `approved` compris.

    OLD_ASSERTION_PURPOSE
        un devoir dont le statut etait `needs_review` ou inconnu comptait comme
        lacune, tandis qu'un corrige `approved` passait -- le statut declare
        suffisait a etablir la conformite.
    NEW_ASSERTION
        la conformite se lit sur la preuve machine COURANTE. Sans recu lie au
        contenu actuel, tout objet d'evaluation est en lacune, quel que soit le
        statut declare, et les corriges ne sont plus exemptes.
    WHY_NEW_IS_STRONGER_OR_EQUIVALENT
        l'ensemble signale est un sur-ensemble strict de l'ancien (4 objets au
        lieu de 2) : l'exemption dont beneficiait un `approved` legacy sans
        aucune preuve disparait, et le cas `verified` -- qui passait aussi par
        le seul statut -- est desormais couvert par le meme mecanisme.
    """
    chapter, resolver = _assessment_corpus(tmp_path, producer)
    for suffix in ("A", "B"):
        _assessment_pair(chapter, suffix, status, "approved")
    result = producer._assessments("1NSI-X", chapter, resolver)
    assert result["invalid_status"] == [
        "EV-A", "EV-A-corrige", "EV-B", "EV-B-corrige",
    ]
    assert result["status"] == "GAP"


def test_current_bound_evidence_admits_an_object_whatever_its_status(
    producer, tmp_path: Path
) -> None:
    """Le pendant : `generated` + preuve courante liee suffit.

    Sans ce test, l'axe pourrait etre satisfait en refusant tout le monde.
    """
    chapter, resolver = _assessment_corpus(tmp_path, producer)
    for suffix in ("A", "B"):
        _assessment_pair(chapter, suffix, "generated", "generated")
        _bind_passing_receipt(chapter, f"EV-{suffix}")
        _bind_passing_receipt(chapter, f"EV-{suffix}-corrige")
    result = producer._assessments("1NSI-X", chapter, resolver)
    assert result["invalid_status"] == []
    assert result["status"] == "COMPLETE"


def test_a_receipt_that_no_longer_matches_its_source_is_not_evidence(
    producer, tmp_path: Path
) -> None:
    """Un `pass` d'hier ne certifie pas un texte reecrit depuis."""
    chapter, resolver = _assessment_corpus(tmp_path, producer)
    for suffix in ("A", "B"):
        _assessment_pair(chapter, suffix, "generated", "generated")
        _bind_passing_receipt(chapter, f"EV-{suffix}")
        _bind_passing_receipt(chapter, f"EV-{suffix}-corrige")
    # La source change apres coup : le recu devient perime.
    victim = chapter / "evaluations/EV-A.tex"
    victim.write_text(victim.read_text(encoding="utf-8") + "\nAjout.\n", encoding="utf-8")
    result = producer._assessments("1NSI-X", chapter, resolver)
    assert "EV-A" in result["invalid_status"]
    assert result["status"] == "GAP"


def test_evidence_requiring_human_review_is_counted_and_never_hidden(
    producer,
) -> None:
    """Une question reservee a l'humain doit rester VISIBLE et comptee.

    Sur decision humaine du 2026-09-02, elle ne rougit plus l'axe machine --
    c'est un constat, pas une lacune, et l'axe `oracle` applique cette regle
    depuis toujours. Mais l'invariant qui compte demeure : elle ne doit jamais
    disparaitre du rapport. Un axe vert qui aurait efface sa dette humaine
    serait exactement le controle auto-confirmant que la campagne combat.
    """

    routed = {
        "1NSI-X": [
            {
                "question_id": "Q1",
                "semantic_question_digest": "sha256:one",
                "evidence_status": "HUMAN_REVIEW_REQUIRED",
            }
        ]
    }
    result = producer._evidence_routing(
        "1NSI-X", routed, expected_question_identities=["Q1::sha256:one"]
    )
    assert result["human_review_required"] == 1
    assert result["unknown"] == 0
    assert result["status"] == "COMPLETE"


def test_evidence_count_must_equal_current_qcm_question_count(producer) -> None:
    routed = {
        "1NSI-X": [
            {
                "question_id": question,
                "semantic_question_digest": f"sha256:{question}",
                "evidence_status": "MACHINE_RECALCULATED",
            }
            for question in ("Q1", "Q2")
        ]
    }
    result = producer._evidence_routing(
        "1NSI-X", routed, expected_question_identities=["Q1::sha256:Q1"]
    )
    assert result["count_matches_qcm"] is False
    assert result["status"] == "GAP"


def test_evidence_semantic_drift_is_detected_even_at_equal_cardinality(
    producer,
) -> None:
    routed = {
        "1NSI-X": [
            {
                "question_id": "Q1",
                "semantic_question_digest": "sha256:old",
                "evidence_status": "MACHINE_RECALCULATED",
            }
        ]
    }
    result = producer._evidence_routing(
        "1NSI-X", routed, expected_question_identities=["Q1::sha256:new"]
    )
    assert result["count_matches_qcm"] is True
    assert result["identity_set_matches_qcm"] is False
    assert result["status"] == "GAP"


def test_cross_discipline_and_course_assembly_are_separate_dimensions(
    producer,
) -> None:
    cross = producer._cross_discipline_truth(
        "1NSI-X",
        {
            "per_chapter": {
                "1NSI-X": {
                    "assembly_authority": "CANONICAL_NSI_ASSEMBLER",
                    "CROSS_DISCIPLINE_TERMINALE_MATHS": 1,
                    "REQUIRES_EXPLICIT_ADJUDICATION": 0,
                }
            }
        },
    )
    assembly = producer._course_assembly_truth(
        "1NSI-X",
        {
            "chapters": {
                "1NSI-X": {
                    "assembly_authority": "CANONICAL_NSI_ASSEMBLER",
                    "foreign_course_bodies": [],
                    "duplicated_course_body_count": 0,
                    "missing_expected_course_capacities": [],
                    "assembled_bodies": [
                        {"ownership_status": "SOURCE_SCOPED_UNIQUE_BODY"}
                    ],
                }
            }
        },
    )
    assert cross["status"] == "GAP"
    assert assembly["status"] == "COMPLETE"
    assert cross["cross_discipline_count"] == 1


def test_ex_co_unknown_or_structural_failure_blocks_machine_dimension(producer) -> None:
    graph = {
        "relations": [
            {
                "correction_id": "CO1",
                "exercise_id": "EX1",
                "correction_chapter": "1NSI-X",
                "classifications": ["UNKNOWN"],
            },
            {
                "correction_id": "CO2",
                "exercise_id": "EX2",
                "correction_chapter": "1NSI-X",
                "classifications": ["MISMATCHED_CAPACITY"],
            },
        ],
        "exercise_cardinality": [
            {
                "exercise_id": "EX1",
                "exercise_chapter": "1NSI-X",
                "classification": "MATCH",
            },
            {
                "exercise_id": "EX2",
                "exercise_chapter": "1NSI-X",
                "classification": "ORPHAN_EX",
            },
        ],
    }
    truth = producer._ex_co_truth("1NSI-X", graph)
    assert truth["unknown"] == 1
    # DEUX échecs structurels, pas un : `UNKNOWN` en est un depuis que le
    # classifieur connaît toutes les conventions du corpus, et qu'une
    # disposition non reconnue est redevenue un signal plutôt qu'une
    # tolérance. Ce test attendait encore l'ancienne règle.
    assert truth["structural_failures"] == 2
    assert truth["cardinality_failures"] == 1
    assert truth["status"] == "GAP"


@pytest.mark.parametrize(
    "human",
    [
        {
            "review_a": "APPROVED",
            "review_b": "APPROVED",
            "qcm_human_approval": "PENDING",
            "publication_approval": False,
        },
        {
            "review_a": "APPROVED",
            "review_b": "APPROVED",
            "qcm_human_approval": "SATISFIED",
            "publication_approval": False,
        },
    ],
)
def test_human_closure_never_ignores_qcm_or_publication_approval(
    producer, human
) -> None:
    assert producer._human_closure_status(human, []) == "PENDING"


def test_human_closure_never_ignores_declared_release_blocking_debt(
    producer,
) -> None:
    human = {
        "review_a": "APPROVED",
        "review_b": "APPROVED",
        "qcm_human_approval": "SATISFIED",
        "publication_approval": True,
    }
    debt = [{"ledger_id": "DEBT", "count": 1, "release_blocking": True}]
    assert producer._human_closure_status(human, debt) == "PENDING"


def test_declared_review_debt_routes_every_ledger_by_entry_chapter(producer) -> None:
    by_chapter = producer._declared_debt()
    geo = by_chapter["TSPE-GEOMETRIE-ESPACE"]
    by_id = {row["ledger_id"]: row for row in geo}
    assert by_id["TSPE_GEO_NEW_40"]["count"] == 40
    assert by_id["TSPE_GEO_NEW_40"]["provenance_counts"] == {
        "NEW_AUTHORED_UNREVIEWED": 40,
    }
    assert by_id["TSPE_GEO_REWRITTEN_STALE_APPROVAL_5"]["count"] == 5
    assert by_id["TSPE_GEO_REWRITTEN_STALE_APPROVAL_5"][
        "provenance_counts"
    ] == {"REWRITTEN_PREVIOUSLY_APPROVED_STALE": 5}

    apt = {
        row["ledger_id"]: row
        for row in by_chapter["1NSI-ALGO-PARCOURS-TRIS"]
    }
    adgk = {
        row["ledger_id"]: row
        for row in by_chapter["1NSI-ALGO-DICHO-GLOUTON-KNN"]
    }
    # Ce qui est verrouille : le routage par chapitre couvre EXACTEMENT le
    # registre du lot couple, sans perdre ni dupliquer une unite. Les comptes
    # par classe suivent le corpus, ils ne sont plus epingles.
    coupled = json.loads(
        (ROOT / "audit/NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT.json").read_text(
            encoding="utf-8"
        )
    )
    routed = sum(
        row["count"]
        for rows in (apt, adgk)
        for row in rows.values()
        if row["ledger_id"].startswith("NSI_COUPLED_")
    )
    assert routed == coupled["count"]
    for ledger_id, row in apt.items():
        if not ledger_id.startswith("NSI_COUPLED_"):
            continue
        assert sum(row["provenance_counts"].values()) == row["count"], ledger_id

    total_routed = sum(
        row["count"] for chapter_rows in by_chapter.values() for row in chapter_rows
    )
    queue_total = producer.human_queue_producer.build_queue()["counts"]["TOTAL"]
    assert total_routed >= queue_total
    assert any(
        row["ledger_id"] == "QCM_ANSWER_SEMANTICS"
        for chapter_rows in by_chapter.values()
        for row in chapter_rows
    )


def test_declared_review_debt_rejects_a_unit_routed_twice(producer) -> None:
    queue = producer.human_queue_producer.build_queue()
    item = next(
        row for row in queue["items"] if len(row["units_by_chapter"]) > 1
    )
    chapters = sorted(item["units_by_chapter"])
    duplicate = item["units_by_chapter"][chapters[0]]["unit_ids"][0]
    second = item["units_by_chapter"][chapters[1]]
    second["unit_ids"].append(duplicate)
    second["unit_ids"].sort()
    second["count"] = len(second["unit_ids"])
    second["set_digest"] = producer._set_digest(second["unit_ids"])

    with pytest.raises(producer.ReadinessError, match="double-routée"):
        producer._declared_debt(queue)


def test_ambiguous_course_ownership_blocks_assembly_truth(producer) -> None:
    result = producer._course_assembly_truth(
        "1NSI-X",
        {
            "chapters": {
                "1NSI-X": {
                    "assembly_authority": "CANONICAL_NSI_ASSEMBLER",
                    "foreign_course_bodies": [],
                    "duplicated_course_body_count": 0,
                    "missing_expected_course_capacities": [],
                    "assembled_bodies": [{"ownership_status": "AMBIGUOUS"}],
                }
            }
        },
    )
    assert result["ambiguous"] == 1
    assert result["status"] == "GAP"


def test_oracle_requires_nonempty_pass_receipts_and_no_manual_review(
    producer, tmp_path: Path
) -> None:
    chapter = tmp_path / "chapter"
    validations = chapter / "validations"
    validations.mkdir(parents=True)
    assert producer._oracle(chapter)["status"] == "NO_RECEIPTS"

    (validations / "one.sympy.json").write_text(
        json.dumps({"verdict": "manual_review"}), encoding="utf-8"
    )
    assert producer._oracle(chapter)["status"] == "GAP"

    (validations / "one.sympy.json").write_text(
        json.dumps({"verdict": "pass"}), encoding="utf-8"
    )
    assert producer._oracle(chapter)["status"] == "COMPLETE"


def test_programme_zero_atoms_is_never_complete(producer, tmp_path: Path) -> None:
    coverage_dir = tmp_path / "coverage"
    coverage_dir.mkdir()
    (coverage_dir / "1NSI.json").write_text(
        json.dumps({"rows": []}), encoding="utf-8"
    )
    corpus = tmp_path / "chapitres"
    chapter = corpus / "1NSI-X"
    chapter.mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {"chapitre": "1NSI-X", "capacites": [{"code": "C1"}]}
        ),
        encoding="utf-8",
    )
    resolver = producer.capacity_identity.CapacityIdentityResolver.from_corpora(
        (corpus,)
    )
    result = producer._programme("1NSI-X", "1NSI", resolver, coverage_dir)
    assert result["official_atoms"] == 0
    assert result["status"] == "NO_OFFICIAL_ATOMS"


def test_programme_mapping_must_resolve_against_the_chapter_contract(
    producer, tmp_path: Path
) -> None:
    coverage_dir = tmp_path / "coverage"
    coverage_dir.mkdir()
    (coverage_dir / "1NSI.json").write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "atom_id": "ATOM-X",
                        "chapter": "1NSI-X",
                        "mandatory": "YES",
                        "contract_capacity": "GARBAGE",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    corpus = tmp_path / "chapitres"
    chapter = corpus / "1NSI-X"
    chapter.mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {
                "chapitre": "1NSI-X",
                "capacites": [{"code": "C1", "ref_capacite": "REF-C1"}],
            }
        ),
        encoding="utf-8",
    )
    resolver = producer.capacity_identity.CapacityIdentityResolver.from_corpora(
        (corpus,)
    )

    result = producer._programme("1NSI-X", "1NSI", resolver, coverage_dir)

    assert result["mapped"] == 0
    assert result["unresolved_mappings"] == ["ATOM-X:GARBAGE"]
    assert result["status"] == "GAP"


def test_programme_row_cannot_credit_a_capacity_owned_by_another_chapter(
    producer, tmp_path: Path
) -> None:
    coverage_dir = tmp_path / "coverage"
    coverage_dir.mkdir()
    (coverage_dir / "1NSI.json").write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "atom_id": "ATOM-X",
                        "chapter": "1NSI-A",
                        "mandatory": "YES",
                        "contract_capacity": "REF-B",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    corpus = tmp_path / "chapitres"
    for chapter_name, reference in (("1NSI-A", "REF-A"), ("1NSI-B", "REF-B")):
        chapter = corpus / chapter_name
        chapter.mkdir(parents=True)
        (chapter / "contrat.yaml").write_text(
            yaml.safe_dump(
                {
                    "chapitre": chapter_name,
                    "capacites": [{"code": "C1", "ref_capacite": reference}],
                }
            ),
            encoding="utf-8",
        )
    resolver = producer.capacity_identity.CapacityIdentityResolver.from_corpora(
        (corpus,)
    )

    result = producer._programme("1NSI-A", "1NSI", resolver, coverage_dir)
    assert result["mapped"] == 0
    assert result["status"] == "GAP"


def test_not_applicable_dimension_does_not_block_machine_completion(producer) -> None:
    assert producer._machine_dimensions_complete(
        {"programme": "COMPLETE", "cross_discipline": "NOT_APPLICABLE"}
    )
    assert not producer._machine_dimensions_complete(
        {"programme": "COMPLETE", "course_truth": "NOT_AUDITED"}
    )


def test_two_assessment_subjects_with_same_variant_do_not_satisfy_a_plus_b(
    producer, tmp_path: Path
) -> None:
    chapter, resolver = _assessment_corpus(tmp_path, producer)
    for index in (1, 2):
        subject = f"EV-A{index}"
        _assessment_source(
            chapter / f"evaluations/{subject}.tex",
            {
                "id": subject,
                "chapitre": "1NSI-X",
                "type_objet": "evaluation",
                "version": "A",
                "capacites": ["C1"],
                "status": "approved",
            },
        )
        _assessment_source(
            chapter / f"evaluations/{subject}-corrige.tex",
            {
                "id": f"{subject}-CORRIGE",
                "chapitre": "1NSI-X",
                "type_objet": "corrige_evaluation",
                "evaluation_ref": subject,
                "capacites": ["C1"],
                "status": "approved",
            },
        )
    result = producer._assessments("1NSI-X", chapter, resolver)
    assert result["duplicate_variants"] == ["A"]
    assert result["missing_variants"] == ["B"]
    assert result["status"] == "GAP"


def test_programme_explicit_plus_mapping_resolves_each_exact_reference(
    producer, tmp_path: Path
) -> None:
    coverage_dir = tmp_path / "coverage"
    coverage_dir.mkdir()
    (coverage_dir / "TCOMPL.json").write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "atom_id": "TCOMPL-OFFICIAL-113",
                        "chapter": "TCOMPL-CALCULS-AIRES",
                        "mandatory": "YES",
                        "contract_capacity": "TCOMPL-AIR-C4 + TCOMPL-AIR-C5",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    corpus = tmp_path / "chapitres"
    chapter = corpus / "TCOMPL-CALCULS-AIRES"
    chapter.mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {
                "chapitre": chapter.name,
                "capacites": [
                    {"code": "C4", "ref_capacite": "TCOMPL-AIR-C4"},
                    {"code": "C5", "ref_capacite": "TCOMPL-AIR-C5"},
                ],
            }
        ),
        encoding="utf-8",
    )
    resolver = producer.capacity_identity.CapacityIdentityResolver.from_corpora(
        (corpus,)
    )
    result = producer._programme(
        chapter.name, "TCOMPL", resolver, coverage_dir
    )
    assert result["mapped"] == 1
    assert result["unresolved_mappings"] == []
    assert result["status"] == "COMPLETE"


def _alignment(producer, cell_id: str, disposition: str = "JUGEMENT_SEMANTIQUE_HUMAIN_REQUIS"):
    """Un registre d'alignement minimal, portant une seule cellule."""

    uid, _, role = cell_id.rpartition("::")
    return {
        "artifact_type": "semantic_alignment_ledger",
        "counts": {"cells_examined": 1, "DEFAUT_ETABLI": 0, "UNKNOWN": 0},
        "records": [
            {
                "chapter": "1NSI-X",
                "cell_id": cell_id,
                "official_capacity": {"canonical_uid": uid},
                "pedagogical_role": role,
                "semantic_alignment": {"disposition": disposition},
            }
        ],
    }


def test_une_cellule_routee_vers_l_humain_ne_bloque_plus_la_machine(producer) -> None:
    """Regle de l'oracle, appliquee a la couverture des roles.

    Decision humaine du 2026-09-02 : un axe est machine-complet quand la
    machine n'a plus rien a classer, jamais quand plus aucun jugement humain
    n'est requis. L'axe `oracle` applique cette regle depuis toujours avec 148
    `human_science_required` ; la couverture des roles l'applique desormais
    aussi. Rien n'est approuve pour autant : `human_closure_status` reste
    PENDING.
    """

    coverage, clone = _fixtures(producer)
    coverage["rows"][0]["state"] = "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED"
    alignment = _alignment(producer, "1NSI::1NSI-X::C1::cours")

    truth = producer._capacity_truth("1NSI-X", coverage, clone, alignment=alignment)
    role = truth["pedagogical_role_coverage"]

    assert role["semantically_unvalidated"] == 1
    assert role["routed_to_human"] == 1
    assert role["machine_unclassified"] == 0
    assert role["defects"] == 0
    assert role["status"] == "COMPLETE"


def test_une_cellule_non_routee_reste_inclassable_et_rougit(producer) -> None:
    """Mutation : le registre ne doit verdir que ce qu'il couvre REELLEMENT.

    Si le rapprochement se faisait au comptage plutot qu'a l'identite, un
    registre qui route une cellule etrangere verdirait la cellule reelle. La
    porte doit rester rouge.
    """

    coverage, clone = _fixtures(producer)
    coverage["rows"][0]["state"] = "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED"
    alignment = _alignment(producer, "1NSI::1NSI-X::C99::cours")

    truth = producer._capacity_truth("1NSI-X", coverage, clone, alignment=alignment)
    role = truth["pedagogical_role_coverage"]

    assert role["machine_unclassified"] == 1
    assert role["status"] == "GAP"


def test_un_defaut_etabli_rougit_la_couverture_des_roles(producer) -> None:
    """Mutation : router n'est pas absoudre.

    Une cellule dont le registre etablit un DEFAUT doit rougir l'axe, sans
    quoi le registre serait un blanchisseur et non une mesure.
    """

    coverage, clone = _fixtures(producer)
    coverage["rows"][0]["state"] = "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED"
    alignment = _alignment(
        producer, "1NSI::1NSI-X::C1::cours", disposition="DEFAUT_ETABLI"
    )

    truth = producer._capacity_truth("1NSI-X", coverage, clone, alignment=alignment)
    role = truth["pedagogical_role_coverage"]

    assert role["defects"] == 1
    assert role["status"] == "GAP"


def test_une_lacune_reelle_rougit_toujours_malgre_le_registre(producer) -> None:
    """Mutation : MISSING et INDETERMINATE ne sont pas routables.

    Une cellule sans contenu, ou dont le proprietaire semantique est
    indecidable, n'est pas un jugement humain en attente : c'est une lacune ou
    une revue de clone. Le registre ne doit jamais les couvrir.
    """

    for state, champ in (
        ("MISSING", "missing"),
        ("INDETERMINATE_CLONE_CREDIT", "indeterminate"),
    ):
        coverage, clone = _fixtures(producer)
        coverage["rows"][0]["state"] = state
        alignment = _alignment(producer, "1NSI::1NSI-X::C1::cours")
        truth = producer._capacity_truth(
            "1NSI-X", coverage, clone, alignment=alignment
        )
        role = truth["pedagogical_role_coverage"]
        assert role[champ] == 1
        assert role["status"] == "GAP", f"{state} doit rester bloquant"


def test_une_question_qcm_reservee_a_l_humain_ne_bloque_plus_la_machine(
    producer,
) -> None:
    """Meme regle pour le routage de preuve QCM.

    `1SPE-VARIABLES-ALEATOIRES/Q16` porte sur le role d'un parametre dans un
    listing Python : aucune famille mathematique ne la decide, et c'est un
    constat, pas une lacune. Ce qui doit rougir est l'INCONNU, jamais l'humain.
    """

    routed = {
        "1NSI-X": [
            {
                "question_id": "Q1",
                "semantic_question_digest": "sha256:d1",
                "evidence_status": "HUMAN_REVIEW_REQUIRED",
            }
        ]
    }
    truth = producer._evidence_routing(
        "1NSI-X", routed, expected_question_identities=["Q1::sha256:d1"]
    )
    assert truth["human_review_required"] == 1
    assert truth["unknown"] == 0
    assert truth["status"] == "COMPLETE"


def test_un_statut_de_preuve_inconnu_rougit_toujours(producer) -> None:
    """Mutation : un statut hors nomenclature reste inclassable."""

    routed = {
        "1NSI-X": [
            {
                "question_id": "Q1",
                "semantic_question_digest": "sha256:d1",
                "evidence_status": "STATUT_IMPREVU",
            }
        ]
    }
    truth = producer._evidence_routing(
        "1NSI-X", routed, expected_question_identities=["Q1::sha256:d1"]
    )
    assert truth["unknown"] == 1
    assert truth["status"] == "GAP"


def test_un_jeu_de_questions_qui_ne_correspond_pas_rougit_toujours(producer) -> None:
    """Mutation : la preuve doit porter sur les questions reellement presentes."""

    routed = {
        "1NSI-X": [
            {
                "question_id": "Q1",
                "semantic_question_digest": "sha256:AUTRE",
                "evidence_status": "MACHINE_RECALCULATED",
            }
        ]
    }
    truth = producer._evidence_routing(
        "1NSI-X", routed, expected_question_identities=["Q1::sha256:d1"]
    )
    assert truth["identity_set_matches_qcm"] is False
    assert truth["status"] == "GAP"


def test_la_dette_humaine_de_richesse_reste_visible_sur_un_axe_vert(
    producer,
) -> None:
    """Un axe vert ne doit jamais effacer ce qu'il a route vers l'humain."""

    truth = producer._richness_truth(
        "1NSI-X",
        {
            "chapters": {
                "1NSI-X": {
                    "machine_status": "COMPLETE",
                    "semantic_validation_status": "ROUTED_TO_HUMAN",
                    "unknown": 0,
                    "routed_to_human": 7,
                    "insufficient": [],
                    "capacity_identity_blockers": [],
                    "excluded_credit_objects": [],
                    "capacities_digest": "sha256:test",
                }
            }
        },
    )
    assert truth["status"] == "COMPLETE"
    assert truth["routed_to_human"] == 7
    assert truth["semantic_validation_status"] == "ROUTED_TO_HUMAN"


def test_a_missing_cell_is_a_gap_only_if_the_triage_says_so(producer) -> None:
    """§22 : le gate consomme `REAL_PEDAGOGICAL_GAP`, pas la population brute.

    Une cellule vide a cinq causes possibles et une seule appelle de
    l'écriture. Compter les cinq reviendrait à lire « 408 cellules vides »
    comme « 408 objets à écrire », ce que le triage réfute explicitement.
    """
    coverage, clone_ledger = _fixtures(producer)
    coverage["rows"] = [
        {"manual": "1NSI", "chapter": "1NSI-X", "capacity": "C1",
         "canonical_capacity_uid": "U1", "role": "cours", "state": "MISSING"},
        {"manual": "1NSI", "chapter": "1NSI-X", "capacity": "C2",
         "canonical_capacity_uid": "U2", "role": "methodes",
         "state": "MISSING"},
    ]
    triage = {
        "units": [
            {"CHAPTER": "1NSI-X", "canonical_capacity_uid": "U1",
             "ROLE": "cours",
             "APPLICABILITY_VERDICT": "SATISFIED_TRANSVERSALLY"},
            {"CHAPTER": "1NSI-X", "canonical_capacity_uid": "U2",
             "ROLE": "methodes",
             "APPLICABILITY_VERDICT": "REAL_PEDAGOGICAL_GAP"},
        ]
    }

    truth = producer._capacity_truth(
        "1NSI-X", coverage, clone_ledger, role_applicability=triage
    )
    role = truth["pedagogical_role_coverage"]
    assert role["raw_missing"] == 2
    assert role["triaged_not_a_gap"] == 1
    assert role["missing"] == 1
    assert role["missing_ids"] == ["U2::methodes"]


def test_a_cell_the_triage_never_judged_stays_a_gap(producer) -> None:
    """Le verdict par défaut est la lacune : l'omission n'exempte pas."""
    coverage, clone_ledger = _fixtures(producer)
    coverage["rows"] = [
        {"manual": "1NSI", "chapter": "1NSI-X", "capacity": "C9",
         "canonical_capacity_uid": "U9", "role": "cours", "state": "MISSING"},
    ]
    truth = producer._capacity_truth(
        "1NSI-X", coverage, clone_ledger, role_applicability={"units": []}
    )
    role = truth["pedagogical_role_coverage"]
    assert role["missing"] == 1
    assert role["triaged_not_a_gap"] == 0
