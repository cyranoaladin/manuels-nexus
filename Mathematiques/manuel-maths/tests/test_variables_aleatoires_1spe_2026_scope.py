"""Périmètre réglementaire 2026-2027 du chapitre Variables aléatoires.

MENE2602917A autorise dans le socle les répétitions de deux à quatre
épreuves de Bernoulli décrites par un arbre. La formalisation par la loi
binomiale, ses coefficients et ses formules de moments est une extension.
"""

from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "chapitres/1SPE-VARIABLES-ALEATOIRES"
REFERENTIAL = ROOT / "referentiel/capacites_1SPE_VARIABLES_ALEATOIRES.json"
LABEL = "Approfondissement — Vers la Terminale"
META = re.compile(r"^% META: (\{.*\})", re.MULTILINE)
FORBIDDEN = re.compile(
    r"loi binomiale|\\mathcal\{B\}\([^\n)]*,|\\binom\{|"
    r"coefficients? binomiaux|E\(X\)\s*=\s*np|V\(X\)\s*=\s*np\(1-p\)",
    re.IGNORECASE,
)
AFFINE_VARIANCE = re.compile(
    r"V\((?:aX\s*\+\s*b|Y|Z)\)|"
    r"\\sigma\((?:aX\s*\+\s*b|Y|Z)\)",
    re.IGNORECASE,
)


def _meta(path: Path) -> dict:
    match = META.search(path.read_text(encoding="utf-8"))
    assert match, f"META absent: {path}"
    return json.loads(match.group(1))


def test_referentiel_et_contrat_separent_socle_et_extensions() -> None:
    referential = json.loads(REFERENTIAL.read_text(encoding="utf-8"))
    contract = yaml.safe_load((CHAPTER / "contrat.yaml").read_text(encoding="utf-8"))

    assert [item["id"] for item in referential["capacites"]] == [
        f"1SPE-VARIABLES-ALEATOIRES-C{i}" for i in range(1, 6)
    ]
    assert [item["code"] for item in contract["capacites"]] == [
        f"C{i}" for i in range(1, 6)
    ]
    assert {item["code"] for item in contract["extensions_facultatives"]} == {
        "X1",
        "X2",
    }
    for item in contract["extensions_facultatives"]:
        assert item["programme_alignment"] == "OPTIONAL_EXTENSION"
        assert item["label"] == LABEL

    mandatory = " ".join(
        item["libelle_bo"] + " " + item["libelle_eleve"]
        for item in referential["capacites"]
    )
    assert not FORBIDDEN.search(mandatory)

    c4 = next(
        item
        for item in referential["capacites"]
        if item["id"] == "1SPE-VARIABLES-ALEATOIRES-C4"
    )
    assert c4["libelle_bo"] == "Utiliser la linéarité de l'espérance."
    assert "variance" not in c4["libelle_eleve"].lower()

    assert {item["code"] for item in referential["optional_extensions"]} == {
        "X1",
        "X2",
    }


def test_variance_affine_post_gel_ne_cree_pas_une_extension_x3() -> None:
    extension = CHAPTER / "cours/13_X3_variance_affine.tex"
    assert not extension.exists()


def test_extensions_optionnelles_sans_besoin_editorial_prouve_sont_absentes() -> None:
    assert not (CHAPTER / "cours/12_C3_bernoulli_binomiale.tex").exists()
    assert not (CHAPTER / "cours/13_C4_esperance_binomiale.tex").exists()


def test_variance_affine_n_est_jamais_exigible_dans_le_socle() -> None:
    offenders: list[str] = []
    for path in sorted(CHAPTER.rglob("*.tex")):
        text = path.read_text(encoding="utf-8")
        meta = _meta(path)
        if meta.get("programme_alignment") == "OPTIONAL_EXTENSION":
            continue
        if AFFINE_VARIANCE.search(text):
            offenders.append(str(path.relative_to(CHAPTER)))

    assert offenders == []


def test_chaine_c4_obligatoire_est_centree_sur_linearite_esperance() -> None:
    mandatory_chain = [
        CHAPTER / "cours/13_C4_transformations_affines.tex",
        CHAPTER / "methodes/1SPE-VARALEA-ME-007.tex",
        CHAPTER / "exercices/1SPE-VARALEA-EX-014.tex",
        CHAPTER / "corriges/1SPE-VARALEA-CO-014.tex",
        CHAPTER / "exercices/1SPE-VARALEA-EX-020.tex",
        CHAPTER / "corriges/1SPE-VARALEA-CO-020.tex",
        CHAPTER / "evaluations/1SPE-VARALEA-EV-B.tex",
        CHAPTER / "evaluations/1SPE-VARALEA-EV-B-corrige.tex",
        CHAPTER / "remediation/1SPE-VARALEA-RE-C4.tex",
    ]
    for path in mandatory_chain:
        text = path.read_text(encoding="utf-8")
        meta = _meta(path)
        assert "C4" in meta["capacites_codes"], path
        assert "E(" in text and "E(X)" in text, path
        assert not AFFINE_VARIANCE.search(text), path

    qcm = json.loads((CHAPTER / "qcm/1SPE-VARALEA-QCM.json").read_text(encoding="utf-8"))
    c4_questions = [question for question in qcm["questions"] if question["capacite"] == "C4"]
    assert len(c4_questions) == 3
    assert all("E(X)" in question["enonce"] for question in c4_questions)
    assert all(not AFFINE_VARIANCE.search(question["enonce"]) for question in c4_questions)


