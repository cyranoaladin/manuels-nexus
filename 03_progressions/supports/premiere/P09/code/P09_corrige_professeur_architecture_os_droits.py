"""Corrigé professeur TP P09 architecture, OS et droits. Statut pédagogique: needs_review."""
from __future__ import annotations


def _digits(mode: int) -> tuple[int, int, int]:
    if mode < 0 or mode > 777:
        raise ValueError("mode invalide")
    text = f"{mode:03d}"
    return tuple(int(ch) for ch in text)  # type: ignore[return-value]


def droits_symboliques(mode: int) -> str:
    blocs = []
    for value in _digits(mode):
        blocs.append(("r" if value & 4 else "-") + ("w" if value & 2 else "-") + ("x" if value & 1 else "-"))
    return "".join(blocs)


def peut_lire(mode: int, role: str) -> bool:
    index = {"user": 0, "group": 1, "other": 2}.get(role)
    if index is None:
        raise ValueError("rôle invalide")
    return bool(_digits(mode)[index] & 4)


def chmod_ajouter_execution(mode: int, role: str) -> int:
    index = {"user": 0, "group": 1, "other": 2}.get(role)
    if index is None:
        raise ValueError("rôle invalide")
    digits = list(_digits(mode))
    digits[index] |= 1
    return digits[0] * 100 + digits[1] * 10 + digits[2]
