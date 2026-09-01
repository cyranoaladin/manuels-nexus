"""La richesse se mesure en gestes, et un geste appartient a sa question.

Le P0 de clonage a montre ce que vaut un compteur de fichiers : cinquante
exercices dont sept seulement etaient les copies de personne. La parade n'est
pas un autre quota -- « deux exercices par capacite » recreerait le
remplissage. Elle est de compter les occasions distinctes de mobilisation et
les gestes de raisonnement qu'elles demandent.

Ces tests protegent la mesure contre le retour du credit global : un probleme
de synthese qui travaille quatre capacites ne fait pas quatre fois le meme
geste, et il ne doit pas les crediter toutes des quatre.
"""

from __future__ import annotations

import importlib.util
import copy
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = "TSPE-GEOMETRIE-ESPACE"
MATRIX = ROOT / f"audit/CHAPTER_RICHNESS_{CHAPTER}.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "chapter_richness", ROOT / "scripts/build_chapter_richness_matrix.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def matrix() -> dict:
    return json.loads(MATRIX.read_text(encoding="utf-8"))


def test_the_committed_matrix_matches_the_producer(producer) -> None:
    assert producer.main(["--chapter", CHAPTER, "--check"]) == 0


def test_the_status_never_depends_on_a_file_quota(matrix: dict) -> None:
    """Une capacité servie par un seul exercice peut passer le seuil déclaratif."""

    single = [
        code
        for code, row in matrix["capacities"].items()
        if row["opportunities"]["targeted_practice"] == 1
        and row["declarative_status"] == "SUFFICIENT"
    ]
    assert single, (
        "la regle doit pouvoir declarer suffisante une capacite servie par un "
        "seul exercice ; sinon elle est redevenue un quota"
    )
    assert "quota" in matrix["rule"] or "jamais en nombre de fichiers" in matrix["rule"]


def test_a_composite_capacity_needs_more_than_one_reasoning_path(
    matrix: dict,
) -> None:
    for code, row in matrix["capacities"].items():
        if row["capacity_type"] in {"COMPOSITE_REASONING", "SYNTHESIS_HEAVY"}:
            assert len(row["reasoning_paths"]) >= 2, (
                f"{code} est composite et n'offre qu'un chemin de raisonnement"
            )


def test_a_multi_capacity_exercise_does_not_grant_all_its_gestures(
    producer,
) -> None:
    """Le credit global, sous une autre forme, reste interdit.

    EX-058 travaille quatre capacites en quatre sous-questions. Sans
    attribution par question, chacune heriterait des quatre gestes du probleme
    et paraitrait riche sans l'etre : c'est exactement le mecanisme du P0,
    deplace du META vers le geste.
    """

    clone = producer._clone_module()
    path = (
        ROOT
        / "Mathematiques/manuel-maths/chapitres"
        / CHAPTER
        / "exercices/TSPE-GEOESPACE-EX-058.tex"
    )
    meta = clone.read_meta(path.read_text(encoding="utf-8"))
    per_question = meta["capacites_par_question"]
    per_gesture = meta["gestes_par_question"]

    assert set(per_question) == set(per_gesture), (
        "chaque sous-question declare sa capacite ET son geste"
    )
    every = {g for gs in per_gesture.values() for g in gs}
    assert len(every) > 1, "le probleme doit bien mobiliser plusieurs gestes"

    built = producer.build_matrix(CHAPTER)["capacities"]
    for question, codes in per_question.items():
        for code in codes:
            granted = set(built[code]["reasoning_paths"])
            assert set(per_gesture[question]) <= granted
    # Aucune capacite ne recoit la totalite des gestes du probleme par le seul
    # fait d'y figurer.
    c8 = set(built["C8"]["reasoning_paths"])
    assert "preuve" not in c8 or "preuve" in {
        g for q, gs in per_gesture.items() for g in gs if "C8" in per_question[q]
    }, "C8 a herite d'un geste qui n'est pas celui de sa sous-question"


