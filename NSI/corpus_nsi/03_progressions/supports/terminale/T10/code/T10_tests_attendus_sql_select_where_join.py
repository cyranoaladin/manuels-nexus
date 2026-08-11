"""Tests attendus du TP T10. Statut pédagogique : needs_review."""
from __future__ import annotations

import importlib
import os
import sqlite3


MODULE = importlib.import_module(
    os.environ.get("TP_MODULE", "T10_starter_sql_select_where_join")
)


def test_base_de_reference() -> None:
    conn = MODULE.creer_base()
    assert conn.execute("SELECT COUNT(*) FROM Eleve").fetchone() == (4,)
    assert conn.execute("SELECT COUNT(*) FROM Note").fetchone() == (6,)


def test_select_join_where_et_frontiere() -> None:
    conn = MODULE.creer_base()
    assert MODULE.notes_minimum(conn, 15) == [
        ("Grace", "MATHS", 18),
        ("Ada", "NSI", 17),
        ("Grace", "NSI", 15),
    ]
    assert MODULE.notes_minimum(conn, 18) == [("Grace", "MATHS", 18)]
    assert MODULE.notes_minimum(conn, 20) == []


def test_insert_parametre_et_cle_unique() -> None:
    conn = MODULE.creer_base()
    assert MODULE.ajouter_note(conn, 16, 4, "MATHS", 12) == (
        16,
        4,
        "MATHS",
        12,
    )
    duplicate_key_rejected = False
    try:
        MODULE.ajouter_note(conn, 16, 4, "NSI", 11)
    except sqlite3.IntegrityError:
        duplicate_key_rejected = True
    assert duplicate_key_rejected, "une clé primaire dupliquée doit être refusée"


def test_update_et_delete_cibles() -> None:
    conn = MODULE.creer_base()
    assert MODULE.modifier_note(conn, 14, 10) == (14, 10)
    assert MODULE.modifier_note(conn, 99, 10) is None
    assert MODULE.supprimer_note(conn, 13) is True
    assert MODULE.supprimer_note(conn, 13) is False
    assert conn.execute("SELECT * FROM Note WHERE id_note = 13").fetchall() == []


def test_base_absente_refusee() -> None:
    for operation, arguments in (
        (MODULE.notes_minimum, (None, 15)),
        (MODULE.ajouter_note, (None, 16, 4, "MATHS", 12)),
        (MODULE.modifier_note, (None, 14, 10)),
        (MODULE.supprimer_note, (None, 13)),
    ):
        try:
            operation(*arguments)
        except ValueError:
            continue
        raise AssertionError("ValueError attendue pour une base absente")


if __name__ == "__main__":
    test_base_de_reference()
    test_select_join_where_et_frontiere()
    test_insert_parametre_et_cle_unique()
    test_update_et_delete_cibles()
    test_base_absente_refusee()
    print("tests attendus T10 OK")
