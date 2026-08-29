"""Le jeu d'objets publiables de 1SPE-VARIABLES-ALEATOIRES est enumere deux fois.

Defaut d'origine : la cloture verticale du chapitre s'appuyait sur un
denominateur (« 155 objets ») produit par un seul recenseur. Un denominateur
non contre-mesure permet a un objet ajoute hors circuit de ne jamais entrer
dans les revues science / pedagogie / editorial : il n'apparait dans aucun
rapport, donc il n'est jamais relu.

Ce test recense les objets par une voie INDEPENDANTE du producteur canonique
(git ls-files + en-tetes META) et fige la repartition exacte par type. Toute
creation, suppression ou requalification d'objet fait echouer le test tant que
la repartition attendue n'a pas ete mise a jour de facon deliberee.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
CHAPITRE = RACINE / "chapitres" / "1SPE-VARIABLES-ALEATOIRES"

# Repartition scellee a la cloture verticale du chapitre.
# 155 objets a l'ouverture de la cloture ; RE-C6 et RE-C7 ont ete ajoutees
# parce que les capacites C6 et C7 n'avaient aucune remediation.
REPARTITION_ATTENDUE = {
    "corrige": 50,
    "exercice": 50,
    "coup_de_pouce": 18,
    "remediation": 12,
    "cours": 7,
    "methode": 7,
    "experimentation": 4,
    "algorithme": 2,
    "td": 2,
    "evaluation": 2,
    "corrige_evaluation": 2,
    "qcm": 1,
}
TOTAL_ATTENDU = 157

_META = re.compile(r"^%\s*META:\s*(\{.*\})\s*$", re.M)


def _objets() -> list[dict]:
    sortie = subprocess.run(
        ["git", "ls-files", "--", str(CHAPITRE.relative_to(RACINE.parents[1]))],
        cwd=RACINE.parents[1],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    objets = []
    for relatif in sortie:
        if not relatif.endswith(".tex"):
            continue
        chemin = RACINE.parents[1] / relatif
        trouve = _META.search(chemin.read_text(encoding="utf-8"))
        assert trouve, f"{relatif} : objet publiable sans en-tete META"
        donnees = json.loads(trouve.group(1))
        donnees["_chemin"] = relatif
        objets.append(donnees)
    return objets


def test_la_somme_de_la_repartition_vaut_le_total() -> None:
    """Le total scelle n'est pas un nombre libre : c'est la somme des types."""
    assert sum(REPARTITION_ATTENDUE.values()) == TOTAL_ATTENDU


def test_enumeration_independante_retrouve_le_total() -> None:
    assert len(_objets()) == TOTAL_ATTENDU


def test_la_repartition_par_type_est_exacte() -> None:
    observee: dict[str, int] = {}
    for objet in _objets():
        type_objet = objet.get("type_objet")
        assert type_objet, f"{objet['_chemin']} : META sans type_objet"
        observee[type_objet] = observee.get(type_objet, 0) + 1
    assert observee == REPARTITION_ATTENDUE


def test_les_identifiants_sont_uniques_et_sans_doublon() -> None:
    identifiants = [objet["id"] for objet in _objets()]
    doublons = sorted({i for i in identifiants if identifiants.count(i) > 1})
    assert not doublons, f"identifiants d'objets en double : {doublons}"
    assert len(set(identifiants)) == TOTAL_ATTENDU


def test_aucune_source_tex_du_chapitre_n_est_non_suivie() -> None:
    """Un .tex non suivi par git est un objet invisible pour toutes les revues."""
    non_suivis = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "--", str(CHAPITRE)],
        cwd=RACINE.parents[1],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    assert [f for f in non_suivis if f.endswith(".tex")] == []


def test_chaque_capacite_du_contrat_a_une_remediation() -> None:
    """Regression : C6 et C7 avaient ete ajoutees au contrat sans remediation."""
    import yaml

    contrat = yaml.safe_load((CHAPITRE / "contrat.yaml").read_text(encoding="utf-8"))
    codes = {capacite["code"] for capacite in contrat["capacites"]}
    presentes = {
        chemin.stem.rsplit("-", 1)[-1]
        for chemin in (CHAPITRE / "remediation").glob("*-RE-*.tex")
    }
    assert codes <= presentes, f"capacites sans remediation : {sorted(codes - presentes)}"
