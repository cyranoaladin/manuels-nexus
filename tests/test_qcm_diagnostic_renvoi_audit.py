"""Un vérificateur qui trouve zéro doit d'abord prouver qu'il sait trouver.

Cet audit annonce `BROKEN_REMEDIATION_REFERENCES = 0` sur 1470 renvois. Un
compteur à zéro du premier coup est exactement celui qu'il faut mettre à
l'épreuve : ces tests cassent délibérément chaque forme de renvoi et exigent
que le producteur le voie.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_qcm_diagnostic_renvoi_audit as audit  # noqa: E402

ARTIFACT = ROOT / "audit/QCM_DIAGNOSTIC_RENVOI_AUDIT.json"


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_the_audit_approves_nothing(payload) -> None:
    assert payload["approves_nothing"] is True


def test_every_renvoi_is_accounted_for(payload) -> None:
    s = payload["summary"]
    assert s["QCM_DIAGNOSTIC_RENVOI_POPULATION"] == len(payload["renvois"])
    assert (
        s["QCM_DIAGNOSTIC_RENVOI_RESOLVED"] + s["QCM_DIAGNOSTIC_MISMATCH"]
        == s["QCM_DIAGNOSTIC_RENVOI_POPULATION"]
    )


def test_the_deposited_audit_is_clean(payload) -> None:
    assert payload["summary"]["BROKEN_REMEDIATION_REFERENCES"] == 0
    assert payload["summary"]["QCM_DIAGNOSTIC_MISMATCH"] == 0
    assert payload["defects"] == []


def _depot_jouet(tmp_path: Path, renvoi: str, *, avec_methode=True,
                 avec_remediation=True, avec_cours=True) -> Path:
    chapitre = tmp_path / "Mathematiques/manuel-maths/chapitres/XTEST-CHAP"
    (chapitre / "qcm").mkdir(parents=True)
    (chapitre / "contrat.yaml").write_text(
        "chapitre: XTEST-CHAP\ncapacites:\n  - {code: C1, libelle_eleve: x}\n",
        encoding="utf-8",
    )
    if avec_cours:
        (chapitre / "cours").mkdir()
        (chapitre / "cours/10_C1.tex").write_text(
            '% META: {"id": "X-CR-1", "type_objet": "cours"}\n', encoding="utf-8"
        )
    if avec_methode:
        (chapitre / "methodes").mkdir()
        (chapitre / "methodes/X-ME-001.tex").write_text(
            '% META: {"id": "X-ME-001", "type_objet": "methode"}\n'
            "\\begin{fichemethode}{M1}{titre}\n\\end{fichemethode}\n",
            encoding="utf-8",
        )
    if avec_remediation:
        (chapitre / "remediation").mkdir()
        (chapitre / "remediation/X-FR-R1.tex").write_text(
            '% META: {"id": "X-FR-R1", "type_objet": "remediation"}\n',
            encoding="utf-8",
        )
    (chapitre / "qcm/XTEST-CHAP-QCM.json").write_text(
        json.dumps({
            "chapitre": "XTEST-CHAP",
            "questions": [{
                "id": "Q1", "capacite": "C1", "enonce": "x",
                "options": {"A": "a", "B": "b"}, "correcte": "A",
                "diagnostics": {"B": {"erreur": "…", "renvoi": renvoi}},
            }],
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    (tmp_path / "NSI/chapitres").mkdir(parents=True)
    return tmp_path


_compteur = [0]


def _etat(tmp_path: Path, renvoi: str, **kwargs) -> tuple[str, str | None]:
    # Un dépôt jouet neuf par appel : plusieurs renvois sont éprouvés dans un
    # même test, et ils ne doivent pas se marcher dessus.
    _compteur[0] += 1
    racine = _depot_jouet(tmp_path / f"depot{_compteur[0]}", renvoi, **kwargs)
    resultat = audit.build(racine)
    ligne = resultat["renvois"][0]
    return ligne["state"], ligne["detail"]


def test_a_capacity_absent_from_the_contract_is_seen(tmp_path) -> None:
    etat, detail = _etat(tmp_path, "C99, notion inventée")
    assert etat == "BROKEN"
    assert "C99" in detail


def test_a_method_sheet_absent_from_the_chapter_is_seen(tmp_path) -> None:
    etat, detail = _etat(tmp_path, "M9, étape 2")
    assert etat == "BROKEN"
    assert "M9" in detail


def test_a_method_renvoi_is_broken_when_the_chapter_has_none(tmp_path) -> None:
    etat, detail = _etat(tmp_path, "M1", avec_methode=False)
    assert etat == "BROKEN"


def test_a_remediation_absent_from_the_chapter_is_seen(tmp_path) -> None:
    etat, detail = _etat(tmp_path, "R7")
    assert etat == "BROKEN"
    assert "R7" in detail


def test_a_course_renvoi_is_broken_when_the_chapter_has_none(tmp_path) -> None:
    etat, _ = _etat(tmp_path, "Cours, définition", avec_cours=False)
    assert etat == "BROKEN"


def test_an_unknown_form_is_not_silently_accepted(tmp_path) -> None:
    etat, detail = _etat(tmp_path, "voir le manuel page 42")
    assert etat == "UNKNOWN_FORM"
    assert "non reconnue" in detail


def test_a_missing_renvoi_is_seen(tmp_path) -> None:
    etat, detail = _etat(tmp_path, "")
    assert etat == "MISSING_RENVOI"


def test_a_compound_renvoi_needs_both_targets(tmp_path) -> None:
    """`M1 ; R9` doit échouer sur R9 même si M1 existe."""
    etat, detail = _etat(tmp_path, "M1 ; R9")
    assert etat == "BROKEN"
    assert "R9" in detail
    # Et le composé entièrement valide passe.
    etat_valide, _ = _etat(tmp_path, "M1 ; R1")
    assert etat_valide == "RESOLVED"


def test_a_valid_renvoi_of_each_form_resolves(tmp_path) -> None:
    for renvoi in ("C1", "C1, définition", "M1", "R1", "RE-C1", "Cours, D2"):
        etat, detail = _etat(tmp_path, renvoi)
        assert etat == "RESOLVED", (renvoi, detail)


def test_an_unjudged_cross_capacity_renvoi_stops_the_build(tmp_path) -> None:
    """Un renvoi croisé sans justification déposée doit faire échouer."""
    racine = tmp_path / "depot"
    racine.mkdir()
    chapitre = racine / "Mathematiques/manuel-maths/chapitres/XTEST-CHAP"
    (chapitre / "qcm").mkdir(parents=True)
    (chapitre / "contrat.yaml").write_text(
        "chapitre: XTEST-CHAP\ncapacites:\n"
        "  - {code: C1, libelle_eleve: x}\n  - {code: C2, libelle_eleve: y}\n",
        encoding="utf-8",
    )
    (chapitre / "qcm/XTEST-CHAP-QCM.json").write_text(
        json.dumps({
            "chapitre": "XTEST-CHAP",
            "questions": [{
                "id": "Q1", "capacite": "C1", "enonce": "x",
                "options": {"A": "a", "B": "b"}, "correcte": "A",
                "diagnostics": {"B": {"erreur": "…", "renvoi": "C2"}},
            }],
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    (racine / "NSI/chapitres").mkdir(parents=True)
    with pytest.raises(ValueError, match="renvoi croisé non jugé"):
        audit.build(racine)


def test_every_cross_capacity_renvoi_carries_its_reason(payload) -> None:
    croises = payload["cross_capacity"]
    assert croises, "le corpus en porte, et ils doivent être jugés"
    for ligne in croises:
        assert ligne["justification"], ligne
        assert len(ligne["justification"]) > 60, ligne
