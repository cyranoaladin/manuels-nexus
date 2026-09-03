"""La vérification des marges tourne sur le manuel LIVRÉ, pas sur une maquette.

Le compositeur a capturé 3 990 notes et n'en a dessiné aucune pendant toute une
campagne. Le contrôle du ledger existait pourtant, complet, éprouvé : il ne
tournait que sur des documents de deux pages recompilés pour l'occasion, et la
construction de production, elle, ne lui fournissait rien à vérifier. Un
harnais qui prouve un pipeline que personne ne livre ne prouve rien.

La construction publie donc désormais, à côté du PDF, les deux inventaires dont
la vérification a besoin : le placement des notes et les liens écrits pour
elles. Ce module les lit tels qu'ils sont livrés, reconstruit le ledger depuis
les objets réels du PDF livré, et exécute le contrôle complet.

Aucun chemin de compilation n'est reconstitué ici : les fichiers sont ceux que
`assemble_manuel.py` a promus.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

MANUAL_ROOT = Path(__file__).resolve().parents[1]
ROOT = MANUAL_ROOT.parents[1]
BUILD = MANUAL_ROOT / "build/MANUEL_1SPE"
VARIANTS = ("eleve", "professeur")


def _load(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def ledger_module() -> Any:
    pytest.importorskip("pikepdf")
    return _load("margin_ledger_production", MANUAL_ROOT / "scripts/margin_ledger.py")


@pytest.fixture(scope="module")
def contract_module() -> Any:
    return _load(
        "margin_contract_production", MANUAL_ROOT / "scripts/margin_contract.py"
    )


def _shipped(variant: str) -> dict[str, Path]:
    stem = f"MANUEL_1SPE_{variant}"
    return {
        "pdf": BUILD / f"{stem}.pdf",
        "layout": BUILD / f"{stem}.margin-layout.json",
        "links": BUILD / f"{stem}.margin-links.json",
    }


# ---------------------------------------------------------------------------
#  Le pipeline produit fournit lui-même ses preuves
# ---------------------------------------------------------------------------


def test_the_production_assembler_publishes_both_inventories() -> None:
    """Sans eux, la vérification ne pourrait tourner que sur des maquettes."""

    assembler = (MANUAL_ROOT / "scripts/assemble_manuel.py").read_text(
        encoding="utf-8"
    )

    assert "margin_layout_path = build /" in assembler
    assert "margin_links_path = build /" in assembler
    assert "NEXUS_MARGIN_LINK_INVENTORY_NEXT" in assembler
    # Les deux inventaires sont promus dans la même boucle que le PDF : ils
    # décrivent CE PDF-là, ou ils ne décrivent rien.
    promotion = assembler[assembler.index("for source, destination in (") :]
    promotion = promotion[: promotion.index("):")]
    for name in ("margin_layout_path", "margin_links_path", "pdf_path"):
        assert name in promotion, name
    # Une passe sans inventaire arrête la construction plutôt que de livrer.
    assert "inventaire de marges absent" in assembler
    assert "inventaire de liens de marge absent" in assembler


@pytest.mark.parametrize("variant", VARIANTS)
def test_the_shipped_inventories_describe_the_shipped_pdf(variant: str) -> None:
    shipped = _shipped(variant)
    for name, path in shipped.items():
        if not path.is_file():
            pytest.skip(f"{name} non construit : {path}")

    layout = json.loads(shipped["layout"].read_text(encoding="utf-8"))

    assert layout["state"] == "stable"
    assert layout["variant"] == variant
    assert layout["read_digest"] == layout["computed_digest"]
    assert layout["notes"], "l'inventaire livré ne décrit aucune note"


@pytest.mark.parametrize("variant", VARIANTS)
def test_every_shipped_margin_note_verifies_against_the_shipped_pdf(
    variant: str, ledger_module: Any, contract_module: Any
) -> None:
    """Le contrôle complet, sur l'artefact livré et sur lui seul.

    Identité, contrat, géométrie physique, liens : chaque note du manuel doit
    se retrouver dans le PDF, au bon endroit, du bon côté, avec le bon
    contenu.
    """

    shipped = _shipped(variant)
    for name, path in shipped.items():
        if not path.is_file():
            pytest.skip(f"{name} non construit : {path}")

    capture = json.loads(shipped["layout"].read_text(encoding="utf-8"))
    stable = contract_module.materialize_stable_layout(capture)
    ledger = ledger_module.reconstruct_margin_ledger(
        shipped["pdf"], capture, stable, shipped["links"]
    )

    # Le PDF vient du moteur : il écrit ses nombres à trois décimales, et la
    # borne au sp près lui est physiquement inaccessible. On le DIT ici plutôt
    # que de relâcher le contrôle pour tout le monde.
    result = ledger_module.verify_margin_layout(
        shipped["pdf"],
        capture,
        stable,
        ledger,
        rendered_position_tolerance_sp=(
            ledger_module.ENGINE_WRITTEN_POSITION_TOLERANCE_SP
        ),
    )

    assert result.passed is True
    assert result.note_count == len(capture["notes"])
    assert result.note_count > 900, "un manuel entier porte plus de notes que cela"


@pytest.mark.parametrize("variant", VARIANTS)
def test_a_note_moved_in_the_inventory_is_refused_against_the_shipped_pdf(
    variant: str, ledger_module: Any, contract_module: Any
) -> None:
    """Mutation : sans elle, la vérification pourrait être vide de sens.

    Une note déplacée d'un centimètre dans l'inventaire ne correspond plus à ce
    que le PDF montre. Le contrôle doit s'en apercevoir.
    """

    shipped = _shipped(variant)
    for name, path in shipped.items():
        if not path.is_file():
            pytest.skip(f"{name} non construit : {path}")

    capture = json.loads(shipped["layout"].read_text(encoding="utf-8"))
    stable = contract_module.materialize_stable_layout(capture)
    ledger = ledger_module.reconstruct_margin_ledger(
        shipped["pdf"], capture, stable, shipped["links"]
    )

    moved = json.loads(json.dumps(ledger))
    one_centimetre_sp = int(65536 * 72.27 / 2.54)
    left, top, right, bottom = moved["notes"][0]["bbox_sp"]
    moved["notes"][0]["bbox_sp"] = [
        left,
        top + one_centimetre_sp,
        right,
        bottom + one_centimetre_sp,
    ]

    with pytest.raises(ledger_module.MarginLedgerError):
        ledger_module.verify_margin_layout(
            shipped["pdf"],
            capture,
            stable,
            moved,
            rendered_position_tolerance_sp=(
                ledger_module.ENGINE_WRITTEN_POSITION_TOLERANCE_SP
            ),
        )
