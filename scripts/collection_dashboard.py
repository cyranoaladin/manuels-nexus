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

import argparse
import hashlib
import json
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
    chapter_ids = sorted(chapter.chapter_id for chapter in chapitres)
    matrix_path = RACINE / "audit/PUBLISH_READINESS_CHAPTER_MATRIX.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    authoritative_ids = sorted(
        str(row["chapter"]) for row in matrix.get("chapters") or []
    )
    if not authoritative_ids or chapter_ids != authoritative_ids:
        raise ValueError(
            "le périmètre du dashboard legacy diverge de la matrice autoritaire"
        )
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
            "legacy_diagnostic_status": (
                "LEGACY_CHECKLIST_SATISFIED"
                if siens and all(c.release_ready for c in siens)
                else "LEGACY_CHECKLIST_INCOMPLETE"
            ),
        }

    total_cap = sum(m["capacites_total"] for m in manuels.values())
    total_map = sum(m["capacites_rattachees"] for m in manuels.values())
    return {
        "schema_version": 1,
        "generated_by": "scripts/collection_dashboard.py",
        "authority": "NON_AUTHORITATIVE_LEGACY_DIAGNOSTIC",
        "authoritative_successor": "audit/PUBLISH_READINESS_CHAPTER_MATRIX.json",
        "authoritative_release_verdict": "NOT_PROVIDED",
        "chapter_ids": chapter_ids,
        "chapter_ids_digest": "sha256:"
        + hashlib.sha256(
            json.dumps(chapter_ids, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "edition": "2026-2027",
        "manuels": manuels,
        "collection": {
            "chapitres_total": len(chapitres),
            "legacy_checklist_satisfied_chapters": sum(
                1 for c in chapitres if c.release_ready
            ),
            "capacites_total": total_cap,
            "capacites_rattachees": total_map,
            "capacites_non_rattachees": total_cap - total_map,
            "objets_total": sum(c.objects_total for c in chapitres),
            "objets_generated": sum(c.objects_generated for c in chapitres),
            "legacy_checklist_satisfied_manuals": sum(
                1
                for m in manuels.values()
                if m["legacy_diagnostic_status"] == "LEGACY_CHECKLIST_SATISFIED"
            ),
        },
    }


def rendre_markdown(d: dict) -> str:
    c = d["collection"]
    lignes = [
        "# ÉTAT DE LA COLLECTION — édition 2026-2027",
        "",
        "> **NON AUTORITAIRE — DIAGNOSTIC HISTORIQUE.** Le verdict de release",
        "> appartient exclusivement à `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`.",
        "",
        "Généré de façon déterministe par `scripts/collection_dashboard.py`.",
        "Aucun chiffre de ce document n'est saisi à la main : tout est recalculé",
        "depuis l'arbre par `scripts/chapter_readiness.py`.",
        "",
        "## Vue d'ensemble",
        "",
        f"- Chapitres : **{c['chapitres_total']}**, dont "
        f"**{c['legacy_checklist_satisfied_chapters']}** satisfont l'ancienne checklist",
        f"- Manuels satisfaisant l'ancienne checklist : "
        f"**{c['legacy_checklist_satisfied_manuals']} / 6**",
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
        "Le libellé `READY` ci-dessus appartient uniquement à l'ancienne",
        "checklist. Il ne constitue jamais un verdict de publication. Les",
        "quinze critères historiques de",
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    d = construire()
    json_path = RACINE / "ETAT_COLLECTION_2026_2027.json"
    markdown_path = RACINE / "ETAT_COLLECTION_2026_2027.md"
    rendered_json = json.dumps(d, ensure_ascii=False, indent=2) + "\n"
    rendered_markdown = rendre_markdown(d)
    if arguments.check:
        if (
            not json_path.is_file()
            or json_path.read_text(encoding="utf-8") != rendered_json
            or not markdown_path.is_file()
            or markdown_path.read_text(encoding="utf-8") != rendered_markdown
        ):
            print("dashboard legacy périmé")
            return 1
        print("dashboard legacy current")
        return 0
    json_path.write_text(rendered_json, encoding="utf-8")
    markdown_path.write_text(rendered_markdown, encoding="utf-8")
    c = d["collection"]
    print(
        f"tableau de bord ecrit | {c['chapitres_total']} chapitres, "
        f"{c['legacy_checklist_satisfied_chapters']} legacy-ready, "
        f"{c['legacy_checklist_satisfied_manuals']}/6 manuels legacy-ready"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
