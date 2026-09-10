"""Dix mutations adverses : la chaine mesure-t-elle vraiment ce qu'elle affirme ?

Chacune introduit une faute precise et exige que la chaine la voie. Un test qui
passe sur des donnees saines ne prouve rien : il prouve seulement qu'aucune
faute n'a ete tentee. Les deux dernieres mutations sont les plus importantes,
parce qu'elles verrouillent la separation des deux matrices -- le rattachement
au BO ne prouve pas le manuel, et le manuel n'a pas besoin du rattachement.
"""
import json
import sys
from collections import Counter
from pathlib import Path



ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_official_programme_binding as jointure  # noqa: E402
import build_official_to_manual_coverage as couverture  # noqa: E402
import programme_normativity as pn  # noqa: E402
from manual_objects import Objet  # noqa: E402

INVENTAIRE = ROOT / "audit" / "OFFICIAL_PROGRAMME_INVENTORY.json"
COVERAGE = ROOT / "audit" / "OFFICIAL_TO_MANUAL_COVERAGE.json"
BINDING = ROOT / "audit" / "OFFICIAL_PROGRAMME_BINDING.json"
AUTOMATISMES = ROOT / "audit" / "1SPE_AUTOMATISMS_AUDIT.json"


def _roles(**compte: int) -> Counter:
    return Counter({cle: valeur for cle, valeur in compte.items() if valeur})


# ---------------------------------------------------------------- A


def test_mutation_a_un_attendu_prive_de_ses_objets_devient_manquant():
    """Retirer les objets qui portent un attendu doit le faire tomber.

    Si le verdict ne dependait pas des objets, la matrice afficherait une
    couverture qui ne repose sur rien.
    """
    avant, _ = couverture.verdict(
        pn.REQUIRED_CONTENT,
        _roles(PRIMARY_TEACHING=1, REINVESTMENT=4),
        {"CHAP-A", "CHAP-B"},
        False,
        False,
    )
    apres, motif = couverture.verdict(
        pn.REQUIRED_CONTENT, _roles(), set(), False, False
    )
    assert avant == "COMPLETE"
    assert apres == "MISSING"
    assert "aucun objet" in motif


# ---------------------------------------------------------------- B


def test_mutation_b_un_rapprochement_par_mots_communs_n_est_pas_confirme():
    """Un atome bourre de mots courants ne doit pas capturer un attendu.

    Sans cette barriere, il suffirait d'ecrire une capacite avec les bons mots
    pour se declarer conforme.
    """
    officiels, _ = jointure.charger_officiels()
    faux = {
        "atom_id": "FAUX-MOTS-CLES",
        "manual": "1SPE",
        "theme": "THEME-INEXISTANT",
        "referential_path": "test",
        "bo_reference": "",
        "declared_authority": None,
        "libelle_interne": (
            "Utiliser une fonction pour determiner une valeur en calculant "
            "un nombre a partir de deux points"
        ),
        "libelle_bo_is_verbatim": False,
        "contenu_bo": None,
        "source_anchor": None,
    }
    lien = jointure.lier(faux, officiels["1SPE"])
    assert lien["binding_method"] not in ("ANCHOR", "VERBATIM")
    relu = jointure.relire_par_contexte(
        {**faux, **lien}, officiels["1SPE"], None
    )
    assert relu["review_status"] == "AMBIGUOUS_REQUIRES_HUMAN"
    assert relu.get("official_id") is None


# ---------------------------------------------------------------- C


def test_mutation_c_un_attendu_du_programme_futur_n_entre_pas_au_denominateur():
    """Le programme de terminale de 2026 s'applique a la rentree 2027.

    Compter ses attendus dans l'edition 2026-2027 ferait porter au manuel des
    exigences qui ne le regissent pas encore.
    """
    index = json.loads(INVENTAIRE.read_text(encoding="utf-8"))
    futurs = [e for e in index["documents"] if not e["applies_to_edition"]]
    assert futurs
    ids_futurs = set()
    for entree in futurs:
        charge = json.loads((ROOT / entree["inventory_path"]).read_text(encoding="utf-8"))
        ids_futurs.update(i["official_id"] for i in charge["items"])
    lignes = json.loads(COVERAGE.read_text(encoding="utf-8"))["rows"]
    assert ids_futurs
    assert not (ids_futurs & {r["official_id"] for r in lignes})