def test_declarations_alone_never_establish_semantic_richness(matrix: dict) -> None:
    assert matrix["insufficient"] == []
    assert matrix["semantic_validation_status"] == "UNKNOWN"
    assert matrix["machine_status"] == "GAP"
    assert matrix["unknown"] == len(matrix["capacities"])
    assert set(matrix["counts"]) == {"CANDIDATE_NON_SEMANTIC"}
    assert all(
        row["status"] == "CANDIDATE_NON_SEMANTIC"
        for row in matrix["capacities"].values()
    )


def test_the_corpus_does_not_rest_on_a_single_repeated_gesture(
    matrix: dict,
) -> None:
    profile = matrix["diversity_profile"]
    assert len(matrix["distinct_reasoning_paths"]) >= 4
    assert max(profile.values()) <= 0.5 * sum(profile.values())
    assert matrix["declarative_diversity_status"] == "SUFFICIENT"
    assert matrix["diversity_status"] == "CANDIDATE_NON_SEMANTIC"


def test_richness_digest_covers_row_content_not_only_capacity_codes(
    producer, matrix: dict
) -> None:
    changed = copy.deepcopy(matrix["capacities"])
    first = sorted(changed)[0]
    changed[first]["reasoning_paths"].append("GESTE_SYNTHETIQUE")
    assert producer._richness_digest(
        changed,
        matrix["capacity_identity_blockers"],
        matrix["excluded_credit_objects"],
    ) != matrix["capacities_digest"]


def test_indeterminate_clone_never_counts_as_richness(
    producer, tmp_path: Path
) -> None:
    corpus = tmp_path / "chapitres"
    chapter = corpus / "1NSI-X"
    exercise = chapter / "exercices/ex.tex"
    exercise.parent.mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {
                "chapitre": "1NSI-X",
                "capacites": [
                    {
                        "code": "C1",
                        "ref_capacite": "P-X-C1",
                        "libelle_eleve": "Parcourir une séquence",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    exercise.write_text(
        '% META: {"id":"EX","chapitre":"1NSI-X",'
        '"type_objet":"exercice","capacites_codes":["C1"],'
        '"gestes":["tracer"]}\nContenu.\n',
        encoding="utf-8",
    )
    identity = producer._identity_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))

    payload = producer.build_matrix(
        "1NSI-X",
        chapter_root=corpus,
        resolver=resolver,
        clone_ledger={
            "objects_on_invalid_credit": [],
            "objects_with_indeterminate_credit": [str(exercise)],
        },
    )

    row = payload["capacities"]["C1"]
    assert row["opportunities"]["targeted_practice"] == 0
    assert row["reasoning_paths"] == []
    assert payload["excluded_credit_objects"] == [
        {"path": str(exercise), "state": "INDETERMINATE"}
    ]


def test_nsi_qcm_official_reference_is_resolved_without_suffix_collision(
    producer, tmp_path: Path
) -> None:
    corpus = tmp_path / "chapitres"
    chapter = corpus / "1NSI-X"
    for role in ("exercices", "evaluations", "qcm", "remediation", "methodes"):
        (chapter / role).mkdir(parents=True, exist_ok=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {
                "chapitre": "1NSI-X",
                "capacites": [
                    {"code": "C1", "ref_capacite": "REF-C1", "libelle_eleve": "Lire"},
                    {
                        "code": "C10",
                        "ref_capacite": "TSPE-CONCLGN-C1",
                        "libelle_eleve": "Écrire",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    (chapter / "qcm/X-QCM.json").write_text(
        json.dumps(
            {
                "chapitre": "1NSI-X",
                "questions": [
                    {"id": "Q1", "capacite": "TSPE-CONCLGN-C1"}
                ],
            }
        ),
        encoding="utf-8",
    )
    identity = producer._identity_module()
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))
    built = producer.build_matrix(
        "1NSI-X", chapter_root=corpus, resolver=resolver
    )["capacities"]
    assert built["C10"]["opportunities"]["qcm"] == 1
    assert built["C1"]["opportunities"]["qcm"] == 0
