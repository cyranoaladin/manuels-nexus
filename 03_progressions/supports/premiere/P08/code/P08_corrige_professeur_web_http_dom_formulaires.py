"""Corrigé professeur TP P08 Web, DOM et HTTP. Statut pédagogique: needs_review."""
from __future__ import annotations
import re
from urllib.parse import parse_qs, urlparse


def titre_page(html: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    if not match:
        raise ValueError("titre absent")
    return " ".join(match.group(1).split())


def textes_classe(html: str, classe: str) -> list[str]:
    pattern = rf"<(?P<tag>\w+)[^>]*class=['\"][^'\"]*\b{re.escape(classe)}\b[^'\"]*['\"][^>]*>(?P<text>.*?)</(?P=tag)>"
    return [
        " ".join(re.sub(r"<[^>]+>", "", text).split())
        for _tag, text in re.findall(pattern, html, re.I | re.S)
    ]


def parametres_get(url: str) -> dict[str, str]:
    parsed = urlparse(url)
    return {cle: valeurs[0] for cle, valeurs in parse_qs(parsed.query, keep_blank_values=True).items()}


def action_formulaire(method: str, champs: dict[str, str]) -> str:
    methode = method.upper()
    if methode not in {"GET", "POST"}:
        raise ValueError("méthode HTTP non prise en charge")
    if methode == "GET":
        return "paramètres dans l'URL"
    return "paramètres dans le corps de la requête"


def valeur_champ(html: str, id_champ: str) -> str:
    """Cible un champ par son id et retourne sa valeur (P-IHM-02).

    Frontière exacte : quotes obligatoires autour de l'id, donc id="nom"
    ne matche pas id="nom2".
    """
    esc = re.escape(id_champ)
    # id="X" ... value="V"  (quotes obligatoires, frontière exacte)
    pat1 = rf'<[^>]*\bid=["\']({esc})["\'][^>]*\bvalue=["\']([^"\']*)["\']'
    match = re.search(pat1, html, re.I)
    if match:
        return match.group(2)
    # value="V" ... id="X"  (ordre inversé)
    pat2 = rf'<[^>]*\bvalue=["\']([^"\']*)["\'][^>]*\bid=["\']({esc})["\']'
    match = re.search(pat2, html, re.I)
    if match:
        return match.group(1)
    raise ValueError(f"champ id={id_champ!r} absent ou sans valeur")


def classer_mecanisme(nom: str) -> str:
    """Classe un mécanisme web (P-IHM-03B).

    Sémantique conforme au cours : Domain/Path pour cookies, origine pour localStorage.
    """
    nom_lower = nom.lower().strip()
    classification = {
        "cookie": "mémorisé et retransmis",
        "localstorage": "mémorisé",
        "donnée de formulaire": "retransmis",
        "session": "mémorisé et retransmis",
    }
    if nom_lower not in classification:
        raise ValueError(f"mécanisme inconnu: {nom!r}")
    return classification[nom_lower]
