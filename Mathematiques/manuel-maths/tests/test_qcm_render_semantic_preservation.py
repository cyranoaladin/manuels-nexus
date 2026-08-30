"""Le texte remis a l'eleve doit survivre au rendu, en entier.

P0 SILENT_PRODUCTION_CONTENT_LOSS. Un `%` non echappe ouvre un commentaire
LaTeX : la compilation reussit, aucun test ne bronche, et la fin de la ligne
disparait du PDF. Deux cas reels ont ete mesures dans des artefacts de
production :

* 1SPE-PROBA-COND Q17 s'imprimait « Sensibilite 99 » et perdait
  « specificite 99%, prevalence 0,1%. La VPP vaut environ : » ;
* TCOMPL-INFERENCE-BAYESIENNE Q5 perdait la fin de son enonce et de ses
  quatre options.

Un smoke de compilation ne suffit donc pas : il faut un aller-retour complet
source -> generateur -> TeX -> compilation -> extraction -> comparaison
semantique.
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
PRODUCTEUR = RACINE / "scripts" / "build_qcm_tex.py"
CHAPITRES = RACINE / "chapitres"
MATH = re.compile(r"\$[^$]*\$")
MACRO = re.compile(r"\\[a-zA-Z]+\s*(\{[^{}]*\}|\|[^|]*\|)?")


@pytest.fixture(scope="module")
def producteur():
    spec = importlib.util.spec_from_file_location("build_qcm_tex_preservation", PRODUCTEUR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _normalise(text: str) -> str:
    """Normalisation tolerante : espaces, espaces fines, ligatures d'extraction."""

    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00a0", " ").replace("\u202f", " ").replace("\u2009", " ")
    text = text.replace("\u2019", "'").replace("\u2013", "-").replace("\u2014", "-")
    return " ".join(text.split())


def _texte_semantique(champ: str) -> str:
    """Ce que l'eleve doit lire : hors segments mathematiques et hors macros."""

    sans_math = "".join(MATH.split(champ))
    sans_macro = MACRO.sub(lambda m: (m.group(1) or "").strip("{}|"), sans_math)
    return _normalise(sans_macro)


def _compiler(corps: str, dossier: Path) -> str:
    source = dossier / "rt.tex"
    source.write_text(
        "\\documentclass[11pt]{article}\n"
        "\\usepackage[T1]{fontenc}\\usepackage[utf8]{inputenc}\n"
        "\\usepackage[french]{babel}\\usepackage{amsmath,amssymb,xcolor}\n"
        "\\usepackage{enumitem,array}\n"
        "\\definecolor{chapcolor}{RGB}{0,90,140}\n"
        "\\newcommand{\\code}[1]{\\texttt{#1}}\n"
        "\\newif\\ifnxVersionProfesseur\\nxVersionProfesseurtrue\n"
        "\\begin{document}\n" + corps + "\n\\end{document}\n",
        encoding="utf-8",
    )
    run = subprocess.run(
        ["lualatex", "-interaction=nonstopmode", "-halt-on-error", "rt.tex"],
        cwd=dossier, capture_output=True, text=True, timeout=300,
    )
    assert run.returncode == 0, run.stdout[-2500:]
    extrait = subprocess.run(
        ["pdftotext", "-layout", str(dossier / "rt.pdf"), "-"],
        capture_output=True, text=True, timeout=120,
    )
    assert extrait.returncode == 0
    return _normalise(extrait.stdout)


def _rendre_et_extraire(producteur, document: dict, dossier: Path) -> str:
    tex = producteur.rendre(document)
    corps = "\n".join(l for l in tex.splitlines() if not l.startswith("% "))
    return _compiler(corps, dossier)


def _document(enonce: str, options: dict[str, str]) -> dict:
    lettres = list(options)
    return {
        "chapitre": "FIXTURE",
        "titre": "Aller-retour",
        "_source": "fixture.json",
        "questions": [{
            "id": "R1", "capacite": "C1", "enonce": enonce, "options": options,
            "correcte": lettres[0],
            "diagnostics": {
                l: {"erreur": f"diagnostic {l}", "renvoi": "C1"} for l in lettres[1:]
            },
        }],
    }


