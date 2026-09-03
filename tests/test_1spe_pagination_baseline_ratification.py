"""La ratification de pagination ne vaut que si elle peut réfuter.

Le producteur ne décide rien : il confronte chaque valeur déclarée par la
décision humaine à une mesure faite sur les deux PDF. Ce module vérifie la
vérité courante, puis mute chaque preuve pour s'assurer qu'une déclaration
fausse est bien rejetée.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_pagination_baseline_ratification as gate  # noqa: E402


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def docket() -> dict[str, Any]:
    return gate.load_docket()


# ---------------------------------------------------------------------------
#  Vérité courante
# ---------------------------------------------------------------------------


def test_no_declared_value_is_refuted(payload: dict[str, Any]) -> None:
    assert payload["summary"]["REFUTED_CLAIMS"] == 0
    for variant in payload["variants"]:
        refuted = [
            row for row in variant["claims"] if row["verdict"] == "REFUTED"
        ]
        assert refuted == [], (variant["variant"], refuted)


def test_the_ratified_candidate_carries_no_false_chapter_folio(
    payload: dict[str, Any],
) -> None:
    """Le point de la décision : le sommaire ne mène plus à la page d'avant."""

    assert payload["summary"]["CHAPTER_OPENING_FALSE_FOLIO_AFTER"] == 0
    assert payload["summary"]["CHAPTER_OPENING_FALSE_BOOKMARK_AFTER"] == 0
    for variant in payload["variants"]:
        assert variant["CHAPTER_OPENING_FALSE_FOLIO_BEFORE"] > 0, (
            "un avant sans folio faux rendrait la ratification vide de sens"
        )
        boundaries = variant["chapter_boundaries"]
        assert len(boundaries) == 10, variant["variant"]
        for row in boundaries:
            assert row["folio_is_wrong_after"] is False, row
            assert row["toc_folio_after"] == row["opening_page_after"], row


def test_the_change_moved_boundaries_and_nothing_else(
    payload: dict[str, Any],
) -> None:
    summary = payload["summary"]
    assert summary["MISSING_CONTENT"] == 0
    assert summary["DUPLICATED_CONTENT"] == 0
    assert summary["UNEXPECTED_REORDERING"] == 0
    for variant in payload["variants"]:
        assert variant["CONTENT_STREAM_CONSERVED"] is True, variant["variant"]
        # Un flux vide serait conservé pour de mauvaises raisons.
        assert variant["after"]["content_stream_length"] > 100_000


def test_every_blank_page_carries_a_documented_reason(
    payload: dict[str, Any],
) -> None:
    summary = payload["summary"]
    assert summary["UNINTENTIONAL_BLANK_PAGE"] == 0
    assert summary["STALE_BLANK_PAGE_REASONS"] == 0
    assert summary["DOCUMENTED_BLANK_PAGE"] > 0
    for variant in payload["variants"]:
        for row in variant["blank_pages"]:
            assert row["documented"] is True, row
            assert row["reason"] != "UNDOCUMENTED", row
            assert row["mechanism"], row
            # Aucune de ces pages ne vient du clearpage ratifié.
            assert row["already_blank_before"] is True, row


def test_the_ratification_claims_nothing_it_was_not_given(
    payload: dict[str, Any],
) -> None:
    assert payload["content_approval"] is False
    assert payload["d7_approval"] is False
    assert payload["publication_approval"] is False
    assert payload["page_counts_are_pinned"] is False
    assert payload["ratified_mechanism"] == "clearpage"
    assert payload["refused_mechanism"] == "cleardoublepage"
    assert payload["authorized_change_class"] == "EXPECTED_PAGE_BOUNDARY_CHANGE"


def test_the_page_counts_are_reported_but_never_pinned(
    payload: dict[str, Any], docket: dict[str, Any]
) -> None:
    """363 et 635 sont mesurés, pas normés : rien ne les impose ailleurs."""

    ratified = {
        row["variant"]: row["after"]["page_count"] for row in payload["variants"]
    }
    assert ratified == {"eleve": 363, "professeur": 635}
    assert docket["page_counts_are_pinned"] is False
    assert docket["page_counts_are_pinned_reason"]
    # Et ils ont effectivement bougé depuis, sans qu'aucune ratification
    # nouvelle soit due : c'est ce que la décision de mise en page prévoit.
    assert docket["superseded_by"]["what_survives"]
    current = payload["summary"]["CURRENT_BUILD_PAGE_COUNTS"]
    assert current != ratified


