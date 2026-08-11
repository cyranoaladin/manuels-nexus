"""Tests attendus TP P08. Statut pédagogique: needs_review."""
from __future__ import annotations
import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "P08_starter_web_http_dom_formulaires"))
HTML = "<html><head><title>Mini site NSI</title></head><body><p class='alerte'>Erreur</p><p class='ok'>Valide</p></body></html>"


def test_nominal_html_dom_get_post() -> None:
    assert MODULE.titre_page(HTML) == "Mini site NSI"
    assert MODULE.textes_classe(HTML, "alerte") == ["Erreur"]
    assert MODULE.parametres_get("https://nsi.test/recherche?q=tri&page=2") == {"q": "tri", "page": "2"}
    assert MODULE.action_formulaire("POST", {"nom": "Ada"}) == "paramètres dans le corps de la requête"


def test_limites_classe_absente_et_get_vide() -> None:
    assert MODULE.textes_classe(HTML, "absente") == []
    assert MODULE.parametres_get("https://nsi.test/recherche") == {}
    assert MODULE.action_formulaire("GET", {"q": "tri"}) == "paramètres dans l'URL"


def test_entrees_invalides() -> None:
    title_absent_refuse = False
    try:
        MODULE.titre_page("<html></html>")
    except ValueError:
        title_absent_refuse = True
    if not title_absent_refuse:
        raise AssertionError("ValueError attendue pour title absent")
    try:
        MODULE.action_formulaire("TRACE", {})
    except ValueError:
        return
    raise AssertionError("ValueError attendue pour méthode interdite")


def test_valeur_champ_cible_par_id() -> None:
    html_form = '<form><input id="nom" name="nom" value="Ada"><input id="age" value="36"></form>'
    assert MODULE.valeur_champ(html_form, "nom") == "Ada"
    assert MODULE.valeur_champ(html_form, "age") == "36"


def test_valeur_champ_frontiere_id_exacte() -> None:
    html_adverse = '<form><input id="nom2" value="Bob"><input id="nom" value="Ada"></form>'
    assert MODULE.valeur_champ(html_adverse, "nom") == "Ada"
    assert MODULE.valeur_champ(html_adverse, "nom2") == "Bob"


def test_valeur_champ_absent_leve_erreur() -> None:
    html_form = '<form><input id="nom" value="Ada"></form>'
    try:
        MODULE.valeur_champ(html_form, "inexistant")
        assert False, "ValueError attendue"
    except ValueError:
        return
    raise AssertionError("ValueError attendue pour champ absent")


def test_classer_mecanisme_cookie_memorise_et_retransmis() -> None:
    assert MODULE.classer_mecanisme("cookie") == "mémorisé et retransmis"


def test_classer_mecanisme_localstorage_memorise_seulement() -> None:
    assert MODULE.classer_mecanisme("localStorage") == "mémorisé"


def test_classer_mecanisme_formulaire_retransmis() -> None:
    assert MODULE.classer_mecanisme("donnée de formulaire") == "retransmis"


def test_classer_mecanisme_session_memorise_et_retransmis() -> None:
    assert MODULE.classer_mecanisme("session") == "mémorisé et retransmis"


def test_classer_mecanisme_inconnu_leve_erreur() -> None:
    try:
        MODULE.classer_mecanisme("websocket")
        assert False, "ValueError attendue"
    except ValueError:
        return
    raise AssertionError("ValueError attendue pour mécanisme inconnu")


if __name__ == "__main__":
    test_nominal_html_dom_get_post()
    test_limites_classe_absente_et_get_vide()
    test_entrees_invalides()
    test_valeur_champ_cible_par_id()
    test_valeur_champ_frontiere_id_exacte()
    test_valeur_champ_absent_leve_erreur()
    test_classer_mecanisme_cookie_memorise_et_retransmis()
    test_classer_mecanisme_localstorage_memorise_seulement()
    test_classer_mecanisme_formulaire_retransmis()
    test_classer_mecanisme_session_memorise_et_retransmis()
    test_classer_mecanisme_inconnu_leve_erreur()
    print("tests attendus OK")
