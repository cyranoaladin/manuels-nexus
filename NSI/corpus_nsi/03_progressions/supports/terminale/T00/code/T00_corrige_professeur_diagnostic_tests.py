"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def maximum_controle(valeurs):
    if valeurs is None or len(valeurs) == 0:
        raise ValueError("liste non vide attendue")
    maximum = valeurs[0]
    for valeur in valeurs[1:]:
        if valeur > maximum:
            maximum = valeur
    return maximum
