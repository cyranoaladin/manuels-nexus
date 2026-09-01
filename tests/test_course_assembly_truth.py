"""Ce qu'un chapitre imprime doit etre ce qu'il possede.

Le sommaire imprime du manuel 1NSI ouvrait le chapitre « Algorithmique 1 :
parcours et tris » sur six sections appartenant au chapitre suivant --
recherche dichotomique, algorithmes gloutons, k plus proches voisins -- chacune
imprimee deux fois, avant que le chapitre n'arrive a son propre contenu.

Un registre de clones dit qu'un corps est partage ; il ne dit pas ce que le
lecteur recoit. Ces tests portent sur la verite d'assemblage.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "audit/COURSE_BODY_OWNERSHIP_MAP.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "course_assembly_truth", ROOT / "scripts/build_course_assembly_truth.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(MAP.read_text(encoding="utf-8"))


def test_the_committed_map_matches_the_producer(producer) -> None:
    assert producer.main(["--check"]) == 0


def test_no_chapter_assembles_a_body_it_does_not_own(payload: dict) -> None:
    """FOREIGN_COURSE_BODY = 0.

    C'est l'etat atteint, pas un objectif : les six copies etrangeres de
    1NSI-ALGO-PARCOURS-TRIS ont ete retirees apres que leur proprietaire eut
    ete ETABLI -- 1NSI-ALGO-DICHO-GLOUTON-KNN detient chaque corps une fois
    sous une capacite unique, tandis que PARCOURS-TRIS le detenait deux fois
    sous deux capacites.
    """

    assert payload["totals"]["FOREIGN_COURSE_BODY"] == 0
    assert payload["chapters_with_foreign_bodies"] == []
    for chapter, row in payload["chapters"].items():
        assert row["foreign_course_bodies"] == [], chapter
        for body in row["assembled_bodies"]:
            if body["ownership_proven"]:
                assert body["semantic_owner_chapter"] == chapter, body["path"]
            else:
                assert body["semantic_owner_chapter"] is None
                assert body["is_foreign"] is None


def test_parcours_tris_opens_on_its_own_content(payload: dict) -> None:
    """Le chapitre reparé, verifie par ses titres de section."""

    chapter = payload["chapters"]["1NSI-ALGO-PARCOURS-TRIS"]
    assert chapter["assembly_authority"] == "CANONICAL_NSI_ASSEMBLER"
    assert chapter["variant_assembly"]["eleve"]["paths"] == chapter[
        "variant_assembly"
    ]["professeur"]["paths"]
    titles = [
        title for body in chapter["assembled_bodies"] for title in body["toc_titles"]
    ]
    assert titles == [
        "Parcours séquentiel d'un tableau",
        "Le tri par insertion",
        "Le tri par sélection",
    ]
    # Et les six capacites du contrat restent servies par ces trois corps :
    # retirer les copies n'a coute aucune couverture.
    assert chapter["missing_expected_course_capacities"] == []
    assert chapter["expected_capacities"] == ["C1", "C2", "C3", "C4", "C5", "C6"]
    assert chapter["duplicated_course_body_count"] == 0


def test_dicho_keeps_the_bodies_it_owns(payload: dict) -> None:
    """Le canonique n'a pas ete touche par le retrait des copies."""

    chapter = payload["chapters"]["1NSI-ALGO-DICHO-GLOUTON-KNN"]
    titles = [
        title for body in chapter["assembled_bodies"] for title in body["toc_titles"]
    ]
    assert titles == [
        "Recherche dichotomique",
        "Algorithmes gloutons",
        "L'algorithme des k plus proches voisins",
    ]
    assert chapter["missing_expected_course_capacities"] == []
    assert chapter["duplicated_course_body_count"] == 0


def test_ownership_is_never_inferred_from_file_order(payload: dict) -> None:
    """La regle affichee doit rester celle qui a ete appliquee."""

    assert "jamais de l'ordre des fichiers" in payload["ownership_rule"]
    ambiguous = 0
    for chapter, row in payload["chapters"].items():
        for body in row["assembled_bodies"]:
            if not body["ownership_proven"]:
                assert body["semantic_owner_chapter"] is None
                assert body["is_foreign"] is None
                assert body["ownership_status"] == "AMBIGUOUS"
                ambiguous += 1
    assert ambiguous == payload["totals"]["AMBIGUOUS_COURSE_BODY"]


def test_the_remaining_duplication_is_measured_not_ignored(payload: dict) -> None:
    """La duplication interne aux chapitres NSI reste comptee et visible.

    Elle n'est pas encore fermee -- la reconstruction est en cours -- mais
    elle ne doit pas AUGMENTER, et le total doit rester exact.
    """

    total = sum(
        row["duplicated_course_body_count"] for row in payload["chapters"].values()
    )
    assert total == payload["totals"]["DUPLICATED_COURSE_BODY"]
    assert total <= 103, "un cours duplique a ete introduit"


def test_conflicting_meta_capacity_fields_fail_closed(
    producer, tmp_path: Path
) -> None:
    corpus = tmp_path / "chapitres"
    chapter = corpus / "1NSI-X"
    chapter.mkdir(parents=True)
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
    identity = producer._load("course_truth_identity_test", "scripts/capacity_identity.py")
    resolver = identity.CapacityIdentityResolver.from_corpora((corpus,))
    with pytest.raises(identity.AmbiguousCapacityIdentity):
        producer._resolve_course_capacities(
            resolver,
            "1NSI-X",
            {"capacites_codes": ["C1"], "capacites": ["REF-C2"]},
        )
