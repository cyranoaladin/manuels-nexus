#!/usr/bin/env python3
"""Couverture pedagogique REELLE, une fois le faux credit retire.

Un objet ne credite une capacite que si son CORPS la sert. Le seul META ne
donne aucun credit : c'est precisement ce que le P0 de clonage a exploite --
dix-sept fiches identiques declarees C1 a C16 creditaient seize capacites
alors qu'une seule, C7, etait reellement traitee.

Ce producteur retire logiquement les credits invalides recenses par
`build_p0_content_clone_ledger.py`, puis mesure ce qui reste, capacite par
capacite et role par role. Il n'enleve aucun fichier.

TROIS PIEGES EVITES.

Identite des capacites. Un objet ne declare pas toujours le code local du
contrat : il declare parfois la reference officielle du programme
(`P-ALGO-01A`) ou la forme qualifiee (`1NSI-ALGO-PARCOURS-TRIS-C1`). Les
rapprocher par extraction de jeton lisait `TSPE-CONCLGN-C1` comme `C1` et
donnait a une capacite le credit de sa voisine. La resolution passe donc par
`capacity_identity.py`, qui n'admet que des egalites exactes dans la portee du
chapitre.

Heritage des corriges. Un corrige ne declare pas toujours de capacite : il la
tient de l'exercice qu'il corrige, via `META.exercice_id`. Les compter sans
cet heritage inventerait des lacunes -- 1SPE en affichait vingt qui n'existent
pas.

Roles mesurables. `qcm` et `evaluations` portent leurs capacites dans leurs
propres structures, pas dans le META du `.tex`. Les mesurer ici produirait un
chiffre faux ; la dette QCM a deja son producteur autoritaire,
`build_qcm_gap_metrics.py`. Ce producteur se limite donc aux cinq roles dont
le META EST le mecanisme de declaration.

Le backlog qui en decoule se compte en unites d'ecriture -- un couple
(capacite, role) sans contenu valide -- jamais en fichiers a remplacer. Le
volume clone d'hier n'est pas un quota pour demain.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CLONE_LEDGER = ROOT / "audit/P0_CONTENT_CLONE_LEDGER.json"
OUTPUT_JSON = ROOT / "audit/TRUE_PEDAGOGICAL_COVERAGE.json"
OUTPUT_MD = ROOT / "audit/TRUE_PEDAGOGICAL_COVERAGE.md"

CORPORA = (
    ROOT / "Mathematiques/manuel-maths/chapitres",
    ROOT / "NSI/chapitres",
)
UNPUBLISHED = ("_harvest",)

#: Les cinq roles dont `META.capacites_codes` est reellement le mecanisme de
#: declaration. `qcm` et `evaluations` en sont exclus a dessein.
MEASURED_ROLES = ("cours", "methodes", "exercices", "corriges", "remediation")


def _resolver_module():
    spec = importlib.util.spec_from_file_location(
        "capacity_identity", ROOT / "scripts/capacity_identity.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _clone_module():
    spec = importlib.util.spec_from_file_location(
        "p0_clone_ledger", ROOT / "scripts/build_p0_content_clone_ledger.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sources() -> list[Path]:
    paths: list[Path] = []
    for corpus in CORPORA:
        if corpus.is_dir():
            paths += [
                p
                for p in sorted(corpus.rglob("*.tex"))
                if not any(part in UNPUBLISHED for part in p.parts)
            ]
    return paths


def build_coverage() -> dict[str, Any]:
    clone = _clone_module()
    identity = _resolver_module()
    resolver = identity.CapacityIdentityResolver.from_corpora()

    def raw_declarations(meta: dict[str, Any]) -> list[str]:
        values: list[str] = []
        for key in ("capacites_codes", "capacites"):
            for value in meta.get(key) or []:
                text = identity.normalise(value)
                if text and text not in values:
                    values.append(text)
        return values

    ledger = json.loads(CLONE_LEDGER.read_text(encoding="utf-8"))
    invalid_credit = set(ledger["objects_on_invalid_credit"])
    # Un clone dont le proprietaire semantique n'est pas demontrable ne prouve
    # rien : il ne credite pas, mais son absence de credit n'est pas une
    # lacune non plus -- le contenu est la, c'est sa capacite qui est
    # indeterminee. Le confondre avec du vide enverrait reecrire un objet qui
    # existe ; le compter comme valide crediterait une capacite au hasard.
    indeterminate_credit = set(ledger["objects_with_indeterminate_credit"])
    paths = _sources()

    # Premiere passe : capacites par identifiant d'objet, pour l'heritage.
    capacities_by_object: dict[str, tuple[str, ...]] = {}
    metas: dict[Path, dict[str, Any]] = {}
    for path in paths:
        meta = clone.read_meta(path.read_text(encoding="utf-8", errors="replace"))
        metas[path] = meta
        chapter = path.parts[path.parts.index("chapitres") + 1]
        if meta.get("id") and chapter in resolver.chapters:
            capacities_by_object[str(meta["id"])] = resolver.resolve_codes(
                chapter, raw_declarations(meta)
            )

    def resolved_capacities(path: Path, role: str) -> tuple[str, ...]:
        meta = metas[path]
        chapter = path.parts[path.parts.index("chapitres") + 1]
        if chapter not in resolver.chapters:
            return ()
        declared = resolver.resolve_codes(chapter, raw_declarations(meta))
        if declared:
            return declared
        if role == "corriges" and meta.get("exercice_id"):
            return capacities_by_object.get(str(meta["exercice_id"]), ())
        return ()

    unresolved: list[str] = []
    valid: dict[str, dict[str, collections.Counter]] = collections.defaultdict(
        lambda: collections.defaultdict(collections.Counter)
    )
    indeterminate: dict[str, dict[str, collections.Counter]] = collections.defaultdict(
        lambda: collections.defaultdict(collections.Counter)
    )
    for path in paths:
        index = path.parts.index("chapitres") + 1
        chapter, role = path.parts[index], path.parts[index + 1]
        if role not in MEASURED_ROLES:
            continue
        capacities = resolved_capacities(path, role)
        relative = str(path.relative_to(ROOT))
        if not capacities:
            unresolved.append(relative)
            continue
        if relative in invalid_credit:
            continue
        if relative in indeterminate_credit:
            for capacity in capacities:
                indeterminate[chapter][capacity][role] += 1
            continue
        for capacity in capacities:
            valid[chapter][capacity][role] += 1

    rows: list[dict[str, Any]] = []
    for corpus in CORPORA:
        if not corpus.is_dir():
            continue
        for chapter_dir in sorted(corpus.iterdir()):
            contract = chapter_dir / "contrat.yaml"
            if not contract.is_file():
                continue
            document = yaml.safe_load(contract.read_text(encoding="utf-8")) or {}
            capacities = [
                str(entry.get("code")) for entry in (document.get("capacites") or [])
            ]
            if not capacities:
                continue
            chapter = chapter_dir.name
            for capacity in capacities:
                for role in MEASURED_ROLES:
                    count = valid[chapter][capacity][role]
                    pending = indeterminate[chapter][capacity][role]
                    if count:
                        state = "VALID_ALIGNED_CONTENT"
                    elif pending:
                        state = "INDETERMINATE_CLONE_CREDIT"
                    else:
                        state = "MISSING"
                    rows.append(
                        {
                            "manual": clone.manual_of(chapter),
                            "chapter": chapter,
                            "capacity": capacity,
                            "role": role,
                            "valid_objects": count,
                            "indeterminate_objects": pending,
                            "state": state,
                        }
                    )

    backlog = [row for row in rows if row["state"] == "MISSING"]
    per_manual: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    per_chapter: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    for row in backlog:
        per_manual[row["manual"]][row["role"]] += 1
        per_manual[row["manual"]]["TOTAL"] += 1
        per_chapter[row["chapter"]][row["role"]] += 1
        per_chapter[row["chapter"]]["TOTAL"] += 1

    identifiers = sorted(
        f"{row['chapter']}/{row['capacity']}/{row['role']}" for row in backlog
    )
    return {
        "artifact_type": "true_pedagogical_coverage",
        "schema_version": 1,
        "generated_by": "scripts/build_true_pedagogical_coverage.py",
        "capacity_identity": (
            "resolue par scripts/capacity_identity.py : egalites exactes dans "
            "la portee du chapitre, jamais par extraction de jeton"
        ),
        "credit_rule": (
            "un objet ne credite une capacite que si son corps la sert ; le "
            "seul META ne donne aucun credit"
        ),
        "cell_states": {
            "VALID_ALIGNED_CONTENT": "au moins un objet credite cette capacite",
            "INDETERMINATE_CLONE_CREDIT": (
                "le contenu existe mais appartient a un groupe de clones dont "
                "le proprietaire semantique n'est pas demontrable : ce n'est "
                "ni un credit ni une lacune, c'est une revue a faire"
            ),
            "MISSING": "aucun contenu, valide ou indetermine",
        },
        "measured_roles": list(MEASURED_ROLES),
        "excluded_roles": {
            "qcm": "capacites portees par le JSON du QCM ; dette mesuree par build_qcm_gap_metrics.py",
            "evaluations": "capacites portees par la structure d'evaluation, pas par META",
        },
        "correction_capacity_inheritance": (
            "un corrige sans capacite declaree herite de celle de son "
            "exercice via META.exercice_id"
        ),
        "inventory": {
            "capacities": len({(r["chapter"], r["capacity"]) for r in rows}),
            "cells": len(rows),
            "cells_with_valid_content": sum(
                1 for r in rows if r["state"] == "VALID_ALIGNED_CONTENT"
            ),
            "cells_with_indeterminate_credit": sum(
                1 for r in rows if r["state"] == "INDETERMINATE_CLONE_CREDIT"
            ),
            "authoring_units_required": len(backlog),
            "objects_without_resolvable_capacity": len(unresolved),
        },
        "authoring_units_digest": "sha256:"
        + hashlib.sha256(
            json.dumps(identifiers, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "per_manual": {k: dict(v) for k, v in sorted(per_manual.items())},
        "per_chapter": {
            k: dict(v)
            for k, v in sorted(
                per_chapter.items(), key=lambda kv: (-kv[1]["TOTAL"], kv[0])
            )
        },
        "rows": rows,
        "authoring_backlog": sorted(
            backlog, key=lambda r: (r["manual"], r["chapter"], r["capacity"], r["role"])
        ),
        "objects_without_resolvable_capacity": sorted(unresolved),
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_md(payload: dict[str, Any]) -> str:
    inventory = payload["inventory"]
    lines = [
        "# Couverture pédagogique réelle",
        "",
        "Un objet ne crédite une capacité que si son **corps** la sert. Le seul",
        "`META` ne donne aucun crédit : c'est exactement ce que le P0 de clonage",
        "exploitait — dix-sept fiches identiques déclarées `C1` à `C16` créditaient",
        "seize capacités alors qu'une seule, `C7`, était traitée.",
        "",
        f"- capacités contractuelles : `{inventory['capacities']}`",
        f"- cellules (capacité × rôle) : `{inventory['cells']}`",
        f"- cellules pourvues : `{inventory['cells_with_valid_content']}`",
        f"- **unités d'écriture requises** : `{inventory['authoring_units_required']}`",
        "",
        "| Manuel | " + " | ".join(payload["measured_roles"]) + " | Total |",
        "|---|" + "---:|" * (len(payload["measured_roles"]) + 1),
    ]
    for manual, counts in sorted(
        payload["per_manual"].items(), key=lambda kv: -kv[1].get("TOTAL", 0)
    ):
        cells = " | ".join(
            str(counts.get(role, 0)) for role in payload["measured_roles"]
        )
        lines.append(f"| `{manual}` | {cells} | **{counts.get('TOTAL', 0)}** |")
    lines += [
        "",
        "Ce backlog se compte en unités d'écriture — un couple (capacité, rôle)",
        "sans contenu valide — jamais en fichiers à remplacer. Le volume cloné",
        "d'hier n'est pas un quota pour demain.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="comparer sans écrire")
    arguments = parser.parse_args(argv)

    payload = build_coverage()
    targets = ((OUTPUT_JSON, render_json(payload)), (OUTPUT_MD, render_md(payload)))
    stale = []
    for path, rendered in targets:
        if arguments.check:
            current = path.read_text(encoding="utf-8") if path.is_file() else ""
            if current != rendered:
                stale.append(str(path.relative_to(ROOT)))
            continue
        path.write_text(rendered, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    for name in stale:
        print(f"STALE: {name}")
    return 1 if stale else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
