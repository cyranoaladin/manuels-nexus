"""Starter TP T01. Statut pédagogique: needs_review."""

from __future__ import annotations

class Pile:
    def __init__(self) -> None:
        self._data: list = []

    def empiler(self, x):
        self._data.append(x)

    def depiler(self):
        raise ValueError("depiler à compléter")

    def sommet(self):
        raise ValueError("sommet à compléter")

    def est_vide(self):
        return len(self._data) == 0


class File:
    def __init__(self) -> None:
        self._data: list = []

    def enfiler(self, x):
        self._data.append(x)

    def defiler(self):
        raise ValueError("defiler à compléter")

    def premier(self):
        raise ValueError("premier à compléter")

    def est_vide(self):
        return len(self._data) == 0

if __name__ == "__main__":
    pile = Pile()
    pile.empiler("A")
    pile.empiler("B")
    print(pile.depiler())
