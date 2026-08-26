from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "Mathematiques" / "manuel-maths" / "chapitres" / "1SPE-SUITES"


def _path(kind: str, number: str) -> Path:
    directory = "exercices" if kind == "EX" else "corriges"
    return CHAPTER / directory / f"1SPE-SUITES-{kind}-{number}.tex"


def _text(kind: str, number: str) -> str:
    return _path(kind, number).read_text(encoding="utf-8")


def _cdp_text(number: str) -> str:
    return (
        CHAPTER
        / "exercices"
        / f"1SPE-SUITES-EX-{number}-CDP.tex"
    ).read_text(encoding="utf-8")


def _rendered(source: str) -> str:
    rendered: list[str] = []
    for line in source.splitlines():
        for index, character in enumerate(line):
            if character != "%":
                continue
            backslashes = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                line = line[:index]
                break
        rendered.append(line)
    return "\n".join(rendered)


def _meta(kind: str, number: str) -> dict:
    first_line = _text(kind, number).splitlines()[0]
    assert first_line.startswith("% META: ")
    return json.loads(first_line.removeprefix("% META: "))


def _compact(source: str) -> str:
    return " ".join(source.split())


@dataclass(frozen=True)
class PedagogicalSignature:
    mathematical_family: str
    surface_context: str
    generic_moves: frozenset[str]
    differentiating_moves: frozenset[str]


def _pedagogical_signature(source: str) -> PedagogicalSignature:
    rendered = _rendered(source)
    lower = rendered.lower()

    if r"\%" in rendered and any(
        marker in lower
        for marker in ("croît", "rémunéré", "augmentation", "augmente")
    ):
        family = "percentage_growth"
    elif re.search(r"[uv]_n\s*=.*\^\{?n\}?", rendered):
        family = "explicit_geometric"
    else:
        family = "other"

    if any(marker in lower for marker in ("bactérie", "colonie")):
        context = "biology"
    elif any(marker in lower for marker in ("livret", "capital", "euros")):
        context = "finance"
    else:
        context = "abstract"

    generic_markers = {
        "calculate_terms": ("calculer $u_0$", "calculer $n_1$", "calculer $p_3$"),
        "identify_geometric": ("arithmétique ou géométrique", "est géométrique"),
        "derive_recurrence": ("_{n+1}$ en fonction de", "_{n+1} ="),
        "derive_explicit": ("en fonction de $n$",),
        "identify_coefficient": ("coefficient multiplicateur",),
    }
    generic = frozenset(
        move
        for move, markers in generic_markers.items()
        if any(marker in lower for marker in markers)
    )

    differentiating_markers = {
        "error_analysis": ("réfuter", "ne convient pas"),
        "inverse_rank": ("rang", "$u_n=192$", "$u_n = 192$"),
        "compare_models": ("modèle additif", "comparer les deux", "comparaison"),
        "interpret_model": ("valeurs décimales", "nombre entier", "arrondir à l'unité"),
    }
    differentiating = frozenset(
        move
        for move, markers in differentiating_markers.items()
        if any(marker in lower for marker in markers)
    )
    return PedagogicalSignature(family, context, generic, differentiating)


def _is_accidental_near_duplicate(left: str, right: str) -> bool:
    """Detect a shared template, without treating a repeated capacity as a clone."""

    left_signature = _pedagogical_signature(left)
    right_signature = _pedagogical_signature(right)
    shared_generic_moves = (
        left_signature.generic_moves & right_signature.generic_moves
    )
    differentiating_moves = (
        left_signature.differentiating_moves
        | right_signature.differentiating_moves
    )
    cognitive_diversity = len(differentiating_moves) >= 2
    return (
        left_signature.mathematical_family == right_signature.mathematical_family
        and len(shared_generic_moves) >= 2
        and not cognitive_diversity
    )


def test_contextual_detector_catches_templates_but_allows_justified_repetition() -> None:
    abstract_template = r"""
    On considère la suite $(u_n)$ définie par $u_n=4\times(3/2)^n$.
    Calculer $u_0$, puis montrer qu'elle est géométrique.
    Exprimer $u_{n+1}$ en fonction de $u_n$.
    """
    abstract_clone = abstract_template.replace("4", "6").replace("3/2", "2")
    contextualized_repeat = abstract_clone + (
        " Lina affirme qu'elle est arithmétique : réfuter son affirmation, "
        "puis déterminer le rang tel que $u_n=192$."
    )
    narration_only = abstract_clone + (
        " Lina affirme qu'elle est arithmétique. Calculer les termes demandés."
    )

    finance_template = r"""
    Un capital augmente de $5\,\%$. Quel est le coefficient multiplicateur ?
    Exprimer $P_{n+1}$ en fonction de $P_n$, puis $P_n$ en fonction de $n$.
    La suite est-elle arithmétique ou géométrique ? Calculer $P_3$.
    """
    biology_surface_clone = r"""
    Une colonie croît de $2\,\%$. Quel est le coefficient multiplicateur ?
    Exprimer $N_{n+1}$ en fonction de $N_n$, puis $N_n$ en fonction de $n$.
    La suite est-elle arithmétique ou géométrique ? Calculer $N_1$.
    """
    contextual_narration_only = biology_surface_clone + (
        " Lina affirme que ce modèle convient."
    )

    assert _is_accidental_near_duplicate(abstract_template, abstract_clone)
    assert _is_accidental_near_duplicate(abstract_template, narration_only)
    assert not _is_accidental_near_duplicate(
        abstract_template, contextualized_repeat
    )
    assert _is_accidental_near_duplicate(finance_template, biology_surface_clone)
    assert _is_accidental_near_duplicate(
        finance_template, contextual_narration_only
    )