# ------------------------------------------------- cas reels de regression ---


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_le_cas_reel_1spe_proba_cond_q17_survit_entierement(producteur, tmp_path: Path) -> None:
    source = json.loads(
        (CHAPITRES / "1SPE-PROBA-COND" / "qcm" / "1SPE-PROBCOND-QCM.json").read_text(
            encoding="utf-8"
        )
    )
    question = next(q for q in source["questions"] if q["id"] == "Q17")

    assert "%" in question["enonce"], "la fixture historique doit contenir le caractere fautif"

    rendu = _rendre_et_extraire(producteur, _document(question["enonce"], question["options"]), tmp_path)

    for fragment in ("specificite", "prevalence", "La VPP vaut environ"):
        assert _normalise(fragment) in rendu, f"tronque apres % : {fragment!r} absent"
    assert rendu.count("99 %") + rendu.count("99%") >= 2


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_le_cas_reel_tcompl_inference_q5_conserve_ses_options(producteur, tmp_path: Path) -> None:
    source = json.loads(
        (CHAPITRES / "TCOMPL-INFERENCE-BAYESIENNE" / "qcm"
         / "TCOMPL-INFERENCE-BAYESIENNE-QCM.json").read_text(encoding="utf-8")
    )
    question = next(q for q in source["questions"] if q["id"] == "Q5")
    rendu = _rendre_et_extraire(producteur, _document(question["enonce"], question["options"]), tmp_path)

    # Fragments accentues a dessein : depuis la campagne diacritiques, le
    # controle prouve aussi que les accents survivent au rendu.
    for fragment in ("car la maladie est rare", "Très forte", "Égale a 50", "Exactement 90"):
        assert _normalise(fragment) in rendu, f"option tronquee : {fragment!r}"


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_la_fixture_historique_echoue_sans_la_correction(producteur, tmp_path: Path, monkeypatch) -> None:
    """Preuve que le test detecte bien le defaut, et non un artefact."""

    monkeypatch.setattr(
        producteur, "_clean_text",
        lambda s, champ="champ": s if not isinstance(s, str) else s.replace("_", "\\_"),
    )
    rendu = _rendre_et_extraire(
        producteur,
        _document("Sensibilite 99%, specificite 99%, prevalence 0,1%. La VPP vaut environ :",
                  {"A": "0,01", "B": "0,09", "C": "0,5", "D": "0,99"}),
        tmp_path,
    )

    assert _normalise("La VPP vaut environ") not in rendu, (
        "sans l'echappement du %, la fin de ligne doit disparaitre"
    )


# ------------------------------------------------ preservation par caractere ---


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
@pytest.mark.parametrize(
    ("enonce", "attendu"),
    [
        ("La fonction a_b_c renvoie APRES.", "La fonction a_b_c renvoie APRES."),
        ("Un taux de 99 % puis APRES.", "Un taux de 99 % puis APRES."),
        ("Le cas # 3 puis APRES.", "Le cas # 3 puis APRES."),
        ("A & B puis APRES.", "A & B puis APRES."),
        ("Pour X ~ B(n,p) puis APRES.", "Pour X ~ B(n,p) puis APRES."),
    ],
)
def test_le_texte_simple_est_integralement_restitue(
    producteur, tmp_path: Path, enonce: str, attendu: str
) -> None:
    rendu = _rendre_et_extraire(
        producteur, _document(enonce, {"A": "un", "B": "deux", "C": "trois", "D": "quatre"}), tmp_path
    )

    assert _normalise(attendu) in rendu


# ------------------------------------------ non-regression de la semantique LaTeX ---


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
@pytest.mark.parametrize(
    "math",
    ["$\\frac{1}{2}$", "$\\sqrt{2}$", "$x_1$", "$2^n$", "$\\{1;2\\}$", "$P(A \\cap B)$"],
)
def test_les_contenus_mathematiques_ne_sont_pas_alteres(
    producteur, tmp_path: Path, math: str
) -> None:
    """La correction texte ne doit rien casser du LaTeX intentionnel."""

    tex = producteur.rendre(_document(f"Calculer {math} puis APRES.",
                                      {"A": math, "B": "b", "C": "c", "D": "d"}))

    assert math in tex, "le segment mathematique doit traverser le producteur intact"
    corps = "\n".join(l for l in tex.splitlines() if not l.startswith("% "))
    rendu = _compiler(corps, tmp_path)
    assert _normalise("puis APRES.") in rendu


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_le_cas_reel_tspe_probabilites_q5_conserve_le_symbole_de_loi(
    producteur, tmp_path: Path
) -> None:
    """Perte d'un TOKEN, sans troncature : le tilde s'evaporait.

    « Pour X ~ B(n,p) » s'imprimait « Pour X B(n,p) » : le symbole « suit la
    loi » disparaissait sans erreur de compilation, car ~ est un espace
    insecable en LaTeX.
    """

    source = json.loads(
        (CHAPITRES / "TSPE-PROBABILITES" / "qcm" / "TSPE-PROBABILITES-QCM.json").read_text(
            encoding="utf-8"
        )
    )
    question = next(q for q in source["questions"] if q["id"] == "Q5")

    assert "~" in question["enonce"], "la fixture historique doit contenir le tilde"

    rendu = _rendre_et_extraire(
        producteur, _document(question["enonce"], question["options"]), tmp_path
    )

    assert "~" in rendu, "le symbole de loi doit rester visible dans le PDF"
