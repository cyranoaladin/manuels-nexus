"""Vingt paquets attendus, vingt présents — et l'attendu n'est pas écrit à la main.

Un paquet manquant ne se voit pas : le dossier existe, les autres paquets sont
là. Il ne se voit qu'en comptant d'abord ce qui est ATTENDU. Ce module vérifie
que l'attendu est LU (chapitres sur l'assembleur, rôles sur les instructions
données aux relecteurs), puis mute la mesure pour prouver qu'un paquet absent,
vide ou muet est bien refusé.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_human_packet_completeness as gate  # noqa: E402


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


def test_every_expected_packet_and_reading_view_is_present(
    payload: dict[str, Any],
) -> None:
    summary = payload["summary"]
    assert summary["HUMAN_PACKETS_EXPECTED"] == 20
    assert summary["HUMAN_PACKETS_PRESENT"] == 20
    assert summary["HUMAN_PACKETS_MISSING"] == 0
    assert summary["HUMAN_READING_VIEWS_MISSING"] == 0
    assert summary["PACKETS_WITHOUT_REQUIRED_FIELDS"] == 0


def test_a_packet_carries_enough_to_be_reviewed(payload: dict[str, Any]) -> None:
    """De quoi il parle, qui le relit, ce qu'il couvre, ce qu'on lui demande."""

    assert set(payload["required_fields"]) >= {
        "chapter_id",
        "review_role",
        "objects",
        "object_set_digest",
        "minimum_controls",
        "permitted_verdicts",
    }
    assert payload["summary"]["OBJECTS_OFFERED_FOR_REVIEW"] > 2000
    for row in payload["packets"]:
        assert row["missing_fields"] == [], row
        assert row["objects"] > 0, row


def test_the_expected_count_is_read_from_the_repository(
    payload: dict[str, Any],
) -> None:
    """Ni « dix », ni « vingt » ne sont écrits dans le producteur."""

    from manual_source_surface import manual_chapters  # noqa: PLC0415

    assert payload["chapters"] == manual_chapters("1SPE")
    instructions = ROOT / payload["what_is_expected_is_read_not_written"][
        "reviewer_roles"
    ]
    assert instructions.is_file()
    text = instructions.read_text(encoding="utf-8")
    for role in payload["reviewer_roles"]:
        assert role in text, role
    source = (ROOT / "scripts/build_1spe_human_packet_completeness.py").read_text(
        encoding="utf-8"
    )
    assert "EXPERT_MATHEMATIQUE" not in source
    assert "1SPE-SUITES" not in source


def test_the_governance_unit_is_twenty_chapter_verdicts(
    payload: dict[str, Any],
) -> None:
    """Vingt décisions, pas des milliers de signatures.

    Les files de relecture comptent 2 325 objets, 167 questions de QCM et
    d'autres lots encore. Les présenter comme une charge humaine annoncerait
    des centaines de décisions là où le contrat en demande vingt : ce sont des
    points d'attention à l'intérieur d'un chapitre, et la revue porte sur le
    chapitre entier.
    """

    summary = payload["summary"]
    assert summary["CHAPTER_VERDICTS_EXPECTED"] == 20
    assert (
        summary["CHAPTER_VERDICTS_RENDERED"] + summary["CHAPTER_VERDICTS_PENDING"]
        == 20
    )
    roles = {row["role"] for row in payload["chapter_verdicts"]}
    assert roles == {"EXPERT_MATHEMATIQUE", "EXPERT_PROGRAMME_PEDAGOGIE"}
    chapters = {row["chapter"] for row in payload["chapter_verdicts"]}
    assert len(chapters) == 10
    assert "vingt" in payload["the_unit_of_governance_is_the_chapter_verdict"]


def test_the_absence_of_rendered_evidence_is_reported_not_buried(
    payload: dict[str, Any],
) -> None:
    """Aucun paquet ne porte les pages rendues : le dire vaut mieux que le taire."""

    assert payload["summary"]["PACKETS_WITHOUT_RENDERED_EVIDENCE"] == 20
    assert "gel de relecture" in payload["rendered_evidence_is_reported_not_required_here"]


# ---------------------------------------------------------------------------
#  Mutations
# ---------------------------------------------------------------------------


def _elsewhere(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    reviews = tmp_path / "human"
    reviews.mkdir()
    instructions = reviews / "ASSIGNMENT_TEMPLATE_AND_REVIEW_INSTRUCTIONS.md"
    instructions.write_text(
        "Relecture A-EXPERT_MATHEMATIQUE et B-EXPERT_PROGRAMME_PEDAGOGIE.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "REVIEWS", reviews)
    monkeypatch.setattr(gate, "INSTRUCTIONS", instructions)
    monkeypatch.setattr(gate, "manual_chapters", lambda manual: ["CHAP-A"])
    return reviews


def _write_packet(reviews: Path, role: str, **overrides: Any) -> None:
    directory = reviews / "CHAP-A"
    directory.mkdir(exist_ok=True)
    content: dict[str, Any] = {
        "chapter_id": "CHAP-A",
        "review_role": role.split("-", 1)[1],
        "objects": [{"id": "O1"}],
        "object_set_digest": "sha256:0",
        "minimum_controls": ["c1"],
        "permitted_verdicts": ["APPROVE", "REJECT"],
        "render_evidence": "ABSENT",
    }
    content.update(overrides)
    (directory / f"packet-{role}.json").write_text(
        json.dumps(content), encoding="utf-8"
    )
    (directory / f"view-{role}.md").write_text("# vue\n", encoding="utf-8")


def test_a_missing_packet_is_counted_and_blocking(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    reviews = _elsewhere(tmp_path, monkeypatch)
    _write_packet(reviews, "A-EXPERT_MATHEMATIQUE")

    result = gate.build()

    assert result["summary"]["HUMAN_PACKETS_EXPECTED"] == 2
    assert result["summary"]["HUMAN_PACKETS_MISSING"] == 1
    assert gate.main(["--check"]) == 1


def test_a_packet_without_its_reading_view_is_counted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    reviews = _elsewhere(tmp_path, monkeypatch)
    for role in ("A-EXPERT_MATHEMATIQUE", "B-EXPERT_PROGRAMME_PEDAGOGIE"):
        _write_packet(reviews, role)
    (reviews / "CHAP-A/view-B-EXPERT_PROGRAMME_PEDAGOGIE.md").unlink()

    result = gate.build()

    assert result["summary"]["HUMAN_PACKETS_MISSING"] == 0
    assert result["summary"]["HUMAN_READING_VIEWS_MISSING"] == 1
    assert gate.main(["--check"]) == 1


def test_an_empty_packet_does_not_count_as_a_packet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Un fichier présent mais sans objet n'offre rien à relire."""

    reviews = _elsewhere(tmp_path, monkeypatch)
    _write_packet(reviews, "A-EXPERT_MATHEMATIQUE", objects=[])
    _write_packet(reviews, "B-EXPERT_PROGRAMME_PEDAGOGIE")

    result = gate.build()

    assert result["summary"]["HUMAN_PACKETS_PRESENT"] == 2
    assert result["summary"]["PACKETS_WITHOUT_REQUIRED_FIELDS"] == 1
    assert gate.main(["--check"]) == 1


