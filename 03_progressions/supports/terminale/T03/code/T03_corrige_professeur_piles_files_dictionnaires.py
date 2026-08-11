"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def jouer_operations(operations):
    if operations is None:
        raise ValueError("operations absentes")
    pile = []
    sorties = []
    for op, value in operations:
        if op == "push":
            pile.append(value)
        elif op == "pop":
            if not pile:
                raise ValueError("pile vide")
            sorties.append(pile.pop())
        else:
            raise ValueError("operation inconnue")
    return sorties
