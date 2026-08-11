"""Corrigé professeur du TP T10 SQL. Statut pédagogique : needs_review."""
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
    """Crée en mémoire la base de référence du chapitre."""
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


def _exiger_connexion(conn: sqlite3.Connection | None) -> sqlite3.Connection:
    if conn is None:
        raise ValueError("base absente")
    return conn


def notes_minimum(
    conn: sqlite3.Connection | None, seuil: int
) -> list[tuple[str, str, int]]:
    """Renvoie nom, matière et note pour les notes au moins égales au seuil."""
    base = _exiger_connexion(conn)
    curseur = base.execute(
        """
        SELECT Eleve.nom, Note.matiere, Note.note
        FROM Eleve
        JOIN Note ON Eleve.id_eleve = Note.id_eleve
        WHERE Note.note >= ?
        ORDER BY Note.note DESC, Eleve.nom ASC
        """,
        (seuil,),
    )
    return [
        (str(nom), str(matiere), int(note))
        for nom, matiere, note in curseur.fetchall()
    ]


def ajouter_note(
    conn: sqlite3.Connection | None,
    id_note: int,
    id_eleve: int,
    matiere: str,
    valeur: int,
) -> tuple[int, int, str, int]:
    """Insère une note et renvoie la ligne insérée pour vérification."""
    base = _exiger_connexion(conn)
    base.execute(
        "INSERT INTO Note(id_note, id_eleve, matiere, note) VALUES (?, ?, ?, ?)",
        (id_note, id_eleve, matiere, valeur),
    )
    row = base.execute(
        "SELECT id_note, id_eleve, matiere, note FROM Note WHERE id_note = ?",
        (id_note,),
    ).fetchone()
    assert row is not None
    return int(row[0]), int(row[1]), str(row[2]), int(row[3])


def modifier_note(
    conn: sqlite3.Connection | None, id_note: int, valeur: int
) -> tuple[int, int] | None:
    """Modifie une note ciblée et renvoie son identifiant et sa nouvelle valeur."""
    base = _exiger_connexion(conn)
    base.execute(
        "UPDATE Note SET note = ? WHERE id_note = ?",
        (valeur, id_note),
    )
    row = base.execute(
        "SELECT id_note, note FROM Note WHERE id_note = ?",
        (id_note,),
    ).fetchone()
    if row is None:
        return None
    return int(row[0]), int(row[1])


def supprimer_note(conn: sqlite3.Connection | None, id_note: int) -> bool:
    """Supprime la note ciblée et indique si une ligne a réellement disparu."""
    base = _exiger_connexion(conn)
    curseur = base.execute("DELETE FROM Note WHERE id_note = ?", (id_note,))
    return curseur.rowcount == 1
