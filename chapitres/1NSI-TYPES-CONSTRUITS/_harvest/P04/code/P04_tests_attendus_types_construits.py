"""Tests attendus TP P04. Statut pédagogique: needs_review."""

from __future__ import annotations

import importlib
import os

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "P04_starter_types_construits"))
milieu = MODULE.milieu
stations_chaudes = MODULE.stations_chaudes
moyenne_notes = MODULE.moyenne_notes

def test_nominal() -> None:
    assert milieu((0, 4), (6, 10)) == (3.0, 7.0)
    stations = [
        {"nom": "Nord", "temperature": 18},
        {"nom": "Sud", "temperature": 24},
        {"nom": "Est", "temperature": 20},
    ]
    assert stations_chaudes(stations, 20) == ["Sud", "Est"]
    assert moyenne_notes([12, 14, 16]) == 14

def test_limite() -> None:
    try:
        moyenne_notes([])
    except ValueError:
        return
    else:
        raise AssertionError("moyenne_notes([]) doit lever ValueError")

def test_invalide() -> None:
    try:
        milieu((2,), (4, 5))
    except (ValueError, TypeError, IndexError):
        return
    raise AssertionError("exception attendue")

if __name__ == "__main__":
    test_nominal()
    test_limite()
    test_invalide()
    print("tests attendus OK")
