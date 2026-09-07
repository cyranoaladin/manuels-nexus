"""Le graphe de clôture ne doit jamais faire hériter une preuve non due.

Le risque de ce graphe est le contraire de son objectif : en cherchant à
réduire 2 537 revues, fabriquer une inférence qui déclare relu ce que personne
n'a lu. Chaque test ci-dessous essaie d'obtenir cette inférence.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_semantic_review_closure_graph as graph  # noqa: E402

ARTIFACT = ROOT / "audit/SEMANTIC_REVIEW_CLOSURE_GRAPH.json"


@pytest.fixture(scope="module")
def payload():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_every_queue_item_appears_exactly_once(payload) -> None:
    queue = json.loads(
        (ROOT / "audit/HUMAN_REVIEW_QUEUE.json").read_text(encoding="utf-8")
    )
    expected = {u for item in queue["items"] for u in item["unit_ids"]}
    seen = [row["REVIEW_ITEM_ID"] for row in payload["records"]]
    assert len(seen) == len(set(seen))
    assert set(seen) == expected
    assert payload["summary"]["RAW_REVIEW_ITEMS"] == len(expected)


def test_no_item_inherits_without_a_proven_equality(payload) -> None:
    assert payload["summary"]["UNJUSTIFIED_REVIEW_EVIDENCE_INHERITANCE"] == 0
    assert payload["unjustified_inheritance"] == []


def test_an_inheriting_item_really_has_the_same_body(payload) -> None:
    by_id = {row["REVIEW_ITEM_ID"]: row for row in payload["records"]}
    inheriting = [r for r in payload["records"] if r["INHERITS_REVIEW_EVIDENCE_FOR"]]
    assert inheriting, "aucun héritage : le test ne prouverait rien"
    for row in inheriting:
        source = by_id[row["CANONICAL_SEMANTIC_SOURCE"]]
        assert source["canonical_body_digest"] == row["canonical_body_digest"]
        # et l'égalité tient sur les fichiers réels, pas sur l'artefact
        left = graph.canonical_body(ROOT / row["path"]) \
            if row["category"] == "OBJECT_REVIEW" else None
        right = graph.canonical_body(ROOT / source["path"]) \
            if source["category"] == "OBJECT_REVIEW" else None
        if left is not None and right is not None:
            assert left == right


def test_a_numeric_delta_inherits_nothing(payload) -> None:
    """Un coefficient différent peut faire d'un énoncé vrai un énoncé faux."""
    deltas = [r for r in payload["records"] if r["DERIVATION"] == "NUMERIC_DELTA"]
    assert deltas, "aucun delta : le test ne prouverait rien"
    for row in deltas:
        assert row["INHERITS_REVIEW_EVIDENCE_FOR"] == []


def test_adequacy_is_never_inherited(payload) -> None:
    """Deux textes identiques restent attachés à deux parents différents."""
    for row in payload["records"]:
        assert "ADEQUATION_A_L_OBJET_PARENT" in row["REQUIRES_OWN_REVIEW_FOR"]
        assert "ADEQUATION_A_L_OBJET_PARENT" not in row["INHERITS_REVIEW_EVIDENCE_FOR"]
    assert payload["summary"]["PER_ITEM_ADEQUACY_CHECKS_STILL_REQUIRED"] == \
        payload["summary"]["RAW_REVIEW_ITEMS"]


def test_the_reduction_is_not_overstated(payload) -> None:
    s = payload["summary"]
    assert s["INDEPENDENT_REVIEW_UNITS_REQUIRED"] == \
        s["RAW_REVIEW_ITEMS"] - s["EXACT_DERIVED_DUPLICATES"]
    assert s["INDEPENDENT_REVIEW_UNITS_REQUIRED"] <= s["RAW_REVIEW_ITEMS"]
    assert s["CANONICAL_SEMANTIC_UNITS"] <= s["RAW_REVIEW_ITEMS"]


def test_a_forged_inheritance_is_detected() -> None:
    """Déclarer un héritage sans égalité de corps doit être compté."""
    forged = [
        {
            "REVIEW_ITEM_ID": "A",
            "canonical_body_digest": "sha256:aaa",
            "CANONICAL_SEMANTIC_SOURCE": "A",
            "DERIVATION": "CANONICAL",
            "DERIVATION_PROOF": {"is_source": True},
            "INHERITS_REVIEW_EVIDENCE_FOR": [],
        },
        {
            "REVIEW_ITEM_ID": "B",
            "canonical_body_digest": "sha256:bbb",
            "CANONICAL_SEMANTIC_SOURCE": "A",
            "DERIVATION": "EXACT_COPY",
            "DERIVATION_PROOF": {"bodies_are_equal": True},
            "INHERITS_REVIEW_EVIDENCE_FOR": list(graph.INHERITABLE),
        },
    ]
    assert graph.unjustified_inheritance(forged) == ["B"]


