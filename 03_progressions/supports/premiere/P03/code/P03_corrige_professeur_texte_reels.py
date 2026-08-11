"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def inspect_text(text):
    if text is None:
        raise ValueError("texte absent")
    data = text.encode("utf-8")
    return {"chars": len(text), "bytes": len(data), "hex": data.hex(" ")}
