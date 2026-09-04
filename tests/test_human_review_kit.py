"""Le dossier de revue doit être lisible, complet, et ne nommer personne.

Vingt verdicts attendent des personnes. Ce module vérifie que ce qui les
attend est ouvrable — index, deux vues par chapitre, formules rendues,
formulaire et commande d'enregistrement — et qu'aucune identité n'y a été
inventée.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_human_review_kit as gate  # noqa: E402


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


def test_the_kit_covers_the_ten_chapters_and_both_roles(
    payload: dict[str, Any],
) -> None:
    summary = payload["summary"]
    assert summary["CHAPTERS"] == 10
    assert summary["EXPECTED_VERDICTS"] == 20
    assert summary["CHAPTERS_WITHOUT_BOTH_ROLES"] == 0
    assert summary["VIEWS_WRITTEN"] == 20
    assert (gate.KIT / "INDEX.html").is_file()
    for entry in payload["chapters"]:
        assert len(entry["roles"]) == 2, entry["chapter"]
        for role in entry["roles"]:
            assert (ROOT / role["kit_view"]).is_file(), role["kit_view"]
            assert (ROOT / role["packet"]).is_file(), role["packet"]


def test_every_view_renders_its_mathematics(payload: dict[str, Any]) -> None:
    """Un relecteur ne doit pas décoder du TeX pour juger une copie."""

    with_math = 0
    for entry in payload["chapters"]:
        for role in entry["roles"]:
            text = (ROOT / role["kit_view"]).read_text(encoding="utf-8")
            assert "MathJax" in text, role["kit_view"]
            formulas = re.findall(r"\$[^$]{2,}\$", text)
            if formulas:
                with_math += 1
                # Le TeX traverse intact : ni fraction vidée, ni pi perdu.
                joined = " ".join(formulas)
                assert "( )/(" not in joined, role["kit_view"]
    assert with_math >= 5, "presque aucune vue ne porte de mathématiques"


def test_no_view_carries_a_control_character(payload: dict[str, Any]) -> None:
    """Une première version appariait les marqueurs par des octets invisibles."""

    for entry in payload["chapters"]:
        for role in entry["roles"]:
            text = (ROOT / role["kit_view"]).read_text(encoding="utf-8")
            offenders = [
                character
                for character in text
                if ord(character) < 32 and character not in "\n\r\t"
            ]
            assert offenders == [], role["kit_view"]


def test_every_view_carries_the_verdict_form_and_its_commands(
    payload: dict[str, Any],
) -> None:
    for entry in payload["chapters"]:
        for role in entry["roles"]:
            text = (ROOT / role["kit_view"]).read_text(encoding="utf-8")
            assert "Votre verdict" in text
            assert "human_review_governance.py draft" in text
            assert "human_review_governance.py validate" in text
            assert entry["semantic_digest"] in text, role["kit_view"]
            for verdict in ("APPROVED", "CHANGES_REQUESTED", "REJECTED"):
                assert verdict in text, (role["kit_view"], verdict)


def test_the_kit_names_no_reviewer(payload: dict[str, Any]) -> None:
    """Aucune identité n'est créée ni déduite : elles viennent de l'humain."""

    assert payload["approves_nothing"] is True
    assert "jamais de Git" in payload["no_reviewer_is_named_here"]
    forbidden = ("Claude", "OpenAI", "Anthropic", "Nexus Réussite <")
    for entry in payload["chapters"]:
        for role in entry["roles"]:
            assert role["verdict"] is None, role
            text = (ROOT / role["kit_view"]).read_text(encoding="utf-8")
            for name in forbidden:
                assert name not in text, (role["kit_view"], name)


def test_the_mandatory_decision_is_visible_and_not_lost(
    payload: dict[str, Any],
) -> None:
    """Les deux GEOREP ne doivent pas se perdre parmi les 54."""

    assert payload["summary"]["CHAPTERS_WITH_MANDATORY_DECISION"] == 1
    georep = next(
        row
        for row in payload["chapters"]
        if row["chapter"] == "1SPE-GEOMETRIE-REPEREE"
    )
    assert georep["bareme"]["has_mandatory_decision"] is True
    assert len(georep["bareme"]["mandatory_decisions"]) == 2
    index = (gate.KIT / "INDEX.html").read_text(encoding="utf-8")
    assert "DÉCISION OBLIGATOIRE" in index
    view = (
        ROOT
        / "audit/HUMAN_REVIEW_KIT_1SPE"
        / "1SPE-GEOMETRIE-REPEREE-B-EXPERT_PROGRAMME_PEDAGOGIE.html"
    ).read_text(encoding="utf-8")
    assert "DÉCISION HUMAINE OBLIGATOIRE" in view


def test_the_index_reports_what_is_pending(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    assert summary["PENDING_VERDICTS"] == summary["EXPECTED_VERDICTS"] == 20
    assert summary["ASSESSMENT_QUESTIONS"] > 250
    assert summary["BAREME_JUDGEMENTS_REQUIRED"] > 0
    index = (gate.KIT / "INDEX.html").read_text(encoding="utf-8")
    for entry in payload["chapters"]:
        assert entry["chapter"] in index


# ---------------------------------------------------------------------------
#  Le rendu minimal ne doit pas réinterpréter les mathématiques
# ---------------------------------------------------------------------------


def test_html_is_escaped_but_formulas_are_not_touched() -> None:
    rendered = gate._inline("Un <b>tag</b> et $\\dfrac{5\\pi}{6}$ intact")

    assert "&lt;b&gt;" in rendered
    assert "$\\dfrac{5\\pi}{6}$" in rendered


def test_paired_markers_become_tags_and_a_lone_marker_survives() -> None:
    assert gate._pair("du **gras** ici", "**", "<b>", "</b>") == (
        "du <b>gras</b> ici"
    )
    # Un marqueur seul n'ouvre rien : il appartient au texte.
    assert gate._pair("un ** seul", "**", "<b>", "</b>") == "un ** seul"


def test_a_missing_source_view_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sans la vue produite par son producteur, il n'y a rien à réafficher."""

    monkeypatch.setattr(gate, "REVIEWS", tmp_path)

    with pytest.raises(gate.KitError, match="chapitres absents"):
        gate.build(write=False)
