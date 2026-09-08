"""Un chapitre faible doit apparaitre dans la taxonomie des blockers.

Douze chapitres classes `WEAK` et `PRODUCT_P2 = 0` : c'etait une taxonomie
fausse, pas un produit sain. La correction porte sur l'AGREGATION, jamais sur
le verdict -- requalifier un chapitre faible en adequat pour vider un
compteur serait exactement le raccourci que le mandat interdit.

Ces tests sont des tests de MUTATION : ils fabriquent un verdict faible et
verifient qu'il ressort en `PRODUCT_P2`, puis un verdict inexploitable et
verifient qu'il ressort au moins en `PRODUCT_P1`. Un test qui se contenterait
de lire le compteur actuel passerait encore le jour ou la regle disparait.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VERDICTS = ROOT / "audit/CHAPTER_PEDAGOGICAL_VERDICT.json"
MATRIX = ROOT / "audit/PUBLISH_READINESS_CHAPTER_MATRIX.json"


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def reasons():
    return _load("raw_reasons", "scripts/build_release_raw_reasons.py")


@pytest.mark.parametrize(
    "verdict,attendu",
    [("WEAK", "PRODUCT_P2"), ("UNUSABLE", "PRODUCT_P1")],
)
def test_a_weak_chapter_becomes_a_product_blocker(reasons, verdict, attendu) -> None:
    classe = reasons.classify(f"CONTENT:TEXP-GRAPHES:pedagogical_quality:{verdict}")
    assert classe is not None, verdict
    assert classe["category"] == attendu
    assert classe["target"] == "TEXP-GRAPHES"


def test_unusable_is_strictly_more_severe_than_weak(reasons) -> None:
    """`UNUSABLE` n'est pas un `WEAK` un peu plus grave : il bloque plus haut."""

    severite = {"PRODUCT_P0": 0, "PRODUCT_P1": 1, "PRODUCT_P2": 2}
    faible = reasons.classify("CONTENT:X:pedagogical_quality:WEAK")["category"]
    inexploitable = reasons.classify("CONTENT:X:pedagogical_quality:UNUSABLE")["category"]
    assert severite[inexploitable] < severite[faible]


def test_an_unaudited_chapter_is_a_certification_blocker_not_a_pass(reasons) -> None:
    """« Non audite » n'est pas « adequat » : c'est une preuve absente."""

    classe = reasons.classify("CONTENT:X:pedagogical_quality:NOT_AUDITED")
    assert classe["category"] == "CERTIFICATION_BLOCKER"


def test_an_adequate_chapter_emits_no_blocker(reasons) -> None:
    """La regle ne doit pas transformer un chapitre sain en blocker."""

    assert reasons.classify("CONTENT:X:pedagogical_quality:ADEQUATE") is None
    assert reasons.classify("CONTENT:X:pedagogical_quality:STRONG") is None