def test_a_packet_that_does_not_say_what_to_control_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    reviews = _elsewhere(tmp_path, monkeypatch)
    _write_packet(reviews, "A-EXPERT_MATHEMATIQUE", minimum_controls=[])
    _write_packet(reviews, "B-EXPERT_PROGRAMME_PEDAGOGIE")

    result = gate.build()

    assert result["packets"][0]["missing_fields"] == ["minimum_controls"]
    assert gate.main(["--check"]) == 1


def test_an_unreadable_packet_is_refused_rather_than_skipped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    reviews = _elsewhere(tmp_path, monkeypatch)
    for role in ("A-EXPERT_MATHEMATIQUE", "B-EXPERT_PROGRAMME_PEDAGOGIE"):
        _write_packet(reviews, role)
    (reviews / "CHAP-A/packet-A-EXPERT_MATHEMATIQUE.json").write_text(
        "{ pas du JSON", encoding="utf-8"
    )

    result = gate.build()

    assert "unreadable" in result["packets"][0]
    assert result["summary"]["PACKETS_WITHOUT_REQUIRED_FIELDS"] == 1
    assert gate.main(["--check"]) == 1


def test_missing_reviewer_instructions_are_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sans les rôles déclarés, l'attendu serait inventé."""

    monkeypatch.setattr(gate, "INSTRUCTIONS", tmp_path / "absent.md")

    with pytest.raises(gate.PacketError):
        gate.build()
    assert gate.main(["--check"]) == 2
