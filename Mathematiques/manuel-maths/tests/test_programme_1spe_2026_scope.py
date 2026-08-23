"""Régressions de périmètre pour le programme 1SPE applicable en 2026-2027.

Ces tests encodent l'arbitrage réglementaire explicite : le socle
trigonométrique de Première s'arrête au cercle, au radian et à la lecture de
sinus/cosinus. Les enrichissements conservés doivent être déclarés comme
extensions et rester hors des QCM et évaluations obligatoires.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "chapitres"
REFERENTIAL = ROOT / "referentiel"
META = re.compile(r"^% META: (\{.*\})", re.MULTILINE)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _meta(path: Path) -> dict:
    match = META.search(path.read_text(encoding="utf-8"))
    assert match, f"META absent: {path}"
    return json.loads(match.group(1))


def test_trigonometrie_socle_ne_contient_que_cercle_radian_sinus_cosinus() -> None:
    referential = _json(REFERENTIAL / "capacites_1SPE_TRIGONOMETRIE.json")
    contract = yaml.safe_load(
        (CHAPTERS / "1SPE-TRIGONOMETRIE/contrat.yaml").read_text(encoding="utf-8")
    )

    assert [item["id"] for item in referential["capacites"]] == [
        "1SPE-TRIGONOMETRIE-C1",
        "1SPE-TRIGONOMETRIE-C2",
    ]
    assert [item["code"] for item in contract["capacites"]] == ["C1", "C2"]
    assert {item["code"] for item in contract["extensions_facultatives"]} == {
        "X1",
        "X2",
        "X3",
    }
    assert all(
        item["programme_alignment"] == "OPTIONAL_EXTENSION"
        and item["label"] == "Approfondissement — Vers la Terminale"
        for item in contract["extensions_facultatives"]
    )


def test_trigonometrie_qcm_et_evaluations_restent_dans_le_socle() -> None:
    chapter = CHAPTERS / "1SPE-TRIGONOMETRIE"
    qcm = _json(chapter / "qcm/1SPE-TRIGONOMETRIE-QCM.json")
    assert len(qcm["questions"]) == 15
    assert {question["capacite"] for question in qcm["questions"]} <= {"C1", "C2"}

    for path in sorted((chapter / "evaluations").glob("*.tex")):
        meta = _meta(path)
        assert set(meta["capacites_codes"]) <= {"C1", "C2"}
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"(?:—|-) C[345]\b", text)


def test_trigonometrie_ressources_avancees_sont_des_extensions_explicitement_marquees() -> None:
    chapter = CHAPTERS / "1SPE-TRIGONOMETRIE"
    expected = {
        "methodes/1SPE-TRIGO-ME-003.tex": "X1",
        "methodes/1SPE-TRIGO-ME-004.tex": "X2",
        "methodes/1SPE-TRIGO-ME-005.tex": "X3",
        "exercices/1SPE-TRIGO-EX-019.tex": "X1",
        "corriges/1SPE-TRIGO-CO-019.tex": "X1",
        "exercices/1SPE-TRIGO-EX-024.tex": "X2",
        "exercices/1SPE-TRIGO-EX-024-CDP.tex": "X2",
        "corriges/1SPE-TRIGO-CO-024.tex": "X2",
    }
    for relative, extension_code in expected.items():
        path = chapter / relative
        meta = _meta(path)
        assert meta.get("capacites", []) == []
        assert meta.get("capacites_codes", []) == []
        assert meta["extension_codes"] == [extension_code]
        assert meta["programme_alignment"] == "OPTIONAL_EXTENSION"
        assert meta["extension_label"] == "Approfondissement — Vers la Terminale"
        assert "Approfondissement — Vers la Terminale" in path.read_text(
            encoding="utf-8"
        )

    curation = _json(chapter / "dossier_curation.json")
    assert set(curation["capacites"]) == {"C1", "C2", "X1", "X2", "X3"}
    assert all(
        curation["capacites"][code]["programme_alignment"]
        == "OPTIONAL_EXTENSION"
        and curation["capacites"][code]["extension_label"]
        == "Approfondissement — Vers la Terminale"
        and "format_examen" not in curation["capacites"][code]
        for code in ("X1", "X2", "X3")
    )


def test_exponentielle_referentiel_reproduit_les_capacites_2026() -> None:
    referential = _json(REFERENTIAL / "capacites_1SPE_EXPONENTIELLE.json")
    contract = yaml.safe_load(
        (CHAPTERS / "1SPE-EXPONENTIELLE/contrat.yaml").read_text(encoding="utf-8")
    )
    labels = [item["libelle_bo"] for item in referential["capacites"]]
    joined = " ".join(labels).lower()

    assert [item["id"] for item in referential["capacites"]] == [
        f"1SPE-EXPONENTIELLE-C{index}" for index in range(1, 6)
    ]
    assert "limite" not in joined
    assert "e^{u(x)}" not in joined
    assert "t → $e^{at}$" in labels[3]
    assert "modéliser" in labels[4].lower()
    assert [item["code"] for item in contract["capacites"]] == [
        f"C{index}" for index in range(1, 6)
    ]
    assert {item["code"] for item in contract["extensions_facultatives"]} == {
        "X1",
        "X2",
        "X3",
        "X4",
    }


def test_exponentielle_contract_math_is_delimited_for_latex_assembly() -> None:
    contract = yaml.safe_load(
        (CHAPTERS / "1SPE-EXPONENTIELLE/contrat.yaml").read_text(encoding="utf-8")
    )

    assert "t → $e^{at}$" in contract["capacites"][3]["libelle_eleve"]


def test_repetitions_bernoulli_uses_the_canonical_method_environment() -> None:
    source = (
        CHAPTERS
        / "1SPE-VARIABLES-ALEATOIRES/cours/12_C3_repetitions_bernoulli.tex"
    ).read_text(encoding="utf-8")

    assert "\\methode{" not in source
    assert "\\begin{methodeV}" in source
    assert "\\end{methodeV}" in source


def test_exponentielle_qcm_exclut_limites_et_derivation_generale() -> None:
    qcm = _json(CHAPTERS / "1SPE-EXPONENTIELLE/qcm/1SPE-EXPONENTIELLE-QCM.json")
    statements = " ".join(question["enonce"] for question in qcm["questions"])
    by_id = {question["id"]: question for question in qcm["questions"]}

    assert len(qcm["questions"]) == 15
    assert "limite" not in statements.lower()
    assert "e}^{x^2}" not in statements
    assert {question["capacite"] for question in qcm["questions"]} <= {
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
    }
    assert {
        question_id: by_id[question_id]["correcte"]
        for question_id in ("Q8", "Q10", "Q11", "Q12", "Q13", "Q14", "Q15")
    } == {
        "Q8": "C",
        "Q10": "C",
        "Q11": "C",
        "Q12": "C",
        "Q13": "B",
        "Q14": "B",
        "Q15": "B",
    }
    assert all(
        set(question["diagnostics"])
        == ({"A", "B", "C", "D"} - {question["correcte"]})
        for question in qcm["questions"]
    )


def test_exponentielle_parcours_obligatoire_exclut_le_programme_de_terminale() -> None:
    chapter = CHAPTERS / "1SPE-EXPONENTIELLE"
    mandatory = [
        *sorted((chapter / "evaluations").glob("*.tex")),
        *sorted((chapter / "remediation").glob("*.tex")),
        chapter / "cours/07_td_contextualise.tex",
        chapter / "cours/07_td_fil_rouge.tex",
    ]
    forbidden = (
        r"\lim",
        r"\ln",
        "croissances comparées",
        "dérivée seconde",
        "(\\mathrm{e}^{u})'",
        r"\mathrm{e}^{x^2}",
        r"\mathrm{e}^{x^2",
    )

    for path in mandatory:
        text = path.read_text(encoding="utf-8")
        assert not any(token in text for token in forbidden), path


def test_exponentielle_exercices_du_socle_retires_des_extensions_implicites() -> None:
    chapter = CHAPTERS / "1SPE-EXPONENTIELLE"
    rewritten = ("007", "010", "017", "024", "026", "031", "032", "046", "047", "049")
    forbidden = (
        r"\lim",
        r"\ln",
        "dérivée seconde",
        "croissances comparées",
        r"\mathrm{e}^{x^2}",
    )

    for number in rewritten:
        for folder, prefix in (("exercices", "EX"), ("corriges", "CO")):
            path = chapter / folder / f"1SPE-EXPO-{prefix}-{number}.tex"
            text = path.read_text(encoding="utf-8")
            assert not any(token in text for token in forbidden), path

    for number in ("024", "031", "032"):
        path = chapter / "exercices" / f"1SPE-EXPO-EX-{number}-CDP.tex"
        text = path.read_text(encoding="utf-8")
        assert r"\mathrm{e}^{u}" not in text
        assert "u(x)" not in text
        assert r"\lim" not in text


def test_exponentielle_exercices_avances_039_040_sont_des_extensions_x1() -> None:
    chapter = CHAPTERS / "1SPE-EXPONENTIELLE"
    for number in ("039", "040"):
        for folder, prefix in (("exercices", "EX"), ("corriges", "CO")):
            path = chapter / folder / f"1SPE-EXPO-{prefix}-{number}.tex"
            meta = _meta(path)
            assert meta.get("capacites", []) == []
            assert meta.get("capacites_codes", []) == []
            assert meta["extension_codes"] == ["X1"]
            assert meta["programme_alignment"] == "OPTIONAL_EXTENSION"
            assert meta["extension_label"] == "Approfondissement — Vers la Terminale"
            assert "Approfondissement — Vers la Terminale" in path.read_text(encoding="utf-8")


def test_exponentielle_algorithmes_restent_numeriques_et_conjecturaux() -> None:
    path = (
        CHAPTERS / "1SPE-EXPONENTIELLE/cours/15_C5_algorithmes_exponentielle.tex"
    )
    algorithm = path.read_text(encoding="utf-8")
    meta = _meta(path)

    assert "méthode d'Euler" in algorithm
    assert r"\left(1+\dfrac{1}{n}\right)^n" in algorithm
    assert "conjecturer" in algorithm
    assert r"\lim" not in algorithm
    assert meta.get("capacites_codes", []) == []
    assert meta["programme_alignment"] == "IMPLEMENTATION_GUIDANCE"
    assert "Mise en œuvre algorithmique — non exigible" in algorithm


def test_modele_exponentiel_conditionne_le_sens_de_variation_a_q0_positif() -> None:
    course = (
        CHAPTERS / "1SPE-EXPONENTIELLE/cours/14_C5_a_modeles_exponentiels.tex"
    ).read_text(encoding="utf-8")
    normalized = " ".join(course.split())

    assert r"Q_0>0" in course
    assert "si $Q_0>0$ et $a>0$" in normalized


def test_extension_equations_exponentielles_definit_son_prerequis_logarithme() -> None:
    course = (
        CHAPTERS / "1SPE-EXPONENTIELLE/cours/14_C5_equations_inequations.tex"
    ).read_text(encoding="utf-8")
    normalized = " ".join(course.split())

    assert "Prérequis de cet approfondissement" in course
    assert "logarithme népérien" in normalized
    assert r"\mathrm{e}^{\ln(k)}=k" in course


def test_exponentielle_enonces_tangente_et_unicite_sont_logiquement_corrects() -> None:
    exercises = CHAPTERS / "1SPE-EXPONENTIELLE/exercices"
    tangent = (exercises / "1SPE-EXPO-EX-006.tex").read_text(encoding="utf-8")
    uniqueness = (exercises / "1SPE-EXPO-EX-001.tex").read_text(encoding="utf-8")

    assert "La tangente passe-t-elle par l'origine" in tangent
    assert "Vérifier que la tangente passe par l'origine" not in tangent
    assert "En utilisant l'unicité admise dans le cours" in uniqueness


def test_suites_limites_intuitives_couvrent_les_trois_comportements_sans_formalisme() -> None:
    chapter = CHAPTERS / "1SPE-SUITES"
    referential = _json(REFERENTIAL / "capacites_1SPE_SUITES.json")
    contract = yaml.safe_load((chapter / "contrat.yaml").read_text(encoding="utf-8"))
    expected = {
        "cours/17_C8_limites_intuitives.tex",
        "methodes/1SPE-SUITES-ME-008.tex",
        "exercices/1SPE-SUITES-EX-051.tex",
        "corriges/1SPE-SUITES-CO-051.tex",
        "remediation/1SPE-SUITES-RE-C8.tex",
    }

    assert referential["bo_reference"] == "MENE2602917A"
    c8 = next(item for item in referential["capacites"] if item["id"].endswith("-C8"))
    assert "finie" in c8["libelle_bo"]
    assert "infinie" in c8["libelle_bo"]
    assert "absence" in c8["libelle_bo"]
    assert c8["formalisation_exclue"] is True
    assert any(item["code"] == "C8" for item in contract["capacites"])
    assert all((chapter / relative).is_file() for relative in expected)

    corpus = "\n".join((chapter / relative).read_text(encoding="utf-8") for relative in expected)
    assert "limite finie" in corpus
    assert "limite infinie" in corpus
    assert "absence de limite" in corpus
    assert "sans démonstration formelle" in corpus
    assert "d'après le théorème de convergence" not in corpus.lower()

    qcm = _json(chapter / "qcm/1SPE-SUITES-QCM.json")
    limit_question = next(question for question in qcm["questions"] if question["id"] == "Q3")
    assert limit_question["capacite"] == "C8"
    assert limit_question["correcte"] == "C"
    assert set(limit_question["diagnostics"]) == {"A", "B", "D"}


def test_remediation_c8_definit_les_suites_avant_de_conjecturer() -> None:
    remediation = (
        CHAPTERS / "1SPE-SUITES/remediation/1SPE-SUITES-RE-C8.tex"
    ).read_text(encoding="utf-8")

    assert r"a_n=1+2^{-n}" in remediation
    assert r"b_n=2^n" in remediation
    assert r"c_n=\dfrac{1+(-1)^n}{2}" in remediation
