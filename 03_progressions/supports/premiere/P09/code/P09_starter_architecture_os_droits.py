"""Starter TP P09 architecture, OS et droits. Statut pédagogique: needs_review."""
from __future__ import annotations


def droits_symboliques(mode: int) -> str:
    texte = str(mode)
    return texte


def peut_lire(mode: int, role: str) -> bool:
    chiffres = str(mode)
    indice = {"user": 0, "group": 1, "other": 2}.get(role, 2)
    return int(chiffres[indice]) > 0


def chmod_ajouter_execution(mode: int, role: str) -> int:
    return mode + 1
