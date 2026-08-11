"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def maximum_controle(valeurs):
    if valeurs is None or len(valeurs) == 0:
        raise ValueError("liste non vide attendue")
    return valeurs[0]

if __name__ == "__main__":
    print(maximum_controle([3, 8, 2]))
