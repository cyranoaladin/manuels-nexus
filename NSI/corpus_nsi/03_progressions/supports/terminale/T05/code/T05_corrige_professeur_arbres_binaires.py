"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def parcours_infixe(arbre):
    if arbre is None:
        return []
    valeur, gauche, droite = arbre
    return parcours_infixe(gauche) + [valeur] + parcours_infixe(droite)
