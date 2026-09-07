"""Le classifieur de fonctions pedagogiques, epingle sur des enonces reels.

Un detecteur dont la liste de marqueurs derive silencieusement fait bouger le
nombre de chapitres faibles sans qu'aucun manuel ait change. Ces fixtures sont
extraites du corpus : elles disent, enonce par enonce, quelle fonction DOIT
etre reconnue et laquelle ne doit PAS l'etre. Ajouter un verbe a la liste sans
casser aucune fixture est legitime ; en ajouter un qui fait basculer une
fixture ne l'est pas.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def taxo():
    spec = importlib.util.spec_from_file_location(
        "exercise_function_taxonomy", ROOT / "scripts/exercise_function_taxonomy.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["exercise_function_taxonomy"] = module
    spec.loader.exec_module(module)
    return module


#: (enonce, fonctions attendues, fonctions interdites)
FIXTURES: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = (
    # -- Le geste de base se LIT, il n'est pas un residu.
    ("Calculer la dérivée de $f(x)=x^3-2x$.", ("DIRECT_APPLICATION",), ("REASONING",)),
    ("Déterminer le module et un argument de $z=-\\sqrt2+\\mathrm{i}\\sqrt2$.",
     ("DIRECT_APPLICATION",), ("REASONING", "CONTEXT_VARIATION")),
    ("Décomposer $\\vec{AG}$ dans la base $(\\vec{AB},\\vec{AD},\\vec{AE})$.",
     ("DIRECT_APPLICATION",), ("REASONING",)),
    ("Écrire $z=-1-\\mathrm{i}$ sous forme exponentielle.",
     ("DIRECT_APPLICATION",), ("REASONING",)),
    ("Traduire ce code en Python.", ("DIRECT_APPLICATION",), ("REASONING",)),
    ("Représenter le nuage de points dans un repère.",
     ("DIRECT_APPLICATION",), ("REASONING",)),
    ("Convertir $156$ en base $2$ puis en base $16$.",
     ("DIRECT_APPLICATION",), ("REASONING", "MODELLING")),
    # -- Un enonce nu sans aucun marqueur reste une application.
    ("$f(x)=3x^2-4x+5$ sur $\\mathbb{R}$.", ("DIRECT_APPLICATION",), ()),
    # -- Le raisonnement.
    ("Démontrer que pour tout $x\\in\\mathbb{R}$, $\\mathrm{e}^x\\geqslant 1+x$.",
     ("REASONING",), ("DIRECT_APPLICATION",)),
    ("Justifier à partir du code.", ("REASONING",), ()),
    ("En déduire que la suite est croissante.", ("REASONING",), ()),
    # -- Un exercice peut etre a la fois direct ET contextualise : c'est le
    #    point qui manquait, et qui faisait voir des lacunes inexistantes.
    ("Une usine produit des pièces. Calculer la masse totale rejetée.",
     ("DIRECT_APPLICATION", "CONTEXT_VARIATION"), ()),
    ("Un magasin de $450$ m$^2$ : estimer son chiffre d'affaires et justifier.",
     ("CONTEXT_VARIATION", "REASONING"), ()),
    # -- Le transfert de methode.
    ("Retrouver ce résultat de deux façons différentes.", ("METHOD_TRANSFER",), ()),
    ("Calculer cette intégrale sans utiliser de primitive.",
     ("METHOD_TRANSFER", "DIRECT_APPLICATION"), ()),
    # -- Le cas limite.
    ("Que renvoie la fonction pour une liste vide ? Expliquer pourquoi ce cas "
     "est impossible à traiter autrement.", ("EDGE_CASE",), ()),
    ("Donner un contre-exemple.", ("EDGE_CASE",), ()),
    # -- La modelisation.
    ("Exprimer la hauteur en fonction du temps écoulé.", ("MODELLING",), ()),
    # -- Les verbes releves sur le corpus : « montrer » sans « que »,
    #    « expliquer », « interpreter », « pourquoi », « comparer ».
    ("Montrer que la suite converge.", ("REASONING",), ()),
    ("Expliquer pourquoi ce résultat est inacceptable.", ("REASONING",), ()),
    ("Interpréter le coefficient obtenu.", ("REASONING",), ()),
    ("Comparer les deux estimations et commenter.", ("REASONING",), ()),
    # -- Et les gestes d'execution qu'on ne voyait pas.
    ("Vérifier le résultat sur $[4, 9, 2]$.", ("DIRECT_APPLICATION",), ("REASONING",)),
    ("Résoudre $x^2-5x+6=0$.", ("DIRECT_APPLICATION",), ("REASONING",)),
    ("Étudier les variations de $f$ sur $[0\\,;\\,3]$.",
     ("DIRECT_APPLICATION",), ("REASONING",)),
    ("Identifier les trois composants graphiques du formulaire.",
     ("DIRECT_APPLICATION",), ("REASONING",)),
    ("Réécrire le test à l'aide de cette fonction.",
     ("DIRECT_APPLICATION",), ("REASONING",)),
    # -- Ce qui ne doit PAS declencher : le bloc oracle n'est pas un enonce.
    ("% assert simplify(diff(F, x) - f) == 0\n% # on démontre ici que la "
     "primitive est correcte\nCalculer $F(2)$.",
     ("DIRECT_APPLICATION",), ("REASONING",)),
)


@pytest.mark.parametrize("enonce,attendues,interdites", FIXTURES)
def test_the_classifier_reads_what_the_statement_asks(
    taxo, enonce, attendues, interdites,
) -> None:
    fonctions = set(taxo.functions_of(enonce, {}))
    for fonction in attendues:
        assert fonction in fonctions, (enonce[:60], sorted(fonctions))
    for fonction in interdites:
        assert fonction not in fonctions, (enonce[:60], sorted(fonctions))


def test_a_reasoning_capacity_asks_for_a_proof_not_a_computation(taxo) -> None:
    """Le geste de base depend de la capacite, pas d'un modele unique."""

    assert taxo.capacity_entry_function(
        "Je sais démontrer des inégalités en exploitant la convexité."
    ) == "REASONING"
    assert taxo.capacity_entry_function(
        "Je sais calculer une intégrale en utilisant une primitive."
    ) == "DIRECT_APPLICATION"
    assert taxo.capacity_entry_function(
        "Je sais expliquer pourquoi une forte corrélation ne prouve pas une cause."
    ) == "REASONING"


