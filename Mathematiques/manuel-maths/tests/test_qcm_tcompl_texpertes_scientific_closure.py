"""Régressions scientifiques des 73 QCM TCOMPL et Math expertes."""

from __future__ import annotations

import json

import _qcm_par_contenu as _par_contenu
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
    q3 = _question("TCOMPL-ECHANTILLONNAGE", "Q3")
    assert q3["correcte"] == _par_contenu.lettre_de_option(q3, "3/8")
    q4 = _question("TCOMPL-ECHANTILLONNAGE", "Q4")
    assert q4["correcte"] == _par_contenu.lettre_de_option(q4, "7/8")


def test_inegalites_evalue_lorenz_et_gini_sans_theoremes_hors_programme() -> None:
    data = _data("TCOMPL-INEGALITES")
    corpus = json.dumps(data, ensure_ascii=False).lower()

    assert not any(term in corpus for term in ("tcheby", "markov", "grands nombres"))
    assert "lorenz" in corpus
    assert "gini" in corpus
    q5 = _question("TCOMPL-INEGALITES", "Q5")
    assert q5["correcte"] == _par_contenu.lettre_de_option(q5, "$1/3$")


def test_graphes_reste_sur_adjacence_et_puissances_de_matrice() -> None:
    data = _data("TEXP-GRAPHES")
    corpus = json.dumps(data, ensure_ascii=False).lower()

    assert "euler" not in corpus
    assert "dijkstra" not in corpus
    assert _question("TEXP-GRAPHES", "Q3")["capacite"] == "C3"
    assert _question("TEXP-GRAPHES", "Q5")["capacite"] == "C5"


def test_les_questions_reconstruites_restent_univoques() -> None:
    # L'identite scientifique de la reponse est sa VALEUR : la politique de
    # distribution des cles rend la lettre mobile, la valeur reste.
    expected_answers = {
        ("TCOMPL-ECHANTILLONNAGE", "Q1"): "la loi binomiale $\\mathcal B(n,p)$",
        ("TCOMPL-ECHANTILLONNAGE", "Q2"): (
            "$\\binom{n}{k}=\\binom{n-1}{k-1}+\\binom{n-1}{k}$"
        ),
        ("TCOMPL-ECHANTILLONNAGE", "Q3"): "$3/8$",
        ("TCOMPL-ECHANTILLONNAGE", "Q4"): "$7/8$",
        ("TCOMPL-ECHANTILLONNAGE", "Q5"): (
            "sum(random() < p for _ in range(n)) / n"
        ),
        ("TCOMPL-INEGALITES", "Q1"): (
            "la part cumulée de population $x$ et la part cumulée de richesse "
            "$L(x)$"
        ),
        ("TCOMPL-INEGALITES", "Q2"): "convexe et au-dessous de la droite $y=x$",
        ("TCOMPL-INEGALITES", "Q3"): "une répartition presque égalitaire",
        ("TCOMPL-INEGALITES", "Q4"): "$L''(x)\\geq0$",
        ("TCOMPL-INEGALITES", "Q5"): "$1/3$",
        ("TCOMPL-MODELES-EVOLUTION", "Q2"): "$1/(1-q)$",
        ("TCOMPL-MODELES-EVOLUTION", "Q5"): "$50$",
        ("TEXP-COMPLEXES-ALGEBRE-GEOMETRIE", "Q5"): "$\\bar z\\,\\bar w$",
        ("TEXP-COMPLEXES-TRIGO-POLYNOMES", "Q5"): "$z-a$ divise $P(z)$",
        ("TEXP-GRAPHES", "Q3"): "symétrique avec diagonale nulle",
        ("TEXP-GRAPHES", "Q5"): (
            "car $\\sum_k(M^n)_{ik}M_{kj}$ classe les chemins selon "
            "l'avant-dernier sommet $k$"
        ),
        ("TEXP-MATRICES-MARKOV", "Q4"): "$(I-A)U=C$",
    }
    for (chapter, question_id), answer in expected_answers.items():
        question = _question(chapter, question_id)
        assert question["options"][question["correcte"]] == answer, (
            f"{chapter}/{question_id}"
        )


def test_les_logarithmes_et_divisibilites_annoncent_leurs_domaines() -> None:
    linearisation = _question("TCOMPL-CORRELATION-CAUSALITE", "Q3")["enonce"]
    puissance = _question("TCOMPL-LOGARITHME-HISTORIQUE", "Q5")["enonce"]
    divisibilite = _question("TEXP-ARITHMETIQUE", "Q1")["enonce"]

    assert "$A>0$" in linearisation and "$x>0$" in linearisation
    assert "$a>0$" in puissance
    assert "a, b et c entiers" in divisibilite
