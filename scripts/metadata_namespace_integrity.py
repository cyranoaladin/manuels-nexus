#!/usr/bin/env python3
"""Une identite d'un namespace ne doit jamais habiter le champ d'un autre.

Le corpus declarait des PREREQUIS dans le champ des CAPACITES. Le resolveur
d'identite faisait son travail -- il refusait de crediter quoi que ce soit --
donc aucun faux credit ni faux gap n'en est resulte. Mais l'objet, lui,
affirmait quelque chose de faux sur lui-meme, et une premiere edition ne peut
pas partir avec 124 objets qui mentent sur leur propre metadonnee.

DEUX NAMESPACES, DERIVES DU CONTRAT.

`CAPACITY_NAMESPACE`
    les codes locaux des capacites du chapitre, et leurs references
    officielles `ref_capacite`, plus la clef qualifiee `<chapitre>-<code>`.

`PREREQUISITE_NAMESPACE`
    les codes des prerequis declares par le contrat du chapitre.

Les deux sont LUS dans `contrat.yaml`. Jamais devines a partir de la forme du
code : une regle du type `code.startswith("R")` marcherait aujourd'hui et
mentirait au premier chapitre qui nomme ses capacites autrement.

La verification est VALEUR PAR VALEUR. Un champ de capacites qui contient
`["C1", "R1"]` viole le contrat pour `R1` seulement ; `C1` reste legitime.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

#: Champs qui portent une identite de CAPACITE.
CAPACITY_FIELDS = ("capacites_codes", "capacites")
#: Champs qui portent une identite de PREREQUIS.
PREREQUISITE_FIELDS = ("prerequis_testes",)

PREREQUISITE_IN_CAPACITY_FIELD = "PREREQUISITE_IN_CAPACITY_FIELD"
CAPACITY_IN_PREREQUISITE_FIELD = "CAPACITY_IN_PREREQUISITE_FIELD"
UNKNOWN_CODE_IN_CAPACITY_FIELD = "UNKNOWN_CODE_IN_CAPACITY_FIELD"
UNKNOWN_CODE_IN_PREREQUISITE_FIELD = "UNKNOWN_CODE_IN_PREREQUISITE_FIELD"
SAME_CODE_IN_MUTUALLY_EXCLUSIVE_FIELDS = "SAME_CODE_IN_MUTUALLY_EXCLUSIVE_FIELDS"

VIOLATION_KINDS = (
    PREREQUISITE_IN_CAPACITY_FIELD,
    CAPACITY_IN_PREREQUISITE_FIELD,
    UNKNOWN_CODE_IN_CAPACITY_FIELD,
    UNKNOWN_CODE_IN_PREREQUISITE_FIELD,
    SAME_CODE_IN_MUTUALLY_EXCLUSIVE_FIELDS,
)


def namespaces(contract: Mapping[str, Any], chapter: str) -> dict[str, set[str]]:
    """Les deux namespaces du chapitre, derives de son contrat."""

    capacities = contract.get("capacites") or []
    prerequisites = contract.get("prerequis") or []
    local = {str(row["code"]) for row in capacities if row.get("code")}
    official = {
        str(row["ref_capacite"]) for row in capacities if row.get("ref_capacite")
    }
    return {
        "capacity": local | official | {f"{chapter}-{code}" for code in local},
        "prerequisite": {str(row["code"]) for row in prerequisites if row.get("code")},
    }


def read_meta(path: Path) -> dict[str, Any] | None:
    first = path.read_text(encoding="utf-8", errors="replace").split("\n", 1)[0]
    if "META:" not in first:
        return None
    try:
        return json.loads(first.split("META:", 1)[1].strip())
    except json.JSONDecodeError:
        return None


def classify_value(value: str, scope: Mapping[str, set[str]], field_kind: str) -> str | None:
    """La violation portee par UNE valeur, ou None si elle est a sa place."""

    in_capacity = value in scope["capacity"]
    in_prerequisite = value in scope["prerequisite"]
    if field_kind == "capacity":
        if in_capacity:
            return None
        return (
            PREREQUISITE_IN_CAPACITY_FIELD
            if in_prerequisite
            else UNKNOWN_CODE_IN_CAPACITY_FIELD
        )
    if in_prerequisite:
        return None
    return (
        CAPACITY_IN_PREREQUISITE_FIELD
        if in_capacity
        else UNKNOWN_CODE_IN_PREREQUISITE_FIELD
    )


def object_violations(
    meta: Mapping[str, Any], scope: Mapping[str, set[str]]
) -> list[dict[str, str]]:
    """Violations d'un objet, valeur par valeur."""

    found: list[dict[str, str]] = []
    for fields, field_kind in ((CAPACITY_FIELDS, "capacity"), (PREREQUISITE_FIELDS, "prerequisite")):
        for field in fields:
            for value in meta.get(field) or []:
                kind = classify_value(str(value), scope, field_kind)
                if kind is not None:
                    found.append({"field": field, "value": str(value), "kind": kind})

    capacity_values = {
        str(value) for field in CAPACITY_FIELDS for value in (meta.get(field) or [])
    }
    prerequisite_values = {
        str(value) for field in PREREQUISITE_FIELDS for value in (meta.get(field) or [])
    }
    for value in sorted(capacity_values & prerequisite_values):
        found.append(
            {
                "field": "both",
                "value": value,
                "kind": SAME_CODE_IN_MUTUALLY_EXCLUSIVE_FIELDS,
            }
        )
    return found


def scan(corpora: Iterable[Path]) -> list[dict[str, Any]]:
    """Toutes les violations des objets publiables des corpus donnes."""

    contracts: dict[str, dict[str, set[str]]] = {}
    roots: list[Path] = []
    for corpus in corpora:
        corpus = Path(corpus)
        if not corpus.is_dir():
            continue
        roots.append(corpus)
        for contract_path in sorted(corpus.glob("*/contrat.yaml")):
            data = yaml.safe_load(contract_path.read_text(encoding="utf-8")) or {}
            chapter = str(data.get("chapitre") or contract_path.parent.name)
            contracts[chapter] = namespaces(data, chapter)

    violations: list[dict[str, Any]] = []
    for corpus in roots:
        for path in sorted(corpus.rglob("*.tex")):
            meta = read_meta(path)
            if not meta:
                continue
            scope = contracts.get(str(meta.get("chapitre") or ""))
            if scope is None:
                continue
            for row in object_violations(meta, scope):
                violations.append(
                    {
                        "object_id": meta.get("id"),
                        "object_type": meta.get("type_objet"),
                        "chapter": meta.get("chapitre"),
                        "path": str(path),
                        **row,
                    }
                )
    return violations
