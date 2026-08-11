"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "P00_starter_diagnostic_python"))
predict_trace = MODULE.predict_trace

def test_nominal() -> None:
    result = predict_trace([("x", 3), ("x", 5)])
    assert result["etat_final"]["x"] == 5

def test_limite() -> None:
    result = predict_trace([])
    assert result["etat_final"] == {}

def test_invalide() -> None:
    try:
        predict_trace(None)
    except (ValueError, TypeError, IndexError):
        return
    raise AssertionError("exception attendue")

if __name__ == "__main__":
    test_nominal()
    test_limite()
    test_invalide()
    print("tests attendus OK")
