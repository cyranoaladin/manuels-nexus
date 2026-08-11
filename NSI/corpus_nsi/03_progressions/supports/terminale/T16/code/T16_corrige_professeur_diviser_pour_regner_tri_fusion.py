"""Corrigé professeur TP T16 tri fusion. Statut pédagogique: needs_review."""
from __future__ import annotations


def fusionner(gauche: list[int], droite: list[int]) -> list[int]:
    if gauche is None or droite is None:
        raise ValueError("liste absente")
    i = j = 0
    resultat: list[int] = []
    while i < len(gauche) and j < len(droite):
        if gauche[i] <= droite[j]:
            resultat.append(gauche[i]); i += 1
        else:
            resultat.append(droite[j]); j += 1
    return resultat + gauche[i:] + droite[j:]


def tri_fusion(valeurs: list[int]) -> list[int]:
    if valeurs is None:
        raise ValueError("liste absente")
    if len(valeurs) <= 1:
        return list(valeurs)
    milieu = len(valeurs) // 2
    return fusionner(tri_fusion(valeurs[:milieu]), tri_fusion(valeurs[milieu:]))


def nombre_niveaux(n: int) -> int:
    if n < 0:
        raise ValueError("taille invalide")
    niveaux = 0
    taille = max(1, n)
    while taille > 1:
        taille = (taille + 1) // 2
        niveaux += 1
    return niveaux
