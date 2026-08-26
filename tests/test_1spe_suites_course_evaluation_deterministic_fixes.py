from __future__ import annotations

import json
import re
import runpy
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "Mathematiques" / "manuel-maths" / "chapitres" / "1SPE-SUITES"
COURSES = CHAPTER / "cours"
METHODS = CHAPTER / "methodes"
EVALUATIONS = CHAPTER / "evaluations"
PYTHON_SOURCES = CHAPTER / "python"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _meta(path: Path) -> dict:
    first_line = _text(path).splitlines()[0]
    assert first_line.startswith("% META: ")
    return json.loads(first_line.removeprefix("% META: "))


def _compact(source: str) -> str:
    return " ".join(source.split())


def _student_rendered_source(source: str) -> str:
    without_professor_content = re.sub(
        r"\\ifnxVersionProfesseur.*?\\fi",
        "",
        source,
        flags=re.DOTALL,
    )
    return "\n".join(
        line for line in without_professor_content.splitlines() if not line.lstrip().startswith("%")
    )


def test_student_bareme_guard_detects_an_unguarded_mutation() -> None:
    protected = r"Question. \ifnxVersionProfesseur\hfill (2 pts)\fi"
    mutation = r"Question. \hfill (2 pts)"
    point_pattern = re.compile(r"\b\d+\s*(?:pt|pts|points)\b", re.IGNORECASE)

    assert point_pattern.search(_student_rendered_source(protected)) is None
    assert point_pattern.search(_student_rendered_source(mutation)) is not None


def test_c1_recurrence_and_syracuse_claims_are_mathematically_exact() -> None:
    source = _text(COURSES / "10_C1_generalites_suites.tex")
    compact = _compact(source)

    assert "si l'on utilise uniquement la relation de récurrence donnée" in source
    assert "selon la parité de la valeur du terme courant" in compact
    assert r"u_0 = a" in source
    assert "entier strictement positif" in source
    assert "atteint le cycle $1,4,2$" in source
    assert "pour $a=1$, ce comportement est directement vérifié" in source
    assert "selon la parité de l'indice" not in source
    assert "Son comportement à long terme reste un problème ouvert" not in source


def test_exponential_curve_language_is_restricted_to_positive_ratios() -> None:
    arithmetic = _text(COURSES / "11_C2_suites_arithmetiques.tex")
    geometric = _text(COURSES / "12_C3_suites_geometriques.tex")
    geometric_reminder = next(
        line for line in geometric.splitlines() if r"\textbf{Rappel :}" in line
    )

    assert "si $q>0$" in arithmetic
    guarded_exponential_link = re.compile(
        r"géométrique,.*si \$q>0\$, lien avec une fonction exponentielle",
        re.IGNORECASE,
    )
    decoy_elsewhere = geometric_reminder.replace(
        "si $q>0$, lien avec une fonction exponentielle",
        "lien avec une fonction exponentielle",
    ) + " Si $q>0$, les termes sont positifs lorsque $u_0>0$."

    assert guarded_exponential_link.search(geometric_reminder)
    assert guarded_exponential_link.search(decoy_elsewhere) is None
    assert "pour $q<0$" in geometric.lower()
    assert "courbe en exponentielle, mais" not in geometric


def _load_geometric_threshold_function():
    namespace = runpy.run_path(
        str(PYTHON_SOURCES / "1SPE-SUITES-CR-016-SEUIL.py")
    )
    assert "seuil_geometrique" in namespace
    return namespace["seuil_geometrique"]


def test_geometric_threshold_contract_is_explicit_in_source_and_course() -> None:
    seuil_geometrique = _load_geometric_threshold_function()
    course = _compact(_text(COURSES / "16_C7_algorithmique.tex"))

    assert seuil_geometrique.__doc__ is not None
    assert "u0 > 0" in seuil_geometrique.__doc__
    assert "q > 1" in seuil_geometrique.__doc__
    assert "plus petit rang" in seuil_geometrique.__doc__
    assert "$u_0>0$" in course
    assert "$q>1$" in course
    assert r"\texttt{ValueError}" in course


def test_geometric_threshold_returns_the_first_strict_crossing() -> None:
    seuil_geometrique = _load_geometric_threshold_function()

    rank, value = seuil_geometrique(1, 1.05, 2)

    assert rank == 15
    assert value == pytest.approx(2.0789281794113688)
    assert value > 2
    assert value / 1.05 <= 2


def test_geometric_threshold_handles_initial_and_strict_boundaries() -> None:
    seuil_geometrique = _load_geometric_threshold_function()

    assert seuil_geometrique(3, 2, 2) == (0, 3)
    assert seuil_geometrique(1, 2, 1) == (1, 2)


