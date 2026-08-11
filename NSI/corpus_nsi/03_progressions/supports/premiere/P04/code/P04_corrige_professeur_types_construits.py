"""Corrigé professeur TP P04. Statut pédagogique: needs_review."""

from __future__ import annotations

def _point2d(point: tuple[float, float], name: str) -> tuple[float, float]:
    if not isinstance(point, tuple) or len(point) != 2:
        raise ValueError(f"{name} doit être un tuple de deux coordonnées")
    x, y = point
    return float(x), float(y)


def milieu(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    ax, ay = _point2d(a, "a")
    bx, by = _point2d(b, "b")
    return ((ax + bx) / 2, (ay + by) / 2)


def stations_chaudes(stations: list[dict], seuil: int) -> list[str]:
    if stations is None:
        raise ValueError("stations absentes")
    noms: list[str] = []
    for station in stations:
        if "nom" not in station or "temperature" not in station:
            raise ValueError("chaque station doit fournir nom et temperature")
        if int(station["temperature"]) >= seuil:
            noms.append(str(station["nom"]))
    return noms


def moyenne_notes(notes: list[int]) -> float:
    if notes is None:
        raise ValueError("notes absentes")
    if not notes:
        raise ValueError("liste de notes vide")
    return sum(notes) / len(notes)
