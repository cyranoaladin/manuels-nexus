"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def inspect_text(text):
    if text is None:
        raise ValueError("texte absent")
    return {"chars": len(text)}

if __name__ == "__main__":
    print(inspect_text("Aé"))
