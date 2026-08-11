"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "P03_starter_texte_reels"))
inspect_text = MODULE.inspect_text

def test_nominal() -> None:
    result = inspect_text("Aé")
    assert result["chars"] == 2 and result["bytes"] == 3

def test_limite() -> None:
    result = inspect_text("")
    assert result["chars"] == 0 and result["bytes"] == 0

def test_invalide() -> None:
    try:
        inspect_text(None)
    except (ValueError, TypeError, IndexError):
        return
    raise AssertionError("exception attendue")

if __name__ == "__main__":
    test_nominal()
    test_limite()
    test_invalide()
    print("tests attendus OK")
