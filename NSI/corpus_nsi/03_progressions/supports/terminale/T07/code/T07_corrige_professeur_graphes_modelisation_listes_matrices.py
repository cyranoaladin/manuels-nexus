"""Corrigé professeur TP T07 graphes. Statut pédagogique: needs_review."""
from __future__ import annotations


def liste_adjacence(aretes: list[tuple[str, str]], oriente: bool = False) -> dict[str, list[str]]:
    if aretes is None:
        raise ValueError("arêtes absentes")
    graphe: dict[str, list[str]] = {}
    for a, b in aretes:
        graphe.setdefault(a, []).append(b)
        graphe.setdefault(b, [])
        if not oriente:
            graphe[b].append(a)
    return {sommet: sorted(voisins) for sommet, voisins in graphe.items()}


def matrice_adjacence(sommets: list[str], aretes: list[tuple[str, str]], oriente: bool = False) -> list[list[int]]:
    if sommets is None or aretes is None:
        raise ValueError("graphe absent")
    index = {sommet: i for i, sommet in enumerate(sommets)}
    matrice = [[0 for _ in sommets] for _ in sommets]
    for a, b in aretes:
        matrice[index[a]][index[b]] = 1
        if not oriente:
            matrice[index[b]][index[a]] = 1
    return matrice


def degre(graphe: dict[str, list[str]], sommet: str) -> int:
    if graphe is None or sommet not in graphe:
        raise ValueError("sommet absent")
    return len(graphe[sommet])
