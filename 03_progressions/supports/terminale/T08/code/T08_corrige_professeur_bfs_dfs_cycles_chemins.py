"""Corrigé professeur TP T08 parcours. Statut pédagogique: needs_review."""
from __future__ import annotations
from collections import deque


def bfs_predecesseurs(graphe: dict[str, list[str]], depart: str) -> dict[str, str | None]:
    if graphe is None or depart not in graphe:
        raise ValueError("départ absent")
    pred: dict[str, str | None] = {depart: None}
    file = deque([depart])
    while file:
        sommet = file.popleft()
        for voisin in graphe[sommet]:
            if voisin not in pred:
                pred[voisin] = sommet
                file.append(voisin)
    return pred


def reconstruire_chemin(pred: dict[str, str | None], depart: str, arrivee: str) -> list[str]:
    if pred is None or depart not in pred:
        raise ValueError("prédécesseurs absents")
    if arrivee not in pred:
        return []
    chemin = [arrivee]
    while chemin[-1] != depart:
        parent = pred[chemin[-1]]
        if parent is None:
            return []
        chemin.append(parent)
    return list(reversed(chemin))


def detecter_cycle_non_oriente(graphe: dict[str, list[str]]) -> bool:
    if graphe is None:
        raise ValueError("graphe absent")
    vus: set[str] = set()
    def dfs(sommet: str, parent: str | None) -> bool:
        vus.add(sommet)
        for voisin in graphe[sommet]:
            if voisin == parent:
                continue
            if voisin in vus or dfs(voisin, sommet):
                return True
        return False
    return any(dfs(s, None) for s in graphe if s not in vus)
