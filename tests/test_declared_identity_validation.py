"""Un détecteur qui ne trouve jamais rien ne prouve rien.

Mille neuf cent cinquante cellules reposaient sur une identité DÉCLARÉE. Le
producteur les valide toutes ; ces tests exigent qu'il sache aussi les
réfuter — un corps recopié d'une capacité à l'autre, une variante numérique,
une capacité hors contrat, un objet absent.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_declared_identity_validation as identite  # noqa: E402

ARTEFACT = ROOT / "audit/DECLARED_IDENTITY_VALIDATION.json"


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(ARTEFACT.read_text(encoding="utf-8"))


def _couverture(cellules: list[dict]) -> dict:
    return {"rows": cellules}


def _cellule(**champs) -> dict:
    base = {
        "canonical_capacity_uid": "M::CH::C1",
        "manual": "M",
        "chapter": "CH",
        "capacity": "C1",
        "role": "cours",
        "state": identite.DECLARED_STATE,
        "valid_object_ids": ["OBJ-1"],
        "valid_object_paths": ["chemin/obj1.tex"],
    }
    base.update(champs)
    return base


# ══════════════════════════════════════════════════════════════════════════
# L'état courant
# ══════════════════════════════════════════════════════════════════════════
def test_every_declared_cell_gets_exactly_one_verdict(payload: dict) -> None:
    resume = payload["summary"]
    assert resume["VERDICTS_SUM_EQUALS_TOTAL"] is True
    assert resume["DECLARED_IDENTITY_UNVALIDATED"] == 0
    assert (
        resume["PROVEN_EXACT_SEMANTIC_IDENTITIES"]
        + resume["SEMANTIC_DELTA_VARIANTS"]
        + resume["INVALID_IDENTITY_DECLARATIONS"]
        == resume["DECLARED_IDENTITY_CELLS"]
    )
    assert {ligne["VERDICT"] for ligne in payload["cells"]} <= {
        identite.PROVEN, identite.DELTA, identite.INVALID,
    }


def test_validation_never_claims_pedagogical_adequacy(payload: dict) -> None:
    """§12 : validé par la preuve, jamais approuvé."""
    assert payload["summary"]["PEDAGOGICAL_ADEQUACY_STILL_HUMAN"] is True
    assert payload["summary"]["APPROVES_NOTHING"] is True
    assert "jamais `approved`" in payload["authority_note"]


def test_the_six_semantic_components_are_declared(payload: dict) -> None:
    assert payload["semantic_components"] == [
        "statement", "numbers", "formulas", "code", "figures", "subquestions",
    ]


# ══════════════════════════════════════════════════════════════════════════
# Le condensé sémantique distingue ce qu'il doit distinguer
# ══════════════════════════════════════════════════════════════════════════
def test_the_digest_separates_bodies_that_differ_in_any_component() -> None:
    base = r"""% META: {"id": "X"}
Calculer $2x+1$ pour $x=3$.
\begin{enumerate}
  \item Première étape.
  \item Seconde étape.
