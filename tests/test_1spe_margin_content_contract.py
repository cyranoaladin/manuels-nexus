"""Ce qui est capturé comme note de marge doit être dessiné, ou ne pas l'être.

Le compositeur capturait 3 990 notes et n'en dessinait aucune : la construction
de production ne lui passait pas d'inventaire de placement, `render_foreground`
sortait immédiatement, et rien ne le disait. Un contenu attendu mais jamais
affiché est une perte silencieuse.

Ce module vérifie le contrat classe par classe, l'égalité entre attendu visible
et rendu, et l'isolation des variantes. Puis il mute : une classe non déclarée,
une note perdue, un identifiant interne côté élève doivent tous être vus.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_margin_content_contract as gate  # noqa: E402


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
#  Le contrat
# ---------------------------------------------------------------------------


def test_the_partition_is_closed_and_nothing_is_unknown(
    payload: dict[str, Any],
) -> None:
    assert payload["summary"]["UNKNOWN_ROLES"] == 0
    assert payload["summary"]["unknown_roles"] == []
    assert payload["partition_is_closed"] == [
        "EXPECTED_VISIBLE_MARGIN_CONTENT",
        "NON_RENDERING_INTERNAL_ANCHOR",
        "OBSOLETE",
        "UNKNOWN",
    ]
    for entry in payload["contract"]:
        assert entry["classification"] in payload["partition_is_closed"]
        assert entry["classification"] != "UNKNOWN"


def test_every_class_cites_the_producer_that_emits_it(
    payload: dict[str, Any],
) -> None:
    """La classe se lit dans le code qui la fabrique, pas dans son nom."""

    assert payload["class_is_read_from_the_producer_not_the_name"] is True
    for entry in payload["contract"]:
        assert ".cls:" in entry["producer"], entry["role"]
        assert entry["pedagogical_role"].strip()
        assert entry["assembly_consumer"].strip()
        assert entry["authority"].strip()
        assert entry["applies_to"], entry["role"]


def test_nothing_expected_visible_is_silently_dropped(
    payload: dict[str, Any],
) -> None:
    """L'invariant : attendu visible == rendu visible."""

    summary = payload["summary"]
    assert summary["SILENTLY_DROPPED_MARGIN_ITEMS"] == 0
    assert summary["EXPECTED_VISIBLE_MARGIN_ITEMS"] == summary[
        "RENDERED_VISIBLE_MARGIN_ITEMS"
    ]
    # Le contrôle serait vide de sens si rien n'était attendu.
    assert summary["EXPECTED_VISIBLE_MARGIN_ITEMS"] > 3000
    for variant in payload["variants"]:
        assert variant["SILENTLY_DROPPED_MARGIN_ITEMS"] == 0, variant["variant"]
        for row in variant["roles"]:
            if row["expected_visible_here"]:
                assert row["rendered"] == row["captured"], row


def test_the_internal_identifier_never_reaches_the_student_edition(
    payload: dict[str, Any],
) -> None:
    """AGENTS.md l'interdit côté élève, et l'autorise côté professeur."""

    by_variant = {row["variant"]: row for row in payload["variants"]}
    student = {row["role"]: row for row in by_variant["eleve"]["roles"]}
    teacher = {row["role"]: row for row in by_variant["professeur"]["roles"]}

    assert student.get("professor-id", {"rendered": 0})["rendered"] == 0
    assert teacher["professor-id"]["rendered"] > 0
    entry = next(row for row in payload["contract"] if row["role"] == "professor-id")
    assert entry["applies_to"] == ["professeur"]


# ---------------------------------------------------------------------------
#  Mutations
# ---------------------------------------------------------------------------


def test_an_undeclared_role_is_unknown_and_blocking(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(gate, "captured_by_role", lambda variant: {"surprise": 3})
    monkeypatch.setattr(gate, "rendered_by_role", lambda variant: {"surprise": 3})

    payload = gate.build()

    assert payload["summary"]["UNKNOWN_ROLES"] == 1
    assert payload["summary"]["unknown_roles"] == ["surprise"]


def test_a_dropped_visible_note_is_counted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """La régression exacte du jour : capturé oui, dessiné non."""

    monkeypatch.setattr(gate, "captured_by_role", lambda variant: {"chrono": 734})
    monkeypatch.setattr(gate, "rendered_by_role", lambda variant: {})

    payload = gate.build()

    assert payload["summary"]["SILENTLY_DROPPED_MARGIN_ITEMS"] == 734 * 2
    assert payload["summary"]["RENDERED_VISIBLE_MARGIN_ITEMS"] == 0


def test_a_note_rendered_where_it_does_not_apply_is_not_counted_as_expected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Un identifiant professeur côté élève n'est pas « attendu visible ».

    Il ne doit donc jamais compter comme un rendu conforme : la variante fait
    partie du contrat.
    """

    monkeypatch.setattr(gate, "captured_by_role", lambda variant: {"professor-id": 5})
    monkeypatch.setattr(gate, "rendered_by_role", lambda variant: {"professor-id": 5})

    payload = gate.build()
    student = next(
        row for row in payload["variants"] if row["variant"] == "eleve"
    )
    role = next(row for row in student["roles"] if row["role"] == "professor-id")

    assert role["expected_visible_here"] is False
    assert student["EXPECTED_VISIBLE_MARGIN_ITEMS"] == 0


# ---------------------------------------------------------------------------
#  Le chemin de production, et pas une reconstruction parallèle
# ---------------------------------------------------------------------------


def test_the_production_build_supplies_the_layout_inventory() -> None:
    """Le pipeline testé doit être le pipeline produit.

    Le compositeur ne dessine qu'à partir de l'inventaire de la passe
    précédente. Tant que seul le harnais de test le fournissait, la production
    capturait sans jamais dessiner — et rien ne le signalait.
    """

    assembler = (
        ROOT / "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
    ).read_text(encoding="utf-8")

    assert "NEXUS_MARGIN_LAYOUT_PREVIOUS" in assembler
    assert "NEXUS_MARGIN_LAYOUT_NEXT" in assembler
    assert "NEXUS_MARGIN_PASS_NUMBER" in assembler
    assert "_margin_pass_environment" in assembler
    # La construction refuse de livrer un PDF dont les placements n'ont pas
    # convergé : sans cela, une passe manquante redeviendrait invisible.
    assert "placements de marge non stabilisés" in assembler
    assert "inventaire de marges absent" in assembler


def test_the_margin_nonce_is_deterministic() -> None:
    """Deux constructions des mêmes sources doivent rester comparables."""

    sys.path.insert(0, str(ROOT / "Mathematiques/manuel-maths/scripts"))
    import assemble_manuel  # noqa: PLC0415

    first = assemble_manuel._margin_run_nonce("1SPE", "eleve")
    second = assemble_manuel._margin_run_nonce("1SPE", "eleve")

    assert first == second
    assert len(first) == 32 and all(c in "0123456789abcdef" for c in first)
    assert first != assemble_manuel._margin_run_nonce("1SPE", "professeur")
