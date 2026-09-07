"""L'audit des fiches méthode doit refuser le remplissage et l'exemption facile.

Deux erreurs symétriques le menacent. Écrire une fiche par chapitre pour
atteindre 10/10 : du remplissage. Déclarer un chapitre exempt parce qu'un mot
manque d'une liste : une exemption fabriquée — c'est ce qu'une première
version faisait, en classant `TNSI-ALGORITHMIQUE` entièrement déclaratif alors
qu'il demande de parcourir un arbre en ordre infixe.

Le jugement est éditorial et déclaré. Ces tests vérifient qu'il reste
vérifiable : couvrant, sans trou, sans fiche inutile, et rouge dès qu'on
tente l'une des deux erreurs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_method_sheet_requirement_audit as audit  # noqa: E402
import method_sheet_decisions as decisions  # noqa: E402

ARTIFACT = ROOT / "audit/METHOD_SHEET_REQUIREMENT_AUDIT.json"


@pytest.fixture(scope="module")
def payload():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_the_audit_covers_every_chapter_that_owes_a_method(payload) -> None:
    """Vingt-cinq chapitres, pas dix : les cinq autres manuels sont jugés."""
    juges = {row["chapter"] for row in payload["chapters"]}
    assert juges == set(decisions.CAPACITY_VERDICTS)
    assert len(juges) == 25
    manuels = {c.split("-")[0] for c in juges}
    assert manuels == {"1NSI", "TNSI", "1SPE", "TCOMPL", "TSPE"}


def test_every_declared_capacity_has_a_verdict(payload) -> None:
    for row in payload["chapters"]:
        contract = yaml.safe_load(
            (ROOT / audit.chapter_directory(row["chapter"]) / "contrat.yaml")
            .read_text(encoding="utf-8")
        )
        declared = {c["code"] for c in contract["capacites"]}
        judged = {c["code"] for c in row["capacities"]}
        assert judged == declared, row["chapter"]


def test_a_capacity_without_a_decision_fails_the_build(monkeypatch) -> None:
    """Ajouter une capacité au contrat ne doit pas passer inaperçu."""
    trimmed = dict(decisions.CAPACITY_VERDICTS)
    trimmed["1NSI-TABLES"] = {
        k: v for k, v in trimmed["1NSI-TABLES"].items() if k != "C4"
    }
    monkeypatch.setattr(audit, "CAPACITY_VERDICTS", trimmed)
    with pytest.raises(ValueError, match="capacites sans decision"):
        audit.audit_chapter(ROOT, ROOT / "NSI/chapitres/1NSI-TABLES")


def test_a_sheet_serving_no_needed_capacity_is_refused(monkeypatch) -> None:
    """Une fiche qui ne sert aucune démarche manquante est du remplissage."""
    padded = dict(decisions.PLANNED_SHEETS)
    padded["1NSI-TYPES-BASE"] = [
        *padded["1NSI-TYPES-BASE"],
        ("M9", "Fiche de remplissage", ("C3",)),
    ]
    monkeypatch.setattr(audit, "PLANNED_SHEETS", padded)
    with pytest.raises(ValueError, match="n'appellent"):
        audit.audit_chapter(ROOT, ROOT / "NSI/chapitres/1NSI-TYPES-BASE")


def test_an_unserved_procedural_capacity_is_refused(monkeypatch) -> None:
    """Une démarche manquante sans fiche planifiée doit bloquer."""
    stripped = dict(decisions.PLANNED_SHEETS)
    stripped["1NSI-TABLES"] = stripped["1NSI-TABLES"][:-1]
    monkeypatch.setattr(audit, "PLANNED_SHEETS", stripped)
    with pytest.raises(ValueError, match="sans fiche planifiee"):
        audit.audit_chapter(ROOT, ROOT / "NSI/chapitres/1NSI-TABLES")


def test_a_coverage_claim_must_name_a_file_that_exists(monkeypatch) -> None:
    """« Déjà couvert » sans objet nommé serait une exemption gratuite."""
    forged = dict(decisions.CAPACITY_VERDICTS)
    chapter = dict(forged["1NSI-PROJET-METHODES"])
    chapter["C3"] = (
        decisions.PROCEDURAL_COVERED, "prétendu couvert", "NSI/chapitres/inexistant.tex",
    )
    forged["1NSI-PROJET-METHODES"] = chapter
    monkeypatch.setattr(audit, "CAPACITY_VERDICTS", forged)
    with pytest.raises(ValueError, match="absent du depot"):
        audit.audit_chapter(ROOT, ROOT / "NSI/chapitres/1NSI-PROJET-METHODES")


def test_every_coverage_claim_points_at_a_written_procedure(payload) -> None:
    """« Déjà couvert » doit désigner un objet qui écrit vraiment la démarche.

    Ce test visait la seule revendication hors des chapitres pourvus, tant que
    les sept autres chapitres étaient vides. Ils ne le sont plus. Il vérifie
    donc la règle : toute revendication nomme un chemin existant, et la
    revendication qui porte sur un objet précis — la démarche de débogage —
    désigne un fichier où la suite d'étapes est réellement écrite.
    """
    claims = [
        (row["chapter"], c["code"], c["covered_by"])
        for row in payload["chapters"]
        for c in row["capacities"]
        if c["verdict"] == decisions.PROCEDURAL_COVERED
    ]
    assert claims, "aucune revendication : le test ne prouverait rien"
    for _, _, covered_by in claims:
        assert covered_by, "une couverture sans objet nommé serait gratuite"
        assert (ROOT / covered_by).exists(), covered_by

    debugging = next(
        c for chapter, code, c in claims
        if (chapter, code) == ("1NSI-PROJET-METHODES", "C3")
    )
    assert debugging == \
        "NSI/chapitres/1NSI-PROJET-METHODES/cours/1NSI-PM-COURS-C3.tex"
    text = (ROOT / debugging).read_text(encoding="utf-8")
    assert "Démarche méthodique de débogage" in text
    assert "\\begin{enumerate}" in text


def test_no_filler_object(payload) -> None:
    assert payload["summary"]["METHOD_BOOKLET_FILLER_OBJECTS"] == 0


def test_sheets_never_serve_the_same_capacity_twice(payload) -> None:
    for row in payload["chapters"]:
        served = [c for sheet in row["planned_sheets"] for c in sheet["covers"]]
        assert len(served) == len(set(served)), row["chapter"]


def test_the_audit_declares_its_freshness(payload) -> None:
    import evidence_freshness as freshness

    assert freshness.assess(payload["freshness"])["FRESHNESS_STATUS"] == \
        freshness.CURRENT
