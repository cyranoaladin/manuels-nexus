"""Deux anomalies distinctes ne peuvent pas porter la même empreinte.

L'empreinte d'anomalie est l'identité des unités de revue humaine : les
registres, la partition de dette et la file de revue sont tous indexés par
elle. Une collision ne produit pas une erreur visible côté revue — elle fait
disparaître des unités, puisque deux défauts n'en occupent plus qu'une.

Le défaut réel : les champs d'identité ignoraient `index`, alors que trois
anomalies d'un même `contrat.yaml` ne se distinguent que par lui. Elles
s'écrasaient. `index` n'est ajouté que lorsqu'il est présent, pour que les
empreintes déjà inscrites dans les registres ne changent pas.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import inventory_collection as ic  # noqa: E402

INVENTORY = ROOT / "audit/INVENTAIRE_COLLECTION.json"


def _current_anomalies() -> list[tuple[str, dict]]:
    payload = json.loads(INVENTORY.read_text(encoding="utf-8"))
    rows = []
    for category, anomalies in sorted(payload.get("anomalies", {}).items()):
        if not isinstance(anomalies, list):
            continue
        rows.extend(
            (str(category), a) for a in anomalies if isinstance(a, dict)
        )
    return rows


def test_current_anomalies_have_pairwise_distinct_fingerprints() -> None:
    buckets = defaultdict(list)
    for category, anomaly in _current_anomalies():
        buckets[ic._anomaly_fingerprint(anomaly, category=category)].append(
            (category, anomaly)
        )
    collisions = {k: v for k, v in buckets.items() if len(v) > 1}
    assert collisions == {}


def test_positional_anomalies_are_distinguished_by_their_index() -> None:
    a = {"index": 1, "path": "c/contrat.yaml", "reason": "vide"}
    b = {"index": 5, "path": "c/contrat.yaml", "reason": "vide"}
    assert ic._anomaly_fingerprint(a, category="invalid_capacities") != \
        ic._anomaly_fingerprint(b, category="invalid_capacities")


def test_adding_index_left_every_indexless_fingerprint_untouched() -> None:
    """Les registres existants ne doivent pas être renommés par ce correctif."""
    anomaly = {
        "chapter": "1SPE-SUITES",
        "id": "1SPE-SUITES-EX-001",
        "manual": "1SPE",
        "path": "a/b.tex",
        "scope": "object",
        "status": "draft",
    }
    fields = ic._anomaly_identity_fields(anomaly, category="blocking_statuses")
    assert "index" not in fields


def test_an_explicit_null_index_is_still_an_identity() -> None:
    without = {"path": "c/contrat.yaml", "reason": "capacites doit etre une liste"}
    with_null = dict(without, index=None)
    assert ic._anomaly_fingerprint(without, category="invalid_capacities") != \
        ic._anomaly_fingerprint(with_null, category="invalid_capacities")
