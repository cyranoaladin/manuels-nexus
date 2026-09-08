"""Le triage des unités de rôle ne doit ni perdre un item, ni en inventer.

Le Release Owner a refusé l'interprétation « 441 unités GAP = 441 objets à
écrire ». Ce triage juge chaque unité sur son applicabilité réelle. Deux
dangers l'encadrent : perdre des items en route, et fabriquer des exemptions
que la preuve ne soutient pas.
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_pedagogical_role_applicability as audit  # noqa: E402

ARTIFACT = ROOT / "audit/PEDAGOGICAL_ROLE_APPLICABILITY_AUDIT.json"


@pytest.fixture(scope="module")
def payload():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_no_item_is_lost(payload) -> None:
    s = payload["summary"]
    somme = sum(s[v] for v in audit.VERDICTS)
    assert somme == s["PEDAGOGICAL_ROLE_UNITS_TOTAL"] == len(payload["units"])
    assert s["NO_ITEM_LOST"] is True


def test_only_the_five_named_verdicts_exist(payload) -> None:
    """« Aucune autre catégorie », dit la décision."""
    vus = {u["APPLICABILITY_VERDICT"] for u in payload["units"]}
    assert vus <= set(audit.VERDICTS)
    assert set(audit.VERDICTS) == {
        "SATISFIED_BY_EXISTING_CONTENT", "SATISFIED_TRANSVERSALLY",
        "BAD_MAPPING", "ROLE_NOT_APPLICABLE", "REAL_PEDAGOGICAL_GAP",
    }


def test_every_unit_carries_the_named_fields(payload) -> None:
    exiges = {
        "MANUAL", "CHAPTER", "CAPACITY", "ROLE", "CURRENT_OBJECTS",
        "TRANSVERSAL_OBJECTS", "REQUIREMENT_SOURCE", "APPLICABILITY_VERDICT",
        "RATIONALE",
    }
    for unit in payload["units"]:
        assert exiges <= set(unit), unit
        assert unit["RATIONALE"], unit


def test_the_default_verdict_is_the_gap(payload) -> None:
    """Une cellule qu'aucune règle ne couvre reste une lacune."""
    assert payload["default_verdict"] == "REAL_PEDAGOGICAL_GAP"


def test_a_transversal_verdict_always_names_objects(payload) -> None:
    """La transversalité ne peut pas couvrir une absence."""
    for unit in payload["units"]:
        if unit["APPLICABILITY_VERDICT"] == "SATISFIED_TRANSVERSALLY":
            assert unit["TRANSVERSAL_OBJECTS"], unit


def test_bad_mapping_is_empty_and_that_is_stated(payload) -> None:
    """Aucune règle ne l'assigne : la catégorie reste vide, et c'est écrit.

    Une première tentative en produisait 64 en confondant les types canoniques
    au singulier avec les rôles au pluriel, et en traitant tout exercice
    déclarant une capacité comme la preuve d'une fiche méthode mal cartographiée.
    Mieux vaut une catégorie vide qu'une catégorie remplie sans preuve.
    """
    assert payload["summary"]["BAD_MAPPING"] == 0
    source = (ROOT / "scripts/build_pedagogical_role_applicability.py").read_text(
        encoding="utf-8"
    )
    assert "BAD_MAPPING` n'est assigne par aucune regle" in source


def test_the_qcm_exemption_cites_a_deposited_policy(payload) -> None:
    """L'exemption QCM ne s'invoque jamais sans citer la politique deposee.

    Le corpus ne porte plus aucune unite de role `qcm` : toutes les cellules
    QCM sont couvertes, il n'y a donc plus rien a exempter. Une population
    vide ne prouve pourtant pas que la regle tient encore -- on verifie donc
    qu'elle existe dans le producteur, que la politique est bien deposee, et
    que toute unite `qcm` qui reapparaitrait la citerait.
    """

    politique = "audit/QCM_POLICY_ORIGIN.md"
    assert (ROOT / politique).is_file()
    source = (ROOT / "scripts/build_pedagogical_role_applicability.py").read_text(
        encoding="utf-8"
    )
    assert politique in source
    for unit in payload["units"]:
        if unit["ROLE"] != "qcm":
            continue
        assert unit["APPLICABILITY_VERDICT"] == "ROLE_NOT_APPLICABLE"
        assert unit["REQUIREMENT_SOURCE"] == politique


def test_no_correction_is_owed_without_a_source_object(payload) -> None:
    """« Pas de corrigé artificiel sans objet source. »"""
    for unit in payload["units"]:
        if unit["ROLE"] != "corriges":
            continue
        couvert = set(unit["capacity_covered_by_roles"])
        if not ({"exercices", "evaluations"} & couvert):
            assert unit["APPLICABILITY_VERDICT"] in (
                "ROLE_NOT_APPLICABLE", "SATISFIED_BY_EXISTING_CONTENT",
            ), unit


def test_the_project_chapter_is_excused_by_its_assessment_mode(payload) -> None:
    projet = [
        u for u in payload["units"]
        if u["CHAPTER"] == "TNSI-PROJET"
    ]
    assert projet
    for unit in projet:
        assert unit["APPLICABILITY_VERDICT"] == "ROLE_NOT_APPLICABLE"
        assert "PROJECT_ASSESSMENT" in unit["RATIONALE"]


