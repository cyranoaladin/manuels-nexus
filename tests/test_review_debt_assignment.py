"""La regle d'imputation unique, testee une fois pour tous ses consommateurs."""

from __future__ import annotations

import importlib.util
import random
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _module():
    spec = importlib.util.spec_from_file_location(
        "review_debt_assignment", ROOT / "scripts/review_debt_assignment.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_an_explicit_ledger_outranks_a_derived_queue() -> None:
    """Le paquet ou l'humain verra reellement l'objet l'emporte."""
    module = _module()
    owner = module.assign(
        {"COUPLED": {"a", "b"}},
        {"REQUALIFICATION": {"b", "c"}},
    )
    assert owner == {"a": "COUPLED", "b": "COUPLED", "c": "REQUALIFICATION"}


def test_precedence_moves_the_imputation_without_closing_the_debt() -> None:
    """`b` change de porteur ; il ne disparait pas et n'est pas approuve."""
    module = _module()
    demoted = module.demoted_by_precedence(
        {"COUPLED": {"a", "b"}}, {"REQUALIFICATION": {"b", "c"}}
    )
    assert demoted == {"b"}
    owned = module.owned_by_class(
        {"COUPLED": {"a", "b"}}, {"REQUALIFICATION": {"b", "c"}}
    )
    assert owned == {"COUPLED": {"a", "b"}, "REQUALIFICATION": {"c"}}
    # Aucun objet perdu : l'union des porteurs couvre toujours l'union des
    # revendications.
    assert set().union(*owned.values()) == {"a", "b", "c"}


def test_two_carriers_of_the_same_class_never_share_an_object() -> None:
    """A l'interieur d'une classe il n'y a pas de precedence a appliquer :
    choisir un gagnant serait arbitraire, donc c'est une erreur."""
    module = _module()
    with pytest.raises(module.DuplicateAttribution):
        module.assign({"LEDGER_A": {"x"}, "LEDGER_B": {"x"}}, {})


def test_the_assignment_does_not_depend_on_any_ordering() -> None:
    """Permutation : memes objets, ordre different, meme attribution.

    L'appartenance a une file ne doit dependre ni de l'ordre de lecture, ni de
    l'ordre des clefs YAML, ni du nom des fichiers.
    """
    module = _module()
    explicit = {
        "TSPE_GEO": {"g1", "g2", "g3"},
        "COUPLED": {"c1", "c2", "shared"},
        "VARALEA": {"v1"},
    }
    derived = {
        "REQUALIFICATION": {"shared", "r1", "r2"},
        "SUSPENDED": {"s1"},
    }
    reference = module.assign(explicit, derived)

    generator = random.Random(20260901)
    for _ in range(25):
        explicit_keys = list(explicit)
        derived_keys = list(derived)
        generator.shuffle(explicit_keys)
        generator.shuffle(derived_keys)
        permuted_explicit = {key: set(explicit[key]) for key in explicit_keys}
        permuted_derived = {key: set(derived[key]) for key in derived_keys}
        assert module.assign(permuted_explicit, permuted_derived) == reference

    assert reference["shared"] == "COUPLED"


def test_an_empty_input_is_not_an_error() -> None:
    module = _module()
    assert module.assign({}, {}) == {}
    assert module.demoted_by_precedence({}, {}) == set()
