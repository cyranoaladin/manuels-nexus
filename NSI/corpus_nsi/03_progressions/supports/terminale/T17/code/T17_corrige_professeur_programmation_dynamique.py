"""Corrigé professeur du TP T17. Statut pédagogique : needs_review."""
from __future__ import annotations


def _verifier_entrees(montant: int, pieces: list[int]) -> None:
    if montant < 0:
        raise ValueError("montant négatif")
    if montant > 0 and not pieces:
        raise ValueError("aucune pièce")
    if any(piece <= 0 for piece in pieces):
        raise ValueError("les valeurs de pièces doivent être positives")


def construire_table(
    montant: int, pieces: list[int]
) -> tuple[list[int], list[int | None]]:
    """Construit les minima et une dernière pièce pour chaque montant."""
    _verifier_entrees(montant, pieces)
    infini = montant + 1
    dp = [0] + [infini] * montant
    choix: list[int | None] = [None] * (montant + 1)

    for m in range(1, montant + 1):
        for piece in pieces:
            if piece <= m and dp[m - piece] != infini:
                candidat = dp[m - piece] + 1
                if candidat < dp[m]:
                    dp[m] = candidat
                    choix[m] = piece
    return dp, choix


def rendu_monnaie_dp(
    montant: int, pieces: list[int]
) -> tuple[int, list[int]] | None:
    """Renvoie le minimum et une solution, ou None si le montant est impossible."""
    dp, choix = construire_table(montant, pieces)
    infini = montant + 1
    if dp[montant] == infini:
        return None

    solution: list[int] = []
    reste = montant
    while reste > 0:
        piece = choix[reste]
        if piece is None:
            raise AssertionError("table de choix incohérente")
        solution.append(piece)
        reste -= piece
    return dp[montant], solution
