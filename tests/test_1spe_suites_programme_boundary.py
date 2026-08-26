from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_1spe_suites_programme_boundary.py"
CHAPTER = ROOT / "Mathematiques" / "manuel-maths" / "chapitres" / "1SPE-SUITES"

EX038 = CHAPTER / "exercices" / "1SPE-SUITES-EX-038.tex"
CO038 = CHAPTER / "corriges" / "1SPE-SUITES-CO-038.tex"
EX042 = CHAPTER / "exercices" / "1SPE-SUITES-EX-042.tex"
CO042 = CHAPTER / "corriges" / "1SPE-SUITES-CO-042.tex"
C5_COURSE = CHAPTER / "cours" / "14_C5_variations.tex"
C1_COURSE = CHAPTER / "cours" / "10_C1_generalites_suites.tex"
EXPECTED_P0_RELATIVE_PATHS = (
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-026.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-026.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-027.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-031.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-031.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-037.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-038.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-038.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-040.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-040.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-042.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-042.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-043.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-043.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-044.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-046.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-048.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-048.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-049.tex",
)


def _producer():
    assert SCRIPT.is_file(), f"analyseur absent: {SCRIPT}"
    spec = importlib.util.spec_from_file_location(
        "check_1spe_suites_programme_boundary", SCRIPT
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _meta(path: Path) -> dict:
    first_line = _source(path).splitlines()[0]
    assert first_line.startswith("% META: ")
    return json.loads(first_line.removeprefix("% META: "))


def _codes(findings: list[dict]) -> set[str]:
    return {finding["code"] for finding in findings}


def test_canonical_p0_scope_scan_is_clean() -> None:
    producer = _producer()

    assert producer.scan_canonical_p0_scope() == []


def test_canonical_chapter_scope_scans_every_current_tex_and_is_clean() -> None:
    producer = _producer()
    expected = tuple(sorted(CHAPTER.rglob("*.tex"), key=lambda path: str(path)))

    assert producer.canonical_chapter_tex_paths() == expected
    assert producer.scan_canonical_chapter_scope() == []


def test_chapter_scope_detects_a_violation_outside_the_exact_nineteen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    producer = _producer()
    chapter = tmp_path / "1SPE-SUITES"
    rogue = chapter / "cours" / "rogue.tex"
    rogue.parent.mkdir(parents=True)
    rogue.write_text("La suite est convergente.\n", encoding="utf-8")
    monkeypatch.setattr(producer, "CHAPTER", chapter)
    monkeypatch.setattr(producer, "validated_canonical_p0_paths", lambda: ())

    findings = producer.scan_canonical_chapter_scope()

    assert producer.canonical_chapter_tex_paths() == (rogue,)
    assert _codes(findings) == {"FORMAL_CONVERGENCE_THEOREM"}
    assert findings[0]["path"] == str(rogue)


def test_c5_course_keeps_bounds_but_replaces_formal_limit_with_observation() -> None:
    producer = _producer()
    source = _source(C5_COURSE)
    rendered = producer.normalize_inline_formatting(
        producer.strip_non_rendered_comments(source)
    )

    assert all(term in rendered for term in ("majorée", "minorée", "bornée"))
    assert all(term in rendered for term in (r"u_1=\frac12", r"u_{10}=\frac{10}{11}", r"u_{100}=\frac{100}{101}"))
    assert "On conjecture que les termes se rapprochent de $1$" in rendered
    assert "ne constitue pas une preuve" in rendered
    assert "théorème de la limite monotone" not in rendered
    assert "converge vers $1$" not in rendered
    assert producer.scan_text(source, path=str(C5_COURSE)) == []


def test_c1_course_does_not_import_later_limit_theory() -> None:
    producer = _producer()
    source = _source(C1_COURSE)
    rendered = producer.normalize_inline_formatting(
        producer.strip_non_rendered_comments(source)
    )

    assert "relation de récurrence" in rendered
    assert "formule explicite" in rendered
    assert "classes préparatoires" not in rendered
    assert "propriétés (monotonie, convergence, limite)" not in rendered
    assert producer.scan_text(source, path=str(C1_COURSE)) == []


def test_scanner_rejects_later_theory_vocabulary_as_a_c1_study_method() -> None:
    producer = _producer()
    source = (
        "Sans formule explicite, on peut seulement étudier les propriétés "
        "(monotonie, convergence, limite) de la suite."
    )

    assert _codes(producer.scan_text(source)) == {"LATER_THEORY_SCOPE"}


def test_canonical_p0_scope_is_the_exact_external_nineteen_path_contract() -> None:
    producer = _producer()
    relative_paths = tuple(
        path.resolve().relative_to(ROOT.resolve()).as_posix()
        for path in producer.CANONICAL_P0_PATHS
    )

    assert relative_paths == EXPECTED_P0_RELATIVE_PATHS
    assert len(relative_paths) == 19


@pytest.mark.parametrize("mutation", ("omission", "addition"))
def test_canonical_p0_rejects_scope_mutations(
    monkeypatch: pytest.MonkeyPatch, mutation: str
) -> None:
    producer = _producer()
    paths = list(producer.CANONICAL_P0_PATHS)
    if mutation == "omission":
        paths.pop()
    else:
        paths.append(SCRIPT)
    monkeypatch.setattr(producer, "CANONICAL_P0_PATHS", tuple(paths))

    with pytest.raises(ValueError, match="canonical P0 scope mismatch"):
        producer.scan_canonical_p0_scope()


def test_cli_success_count_is_derived_from_validated_scope(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    producer = _producer()
    p0_paths = (tmp_path / "one.tex", tmp_path / "two.tex")
    chapter_paths = (*p0_paths, tmp_path / "three.tex")
    monkeypatch.setattr(producer, "validated_canonical_p0_paths", lambda: p0_paths)
    monkeypatch.setattr(producer, "canonical_chapter_tex_paths", lambda: chapter_paths)

    def clean_scan(observed_paths):
        assert tuple(observed_paths) == chapter_paths
        return []

    monkeypatch.setattr(producer, "scan_paths", clean_scan)

    assert producer.main() == 0
    assert capsys.readouterr().out == (
        "PASS: 1SPE-SUITES programme boundary clean "
        "(2 P0 files; 3 chapter TeX files)\n"
    )


def test_non_rendered_comments_and_internal_oracles_are_ignored() -> None:
    producer = _producer()
    source = r"""
% BEGIN-VERIFY
% import math
% n = math.ceil(math.log(0.5) / math.log(0.88))
% assert n == 6
% END-VERIFY
La baisse est de 12\,\% et le seuil numérique vaut 9\,000 euros.
"""

    assert producer.scan_text(source, path="fixture.tex") == []
    rendered = producer.strip_non_rendered_comments(source)
    assert "math.log" not in rendered
    assert r"12\,\%" in rendered


@pytest.mark.parametrize(
    "allowed",
    (
        "Déterminer numériquement le premier rang correspondant au seuil.",
        "Les valeurs semblent se rapprocher de 1.",
        "On conjecture que les termes se rapprochent de 1 lorsque n devient grand.",
        "On conjecture que la suite converge vers 1.",
        r"On conjecture que la suite est \textbf{convergente}.",
        "La suite semble converger vers 1.",
        "La suite paraît converger vers 6.",
        r"Un élève conjecture que $(u_n)$ tend vers 6.",
        "Ces valeurs semblent-elles converger ?",
        "Ce raisonnement n'invoque aucun théorème de convergence.",
        "On n'utilise ni limite formelle ni théorème de convergence.",
        r"La complexité est en $O(\log n)$ ; calculer le coût asymptotique.",
        "La limite de vitesse autorisée est un seuil contextuel.",
        "En passant du rang n vers n+1, on multiplie par 0,88.",
    ),
)
def test_allowed_first_spe_wording_is_not_a_raw_word_ban(allowed: str) -> None:
    assert _producer().scan_text(allowed, path="allowed.tex") == []


@pytest.mark.parametrize(
    ("forbidden", "expected_code"),
    (
        (
            r"Pour résoudre l'inéquation, on applique \log_{10} aux deux membres.",
            "LOGARITHM_SOLVING_METHOD",
        ),
        (
            r"On utilise \ln pour calculer le rang minimal.",
            "LOGARITHM_SOLVING_METHOD",
        ),
        (
            "La suite est croissante et majorée, donc elle converge.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "La suite est majorée et croissante, donc elle admet une limite.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "La suite est monotone et bornée, donc elle converge.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "Une suite croissante et majorée converge.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "D'après le théorème de convergence monotone, la suite admet une limite.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            r"On obtient \lim_{n \to +\infty} S_n=1.",
            "FORMAL_LIMIT_NOTATION",
        ),
        (
            "En passant à la limite dans la relation de récurrence, on obtient L=1.",
            "FORMAL_PASSAGE_TO_LIMIT",
        ),
        (
            "On conjecture… La suite est croissante et majorée, donc elle converge.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "La suite converge vers 1.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "La suite est convergente.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "La suite admet pour limite 1.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "On démontre la convergence de la suite.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "On prend la limite dans la relation de récurrence.",
            "FORMAL_PASSAGE_TO_LIMIT",
        ),
        (
            r"La suite est \textbf{convergente} vers 1.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "$S_n$ tend vers 1.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "La limite de la suite est 1.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "On conjecture que les premiers termes oscillent ; "
            "la suite converge vers 1.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "On conjecture que les premiers termes oscillent ; "
            "$S_n$ tend vers 1.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "On conjecture que les premiers termes oscillent ; "
            "la limite de la suite est 1.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "La suite a pour limite 1.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "La suite possède une limite égale à 1.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "La suite a une limite égale à 1.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "On prouve que la suite se rapproche de 1.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            r"On obtient $u_n \to 1$ lorsque $n \to +\infty$.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            r"On obtient $u_n \longrightarrow 1$ lorsque "
            r"$n \longrightarrow +\infty$.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
        (
            "On en déduit que la limite vaut 1.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
    ),
)
def test_each_forbidden_boundary_class_is_detected(
    forbidden: str, expected_code: str
) -> None:
    findings = _producer().scan_text(forbidden, path="forbidden.tex")

    assert expected_code in _codes(findings), findings


@pytest.mark.parametrize(
    ("forbidden", "expected_code"),
    (
        (
            "Pour résoudre l'inéquation, on applique\n"
            r"\log_{10} aux deux membres.",
            "LOGARITHM_SOLVING_METHOD",
        ),
        (
            "La suite est croissante.\nElle est majorée par 1.\n"
            "Donc elle converge.",
            "FORMAL_CONVERGENCE_THEOREM",
        ),
    ),
)
def test_forbidden_reasoning_split_across_source_lines_is_detected(
    forbidden: str, expected_code: str
) -> None:
    findings = _producer().scan_text(forbidden, path="multiline.tex")

    assert expected_code in _codes(findings), findings


def test_multiline_implication_has_one_logical_conclusion_finding() -> None:
    source = (
        "La suite est croissante.\n"
        "Elle est majorée par 1.\n"
        "Donc elle converge."
    )

    findings = [
        finding
        for finding in _producer().scan_text(source, path="multiline.tex")
        if finding["code"] == "FORMAL_CONVERGENCE_THEOREM"
    ]

    assert len(findings) == 1, findings


@pytest.mark.parametrize("path", (EX038, CO038))
def test_vehicle_pair_keeps_only_its_real_c3_c6_metadata(path: Path) -> None:
    meta = _meta(path)

    assert set(meta["capacites_codes"]) == {"C3", "C6"}
    assert set(meta["capacites"]) == {
        "1SPE-SUITES-C3",
        "1SPE-SUITES-C6",
    }


def test_vehicle_question_and_solution_use_the_same_numeric_method() -> None:
    producer = _producer()
    exercise = producer.strip_non_rendered_comments(_source(EX038))
    correction = producer.strip_non_rendered_comments(_source(CO038))

    assert all(token in exercise for token in ("calculatrice", "tableau de valeurs", "essais successifs"))
    assert all(token in exercise for token in (r"V_5", r"V_6", "arrondies à l'euro"))
    assert all(token in correction for token in (r"V_5", r"V_6", "arrondi à l'euro"))
    assert r"\log" not in exercise
    assert r"\log" not in correction
    assert r"\ln" not in exercise
    assert r"\ln" not in correction


def test_vehicle_q2_uses_the_definition_without_borrowing_q3_formula() -> None:
    correction = _source(CO038)
    question_2 = correction.split("Question 2", 1)[1].split("Question 3", 1)[0]

    assert r"V_{n+1} = 0{,}88 \times V_n" in question_2
    assert "par définition" in question_2
    assert r"\frac{V_{n+1}}{V_n}" not in question_2
    assert r"V_n = 18\,000 \times 0{,}88^n" not in question_2
    assert "calcul du quotient" not in correction


def test_vehicle_exercise_oracle_uses_the_strict_threshold_inequality() -> None:
    exercise = _source(EX038)

    assert "# Seuil V_n < 9000" in exercise
    assert "0.88^n < 0.5 => n > log(0.5)/log(0.88)" in exercise
    assert "# Seuil V_n <= 9000" not in exercise


def test_vehicle_values_rounding_and_sale_timing_are_exact() -> None:
    correction = _source(CO038)
    values = {
        n: Decimal(18_000) * Decimal("0.88") ** n for n in (3, 5, 6)
    }
    rounded = {
        n: value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        for n, value in values.items()
    }

    assert values == {
        3: Decimal("12266.496000"),
        5: Decimal("9499.1745024000"),
        6: Decimal("8359.273562112000"),
    }
    assert rounded == {
        3: Decimal("12266"),
        5: Decimal("9499"),
        6: Decimal("8359"),
    }
    assert all(value in correction for value in ("12\\,266", "9\\,499", "8\\,359"))
    assert "après $6$ années" in correction
    assert "au plus tard au $5^e$ anniversaire" in correction
    assert "avant d'achever la sixième année" in correction


@pytest.mark.parametrize("path", (EX042, CO042))
def test_telescoping_pair_has_real_c8_metadata(path: Path) -> None:
    meta = _meta(path)

    assert set(meta["capacites_codes"]) == {"C4", "C5", "C8"}
    assert set(meta["capacites"]) == {
        "1SPE-SUITES-C4",
        "1SPE-SUITES-C5",
        "1SPE-SUITES-C8",
    }


def test_telescoping_question_and_solution_align_on_numeric_conjecture() -> None:
    exercise = _source(EX042)
    correction = _source(CO042)

    assert all(token in exercise for token in (r"S_{10}", r"S_{100}", r"S_{1\,000}"))
    assert "conjecturer" in exercise
    assert "En déduire sa nature" not in exercise
    assert all(token in correction for token in (r"S_{10}", r"S_{100}", r"S_{1\,000}"))
    assert "semble se rapprocher de $1$" in correction
    assert "On conjecture" in correction


def test_telescoping_displayed_values_are_independently_computed() -> None:
    correction = _source(CO042)
    exact = {n: Fraction(n, n + 1) for n in (10, 100, 1000)}

    assert exact == {
        10: Fraction(10, 11),
        100: Fraction(100, 101),
        1000: Fraction(1000, 1001),
    }
    assert all(value in correction for value in ("0{,}909", "0{,}990", "0{,}999"))
    assert r"\lim" not in _producer().strip_non_rendered_comments(correction)


def test_cli_is_green_and_deterministic() -> None:
    commands = [sys.executable, str(SCRIPT)]
    first = subprocess.run(commands, cwd=ROOT, text=True, capture_output=True)
    second = subprocess.run(commands, cwd=ROOT, text=True, capture_output=True)
    chapter_tex_count = len(tuple(CHAPTER.rglob("*.tex")))

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 0, second.stdout + second.stderr
    assert first.stdout == second.stdout
    assert first.stdout == (
        "PASS: 1SPE-SUITES programme boundary clean "
        f"({len(EXPECTED_P0_RELATIVE_PATHS)} P0 files; "
        f"{chapter_tex_count} chapter TeX files)\n"
    )