def test_the_proof_is_pinned_to_its_commit_and_the_build_measured_apart(
    payload: dict[str, Any],
) -> None:
    """La ratification porte sur UN changement ; le build courant vit sa vie.

    Les deux etats compares sont relus dans l'historique, donc la preuve reste
    vraie quels que soient les changements autorises qui suivent. Ce qu'on
    demande au build courant, c'est de tenir encore les proprietes ratifiees —
    pas d'etre le meme fichier.
    """

    summary = payload["summary"]
    assert summary["CURRENT_BUILD_FALSE_CHAPTER_FOLIO"] == 0
    # Le compteur de pages n'est pas un invariant : la refonte des ouvertures
    # le supersede, et le docket ne l'a jamais epingle. Ce qui doit survivre,
    # c'est le folio vrai.
    assert "CURRENT_BUILD_PAGE_COUNT_CHANGED" in summary
    for row in payload["variants"]:
        current = row["current_build"]
        assert row["ratified_after_commit"] == payload["change_commit"]
        assert current["still_carries_no_false_chapter_folio"] is True
        assert current["pdf_sha256"]


def test_the_teacher_edition_carries_more_than_the_student_one(
    payload: dict[str, Any],
) -> None:
    """Les deux variantes ne portent pas le même texte, et c'est mesurable.

    Le manuel professeur ajoute corrigés, clés et barèmes : son flux dépouillé
    doit être nettement plus long que celui de l'élève. L'isolation elle-même
    — aucun identifiant interne, aucun barème côté élève — est prouvée par le
    contrat des notes de marge et par le gate de complétude professeur ; ici on
    vérifie seulement que les deux éditions restent bien deux éditions.
    """

    by_variant = {row["variant"]: row for row in payload["variants"]}
    student = by_variant["eleve"]["current_build"]["content_stream_length"]
    teacher = by_variant["professeur"]["current_build"]["content_stream_length"]

    assert teacher > student * 1.5, (student, teacher)


def test_the_folio_oracle_does_not_read_the_summary_twice(
    payload: dict[str, Any],
) -> None:
    """Ouverture localisée par le contenu, folio lu dans le sommaire imprimé.

    Confondre les deux était la raison pour laquelle le défaut a survécu :
    signet et sommaire descendent du même `\\addcontentsline`, ils étaient
    faux ensemble.
    """

    for variant in payload["variants"]:
        for row in variant["after"]["chapter_openings"]:
            assert row["opening_page"] >= 1
            assert row["toc_printed_folio"] is not None, row
            assert row["bookmark_destination"] is not None, row
    assert payload["summary"]["CHAPTER_TITLES_CARRY_NO_OWN_HYPHEN"] is True


def test_the_chapter_opener_overflow_is_named_and_not_laundered(
    payload: dict[str, Any],
) -> None:
    """Le débordement de l'ouverture est un défaut distinct, compté, pas absous.

    Il préexiste à la décision ratifiée et il a empiré : le producteur doit le
    dire, et surtout ne pas le ranger parmi les pages blanches documentées.
    """

    summary = payload["summary"]
    assert "CHAPTER_OPENER_OVERFLOW_AFTER" in summary
    assert summary["CHAPTER_OPENER_ORPHAN_PAGE_AFTER"] > 0, (
        "si le défaut disparaît, ce test doit être retiré avec sa mesure"
    )
    assert (
        summary["CHAPTER_OPENER_ORPHAN_PAGE_AFTER"]
        > summary["CHAPTER_OPENER_ORPHAN_PAGE_BEFORE"]
    ), "la ratification a aggravé ce défaut : le dire est le minimum"
    for variant in payload["variants"]:
        for row in variant["chapter_opener_overflow"]:
            assert row["overflow_page"] == row["opening_page"] + 1, row
            if row["overflow_is_nearly_empty"]:
                assert row["overflow_characters"] < gate.NEARLY_EMPTY_CHARACTERS


# ---------------------------------------------------------------------------
#  Mutations : le producteur doit refuser une déclaration fausse
# ---------------------------------------------------------------------------


def _measurement(**overrides: Any) -> dict[str, Any]:
    base = {
        "page_count": 363,
        "bookmark_count": 74,
        "summary_pages": [9, 10, 11, 12],
        "chapter_openings": [
            {
                "chapter_number": 1,
                "title": "Suites numériques",
                "opening_page": 14,
                "toc_printed_folio": 14,
                "bookmark_destination": 14,
                "folio_is_wrong": False,
                "bookmark_is_wrong": False,
            }
        ],
        "chapter_opening_false_folio": 0,
        "chapter_opening_false_bookmark": 0,
        "content_stream_sha256": "a" * 64,
        "content_stream_length": 582029,
        "chapter_titles_carry_no_own_hyphen": True,
        "opener_overflow": [],
        "blank_pages": [2],
        "nearly_empty_pages": [],
    }
    base.update(overrides)
    return base