def test_aucune_ressource_obligatoire_ne_formalise_la_loi_binomiale() -> None:
    roots = ("cours", "methodes", "exercices", "corriges", "evaluations", "remediation")
    offenders: list[str] = []
    for folder in roots:
        for path in sorted((CHAPTER / folder).rglob("*.tex")):
            text = path.read_text(encoding="utf-8")
            if not FORBIDDEN.search(text):
                continue
            meta = _meta(path)
            if meta.get("programme_alignment") != "OPTIONAL_EXTENSION":
                offenders.append(str(path.relative_to(CHAPTER)))
                continue
            assert meta.get("capacites", []) == []
            assert meta.get("capacites_codes", []) == []
            assert set(meta["extension_codes"]) <= {"X1", "X2"}
            assert meta["extension_codes"]
            assert meta["extension_label"] == LABEL
            assert LABEL in text
    assert offenders == []


def test_qcm_evaluations_diagnostics_et_remediations_restent_dans_le_socle() -> None:
    qcm = json.loads((CHAPTER / "qcm/1SPE-VARALEA-QCM.json").read_text(encoding="utf-8"))
    assert len(qcm["questions"]) == 15
    assert not FORBIDDEN.search(json.dumps(qcm, ensure_ascii=False))

    mandatory_paths = [
        CHAPTER / "cours/01_diagnostic.tex",
        *(CHAPTER / "evaluations").glob("*.tex"),
        CHAPTER / "remediation/1SPE-VARALEA-RE-C3.tex",
        CHAPTER / "remediation/1SPE-VARALEA-RE-C4.tex",
    ]
    for path in mandatory_paths:
        assert not FORBIDDEN.search(path.read_text(encoding="utf-8")), path


def test_repetitions_obligatoires_sont_bornees_a_quatre_epreuves() -> None:
    contract = (CHAPTER / "contrat.yaml").read_text(encoding="utf-8")
    referential = REFERENTIAL.read_text(encoding="utf-8")
    qcm = (CHAPTER / "qcm/1SPE-VARALEA-QCM.json").read_text(encoding="utf-8")
    evaluations = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((CHAPTER / "evaluations").glob("*.tex"))
    )
    assert "n <= 4" in contract
    assert "n ≤ 4" in referential
    for text in (qcm, evaluations):
        assert not re.search(r"(?:[5-9]|[1-9][0-9]+) (?:tirs|lancers|épreuves|fois)", text)


def test_qcm_reclasses_ont_une_cle_unique_et_des_diagnostics_specifiques() -> None:
    data = json.loads((CHAPTER / "qcm/1SPE-VARALEA-QCM.json").read_text(encoding="utf-8"))
    questions = {question["id"]: question for question in data["questions"]}
    expected = {
        "Q7": ("B", Fraction(1, 2) ** 3),
        "Q8": ("B", 2 * Fraction(1, 3) * Fraction(2, 3)),
        "Q9": ("B", 2**3),
        "Q10": ("B", 3 * 4 - 2),
        "Q11": ("B", -2 * 5 + 7),
        "Q12": ("B", -4 * (-3) + 1),
    }
    rendered_answers = {
        "Q7": {"A": Fraction(1, 6), "B": Fraction(1, 8), "C": Fraction(3, 8), "D": Fraction(1, 2)},
        "Q8": {"A": Fraction(2, 9), "B": Fraction(4, 9), "C": Fraction(1, 9), "D": Fraction(2, 3)},
        "Q9": {"A": 3, "B": 8, "C": 6, "D": 9},
        "Q10": {"A": 12, "B": 10, "C": 6, "D": 2},
        "Q11": {"A": -10, "B": -3, "C": 17, "D": 12},
        "Q12": {"A": -13, "B": 13, "C": -11, "D": -2},
    }
    generic = re.compile(r"arbitraire|erreur de calcul|confusion totale", re.IGNORECASE)
    for question_id, (answer, value) in expected.items():
        question = questions[question_id]
        correct_options = [
            option for option, option_value in rendered_answers[question_id].items()
            if option_value == value
        ]
        assert correct_options == [answer]
        assert question["correcte"] == answer
        assert set(question["diagnostics"]) == set(question["options"]) - {answer}
        assert all(
            not generic.search(diagnostic["erreur"])
            for diagnostic in question["diagnostics"].values()
        )
