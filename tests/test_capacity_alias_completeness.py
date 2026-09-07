"""Un code local sans alias officiel doit le déclarer, jamais l'omettre.

`ref_capacite` est un alias un-vers-un : `capacity_identity.REF_EXACT` résout
une chaîne déclarée par égalité avec lui, donc deux codes locaux partageant une
même référence officielle rendraient le crédit ambigu. Mais le schéma n'offrait
que deux formes : porter un alias, ou n'avoir aucun champ — et cette seconde
forme ne distinguait pas l'omission accidentelle du choix éditorial.

Un code local qui travaille une facette d'une capacité officielle déjà portée
par un code frère doit le déclarer explicitement et nommer le frère. Le gate
vérifie alors que ce frère existe et porte bien cette référence : la
déclaration est contrôlée, pas crue sur parole.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import inventory_collection as ic  # noqa: E402


def _contract_paths() -> list[Path]:
    return sorted(ROOT.glob("*/**/chapitres/*/contrat.yaml"))


def _capacities(path: Path) -> list[dict]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return [c for c in (payload.get("capacites") or []) if isinstance(c, dict)]


def test_no_capacity_silently_omits_its_official_reference() -> None:
    silent = []
    for path in _contract_paths():
        for capacity in _capacities(path):
            has_ref = bool(str(capacity.get("ref_capacite") or "").strip())
            declared = isinstance(capacity.get("sans_alias_officiel"), dict)
            if not has_ref and not declared:
                silent.append(f"{path.relative_to(ROOT)}::{capacity.get('code')}")
    assert silent == []


def test_a_declared_absence_names_a_sibling_that_actually_carries_it() -> None:
    """La facette doit renvoyer à une capacité officielle réellement couverte."""
    broken = []
    for path in _contract_paths():
        capacities = _capacities(path)
        by_code = {c.get("code"): c for c in capacities}
        for capacity in capacities:
            declaration = capacity.get("sans_alias_officiel")
            if not isinstance(declaration, dict):
                continue
            bearer = by_code.get(declaration.get("porte_par"))
            official = str(declaration.get("facette_de") or "").strip()
            where = f"{path.relative_to(ROOT)}::{capacity.get('code')}"
            if bearer is None:
                broken.append(f"{where}: code frère inexistant")
            elif str(bearer.get("ref_capacite") or "").strip() != official:
                broken.append(f"{where}: le frère ne porte pas {official}")
            elif not official:
                broken.append(f"{where}: facette_de vide")
    assert broken == []


def test_the_official_reference_stays_a_one_to_one_alias() -> None:
    seen: dict[str, str] = {}
    duplicates = []
    for path in _contract_paths():
        for capacity in _capacities(path):
            ref = str(capacity.get("ref_capacite") or "").strip()
            if not ref:
                continue
            where = f"{path.relative_to(ROOT)}::{capacity.get('code')}"
            if ref in seen:
                duplicates.append(f"{ref}: {seen[ref]} et {where}")
            seen[ref] = where
    assert duplicates == []


def test_the_gate_rejects_an_undeclared_omission(tmp_path: Path) -> None:
    """Le défaut par défaut reste l'anomalie : la tolérance est opt-in."""
    capacity = {"code": "C9", "libelle_eleve": "sans rien"}
    verdict = ic._capacity_alias_verdict(capacity, {"C9": capacity})
    assert verdict is not None
    assert "ref_capacite" in verdict


def test_the_gate_rejects_a_declaration_pointing_at_a_missing_sibling() -> None:
    capacity = {
        "code": "C9",
        "sans_alias_officiel": {"facette_de": "X-2026-C4", "porte_par": "C42"},
    }
    verdict = ic._capacity_alias_verdict(capacity, {"C9": capacity})
    assert verdict is not None
    assert "C42" in verdict


def test_the_gate_rejects_a_declaration_whose_sibling_carries_another_reference() -> None:
    bearer = {"code": "C1", "ref_capacite": "X-2026-C2"}
    capacity = {
        "code": "C9",
        "sans_alias_officiel": {"facette_de": "X-2026-C4", "porte_par": "C1"},
    }
    verdict = ic._capacity_alias_verdict(capacity, {"C1": bearer, "C9": capacity})
    assert verdict is not None
    assert "X-2026-C4" in verdict


def test_the_gate_accepts_a_fully_justified_declaration() -> None:
    bearer = {"code": "C1", "ref_capacite": "X-2026-C4"}
    capacity = {
        "code": "C9",
        "sans_alias_officiel": {"facette_de": "X-2026-C4", "porte_par": "C1"},
    }
    assert ic._capacity_alias_verdict(capacity, {"C1": bearer, "C9": capacity}) is None
