#!/usr/bin/env python3
"""Richesse pedagogique d'un chapitre, mesuree en occasions et en gestes.

Le P0 de clonage a montre ce que vaut un compteur de fichiers : cinquante
exercices dont sept seulement etaient les copies de personne. Compter les
fichiers mesure le volume, pas ce que l'eleve peut faire.

Ce producteur mesure autre chose. Pour chaque capacite du contrat il recense
les OCCASIONS distinctes de mobilisation -- pratique ciblee, evaluation, QCM,
remediation, methode -- et les GESTES de raisonnement que ces occasions
demandent. Les gestes ne sont pas devines : chaque exercice les declare dans
son META, ou ils restent relisibles et contestables.

La regle de statut depend de la NATURE de la capacite, jamais d'un quota :

* une capacite composite ou de synthese exige au moins deux gestes distincts,
  parce qu'un seul chemin de raisonnement ne prepare pas au transfert ;
* une capacite procedurale ou de support est servie des lors qu'elle dispose
  d'une pratique ciblee, d'une remediation et d'une methode.

Exiger « deux exercices par capacite » recreerait le remplissage qu'on repare.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"

#: Nature d'une capacite, deduite de son libelle contractuel. Elle commande
#: l'exigence appliquee : on ne demande pas la meme chose a « lire des
#: coordonnees » et a « resoudre des problemes de configuration ».
COMPOSITE_MARKERS = (
    "résoudre des problèmes",
    "resoudre des problemes",
    "étudier des problèmes",
    "etudier des problemes",
    "traduire un problème",
    "traduire un probleme",
)
CONCEPTUAL_MARKERS = ("démontrer", "demontrer", "déterminer sur une figure si")

#: Une capacite composite ou conceptuelle demande plus d'un chemin de
#: raisonnement ; les autres sont servies par une chaine complete.
MULTI_GESTURE_TYPES = {"COMPOSITE_REASONING", "SYNTHESIS_HEAVY"}


def _clone_module():
    spec = importlib.util.spec_from_file_location(
        "p0_clone_ledger", ROOT / "scripts/build_p0_content_clone_ledger.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def capacity_type(libelle: str) -> str:
    lowered = libelle.lower()
    if any(marker in lowered for marker in COMPOSITE_MARKERS):
        return "COMPOSITE_REASONING"
    if any(marker in lowered for marker in CONCEPTUAL_MARKERS):
        return "CONCEPTUAL"
    if "lire" in lowered or "représenter" in lowered or "representer" in lowered:
        return "ATOMIC_SUPPORT"
    return "PROCEDURAL"


def build_matrix(chapter: str) -> dict[str, Any]:
    clone = _clone_module()
    base = CHAPTERS / chapter
    contract = yaml.safe_load((base / "contrat.yaml").read_text(encoding="utf-8"))
    capacities = {c["code"]: c["libelle_eleve"] for c in contract["capacites"]}

    def meta(path: Path) -> dict[str, Any]:
        return clone.read_meta(path.read_text(encoding="utf-8"))

    practice: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    gestures: dict[str, set[str]] = collections.defaultdict(set)
    for path in sorted((base / "exercices").glob("*.tex")):
        entry = meta(path)
        declared = clone.declared_capacities(entry)
        per_question = entry.get("capacites_par_question") or {}
        per_question_gestures = entry.get("gestes_par_question") or {}
        for code in declared:
            served = [q for q, cs in per_question.items() if code in cs] or None
            practice[code].append(
                {
                    "id": entry["id"],
                    "parcours": entry.get("parcours"),
                    "duree_min": entry.get("duree_min"),
                    "questions_for_this_capacity": served,
                }
            )
            # Un exercice multi-capacites ne transmet pas TOUS ses gestes a
            # CHACUNE de ses capacites : ce serait le credit global que le
            # contrat interdit. Quand la sous-question est declaree, seul le
            # geste de cette sous-question compte pour cette capacite.
            if served and per_question_gestures:
                for question in served:
                    gestures[code] |= set(per_question_gestures.get(question, []))
            else:
                gestures[code] |= set(entry.get("gestes") or [])

    assessed: dict[str, list[str]] = collections.defaultdict(list)
    for path in sorted((base / "evaluations").glob("*.tex")):
        entry = meta(path)
        if entry.get("type_objet") != "evaluation":
            continue
        for code in clone.declared_capacities(entry):
            assessed[code].append(entry["id"])

    qcm_file = next((base / "qcm").glob("*-QCM.json"), None)
    qcm = collections.Counter()
    if qcm_file:
        for question in json.loads(qcm_file.read_text(encoding="utf-8"))["questions"]:
            qcm[str(question["capacite"])] += 1

    remediation = collections.Counter()
    for path in (base / "remediation").glob("*.tex"):
        for code in clone.declared_capacities(meta(path)):
            remediation[code] += 1
    methods = collections.Counter()
    for path in (base / "methodes").glob("*.tex"):
        for code in clone.declared_capacities(meta(path)):
            methods[code] += 1

    rows: dict[str, Any] = {}
    for code, libelle in capacities.items():
        kind = capacity_type(libelle)
        paths = sorted(gestures[code])
        opportunities = {
            "targeted_practice": len(practice[code]),
            "assessment": len(assessed[code]),
            "qcm": qcm[code],
            "remediation": remediation[code],
            "method": methods[code],
        }
        missing = []
        if not practice[code]:
            missing.append("NO_TARGETED_PRACTICE")
        if not remediation[code]:
            missing.append("NO_REMEDIATION")
        if not methods[code]:
            missing.append("NO_METHOD")
        if not qcm[code]:
            missing.append("NO_QCM")
        if kind in MULTI_GESTURE_TYPES and len(paths) < 2:
            missing.append("SINGLE_REASONING_PATH_FOR_COMPOSITE_CAPACITY")
        status = "SUFFICIENT" if not missing else "INSUFFICIENT"
        rows[code] = {
            "libelle_eleve": libelle,
            "capacity_type": kind,
            "reasoning_paths": paths,
            "distinct_opportunities": sum(1 for v in opportunities.values() if v),
            "opportunities": opportunities,
            "practice": practice[code],
            "assessed_by": assessed[code],
            "missing_function": missing,
            "status": status,
        }

    all_paths = sorted({g for gs in gestures.values() for g in gs})
    dominant = collections.Counter()
    for path in sorted((base / "exercices").glob("*.tex")):
        for gesture in meta(path).get("gestes") or []:
            dominant[gesture] += 1
    statuses = collections.Counter(row["status"] for row in rows.values())
    return {
        "artifact_type": "chapter_richness_matrix",
        "schema_version": 1,
        "generated_by": "scripts/build_chapter_richness_matrix.py",
        "chapter": chapter,
        "rule": (
            "la richesse se mesure en occasions distinctes et en gestes de "
            "raisonnement declares ; jamais en nombre de fichiers"
        ),
        "capacities": rows,
        "diversity_profile": dict(sorted(dominant.items(), key=lambda kv: -kv[1])),
        "distinct_reasoning_paths": all_paths,
        "diversity_status": (
            "SUFFICIENT"
            if len(all_paths) >= 4
            and max(dominant.values(), default=0) <= 0.5 * sum(dominant.values())
            else "INSUFFICIENT"
        ),
        "counts": dict(statuses),
        "insufficient": sorted(c for c, r in rows.items() if r["status"] != "SUFFICIENT"),
        "unknown": 0,
        "capacities_digest": "sha256:"
        + hashlib.sha256(
            json.dumps(sorted(rows), separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
    }


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapter", default="TSPE-GEOMETRIE-ESPACE")
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)

    payload = build_matrix(arguments.chapter)
    target = ROOT / f"audit/CHAPTER_RICHNESS_{arguments.chapter}.json"
    rendered = render(payload)
    if arguments.check:
        current = target.read_text(encoding="utf-8") if target.is_file() else ""
        if current != rendered:
            print(f"STALE: {target.relative_to(ROOT)}")
            return 1
        return 0
    target.write_text(rendered, encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
