from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_product_scalar_optional_extension_uses_canonical_contract_field() -> None:
    contract = yaml.safe_load(
        (
            ROOT
            / "Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE/contrat.yaml"
        ).read_text(encoding="utf-8")
    )

    assert "extensions" not in contract
    assert {item["code"] for item in contract["extensions_facultatives"]} == {"X1"}
