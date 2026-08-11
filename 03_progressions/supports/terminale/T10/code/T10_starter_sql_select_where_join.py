"""Starter élève du TP T10 SQL. Statut pédagogique : needs_review."""
from __future__ import annotations

import sqlite3


ELEVES = [
    (1, "Ada", "T1"),
    (2, "Linus", "T2"),
    (3, "Grace", "T1"),
    (4, "Alan", "T2"),
]

NOTES = [
    (10, 1, "NSI", 17),
    (11, 2, "NSI", 13),
    (12, 3, "NSI", 15),
    (13, 1, "MATHS", 14),
    (14, 4, "NSI", 9),
    (15, 3, "MATHS", 18),
]


def creer_base() -> sqlite3.Connection:
    """Crée la base fournie ; cette fonction n'est pas à compléter."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        "CREATE TABLE Eleve("
        "id_eleve INTEGER PRIMARY KEY, nom TEXT NOT NULL, classe TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE Note("
        "id_note INTEGER PRIMARY KEY, "
        "id_eleve INTEGER NOT NULL REFERENCES Eleve(id_eleve), "
        "matiere TEXT NOT NULL, note INTEGER NOT NULL)"
    )
    conn.executemany("INSERT INTO Eleve VALUES (?, ?, ?)", ELEVES)
    conn.executemany("INSERT INTO Note VALUES (?, ?, ?, ?)", NOTES)
    return conn


def notes_minimum(
    conn: sqlite3.Connection | None, seuil: int
) -> list[tuple[str, str, int]]:
    """À compléter : SELECT + JOIN + WHERE + ORDER BY, avec paramètre ``seuil``."""
    if conn is None:
        raise ValueError("base absente")
    raise NotImplementedError


def ajouter_note(
    conn: sqlite3.Connection | None,
    id_note: int,
    id_eleve: int,
    matiere: str,
    valeur: int,
) -> tuple[int, int, str, int]:
    """À compléter : INSERT paramétré puis SELECT de contrôle."""
    if conn is None:
        raise ValueError("base absente")
    raise NotImplementedError


def modifier_note(
    conn: sqlite3.Connection | None, id_note: int, valeur: int
) -> tuple[int, int] | None:
    """À compléter : UPDATE ciblé puis SELECT de contrôle."""
    if conn is None:
        raise ValueError("base absente")
    raise NotImplementedError


def supprimer_note(conn: sqlite3.Connection | None, id_note: int) -> bool:
    """À compléter : DELETE ciblé ; renvoyer True si une ligne est supprimée."""
    if conn is None:
        raise ValueError("base absente")
    raise NotImplementedError
