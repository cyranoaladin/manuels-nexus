"""Couper du LaTeX à l'aveugle produit des attendus que personne ne peut lire.

Quarante attendus du barème portaient des délimiteurs déséquilibrés : un `\\[`
sans `\\]`, un `\\end{align*}` orphelin, une formule tranchée au milieu. La
cause n'était pas dans les corrigés : c'était une coupure à quatre cents
caractères qui ne demandait l'avis de personne.

Les cas ci-dessous sont pris dans le manuel courant, pas imaginés.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tex_units as tex  # noqa: E402


# ---------------------------------------------------------------------------
#  Les cas observés dans le manuel courant
# ---------------------------------------------------------------------------

OBSERVED_BROKEN = {
    # DERGLOBAL : un display ouvert que la coupure n'a jamais refermé.
    "display_never_closed": (
        r"Équation de la tangente : \[ T : y = f'(2)(x - 2) + 9 = 10x - 11",
        "\\[ sans \\]",
    ),
    # DERLOCAL : la coupure est tombée entre deux exercices, laissant la
    # fermeture du précédent devant l'ouverture du suivant.
    "orphan_environment_close": (
        r"\end{align*} \[ \frac{f(3+h)-f(3)}{h} = h+2 \]",
        "\\end{align*} sans \\begin",
    ),
    # SECDEG : un fragment qui commence par la fermeture du display précédent.
    "leading_display_close": (
        r"\] Vérification : $T(1) = 7 - 6 = 1 = f(1)$",
        "\\] sans \\[",
    ),
    "unclosed_inline_math": (r"On obtient $f(x) = 3x^2 - 2x", "$ non refermé"),
    "unclosed_group": (r"Le résultat est \boxed{u_n = 800 \times 1{,}05^n",
                       "{ sans }"),
}

OBSERVED_SOUND = {
    "boxed_display": r"\[ \boxed{u_n = 800 \times 1{,}05^n} \quad \text{pour tout } n \]",
    "two_inline": r"$f(0)=1$ et $f(5)=\mathrm{e}^{-2}\approx0{,}14$",
    "escaped_percent": r"Le taux vaut $5\,\%$ par an, donc $q = 1{,}05$",
    "align_environment": (
        r"\begin{align*} u_{n+1} &= u_n + 0{,}05\,u_n \\ &= 1{,}05\,u_n \end{align*}"
    ),
    "array_environment": (
        r"\[ \begin{array}{c|c} x & f(x) \\ \hline 0 & 1 \end{array} \]"
    ),
    "comment_is_not_a_percent": "Une remarque % le reste est un commentaire\n",
}


@pytest.mark.parametrize("name", sorted(OBSERVED_BROKEN))
def test_a_fragment_observed_broken_is_reported_broken(name: str) -> None:
    text, expected_fault = OBSERVED_BROKEN[name]

    faults = tex.imbalances(text)

    assert faults, name
    assert expected_fault in faults, (name, faults)
    assert not tex.is_balanced(text)


@pytest.mark.parametrize("name", sorted(OBSERVED_SOUND))
def test_a_fragment_observed_sound_is_left_alone(name: str) -> None:
    assert tex.is_balanced(OBSERVED_SOUND[name]), (name, tex.imbalances(OBSERVED_SOUND[name]))


# ---------------------------------------------------------------------------
#  La coupure
# ---------------------------------------------------------------------------

PARAGRAPH = (
    r"La relation $u_{n+1} = 1{,}05\,u_n$ montre que la suite est géométrique. "
    r"Par la formule du terme général : "
    r"\[ \boxed{u_n = 800 \times 1{,}05^n} \quad \text{pour tout } n \in \mathbb{N}. \] "
    r"On en déduit $u_1 = 840$ €."
)


@pytest.mark.parametrize("limit", list(range(20, len(PARAGRAPH) + 40, 7)))
def test_no_truncation_ever_breaks_a_tex_unit(limit: int) -> None:
    """La propriété qui compte : quelle que soit la limite, ça tient debout."""

    cut = tex.truncate(PARAGRAPH, limit)

    assert tex.is_balanced(cut), (limit, cut)
    assert len(cut) <= max(limit, 0)
    assert PARAGRAPH.startswith(cut.rstrip())


def test_a_limit_that_falls_inside_a_display_stops_before_it() -> None:
    """Plutôt s'arrêter avant la formule que la couper en deux."""

    inside = PARAGRAPH.index(r"\boxed") + 10
    cut = tex.truncate(PARAGRAPH, inside)

    assert r"\[" not in cut
    assert tex.is_balanced(cut)


def test_a_text_that_fits_is_returned_whole() -> None:
    assert tex.truncate(PARAGRAPH, len(PARAGRAPH) + 100) == PARAGRAPH


def test_a_text_with_no_safe_boundary_yields_nothing() -> None:
    """Mieux vaut ne rien montrer qu'une formule tranchée."""

    assert tex.truncate(r"\[ x = \frac{1}{2} \]", 8) == ""


# ---------------------------------------------------------------------------
#  Le découpage en phrases
# ---------------------------------------------------------------------------


def test_a_full_stop_inside_a_formula_does_not_end_a_sentence() -> None:
    """C'est ce point-là qui fabriquait les attendus commençant par `\\end`."""

    parts = tex.sentences(PARAGRAPH)

    assert len(parts) == 2
    assert all(tex.is_balanced(part) for part in parts)
    assert parts[1].startswith("Par la formule")
    assert r"\]" in parts[1]


def test_every_sentence_of_a_real_correction_stands_on_its_own() -> None:
    text = (
        r"$f'(x)=-0{,}4\mathrm{e}^{-0{,}4x}<0$, donc $f$ est décroissante. "
        r"$f(0)=1$ et $f(5)=\mathrm{e}^{-2}\approx0{,}14$."
    )

    parts = tex.sentences(text)

    assert len(parts) == 2
    for part in parts:
        assert tex.is_balanced(part), part


def test_a_semicolon_outside_mathematics_separates_sentences() -> None:
    parts = tex.sentences("D'abord $a = 1$ ; ensuite $b = 2$.")

    assert len(parts) == 2