def test_a_capacity_naming_one_result_is_singular(taxo) -> None:
    assert taxo.is_singular_capacity("Je sais démontrer le théorème de Gauss.")
    assert taxo.is_singular_capacity("Je sais utiliser l'algorithme d'Euclide.")
    assert not taxo.is_singular_capacity(
        "Je sais calculer des probabilités conditionnelles."
    )


def test_ten_direct_applications_are_not_diversity(taxo) -> None:
    dix = [["DIRECT_APPLICATION"]] * 10
    verdict = taxo.diversity_verdict(dix, "Je sais calculer.")
    assert verdict["verdict"] == "REAL_DIVERSITY_GAP"
    assert verdict["missing"] == ["un seul mode d'exercice"]


def test_one_rich_exercise_can_be_enough(taxo) -> None:
    """Ce que compte le contrat, ce sont les fonctions, pas les fichiers."""

    un_seul = [["DIRECT_APPLICATION", "CONTEXT_VARIATION", "REASONING"]]
    assert taxo.diversity_verdict(un_seul, "Je sais calculer.")["verdict"] == (
        "DIVERSITY_SUFFICIENT"
    )


def test_the_transfer_functions_never_include_the_plain_application(taxo) -> None:
    assert taxo.DIRECT not in taxo.TRANSFER_FUNCTIONS
    assert set(taxo.TRANSFER_FUNCTIONS) | {taxo.DIRECT} == set(taxo.FUNCTIONS)
