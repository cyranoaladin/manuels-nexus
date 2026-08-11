#!/usr/bin/env python3
"""Agrège l'état de préparation des chapitres en tableau de bord de collection.

Produit `ETAT_COLLECTION_2026_2027.json` et son rendu `.md`. Les deux sont
dérivés de `scripts/chapter_readiness.py`, lui-même recalculé depuis l'arbre :
aucun chiffre de ce tableau de bord n'est saisi à la main.

Classement d'un chapitre :

- READY       release_ready vrai
- BLOCKED     un verdict scientifique en échec, ou aucune capacité au contrat
- SKELETON    moins de la moitié de la cible d'exercices
- IN_PROGRESS le reste

Usage :
    python3 scripts/collection_dashboard.py
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import yaml

import sys

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

from chapter_readiness import collecter  # noqa: E402

ORDRE = ["1SPE", "1NSI", "TSPE_2026_2027", "TNSI", "TCOMPL", "TEXPERTES"]

LIBELLES = {
    "1SPE": "Mathématiques Première spécialité",
    "1NSI": "NSI Première spécialité",
    "TSPE_2026_2027": "Mathématiques Terminale spécialité",
    "TNSI": "NSI Terminale spécialité",
    "TCOMPL": "Mathématiques complémentaires Terminale",
    "TEXPERTES": "Mathématiques expertes Terminale",
}


def classer(ch) -> str:
    if ch.release_ready:
        return "READY"
    if ch.scientific_review.get("fail") or ch.capabilities_total == 0:
        return "BLOCKED"
    if ch.exercise_count < ch.target_exercises / 2:
        return "SKELETON"
    return "IN_PROGRESS"


def construire() -> dict:
    chapitres = collecter()
    registre_path = RACINE / "docs/programmes/PROGRAMMES_2026_2027.yaml"
    registre = yaml.safe_load(registre_path.read_text(encoding="utf-8")) if registre_path.exists() else {}
    programmes = {m["manual_id"]: m for m in (registre.get("manuels") or [])}

    manuels = {}
    for manual_id in ORDRE:
        siens = [c for c in chapitres if c.manual_id == manual_id]
        etats = {"READY": 0, "IN_PROGRESS": 0, "SKELETON": 0, "BLOCKED": 0}
        for ch in siens:
            etats[classer(ch)] += 1
        prog = programmes.get(manual_id, {})
        manuels[manual_id] = {
            "libelle": LIBELLES[manual_id],
            "programme_source": prog.get("programme_source"),
            "programme_version": prog.get("programme_version"),
            "chapitres_total": len(siens),
            "etats": etats,
            "capacites_total": sum(c.capabilities_total for c in siens),
            "capacites_rattachees": sum(c.capabilities_mapped for c in siens),
            "exercices": sum(c.exercise_count for c in siens),
            "exercices_cible": sum(c.target_exercises for c in siens),
            "objets_total": sum(c.objects_total for c in siens),
            "objets_generated": sum(c.objects_generated for c in siens),
            "objets_relus": sum(c.objects_reviewed for c in siens),
            "build_eleve": any(c.student_build for c in siens),
            "build_professeur": any(c.teacher_build for c in siens),
            "readiness_moyenne": round(
                sum(c.readiness_percent for c in siens) / len(siens), 1
            ) if siens else 0.0,
            "release_status": "RELEASE_CANDIDATE" if siens and all(c.release_ready for c in siens) else "EN_PRODUCTION",
        }

    total_cap = sum(m["capacites_total"] for m in manuels.values())
    total_map = sum(m["capacites_rattachees"] for m in manuels.values())
    return {
        "schema_version": 1,
        "generated_by": "scripts/collection_dashboard.py",
        "generated_on": date.today().isoformat(),
        "edition": "2026-2027",
        "manuels": manuels,
        "collection": {
            "chapitres_total": len(chapitres),
            "chapitres_ready": sum(1 for c in chapitres if c.release_ready),
            "capacites_total": total_cap,
            "capacites_rattachees": total_map,
            "capacites_non_rattachees": total_cap - total_map,
            "objets_total": sum(c.objects_total for c in chapitres),
            "objets_generated": sum(c.objects_generated for c in chapitres),
            "manuels_release_ready": sum(
                1 for m in manuels.values() if m["release_status"] == "RELEASE_CANDIDATE"
            ),
        },
    }


def rendre_markdown(d: dict) -> str:
    c = d["collection"]
    lignes = [
        "# ÉTAT DE LA COLLECTION — édition 2026-2027",
        "",
        f"Généré le {d['generated_on']} par `scripts/collection_dashboard.py`.",
        "Aucun chiffre de ce document n'est saisi à la main : tout est recalculé",
        "depuis l'arbre par `scripts/chapter_readiness.py`.",
        "",
        "## Vue d'ensemble",
        "",
        f"- Chapitres : **{c['chapitres_total']}**, dont **{c['chapitres_ready']}** prêts pour release",
        f"- Manuels prêts pour release : **{c['manuels_release_ready']} / 6**",
        f"- Capacités rattachées : **{c['capacites_rattachees']} / {c['capacites_total']}**"
        f" ({c['capacites_non_rattachees']} non rattachées)",
        f"- Objets encore au statut `generated` : **{c['objets_generated']} / {c['objets_total']}**",
        "",
        "## Par manuel",
        "",
        "| Manuel | Programme | Chapitres | READY | EN COURS | SQUELETTE | BLOQUÉ | Capacités | Exercices | `generated` | Prêt |",
        "|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|",
    ]
    for manual_id in ORDRE:
        m = d["manuels"][manual_id]
        e = m["etats"]
        lignes.append(
            f"| {m['libelle']} | {m['programme_version'] or '?'} | {m['chapitres_total']} "
            f"| {e['READY']} | {e['IN_PROGRESS']} | {e['SKELETON']} | {e['BLOCKED']} "
            f"| {m['capacites_rattachees']}/{m['capacites_total']} "
            f"| {m['exercices']}/{m['exercices_cible']} "
            f"| {m['objets_generated']}/{m['objets_total']} "
            f"| {m['readiness_moyenne']}% |"
        )
    lignes += [
        "",
        "## Lecture",
        "",
        "Un chapitre n'est `READY` que si les quinze critères de",
        "`chapter_readiness.py` sont réunis, dont l'absence totale d'objet au",
        "statut `generated`. Un objet `generated` n'a franchi aucune revue :",
        "le pipeline de statuts interdit qu'il paraisse dans une release.",
        "",
        "La colonne Exercices compare l'effectif au seuil capacitaire",
        "`min(50, max(24, 6 × C))`, où C est le nombre de capacités du chapitre.",
        "Ce seuil est un plancher de couverture, pas l'indicateur principal :",
        "les KPI qui décident d'une release sont la couverture des capacités,",
        "la couverture de revue scientifique, la traçabilité programme, la",
        "couverture d'évaluation et de remédiation, et l'état des builds.",
        "",
        "Détail par chapitre : `audit/CHAPTER_READINESS.json`.",
        "",
    ]
    return "\n".join(lignes)


def main() -> int:
    d = construire()
    (RACINE / "ETAT_COLLECTION_2026_2027.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (RACINE / "ETAT_COLLECTION_2026_2027.md").write_text(rendre_markdown(d), encoding="utf-8")
    c = d["collection"]
    print(
        f"tableau de bord ecrit | {c['chapitres_total']} chapitres, "
        f"{c['chapitres_ready']} ready, {c['manuels_release_ready']}/6 manuels"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
