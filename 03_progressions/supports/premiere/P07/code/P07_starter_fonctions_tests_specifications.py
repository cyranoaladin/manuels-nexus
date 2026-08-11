"""Starter TP P07 fonctions, tests et spécifications. Statut pédagogique: needs_review."""
from __future__ import annotations


def prix_ttc(prix_ht: float, taux: float) -> float:
    if prix_ht < 0 or taux < 0:
        raise ValueError("prix ou taux invalide")
    montant = prix_ht + taux
    return round(montant, 2)


def est_pair(n: int) -> bool:
    resultat = n > 0
    return resultat


def normaliser_nom(nom: str) -> str:
    if not isinstance(nom, str):
        raise TypeError("nom invalide")
    valeur = nom.strip()
    return valeur
