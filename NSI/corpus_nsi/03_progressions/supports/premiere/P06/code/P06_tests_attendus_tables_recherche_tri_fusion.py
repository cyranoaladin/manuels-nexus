"""Tests attendus TP P06. Statut pédagogique: needs_review."""
from __future__ import annotations
import importlib, os
MODULE=importlib.import_module(os.environ.get("TP_MODULE","P06_starter_tables_recherche_tri_fusion"))
INSCRIPTIONS=[{"id":17,"nom":"Ada","atelier":"robot"},{"id":4,"nom":"Linus","atelier":"web"},{"id":17,"nom":"Ada","atelier":"python"}]
PRESENCES=[{"id":17,"present":True},{"id":9,"present":True}]

def test_nominal_recherche_tri_fusion() -> None:
    assert MODULE.rechercher_premiere_ligne(INSCRIPTIONS,"id",17)["atelier"] == "robot"
    assert MODULE.detecter_doublons(INSCRIPTIONS,"id") == [17]
    assert [row["atelier"] for row in MODULE.trier_par_nom_atelier(INSCRIPTIONS)] == ["python","robot","web"]
    fusion, erreurs = MODULE.fusionner_presences(INSCRIPTIONS,PRESENCES)
    assert fusion[0]["nom"] == "Ada" and erreurs == ["id_absent=9"]

def test_limite_cle_absente() -> None:
    assert MODULE.rechercher_premiere_ligne(INSCRIPTIONS,"id",9) is None
    assert MODULE.detecter_doublons([],"id") == []

def test_invalide_table_absente() -> None:
    for func,args in [(MODULE.rechercher_premiere_ligne,(None,"id",17)),(MODULE.detecter_doublons,(None,"id")),(MODULE.trier_par_nom_atelier,(None,)),(MODULE.fusionner_presences,(None,PRESENCES))]:
        try: func(*args)
        except ValueError: continue
        raise AssertionError("ValueError attendue")

if __name__ == "__main__":
    test_nominal_recherche_tri_fusion(); test_limite_cle_absente(); test_invalide_table_absente(); print("tests attendus OK")
