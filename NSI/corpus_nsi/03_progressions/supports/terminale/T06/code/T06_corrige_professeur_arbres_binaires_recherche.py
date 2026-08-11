"""Corrigé professeur TP T06 ABR. Statut pédagogique: needs_review."""
from __future__ import annotations


def inserer_abr(arbre: dict | None, valeur: int) -> dict:
    if valeur is None:
        raise ValueError("valeur absente")
    if arbre is None:
        return {"valeur": valeur, "gauche": None, "droite": None}
    if valeur == arbre["valeur"]:
        return arbre
    if valeur < arbre["valeur"]:
        arbre["gauche"] = inserer_abr(arbre["gauche"], valeur)
    else:
        arbre["droite"] = inserer_abr(arbre["droite"], valeur)
    return arbre


def rechercher_abr(arbre: dict | None, valeur: int) -> bool:
    if valeur is None:
        raise ValueError("valeur absente")
    if arbre is None:
        return False
    if valeur == arbre["valeur"]:
        return True
    if valeur < arbre["valeur"]:
        return rechercher_abr(arbre["gauche"], valeur)
    return rechercher_abr(arbre["droite"], valeur)


def parcours_infixe(arbre: dict | None) -> list[int]:
    if arbre is None:
        return []
    return parcours_infixe(arbre["gauche"]) + [arbre["valeur"]] + parcours_infixe(arbre["droite"])
