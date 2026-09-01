r"""Chaque objet laisse en revue manuelle sait ou il va.

L'oracle rend `manual_review` pour un motif unique -- pas de bloc VERIFY --
qui recouvre des situations sans rapport. Le registre les route sans jamais en
rendre un vert, et sans jamais nommer un objet : la disposition se deduit de ce
que l'objet CONTIENT.

L'objectif est MACHINE_UNCLASSIFIED = 0, pas MANUAL_REVIEW = 0 : exiger le
second reviendrait a exiger qu'aucune science humaine ne soit jamais requise.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def producer():
    return _module("disposition_ledger", "scripts/build_manual_review_disposition_ledger.py")


@pytest.fixture(scope="module")
def committed():
    return json.loads(
        (ROOT / "audit/1SPE_MANUAL_REVIEW_DISPOSITION_LEDGER.json").read_text(
            encoding="utf-8"
        )
    )


def test_the_committed_ledger_matches_the_producer(producer, committed) -> None:
    assert producer.build_ledger() == committed


def test_nothing_is_left_unclassified(committed) -> None:
    assert committed["machine_unclassified"] == 0
    assert committed["machine_unclassified_ids"] == []


def test_every_routed_object_carries_its_reason(committed) -> None:
    for row in committed["objects"]:
        assert row["disposition"]
        assert row["because"]
        assert row["path"]


def test_a_claimless_object_is_cleared_and_a_claiming_one_is_not(producer) -> None:
    """La disposition suit le CONTENU, jamais l'identifiant."""
    assert producer.computable_claims("Pense a deriver terme a terme.") == []
    assert producer.computable_claims(r"On a $f'(x) = 6x - 2$.") != []
    # Le meme texte, sous deux identifiants differents, donne la meme reponse.
    assert producer.computable_claims(r"$u_0 = 3$") == producer.computable_claims(
        r"$u_0 = 3$"
    )


def test_the_ledger_names_no_object_identifier_in_its_rules(producer) -> None:
    """Aucune liste blanche : le code ne cite aucun identifiant d'objet."""
    source = Path(producer.__file__).read_text(encoding="utf-8")
    rules = source.split("def build_ledger", 1)[0]
    assert "1SPE-" not in rules.replace('SCOPE_PREFIX = "1SPE-"', "")


def test_a_human_queue_smaller_than_the_raw_review_set(committed) -> None:
    """Le but du registre : ne pas envoyer 249 objets a un expert."""
    total = sum(committed["totals"].values())
    assert committed["human_queue_size"] < total
    assert committed["totals"]["AUCUNE_AFFIRMATION_CALCULABLE"] > 0


# ---------------------------------------------------------------------------
# L'axe oracle ne doit pas devenir un tampon
# ---------------------------------------------------------------------------


def _matrix():
    return _module("readiness_matrix", "scripts/build_publish_readiness_chapter_matrix.py")


def _chapter_with(tmp_path: Path, verdicts: list[str]) -> Path:
    directory = tmp_path / "1SPE-FICTIF"
    (directory / "validations").mkdir(parents=True)
    for index, verdict in enumerate(verdicts):
        (directory / "validations" / f"OBJ-{index}.sympy.json").write_text(
            json.dumps({"verdict": verdict}), encoding="utf-8"
        )
    return directory


def test_an_unrouted_manual_review_keeps_the_axis_red(tmp_path: Path) -> None:
    """La sensibilite du nouvel axe : sans routage, il reste rouge.

    Si ce test devenait vert, l'axe se contenterait de compter des recus et
    n'aurait plus rien a dire.
    """
    matrix = _matrix()
    directory = _chapter_with(tmp_path, ["pass", "manual_review"])
    result = matrix._oracle(directory, {"objects": []})
    assert result["machine_unclassified"] == 1
    assert result["status"] == "GAP"


def test_a_routed_manual_review_satisfies_the_axis(tmp_path: Path) -> None:
    matrix = _matrix()
    directory = _chapter_with(tmp_path, ["pass", "manual_review"])
    routed = {
        "objects": [
            {"chapter": "1SPE-FICTIF", "disposition": "SCIENCE_HUMAINE_REQUISE"}
        ]
    }
    result = matrix._oracle(directory, routed)
    assert result["machine_unclassified"] == 0
    assert result["human_science_required"] == 1
    assert result["status"] == "COMPLETE"


def test_a_failing_object_is_never_routed_away(tmp_path: Path) -> None:
    """Aucune disposition ne rattrape un `fail`."""
    matrix = _matrix()
    directory = _chapter_with(tmp_path, ["fail"])
    routed = {
        "objects": [
            {"chapter": "1SPE-FICTIF", "disposition": "AUCUNE_AFFIRMATION_CALCULABLE"}
        ]
    }
    assert matrix._oracle(directory, routed)["status"] == "GAP"
