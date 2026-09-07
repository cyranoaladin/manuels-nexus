#!/usr/bin/env python3
"""Build the exact, non-overlapping partition of current human-review debt.

The historical residual algebra remains the authority for its historical
classes.  This projection adds the object-level evidence and keeps rewritten
objects separate from objects that never had a human approval.
"""

from __future__ import annotations

import argparse
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "audit" / "CURRENT_REVIEW_DEBT_PARTITION.json"
INVENTORY = Path("audit/INVENTAIRE_COLLECTION.json")
ALGEBRA = Path("audit/CURRENT_ANOMALY_SET_ALGEBRA_RESIDUAL.json")
#: Registres de dette bloquante. La liste est celle de
#: `build_residual_true_new_forensics.py`, qui est l'autorité : trois copies
#: de la même liste finissent par diverger, et l'une d'elles avait divergé.
#: Le contrôle d'inventaire fermé ci-dessous reste entier — il exige que les
#: registres découverts dans `audit/` soient exactement ceux déclarés.
LEDGERS = tuple(
    __import__("importlib").import_module(
        "build_residual_true_new_forensics"
    ).DECLARED_DEBT_LEDGERS
)
METHOD_REQUALIFICATION = Path("audit/METHOD_REQUALIFICATION_QUEUE.json")
RESIDUAL_FORENSICS = Path("audit/RESIDUAL_TRUE_NEW_FORENSICS.json")


def _validated_ledger_manifest(root: Path) -> tuple[Path, ...]:
    """Exige un inventaire fermé des registres bloquants courants.

    Un nouveau registre ne peut pas entrer silencieusement dans la release et
    un registre attendu ne peut pas disparaître par omission d'une constante.
    """

    expected = set(LEDGERS)
    discovered: set[Path] = set()
    for path in sorted((root / "audit").glob("*REVIEW_DEBT*.json")):
        relative = path.relative_to(root)
        if relative == OUTPUT.relative_to(ROOT):
            continue
        payload = _read_json(path)
        if payload.get("artifact_type") != "BLOCKING_REVIEW_DEBT_LEDGER":
            raise ValueError(f"registre de dette non classifié: {relative}")
        discovered.add(relative)
    missing = sorted(expected - discovered)
    unexpected = sorted(discovered - expected)
    if missing:
        raise ValueError(
            "registre de dette attendu absent: " + ", ".join(map(str, missing))
        )
    if unexpected:
        raise ValueError(
            "registre de dette bloquant inattendu: "
            + ", ".join(map(str, unexpected))
        )
    return LEDGERS


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"racine JSON non objet: {path}")
    return value


