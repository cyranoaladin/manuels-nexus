#!/usr/bin/env python3
"""Etat de sunset du contrat de manifeste v1 (provenance couplee a la branche).

Le schema v1 reste enregistre, mais uniquement comme HISTORICAL_MIGRATION_ONLY :
il ne sert qu'a valider une enveloppe heritee SANS build observe, le temps de
la migrer. Cet artefact compte ce qui doit tomber a zero avant PUBLISH_READY.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "audit" / "BUILD_MANIFEST_V1_SUNSET.json"
V1_SCHEMA = "audit/schemas/v1/build-manifest.schema.json"
V2_SCHEMA = "audit/schemas/v1/build-manifest-provenance-v2.schema.json"


def _manifest_paths() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("BUILD_MANIFEST.json")
        if ".git" not in path.parts and "node_modules" not in path.parts
    )


def _receipt_paths() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("build-receipt*.json")
        if ".git" not in path.parts
    )


def _v1_producers() -> list[str]:
    """Producteurs d'execution capables d'ecrire une enveloppe v1."""

    producer = (ROOT / "scripts" / "build_manifest.py").read_text(encoding="utf-8")
    offenders: list[str] = []
    if re.search(r'"schema_version":\s*1\b', producer):
        offenders.append("scripts/build_manifest.py")
    if '"branch": branch' in producer:
        offenders.append("scripts/build_manifest.py:provenance")
    return sorted(set(offenders))


def _v1_consumers() -> list[dict[str, str]]:
    """Chemins d'execution qui acceptent encore une enveloppe v1."""

    inventory = (ROOT / "scripts" / "inventory_collection.py").read_text(encoding="utf-8")
    consumers: list[dict[str, str]] = []
    if "legacy_envelope_migration" in inventory:
        consumers.append(
            {
                "path": "scripts/inventory_collection.py",
                "symbol": "legacy_envelope_migration",
                "class": "HISTORICAL_MIGRATION_ONLY",
                "restriction": "enveloppe vide uniquement, aucun build observe",
            }
        )
    return consumers


def build_ledger() -> dict[str, Any]:
    manifests = []
    for path in _manifest_paths():
        payload = json.loads(path.read_text(encoding="utf-8"))
        manifests.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "schema_version": payload.get("schema_version"),
                "provenance_binding_version": (payload.get("provenance") or {}).get(
                    "provenance_binding_version"
                ),
                "observed_builds": len(payload.get("builds") or []),
            }
        )
    receipts = []
    for path in _receipt_paths():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        provenance = payload.get("provenance")
        receipts.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "is_v1": isinstance(provenance, dict) and "branch" in provenance,
            }
        )

    v1_manifests = [row for row in manifests if row["schema_version"] == 1]
    v1_receipts = [row for row in receipts if row["is_v1"]]
    producers = _v1_producers()
    consumers = _v1_consumers()

    return {
        "artifact_type": "build_manifest_v1_sunset",
        "schema_version": 1,
        "generated_by": "scripts/build_manifest_v1_sunset_ledger.py",
        "V1_SCHEMA_PRESENT": (ROOT / V1_SCHEMA).is_file(),
        "V1_SCHEMA_CLASS": "HISTORICAL_MIGRATION_ONLY",
        "V1_RUNTIME_PRODUCERS": len(producers),
        "V1_RUNTIME_PRODUCER_PATHS": producers,
        "V1_RUNTIME_CONSUMERS": len(consumers),
        "V1_RUNTIME_CONSUMER_PATHS": consumers,
        "V1_CURRENT_MANIFESTS": len(v1_manifests),
        "V1_CURRENT_BUILD_RECEIPTS": len(v1_receipts),
        "manifests": manifests,
        "receipts": receipts,
        "publish_ready_requirement": {
            "V1_RUNTIME_PRODUCERS": 0,
            "V1_RUNTIME_CONSUMERS": 0,
            "V1_CURRENT_MANIFESTS": 0,
            "V1_CURRENT_BUILD_RECEIPTS": 0,
        },
        "no_current_build_can_be_attested_in_v1": not producers,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build_ledger()
    rendered = render_json(payload)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("STALE: audit/BUILD_MANIFEST_V1_SUNSET.json")
        print(
            "v1 sunset: producers="
            f"{payload['V1_RUNTIME_PRODUCERS']} consumers="
            f"{payload['V1_RUNTIME_CONSUMERS']} manifests="
            f"{payload['V1_CURRENT_MANIFESTS']} receipts="
            f"{payload['V1_CURRENT_BUILD_RECEIPTS']}"
        )
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.name}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
