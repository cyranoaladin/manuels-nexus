"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def jouer_operations(operations):
    if operations is None:
        raise ValueError("operations absentes")
    return []

if __name__ == "__main__":
    print(jouer_operations([("push", "A"), ("push", "B"), ("pop", None)]))