# ---------------------------------------------------------------- D


def test_mutation_d_la_definition_d_epreuve_ne_devient_pas_un_programme():
    """MENE2516123N fixe des modalites, jamais des contenus.

    L'invoquer comme programme ferait entrer dans la couverture des exigences
    d'examen qui ne sont pas des attendus d'enseignement.
    """
    index = json.loads(INVENTAIRE.read_text(encoding="utf-8"))
    autorites = {e["authority_ref"] for e in index["documents"]}
    assert "MENE2516123N" not in autorites
    lignes = json.loads(COVERAGE.read_text(encoding="utf-8"))["rows"]
    assert "MENE2516123N" not in {r["authority_ref"] for r in lignes}


# ---------------------------------------------------------------- E


def test_mutation_e_un_atome_sans_parent_est_signale_et_classe():
    """Un atome qui ne repond a aucun attendu ne doit pas passer inapercu."""
    officiels, _ = jointure.charger_officiels()
    orphelin = {
        "atom_id": "ORPHELIN-TEST",
        "manual": "1SPE",
        "theme": "THEME-INEXISTANT",
        "referential_path": "test",
        "bo_reference": "",
        "declared_authority": None,
        "libelle_interne": "Zorglub farfelu sans rapport aucun avec le programme.",
        "libelle_bo_is_verbatim": False,
        "contenu_bo": None,
        "source_anchor": None,
    }
    lien = jointure.lier(orphelin, officiels["1SPE"])
    assert lien["binding_method"] == "NONE"
    classement = jointure.classer_residu({**orphelin, **lien}, officiels, {})
    assert classement["residual_classification"] in {
        "OBSOLETE_INTERNAL_ATOM",
        "PEDAGOGICAL_SUBDIVISION",
        "OFFICIAL_CHILD",
        "ENRICHMENT",
        "WRONG_YEAR",
    }
    assert classement["residual_evidence"]


# ---------------------------------------------------------------- F


def test_mutation_f_un_automatisme_ramene_a_un_chapitre_cesse_d_etre_entretenu():
    """Le programme exclut qu'un automatisme fasse l'objet d'un chapitre."""
    reparti, _ = couverture.verdict(
        pn.REQUIRED_AUTOMATISM,
        _roles(REINVESTMENT=12, ASSESSMENT=2),
        {"CHAP-A", "CHAP-B", "CHAP-C"},
        False,
        False,
    )
    concentre, motif = couverture.verdict(
        pn.REQUIRED_AUTOMATISM,
        _roles(REINVESTMENT=12, ASSESSMENT=2),
        {"CHAP-A"},
        False,
        False,
    )
    assert reparti == "COMPLETE"
    assert concentre == "PARTIAL"
    assert "reparti" in motif or "concentre" in motif


# ---------------------------------------------------------------- G


def test_mutation_g_un_enrichissement_ne_gonfle_pas_la_couverture():
    """« Le programme propose des approfondissements, en aucun cas obligatoires. »

    Les faire entrer au denominateur, ou les compter comme couverture,
    presenterait un manuel plus conforme qu'il ne l'est.
    """
    obligatoire = pn.resolve(None, "Capacités attendues")
    facultatif = pn.resolve(None, "Approfondissements possibles")
    assert obligatoire.mandatory is True
    assert facultatif.mandatory is False

    statut, _ = couverture.verdict(
        pn.OPTIONAL_ENRICHMENT,
        _roles(PRIMARY_TEACHING=3, REINVESTMENT=9),
        {"CHAP-A", "CHAP-B"},
        True,
        True,
    )
    assert statut == "OUT_OF_SCOPE_ENRICHMENT"

    lignes = json.loads(COVERAGE.read_text(encoding="utf-8"))["rows"]
    enrichissements = [
        r for r in lignes if r["official_normativity"] == pn.OPTIONAL_ENRICHMENT
    ]
    assert enrichissements
    assert not any(r["mandatory"] for r in enrichissements)
    assert not any(r["coverage_status"] == "COMPLETE" for r in enrichissements)


# ---------------------------------------------------------------- H


