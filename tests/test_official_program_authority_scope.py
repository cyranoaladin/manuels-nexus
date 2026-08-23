from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "audit/OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml"


def test_1spe_authority_does_not_name_binomial_law_as_mandatory_domain() -> None:
    payload = yaml.safe_load(AUTHORITY.read_text(encoding="utf-8"))
    first = payload["programme_d_enseignement"]["1SPE"]
    domains = " ".join(first["domains"]).lower()

    assert "loi binomiale" not in domains
    assert "répétitions de bernoulli" in domains
    assert "variables aléatoires" in domains
