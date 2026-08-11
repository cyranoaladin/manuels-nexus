"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def predict_trace(steps):
    if steps is None:
        raise ValueError("steps absent")
    state = {}
    for name, value in steps:
        state[name] = value
    return {"etat_final": state, "operations_lues": len(steps)}
