"""Structures support pour la séquence Terminale S01."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Generic, Iterable, List, TypeVar

T = TypeVar("T")


@dataclass
class Stack(Generic[T]):
    """Pile LIFO implémentée par liste Python."""

    _items: List[T] = field(default_factory=list)

    def push(self, item: T) -> None:
        """Ajoute un élément au sommet de la pile."""
        self._items.append(item)

    def pop(self) -> T:
        """Retire et retourne l'élément du sommet."""
        if self.is_empty():
            raise IndexError("pile vide")
        return self._items.pop()

    def is_empty(self) -> bool:
        """Indique si la pile ne contient aucun élément."""
        return len(self._items) == 0

    def size(self) -> int:
        """Retourne le nombre d'éléments stockés."""
        return len(self._items)


@dataclass
class Queue(Generic[T]):
    """File FIFO implémentée par deque."""

    _items: Deque[T] = field(default_factory=deque)

    def enqueue(self, item: T) -> None:
        """Ajoute un élément en fin de file."""
        self._items.append(item)

    def dequeue(self) -> T:
        """Retire et retourne l'élément en tête de file."""
        if self.is_empty():
            raise IndexError("file vide")
        return self._items.popleft()

    def is_empty(self) -> bool:
        """Indique si la file ne contient aucun élément."""
        return len(self._items) == 0

    def size(self) -> int:
        """Retourne le nombre d'éléments stockés."""
        return len(self._items)


def adjacency_list_from_edges(edges: Iterable[tuple[str, str]], directed: bool = False) -> Dict[str, List[str]]:
    """Construit une liste d'adjacence à partir d'arêtes."""
    graph: Dict[str, List[str]] = {}
    for source, target in edges:
        graph.setdefault(source, [])
        graph.setdefault(target, [])
        graph[source].append(target)
        if not directed:
            graph[target].append(source)
    return {node: sorted(neighbours) for node, neighbours in graph.items()}


def adjacency_matrix(graph: Dict[str, List[str]], nodes: List[str]) -> List[List[int]]:
    """Construit la matrice d'adjacence d'un graphe selon un ordre de sommets."""
    index = {node: position for position, node in enumerate(nodes)}
    matrix = [[0 for _ in nodes] for _ in nodes]
    for source, neighbours in graph.items():
        if source not in index:
            raise KeyError(f"sommet absent de nodes: {source}")
        for target in neighbours:
            if target not in index:
                raise KeyError(f"voisin absent de nodes: {target}")
            matrix[index[source]][index[target]] = 1
    return matrix


def graph_from_matrix(matrix: List[List[int]], nodes: List[str]) -> Dict[str, List[str]]:
    """Reconstruit une liste d'adjacence depuis une matrice d'adjacence."""
    if len(matrix) != len(nodes):
        raise ValueError("dimensions incompatibles")
    graph: Dict[str, List[str]] = {node: [] for node in nodes}
    for row_index, row in enumerate(matrix):
        if len(row) != len(nodes):
            raise ValueError("matrice non carrée")
        for col_index, value in enumerate(row):
            if value not in {0, 1}:
                raise ValueError("matrice d'adjacence attendue avec valeurs 0 ou 1")
            if value:
                graph[nodes[row_index]].append(nodes[col_index])
    return graph


def bfs_path(graph: Dict[str, List[str]], start: str, goal: str) -> List[str]:
    """Retourne un chemin trouvé par parcours en largeur, ou une liste vide."""
    queue: Deque[List[str]] = deque([[start]])
    visited = {start}
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == goal:
            return path
        for neighbour in graph.get(node, []):
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(path + [neighbour])
    return []
