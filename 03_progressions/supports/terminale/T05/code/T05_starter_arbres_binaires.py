"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def parcours_infixe(arbre):
    if arbre is None:
        return []
    return [arbre[0]]

if __name__ == "__main__":
    print(parcours_infixe((4, (2, None, None), (7, None, None))))
