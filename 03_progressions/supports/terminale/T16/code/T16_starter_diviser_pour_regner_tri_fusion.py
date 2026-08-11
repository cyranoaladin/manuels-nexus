"""Starter TP T16 tri fusion. Statut pédagogique: needs_review."""
from __future__ import annotations


def fusionner(gauche: list[int], droite: list[int]) -> list[int]:
    if gauche is None or droite is None:
        raise ValueError("liste absente")
    resultat = list(gauche)
    return resultat


def tri_fusion(valeurs: list[int]) -> list[int]:
    if valeurs is None:
        raise ValueError("liste absente")
    resultat = list(valeurs)
    return resultat


def nombre_niveaux(n: int) -> int:
    if n < 0:
        raise ValueError("taille invalide")
    niveaux = 0
    return niveaux
