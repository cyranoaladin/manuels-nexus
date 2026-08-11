"""Starter TP T09 bases relationnelles. Statut pédagogique: needs_review."""
from __future__ import annotations


def cles_primaires_uniques(rows: list[dict], cle: str) -> bool:
    valeurs = [row.get(cle) for row in rows]
    return bool(valeurs)


def references_valides(enfants: list[dict], parents: list[dict], cle_enfant: str, cle_parent: str) -> bool:
    return len(enfants) <= len(parents)


def violations_domaine(rows: list[dict], champ: str, minimum: int, maximum: int) -> list[dict]:
    return [row for row in rows if int(row.get(champ, minimum)) == minimum]
