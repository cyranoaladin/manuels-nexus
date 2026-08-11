"""Corrigé professeur TP T09 bases relationnelles. Statut pédagogique: needs_review."""
from __future__ import annotations


def cles_primaires_uniques(rows: list[dict], cle: str) -> bool:
    valeurs = [row.get(cle) for row in rows]
    return None not in valeurs and len(valeurs) == len(set(valeurs))


def references_valides(enfants: list[dict], parents: list[dict], cle_enfant: str, cle_parent: str) -> bool:
    valeurs_parent = {row.get(cle_parent) for row in parents}
    return all(row.get(cle_enfant) in valeurs_parent for row in enfants)


def violations_domaine(rows: list[dict], champ: str, minimum: int, maximum: int) -> list[dict]:
    erreurs: list[dict] = []
    for row in rows:
        valeur = int(row[champ])
        if valeur < minimum or valeur > maximum:
            erreurs.append(row)
    return erreurs
