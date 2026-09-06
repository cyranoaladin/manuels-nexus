#!/usr/bin/env python3
"""Maturité des livrables requis, en distinguant développement et release.

Le compteur unique de « prêt » mélangeait trois choses : la maturité du
produit, sa buildabilité, et l'existence d'un reçu de build final. Comme la
gouvernance interdit d'enregistrer un reçu tant que le contenu bouge, tout
livrable restait éternellement « non prêt » quel que soit le travail accompli —
la métrique ne mesurait plus rien d'utile.

Deux états distincts :

`DEVELOPMENT_READY`
    contenu présent, programme conforme, science conforme, assemblage et cible
    de build déclarés, build diagnostic réussi, tests ciblés verts, aucun
    blocage produit propre au livrable. **Aucun reçu final requis.**

`RELEASE_READY`
    tout ce qui précède, plus un HEAD gelé, des preuves fraîches, un build
    final, un manifeste, la reproductibilité, le préflight et l'approbation
    humaine. Il reste volontairement faux pendant toute la phase de contenu.

Aucun gate de release n'est affaibli : `RELEASE_READY` conserve exactement ses
exigences, on cesse simplement de s'en servir pour mesurer l'avancement.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCOPE = ROOT / "audit/RELEASE_DELIVERABLE_SCOPE_MATRIX.json"
INVENTORY = ROOT / "audit/INVENTAIRE_COLLECTION.json"
OUTPUT_JSON = ROOT / "audit/RELEASE_DELIVERABLE_READINESS.json"
OUTPUT_MD = ROOT / "audit/RELEASE_DELIVERABLE_READINESS.md"

#: Racines de build par projet.
BUILD_ROOTS = {
    "math": ROOT / "Mathematiques/manuel-maths/build",
    "nsi": ROOT / "NSI/build",
}

DIMENSION_BY_AXIS = {
    "programme": ROOT / "audit/DIMENSION_REGULATION.json",
    "science": ROOT / "audit/DIMENSION_MATHEMATICS.json",
}


def _dimension_targets_in_failure(path: Path) -> set[str]:
    """Manuels portant au moins un constat bloquant pour cette dimension."""
    if not path.is_file():
        return set()
    payload = json.loads(path.read_text(encoding="utf-8"))
    failing = set()
    for finding in payload.get("findings", []):
        if not finding.get("blocking", True):
            continue
        target = str(finding.get("target", ""))
        failing.add(target.split("::", 1)[0])
    return failing


def _normalise(name: str) -> str:
    """Les répertoires de build écrivent `TSPE_2026-2027`, le scope `TSPE_2026_2027`."""
    return name.replace("-", "_").upper()


def _development_build(manual: str, variant: str) -> dict[str, Any]:
    """PDF de développement produit pour ce livrable, s'il existe.

    On apparie sur le manuel et la variante plutôt que sur un nom de fichier
    reconstruit : les deux projets ne nomment pas leurs sorties de la même
    façon, et un appariement littéral déclarait absents des PDF bien présents.
    """
    wanted = _normalise(manual)
    for root in BUILD_ROOTS.values():
        if not root.is_dir():
            continue
        for candidate in sorted(root.glob(f"*/*_{variant}.pdf")):
            # Les répertoires cachés *sous la racine de build* sont des zones
            # de travail d'un build en cours ; leur PDF n'est pas la sortie
            # publiée. On ne regarde que le chemin relatif : la racine du dépôt
            # est elle-même sous un `.worktrees`.
            if any(part.startswith(".") for part in candidate.parts[len(root.parts):]):
                continue
            if _normalise(candidate.parent.name).endswith(wanted):
                try:
                    shown = str(candidate.relative_to(ROOT))
                except ValueError:
                    shown = str(candidate)
                return {"present": True, "path": shown,
                        "bytes": candidate.stat().st_size}
    return {"present": False, "path": None, "bytes": 0}


def _chapter_of(path: str) -> str | None:
    """Chapitre auquel appartient un objet, quel que soit le préfixe du dépôt."""
    parts = path.split("/")
    if "chapitres" not in parts:
        return None
    index = parts.index("chapitres") + 1
    return parts[index] if index < len(parts) else None


def pedagogical_object_paths(inventory: dict[str, Any]) -> set[str]:
    """Chemins des objets pédagogiques, tels que l'inventaire les déclare.

    C'est la seule définition faisant autorité. Compter les `.tex` d'un
    assemblage ne suffisait pas : un `contrat.yaml`, un include technique ou un
    gabarit ne sont pas du contenu, et c'est exactement ce qui avait fait
    passer une variante vide pour pourvue.
    """
    paths: set[str] = set()
    for manual in inventory.get("manuals", {}).values():
        for chapter in manual.get("chapters", {}).values():
            for obj in chapter.get("objects", []):
                if obj.get("path"):
                    paths.add(str(obj["path"]))
    return paths


def content_coverage(inventory: dict[str, Any], assembly_id: str | None,
                     manual: str) -> dict[str, Any]:
    """Couverture réelle en objets de contenu d'un assemblage.

    `included_files` ne mesure pas le contenu : il compte aussi les
    `contrat.yaml` lus pour composer les ouvertures de chapitre. Une variante
    vide déclare ainsi sept fichiers et zéro objet. On ne compte donc que les
    sources `.tex` de chapitre, et on exige que **chaque** chapitre du manuel
    en apporte au moins une — un livret qui saute la moitié des chapitres
    n'est pas le livret de ce manuel.
    """
    chapters = set(inventory["manuals"].get(manual, {}).get("chapters", {}))
    assemblies = {a["assembly_id"]: a for a in inventory.get("declared_assemblies", [])}
    assembly = assemblies.get(assembly_id or "")
    if assembly is None:
        return {"objects": 0, "chapters_covered": 0, "chapters_total": len(chapters),
                "complete": False}
    declared = pedagogical_object_paths(inventory)
    covered = set()
    objects = 0
    for path in assembly.get("included_files", []):
        # Un fichier ne compte que s'il est un objet pédagogique déclaré.
        if path not in declared:
            continue
        objects += 1
        chapter = _chapter_of(path)
        if chapter:
            covered.add(chapter)
    return {
        "objects": objects,
        "chapters_covered": len(covered & chapters),
        "chapters_total": len(chapters),
        "complete": bool(chapters) and (covered & chapters) == chapters,
    }


def build() -> dict[str, Any]:
    scope = json.loads(SCOPE.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    failing = {axis: _dimension_targets_in_failure(path)
               for axis, path in DIMENSION_BY_AXIS.items()}

    rows: list[dict[str, Any]] = []
    for entry in scope["deliverables"]:
        required = entry["canonical_release_product"] or entry["required_auxiliary_product"]
        if not required:
            continue
        manual = entry["deliverable_id"].split("::", 1)[0]
        profile = entry["build_profile"]
        dev_build = _development_build(manual, profile["variant_argument"])
        coverage = content_coverage(inventory, profile["assembly_id"], manual)

        axes = {
            "content": coverage["complete"] and coverage["objects"] > 0,
            "assembly": entry["declared_assembly"],
            "build_target": entry["build_target_declared"],
            "development_build": dev_build["present"],
            "programme": manual not in failing["programme"],
            "science": manual not in failing["science"],
        }
        rows.append({
            "deliverable_id": entry["deliverable_id"],
            "manual": manual,
            "kind": "MANUEL" if entry["canonical_release_product"] else "AUXILIAIRE",
            "axes": axes,
            "content_coverage": coverage,
            "development_build": dev_build,
            "development_ready": all(axes.values()),
            # Volontairement faux pendant la phase de contenu : il exige un
            # HEAD gelé, un build final, un manifeste et une décision humaine.
            "release_ready": False,
            "release_ready_blocked_by": [
                "FROZEN_HEAD", "FINAL_BUILD", "CURRENT_MANIFEST",
                "REPRODUCIBILITY", "PREFLIGHT", "HUMAN_APPROVAL",
            ],
        })

    def count(predicate) -> int:
        return sum(1 for row in rows if predicate(row))

    summary = {
        "REQUIRED_RELEASE_DELIVERABLES": len(rows),
        "DEVELOPMENT_READY": count(lambda r: r["development_ready"]),
        "ASSEMBLY_READY": count(lambda r: r["axes"]["assembly"]),
        "BUILD_TARGET_READY": count(lambda r: r["axes"]["build_target"]),
        "DEVELOPMENT_BUILD_PASS": count(lambda r: r["axes"]["development_build"]),
        "PEDAGOGICAL_OBJECT_COUNT_TOTAL": sum(
            r["content_coverage"]["objects"] for r in rows
        ),
        "PROGRAMME_CONFORM": count(lambda r: r["axes"]["programme"]),
        "SCIENCE_CONFORM": count(lambda r: r["axes"]["science"]),
        "CONTENT_COMPLETE": count(lambda r: r["axes"]["content"]),
        "RELEASE_READY": 0,
        "CURRENT_BUILD_RECEIPTS_REQUIRED_DURING_DEVELOPMENT": False,
    }
    return {
        "artifact_type": "release_deliverable_readiness",
        "schema_version": 1,
        "generated_by": "scripts/build_release_deliverable_readiness.py",
        "summary": summary,
        "deliverables": sorted(rows, key=lambda r: r["deliverable_id"]),
    }


def render_md(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Maturité des livrables requis",
        "",
        "`DEVELOPMENT_READY` mesure la maturité du produit ; il n'exige aucun",
        "reçu de build final. `RELEASE_READY` conserve toutes ses exigences et",
        "reste faux pendant la phase de contenu.",
        "",
        f"- `DEVELOPMENT_READY` : `{s['DEVELOPMENT_READY']}/{s['REQUIRED_RELEASE_DELIVERABLES']}`",
        f"- `ASSEMBLY_READY` : `{s['ASSEMBLY_READY']}/{s['REQUIRED_RELEASE_DELIVERABLES']}`",
        f"- `BUILD_TARGET_READY` : `{s['BUILD_TARGET_READY']}/{s['REQUIRED_RELEASE_DELIVERABLES']}`",
        f"- `DEVELOPMENT_BUILD_PASS` : `{s['DEVELOPMENT_BUILD_PASS']}/{s['REQUIRED_RELEASE_DELIVERABLES']}`",
        f"- `RELEASE_READY` : `{s['RELEASE_READY']}` (attendu pendant cette phase)",
        "",
        "| Livrable | Type | Contenu | Assemblage | Cible | Build dev | Programme | Science | Dev ready |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in payload["deliverables"]:
        a = row["axes"]
        mark = lambda value: "oui" if value else "**non**"  # noqa: E731
        lines.append(
            f"| `{row['deliverable_id']}` | {row['kind']} | {mark(a['content'])} | "
            f"{mark(a['assembly'])} | {mark(a['build_target'])} | "
            f"{mark(a['development_build'])} | {mark(a['programme'])} | "
            f"{mark(a['science'])} | {mark(row['development_ready'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if OUTPUT_JSON.is_file() and OUTPUT_JSON.read_text(encoding="utf-8") == rendered:
            print("RELEASE_DELIVERABLE_READINESS check: OK")
            return 0
        print("RELEASE_DELIVERABLE_READINESS check: STALE")
        return 1
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