def test_001_and_009_now_have_distinct_cognitive_contracts() -> None:
    exercise_001 = _text("EX", "001")
    exercise_009 = _text("EX", "009")
    correction_009 = _text("CO", "009")
    compact_exercise_009 = _compact(exercise_009)

    assert not _is_accidental_near_duplicate(exercise_001, exercise_009)
    assert "Lina affirme" in exercise_009
    assert "suite arithmétique de raison $6$" in compact_exercise_009
    assert "Réfuter cette affirmation" in exercise_009
    assert "Déterminer le rang $n$ pour lequel $u_n=192$" in exercise_009
    assert all(
        token in correction_009
        for token in (r"u_2-u_1=24-12=12", r"u_1-u_0=12-6=6")
    )
    assert "les différences ne sont pas constantes" in correction_009
    assert r"2^n=32=2^5" in correction_009
    assert "le rang cherché est $n=5$" in correction_009
    assert r"u_{n+1} = 2 \times u_n" not in _rendered(correction_009)


def test_018_and_019_are_distinct_models_not_a_context_swap() -> None:
    exercise_018 = _text("EX", "018")
    exercise_019 = _text("EX", "019")
    correction_019 = _text("CO", "019")
    compact_exercise_019 = _compact(exercise_019)
    compact_correction_019 = _compact(correction_019)

    assert not _is_accidental_near_duplicate(exercise_018, exercise_019)
    assert r"N_{n+1}=1{,}02N_n" in exercise_019
    assert r"A_n=1200+24n" in exercise_019
    assert "modèle additif" in exercise_019
    assert "Comparer les deux modèles" in compact_exercise_019
    assert "valeurs décimales" in exercise_019
    assert "arrondies à l'unité" in exercise_019
    assert all(
        token in compact_correction_019
        for token in (
            r"N_1=A_1=1224",
            r"N_2=1248{,}48",
            r"A_2=1248",
            r"N_{10}=1200\times(1{,}02)^{10}\approx1462{,}79",
            r"A_{10}=1200+24\times10=1440",
            r"22{,}79",
            "environ $1248$ bactéries",
            "environ $1463$ bactéries",
        )
    )
    assert "une valeur théorique fournie par le modèle" in compact_correction_019.lower()


def test_richness_changes_preserve_object_identity_and_true_capacities() -> None:
    expected = {
        "001": ["C3"],
        "009": ["C3"],
        "018": ["C3", "C6"],
        "019": ["C3", "C6"],
    }
    for number, capacities in expected.items():
        for kind in ("EX", "CO"):
            metadata = _meta(kind, number)
            assert metadata["id"] == f"1SPE-SUITES-{kind}-{number}"
            assert metadata["capacites_codes"] == capacities
            assert metadata["status"] == "generated"

    assert _meta("EX", "009")["competences"] == ["calculer", "raisonner"]
    exercise_019_parameters = _meta("EX", "019")["parametres_sympy"]
    assert exercise_019_parameters["taux_horaire"] == 0.02
    assert "taux_annuel" not in exercise_019_parameters


def test_changed_sources_keep_the_existing_help_contracts_true() -> None:
    cdp_009_source = _cdp_text("009")
    cdp_019_source = _cdp_text("019")
    cdp_009 = _rendered(cdp_009_source)
    cdp_019 = _rendered(cdp_019_source)

    cdp_009_meta = json.loads(
        cdp_009_source.splitlines()[0].removeprefix("% META: ")
    )
    cdp_019_meta = json.loads(
        cdp_019_source.splitlines()[0].removeprefix("% META: ")
    )
    assert cdp_009_meta == {
        "id": "1SPE-SUITES-EX-009-CDP",
        "chapitre": "1SPE-SUITES",
        "type_objet": "coup_de_pouce",
        "exercice_id": "1SPE-SUITES-EX-009",
        "status": "generated",
    }
    assert cdp_019_meta == {
        "id": "1SPE-SUITES-EX-019-CDP",
        "chapitre": "1SPE-SUITES",
        "type_objet": "coup_de_pouce",
        "exercice_id": "1SPE-SUITES-EX-019",
        "status": "generated",
    }
    assert r"u_n = 6 \times 2^n" in cdp_009
    assert r"\dfrac{u_{n+1}}{u_n}" in cdp_009
    assert r"2\,\%$ par heure" in cdp_019
    assert r"1{,}02" in cdp_019
