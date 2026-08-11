"""Regression : un prerequis attribue a la Premiere doit exister dans le BO Premiere.

Defaut d'origine (2026-08-11) : trois contrats de Terminale declaraient comme
« vus en premiere » des contenus absents des deux programmes de Premiere —
nombres complexes (TEXP-COMPLEXES-ALGEBRE-GEOMETRIE), recursivite
(TEXP-ARITHMETIQUE), structures de donnees (TEXP-GRAPHES). Le contrat des
complexes annoncait meme a l'eleve un chapitre qui « reprend ce qui a ete vu en
premiere ».

Le verdict n'est pas code en dur : il est recalcule a chaque execution par
recherche dans les BO 1SPE 2019 et 2026 deposes dans sources/txt/.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parents[1]
CHAPITRES = RACINE / "chapitres"
BO_PREMIERE = (
    RACINE / "sources/txt/BO2019_1SPE_specialite.txt",
    RACINE / "sources/txt/BO2026_1SPE_specialite.txt",
)

# Notions dont l'attribution a la Premiere est verifiee contre le texte officiel.
# Chaque entree : (motif cherche dans le libelle du prerequis, motif cherche dans le BO).
NOTIONS_SURVEILLEES = (
    (r"nombres?\s+complexes?", r"nombres?\s+complexes?"),
    (r"recursivite|recursif", r"recursivite|recursif"),
    (r"structures?\s+de\s+donnees", r"structures?\s+de\s+donnees"),
    (r"matrices?", r"matrices?"),
    (r"integrale|primitive", r"integrale|primitive"),
    (r"logarithme", r"logarithme"),
)


def _sans_accents(texte: str) -> str:
    decompose = unicodedata.normalize("NFD", texte)
    return "".join(c for c in decompose if unicodedata.category(c) != "Mn").lower()


@pytest.fixture(scope="module")
def texte_bo_premiere() -> str:
    morceaux = []
    for chemin in BO_PREMIERE:
        assert chemin.exists(), f"BO Premiere absent des sources suivies : {chemin}"
        morceaux.append(chemin.read_text(encoding="utf-8", errors="replace"))
    return _sans_accents("\n".join(morceaux))


def _contrats_terminale() -> list[Path]:
    return sorted(
        chemin
        for chemin in CHAPITRES.glob("*/contrat.yaml")
        if chemin.parent.name.startswith(("TSPE-", "TCOMPL-", "TEXP-"))
    )


def _prerequis_attribues_a_la_premiere(contrat: Path):
    donnees = yaml.safe_load(contrat.read_text(encoding="utf-8")) or {}
    for prerequis in donnees.get("prerequis") or []:
        origine = str(prerequis.get("chapitre_origine", ""))
        if "1SPE" in origine:
            yield str(prerequis.get("libelle", "")), origine


@pytest.mark.parametrize("contrat", _contrats_terminale(), ids=lambda p: p.parent.name)
def test_prerequis_premiere_existent_dans_le_bo(contrat: Path, texte_bo_premiere: str) -> None:
    for libelle, origine in _prerequis_attribues_a_la_premiere(contrat):
        libelle_nu = _sans_accents(libelle)
        for motif_libelle, motif_bo in NOTIONS_SURVEILLEES:
            if not re.search(motif_libelle, libelle_nu):
                continue
            assert re.search(motif_bo, texte_bo_premiere), (
                f"{contrat.parent.name} attribue a la Premiere ({origine}) la notion "
                f"« {libelle} », absente des programmes de Premiere 2019 et 2026."
            )


@pytest.mark.parametrize("contrat", _contrats_terminale(), ids=lambda p: p.parent.name)
def test_accroche_ne_promet_pas_un_acquis_de_premiere_inexistant(
    contrat: Path, texte_bo_premiere: str
) -> None:
    donnees = yaml.safe_load(contrat.read_text(encoding="utf-8")) or {}
    accroche = _sans_accents(str(donnees.get("situation_accroche", "")))
    if not re.search(r"vue?s?\s+en\s+premiere|revu.{0,20}premiere", accroche):
        return
    for motif_libelle, motif_bo in NOTIONS_SURVEILLEES:
        if re.search(motif_libelle, accroche):
            assert re.search(motif_bo, texte_bo_premiere), (
                f"{contrat.parent.name} annonce a l'eleve un contenu « vu en premiere » "
                f"qui n'est dans aucun programme de Premiere."
            )
