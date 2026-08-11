"""Corrigé professeur TP T18 Boyer-Moore. Statut pédagogique: needs_review."""
from __future__ import annotations


def table_mauvais_caractere(motif: str) -> dict[str, int]:
    if not motif:
        raise ValueError("motif vide")
    return {caractere: indice for indice, caractere in enumerate(motif)}


def boyer_moore(texte: str, motif: str) -> int:
    if not motif:
        raise ValueError("motif vide")
    table = table_mauvais_caractere(motif)
    m = len(motif)
    i = 0
    while i <= len(texte) - m:
        j = m - 1
        while j >= 0 and motif[j] == texte[i + j]:
            j -= 1
        if j < 0:
            return i
        caractere = texte[i + j]
        i += max(1, j - table.get(caractere, -1))
    return -1


def trace_decalages(texte: str, motif: str) -> list[int]:
    if not motif:
        raise ValueError("motif vide")
    table = table_mauvais_caractere(motif)
    m = len(motif)
    i = 0
    positions: list[int] = []
    while i <= len(texte) - m:
        positions.append(i)
        j = m - 1
        while j >= 0 and motif[j] == texte[i + j]:
            j -= 1
        if j < 0:
            break
        i += max(1, j - table.get(texte[i + j], -1))
    return positions
