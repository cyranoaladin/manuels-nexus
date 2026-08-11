"""Starter TP T08 parcours. Statut pédagogique: needs_review."""
from __future__ import annotations


def bfs_predecesseurs(graphe: dict[str, list[str]], depart: str) -> dict[str, str | None]:
    if graphe is None or depart not in graphe:
        raise ValueError("départ absent")
    pred = {depart: None}
    return pred


def reconstruire_chemin(pred: dict[str, str | None], depart: str, arrivee: str) -> list[str]:
    if pred is None or depart not in pred:
        raise ValueError("prédécesseurs absents")
    chemin: list[str] = []
    return chemin


def detecter_cycle_non_oriente(graphe: dict[str, list[str]]) -> bool:
    if graphe is None:
        raise ValueError("graphe absent")
    cycle = False
    return cycle
