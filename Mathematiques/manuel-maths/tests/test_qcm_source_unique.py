"""Regression : un QCM doit avoir une cle, des diagnostics, et ne pas diverger.

Defaut d'origine : la revue de contenu 1NSI a classe en P1 les QCM livres sans
cle de correction, sans diagnostic par distracteur et sans renvoi de
remediation. S'y ajoute un risque structurel : quand le .tex imprime et le
.json exploitable sont maintenus a la main en parallele, ils divergent.

Ces tests s'appliquent a tout chapitre disposant d'un QCM au format JSON. Les
chapitres dont le QCM n'existe qu'en .tex ne sont pas encore couverts : ils le
deviendront a mesure de leur migration vers la source unique.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
GENERATEUR = RACINE / "scripts" / "build_qcm_tex.py"


def _sources_qcm() -> dict[str, Path]:
    """Les noms de fichiers utilisent des prefixes courts (1SPE-SECDEG pour
    1SPE-SECOND-DEGRE) : on decouvre le fichier au lieu de deduire son nom."""
    trouves: dict[str, Path] = {}
    for chemin in sorted(RACINE.glob("chapitres/*/qcm/*-QCM.json")):
        trouves[chemin.parent.parent.name] = chemin
    return trouves


SOURCES = _sources_qcm()
CHAPITRES = sorted(SOURCES)
MARQUE_SOURCE_UNIQUE = "genere par scripts/build_qcm_tex.py"
CHAPITRES_SOURCE_UNIQUE = sorted(
    nom
    for nom, chemin in SOURCES.items()
    if chemin.with_suffix(".tex").exists()
    and MARQUE_SOURCE_UNIQUE in chemin.with_suffix(".tex").read_text(encoding="utf-8")
)


@pytest.mark.parametrize("chapitre", CHAPITRES)
def test_chaque_distracteur_porte_un_diagnostic_et_un_renvoi(chapitre: str) -> None:
    donnees = json.loads(SOURCES[chapitre].read_text(encoding="utf-8"))

    for question in donnees["questions"]:
        if "options" not in question:
            # Schema reduit hérité (id / capacite / correcte / diagnostics) : les
            # enonces et les options vivent alors dans le .tex. Ces chapitres sont
            # couverts par les autres controles mais pas par celui-ci tant qu'ils
            # n'ont pas migre vers la source unique.
            continue
        correcte = question["correcte"]
        assert correcte in question["options"], (
            f"{chapitre}/{question['id']} : la reponse correcte ne figure pas parmi les options"
        )
        for lettre in question["options"]:
            if lettre == correcte:
                assert lettre not in question["diagnostics"], (
                    f"{chapitre}/{question['id']} : la bonne reponse porte un diagnostic d'erreur"
                )
                continue
            diagnostic = question["diagnostics"].get(lettre)
            assert diagnostic, (
                f"{chapitre}/{question['id']} : distracteur {lettre} sans erreur documentee"
            )
            assert diagnostic.get("erreur", "").strip(), (
                f"{chapitre}/{question['id']} : diagnostic {lettre} vide"
            )
            assert diagnostic.get("renvoi", "").strip(), (
                f"{chapitre}/{question['id']} : distracteur {lettre} sans renvoi de remediation"
            )


@pytest.mark.parametrize("chapitre", CHAPITRES)
def test_identifiants_de_questions_uniques(chapitre: str) -> None:
    donnees = json.loads(SOURCES[chapitre].read_text(encoding="utf-8"))
    identifiants = [question["id"] for question in donnees["questions"]]
    assert len(identifiants) == len(set(identifiants)), f"{chapitre} : identifiants de questions en double"


@pytest.mark.parametrize("chapitre", CHAPITRES)
def test_toutes_les_capacites_du_contrat_sont_interrogees(chapitre: str) -> None:
    import yaml

    contrat = yaml.safe_load(
        (RACINE / "chapitres" / chapitre / "contrat.yaml").read_text(encoding="utf-8")
    )
    attendues = {capacite["code"] for capacite in (contrat.get("capacites") or [])}
    donnees = json.loads(SOURCES[chapitre].read_text(encoding="utf-8"))
    interrogees = {question["capacite"] for question in donnees["questions"]}
    manquantes = attendues - interrogees
    assert not manquantes, f"{chapitre} : capacites absentes du QCM : {sorted(manquantes)}"


@pytest.mark.parametrize("chapitre", CHAPITRES_SOURCE_UNIQUE)
def test_le_tex_ne_diverge_pas_de_sa_source_json(chapitre: str) -> None:
    resultat = subprocess.run(
        [sys.executable, str(GENERATEUR), "--chap", chapitre, "--check"],
        capture_output=True,
        text=True,
    )
    assert resultat.returncode == 0, (
        f"{chapitre} : le .tex a diverge de son .json. "
        f"Regenerer avec build_qcm_tex.py --chap {chapitre}.\n{resultat.stderr}"
    )