def test_the_method_verdicts_are_read_not_recomputed(payload) -> None:
    """Les fiches méthode 1NSI ont déjà leur verdict : on le lit."""
    unites = [
        u for u in payload["units"]
        if u["MANUAL"] == "1NSI" and u["ROLE"] == "methodes"
    ]
    assert unites
    for unit in unites:
        assert unit["APPLICABILITY_VERDICT"] != "REAL_PEDAGOGICAL_GAP", unit
        assert unit["REQUIREMENT_SOURCE"] == \
            "audit/METHOD_SHEET_REQUIREMENT_AUDIT.json"


def test_the_remaining_gaps_are_concentrated_and_nameable(payload) -> None:
    """Ce qui reste doit être petit, localisé, et attribuable.

    Une version antérieure exigeait qu'il RESTE des lacunes, pour attraper un
    triage qui exempterait tout. Elles sont maintenant toutes fermées — par
    jugement éditorial pour la plupart, par écriture pour les autres — et cette
    exigence n'a plus de sens. La pression qu'elle exerçait est reprise par les
    deux tests suivants, qui vérifient que chaque exemption s'appuie sur une
    preuve nommée.
    """
    gaps = [
        u for u in payload["units"]
        if u["APPLICABILITY_VERDICT"] == "REAL_PEDAGOGICAL_GAP"
    ]
    roles = collections.Counter(u["ROLE"] for u in gaps)
    assert set(roles) <= {"methodes", "cours", "exercices", "evaluations",
                          "remediation"}, dict(roles)
    chapitres = {u["CHAPTER"] for u in gaps}
    assert len(chapitres) <= 20, sorted(chapitres)


def test_no_verdict_exempts_without_naming_its_ground(payload) -> None:
    """Une exemption sans preuve nommée est une exemption fabriquée."""
    for unit in payload["units"]:
        verdict = unit["APPLICABILITY_VERDICT"]
        if verdict == "REAL_PEDAGOGICAL_GAP":
            continue
        assert unit["RATIONALE"], unit
        assert unit["REQUIREMENT_SOURCE"], unit
        if verdict == "SATISFIED_BY_EXISTING_CONTENT":
            assert unit["CURRENT_OBJECTS"] or unit["TRANSVERSAL_OBJECTS"], unit
        if verdict == "SATISFIED_TRANSVERSALLY":
            assert unit["TRANSVERSAL_OBJECTS"], unit


def test_every_method_exemption_rests_on_a_deposited_editorial_verdict(
    payload,
) -> None:
    """Aucune fiche méthode n'est excusée sans verdict écrit.

    C'est ici que se joue le risque d'exemption facile : déclarer une capacité
    « non applicable » pour n'avoir pas à écrire la fiche. Chaque exemption doit
    renvoyer à un verdict déposé, et chaque couverture doit nommer un fichier
    qui existe.
    """
    from method_sheet_decisions import (
        CAPACITY_VERDICTS, DECLARATIVE, PROCEDURAL_COVERED,
    )

    exemptees = [
        u for u in payload["units"]
        if u["ROLE"] == "methodes"
        and u["REQUIREMENT_SOURCE"] == "audit/METHOD_SHEET_REQUIREMENT_AUDIT.json"
    ]
    assert exemptees, "le triage doit lire les verdicts déposés"
    for unit in exemptees:
        verdict, _, couvrant = CAPACITY_VERDICTS[unit["CHAPTER"]][unit["CAPACITY"]]
        if unit["APPLICABILITY_VERDICT"] == "ROLE_NOT_APPLICABLE":
            assert verdict == DECLARATIVE, unit
        else:
            assert verdict == PROCEDURAL_COVERED, unit
            assert couvrant and (ROOT / couvrant).exists(), unit


def test_a_capacity_taught_nowhere_is_not_covered_transversally(payload) -> None:
    """La transversalité couvre une déclaration incomplète, pas une absence.

    Les trois capacités concernées sont au contrat de leur chapitre et
    n'apparaissent dans aucun objet. Les créditer « transversalement » aurait
    désigné des objets qui ne les traitent pas.
    """
    orphelines = [
        u for u in payload["units"] if not u["capacity_covered_by_roles"]
    ]
    # La règle se retire d'elle-même : depuis que les trois capacités TCOMPL
    # sont enseignées, plus aucune cellule n'est orpheline. Le test vérifie
    # donc l'invariant, pas la présence d'une population.
    for unit in orphelines:
        assert unit["APPLICABILITY_VERDICT"] != "SATISFIED_TRANSVERSALLY", unit
        if unit["ROLE"] in {"cours", "exercices", "evaluations", "remediation"}:
            assert unit["APPLICABILITY_VERDICT"] == "REAL_PEDAGOGICAL_GAP"
            assert unit["REQUIREMENT_SOURCE"] == "ORPHAN_CAPACITY"


def test_a_transversal_verdict_never_rests_on_an_empty_chapter(payload) -> None:
    """Aucun verdict transversal ne peut porter sur une capacité orpheline."""
    for unit in payload["units"]:
        if unit["APPLICABILITY_VERDICT"] != "SATISFIED_TRANSVERSALLY":
            continue
        assert unit["capacity_covered_by_roles"], unit


def test_the_audit_declares_its_freshness(payload) -> None:
    import evidence_freshness as freshness

    assert freshness.assess(payload["freshness"])["FRESHNESS_STATUS"] == \
        freshness.CURRENT
