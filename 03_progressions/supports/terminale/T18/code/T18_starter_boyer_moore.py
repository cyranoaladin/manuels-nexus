"""Starter TP T18 Boyer-Moore. Statut pédagogique: needs_review."""
from __future__ import annotations


def table_mauvais_caractere(motif: str) -> dict[str, int]:
    table: dict[str, int] = {}
    for indice, caractere in enumerate(motif):
        table[caractere] = indice
    return table


def boyer_moore(texte: str, motif: str) -> int:
    if not motif:
        raise ValueError("motif vide")
    return texte.find(motif[0])


def trace_decalages(texte: str, motif: str) -> list[int]:
    if not motif:
        raise ValueError("motif vide")
    return list(range(len(texte)))
