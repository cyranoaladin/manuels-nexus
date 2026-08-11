#!/usr/bin/env python3
"""Validate ready supports against per-sequence disciplinary contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import re

import yaml

from scripts._qa_common import FULL_SEQUENCE_SCOPE, ROOT

CONTRACT_DIR = ROOT / "03_progressions" / "supports" / "contracts"


@dataclass
class ContractResult:
    errors: list[str] = field(default_factory=list)


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[’']", "'", text)
    text = re.sub(r"[^a-z0-9àâçéèêëîïôûùüÿñæœ_+*/<>= -]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def prefix_text(root: Path, prefix: str) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in sorted(root.rglob(f"{prefix}_*.md")))


def load_contract(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def analyze_contracts(
    root: Path = ROOT / "03_progressions" / "supports",
    contract_dir: Path = CONTRACT_DIR,
    prefixes: list[str] | None = None,
) -> ContractResult:
    prefixes = prefixes or [*FULL_SEQUENCE_SCOPE["premiere"], *FULL_SEQUENCE_SCOPE["terminale"]]
    result = ContractResult()
    for prefix in prefixes:
        contract_path = contract_dir / f"{prefix}_contract.yml"
        if not contract_path.exists():
            result.errors.append(f"{prefix}: contrat absent")
            continue
        contract = load_contract(contract_path)
        combined = normalize(prefix_text(root, prefix))
        if not combined:
            result.errors.append(f"{prefix}: aucun support trouvé")
            continue
        for item in contract.get("must_include", []) or []:
            if normalize(str(item)) not in combined:
                result.errors.append(f"{prefix}: élément obligatoire absent -> {item}")
        for item in contract.get("must_not", []) or []:
            if normalize(str(item)) in combined:
                result.errors.append(f"{prefix}: interdit pédagogique présent -> {item}")
        for key in [
            "notions_exigibles",
            "capacites_officielles",
            "exemples_obligatoires",
            "cas_limites",
            "erreurs_frequentes",
            "types_exercices_attendus",
            "tp_attendu",
            "interdits_pedagogiques",
            "criteres_validation_humaine",
        ]:
            if not contract.get(key):
                result.errors.append(f"{prefix}: champ contrat vide -> {key}")
    return result


def main() -> int:
    result = analyze_contracts()
    if result.errors:
        print("check_sequence_contracts: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print("check_sequence_contracts: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
