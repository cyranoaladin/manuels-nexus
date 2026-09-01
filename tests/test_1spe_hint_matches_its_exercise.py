"""Un coup de pouce doit aider POUR l'exercice auquel il est attache.

Dix-huit exercices de 1SPE-DERIVATION-GLOBAL partageaient un seul et meme
coup de pouce : « Identifie la structure de l'expression (reference, somme,
produit ou quotient) puis applique la formule correspondante. »

Il est juste pour C1 -- deriver une fonction de reference. Il ne l'est plus
du tout pour C3, C4 et C5, ou l'eleve ne cherche pas a deriver mais a lire le
SIGNE de la derivee, a en deduire un tableau de variations, un extremum, ou a
resoudre un probleme d'optimisation. Un indice qui parle d'autre chose que de
la question posee n'aide pas : il egare.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL"


def _hint_text(path: Path) -> str:
    body = path.read_text(encoding="utf-8").split("\n", 1)[1]
    match = re.search(r"\\coupDePouce\{\d+\}\{(.*)\}", body, re.DOTALL)
    assert match, path.name
    return match.group(1).strip()


def _capacity_of_exercise(hint_path: Path) -> str:
    exercise = hint_path.with_name(hint_path.name.replace("-CDP.tex", ".tex"))
    meta = json.loads(
        exercise.read_text(encoding="utf-8").split("META:", 1)[1].split("\n", 1)[0]
    )
    codes = meta.get("capacites_codes") or meta.get("capacites") or []
    assert len(codes) == 1, exercise.name
    return str(codes[0])


def test_a_single_hint_never_spans_unrelated_capacities() -> None:
    """Le meme indice ne peut pas servir des capacites qui ne demandent pas
    le meme geste. C1/C2 derivent ; C3/C4/C5 exploitent une derivee deja
    calculee."""
    by_hint: dict[str, set[str]] = defaultdict(set)
    for hint in sorted((CHAPTER / "exercices").glob("*-CDP.tex")):
        by_hint[hashlib.sha256(_hint_text(hint).encode()).hexdigest()].add(
            _capacity_of_exercise(hint)
        )

    derivation = {"C1", "C2"}
    exploitation = {"C3", "C4", "C5"}
    straddling = {
        digest[:12]: sorted(caps)
        for digest, caps in by_hint.items()
        if caps & derivation and caps & exploitation
    }
    assert straddling == {}, (
        f"indice partage entre calcul de derivee et exploitation : {straddling}"
    )


def test_every_variation_or_extremum_hint_speaks_of_the_derivative_sign() -> None:
    """Pour C3, C4 et C5, l'indice doit orienter vers le geste reel."""
    expected = {
        "C3": ("signe", "variation"),
        "C4": ("annul", "extremum"),
        "C5": ("optimis", "derivée"),
    }
    for hint in sorted((CHAPTER / "exercices").glob("*-CDP.tex")):
        capacity = _capacity_of_exercise(hint)
        if capacity not in expected:
            continue
        text = _hint_text(hint).lower()
        assert any(token in text for token in expected[capacity]), (
            f"{hint.name} ({capacity}) : indice sans rapport avec la question"
        )
