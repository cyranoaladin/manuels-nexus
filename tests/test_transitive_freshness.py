"""Un artefact ne peut pas être frais s'il repose sur une entrée périmée.

Le défaut observé : la réconciliation des populations mathématiques déclarait
`CURRENT_BY_INPUT_DIGEST` alors qu'elle lisait un `DIMENSION_MATHEMATICS.json`
qui n'avait pas été régénéré depuis l'écriture de soixante-deux objets. Son
enveloppe était honnête — les octets lus n'avaient pas bougé — et son verdict
faux : ces octets étaient eux-mêmes obsolètes.

L'empreinte d'entrée prouve « ces octets n'ont pas changé depuis ma lecture ».
Elle ne prouve pas « ces octets décrivaient le dépôt courant ». La différence
n'apparaît que sur les artefacts dérivés, et c'est là qu'elle est dangereuse :
ce sont eux qu'on cite.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import evidence_freshness as freshness  # noqa: E402


def test_a_stale_input_makes_its_consumer_stale(tmp_path: Path) -> None:
    """La fraîcheur se propage : un parent n'est jamais plus frais qu'un fils."""
    source = tmp_path / "source.txt"
    source.write_text("v1", encoding="utf-8")

    intermediate = tmp_path / "intermediate.json"
    intermediate.write_text(json.dumps({
        "freshness": freshness.stamp(["source.txt"], root=tmp_path),
    }), encoding="utf-8")

    consumer_envelope = freshness.stamp(["intermediate.json"], root=tmp_path)

    # Rien n'a bougé : les deux sont courants.
    assert freshness.assess(consumer_envelope, root=tmp_path)["FRESHNESS_STATUS"] == \
        freshness.CURRENT

    # La source change ; l'intermédiaire n'est pas régénéré. Ses octets à lui
    # n'ont pas bougé — c'est exactement le piège.
    source.write_text("v2", encoding="utf-8")
    assert freshness.assess_artifact(Path("intermediate.json"), root=tmp_path)[
        "FRESHNESS_STATUS"] == freshness.STALE

    verdict = freshness.assess(consumer_envelope, root=tmp_path)
    assert verdict["FRESHNESS_STATUS"] == freshness.STALE_TRANSITIVE
    assert verdict["STALE_INPUTS"] == ["intermediate.json"]


def test_a_current_chain_stays_current(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("v1", encoding="utf-8")
    intermediate = tmp_path / "intermediate.json"
    intermediate.write_text(json.dumps({
        "freshness": freshness.stamp(["source.txt"], root=tmp_path),
    }), encoding="utf-8")
    envelope = freshness.stamp(["intermediate.json"], root=tmp_path)
    verdict = freshness.assess(envelope, root=tmp_path)
    assert verdict["FRESHNESS_STATUS"] == freshness.CURRENT
    assert verdict["STALE_INPUTS"] == []


def test_inputs_without_an_envelope_are_not_penalised(tmp_path: Path) -> None:
    """Un `.tex` n'a pas d'enveloppe : son absence n'est pas une péremption."""
    (tmp_path / "objet.tex").write_text("contenu", encoding="utf-8")
    envelope = freshness.stamp(["objet.tex"], root=tmp_path)
    verdict = freshness.assess(envelope, root=tmp_path)
    assert verdict["FRESHNESS_STATUS"] == freshness.CURRENT
    assert verdict["STALE_INPUTS"] == []


def test_a_cycle_does_not_hang(tmp_path: Path) -> None:
    """Deux artefacts qui se citent l'un l'autre ne doivent pas boucler."""
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(json.dumps({"freshness": {"INPUT_PATHS": ["b.json"],
                                           "INPUT_DIGEST": "sha256:x"}}), encoding="utf-8")
    b.write_text(json.dumps({"freshness": {"INPUT_PATHS": ["a.json"],
                                           "INPUT_DIGEST": "sha256:y"}}), encoding="utf-8")
    envelope = freshness.stamp(["a.json"], root=tmp_path)
    verdict = freshness.assess(envelope, root=tmp_path)
    assert verdict["FRESHNESS_STATUS"] in {
        freshness.CURRENT, freshness.STALE, freshness.STALE_TRANSITIVE,
    }


def test_the_real_reconciliation_is_transitively_current() -> None:
    """Le cas qui a révélé le défaut doit maintenant être vérifié."""
    verdict = freshness.assess_artifact(
        Path("audit/MATHEMATICS_POPULATION_RECONCILIATION.json")
    )
    assert verdict["FRESHNESS_STATUS"] == freshness.CURRENT, verdict.get("STALE_INPUTS")
