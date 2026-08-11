#!/usr/bin/env python3
"""Audit semantic richness of sequence contracts without promoting resources."""

from __future__ import annotations

import yaml

from scripts._qa_common import ROOT, print_result


CONTRACTS = ROOT / "03_progressions" / "supports" / "contracts"
REQUIRED_LISTS = {
    "notions_exigibles": 2,
    "capacites_officielles": 1,
    "exemples_obligatoires": 2,
    "cas_limites": 2,
    "erreurs_frequentes": 2,
    "types_exercices_attendus": 2,
    "interdits_pedagogiques": 2,
    "must_include": 3,
    "must_not": 2,
    "criteres_validation_humaine": 2,
}


def list_len(value: object) -> int:
    return len(value) if isinstance(value, list) else 0


def main() -> None:
    errors: list[str] = []
    rich = 0
    poor: list[str] = []
    for path in sorted(CONTRACTS.glob("*_contract.yml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        missing: list[str] = []
        for key, minimum in REQUIRED_LISTS.items():
            if list_len(data.get(key)) < minimum:
                missing.append(f"{key}<{minimum}")
        if not data.get("theme"):
            missing.append("theme absent")
        if not data.get("sequence"):
            missing.append("sequence absent")
        if missing:
            poor.append(f"{path.name}: {', '.join(missing)}")
        else:
            rich += 1
    if rich + len(poor) != 35:
        errors.append(f"{rich + len(poor)} contrats détectés, 35 attendus")
    errors.extend(poor)
    print(f"Contrats riches : {rich}")
    print(f"Contrats pauvres : {len(poor)}")
    print_result("check_contract_substance_quality", errors)


if __name__ == "__main__":
    main()
