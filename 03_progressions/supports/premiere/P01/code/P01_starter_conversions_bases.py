"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def convert_base(value):
    if value is None or value < 0:
        raise ValueError("entier naturel attendu")
    return {"decimal": value}

if __name__ == "__main__":
    print(convert_base(45))
