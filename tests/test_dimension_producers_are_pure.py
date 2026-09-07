"""Calculer une preuve ne doit pas la publier.

Les quatre producteurs de dimension écrivaient leur artefact depuis `build()`.
Deux conséquences, toutes deux observées :

* un test qui appelle `build()` pour lire un verdict réécrit la preuve
  déposée — et s'il l'appelle au milieu d'une mutation, il publie la mutation.
  C'est ainsi que `1SPE-SECOND-DEGRE-2026-C99`, capacité inventée par un test
  de non-régression, s'est retrouvée dans `audit/DIMENSION_REGULATION.json`
  avec `status: failed` ;
* `--check` lisait l'artefact, appelait `build()` — qui l'écrasait — puis
  comparait sa lecture au résultat. Le contrôle effaçait la dérive qu'il était
  censé signaler : après un `--check`, plus aucun lecteur ne pouvait la voir.

`build()` calcule et retourne. `write()` publie. `main()` publie hors `--check`.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

PRODUCERS = [
    "build_dimension_mathematics",
    "build_dimension_print",
    "build_dimension_regulation",
    "build_dimension_visual",
]


@pytest.mark.parametrize("name", PRODUCERS)
def test_build_does_not_touch_the_deposited_evidence(name: str) -> None:
    module = importlib.import_module(name)
    output = Path(module.OUTPUT)
    before = output.read_bytes() if output.is_file() else None
    module.build()
    after = output.read_bytes() if output.is_file() else None
    assert after == before, f"{name}.build() a réécrit {output.name}"


@pytest.mark.parametrize("name", PRODUCERS)
def test_the_producer_exposes_a_separate_publication_step(name: str) -> None:
    module = importlib.import_module(name)
    assert callable(getattr(module, "write", None)), (
        f"{name} doit exposer write(payload) distinct de build()"
    )


@pytest.mark.parametrize("name", ["build_dimension_regulation"])
def test_build_is_reproducible(name: str) -> None:
    """Deux calculs successifs sur la même source donnent le même verdict.

    Restreint à `regulation` : `visual` et `print` réouvrent les PDF de la
    collection, et doubler ce coût pour retrouver la même réponse n'apprend
    rien de plus que le premier appel.
    """
    module = importlib.import_module(name)
    first = module.build()
    second = module.build()
    ignored = {"generated_at_utc", "generated_at"}
    assert {k: v for k, v in first.items() if k not in ignored} == \
        {k: v for k, v in second.items() if k not in ignored}


def test_check_reports_drift_without_erasing_it(tmp_path: Path) -> None:
    module = importlib.import_module("build_dimension_regulation")
    output = Path(module.OUTPUT)
    saved = output.read_bytes()
    try:
        drifted = json.loads(saved)
        drifted["status"] = "passed_but_stale_marker"
        output.write_text(
            json.dumps(drifted, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        rc = module.main_for_argv(["--check"])
        assert rc == 1, "la dérive doit être signalée"
        still = json.loads(output.read_text(encoding="utf-8"))
        assert still["status"] == "passed_but_stale_marker", (
            "--check ne doit pas effacer la dérive qu'il signale"
        )
    finally:
        output.write_bytes(saved)
