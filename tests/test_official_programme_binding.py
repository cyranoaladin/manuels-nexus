"""Le rattachement au programme doit dire ce qu'il sait et ce qu'il suppose.

Un lien etabli et un lien propose n'ont pas la meme valeur de preuve. Ces
tests verifient que la difference est tenue partout : une proposition ne doit
jamais ressortir avec l'apparence d'un lien etabli, et un attendu officiel
revendique par plusieurs atomes internes ne doit pas etre compte plusieurs
fois -- ce serait gonfler la couverture avec le meme attendu.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BINDING = ROOT / "audit" / "OFFICIAL_PROGRAMME_BINDING.json"
INDEX = ROOT / "audit" / "OFFICIAL_PROGRAMME_INVENTORY.json"

ETABLIS = {"ANCHOR", "VERBATIM"}


@pytest.fixture(scope="module")
def liaison():
    return json.loads(BINDING.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def officiels():
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    items = {}
    for entree in index["documents"]:
        if not entree["applies_to_edition"]:
            continue
        charge = json.loads((ROOT / entree["inventory_path"]).read_text(encoding="utf-8"))
        for item in charge["items"]:
            items[item["official_id"]] = item
    return items


def test_une_proposition_ne_prend_jamais_l_apparence_d_un_lien_etabli(liaison):
    """Sans cela, un rapprochement automatique passerait pour une preuve.

    Une proposition publie ses candidats et sa mesure, jamais un parent : ce
    qui n'a pas ete tranche ne doit pas pouvoir etre lu comme tranche.
    """
    for lien in liaison["bindings"]:
        if lien["binding_method"] == "PROPOSED":
            assert lien["official_id"] is None, lien["atom_id"]
            assert lien["review_status"] == "PROPOSED_REQUIRES_HUMAN_CONFIRMATION"
            assert lien["candidates"], lien["atom_id"]
        if lien["binding_method"] in ETABLIS:
            assert lien["official_id"], lien["atom_id"]
            assert lien["review_status"].startswith("CONFIRMED_BY_")


def test_tout_lien_etabli_designe_un_item_officiel_existant(liaison, officiels):
    for lien in liaison["bindings"]:
        if lien["binding_method"] not in ETABLIS:
            continue
        item = officiels.get(lien["official_id"])
        assert item is not None, lien["atom_id"]
        assert item["manual"] == lien["manual"]
        assert item["kind"] == lien["official_kind"]


def test_un_ancrage_designe_bien_les_coordonnees_qu_il_cite(liaison, officiels):
    """Un ancrage est exact ou il n'est rien.

    S'il pointait a cote, il donnerait une fausse certitude la ou une
    proposition, elle, se serait annoncee comme telle.
    """
    ancres = [b for b in liaison["bindings"] if b["binding_method"] == "ANCHOR"]
    assert ancres, "aucun ancrage : la methode la plus forte serait inutilisee"
    for lien in ancres:
        item = officiels[lien["official_id"]]
        sous, rubrique, puce = [p.strip() for p in lien["source_anchor"].split("/")]
        assert (item["official_subsection"] or item["official_section"]) == sous
        assert item["official_rubric"] == rubrique
        assert puce == f"puce {item['official_rubric_index']}"


def test_les_compteurs_publies_decoulent_des_liens_publies(liaison):
    """Un resume fige passerait au vert sans rien mesurer."""
    liens = liaison["bindings"]
    resume = liaison["summary"]
    etablis = [b for b in liens if b["binding_method"] in ETABLIS]
    assert resume["internal_atoms"] == len(liens)
    assert resume["bound_confirmed"] == len(etablis)
    assert resume["bound_proposed"] == sum(
        1 for b in liens if b["binding_method"] == "PROPOSED"
    )
    assert resume["INTERNAL_ATOM_WITHOUT_OFFICIAL_PARENT"] == len(liens) - len(etablis)
    assert resume["bound_confirmed"] + resume["bound_proposed"] + resume["unbound"] == len(liens)


def test_un_meme_attendu_officiel_n_est_jamais_compte_deux_fois(liaison, officiels):
    """Le referentiel interne decoupe parfois un attendu en deux atomes.

    « Calculer la taille et la hauteur d'un arbre » devient deux capacites
    internes. C'est un choix pedagogique legitime, mais il ne rend pas le
    programme plus couvert : le denominateur reste celui du BO.
    """
    for manuel, resume in liaison["per_manual"].items():
        revendiques = {
            b["official_id"] for b in liaison["bindings"]
            if b["manual"] == manuel and b["binding_method"] in ETABLIS
        }
        obligatoires = {
            oid for oid, item in officiels.items()
            if item["manual"] == manuel and item["mandatory"]
        }
        attendu = len(revendiques & obligatoires)
        assert resume["official_mandatory_bound_confirmed"] == attendu, manuel
        assert resume["OFFICIAL_REQUIRED_UNMAPPED"] == len(obligatoires) - attendu
        assert attendu <= resume["official_mandatory"]


def test_une_definition_d_epreuve_n_est_jamais_invoquee_comme_programme(liaison):
    assert liaison["summary"]["AUTHORITY_NAMESPACE_VIOLATION"] == 0
    assert liaison["authority_namespace_violations"] == []


def test_aucun_referentiel_ne_s_appuie_sur_le_programme_d_une_autre_annee(liaison):
    assert liaison["summary"]["WRONG_YEAR_USED_AS_AUTHORITY"] == 0, (
        liaison["wrong_year_citations"]
    )


def test_le_rattachement_est_bien_regenere_par_son_generateur():
    acheve = subprocess.run(
        [sys.executable, "scripts/build_official_programme_binding.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert acheve.returncode == 0, acheve.stdout + acheve.stderr


def test_un_libelle_reecrit_perd_son_statut_de_lien_etabli():
    """Mutation : le mot-pour-mot doit reellement comparer les deux textes.

    Si l'egalite etait fictive, tout atome ressortirait « etabli » sans que
    personne ne s'en apercoive.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_official_programme_binding as jointure

    officiels, _ = jointure.charger_officiels()
    atomes = jointure.charger_atomes()
    verbatim = [
        a for a in atomes
        if jointure.lier(a, officiels.get(a["manual"] or "", []))["binding_method"]
        == "VERBATIM"
    ]
    assert verbatim, "aucun libelle repris mot pour mot : la methode est morte"

    temoin = dict(verbatim[0])
    temoin["libelle_interne"] = "Libelle reecrit par le test de mutation."
    apres = jointure.lier(temoin, officiels[temoin["manual"]])
    assert apres["binding_method"] != "VERBATIM"
    assert apres["official_id"] is None


def test_la_typographie_du_bo_ne_fait_pas_passer_une_identite_pour_une_reformulation():
    """L'apostrophe courbe et le ƒ du BO ne changent pas l'attendu.

    Comparer caractere pour caractere renvoyait vers un arbitrage humain des
    phrases rigoureusement identiques au texte officiel.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_official_programme_binding as jointure

    assert jointure.forme_typographique("Résoudre un problème d’optimisation.") == (
        jointure.forme_typographique("Résoudre un problème d'optimisation.")
    )
    assert jointure.forme_typographique("ƒ (a + h)") == (
        jointure.forme_typographique("f(a+h)")
    )
    assert jointure.forme_typographique("Calculer la taille.") != (
        jointure.forme_typographique("Calculer la hauteur.")
    )
