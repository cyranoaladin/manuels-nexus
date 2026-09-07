"""Aménager change le chemin, jamais la cible.

La faute que ces tests cherchent porte un nom : baisser l'exigence en croyant
aménager. Un exercice dont on retire la capacité visée n'est pas aménagé, il
est vide — et il passerait pour du contenu dans tous les compteurs.

Ils cherchent aussi la faute inverse, que j'ai commise en écrivant ce
producteur : déclarer qu'un objet a « bougé la cible » parce qu'il nomme sa
capacité par son code local alors que sa source la nomme par sa référence
officielle. Comparer sans résoudre fabrique des défauts qui n'existent pas.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import amenagement_profiles as profiles  # noqa: E402
import build_amenagement_derivation_graph as graph  # noqa: E402

ARTIFACT = ROOT / "audit/AMENAGEMENT_DERIVATION_GRAPH.json"


@pytest.fixture(scope="module")
def payload():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_no_derivation_defect(payload) -> None:
    assert payload["summary"]["DERIVATION_DEFECTS"] == 0


def test_every_amenaged_object_names_an_existing_source(payload) -> None:
    for row in payload["records"]:
        assert row["CANONICAL_OBJECT"], row["object_id"]
        assert row["canonical_resolved"] == row["CANONICAL_OBJECT"], row["object_id"]


def test_the_target_is_preserved(payload) -> None:
    """Les capacités travaillées sont incluses dans celles de la source."""
    for row in payload["records"]:
        own = set(row["capacity_codes"])
        source = set(row["source_capacity_codes"])
        assert own & source, row["object_id"]
        assert own <= source, row["object_id"]


def test_a_local_code_is_resolved_before_comparison() -> None:
    """Le défaut que j'avais introduit : comparer `C1` et `P-BASE-01`."""
    alias = {"C1": "P-BASE-01", "C2": "P-BASE-02"}
    meta = {"capacites_codes": ["C1"], "capacites": ["P-BASE-01"]}
    assert graph._capacity_codes(meta, alias) == {"P-BASE-01"}
    source = {"capacites": ["P-BASE-01"]}
    assert graph._capacity_codes(meta, alias) <= graph._capacity_codes(source, alias)


def test_a_declared_profile_must_leave_a_trace() -> None:
    """Une étiquette n'est pas un aménagement."""
    nothing = "Texte ordinaire sans aucun aménagement."
    assert profiles.observed_profiles(nothing) == set()

    sequenced = r"\textbf{Étape 1.} Fais ceci."
    assert "SEQUENCAGE" in profiles.observed_profiles(sequenced)


def test_a_complete_code_block_is_not_a_starter() -> None:
    """`\\begin{python}` seul ne prouve aucune amorce : c'est un énoncé."""
    complete = "\\begin{python}\nx = 1 + 1\n\\end{python}"
    assert "AMORCE_FOURNIE" not in profiles.observed_profiles(complete)

    started = "\\begin{python}\nx = 1 + ______\n\\end{python}"
    assert "AMORCE_FOURNIE" in profiles.observed_profiles(started)


def test_a_model_row_counts_as_a_starter() -> None:
    """Une première ligne remplie amorce autant qu'un début de code."""
    table = (
        "\\begin{tabular}{|c|c|}\n"
        "\\hline\n"
        "\\textbf{Nombre} & \\textbf{Reste} \\\\\n"
        "\\hline\n"
        "$156$ & $0$ \\\\\n"
        "\\hline\n"
        "$78$ & \\dotfill \\\\\n"
        "\\hline\n"
        "\\end{tabular}"
    )
    assert "AMORCE_FOURNIE" in profiles.observed_profiles(table)

    empty = table.replace("$156$ & $0$", "$156$ & \\dotfill")
    assert "AMORCE_FOURNIE" not in profiles.observed_profiles(empty)


def test_fragile_tabular_markup_is_detected() -> None:
    """`\\lstinline{...}` collé à un `&` casse la compilation du livret."""
    assert profiles.FRAGILE_IN_TABULAR.search(r"\lstinline{x} & y")
    assert not profiles.FRAGILE_IN_TABULAR.search(r"\texttt{x} & y")


def test_the_graph_declares_its_freshness(payload) -> None:
    import evidence_freshness as freshness

    assert freshness.assess(payload["freshness"])["FRESHNESS_STATUS"] == \
        freshness.CURRENT