def _digest(values: Iterable[str]) -> str:
    encoded = json.dumps(
        sorted(str(value) for value in values),
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _anomalies_by_fingerprint(
    inventory: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from inventory_collection import _anomaly_fingerprint  # noqa: PLC0415

    result: dict[str, dict[str, Any]] = {}
    for category, anomalies in sorted(inventory.get("anomalies", {}).items()):
        if not isinstance(anomalies, list):
            continue
        for anomaly in anomalies:
            if not isinstance(anomaly, Mapping):
                continue
            fingerprint = _anomaly_fingerprint(anomaly, category=str(category))
            if fingerprint in result:
                raise ValueError(f"empreinte courante non univoque: {fingerprint}")
            path = anomaly.get("path") or anomaly.get("source")
            object_id = anomaly.get("id")
            scope = str(anomaly.get("scope") or "unknown")
            object_key = (
                f"OBJECT:{object_id}"
                if isinstance(object_id, str) and object_id.strip()
                else f"{scope.upper()}:{path}"
            )
            result[fingerprint] = {
                "fingerprint": fingerprint,
                "object_id": object_id,
                "object_key": object_key,
                "path": path,
                "manual": anomaly.get("manual"),
                "chapter": anomaly.get("chapter"),
                "scope": scope,
                "status": anomaly.get("status"),
                "category": str(category),
            }
    return result


def _component(
    name: str,
    fingerprints: Iterable[str],
    objects_by_fingerprint: Mapping[str, Mapping[str, Any]],
    *,
    provenance: str,
) -> dict[str, Any]:
    members = sorted(set(str(value) for value in fingerprints))
    missing = sorted(set(members) - set(objects_by_fingerprint))
    if missing:
        raise ValueError(f"objets courants absents de {name}: {missing[:5]}")
    objects = [dict(objects_by_fingerprint[value]) for value in members]
    object_keys = [str(row["object_key"]) for row in objects]
    object_ids = sorted(
        str(row["object_id"])
        for row in objects
        if isinstance(row.get("object_id"), str) and row["object_id"].strip()
    )
    return {
        "count": len(members),
        "provenance": provenance,
        "fingerprints": members,
        "fingerprints_digest": _digest(members),
        "object_ids": object_ids,
        "object_ids_digest": _digest(object_ids),
        "object_keys_digest": _digest(object_keys),
        "objects": objects,
    }


def _ledger_sets(root: Path) -> tuple[dict[str, set[str]], dict[str, Any]]:
    sets: dict[str, set[str]] = {}
    evidence: dict[str, Any] = {}
    for relative in _validated_ledger_manifest(root):
        ledger = _read_json(root / relative)
        entries = ledger.get("entries")
        if not isinstance(entries, list) or len(entries) != ledger.get("count"):
            raise ValueError(f"registre incohérent: {relative}")
        evidence[str(relative)] = _file_digest(root / relative)
        ledger_id = str(ledger.get("ledger_id") or relative.stem)
        if ledger_id == "TSPE_GEOESPACE_AUTHORED_REVIEW_DEBT_45":
            created = {
                str(row["fingerprint"])
                for row in entries
                if row.get("origin") == "NEW_AUTHORED_UNREVIEWED"
            }
            rewritten = {
                str(row["fingerprint"])
                for row in entries
                if row.get("origin") == "REWRITTEN_PREVIOUSLY_APPROVED"
                and row.get("human_approval_invalidated_by_rewrite") is True
            }
            if created | rewritten != {str(row["fingerprint"]) for row in entries}:
                raise ValueError("provenance TSPE-GEOESPACE incomplète")
            sets["TSPE_GEO_NEW_40"] = created
            sets["TSPE_GEO_REWRITTEN_STALE_APPROVAL_5"] = rewritten
        elif ledger_id == "NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT":
            created = {
                str(row["fingerprint"])
                for row in entries
                if row.get("origin") == "CREATED"
            }
            rewritten = {
                str(row["fingerprint"])
                for row in entries
                if row.get("origin")
                == "REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED"
                and row.get("human_approval_invalidated_by_rewrite") is False
                and row.get("human_approval_evidence") is False
            }
            # Une reecriture d'un objet qui ne portait NI approbation humaine NI
            # verification machine : elle ne perime rien, elle cree de la dette.
            plain_rewrite = {
                str(row["fingerprint"])
                for row in entries
                if row.get("origin") == "REWRITTEN"
                and row.get("human_approval_invalidated_by_rewrite") is False
            }
            # Source modifiee, corps pedagogique identique au digest pres : la
            # declaration se relit, le contenu n'a pas bouge.
            declaration = {
                str(row["fingerprint"])
                for row in entries
                if row.get("origin") == "DECLARATION_CHANGED_SEMANTICS_IDENTICAL"
                and row.get("human_approval_invalidated_by_rewrite") is False
            }
            observed = {str(row["fingerprint"]) for row in entries}
            if created | rewritten | plain_rewrite | declaration != observed:
                raise ValueError("provenance NSI couplée incomplète")
            sets["NSI_COUPLED_NEW_32"] = created
            sets[
                "NSI_COUPLED_REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED_4"
            ] = rewritten
            sets["NSI_COUPLED_REWRITTEN"] = plain_rewrite
            sets["NSI_COUPLED_DECLARATION_CHANGED"] = declaration
        else:
            sets[ledger_id] = {str(row["fingerprint"]) for row in entries}
    return sets, evidence


def _assignment_module():
    """Le resolveur d'imputation, charge une fois."""

    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "review_debt_assignment_for_partition",
        ROOT / "scripts/review_debt_assignment.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_partition(root: Path = ROOT) -> dict[str, Any]:
    inventory = _read_json(root / INVENTORY)
    algebra = _read_json(root / ALGEBRA)["full_current_algebra"]
    historical = algebra["sets"]
    objects_by_fingerprint = _anomalies_by_fingerprint(inventory)
    current = set(str(value) for value in historical["CURRENT_ACTIVE"])
    if current != set(objects_by_fingerprint):
        raise ValueError("inventaire et algèbre courante divergent")

    previously_qualified = set(historical["PREVIOUSLY_QUALIFIED_ACTIVE_DEBT"])
    ledger_sets, ledger_evidence = _ledger_sets(root)
    declared_debt_fingerprints = (
        set().union(*ledger_sets.values()) if ledger_sets else set()
    )
    requalification = _read_json(root / METHOD_REQUALIFICATION)
    declared_stale = {
        str(row["fingerprint"])
        for row in requalification.get("items", [])
        if row.get("state") == "STALE"
    }
    # Un objet deja porte par un registre de dette DECLAREE y est impute une
    # seule fois. La regle vient du resolveur commun, jamais d'une
    # soustraction locale : c'est en la dupliquant qu'elle avait diverge.
    stale_methods = declared_stale - _assignment_module().demoted_by_precedence(
        ledger_sets, {"METHOD_REQUALIFICATION": declared_stale}
    )
    if not stale_methods <= previously_qualified:
        raise ValueError("requalifications périmées hors dette historique 89")
    stale_items = {
        str(row["fingerprint"]): row
        for row in requalification.get("items", [])
        if row.get("state") == "STALE"
    }
    stale_trigo = {
        fingerprint
        for fingerprint, row in stale_items.items()
        if row.get("chapter") == "1SPE-TRIGONOMETRIE"
    }
    stale_a4 = stale_methods - stale_trigo
    current_a4 = previously_qualified - stale_methods
    qualifications = inventory.get("anomaly_qualifications", {})
    if any(
        qualifications.get(fingerprint, {}).get("decision_ref")
        != "audit/A4_METHOD_REVIEW_DEBT_POLICY.md#decision-a4-method-review-debt-2026-08-19"
        or qualifications.get(fingerprint, {}).get("qualified") is not True
        or qualifications.get(fingerprint, {}).get("chapter")
        != "1NSI-ALGO-DICHO-GLOUTON-KNN"
        for fingerprint in current_a4
    ):
        raise ValueError("complément courant du 89 non conforme à la décision A4")
    # Les cardinalites ne sont plus epinglees : elles suivent le corpus des que
    # une fiche de plus est reecrite ou passe en dette declaree. Ce qui est
    # verrouille, c'est que la sous-partition soit EXACTE et DISJOINTE.
    if stale_a4 & stale_trigo or (stale_a4 | stale_trigo) & current_a4:
        raise ValueError("sous-partition décisionnelle du 89 non disjointe")
    if stale_a4 | stale_trigo | current_a4 != previously_qualified:
        raise ValueError("sous-partition décisionnelle du 89 inexacte")

    residual_forensics = _read_json(root / RESIDUAL_FORENSICS)
    residual_entries = residual_forensics.get("entries")
    if not isinstance(residual_entries, list):
        raise ValueError("forensics résiduelles sans entries")
    residual_states = {str(row.get("current_review_state")) for row in residual_entries}
    residual_fingerprints = {str(row["fingerprint"]) for row in residual_entries}
    if residual_states != {"PENDING_QUALIFIED_OPEN_DEBT"}:
        raise ValueError(f"état courant du résiduel 13 inattendu: {sorted(residual_states)}")
    if residual_fingerprints != set(historical["TRUE_NEW"]):
        raise ValueError("résiduel 13 et algèbre historique divergent")

    named_sets: dict[str, set[str]] = {
        "UNCHANGED": set(historical["UNCHANGED"]),
        "APPROVED_TRANSITION_NEW": set(historical["APPROVED_TRANSITION_NEW"]),
        "A4_METHOD_REQUALIFICATION_STALE_83": stale_a4,
        "A4_METHOD_QUALIFIED_CURRENT_3": current_a4,
        "TRIGO_OPTIONAL_EXTENSION_REQUALIFICATION_STALE_3": stale_trigo,
        "RESIDUAL_TRUE_NEW_13": residual_fingerprints,
    }
    named_sets.update(ledger_sets)

    provenance = {
        "UNCHANGED": "surviving baseline review debt, unchanged identity",
        "APPROVED_TRANSITION_NEW": "approved-baseline identity transition still current",
        "A4_METHOD_REQUALIFICATION_STALE_83": (
            "A4 method qualifications invalidated by editorial rewrites; human re-review required"
        ),
        "A4_METHOD_QUALIFIED_CURRENT_3": (
            "current qualified A4 method review debt in 1NSI algorithmics"
        ),
        "TRIGO_OPTIONAL_EXTENSION_REQUALIFICATION_STALE_3": (
            "optional-extension qualifications invalidated by editorial rewrites"
        ),
        "RESIDUAL_TRUE_NEW_13": "true-new residual from the frozen set of 18",
        "TSPE_GEO_NEW_40": "no human approval ever existed",
        "TSPE_GEO_REWRITTEN_STALE_APPROVAL_5": (
            "previous approval invalidated by rewritten content"
        ),
        "NSI_COUPLED_NEW_32": "no human approval ever existed",
        "NSI_COUPLED_REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED_4": (
            "rewritten content whose prior machine verification was not a human approval"
        ),
    }
    for name in named_sets:
        provenance.setdefault(name, "separately declared current review debt")

    intersections = []
    for left, right in combinations(sorted(named_sets), 2):
        overlap = sorted(named_sets[left] & named_sets[right])
        if overlap:
            intersections.append(
                {"left": left, "right": right, "count": len(overlap), "fingerprints": overlap}
            )
    union = set().union(*named_sets.values())
    if intersections or union != current:
        raise ValueError("partition de dette courante ni disjointe ni exhaustive")

    components = {
        name: _component(
            name,
            values,
            objects_by_fingerprint,
            provenance=provenance[name],
        )
        for name, values in named_sets.items()
    }
    tspe = named_sets["TSPE_GEO_NEW_40"] | named_sets[
        "TSPE_GEO_REWRITTEN_STALE_APPROVAL_5"
    ]
    residual = named_sets["RESIDUAL_TRUE_NEW_13"]
    nsi = (
        named_sets["NSI_COUPLED_NEW_32"]
        | named_sets["NSI_COUPLED_REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED_4"]
        | named_sets["NSI_COUPLED_REWRITTEN"]
        | named_sets["NSI_COUPLED_DECLARATION_CHANGED"]
    )
    other = current - tspe - residual
    aliases = {
        "PENDING_HUMAN_REVIEW_13": {
            "alias_of": ["RESIDUAL_TRUE_NEW_13"],
            "count": len(residual),
            "fingerprints_digest": _digest(residual),
            "contributes_to_union": False,
        },
        "HISTORICAL_PENDING_UNQUALIFIED_13_LABEL": {
            "refers_to": ["RESIDUAL_TRUE_NEW_13"],
            "count": len(residual),
            "semantic_alias_valid": False,
            "current_qualification_state": "PENDING_QUALIFIED_OPEN_DEBT",
            "note": (
                "PENDING_UNQUALIFIED is a historical label contradicted by the "
                "current inventory; it is retained only as a named discrepancy"
            ),
            "contributes_to_union": False,
        },
        "PREVIOUSLY_QUALIFIED_ACTIVE_DEBT_89": {
            "aggregate_of": [
                "A4_METHOD_REQUALIFICATION_STALE_83",
                "A4_METHOD_QUALIFIED_CURRENT_3",
                "TRIGO_OPTIONAL_EXTENSION_REQUALIFICATION_STALE_3",
            ],
            "count": len(previously_qualified),
            "fingerprints_digest": _digest(previously_qualified),
            "contributes_to_union": False,
        },
        "TSPE_GEO_REVIEW_PACKET_45": {
            "aggregate_of": [
                "TSPE_GEO_NEW_40",
                "TSPE_GEO_REWRITTEN_STALE_APPROVAL_5",
            ],
            "count": len(tspe),
            "fingerprints_digest": _digest(tspe),
            "provenance_counts": {"NEW": 40, "REWRITTEN_STALE_APPROVAL": 5},
            "contributes_to_union": False,
        },
        "NSI_COUPLED_REVIEW_PACKET_36": {
            # Le suffixe numerique est le LABEL de la decision d'origine, pas
            # un compte vivant : le paquet suit le lot couple, qui grandit a
            # chaque objet reellement touche.
            "aggregate_of": [
                "NSI_COUPLED_NEW_32",
                "NSI_COUPLED_REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED_4",
                "NSI_COUPLED_REWRITTEN",
                "NSI_COUPLED_DECLARATION_CHANGED",
            ],
            "count": len(nsi),
            "fingerprints_digest": _digest(nsi),
            "provenance_counts": {
                "NEW": len(named_sets["NSI_COUPLED_NEW_32"]),
                "REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED": len(
                    named_sets["NSI_COUPLED_REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED_4"]
                ),
                "REWRITTEN": len(named_sets["NSI_COUPLED_REWRITTEN"]),
                "DECLARATION_CHANGED_SEMANTICS_IDENTICAL": len(
                    named_sets["NSI_COUPLED_DECLARATION_CHANGED"]
                ),
            },
            "contributes_to_union": False,
        },
        "OTHER_CURRENT_REVIEW_DEBT": {
            "aggregate_definition": (
                "CURRENT_REVIEW_DEBT minus TSPE_GEO packet minus RESIDUAL_TRUE_NEW_13"
            ),
            "count": len(other),
            "fingerprints_digest": _digest(other),
            "contributes_to_union": False,
        },
    }
    return {
        "schema_version": 1,
        "artifact_type": "current_review_debt_partition",
        "generated_by": "scripts/build_current_review_debt_partition.py",
        "approves_nothing": True,
        "release_acceptance": False,
        "current_review_debt_count": len(current),
        "current_review_debt_digest": _digest(current),
        "components": components,
        "non_counting_aliases_and_aggregates": aliases,
        "pairwise_intersections": intersections,
        "union_equals_current_review_debt": union == current,
        "unknown_count": 0,
        "evidence": {
            str(INVENTORY): _file_digest(root / INVENTORY),
            str(ALGEBRA): _file_digest(root / ALGEBRA),
            str(METHOD_REQUALIFICATION): _file_digest(root / METHOD_REQUALIFICATION),
            str(RESIDUAL_FORENSICS): _file_digest(root / RESIDUAL_FORENSICS),
            **ledger_evidence,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    payload = build_partition(ROOT)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    output = args.out if args.out.is_absolute() else ROOT / args.out
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != rendered:
            print(f"partition de dette périmée: {output.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(f"partition de dette courante: {payload['current_review_debt_count']}")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"partition de dette écrite: {payload['current_review_debt_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