def test_an_inheritance_from_a_missing_source_is_detected() -> None:
    forged = [
        {
            "REVIEW_ITEM_ID": "B",
            "canonical_body_digest": "sha256:bbb",
            "CANONICAL_SEMANTIC_SOURCE": "ABSENT",
            "DERIVATION": "EXACT_COPY",
            "DERIVATION_PROOF": {"bodies_are_equal": True},
            "INHERITS_REVIEW_EVIDENCE_FOR": list(graph.INHERITABLE),
        },
    ]
    assert graph.unjustified_inheritance(forged) == ["B"]


def test_the_meta_line_never_hides_a_difference(tmp_path: Path) -> None:
    """Retirer META ne doit pas faire fusionner deux corps différents."""
    a = tmp_path / "a.tex"
    b = tmp_path / "b.tex"
    a.write_text('% META: {"id":"X"}\n\\coupDePouce{1}{Un}\n', encoding="utf-8")
    b.write_text('% META: {"id":"Y"}\n\\coupDePouce{1}{Deux}\n', encoding="utf-8")
    assert graph.canonical_body(a) != graph.canonical_body(b)

    c = tmp_path / "c.tex"
    c.write_text('% META: {"id":"Z"}\n\\coupDePouce{1}{Un}\n', encoding="utf-8")
    assert graph.canonical_body(a) == graph.canonical_body(c)


def test_the_numeric_skeleton_does_not_erase_a_whole_statement() -> None:
    """Abstraire les nombres ne doit pas rendre deux énoncés interchangeables."""
    assert graph.numeric_skeleton("Résous 2x + 3 = 0") == \
        graph.numeric_skeleton("Résous 5x + 7 = 0")
    assert graph.numeric_skeleton("Résous 2x + 3 = 0") != \
        graph.numeric_skeleton("Dérive 2x + 3")


def test_the_graph_declares_its_freshness(payload) -> None:
    import evidence_freshness as freshness

    assessment = freshness.assess(payload["freshness"])
    assert assessment["FRESHNESS_STATUS"] == freshness.CURRENT


def test_the_identity_argument_never_hides_a_copy(tmp_path: Path) -> None:
    """Le corps porte l'identite une seconde fois, dans l'environnement.

    Retirer la ligne META ne suffit pas : `\\begin{exercice}{<id>}` nomme
    l'objet a nouveau. Tant qu'elle y restait, deux copies exactes logees dans
    deux chapitres differents comptaient pour deux unites semantiques
    distinctes, et la reduction annoncait un corpus plus riche qu'il n'est.
    """

    a = tmp_path / "a.tex"
    b = tmp_path / "b.tex"
    enonce = "Etudier les variations de $f(x) = x^3 - 3x^2 + 2$."
    a.write_text(
        '% META: {"id":"TEXP-ARI-EX-010"}\n'
        "\\begin{exercice}{TEXP-ARI-EX-010}{1}{12}\n" + enonce + "\n"
        "\\end{exercice}\n",
        encoding="utf-8",
    )
    b.write_text(
        '% META: {"id":"TCOMPL-AIR-EX-010"}\n'
        "\\begin{exercice}{TCOMPL-AIR-EX-010}{1}{12}\n" + enonce + "\n"
        "\\end{exercice}\n",
        encoding="utf-8",
    )
    assert graph.canonical_body(a) == graph.canonical_body(b)

    # Et la neutralisation ne fabrique pas d'egalite : deux enonces
    # differents restent differents.
    c = tmp_path / "c.tex"
    c.write_text(
        '% META: {"id":"TCOMPL-AIR-EX-011"}\n'
        "\\begin{exercice}{TCOMPL-AIR-EX-011}{1}{12}\n"
        "Etudier les variations de $f(x) = x^3 - 3x^2 + 5$.\n"
        "\\end{exercice}\n",
        encoding="utf-8",
    )
    assert graph.canonical_body(a) != graph.canonical_body(c)
