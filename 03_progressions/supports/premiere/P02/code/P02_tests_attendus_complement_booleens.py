"""Asset Python TP. Statut pédagogique: needs_review."""

from __future__ import annotations

import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "P02_starter_complement_booleens"))
twos_complement_value = MODULE.twos_complement_value

def test_nominal() -> None:
    result = twos_complement_value("11101001")
    assert result == -23

def test_limite() -> None:
    result = twos_complement_value("10000000")
    assert result == -128

def test_invalide() -> None:
    try:
        twos_complement_value("102")
    except (ValueError, TypeError, IndexError):
        return
    raise AssertionError("exception attendue")

if __name__ == "__main__":
    test_nominal()
    test_limite()
    test_invalide()
    print("tests attendus OK")
