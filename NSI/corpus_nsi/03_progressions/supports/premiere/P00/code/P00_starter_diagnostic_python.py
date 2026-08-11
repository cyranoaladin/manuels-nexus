"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

def predict_trace(steps):
    if steps is None:
        raise ValueError("steps absent")
    return {"etat_final": {}, "operations_lues": len(steps)}

if __name__ == "__main__":
    print(predict_trace([("x", 3), ("x", 5)]))