\end{enumerate}
"""
    reference = identite.semantic_digest(base)
    assert identite.semantic_digest(base.replace("x=3", "x=4")) != reference
    assert identite.semantic_digest(base.replace("2x+1", "2x-1")) != reference
    assert identite.semantic_digest(base.replace("Première", "Troisième")) != reference
    assert identite.semantic_digest(base.replace("  \\item Seconde étape.\n", "")) != reference
    assert identite.semantic_digest(base + "\\includegraphics{f.png}\n") != reference
    assert identite.semantic_digest(
        base + "\\begin{python}\nprint(1)\n\\end{python}\n"
    ) != reference


def test_the_numeric_skeleton_ignores_numbers_but_nothing_else() -> None:
    gauche = "Calculer $2x+1$ pour $x=3$."
    droite = "Calculer $5x+7$ pour $x=9$."
    autre = "Factoriser $2x+1$ pour $x=3$."
    assert identite.numeric_skeleton_digest(gauche) == identite.numeric_skeleton_digest(droite)
    assert identite.semantic_digest(gauche) != identite.semantic_digest(droite)
    assert identite.numeric_skeleton_digest(gauche) != identite.numeric_skeleton_digest(autre)


# ══════════════════════════════════════════════════════════════════════════
# Les réfutations : le détecteur doit savoir dire non
# ══════════════════════════════════════════════════════════════════════════
def test_a_body_copied_across_two_capacities_is_refused(tmp_path, monkeypatch) -> None:
    """La signature du P0 fondateur : deux objets, un seul corps."""
    corps = "% META: {\"id\": \"OBJ-A\"}\nUn énoncé qui sert de corps partagé.\n"
    premier = tmp_path / "a.tex"
    second = tmp_path / "b.tex"
    premier.write_text(corps, encoding="utf-8")
    second.write_text(corps.replace("OBJ-A", "OBJ-B"), encoding="utf-8")
    monkeypatch.setattr(identite, "ROOT", tmp_path)
    resultat = identite.build(_couverture([
        _cellule(capacity="C1", valid_object_ids=["OBJ-A"],
                 valid_object_paths=["a.tex"]),
        _cellule(canonical_capacity_uid="M::CH::C2", capacity="C2",
                 valid_object_ids=["OBJ-B"], valid_object_paths=["b.tex"]),
    ]))
    assert resultat["summary"]["INVALID_IDENTITY_DECLARATIONS"] == 2
    assert resultat["summary"]["PROVEN_EXACT_SEMANTIC_IDENTITIES"] == 0
    for ligne in resultat["cells"]:
        assert any("corps sémantique identique" in m for m in ligne["contradictions"])


def test_one_object_declaring_several_capacities_is_not_a_defect(
    tmp_path, monkeypatch,
) -> None:
    """Une évaluation qui porte sur trois capacités les sert vraiment."""
    corps = "% META: {\"id\": \"EVAL-A\"}\nUn devoir couvrant plusieurs capacités.\n"
    (tmp_path / "eval.tex").write_text(corps, encoding="utf-8")
    monkeypatch.setattr(identite, "ROOT", tmp_path)
    resultat = identite.build(_couverture([
        _cellule(capacity=code, canonical_capacity_uid=f"M::CH::{code}",
                 valid_object_ids=["EVAL-A"], valid_object_paths=["eval.tex"])
        for code in ("C1", "C2", "C3")
    ]))
    assert resultat["summary"]["INVALID_IDENTITY_DECLARATIONS"] == 0
    assert resultat["summary"]["PROVEN_EXACT_SEMANTIC_IDENTITIES"] == 3


def test_two_numeric_variants_of_one_cell_are_a_delta(tmp_path, monkeypatch) -> None:
    (tmp_path / "v1.tex").write_text(
        "% META: {\"id\": \"V1\"}\nCalculer $2x+1$ pour $x=3$.\n", encoding="utf-8"
    )
    (tmp_path / "v2.tex").write_text(
        "% META: {\"id\": \"V2\"}\nCalculer $5x+7$ pour $x=9$.\n", encoding="utf-8"
    )
    monkeypatch.setattr(identite, "ROOT", tmp_path)
    resultat = identite.build(_couverture([
        _cellule(valid_object_ids=["V1", "V2"],
                 valid_object_paths=["v1.tex", "v2.tex"]),
    ]))
    assert resultat["summary"]["SEMANTIC_DELTA_VARIANTS"] == 1
    assert resultat["cells"][0]["VERDICT"] == identite.DELTA


def test_a_missing_crediting_object_is_refused(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(identite, "ROOT", tmp_path)
    resultat = identite.build(_couverture([
        _cellule(valid_object_paths=["absent.tex"]),
    ]))
    assert resultat["summary"]["INVALID_IDENTITY_DECLARATIONS"] == 1
    assert any(
        "absent du disque" in motif
        for motif in resultat["cells"][0]["contradictions"]
    )


def test_a_capacity_outside_the_contract_is_refused(tmp_path, monkeypatch) -> None:
    (tmp_path / "obj.tex").write_text(
        "% META: {\"id\": \"OBJ\"}\nUn énoncé quelconque mais bien réel.\n",
        encoding="utf-8",
    )
    contrat = tmp_path / "NSI/chapitres/CH"
    contrat.mkdir(parents=True)
    (contrat / "contrat.yaml").write_text(
        "capacites:\n  - code: C1\n  - code: C2\n", encoding="utf-8"
    )
    monkeypatch.setattr(identite, "ROOT", tmp_path)
    # La cellule déclare C9, que le contrat du chapitre ne porte pas.
    cellule = _cellule(capacity="C9", canonical_capacity_uid="M::CH::C9",
                       valid_object_paths=["obj.tex"])
    resultat = identite.build(_couverture([cellule]))
    assert resultat["summary"]["INVALID_IDENTITY_DECLARATIONS"] == 1
    assert any(
        "absente du contrat" in motif
        for motif in resultat["cells"][0]["contradictions"]
    )
