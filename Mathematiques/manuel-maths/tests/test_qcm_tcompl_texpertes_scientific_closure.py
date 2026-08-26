"""Régressions scientifiques des 73 QCM TCOMPL et Math expertes."""

from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


EXPECTED = {
    "TCOMPL-CALCULS-AIRES": ["C5", "C4", "C1", "C3", "C2", "C6"],
    "TCOMPL-CORRELATION-CAUSALITE": ["C2", "C2", "C3", "C4", "C5", "C5", "C1"],
    "TCOMPL-ECHANTILLONNAGE": ["C1", "C2", "C3", "C4", "C5"],
    "TCOMPL-INEGALITES": ["C1", "C2", "C3", "C4", "C5"],
    "TCOMPL-INFERENCE-BAYESIENNE": ["C2", "C1", "C1", "C3", "C4"],
    "TCOMPL-LOGARITHME-HISTORIQUE": ["C1", "C2", "C5", "C1", "C3"],
    "TCOMPL-MODELES-EVOLUTION": ["C1", "C2", "C5", "C5", "C4"],
    "TCOMPL-MODELES-FONCTION": ["C1", "C5", "C4", "C1", "C1"],
    "TCOMPL-TEMPS-ATTENTE": ["C1", "C2", "C3", "C2", "C1"],
    "TEXP-ARITHMETIQUE": ["C1", "C1", "C1", "C5", "C2"],
    "TEXP-COMPLEXES-ALGEBRE-GEOMETRIE": ["C1", "C1", "C4", "C4", "C3"],
    "TEXP-COMPLEXES-TRIGO-POLYNOMES": ["C1", "C2", "C2", "C7", "C5"],
    "TEXP-GRAPHES": ["C1", "C1", "C3", "C4", "C5"],
    "TEXP-MATRICES-MARKOV": ["C4", "C5", "C7", "C3", "C1"],
}


def _data(chapter: str) -> dict:
    source = ROOT / "chapitres" / chapter / "qcm" / f"{chapter}-QCM.json"
    return json.loads(source.read_text(encoding="utf-8"))


def _question(chapter: str, question_id: str) -> dict:
    return next(q for q in _data(chapter)["questions"] if q["id"] == question_id)


def test_les_73_questions_sont_rattachees_a_leur_capacite_reelle() -> None:
    assert sum(len(capacities) for capacities in EXPECTED.values()) == 73
    for chapter, capacities in EXPECTED.items():
        questions = _data(chapter)["questions"]
        assert [q["capacite"] for q in questions] == capacities
        contract = yaml.safe_load(
            (ROOT / "chapitres" / chapter / "contrat.yaml").read_text(encoding="utf-8")
        )
        contract_codes = {capacity["code"] for capacity in contract["capacites"]}
        assert set(capacities) <= contract_codes


def test_les_219_distracteurs_portent_un_modele_derreur_specifique() -> None:
    diagnostics = []
    for chapter in EXPECTED:
        for question in _data(chapter)["questions"]:
            assert question["correcte"] in question["options"]
            assert set(question["diagnostics"]) == set(question["options"]) - {
                question["correcte"]
            }
            diagnostics.extend(
                diagnostic["erreur"] for diagnostic in question["diagnostics"].values()
            )
    assert len(diagnostics) == 219
    assert all(len(error) >= 60 for error in diagnostics)
    assert all("Consulter le cours" not in error for error in diagnostics)


def test_echantillonnage_reste_sur_les_objets_binomiaux_du_programme() -> None:
    data = _data("TCOMPL-ECHANTILLONNAGE")
    corpus = json.dumps(
        [
            {"enonce": question["enonce"], "options": question["options"]}
            for question in data["questions"]
        ],
        ensure_ascii=False,
    ).lower()

    assert not any(term in corpus for term in ("intervalle de confiance", "approximation normale", "estimateur"))
    assert _question("TCOMPL-ECHANTILLONNAGE", "Q3")["correcte"] == "B"
    assert "3/8" in _question("TCOMPL-ECHANTILLONNAGE", "Q3")["options"]["B"]
    assert _question("TCOMPL-ECHANTILLONNAGE", "Q4")["correcte"] == "D"
    assert "7/8" in _question("TCOMPL-ECHANTILLONNAGE", "Q4")["options"]["D"]


def test_inegalites_evalue_lorenz_et_gini_sans_theoremes_hors_programme() -> None:
    data = _data("TCOMPL-INEGALITES")
    corpus = json.dumps(data, ensure_ascii=False).lower()

    assert not any(term in corpus for term in ("tcheby", "markov", "grands nombres"))
    assert "lorenz" in corpus
    assert "gini" in corpus
    assert _question("TCOMPL-INEGALITES", "Q5")["correcte"] == "B"
    assert _question("TCOMPL-INEGALITES", "Q5")["options"]["B"] == "$1/3$"


def test_graphes_reste_sur_adjacence_et_puissances_de_matrice() -> None:
    data = _data("TEXP-GRAPHES")
    corpus = json.dumps(data, ensure_ascii=False).lower()

    assert "euler" not in corpus
    assert "dijkstra" not in corpus
    assert _question("TEXP-GRAPHES", "Q3")["capacite"] == "C3"
    assert _question("TEXP-GRAPHES", "Q5")["capacite"] == "C5"


def test_les_questions_reconstruites_restent_univoques() -> None:
    expected_answers = {
        ("TCOMPL-ECHANTILLONNAGE", "Q1"): "B",
        ("TCOMPL-ECHANTILLONNAGE", "Q2"): "C",
        ("TCOMPL-ECHANTILLONNAGE", "Q3"): "B",
        ("TCOMPL-ECHANTILLONNAGE", "Q4"): "D",
        ("TCOMPL-ECHANTILLONNAGE", "Q5"): "A",
        ("TCOMPL-INEGALITES", "Q1"): "B",
        ("TCOMPL-INEGALITES", "Q2"): "C",
        ("TCOMPL-INEGALITES", "Q3"): "A",
        ("TCOMPL-INEGALITES", "Q4"): "C",
        ("TCOMPL-INEGALITES", "Q5"): "B",
        ("TCOMPL-MODELES-EVOLUTION", "Q2"): "B",
        ("TCOMPL-MODELES-EVOLUTION", "Q5"): "C",
        ("TEXP-COMPLEXES-ALGEBRE-GEOMETRIE", "Q5"): "D",
        ("TEXP-COMPLEXES-TRIGO-POLYNOMES", "Q5"): "A",
        ("TEXP-GRAPHES", "Q3"): "B",
        ("TEXP-GRAPHES", "Q5"): "C",
        ("TEXP-MATRICES-MARKOV", "Q4"): "B",
    }
    for (chapter, question_id), answer in expected_answers.items():
        assert _question(chapter, question_id)["correcte"] == answer


def test_les_logarithmes_et_divisibilites_annoncent_leurs_domaines() -> None:
    linearisation = _question("TCOMPL-CORRELATION-CAUSALITE", "Q3")["enonce"]
    puissance = _question("TCOMPL-LOGARITHME-HISTORIQUE", "Q5")["enonce"]
    divisibilite = _question("TEXP-ARITHMETIQUE", "Q1")["enonce"]

    assert "$A>0$" in linearisation and "$x>0$" in linearisation
    assert "$a>0$" in puissance
    assert "a, b et c entiers" in divisibilite