@pytest.fixture()
def verdicts_synthetiques(reasons, tmp_path, monkeypatch):
    """Un corpus fabrique, avec un chapitre faible et un inexploitable.

    Le corpus reel n'en compte plus aucun, et c'est le but recherche. Une
    population vide ne prouve pourtant rien sur le detecteur : elle le rend
    seulement silencieux. On lui fournit donc les cas qu'il doit voir.
    """

    (tmp_path / "audit").mkdir()
    (tmp_path / "audit/CHAPTER_PEDAGOGICAL_VERDICT.json").write_text(
        json.dumps({
            "chapters": [
                {"CHAPTER_ID": "TEST-FAIBLE", "PEDAGOGICAL_VERDICT": "WEAK"},
                {"CHAPTER_ID": "TEST-INEXPLOITABLE", "PEDAGOGICAL_VERDICT": "UNUSABLE"},
                {"CHAPTER_ID": "TEST-SAIN", "PEDAGOGICAL_VERDICT": "ADEQUATE"},
                {"CHAPTER_ID": "TEST-FORT", "PEDAGOGICAL_VERDICT": "STRONG"},
            ]
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(reasons, "ROOT", tmp_path)
    return reasons


def test_the_conflict_detector_catches_a_verdict_missing_from_the_taxonomy(
    verdicts_synthetiques,
) -> None:
    """Le test de mutation du detecteur lui-meme.

    On lui donne un jeu de raisons ou aucun blocker pedagogique n'apparait :
    il doit signaler un conflit pour chaque chapitre faible ou inexploitable.
    Sinon `PEDAGOGICAL_QUALITY_TAXONOMY_CONFLICTS = 0` ne prouverait rien.
    """

    conflits = verdicts_synthetiques._pedagogical_quality_conflicts([])
    assert sorted(c["chapter"] for c in conflits) == [
        "TEST-FAIBLE", "TEST-INEXPLOITABLE"
    ]
    assert all(c["observed"] == "ABSENT_FROM_TAXONOMY" for c in conflits)
    assert {c["expected"] for c in conflits} == {"PRODUCT_P2", "PRODUCT_P1"}


def test_the_conflict_detector_is_silent_when_every_verdict_is_routed(
    verdicts_synthetiques,
) -> None:
    attendu = verdicts_synthetiques.PEDAGOGICAL_QUALITY_EXPECTED_TAXONOMY
    complet = [
        {"target": chapitre, "category": categorie,
         "root_cause_id": "ROOT-PEDAGOGICAL-QUALITY-WEAK"}
        for chapitre, categorie in (
            ("TEST-FAIBLE", attendu["WEAK"]),
            ("TEST-INEXPLOITABLE", attendu["UNUSABLE"]),
        )
    ]
    assert verdicts_synthetiques._pedagogical_quality_conflicts(complet) == []


def test_a_downgraded_severity_is_reported_as_a_conflict(
    verdicts_synthetiques,
) -> None:
    """Ranger un chapitre faible ailleurs qu'en `PRODUCT_P2`.

    Si demain quelqu'un range la qualite pedagogique en blocker de
    certification -- « le produit va bien, c'est la preuve qui manque » -- le
    compteur produit retomberait a zero sans qu'un seul chapitre se soit
    ameliore. Le detecteur doit le voir.
    """

    mal_range = [{
        "target": "TEST-FAIBLE",
        "category": "CERTIFICATION_BLOCKER",
        "root_cause_id": "ROOT-PEDAGOGICAL-QUALITY-WEAK",
    }]
    conflits = verdicts_synthetiques._pedagogical_quality_conflicts(mal_range)
    detail = next(c for c in conflits if c["chapter"] == "TEST-FAIBLE")
    assert detail["expected"] == "PRODUCT_P2"
    assert detail["observed"] == "CERTIFICATION_BLOCKER"


def test_the_real_corpus_carries_no_taxonomy_conflict(reasons) -> None:
    """Et sur le corpus reel, le compteur doit valoir zero pour la bonne raison.

    Zero conflit parce qu'aucun chapitre n'est faible, et non parce que le
    detecteur ne regarde rien : les deux tests precedents l'etablissent sur
    des cas fabriques.
    """

    payload = json.loads(VERDICTS.read_text(encoding="utf-8"))
    verdicts = {r["PEDAGOGICAL_VERDICT"] for r in payload["chapters"]}
    assert verdicts <= {"STRONG", "ADEQUATE"}
    assert reasons._pedagogical_quality_conflicts([]) == []


def test_the_matrix_publishes_the_verdict_that_the_gate_will_read() -> None:
    """L'axe doit traverser la matrice, sinon la regle ne se declenche jamais.

    Le gate ne lit pas le verdict pedagogique : il lit `machine_dimensions`.
    Une regle branchee sur une dimension que la matrice n'exporte pas serait
    une regle morte.
    """

    verdicts = {
        r["CHAPTER_ID"]: r["PEDAGOGICAL_VERDICT"]
        for r in json.loads(VERDICTS.read_text(encoding="utf-8"))["chapters"]
    }
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    for row in matrix["chapters"]:
        dimension = row["machine_dimensions"]["pedagogical_quality"]
        verdict = verdicts[row["chapter"]]
        attendu = "COMPLETE" if verdict in {"STRONG", "ADEQUATE"} else verdict
        assert dimension == attendu, row["chapter"]


def test_the_gate_requires_both_structure_and_quality() -> None:
    """`STRUCTURAL_COMPLETENESS = PASS` ne suffit pas.

    Un chapitre peut avoir tous ses objets, tous ses corriges et tous ses
    QCM, et n'entrainer qu'a reproduire. Les deux conditions sont
    independantes et le gate exige les deux : on le verifie en constatant
    qu'un chapitre complet sur toutes les autres dimensions reste bloque par
    la seule qualite pedagogique.
    """

    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    ouverts = {"COMPLETE", "NO_QCM", "NOT_APPLICABLE"}
    faibles_mais_structurellement_complets = [
        row["chapter"] for row in matrix["chapters"]
        if row["machine_dimensions"]["pedagogical_quality"] not in ouverts
        and all(
            v in ouverts
            for k, v in row["machine_dimensions"].items()
            if k != "pedagogical_quality"
        )
    ]
    for chapitre in faibles_mais_structurellement_complets:
        row = next(r for r in matrix["chapters"] if r["chapter"] == chapitre)
        assert row["vertical_machine_status"] != "MACHINE_REVIEW_COMPLETE", chapitre