def _docket(**overrides: Any) -> dict[str, Any]:
    base = {
        "superseded_baseline": {
            "student_page_count": 359,
            "teacher_page_count": 633,
            "student_wrong_chapter_folios": 3,
            "teacher_wrong_chapter_folios": 6,
        },
        "ratified_candidate": {
            "student_page_count": 363,
            "teacher_page_count": 635,
            "student_wrong_chapter_folios": 0,
            "teacher_wrong_chapter_folios": 0,
        },
        "documented_blank_pages": [
            {"page": 2, "reason": "VERSO", "mechanism": "cleardoublepage"}
        ],
    }
    base.update(overrides)
    return base


def test_a_wrong_declared_page_count_is_refuted() -> None:
    before = _measurement(page_count=359, chapter_opening_false_folio=3)
    after = _measurement(page_count=364)  # le PDF dit 364, la décision dit 363

    row = gate.compare("eleve", before, after, _docket())

    assert row["REFUTED_CLAIMS"] == 1
    refuted = [item for item in row["claims"] if item["verdict"] == "REFUTED"]
    assert refuted[0]["claim"] == "eleve_page_count_after"
    assert refuted[0]["observed"] == 364


def test_a_wrong_declared_folio_count_is_refuted() -> None:
    before = _measurement(page_count=359, chapter_opening_false_folio=3)
    after = _measurement(chapter_opening_false_folio=1)

    row = gate.compare("eleve", before, after, _docket())

    assert row["CHAPTER_OPENING_FALSE_FOLIO_AFTER"] == 1
    assert row["REFUTED_CLAIMS"] == 1


def test_a_content_stream_that_moved_is_reported_on_all_three_counts() -> None:
    """Perte, doublon et réordonnancement changent le même condensat."""

    before = _measurement(page_count=359, chapter_opening_false_folio=3)
    after = _measurement(content_stream_sha256="b" * 64)

    row = gate.compare("eleve", before, after, _docket())

    assert row["CONTENT_STREAM_CONSERVED"] is False
    assert row["MISSING_CONTENT"] == 1
    assert row["DUPLICATED_CONTENT"] == 1
    assert row["UNEXPECTED_REORDERING"] == 1


def test_an_undeclared_blank_page_is_unintentional() -> None:
    before = _measurement(page_count=359, chapter_opening_false_folio=3)
    after = _measurement(blank_pages=[2, 200])

    row = gate.compare("eleve", before, after, _docket())

    assert row["UNINTENTIONAL_BLANK_PAGE"] == 1
    undocumented = [
        item for item in row["blank_pages"] if not item["documented"]
    ]
    assert [item["page"] for item in undocumented] == [200]
    assert undocumented[0]["reason"] == "UNDOCUMENTED"


def test_a_reason_kept_for_a_page_that_is_no_longer_blank_is_stale() -> None:
    before = _measurement(page_count=359, chapter_opening_false_folio=3)
    after = _measurement(blank_pages=[])

    row = gate.compare("eleve", before, after, _docket())

    assert row["STALE_BLANK_PAGE_REASONS"] == 1
    assert row["stale_blank_page_reasons"] == [2]


def test_a_blank_page_created_by_the_change_is_not_hidden_by_its_reason() -> None:
    """Une page blanche déclarée mais nouvelle doit rester visible comme telle."""

    before = _measurement(page_count=359, chapter_opening_false_folio=3, blank_pages=[])
    after = _measurement(blank_pages=[2])

    row = gate.compare("eleve", before, after, _docket())

    assert row["blank_pages"][0]["already_blank_before"] is False


def test_the_dehyphenation_only_repairs_a_line_break() -> None:
    assert (
        gate.dehyphenate("Probabilités condition- nelles et indépendance")
        == "Probabilités conditionnelles et indépendance"
    )
    # Une valeur déjà recollée est un point fixe.
    assert (
        gate.dehyphenate("Probabilités conditionnelles et indépendance")
        == "Probabilités conditionnelles et indépendance"
    )
    # Un trait d'union non suivi d'une espace est conservé : c'est le cas qui
    # rendrait l'oracle faux, et le producteur le signale comme bloquant.
    assert gate.dehyphenate("Al-Kashi") == "Al-Kashi"


def test_the_producer_refuses_to_run_without_a_human_decision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(gate, "docket_paths", lambda: [])

    with pytest.raises(gate.RatificationError, match="aucune décision humaine"):
        gate.load_docket()


def test_two_competing_decisions_are_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deux dockets concurrents : le producteur refuse d'en choisir un."""

    audit = ROOT / "audit"
    first = audit / "HUMAN_DECISION_1SPE_VISUAL_BASELINE_PAGINATION_1970-01-01.json"
    second = audit / "HUMAN_DECISION_1SPE_VISUAL_BASELINE_PAGINATION_1970-01-02.json"
    assert not first.exists() and not second.exists()
    monkeypatch.setattr(gate, "docket_paths", lambda: [first, second])

    with pytest.raises(gate.RatificationError, match="plusieurs décisions"):
        gate.load_docket()
