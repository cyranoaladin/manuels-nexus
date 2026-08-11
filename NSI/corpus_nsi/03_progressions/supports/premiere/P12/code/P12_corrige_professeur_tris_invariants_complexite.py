"""Corrigé professeur TP P12 tris. Statut pédagogique: needs_review."""
from __future__ import annotations


def inserer_dans_partie_triee(valeurs: list[int], index: int) -> list[int]:
    if valeurs is None or index < 0 or index >= len(valeurs):
        raise ValueError("index invalide")
    resultat = list(valeurs)
    cle = resultat[index]
    j = index - 1
    while j >= 0 and resultat[j] > cle:
        resultat[j + 1] = resultat[j]
        j -= 1
    resultat[j + 1] = cle
    return resultat


def indice_minimum_suffixe(valeurs: list[int], debut: int) -> int:
    if valeurs is None or debut < 0 or debut >= len(valeurs):
        raise ValueError("début invalide")
    indice = debut
    for i in range(debut + 1, len(valeurs)):
        if valeurs[i] < valeurs[indice]:
            indice = i
    return indice


def tri_selection(valeurs: list[int]) -> list[int]:
    if valeurs is None:
        raise ValueError("liste absente")
    resultat = list(valeurs)
    for i in range(len(resultat)):
        j = indice_minimum_suffixe(resultat, i)
        resultat[i], resultat[j] = resultat[j], resultat[i]
    return resultat
