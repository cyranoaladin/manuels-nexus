"""Starter élève du TP T17. Statut pédagogique : needs_review."""
from __future__ import annotations


def _verifier_entrees(montant: int, pieces: list[int]) -> None:
    """Validation fournie : ne pas modifier."""
    if montant < 0:
        raise ValueError("montant négatif")
    if montant > 0 and not pieces:
        raise ValueError("aucune pièce")
    if any(piece <= 0 for piece in pieces):
        raise ValueError("les valeurs de pièces doivent être positives")


def construire_table(
    montant: int, pieces: list[int]
) -> tuple[list[int], list[int | None]]:
    """À compléter : tabulation des minima et des dernières pièces."""
    _verifier_entrees(montant, pieces)
    raise NotImplementedError


def rendu_monnaie_dp(
    montant: int, pieces: list[int]
) -> tuple[int, list[int]] | None:
    """À compléter : décider l'impossible puis reconstruire une solution."""
    _verifier_entrees(montant, pieces)
    raise NotImplementedError
