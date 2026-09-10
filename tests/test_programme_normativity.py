"""La portee normative doit venir du BO, pas de l'etiquette interne.

Un type interne ne doit jamais pouvoir relever silencieusement le niveau
d'obligation d'un attendu. Ces tests verrouillent la chaine
intitule -> sous-intitule -> puce -> portee, et verifient qu'elle depend bien
de ce que le programme imprime.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import programme_normativity as pn  # noqa: E402

INDEX = ROOT / "audit" / "OFFICIAL_PROGRAMME_INVENTORY.json"


@pytest.fixture(scope="module")
def items():
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    trouves = []
    for entree in index["documents"]:
        charge = json.loads((ROOT / entree["inventory_path"]).read_text(encoding="utf-8"))
        trouves.extend(charge["items"])
    return trouves


def test_chaque_item_porte_l_intitule_la_portee_et_l_etiquette(items):
    """Les trois doivent voyager ensemble, sinon la portee n'est pas verifiable."""
    for item in items:
        assert item["official_normativity"] in pn.NORMATIVITIES, item["official_id"]
        assert item["local_kind"], item["official_id"]
        assert item["normativity_basis"], item["official_id"]
        assert "official_heading" in item, item["official_id"]


def test_l_obligation_decoule_de_la_portee_et_de_rien_d_autre(items):
    for item in items:
        attendu = item["official_normativity"] in pn.MANDATORY_NORMATIVITIES
        assert item["mandatory"] is attendu, item["official_id"]


def test_un_approfondissement_possible_n_est_jamais_obligatoire(items):
    """Le BO l'ecrit : « en aucun cas obligatoires ».

    C'est la phrase la plus explicite du programme sur la normativite ; si
    l'inventaire la contredisait, plus aucune de ses portees ne serait fiable.
    """
    enrichissements = [
        i for i in items if i["official_normativity"] == pn.OPTIONAL_ENRICHMENT
    ]
    assert enrichissements
    assert all(i["mandatory"] is False for i in enrichissements)
    assert all("en aucun cas obligatoires" in i["normativity_basis"] for i in enrichissements)


def test_un_exemple_d_algorithme_n_entre_pas_au_denominateur(items):
    """Le BO intitule cette rubrique « Exemples d'algorithme ».

    Aucun passage du texte ne les rend exigibles : ni l'organisation du
    programme, ni la partie « Algorithmique et programmation ». Les compter
    comme obligatoires reviendrait a fabriquer un niveau d'obligation que le
    ministere n'a pas ecrit -- et a exiger du manuel qu'il implemente
    exactement l'algorithme cite.

    Que la partie concernee comporte un travail algorithmique reel est une
    exigence de la collection, controlee sous son propre nom.
    """
    exemples = [i for i in items if i["local_kind"] == "ALGORITHM_EXAMPLE"]
    assert exemples
    for item in exemples:
        assert item["official_normativity"] == pn.ILLUSTRATIVE_EXAMPLE
        assert item["mandatory"] is False
        assert item["exact_example_imposed"] is False
        assert "Exemple" in (item["official_heading"] or "")


def test_les_automatismes_relevent_de_la_partie_et_non_de_la_rubrique():
    """Dans « Automatismes », le BO intitule ses listes « Capacites attendues ».

    Lire la rubrique seule effacerait ce que la partie ajoute : un
    entrainement reparti sur l'annee, et non un chapitre. La partie doit donc
    primer sur la rubrique.
    """
    seule = pn.resolve(None, "Capacités attendues")
    dans_automatismes = pn.resolve("Automatismes", "Capacités attendues")
    assert seule.normativity == pn.EXPECTED_CAPACITY
    assert dans_automatismes.normativity == pn.REQUIRED_AUTOMATISM
    assert dans_automatismes.mandatory is True


def test_mutation_deplacer_une_puce_change_sa_normativite():
    """Mutation : la portee suit-elle vraiment l'intitule qui surplombe la puce ?

    Si la normativite etait attachee au libelle plutot qu'a sa place dans le
    texte, un enrichissement facultatif deplace sous « Capacites attendues »
    resterait facultatif -- et le denominateur pourrait etre modifie sans que
    rien ne le signale.
    """
    import extract_official_programme as puces

    gabarit = (
        "Programme\n"
        "Algèbre\n"
        "Sous-partie de test\n"
        "{rubrique}\n"
        " − Une puce dont la portee est mise a l'epreuve.\n"
    )
    facultatif = puces.extract(
        gabarit.format(rubrique="Approfondissements possibles"),
        "NOR-TEST",
        "TEST",
        section_names=("Algèbre",),
    )
    obligatoire = puces.extract(
        gabarit.format(rubrique="Capacités attendues"),
        "NOR-TEST",
        "TEST",
        section_names=("Algèbre",),
    )
    assert len(facultatif.items) == len(obligatoire.items) == 1
    avant, apres = facultatif.items[0], obligatoire.items[0]
    assert avant["official_wording"] == apres["official_wording"]
    assert avant["official_normativity"] == pn.OPTIONAL_ENRICHMENT
    assert avant["mandatory"] is False
    assert apres["official_normativity"] == pn.EXPECTED_CAPACITY
    assert apres["mandatory"] is True
    assert avant["official_id"] != apres["official_id"]


def test_aucune_etiquette_interne_ne_cree_une_portee_inconnue(items):
    """Une portee hors vocabulaire echapperait a toute regle de comptage."""
    portees = {i["official_normativity"] for i in items}
    assert portees <= pn.NORMATIVITIES, sorted(portees - pn.NORMATIVITIES)
