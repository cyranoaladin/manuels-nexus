"""Corrigé TP P06. Statut pédagogique: needs_review."""
from __future__ import annotations

def rechercher_premiere_ligne(rows: list[dict], key: str, value) -> dict | None:
    if rows is None: raise ValueError("table absente")
    for row in rows:
        if row.get(key) == value: return row
    return None

def detecter_doublons(rows: list[dict], key: str) -> list:
    if rows is None: raise ValueError("table absente")
    vus=set(); doublons=[]
    for row in rows:
        value=row.get(key)
        if value in vus and value not in doublons: doublons.append(value)
        vus.add(value)
    return doublons

def trier_par_nom_atelier(rows: list[dict]) -> list[dict]:
    if rows is None: raise ValueError("table absente")
    return sorted(rows, key=lambda row: (row["nom"], row["atelier"]))

def fusionner_presences(inscriptions: list[dict], presences: list[dict]) -> tuple[list[dict], list[str]]:
    if inscriptions is None or presences is None: raise ValueError("tables absentes")
    index={row["id"]: row for row in inscriptions}
    fusion=[]; erreurs=[]
    for presence in presences:
        row=index.get(presence["id"])
        if row is None: erreurs.append(f"id_absent={presence['id']}")
        else: fusion.append({**row, "present": presence["present"]})
    return fusion, erreurs
