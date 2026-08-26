"""Tests du controle de classe variance / ecart-type (P0 1SPE-VARALEA-CO-048).

Le controle doit attraper la CLASSE du defaut, pas seulement l'objet CO-048, et
ne doit produire aucun faux positif sur les ecritures exactes du corpus
(fractions, racines symboliques, chaines d'egalites terminees par un arrondi).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_variance_sigma_consistency as audit  # noqa: E402
from latex_arith import UnsupportedExpression, evaluate  # noqa: E402

VARALEA = "1SPE-VARIABLES-ALEATOIRES"
CHAPTERS = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"


# --------------------------------------------------------------------------
# Evaluateur arithmetique LaTeX
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (r"\frac{15}{8}", 1.875),
        # Forme sans accolades : TeX ne consomme qu'un caractere par argument.
        (r"\frac34", 0.75),
        (r"\frac{\sqrt3}{2}", 3**0.5 / 2),
        (r"\sqrt3", 3**0.5),
        (r"10 \times \frac{1}{4} \times \frac{3}{4}", 1.875),
        (r"\frac{125}{3}", 125 / 3),
        (r"\sqrt{\frac{35}{12}}", (35 / 12) ** 0.5),
        (r"\frac{\sqrt{26}}{3}", 26**0.5 / 3),
        ("4{,}41", 4.41),
        (r"77\,760\,000", 77760000.0),
        (r"1600^{2} \times 0{,}6 + 2000^{2} \times 0{,}4", 3136000.0),
    ],
)
def test_latex_arithmetic_is_exact(source: str, expected: float) -> None:
    assert float(evaluate(source)) == pytest.approx(expected, rel=1e-12)


@pytest.mark.parametrize("source", [r"\int_0^1 x", "E(X)", r"\alpha", "{"])
def test_latex_arithmetic_refuses_what_it_cannot_read(source: str) -> None:
    """Aucune valeur approchee silencieuse : hors sous-langage, on refuse."""

    with pytest.raises(UnsupportedExpression):
        evaluate(source)


# --------------------------------------------------------------------------
# Detection de la classe de defaut
# --------------------------------------------------------------------------


def _audit_text(tmp_path: Path, body: str, verify: str = "") -> list:
    meta = {
        "id": "TEST-CO-001",
        "chapitre": "TEST",
        "type_objet": "corrige",
        "status": "generated",
    }
    block = f"% BEGIN-VERIFY\n{verify}% END-VERIFY\n" if verify else ""
    path = tmp_path / "TEST-CO-001.tex"
    path.write_text(f"% META: {json.dumps(meta)}\n{block}{body}\n", encoding="utf-8")
    return audit.audit_object(path, "TEST", [])


def test_detects_variance_sigma_swap(tmp_path: Path) -> None:
    findings = _audit_text(tmp_path, r"$V(X) = 9$ donc $\sigma(X) = 9$.")
    assert [f.defect_class for f in findings] == ["VARIANCE_SIGMA_SWAP"]
    assert findings[0].severity == "P0"


def test_detects_root_mismatch(tmp_path: Path) -> None:
    findings = _audit_text(tmp_path, r"$V(X) = 100$ donc $\sigma(X) = 4$.")
    assert [f.defect_class for f in findings] == ["ROOT_MISMATCH"]


def test_detects_rounding_mismatch(tmp_path: Path) -> None:
    findings = _audit_text(tmp_path, r"$V(X) = 12$ donc $\sigma(X) \approx 3{,}47$.")
    assert [f.defect_class for f in findings] == ["ROUNDING_MISMATCH"]
    assert "3.46" in findings[0].description


def test_detects_unit_carried_by_a_variance(tmp_path: Path) -> None:
    findings = _audit_text(tmp_path, r"$V(X) = 9$~euros et $\sigma(X) = 3$.")
    assert "UNIT_ON_VARIANCE" in {f.defect_class for f in findings}


def test_detects_sigma_without_any_oracle(tmp_path: Path) -> None:
    """Exactement la forme du P0 CO-048 : une valeur approchee sans support."""

    findings = _audit_text(tmp_path, r"Mais $\sigma \approx 3946$~euros.")
    assert [f.defect_class for f in findings] == ["SIGMA_WITHOUT_ORACLE"]
    assert findings[0].severity == "P0"


def test_a_sigma_covered_by_the_sympy_oracle_is_accepted(tmp_path: Path) -> None:
    findings = _audit_text(
        tmp_path,
        r"Mais $\sigma \approx 3944$~euros.",
        verify="% assert round(float(sqrt(15552000))) == 3944\n",
    )
    assert findings == []


# --------------------------------------------------------------------------
# Absence de faux positifs sur les ecritures exactes du corpus
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "body",
    [
        r"$V(X) = np(1-p) = 10 \times \frac{1}{4} \times \frac{3}{4} = \frac{15}{8}$. "
        r"$\sigma(X) = \sqrt{\frac{15}{8}} \approx 1{,}37$.",
        r"$V(G) = 100 \times \frac{5}{12} = \frac{500}{12} = \frac{125}{3} \approx 41{,}7$. "
        r"$\sigma(G) \approx 6{,}45$~euros.",
        r"$V(X) = 100 \times \frac{1}{2} \times \frac{1}{2} = 25$, donc $\sigma(X) = 5$.",
        r"$E(X)=1{,}3,\qquad V(X)=4{,}41,\qquad \sigma(X)=2{,}1.$",
    ],
)
def test_exact_writings_are_not_flagged(tmp_path: Path, body: str) -> None:
    """Une chaine terminee par un arrondi ne doit pas servir de reference."""

    assert _audit_text(tmp_path, body) == []


# --------------------------------------------------------------------------
# Etat reel du corpus
# --------------------------------------------------------------------------


def test_co_048_is_corrected_and_covered_by_its_oracle() -> None:
    path = CHAPTERS / VARALEA / "corriges" / "1SPE-VARALEA-CO-048.tex"
    text = path.read_text(encoding="utf-8")
    assert r"15\,552\,000" in text
    assert r"3\,944" in text
    assert "3946" not in text
    assert "assert V5 == 15552000" in text
    assert "assert round(float(sqrt(V5))) == 3944" in text
    # Les trois affirmations du texte que l'oracle amont ne couvrait pas :
    assert "assert V == 77760000" in text
    assert "assert round(float(sigma)) == 8818" in text
    assert "sqrt(5)" in text


def test_co_048_sympy_oracle_executes() -> None:
    import re

    path = CHAPTERS / VARALEA / "corriges" / "1SPE-VARALEA-CO-048.tex"
    block = re.search(
        r"% BEGIN-VERIFY(.*?)% END-VERIFY", path.read_text(encoding="utf-8"), re.DOTALL
    )
    assert block is not None
    code = "\n".join(
        line[2:] if line.startswith("% ") else line.lstrip("%")
        for line in block.group(1).strip().splitlines()
    )
    exec(compile(code, str(path), "exec"), {})  # noqa: S102


def test_the_math_corpus_carries_no_remaining_p0_of_this_class() -> None:
    report = audit.audit_corpus()
    blocking = [f for f in report["findings"] if f["severity"] == "P0"]
    assert blocking == [], blocking


def test_the_audit_covers_every_math_chapter() -> None:
    report = audit.audit_corpus()
    expected = sorted(path.name for path in CHAPTERS.iterdir() if path.is_dir())
    assert report["scope_chapters"] == expected
    assert len(expected) >= 35
