"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "P01_starter_conversions_bases"))
convert_base = MODULE.convert_base

def test_nominal() -> None:
    result = convert_base(45)
    assert result["binary"] == "101101" and result["hex"] == "2D"

def test_limite_zero() -> None:
    result = convert_base(0)
    assert result["binary"] == "0" and result["hex"] == "0"

def test_invalide() -> None:
    try:
        convert_base(-1)
    except (ValueError, TypeError, IndexError):
        return
    raise AssertionError("exception attendue")

if __name__ == "__main__":
    test_nominal()
    test_limite_zero()
    test_invalide()
    print("tests attendus OK")
