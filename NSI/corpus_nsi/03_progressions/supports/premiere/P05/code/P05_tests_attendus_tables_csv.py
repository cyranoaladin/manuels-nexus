"""Tests attendus TP P05. Statut pédagogique: needs_review."""

from __future__ import annotations

import importlib
import os
import tempfile
from pathlib import Path

MODULE = importlib.import_module(os.environ.get("TP_MODULE", "P05_starter_tables_csv"))
charger_pays_csv = MODULE.charger_pays_csv
filtrer_par_continent = MODULE.filtrer_par_continent
convertir_populations = MODULE.convertir_populations
trier_par_continent_population = MODULE.trier_par_continent_population


EXTRAIT = [
    {"PAYS": "Allemagne", "CAPITALE": "Berlin", "CONTINENT": "Europe", "POPULATION": "82801531"},
    {"PAYS": "Albanie", "CAPITALE": "Tirana", "CONTINENT": "Europe", "POPULATION": "3063320"},
    {"PAYS": "Brésil", "CAPITALE": "Brasilia", "CONTINENT": "Amérique du Sud", "POPULATION": "204259812"},
    {"PAYS": "Erreur", "CAPITALE": "NA", "CONTINENT": "Europe", "POPULATION": "invalide"},
]


def test_nominal() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "pays_monde.csv"
        path.write_text(
            "PAYS,CAPITALE,CONTINENT,POPULATION\n"
            "Allemagne,Berlin,Europe,82801531\n"
            "Albanie,Tirana,Europe,3063320\n"
            "Brésil,Brasilia,Amérique du Sud,204259812\n",
            encoding="utf-8",
        )
        loaded = charger_pays_csv(str(path))
    assert loaded[0]["PAYS"] == "Allemagne"
    assert loaded[0]["CAPITALE"] == "Berlin"
    valides, erreurs = convertir_populations(EXTRAIT)
    assert [row["PAYS"] for row in erreurs] == ["Erreur"]
    assert [row["PAYS"] for row in valides] == ["Allemagne", "Albanie", "Brésil"]
    europe = filtrer_par_continent(valides, "Europe")
    assert [row["PAYS"] for row in europe] == ["Allemagne", "Albanie"]

def test_limite() -> None:
    valides, erreurs = convertir_populations(EXTRAIT)
    assert [row["PAYS"] for row in erreurs] == ["Erreur"]
    assert all(isinstance(row["POPULATION"], int) for row in valides)
    lexicographique = sorted(["100", "20", "3"])
    assert lexicographique == ["100", "20", "3"]
    numerique = sorted([100, 20, 3])
    assert numerique == [3, 20, 100]
    tri = trier_par_continent_population(EXTRAIT)
    assert [row["PAYS"] for row in tri[:2]] == ["Brésil", "Allemagne"]

def test_invalide() -> None:
    try:
        filtrer_par_continent(None, "Europe")
    except (ValueError, TypeError, IndexError):
        return
    raise AssertionError("exception attendue")

if __name__ == "__main__":
    test_nominal()
    test_limite()
    test_invalide()
    print("tests attendus OK")