def test_mutation_h_une_assignation_multiple_non_justifiee_est_comptee():
    """Le meme attendu revendique par deux chapitres doit rester visible.

    Il ne compte qu'une fois dans la couverture -- sans quoi deux chapitres
    couvriraient deux fois le meme programme -- et l'ecart doit etre signale.
    """
    liaison = json.loads(BINDING.read_text(encoding="utf-8"))
    multiples = liaison["multiple_assignment"]
    assert liaison["summary"]["UNJUSTIFIED_MULTIPLE_ASSIGNMENT"] == len(multiples)
    for oid, themes in multiples.items():
        assert len(themes) > 1, oid

    lignes = json.loads(COVERAGE.read_text(encoding="utf-8"))["rows"]
    par_id = {r["official_id"]: r for r in lignes}
    for oid in multiples:
        assert oid in par_id
        assert sum(1 for r in lignes if r["official_id"] == oid) == 1


# ---------------------------------------------------------------- I


def test_mutation_i_une_connaissance_sans_atome_mais_avec_cours_est_couverte():
    """L'atome interne n'est pas une condition de conformite.

    Si la chaine l'exigeait, toutes les connaissances du programme
    ressortiraient comme manquantes alors qu'elles sont enseignees -- et il
    faudrait fabriquer des centaines d'atomes vides pour faire tomber un
    compteur.
    """
    statut, motif = couverture.verdict(
        pn.REQUIRED_CONTENT,
        _roles(PRIMARY_TEACHING=1),
        set(),
        False,
        False,
    )
    assert statut == "COMPLETE"
    assert "cours" in motif

    lignes = json.loads(COVERAGE.read_text(encoding="utf-8"))["rows"]
    sans_atome = [
        r for r in lignes
        if r["mandatory"] and not r["internal_atoms"] and r["coverage_status"] == "COMPLETE"
    ]
    assert sans_atome, "aucune connaissance couverte sans atome : l'atome serait requis"


# ---------------------------------------------------------------- J


def test_mutation_j_un_atome_bien_lie_mais_sans_cours_ne_prouve_pas_le_manuel():
    """La mutation la plus importante : les deux matrices sont independantes.

    Un atome parfaitement rattache au BO peut ne rien avoir derriere lui. Si
    le rattachement suffisait a prouver la couverture, il suffirait d'ecrire un
    referentiel pour declarer un manuel conforme.
    """
    officiels, _ = jointure.charger_officiels()
    # Cote rattachement : un atome qui reprend mot pour mot un attendu est
    # etabli, sans qu'aucun objet n'existe.
    modele = next(i for i in officiels["1SPE"] if i["mandatory"])
    atome = {
        "atom_id": "LIE-MAIS-SANS-COURS",
        "manual": "1SPE",
        "theme": "THEME-TEST",
        "referential_path": "test",
        "bo_reference": "",
        "declared_authority": None,
        "libelle_interne": modele["official_wording"],
        "libelle_bo_is_verbatim": True,
        "contenu_bo": None,
        "source_anchor": None,
    }
    lien = jointure.lier(atome, officiels["1SPE"])
    assert lien["binding_method"] == "VERBATIM"
    assert lien["official_id"] == modele["official_id"]

    # Cote couverture : aucun objet, donc rien de prouve.
    statut, motif = couverture.verdict(
        modele["official_normativity"], _roles(), set(), False, False
    )
    assert statut == "MISSING"
    assert "aucun objet" in motif


# ---------------------------------------------------------------- garde-fous


def test_les_dix_mutations_sont_bien_presentes():
    """Le compte est verifie : une mutation supprimee doit se voir."""
    presentes = [
        nom for nom in globals()
        if nom.startswith("test_mutation_")
    ]
    assert len(presentes) == 10, sorted(presentes)


def test_un_objet_de_test_ne_contamine_aucun_artefact_publie():
    """Les mutations vivent en memoire et ne touchent pas le depot."""
    temoin = Objet(
        object_id="OBJET-DE-MUTATION",
        chapter="CHAP-TEST",
        manual="1SPE",
        kind="cours",
        role="PRIMARY_TEACHING",
        path="inexistant.tex",
    )
    lignes = json.loads(COVERAGE.read_text(encoding="utf-8"))["rows"]
    tous = {
        oid
        for r in lignes
        for role in r["objects_by_role"]
        for oid in r["objects_by_role"][role]
    }
    assert temoin.object_id not in tous
    automatismes = json.loads(AUTOMATISMES.read_text(encoding="utf-8"))
    assert all(
        temoin.object_id not in x["PRACTICE_EVIDENCE"]
        for x in automatismes["automatisms"]
    )
