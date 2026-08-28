"""Qui echappe quoi, entre la source QCM et le producteur LaTeX.

Defaut d'origine : un enonce ecrit `\\_variable` dans le JSON alors que
build_qcm_tex echappe deja `_` hors mode mathematique. Le .tex obtenu portait
`\\\\_`, soit un saut de ligne suivi d'un indice hors math : erreur LaTeX
fatale, aucun PDF produit pour les deux variantes. Les 246 tests QCM passaient
pourtant, et le .tex etait declare synchrone avec le .json -- la synchronisation
JSON ne prouve rien sur la compilabilite.

Contrat retenu :

PLAIN_TEXT et CODE_TEXT
    la source reste semantique, le producteur possede l'echappement TeX ;
    aucun pre-echappement manuel.

EXPLICIT_LATEX et MATH_LATEX
    segments entre $...$ : la source porte du LaTeX assume, le producteur n'y
    touche pas. On n'applique donc pas aveuglement la meme regle.
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
PRODUCTEUR = RACINE / "scripts" / "build_qcm_tex.py"
CHAPITRES = RACINE / "chapitres"
#: hors mode mathematique, ces sequences signalent un pre-echappement
PRE_ECHAPPE = re.compile(r"\\[_^&#%]")


@pytest.fixture(scope="module")
def producteur():
    spec = importlib.util.spec_from_file_location("build_qcm_tex_contract", PRODUCTEUR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _hors_math(texte: str) -> list[str]:
    return re.split(r"\$[^$]*\$", texte)


# ------------------------------------------------------- contrat de champ ---


@pytest.mark.parametrize(
    ("brut", "attendu"),
    [
        ("simuler_variable", "simuler\\_variable"),
        ("a_b_c", "a\\_b\\_c"),
        ("2^n", "2\\textasciicircum{}n"),
    ],
)
def test_le_producteur_possede_l_echappement_du_texte_simple(
    producteur, brut: str, attendu: str
) -> None:
    """PLAIN_TEXT / CODE_TEXT : la source est semantique."""

    assert producteur._clean_text(brut) == attendu


def test_le_producteur_ne_touche_pas_aux_segments_mathematiques(producteur) -> None:
    """MATH_LATEX : ce qui est entre $...$ est du LaTeX assume."""

    assert producteur._clean_text("$x_1$") == "$x_1$"
    assert producteur._clean_text("$2^n$") == "$2^n$"
    assert producteur._clean_text("avant $x_1$ apres_ici") == "avant $x_1$ apres\\_ici"


def test_le_pre_echappement_produit_une_sequence_invalide(producteur) -> None:
    """La preuve du defaut : pre-echapper donne \\\\_, non \\_."""

    assert producteur._clean_text("simuler\\_variable") == "simuler\\\\_variable"


@pytest.mark.parametrize("caractere", ["%", "#", "&", "{", "}", "\\"])
def test_les_autres_caracteres_speciaux_ne_sont_pas_reecrits(
    producteur, caractere: str
) -> None:
    """Le producteur ne fabrique pas un sanitizer generique.

    Elargir l'echappement a { } \\ casserait tous les champs mathematiques et
    les macros legitimes. Ces caracteres restent sous la responsabilite de
    l'auteur, et le smoke de compilation ci-dessous en est le garde-fou.
    """

    assert producteur._clean_text(f"texte {caractere} suite") == f"texte {caractere} suite"


# ------------------------------------------------- scan de classe (sources) --


def test_aucune_source_qcm_ne_pre_echappe_hors_mode_mathematique() -> None:
    fautes: list[str] = []
    champs = 0
    for source in sorted(CHAPITRES.glob("*/qcm/*-QCM.json")):
        document = json.loads(source.read_text(encoding="utf-8"))
        for question in document.get("questions", []):
            valeurs = {"enonce": question.get("enonce", "")}
            valeurs.update(
                {f"options.{k}": v for k, v in (question.get("options") or {}).items()}
            )
            for lettre, diagnostic in (question.get("diagnostics") or {}).items():
                if isinstance(diagnostic, dict):
                    valeurs[f"diagnostics.{lettre}"] = diagnostic.get("erreur", "")
            for nom, valeur in valeurs.items():
                champs += 1
                if any(PRE_ECHAPPE.search(seg) for seg in _hors_math(str(valeur))):
                    fautes.append(
                        f"{source.parents[1].name}/{question.get('id')}/{nom}"
                    )
    assert champs > 2000, "le scan doit couvrir tout le corpus QCM"
    assert fautes == [], f"champs pre-echappes : {fautes[:10]}"


# --------------------------------------------------- smoke de compilation ---


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_le_tex_qcm_genere_compile(tmp_path: Path) -> None:
    """JSON_SYNC_PASS ne prouve pas la compilabilite : on compile vraiment."""

    genere = (
        CHAPITRES
        / "1SPE-VARIABLES-ALEATOIRES"
        / "qcm"
        / "1SPE-VARALEA-QCM.tex"
    ).read_text(encoding="utf-8")
    corps = "\n".join(
        ligne for ligne in genere.splitlines() if not ligne.startswith("% ")
    )
    document = tmp_path / "smoke.tex"
    document.write_text(
        "\\documentclass[11pt]{article}\n"
        "\\usepackage[T1]{fontenc}\\usepackage[utf8]{inputenc}\n"
        "\\usepackage[french]{babel}\\usepackage{amsmath,amssymb,xcolor}\n"
        # le .tex genere utilise \\begin{enumerate}[label=\\Alph*]
        "\\usepackage{enumitem,array}\n"
        "\\definecolor{chapcolor}{RGB}{0,90,140}\n"
        "\\newcommand{\\code}[1]{\\texttt{#1}}\n"
        "\\newif\\ifnxVersionProfesseur\\nxVersionProfesseurtrue\n"
        "\\begin{document}\n" + corps + "\n\\end{document}\n",
        encoding="utf-8",
    )
    run = subprocess.run(
        ["lualatex", "-interaction=nonstopmode", "-halt-on-error", document.name],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert run.returncode == 0, run.stdout[-2500:]
    assert (tmp_path / "smoke.pdf").is_file()
