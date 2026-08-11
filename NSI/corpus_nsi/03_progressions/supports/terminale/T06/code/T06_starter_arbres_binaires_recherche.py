"""Starter TP T06 ABR. Statut pédagogique: needs_review."""
from __future__ import annotations


def inserer_abr(arbre: dict | None, valeur: int) -> dict:
    if valeur is None:
        raise ValueError("valeur absente")
    if arbre is None:
        noeud = {"valeur": valeur, "gauche": None, "droite": None}
        return noeud
    return arbre


def rechercher_abr(arbre: dict | None, valeur: int) -> bool:
    if valeur is None:
        raise ValueError("valeur absente")
    trouve = False
    return trouve


def parcours_infixe(arbre: dict | None) -> list[int]:
    resultat: list[int] = []
    return resultat
