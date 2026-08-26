from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "Mathematiques"
    / "manuel-maths"
    / "chapitres"
    / "1SPE-SUITES"
    / "cours"
    / "07_td_fil_rouge.tex"
)


def _source() -> str:
    return SOURCE.read_text(encoding="utf-8")


def test_fil_rouge_asks_for_and_proves_a_first_crossing() -> None:
    source = _source()
    normalized = " ".join(source.split())

    assert "premier rang $n$ (à partir du rang $10$) tel que $B_n>A_n$" in normalized
    assert "montrer que le solde de B reste ensuite supérieur à celui de A" in normalized
    assert "dépasse définitivement" not in source
    assert "croissance exponentielle" not in source
    assert "l'emporte sur une croissance linéaire" not in source


def test_fil_rouge_permanence_argument_is_elementary_and_exact() -> None:
    source = _source()

    def b(n: int) -> float:
        return 1000 * 1.004**n

    def a(n: int) -> int:
        return 200 * n

    assert b(1414) <= a(1414)
    assert b(1415) > a(1415)
    assert abs((b(1416) - b(1415)) - 0.004 * b(1415)) < 1e-9
    assert 0.004 * b(1415) > 200

    for evidence in (
        r"B_{n+1}-B_n=0{,}004B_n",
        r"A_{n+1}-A_n=200",
        r"0{,}004B_{1415}\approx1\,135{,}70>200",
        "raisonnement par récurrence",
        "assert B(1416) - B(1415) > 200",
    ):
        assert evidence in source
