"""Corrigé professeur TP P11 parcours et recherche. Statut pédagogique: needs_review."""
from __future__ import annotations


def maximum(valeurs: list[int]) -> int:
    if not valeurs:
        raise ValueError("liste vide")
    meilleur = valeurs[0]
    for valeur in valeurs[1:]:
        if valeur > meilleur:
            meilleur = valeur
    return meilleur


def indices_de(valeurs: list[int], cible: int) -> list[int]:
    resultat: list[int] = []
    for indice, valeur in enumerate(valeurs):
        if valeur == cible:
            resultat.append(indice)
    return resultat


def moyenne(valeurs: list[int]) -> float:
    if not valeurs:
        raise ValueError("liste vide")
    return sum(valeurs) / len(valeurs)
