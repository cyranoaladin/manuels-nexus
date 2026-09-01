r"""Le corpus ne contient plus de macro detruite par une sequence d'echappement.

Ce defaut etait deja connu : un test verifiait que `1SPE-SUITES-CO-016`
contenait `$\nearrow$` et non `$` + saut de ligne + `earrow$`. Mais l'oracle
etait attache A UN OBJET. Cinquante-deux autres fichiers portaient la meme
corruption sans qu'aucun test ne soit rouge. L'invariant est donc reecrit au
niveau de la classe, sur toute la collection.

Un detecteur qui ne trouve rien doit d'abord prouver qu'il sait trouver
quelque chose : les tests de sensibilite ci-dessous injectent la corruption
dans les trois contextes mathematiques reels du corpus.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "latex_escape_corruption", ROOT / "scripts" / "latex_escape_corruption.py"
)
detector = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(detector)


CORRUPTED_INLINE = "$g(x)$ & $-\\infty$ & $\nearrow$ & $4$ \\\\"
CORRUPTED_ARRAY = "\\[\\begin{array}{c}\nf & \nearrow & 3 \\\\\n\\end{array}\\]"
CORRUPTED_DISPLAY = "\\[\nP(A) \neq 0.\n\\]"


@pytest.mark.parametrize(
    "sample, expected",
    [
        (CORRUPTED_INLINE, "\\nearrow"),
        (CORRUPTED_ARRAY, "\\nearrow"),
        (CORRUPTED_DISPLAY, "\\neq"),
    ],
)
def test_the_detector_sees_the_corruption_in_every_math_context(sample, expected) -> None:
    findings = detector.scan(sample)
    assert findings, f"corruption non detectee dans :\n{sample}"
    assert expected in {macro for _, _, macro in findings}


def test_the_detector_reconstructs_the_original_macro() -> None:
    (_, fragment, macro), = detector.scan(CORRUPTED_INLINE)
    assert fragment == "earrow"
    assert macro == "\\nearrow"


def test_repaired_source_is_not_flagged() -> None:
    assert detector.scan("$g(x)$ & $-\\infty$ & $\\nearrow$ & $4$ \\\\") == []


def test_french_prose_outside_math_is_not_flagged() -> None:
    """« ne sont pas coplanaires » n'est pas une macro cassee."""
    prose = "et pourtant $D(0;0;1)$ n'appartient pas a leur plan $(z=0)$.\nne sont pas coplanaires."
    assert detector.scan(prose) == []


def test_an_ordinary_table_cell_is_not_flagged() -> None:
    """Une cellule commencant par « f » ou « e » reste legitime."""
    table = "\\[\\begin{array}{c}\nf & \\nearrow & 3 \\\\\ne & \\searrow & 4 \\\\\n\\end{array}\\]"
    assert detector.scan(table) == []


def test_the_whole_collection_is_free_of_escape_corruption() -> None:
    report = detector.scan_tree(ROOT)
    assert report == {}, {k: v[:3] for k, v in list(report.items())[:5]}


def test_no_tex_source_carries_a_raw_control_character() -> None:
    guilty = [
        str(p) for p in ROOT.rglob("*.tex")
        if "/build/" not in str(p) and detector.CONTROL.search(p.read_bytes())
    ]
    assert guilty == []
