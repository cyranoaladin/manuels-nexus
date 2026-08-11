"""Starter TP P05. Statut pédagogique: needs_review."""

from __future__ import annotations

import csv


def charger_pays_csv(path: str) -> list[dict]:
    """Charger `pays_monde.csv`.

    Version élève volontairement incomplète : elle lit les lignes mais ne produit
    pas encore les dictionnaires demandés par les tests.
    """
    with open(path, encoding="utf-8", newline="") as handle:
        return list(csv.reader(handle))


def filtrer_par_continent(rows: list[dict], continent: str) -> list[dict]:
    if rows is None:
        raise ValueError("table absente")
    if not continent:
        raise ValueError("continent absent")
    return []


def convertir_populations(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    if rows is None:
        raise ValueError("table absente")
    return [], []


def trier_par_continent_population(rows: list[dict]) -> list[dict]:
    if rows is None:
        raise ValueError("table absente")
    return []


if __name__ == "__main__":
    exemple = [
        {"PAYS": "Allemagne", "CAPITALE": "Berlin", "CONTINENT": "Europe", "POPULATION": "82801531"},
        {"PAYS": "Brésil", "CAPITALE": "Brasilia", "CONTINENT": "Amérique du Sud", "POPULATION": "204259812"},
    ]
    print(filtrer_par_continent(exemple, "Europe"))
