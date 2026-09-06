"""Une capacite declaree en META ne vaut jamais preuve de couverture.

C'est ainsi que des copies synthetiques ont fabrique de la couverture : elles
heritaient d'un identifiant de capacite sans porter la notion. Le gate exige
donc la chaine entiere, jusqu'a la page imprimee.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CHAIN_JSON = ROOT / "audit/COVERAGE_CHAIN.json"


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def chain():
    assert CHAIN_JSON.is_file()
    return json.loads(CHAIN_JSON.read_text(encoding="utf-8"))


def test_the_chain_declares_every_link(chain):
    assert chain["chain"] == [
        "official_atom", "canonical_mapping", "printed_object",
        "actual_relevant_content", "page/variant",
    ]


def test_a_proven_atom_names_its_object_and_page(chain):
    for result in chain["results"]:
        if result["chain"] != "PROVEN":
            continue
        assert result["source"], result["atom_id"]
        assert (ROOT / result["source"]).is_file(), result["source"]
        assert result["printed_page"] >= 1
        assert result["variant"] == "professeur"


def test_totals_match_the_result_list(chain):
    summary = chain["summary"]
    assert summary["ATOMS"] == len(chain["results"])
    for state, key in (
        ("PROVEN", "CHAIN_PROVEN"), ("BROKEN", "CHAIN_BROKEN"), ("NO_MAPPING", "NO_MAPPING"),
    ):
        assert summary[key] == sum(1 for r in chain["results"] if r["chain"] == state)


def test_mutation_a_declared_capacity_without_content_breaks_the_chain(tmp_path):
    """Garder la META et retirer le contenu : le gate doit virer au rouge.

    C'est le scenario exact du remplissage synthetique : un objet qui declare
    une capacite sans rien enseigner.
    """

    module = _load("coverage_chain", "scripts/check_coverage_chain.py")
    baseline = json.loads(CHAIN_JSON.read_text(encoding="utf-8"))
    proven = [r for r in baseline["results"] if r["chain"] == "PROVEN"]
    assert proven, "il faut au moins un atome prouve pour muter"

    victim = proven[0]
    source = ROOT / victim["source"]
    original = source.read_text(encoding="utf-8")
    head, _, _ = original.partition("\n")
    assert head.startswith("% META:"), "l'objet doit porter une ligne d'identite"

    # On conserve la META, on vide le contenu pedagogique.
    emptied = head + "\n\\section*{}\n"
    try:
        source.write_text(emptied, encoding="utf-8")
        mutated = module.build(ROOT)
        after = next(
            r for r in mutated["results"] if r["atom_id"] == victim["atom_id"]
        )
        assert after["chain"] != "PROVEN", (
            "un objet qui garde sa capacite declaree mais perd son contenu "
            "ne doit plus prouver la couverture"
        )
    finally:
        source.write_text(original, encoding="utf-8")

    restored = module.build(ROOT)
    back = next(r for r in restored["results"] if r["atom_id"] == victim["atom_id"])
    assert back["chain"] == "PROVEN", "le gate doit redevenir vert apres restauration"


def test_committed_chain_matches_the_producer(chain):
    module = _load("coverage_chain_2", "scripts/check_coverage_chain.py")
    recomputed = module.build(ROOT)
    assert recomputed["summary"] == chain["summary"]


def test_no_atom_remains_without_a_proven_chain(chain):
    """Gate produit : rouge tant qu'un atome obligatoire n'est pas prouve."""

    summary = chain["summary"]
    assert summary["CHAIN_BROKEN"] == 0
    assert summary["NO_MAPPING"] == 0
