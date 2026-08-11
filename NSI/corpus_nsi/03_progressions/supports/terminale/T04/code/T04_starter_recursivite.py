"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def factorielle(n):
    if n is None or n < 0:
        raise ValueError("entier naturel attendu")
    return n

if __name__ == "__main__":
    print(factorielle(5))
