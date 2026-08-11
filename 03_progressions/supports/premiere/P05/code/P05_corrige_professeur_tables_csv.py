"""Corrigé professeur TP P05. Statut pédagogique: needs_review."""

from __future__ import annotations

import csv


def charger_pays_csv(path: str) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def filtrer_par_continent(rows: list[dict], continent: str) -> list[dict]:
    if rows is None:
        raise ValueError("table absente")
    if not continent:
        raise ValueError("continent absent")
    return [row for row in rows if row.get("CONTINENT") == continent]


def convertir_populations(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    if rows is None:
        raise ValueError("table absente")
    valides = []
    erreurs = []
    for row in rows:
        try:
            population = int(row["POPULATION"])
        except ValueError:
            erreurs.append(row)
            continue
        except KeyError as exc:
            raise ValueError("champ POPULATION absent") from exc
        valides.append(dict(row, POPULATION=population))
    return valides, erreurs


def trier_par_continent_population(rows: list[dict]) -> list[dict]:
    valides, _ = convertir_populations(rows)
    return sorted(valides, key=lambda row: (row["CONTINENT"], -row["POPULATION"], row["PAYS"]))
