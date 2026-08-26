"""Regressions sur la definition canonique d'une suite geometrique.

Decision humaine du 2026-08-27. Sous la definition canonique

    il existe q tel que, pour tout n,  u_{n+1} = q u_n,

une suite geometrique PEUT comporter un terme nul : il suffit de q = 0, ou
d'un terme initial nul. Le quotient u_{n+1}/u_n n'est qu'une caracterisation
CONDITIONNELLE, valable lorsque les termes sont non nuls ; ce n'est pas la
definition generale.

Ces tests empechent la reintroduction des deux erreurs correspondantes.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_geometric_sequence_definition as audit  # noqa: E402

SUITES_QCM = (
    ROOT / "Mathematiques" / "manuel-maths" / "chapitres" / "1SPE-SUITES"
    / "qcm" / "1SPE-SUITES-QCM.json"
)


def geometric(first: Fraction, ratio: Fraction, count: int) -> list[Fraction]:
    """Suite geometrique construite par la definition canonique."""

    terms = [first]
    for _ in range(count - 1):
        terms.append(ratio * terms[-1])
    return terms


# --------------------------------------------------------------------------
# La definition canonique
# --------------------------------------------------------------------------


def test_a_zero_ratio_yields_a_valid_geometric_sequence() -> None:
    terms = geometric(Fraction(7), Fraction(0), 5)
    assert terms == [Fraction(7), *[Fraction(0)] * 4]
    ratio = Fraction(0)
    assert all(terms[i + 1] == ratio * terms[i] for i in range(len(terms) - 1))


def test_a_geometric_sequence_may_carry_a_zero_term() -> None:
    """Deux constructions donnent des termes nuls sans sortir de la definition."""

    assert Fraction(0) in geometric(Fraction(7), Fraction(0), 5)
    assert set(geometric(Fraction(0), Fraction(3), 5)) == {Fraction(0)}


def test_the_quotient_is_not_the_general_definition() -> None:
    """Le quotient n'est meme pas defini des qu'un terme s'annule."""

    terms = geometric(Fraction(7), Fraction(0), 4)
    with pytest.raises(ZeroDivisionError):
        _ = terms[2] / terms[1]
    # La definition, elle, reste verifiable sur toute la suite.
    assert all(terms[i + 1] == Fraction(0) * terms[i] for i in range(len(terms) - 1))


def test_the_quotient_characterisation_holds_only_for_non_zero_terms() -> None:
    terms = geometric(Fraction(4), Fraction(3, 2), 5)
    assert all(term != 0 for term in terms)
    quotients = {terms[i + 1] / terms[i] for i in range(len(terms) - 1)}
    assert quotients == {Fraction(3, 2)}


# --------------------------------------------------------------------------
# Le QCM 1SPE-SUITES retenu
# --------------------------------------------------------------------------


def test_the_retained_q9_has_a_single_unambiguous_answer() -> None:
    questions = {
        item["id"]: item
        for item in json.loads(SUITES_QCM.read_text(encoding="utf-8"))["questions"]
    }
    question = questions["Q9"]
    assert question["correcte"] == "C"
    assert "u_{n+1}=qu_n" in question["options"]["C"].replace(" ", "")
    # La bonne reponse est la definition ; les distracteurs ne le sont pas.
    assert question["options"]["B"] != question["options"]["C"]
    assert set(question["diagnostics"]) == {"A", "B", "D"}
    assert question["correcte"] not in question["diagnostics"]


def test_no_option_of_q9_claims_a_geometric_sequence_excludes_zero_terms() -> None:
    questions = {
        item["id"]: item
        for item in json.loads(SUITES_QCM.read_text(encoding="utf-8"))["questions"]
    }
    for label, text in questions["Q9"]["options"].items():
        normalised = text.lower()
        assert "terme nul" not in normalised, (label, text)


# --------------------------------------------------------------------------
# Le corpus entier
# --------------------------------------------------------------------------


def test_the_corpus_carries_no_zero_term_misconception() -> None:
    findings = [
        item for item in audit.scan() if item.defect_class == "ZERO_TERM_MISCONCEPTION"
    ]
    assert findings == [], [(item.path, item.line, item.excerpt) for item in findings]


def test_the_corpus_never_presents_the_quotient_as_the_general_definition() -> None:
    findings = [
        item
        for item in audit.scan()
        if item.defect_class == "QUOTIENT_AS_GENERAL_DEFINITION"
    ]
    assert findings == [], [(item.path, item.line, item.excerpt) for item in findings]


def test_the_audit_recognises_both_defects_when_they_appear(tmp_path: Path) -> None:
    """Le controle doit rester capable de les detecter."""

    sample = tmp_path / "sample.tex"
    sample.write_text(
        "En particulier, une suite geometrique ne peut pas avoir de terme nul.\n"
        "Le quotient est constant : c'est la definition d'une suite geometrique.\n",
        encoding="utf-8",
    )
    text = sample.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert audit.ZERO_TERM_RE.search(lines[0])
    assert audit.QUOTIENT_DEFINITION_RE.search(lines[1])
    assert not audit.SAFEGUARD_RE.search(lines[1])


def test_a_conditional_wording_is_not_flagged() -> None:
    safe = (
        "Lorsque les termes sont non nuls, la constance du quotient est une "
        "caracterisation, pas la definition generale."
    )
    assert audit.SAFEGUARD_RE.search(safe)
