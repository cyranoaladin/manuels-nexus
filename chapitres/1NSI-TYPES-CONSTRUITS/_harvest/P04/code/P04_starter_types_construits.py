"""Starter TP P04. Statut pédagogique: needs_review."""

from __future__ import annotations

def milieu(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    """Retourner le milieu de deux points 2D.

    La validation de taille est volontairement à compléter par l'élève.
    """
    raise ValueError("calcul du milieu à compléter")


def stations_chaudes(stations: list[dict], seuil: int) -> list[str]:
    """Extraire les noms de stations dont la température dépasse le seuil."""
    if stations is None:
        raise ValueError("stations absentes")
    return []


def moyenne_notes(notes: list[int]) -> float:
    """Calculer la moyenne d'une liste non vide de notes."""
    raise ValueError("moyenne à compléter")


if __name__ == "__main__":
    print(milieu((0, 4), (6, 10)))
