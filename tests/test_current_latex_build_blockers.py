from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATH = ROOT / "Mathematiques" / "manuel-maths"


def test_1spe_intuitive_limits_uses_a_defined_canonical_notice_box() -> None:
    source = (
        MATH / "chapitres/1SPE-SUITES/cours/17_C8_limites_intuitives.tex"
    ).read_text(encoding="utf-8")

    assert r"\attention" not in source
    assert r"\begin{remarqueV}" in source
    assert r"\end{remarqueV}" in source


def test_tspe_convexity_diagnostics_have_balanced_inline_math() -> None:
    payload = json.loads(
        (
            MATH
            / "chapitres/TSPE-DERIVATION-CONVEXITE/qcm/TSPE-DERIVATION-CONVEXITE-QCM.json"
        ).read_text(encoding="utf-8")
    )

    for question in payload["questions"]:
        for option, diagnostic in question["diagnostics"].items():
            assert diagnostic["erreur"].count("$") % 2 == 0, (
                question["id"],
                option,
                diagnostic["erreur"],
            )
