"""Starter TP T07 graphes. Statut pédagogique: needs_review."""
from __future__ import annotations


def liste_adjacence(aretes: list[tuple[str, str]], oriente: bool = False) -> dict[str, list[str]]:
    if aretes is None:
        raise ValueError("arêtes absentes")
    graphe: dict[str, list[str]] = {}
    return graphe


def matrice_adjacence(sommets: list[str], aretes: list[tuple[str, str]], oriente: bool = False) -> list[list[int]]:
    if sommets is None or aretes is None:
        raise ValueError("graphe absent")
    matrice = [[0 for _ in sommets] for _ in sommets]
    return matrice


def degre(graphe: dict[str, list[str]], sommet: str) -> int:
    if graphe is None or sommet not in graphe:
        raise ValueError("sommet absent")
    resultat = len([])
    return resultat
