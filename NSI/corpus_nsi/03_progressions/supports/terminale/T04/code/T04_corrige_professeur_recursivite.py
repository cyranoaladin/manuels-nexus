"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def factorielle(n):
    if n is None or n < 0:
        raise ValueError("entier naturel attendu")
    if n == 0:
        return 1
    return n * factorielle(n - 1)