@pytest.mark.parametrize(
    ("u0", "q", "threshold", "message"),
    [
        (1, 1, 2, "q doit être strictement supérieur à 1"),
        (1, 0.5, 2, "q doit être strictement supérieur à 1"),
        (0, 2, 2, "u0 doit être strictement positif"),
        (1, 2, float("inf"), "paramètres doivent être des nombres réels finis"),
    ],
)
def test_geometric_threshold_rejects_invalid_or_impossible_cases(
    u0: float, q: float, threshold: float, message: str
) -> None:
    seuil_geometrique = _load_geometric_threshold_function()

    with pytest.raises(ValueError, match=message):
        seuil_geometrique(u0, q, threshold)


def test_fil_rouge_has_exact_rounding_and_proves_the_only_two_crossings() -> None:
    source = _text(COURSES / "07_td_fil_rouge.tex")

    assert round(1000 * 1.004**24) == 1101
    assert round(1000 * 1.004**60) == 1271
    assert all(
        token in source
        for token in (
            r"1{,}1005",
            r"1\,101",
            r"1{,}2706",
            r"1\,271",
            r"B_7\approx1\,028{,}34<A_7=1\,400",
            r"B_8\approx1\,032{,}45<A_8=1\,600",
            r"B_9\approx1\,036{,}58<A_9=1\,800",
            "flux de versements différents",
            "solde",
        )
    )
    assert "Compléter et expliquer le programme" not in source
    assert "Lire et expliquer le programme" in source
    assert "plus avantageuse" not in source
    assert "plus efficace" not in source
    assert "reste nettement meilleure" not in source
    assert "cet avantage" not in source
    assert "est en tête" not in source
    assert "repris l'avantage" not in source


def test_c7_course_matches_code_and_states_honest_termination_and_costs() -> None:
    source = _text(COURSES / "16_C7_algorithmique.tex")
    compact = _compact(source)

    assert "on initialise $u$ à $u_0$ et l'accumulateur $S$ à $u_0$" in compact
    assert "vérifier que les termes évoluent dans le bon sens et que le seuil peut être atteint" in compact
    assert "la boucle peut ne jamais s'arrêter" in compact
    assert "Enrichissement non exigible" in source
    assert "ne constitue pas une affirmation de complexité" in compact
    assert "d'autres méthodes existent" in source
    assert "$O(1)$" not in source
    assert "seule l'approche itérative est directement accessible" not in source


def test_variation_method_names_term_intervals_not_difference_indices() -> None:
    source = _text(METHODS / "1SPE-SUITES-ME-005.tex")

    assert "$u_0>u_1>u_2$" in source
    assert "strictement décroissante jusqu'au rang $2$" in source
    assert "strictement croissante à partir du rang $2$" in source
    assert "décroissante pour $n \\in \\{0\\,;\\,1\\}$" not in source


def test_student_evaluations_hide_every_point_allocation_but_teacher_keeps_it() -> None:
    point_pattern = re.compile(r"\b\d+\s*(?:pt|pts|points)\b", re.IGNORECASE)

    for variant in ("A", "B"):
        path = EVALUATIONS / f"1SPE-SUITES-EV-{variant}.tex"
        source = _text(path)
        student_source = _student_rendered_source(source)

        assert point_pattern.search(student_source) is None
        assert len(point_pattern.findall(source)) >= 19
        assert source.count(r"\ifnxVersionProfesseur") == source.count(r"\fi")


def test_evaluation_metadata_and_exercise_four_capacity_labels_are_exact() -> None:
    for variant in ("A", "B"):
        student = EVALUATIONS / f"1SPE-SUITES-EV-{variant}.tex"
        correction = EVALUATIONS / f"1SPE-SUITES-EV-{variant}-corrige.tex"

        assert "representer" not in _meta(student)["competences"]
        assert "Exercice 4" in _text(student)
        assert "Capacités C2, C4" in _text(student)
        assert "(4 points) — C2, C4" in _text(correction)
        assert _meta(student)["status"] == "generated"
        assert _meta(correction)["status"] == "generated"


def test_evaluation_rounding_and_embedded_oracles_match_published_answers() -> None:
    evaluation_b = _text(EVALUATIONS / "1SPE-SUITES-EV-B.tex")
    correction_a = _text(EVALUATIONS / "1SPE-SUITES-EV-A-corrige.tex")
    correction_b = _text(EVALUATIONS / "1SPE-SUITES-EV-B-corrige.tex")

    assert all(
        token in correction_a for token in (r"1\,126", r"1\,182", r"1\,241")
    )
    assert all(
        token not in correction_a for token in (r"1\,127", r"1\,183", r"1\,242")
    )
    oracle = "assert round(float(u_place.subs(n, 2))) == 1082"
    assert oracle in evaluation_b
    assert oracle in correction_b
    assert "assert int(float(u_place.subs(n, 2))) == 1081" not in evaluation_b
    assert "assert int(float(u_place.subs(n, 2))) == 1081" not in correction_b
