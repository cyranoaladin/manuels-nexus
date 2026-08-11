"""Corrigé professeur TP T01. Statut pédagogique: needs_review."""

from __future__ import annotations

class Pile:
    def __init__(self) -> None:
        self._data: list = []

    def empiler(self, x):
        self._data.append(x)

    def depiler(self):
        if self.est_vide():
            raise IndexError("pile vide")
        return self._data.pop()

    def sommet(self):
        if self.est_vide():
            raise IndexError("pile vide")
        return self._data[-1]

    def est_vide(self):
        return len(self._data) == 0


class File:
    """File FIFO simple.

    Cette implémentation par liste utilise `pop(0)`, dont la complexité est O(n).
    Une implémentation alternative avec `collections.deque` donne des retraits O(1).
    """

    def __init__(self) -> None:
        self._data: list = []

    def enfiler(self, x):
        self._data.append(x)

    def defiler(self):
        if self.est_vide():
            raise IndexError("file vide")
        return self._data.pop(0)

    def premier(self):
        if self.est_vide():
            raise IndexError("file vide")
        return self._data[0]

    def est_vide(self):
        return len(self._data) == 0
