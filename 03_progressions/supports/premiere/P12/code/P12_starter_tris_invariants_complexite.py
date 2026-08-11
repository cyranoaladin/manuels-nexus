"""Starter TP P12 tris. Statut pédagogique: needs_review."""
from __future__ import annotations


def inserer_dans_partie_triee(valeurs: list[int], index: int) -> list[int]:
    if valeurs is None or index < 0 or index >= len(valeurs):
        raise ValueError("index invalide")
    resultat = list(valeurs)
    return resultat


def indice_minimum_suffixe(valeurs: list[int], debut: int) -> int:
    if valeurs is None or debut < 0 or debut >= len(valeurs):
        raise ValueError("début invalide")
    indice = debut
    return indice


def tri_selection(valeurs: list[int]) -> list[int]:
    if valeurs is None:
        raise ValueError("liste absente")
    resultat = list(valeurs)
    return resultat
