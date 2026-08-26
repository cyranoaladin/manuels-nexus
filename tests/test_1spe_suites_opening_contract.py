from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CHAPTER = (
    ROOT / "Mathematiques" / "manuel-maths" / "chapitres" / "1SPE-SUITES"
)
OPENING = CHAPTER / "cours" / "00_ouverture.tex"
FIL_ROUGE = CHAPTER / "cours" / "07_td_fil_rouge.tex"
CONTRACT = CHAPTER / "contrat.yaml"


def _metadata(path: Path) -> dict:
    first_line = path.read_text(encoding="utf-8").splitlines()[0]
    return json.loads(first_line.removeprefix("% META: "))


def test_opening_lists_every_contract_capacity_including_c8() -> None:
    contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    expected = [capacity["code"] for capacity in contract["capacites"]]
    opening = OPENING.read_text(encoding="utf-8")

    assert expected == [f"C{index}" for index in range(1, 9)]
    assert _metadata(OPENING)["capacites"] == expected
    for code in expected:
        assert rf"\item[\textbf{{{code}}}]" in opening


def test_opening_and_fil_rouge_use_the_same_savings_scenario() -> None:
    opening = " ".join(OPENING.read_text(encoding="utf-8").split())
    fil_rouge = " ".join(FIL_ROUGE.read_text(encoding="utf-8").split())

    for fact in (
        "livret initialement vide",
        "$200$~€ par mois",
        "capital initial de $1\\,000$~€",
        "taux mensuel de $0{,}4\\,\\%$",
    ):
        assert fact in opening
        assert fact in fil_rouge

    assert "Les deux offres partent du même capital initial" not in opening
    assert "À quel moment l'offre A rattrape-t-elle d'abord l'offre B" in opening
    assert "l'offre B reprend-elle ensuite l'avantage" in opening
