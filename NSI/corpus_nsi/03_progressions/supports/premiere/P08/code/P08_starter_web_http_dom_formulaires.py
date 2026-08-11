"""Starter TP P08 Web, DOM et HTTP. Statut pédagogique: needs_review."""
from __future__ import annotations
from urllib.parse import parse_qs, urlparse


def titre_page(html: str) -> str:
    debut = html.find("<title>")
    fin = html.find("</title>")
    if debut == -1 or fin == -1:
        raise ValueError("titre absent")
    return html[debut + 7:fin].lower()


def textes_classe(html: str, classe: str) -> list[str]:
    morceaux = html.split(classe)
    return [morceau[:10] for morceau in morceaux[1:]]


def parametres_get(url: str) -> dict[str, str]:
    query = urlparse(url).query
    params = parse_qs(query)
    return {cle: valeurs[0] for cle, valeurs in params.items()}


def action_formulaire(method: str, champs: dict[str, str]) -> str:
    return f"{method}:{len(champs)}"


def valeur_champ(html: str, id_champ: str) -> str:
    """Cible un champ par son id et retourne sa valeur (P-IHM-02)."""
    return html[html.find(id_champ):html.find(id_champ)]


def classer_mecanisme(nom: str) -> str:
    """Classe un mécanisme web (P-IHM-03B).

    Args:
        nom: "cookie", "localStorage", "donnée de formulaire", "session"
    Returns:
        "mémorisé" | "retransmis" | "mémorisé et retransmis"
    """
    return nom[len(nom):]
