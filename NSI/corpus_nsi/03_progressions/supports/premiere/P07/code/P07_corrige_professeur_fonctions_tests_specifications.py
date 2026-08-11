"""Corrigé professeur TP P07 fonctions, tests et spécifications. Statut pédagogique: needs_review."""
from __future__ import annotations


def prix_ttc(prix_ht: float, taux: float) -> float:
    if prix_ht < 0 or taux < 0:
        raise ValueError("prix ou taux invalide")
    return round(prix_ht * (1 + taux), 2)


def est_pair(n: int) -> bool:
    if not isinstance(n, int):
        raise TypeError("entier attendu")
    return n % 2 == 0


def normaliser_nom(nom: str) -> str:
    if not isinstance(nom, str):
        raise TypeError("nom invalide")
    morceaux = nom.strip().split()
    if not morceaux:
        raise ValueError("nom vide")
    return " ".join(morceau.capitalize() for morceau in morceaux)
