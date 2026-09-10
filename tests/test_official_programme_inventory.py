"""L'inventaire officiel doit venir du texte du BO, et de rien d'autre.

Ces tests ne verifient pas que les manuels couvrent le programme -- c'est
l'affaire de la matrice de couverture. Ils verifient l'etape d'avant, sans
laquelle cette matrice ne vaudrait rien : que l'inventaire officiel est bien
tire des textes officiels, qu'il n'en perd aucun attendu en chemin, et qu'il
ne fige pas des chiffres qu'un simple ecart de lecture rendrait faux.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "audit" / "OFFICIAL_PROGRAMME_INVENTORY.json"

#: Les six autorites de programme mandatees pour l'edition 2026-2027.
AUTORITES_ATTENDUES = {
    "1SPE": "MENE2602917A",
    "TSPE": "MENE1921246A",
    "TCOMPL": "MENE1921265A",
    "TEXPERTES": "MENE1921264A",
    "1NSI": "MENE1901633A",
    "TNSI": "MENE1921247A",
}
CHAMPS_REQUIS = {
    "official_id",
    "locally_assigned_identifier",
    "manual",
    "authority_ref",
    "official_section",
    "official_rubric",
    "official_wording",
    "kind",
    "mandatory",
    "source_page_or_anchor",
    "effective_from",
    "effective_until",
}


@pytest.fixture(scope="module")
def index():
    return json.loads(INDEX.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def inventaires(index):
    return {
        (e["manual"], e["authority_ref"]): json.loads(
            (ROOT / e["inventory_path"]).read_text(encoding="utf-8")
        )
        for e in index["documents"]
    }


def test_les_six_autorites_sont_exactement_celles_du_mandat(index):
    applicables = {
        e["manual"]: e["authority_ref"]
        for e in index["documents"]
        if e["applies_to_edition"]
    }
    assert applicables == AUTORITES_ATTENDUES
    assert index["OFFICIAL_REFERENCES_VERIFIED"] == "6/6"


def test_une_definition_d_epreuve_n_est_jamais_une_autorite_de_programme(inventaires):
    """MENE2516123N definit l'epreuve de NSI ; elle n'ajoute aucun contenu.

    La confondre avec un programme ferait entrer dans la couverture des
    exigences d'examen qui ne sont pas des attendus d'enseignement.
    """
    for cle, charge in inventaires.items():
        assert charge["authority_namespace"] == "PROGRAMME_D_ENSEIGNEMENT"
        refs = {i["authority_ref"] for i in charge["items"]}
        assert "MENE2516123N" not in refs, cle


def test_aucune_puce_du_texte_officiel_n_est_perdue_en_silence(inventaires):
    """Un extracteur qui jette des lignes ne peut pas servir de reference.

    Chaque puce du corps du programme devient soit un item, soit un rejet
    portant son motif. Le total doit retomber sur le nombre de puces lues.
    """
    for cle, charge in inventaires.items():
        if charge["layout"] != "bullets":
            continue
        c = charge["accounting"]
        assert c["extracted_items"] + c["discarded_bullets"] == c["bullets_in_body"], cle
        assert c["every_body_bullet_accounted_for"] is True
        assert c["bullets_in_body"] > 0, cle


def test_chaque_item_porte_son_ancrage_et_sa_nature(inventaires):
    for cle, charge in inventaires.items():
        for item in charge["items"]:
            assert CHAMPS_REQUIS <= item.keys(), (cle, item["official_id"])
            assert item["official_wording"].strip()
            assert item["kind"]
            assert item["source_page_or_anchor"]
            assert item["manual"] == charge["manual"]
            assert item["authority_ref"] == charge["authority_ref"]


def test_les_identifiants_sont_declares_techniques_et_uniques(inventaires):
    """Le ministere ne publie pas d'identifiant : les notres sont locaux.

    Les presenter autrement laisserait croire a une numerotation officielle
    opposable, alors que la seule reference est le libelle et son ancrage.
    """
    for cle, charge in inventaires.items():
        assert charge["identifiers_are_locally_assigned"] is True
        ids = [i["official_id"] for i in charge["items"]]
        assert len(set(ids)) == len(ids), cle
        assert all(i["locally_assigned_identifier"] is True for i in charge["items"])


def test_le_programme_de_terminale_de_2026_ne_regit_pas_l_edition(index, inventaires):
    """Il s'applique a la rentree 2027, donc pas au manuel 2026-2027.

    Il est extrait quand meme : sans lui, rien ne permettrait de detecter
    qu'un chapitre de terminale s'adosserait par avance a ce texte.
    """
    futurs = [e for e in index["documents"] if not e["applies_to_edition"]]
    assert futurs, "le programme de terminale de 2026 doit rester inventorie"
    for e in futurs:
        assert e["effective_from"] > "2027-01-01"
        charge = inventaires[(e["manual"], e["authority_ref"])]
        assert all(
            i["applies_to_edition_2026_2027"] is False for i in charge["items"]
        )


def test_les_automatismes_de_1spe_sont_une_composante_obligatoire(inventaires):
    """Le programme de 2026 porte une partie « Automatismes » a part entiere.

    La traiter comme un appendice facultatif reviendrait a retirer du
    programme ce que le texte y a mis.
    """
    charge = inventaires[("1SPE", "MENE2602917A")]
    autos = [i for i in charge["items"] if i["kind"] == "AUTOMATISM"]
    assert autos, "aucun automatisme extrait du programme de premiere 2026"
    assert all(i["mandatory"] for i in autos)
    domaines = {i["official_subsection"] for i in autos}
    assert len(domaines) >= 4, domaines
    assert all(d for d in domaines), "un automatisme sans domaine n'est pas exploitable"


def test_un_approfondissement_possible_n_engage_pas_le_manuel(inventaires):
    for cle, charge in inventaires.items():
        for item in charge["items"]:
            if item["kind"] in ("OPTIONAL_ENRICHMENT", "COMMENTARY", "HISTORY_CONTEXT"):
                assert item["mandatory"] is False, (cle, item["official_id"])
            if item["kind"] in ("KNOWLEDGE", "EXPECTED_CAPACITY", "AUTOMATISM"):
                assert item["mandatory"] is True, (cle, item["official_id"])


def test_les_tableaux_nsi_conservent_le_lien_entre_contenu_et_capacite(inventaires):
    """Le BO de NSI place sur une meme ligne un contenu et ses capacites.

    C'est ce lien qui dit quelle connaissance une capacite met en oeuvre ;
    l'export texte du PDF le perdait entierement.
    """
    for cle, charge in inventaires.items():
        if charge["layout"] != "table":
            continue
        liaisons = charge["row_bindings"]
        assert liaisons, cle
        connus = {i["official_id"] for i in charge["items"]}
        lie = 0
        for ligne_ in liaisons:
            for champ in ("knowledge", "expected_capacity", "commentary"):
                assert set(ligne_[champ]) <= connus, (cle, ligne_["official_row"])
            if ligne_["knowledge"] and ligne_["expected_capacity"]:
                lie += 1
        assert lie >= len(liaisons) // 2, cle


def test_l_inventaire_est_bien_regenere_par_son_generateur():
    acheve = subprocess.run(
        [sys.executable, "scripts/build_official_programme_inventory.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert acheve.returncode == 0, acheve.stdout + acheve.stderr


def test_l_inventaire_suit_le_texte_et_ne_recite_pas_un_chiffre_appris():
    """Mutation : ajouter une capacite au texte doit ajouter un item.

    Un compteur fige passerait tous les tests precedents sans jamais avoir lu
    le BO. Celui-ci echoue si l'extraction ne depend pas reellement du texte.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    import extract_official_programme as puces

    source = ROOT / "Mathematiques/manuel-maths/sources/txt/BO2026_1SPE_specialite.txt"
    texte = source.read_text(encoding="utf-8")
    avant = puces.extract(texte, "NOR-TEST", "1SPE")

    ancre = "\nCapacités attendues\n"
    assert ancre in texte
    injecte = texte.replace(
        ancre,
        ancre + " − Capacite ajoutee par le test de mutation.\n",
        1,
    )
    apres = puces.extract(injecte, "NOR-TEST", "1SPE")
    assert len(apres.items) == len(avant.items) + 1
    assert any(
        "mutation" in i["official_wording"] for i in apres.items
    )

    retire = texte.replace(
        " −   Résoudre une équation du second degré.\n", "", 1
    )
    if retire != texte:
        assert len(puces.extract(retire, "NOR-TEST", "1SPE").items) == len(avant.items) - 1


def test_un_titre_de_rubrique_indente_n_est_pas_avale_par_la_puce_precedente():
    """Le BO de 2019 indente ses rubriques autant que ses continuations.

    Sans distinction, « Capacites attendues » se retrouvait colle au libelle
    de la puce qui le precede, et toutes les capacites de la rubrique
    changeaient de nature.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    import extract_official_programme as puces

    texte = (
        "Programme\n"
        "Algèbre\n"
        "  Contenus\n"
        "    Un contenu du programme.\n"
        "  Capacités attendues\n"
        "    Une capacité attendue du programme.\n"
    )
    res = puces.extract(texte, "NOR-TEST", "TEST", section_names=("Algèbre",))
    natures = {i["official_wording"]: i["kind"] for i in res.items}
    assert natures == {
        "Un contenu du programme.": "KNOWLEDGE",
        "Une capacité attendue du programme.": "EXPECTED_CAPACITY",
    }
