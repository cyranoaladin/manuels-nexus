"""Régressions de périmètre pour le programme 1SPE applicable en 2026-2027.

Ces tests encodent l'arbitrage réglementaire explicite : le socle
trigonométrique de Première s'arrête au cercle, au radian et à la lecture de
sinus/cosinus. Les enrichissements conservés doivent être déclarés comme
extensions et rester hors des QCM et évaluations obligatoires.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "chapitres"
REFERENTIAL = ROOT / "referentiel"
META = re.compile(r"^% META: (\{.*\})", re.MULTILINE)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _meta(path: Path) -> dict:
    match = META.search(path.read_text(encoding="utf-8"))
    assert match, f"META absent: {path}"
    return json.loads(match.group(1))


def test_trigonometrie_socle_ne_contient_que_cercle_radian_sinus_cosinus() -> None:
    referential = _json(REFERENTIAL / "capacites_1SPE_TRIGONOMETRIE.json")
    contract = yaml.safe_load(
        (CHAPTERS / "1SPE-TRIGONOMETRIE/contrat.yaml").read_text(encoding="utf-8")
    )

    assert [item["id"] for item in referential["capacites"]] == [
        "1SPE-TRIGONOMETRIE-C1",
        "1SPE-TRIGONOMETRIE-C2",
    ]
    assert [item["code"] for item in contract["capacites"]] == ["C1", "C2"]
    assert {item["code"] for item in contract["extensions_facultatives"]} == {
        "X1",
        "X2",
        "X3",
    }
    assert all(
        item["programme_alignment"] == "OPTIONAL_EXTENSION"
        and item["label"] == "Approfondissement — Vers la Terminale"
        for item in contract["extensions_facultatives"]
    )


def test_trigonometrie_qcm_et_evaluations_restent_dans_le_socle() -> None:
    chapter = CHAPTERS / "1SPE-TRIGONOMETRIE"
    qcm = _json(chapter / "qcm/1SPE-TRIGONOMETRIE-QCM.json")
    assert len(qcm["questions"]) == 15
    assert {question["capacite"] for question in qcm["questions"]} <= {"C1", "C2"}

    for path in sorted((chapter / "evaluations").glob("*.tex")):
        meta = _meta(path)
        assert set(meta["capacites_codes"]) <= {"C1", "C2"}
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"(?:—|-) C[345]\b", text)


def test_trigonometrie_ressources_avancees_sont_des_extensions_explicitement_marquees() -> None:
    chapter = CHAPTERS / "1SPE-TRIGONOMETRIE"
    expected = {
        "methodes/1SPE-TRIGO-ME-003.tex": "X1",
        "methodes/1SPE-TRIGO-ME-004.tex": "X2",
        "methodes/1SPE-TRIGO-ME-005.tex": "X3",
        "exercices/1SPE-TRIGO-EX-019.tex": "X1",
        "corriges/1SPE-TRIGO-CO-019.tex": "X1",
        "exercices/1SPE-TRIGO-EX-024.tex": "X2",
        "exercices/1SPE-TRIGO-EX-024-CDP.tex": "X2",
        "corriges/1SPE-TRIGO-CO-024.tex": "X2",
    }
    for relative, extension_code in expected.items():
        path = chapter / relative
        meta = _meta(path)
        assert meta.get("capacites", []) == []
        assert meta.get("capacites_codes", []) == []
        assert meta["extension_codes"] == [extension_code]
        assert meta["programme_alignment"] == "OPTIONAL_EXTENSION"
        assert meta["extension_label"] == "Approfondissement — Vers la Terminale"
        assert "Approfondissement — Vers la Terminale" in path.read_text(
            encoding="utf-8"
        )

    curation = _json(chapter / "dossier_curation.json")
    assert set(curation["capacites"]) == {"C1", "C2", "X1", "X2", "X3"}
    assert all(
        curation["capacites"][code]["programme_alignment"]
        == "OPTIONAL_EXTENSION"
        and curation["capacites"][code]["extension_label"]
        == "Approfondissement — Vers la Terminale"
        and "format_examen" not in curation["capacites"][code]
        for code in ("X1", "X2", "X3")
    )
